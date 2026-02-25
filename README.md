# discord_tts_bot

Discord bot that monitors a text channel and reads every message aloud in a voice channel using text-to-speech (TTS).

## Features

- **Auto-TTS**: every message posted in the configured text channel is spoken in the bot's current voice channel.
- **`!join`** – bot joins the voice channel of the user who typed the command.
- **`!leave`** – bot leaves the voice channel.
- **`!tts <text>`** – speak arbitrary text on demand from any channel.
- Messages are queued so rapid posts are spoken in order without overlapping.

## Requirements

- Python 3.8+
- [FFmpeg](https://ffmpeg.org/) installed and available on your `PATH`.

## Setup

1. **Clone the repo and install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

2. **Create your `.env` file**

   ```bash
   cp .env.example .env
   ```

   Fill in the values:

   | Variable | Description |
   |---|---|
   | `DISCORD_TOKEN` | Your bot's token from the [Discord Developer Portal](https://discord.com/developers/applications) |
   | `TTS_CHANNEL_ID` | The numeric ID of the text channel to monitor for auto-TTS |

3. **Enable the Message Content Intent**

   In the Discord Developer Portal → your application → **Bot** → enable **Message Content Intent**.

4. **Run the bot**

   ```bash
   python bot.py
   ```

## Usage

1. Join a voice channel on your server.
2. Type `!join` in any text channel – the bot will join your voice channel.
3. Post a message in the configured TTS text channel – the bot will speak it aloud.
4. Alternatively, use `!tts Hello world` from any channel to speak text directly.
5. Type `!leave` to disconnect the bot.
