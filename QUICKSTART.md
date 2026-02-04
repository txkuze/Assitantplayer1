# Quick Start Guide

Get your Telegram Music Bot up and running in 5 minutes!

## Prerequisites

- Python 3.11+
- FFmpeg installed
- Telegram account
- MongoDB database (free tier available at MongoDB Atlas)

## Step 1: Get Telegram Credentials

### API Credentials
1. Visit [my.telegram.org](https://my.telegram.org)
2. Login and go to "API Development Tools"
3. Create an app and copy `API_ID` and `API_HASH`

### Bot Token
1. Message [@BotFather](https://t.me/BotFather)
2. Send `/newbot` and follow instructions
3. Copy the bot token

## Step 2: Setup MongoDB

1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create a free cluster
3. Create a database user
4. Get your connection string
5. Replace `<password>` with your actual password

## Step 3: Create Logger Group

1. Create a new Telegram group
2. Add your bot to the group and make it admin
3. Send any message in the group
4. Forward it to [@userinfobot](https://t.me/userinfobot)
5. Copy the group ID (starts with -100)

## Step 4: Install and Configure

### Automatic Setup (Recommended)

```bash
git clone https://github.com/yourusername/telegram-music-bot.git
cd telegram-music-bot
chmod +x setup.sh
./setup.sh
```

### Manual Setup

```bash
git clone https://github.com/yourusername/telegram-music-bot.git
cd telegram-music-bot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## Step 5: Generate String Session

```bash
python generate_session.py
```

Follow the prompts:
1. Enter API_ID and API_HASH
2. Enter phone number (with country code)
3. Enter the code you receive
4. Copy the string session

## Step 6: Configure Environment

Edit `.env` file:

```env
API_ID=12345678
API_HASH=abcdef1234567890
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
STRING_SESSION=your_string_session_here
LOGGER_GROUP_ID=-100xxxxxxxxxx
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/
OWNER_ID=your_telegram_user_id
```

## Step 7: Run the Bot

```bash
./start.sh
```

Or manually:
```bash
source venv/bin/activate
python bot.py
```

## Step 8: Test the Bot

1. Add your bot to a group
2. Make it admin with necessary permissions
3. Start or join a voice chat in the group
4. In the group, send: `/assiststart`
5. The assistant will join the voice chat and start listening
6. Speak in the voice chat: "Assistant play Despacito"
7. Or send: `/play Despacito`
8. Enjoy the music with voice control!

## Deploy to Heroku

One-click deploy:

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

Or via CLI:

```bash
heroku login
heroku create your-app-name
git push heroku main
heroku ps:scale worker=1
```

## Troubleshooting

### Bot not starting
- Check all credentials in `.env`
- Ensure MongoDB connection string is correct
- Verify FFmpeg is installed: `ffmpeg -version`

### Assistant not joining
- Verify string session is correct
- Check if the assistant account is restricted
- Make sure the account hasn't joined too many groups

### Music not playing
- Ensure FFmpeg is installed
- Check voice chat is active in the group
- Verify the bot and assistant have admin rights

## Need Help?

- Check [README.md](README.md) for detailed documentation
- Create an issue on GitHub
- Join our support group (if available)

## Next Steps

- Add Spotify integration (optional)
- Set up YouTube cookies for age-restricted content
- Customize the bot's responses
- Add more music platforms

Happy listening!
