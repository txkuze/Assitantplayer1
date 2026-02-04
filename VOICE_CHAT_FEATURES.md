# Voice Chat Listening Features

## Overview

The bot now features continuous voice chat listening with wake word detection and natural language command processing. The assistant stays in the voice chat and actively listens for voice commands from users.

## New Capabilities

### 1. Continuous Voice Chat Listening

When you activate the assistant with `/assiststart`, it:
- Joins the voice chat immediately
- Starts listening continuously for voice commands
- Stays active until you use `/assistclose`
- Processes commands from all users in the voice chat

### 2. Wake Word Detection

The assistant responds to the following wake words:
- "assistant"
- "hey assistant"
- "ok assistant"
- "hello assistant"

Simply say the wake word followed by your command.

### 3. Natural Language Commands

You can speak naturally. The bot understands various phrasings:

**Play Music:**
- "Assistant play Challeya"
- "Assistant play Shape of You by Ed Sheeran"
- "Assistant search for Despacito"
- "Assistant start playing Bohemian Rhapsody"
- "Assistant put on some Beatles"
- "Assistant listen to Purple Rain"

**Playback Control:**
- "Assistant pause"
- "Assistant resume"
- "Assistant stop"
- "Assistant skip"
- "Assistant next"

**Volume Control:**
- "Assistant volume 50"
- "Assistant volume 100"

## How It Works

### Technical Flow

1. **Assistant Joins**: When `/assiststart` is triggered, the assistant joins the voice chat
2. **Listening Activated**: Continuous listening mode starts automatically
3. **Audio Processing**: Voice chat audio is captured in real-time
4. **Speech Recognition**: Google Speech Recognition processes spoken commands
5. **Wake Word Detection**: System detects if "assistant" was said
6. **Command Parsing**: Natural language parser extracts the action and query
7. **Music Search**: Searches YouTube/Spotify for the requested song
8. **Playback**: Downloads and plays the song while continuing to listen

### Architecture Components

#### New Files Created:

1. **`utils/voice_listener.py`**
   - Manages voice chat listening sessions
   - Implements wake word detection
   - Parses natural language commands
   - Handles continuous listening loops

2. **`utils/audio_capture.py`**
   - Captures audio from voice chat
   - Manages audio buffers
   - Converts audio to processable format

3. **`utils/generate_silence.py`**
   - Generates silence audio file
   - Used when assistant joins without playing music

#### Modified Files:

1. **`handlers/voice_chat.py`**
   - Added continuous listening on `/assiststart`
   - Integrated voice listener and audio capture
   - Added background task management
   - Enhanced `/assistclose` to stop all listening tasks

2. **`handlers/music.py`**
   - Updated voice message handler to use voice listener
   - Added command processing from voice chat

3. **`bot.py`**
   - Added silence file generation on startup
   - Creates necessary cache directories

4. **Documentation Files**
   - Updated README.md, QUICKSTART.md, PROJECT_OVERVIEW.md
   - Updated help commands in handlers/commands.py

## Usage Instructions

### For Users

1. **Start Voice Chat**
   ```
   - Start or join a voice chat in your Telegram group
   ```

2. **Activate Assistant**
   ```
   /assiststart
   ```

3. **Speak Your Commands**
   ```
   Say: "Assistant play Challeya"
   Say: "Assistant pause"
   Say: "Assistant play Shape of You"
   ```

4. **Alternative Methods**
   - Use text commands: `/play Challeya`
   - Send voice messages in the chat

5. **Stop Assistant**
   ```
   /assistclose
   ```

### For Developers

#### Testing Voice Recognition

```python
from utils.voice_listener import voice_listener

async def test_command_parsing():
    command = voice_listener._extract_command("assistant play despacito")
    print(command)
```

#### Adding New Commands

Edit `utils/voice_listener.py` and add patterns to `command_patterns`:

```python
command_patterns = [
    (r'play\s+(.+)', 'play'),
    (r'your_pattern_here', 'your_action'),
]
```

## Benefits

1. **Hands-Free Control**: Users can control music without typing
2. **Natural Interaction**: Speak naturally instead of rigid commands
3. **Multi-User Support**: Any user in voice chat can give commands
4. **Continuous Operation**: Assistant stays active and listening
5. **Smart Parsing**: Understands various phrasings of the same command

## Performance Considerations

- Speech recognition uses Google's API (requires internet)
- Audio processing happens in real-time
- Background tasks run asynchronously for non-blocking operation
- Silence audio file is pre-generated on startup

## Troubleshooting

### Assistant Not Responding to Voice

1. Make sure you're using the wake word "assistant"
2. Check that voice chat is active
3. Ensure `/assiststart` was executed successfully
4. Verify microphone permissions in the group

### Commands Not Recognized

1. Speak clearly and at normal pace
2. Use supported command patterns
3. Check internet connection for speech recognition
4. Review logs for recognition errors

### Audio Issues

1. Ensure FFmpeg is installed correctly
2. Check cache directories exist and are writable
3. Verify pytgcalls is properly configured
4. Check assistant account has proper permissions

## Future Enhancements

Potential improvements for future versions:

- Queue management for multiple songs
- Playlist support
- User-specific preferences
- Multi-language support
- Custom wake words
- Offline speech recognition
- Audio effects and equalizer
- DJ mode with voting

## Security & Privacy

- Voice commands are processed through Google Speech Recognition
- No voice data is stored permanently
- Audio files are cleaned up after processing
- Commands are logged for debugging purposes only

## Credits

Built using:
- Pyrogram for Telegram API
- Py-TgCalls for voice chat integration
- Google Speech Recognition API
- yt-dlp for music downloads
- Natural language processing for command parsing

---

For more information, see the main [README.md](README.md) or [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md).
