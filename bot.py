import os
import asyncio
import discord
from discord.ext import commands
from gtts import gTTS
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
TTS_CHANNEL_ID = int(os.getenv("TTS_CHANNEL_ID", 0))

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Per-guild state: voice client and a queue of text to speak
tts_queues: dict[int, asyncio.Queue] = {}


async def play_next(guild_id: int, vc: discord.VoiceClient) -> None:
    """Dequeue the next TTS message and play it; loop until the queue is empty."""
    queue = tts_queues.get(guild_id)
    if queue is None or queue.empty():
        return

    text = await queue.get()
    filename = f"tts_{guild_id}.mp3"

    tts = gTTS(text=text, lang="en")
    tts.save(filename)

    def after_playing(error):
        if error:
            print(f"Playback error: {error}")
        os.remove(filename)
        # Schedule next item from the queue
        asyncio.run_coroutine_threadsafe(play_next(guild_id, vc), bot.loop)

    vc.play(discord.FFmpegPCMAudio(filename), after=after_playing)


@bot.event
async def on_ready() -> None:
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print(f"Listening for TTS messages in channel ID: {TTS_CHANNEL_ID}")


@bot.command(name="join")
async def join(ctx: commands.Context) -> None:
    """Join the voice channel of the user who invoked the command."""
    if ctx.author.voice is None:
        await ctx.send("You must be in a voice channel for me to join.")
        return

    channel = ctx.author.voice.channel

    if ctx.voice_client is not None:
        await ctx.voice_client.move_to(channel)
    else:
        await channel.connect()

    tts_queues.setdefault(ctx.guild.id, asyncio.Queue())
    await ctx.send(f"Joined **{channel.name}**.")


@bot.command(name="leave")
async def leave(ctx: commands.Context) -> None:
    """Disconnect the bot from its current voice channel."""
    if ctx.voice_client is None:
        await ctx.send("I am not currently in a voice channel.")
        return

    tts_queues.pop(ctx.guild.id, None)
    await ctx.voice_client.disconnect()
    await ctx.send("Disconnected from the voice channel.")


@bot.command(name="tts")
async def tts_command(ctx: commands.Context, *, text: str) -> None:
    """Speak the given text in the current voice channel."""
    if ctx.voice_client is None:
        await ctx.send("I am not in a voice channel. Use `!join` first.")
        return

    queue = tts_queues.setdefault(ctx.guild.id, asyncio.Queue())
    await queue.put(text)

    if not ctx.voice_client.is_playing():
        await play_next(ctx.guild.id, ctx.voice_client)


@bot.event
async def on_message(message: discord.Message) -> None:
    """Forward messages from the configured TTS channel to the voice channel."""
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return

    # Allow commands to be processed normally
    await bot.process_commands(message)

    # Auto-TTS: if the message is in the designated channel and the bot is in a
    # voice channel in the same guild, queue it for playback.
    if (
        TTS_CHANNEL_ID
        and message.channel.id == TTS_CHANNEL_ID
        and message.guild is not None
        and message.guild.voice_client is not None
        and message.content
    ):
        vc = message.guild.voice_client
        queue = tts_queues.setdefault(message.guild.id, asyncio.Queue())
        await queue.put(message.content)

        if not vc.is_playing():
            await play_next(message.guild.id, vc)


if __name__ == "__main__":
    bot.run(TOKEN)
