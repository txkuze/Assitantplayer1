# Telegram Music Bot

A powerful Telegram music bot with voice chat support, speech recognition, and multi-platform streaming capabilities.

## Features

- Play music from YouTube, Spotify, SoundCloud, and more
- Voice chat integration with pytgcalls
- Continuous voice chat listening - assistant listens while in voice chat
- Wake word detection - say "assistant" to activate commands
- Natural language processing - speak naturally to control playback
- Speech recognition - just speak and the bot will play your request
- Assistant account that joins groups automatically
- Comprehensive logging system
- MongoDB database for stats and analytics
- Support for multiple platforms
- Easy deployment on Heroku or VPS

## Commands

### Basic Commands
- `/start` - Start the bot
- `/help` - Get help information
- `/stats` - View bot statistics
- `/ping` - Check bot latency

### Music Commands
- `/assiststart` - Start assistant and activate voice chat listening
- `/assistclose` - Stop assistant from voice chat
- `/play [song name]` - Play a song in voice chat

### Voice Chat Listening
When you use `/assiststart`, the assistant joins the voice chat and continuously listens for commands. Simply speak naturally in the voice chat:

- "Assistant play Challeya" - Play a song
- "Assistant play Shape of You by Ed Sheeran" - Play specific song
- "Assistant pause" - Pause playback
- "Assistant resume" - Resume playback
- "Assistant stop" - Stop playback

You can also send voice messages in the chat, and the bot will process them!

## Requirements

- Python 3.11+
- FFmpeg
- MongoDB database
- Telegram API credentials
- Bot token from [@BotFather](https://t.me/BotFather)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/telegram-music-bot.git
cd telegram-music-bot
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Get Required Credentials

#### Telegram API Credentials
1. Go to [my.telegram.org](https://my.telegram.org)
2. Log in with your phone number
3. Click on "API Development Tools"
4. Create a new application
5. Copy your `API_ID` and `API_HASH`

#### Bot Token
1. Open [@BotFather](https://t.me/BotFather) on Telegram
2. Send `/newbot` and follow the instructions
3. Copy the bot token

#### String Session
1. Run the session generator:
```bash
python generate_session.py
```
2. Enter your API_ID and API_HASH
3. Login with your phone number (this will be the assistant account)
4. Copy the generated string session

#### MongoDB
1. Create a free MongoDB cluster at [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Get your connection string
3. Replace `<password>` with your actual password

#### Logger Group
1. Create a new private group on Telegram
2. Add your bot to the group
3. Send a message in the group
4. Forward the message to [@userinfobot](https://t.me/userinfobot)
5. Copy the group ID (it will be negative, like -100xxxxxxxxxx)

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and fill in your credentials:

```env
API_ID=your_api_id
API_HASH=your_api_hash
BOT_TOKEN=your_bot_token
STRING_SESSION=your_string_session
LOGGER_GROUP_ID=-100xxxxxxxxxx
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
OWNER_ID=your_telegram_user_id
```

### 5. Optional: YouTube Cookies (for age-restricted content)

1. Install a browser extension to export cookies
2. Export cookies for youtube.com
3. Save as `cookies.txt` in the project root

### 6. Optional: Spotify Integration

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Create a new app
3. Copy Client ID and Client Secret
4. Add to `.env`:

```env
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret
```

## Running the Bot

### Local Development

```bash
python bot.py
```

### Using Docker

```bash
docker-compose up -d
```

### Deploy to Heroku

#### Method 1: One-Click Deploy

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

#### Method 2: Using Heroku CLI

```bash
heroku login
heroku create your-app-name
heroku stack:set heroku-22
heroku buildpacks:add heroku/python
heroku buildpacks:add https://github.com/jonathanong/heroku-buildpack-ffmpeg-latest.git

git push heroku main

heroku config:set API_ID=your_api_id
heroku config:set API_HASH=your_api_hash
heroku config:set BOT_TOKEN=your_bot_token
heroku config:set STRING_SESSION=your_string_session
heroku config:set LOGGER_GROUP_ID=-100xxxxxxxxxx
heroku config:set MONGODB_URI=your_mongodb_uri
heroku config:set OWNER_ID=your_user_id

heroku ps:scale worker=1
heroku logs --tail
```

### Deploy to VPS

#### Using systemd

1. Create a service file:

```bash
sudo nano /etc/systemd/system/music-bot.service
```

2. Add the following content:

```ini
[Unit]
Description=Telegram Music Bot
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/telegram-music-bot
ExecStart=/usr/bin/python3 bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

3. Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable music-bot
sudo systemctl start music-bot
sudo systemctl status music-bot
```

4. View logs:

```bash
sudo journalctl -u music-bot -f
```

## Usage

1. Add the bot to your group
2. Make it an admin with necessary permissions
3. Start or join a voice chat in your group
4. Use `/assiststart` to activate the assistant
5. The assistant will join the voice chat and start listening
6. Speak naturally in the voice chat:
   - Say "Assistant play Challeya" to play a song
   - Say "Assistant pause" to pause
   - Say "Assistant resume" to resume
7. Alternatively, use `/play [song name]` or send voice messages
8. The assistant stays in voice chat and continuously listens for commands
9. Use `/assistclose` to stop the session

## Project Structure

```
telegram-music-bot/
├── bot.py                 # Main bot file
├── config.py             # Configuration
├── requirements.txt      # Python dependencies
├── Procfile             # Heroku worker configuration
├── Dockerfile           # Docker configuration
├── docker-compose.yml   # Docker Compose setup
├── app.json             # Heroku app configuration
├── generate_session.py  # String session generator
├── database/
│   ├── __init__.py
│   └── mongodb.py       # MongoDB operations
├── handlers/
│   ├── __init__.py
│   ├── commands.py      # Basic command handlers
│   ├── voice_chat.py    # Voice chat handlers
│   └── music.py         # Music playback handlers
└── utils/
    ├── __init__.py
    ├── logger.py          # Logging utilities
    ├── downloader.py      # Music download utilities
    ├── speech.py          # Speech recognition
    ├── voice_listener.py  # Voice chat listening and wake word detection
    ├── audio_capture.py   # Voice chat audio capture
    └── generate_silence.py # Silence audio file generator
```

## Troubleshooting

### Bot not responding
- Check if the bot is running
- Verify bot token is correct
- Check internet connection

### Assistant not joining groups
- Make sure string session is correct
- Verify the assistant account is not restricted
- Check if the account has joined too many groups

### Music not playing
- Install FFmpeg: `sudo apt-get install ffmpeg`
- Check voice chat is active in the group
- Verify pytgcalls is installed correctly

### Speech recognition not working
- Install portaudio: `sudo apt-get install portaudio19-dev`
- Check microphone permissions
- Verify speech_recognition library is installed

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.

## Disclaimer

This bot is for educational purposes only. Make sure you comply with Telegram's Terms of Service and the terms of service of any platform you stream content from.

## Support

For support, create an issue on GitHub or contact the bot owner.

## Credits

- [Pyrogram](https://github.com/pyrogram/pyrogram)
- [Py-TgCalls](https://github.com/pytgcalls/pytgcalls)
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- [SpeechRecognition](https://github.com/Uberi/speech_recognition)

## Star History

If you like this project, please give it a star!
