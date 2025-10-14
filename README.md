# 🎬 Discord VLC Media Player Bot

A powerful Discord bot that provides complete control over VLC Media Player through an interactive interface. Control your VLC playback directly from Discord with beautiful embeds, button controls, and real-time status updates.

## ✨ Features

### 🎮 Interactive Controls
- **Button-based Interface**: Easy-to-use button controls (no slash commands needed)
- **Real-time Updates**: Status updates every 6 seconds automatically
- **Spotify-style Progress Bar**: Visual progress tracking with timestamps
- **Media Information**: Automatic movie/TV show information scraping from IMDb

### 🎵 Playback Controls
- ▶️ **Play/Pause**: Start and stop media playback
- ⏭️/⏮️ **Next/Previous**: Navigate through playlist items
- ⏪/⏩ **Seek Controls**: Jump backward/forward by 10 seconds
- 🔄 **Refresh**: Manually update the status display

### 📋 Playlist Management
- **Playlist Display**: View current playlist with item names and positions
- **Queue Information**: See what's playing next
- **Playlist Navigation**: Jump to next/previous tracks easily

### 📊 Advanced Features
- **User Activity Tracking**: Monitor who's controlling the player
- **Command History**: Track recent user actions
- **Statistics Display**: View bot usage statistics
- **Admin Controls**: Role-based permissions and overrides
- **Connection Monitoring**: Automatic VLC reconnection handling

### 🛡️ Security & Permissions
- **Role-based Access**: Restrict bot usage to specific roles
- **Admin-only Features**: Limit seeking and playlist controls to admins
- **Cooldown System**: Prevent button spam with configurable cooldowns
- **Pause Protection**: Only the person who paused (or admins) can resume

### 🎨 Customization
- **Themed Embeds**: Color-coded status based on playback state
- **Rich Media Info**: Movie posters, ratings, and plot summaries
- **Bot Status Updates**: Shows current playing media in bot's status
- **Configurable Display**: Customize progress bar length, colors, and more

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- VLC Media Player with HTTP interface enabled
- Discord Bot Token

### Required Dependencies

Install all required packages using pip:

```bash
pip install discord.py python-dotenv aiohttp requests beautifulsoup4
```
Or install through requirements file:

```bash
pip install -r requirements.txt
```

### Individual Package Descriptions

- **discord.py**: Discord API wrapper for Python
- **python-dotenv**: Load environment variables from .env file
- **aiohttp**: Asynchronous HTTP client for VLC API communication
- **requests**: HTTP library for web requests
- **beautifulsoup4**: HTML parsing for media information scraping

### VLC Setup

1. **Enable VLC HTTP Interface:**
   - Open VLC Media Player
   - Go to `Tools` → `Preferences`
   - Show settings: `All`
   - Navigate to `Interface` → `Main interfaces`
   - Check `Web`
   - Go to `Interface` → `Main interfaces` → `Lua`
   - Set password in `Lua HTTP` → `Password`
   - Restart VLC

2. **Verify HTTP Interface:**
   - Open browser and go to `http://localhost:8080`
   - You should see VLC's web interface

### Discord Bot Setup

1. **Create Discord Application:**
   - Go to [Discord Developer Portal](https://discord.com/developers/applications)
   - Click "New Application"
   - Go to "Bot" section
   - Click "Add Bot"
   - Copy the bot token

2. **Bot Permissions:**
   Required permissions for the bot:
   - Send Messages
   - Use Slash Commands
   - Embed Links
   - Read Message History
   - Add Reactions

3. **Invite Bot to Server:**
   - Go to "OAuth2" → "URL Generator"
   - Select "bot" and "applications.commands"
   - Select the required permissions above
   - Use the generated URL to invite the bot

## ⚙️ Configuration

Create a `.env` file in the same directory as the bot:

```env
# Required Settings
DISCORD_BOT_TOKEN=your_discord_bot_token_here
VLC_PASSWORD=your_vlc_password_here
STATUS_CHANNEL_ID=your_discord_channel_id_here

# Optional VLC Settings
VLC_HOST=localhost
VLC_PORT=8080

# Optional Discord Settings
BOT_PREFIX=!
ALLOWED_GUILD_ID=your_server_id_here
REQUIRED_ROLE_ID=role_id_for_bot_access

# Bot Status Customization
BOT_STATUS_TYPE=watching
BOT_STATUS_TEXT=movies with friends
SHOW_PROGRESS_IN_STATUS=true
UPDATE_INTERVAL=6

# Security Settings
ADMIN_ONLY_SEEK=false
ADMIN_ONLY_PLAYLIST=false
PAUSE_COOLDOWN=2
BUTTON_COOLDOWN=1

# Visual Customization
EMBED_COLOR_PLAYING=0x00ff00
EMBED_COLOR_PAUSED=0xff8c00
EMBED_COLOR_STOPPED=0xff0000
EMBED_COLOR_ERROR=0x800080
PROGRESS_BAR_LENGTH=25
SHOW_THUMBNAIL=true

# Advanced Features
ENABLE_RICH_PRESENCE=true
AUTO_RECONNECT_VLC=true
MAX_RECONNECT_ATTEMPTS=5
RECONNECT_DELAY=10
ENABLE_MEDIA_INFO_SCRAPING=true
SCRAPING_TIMEOUT=10

# Logging
LOG_LEVEL=INFO
LOG_TO_FILE=true
LOG_FILE=vlc_bot.log
```

### Configuration Options Explained

#### Required Settings
- `DISCORD_BOT_TOKEN`: Your Discord bot token
- `VLC_PASSWORD`: Password set in VLC HTTP interface
- `STATUS_CHANNEL_ID`: Discord channel where the control panel will be posted

#### VLC Connection
- `VLC_HOST`: VLC server host (default: localhost)
- `VLC_PORT`: VLC HTTP interface port (default: 8080)

#### Security & Permissions
- `ALLOWED_GUILD_ID`: Restrict bot to specific server (optional)
- `REQUIRED_ROLE_ID`: Role required to use bot controls (optional)
- `ADMIN_ONLY_SEEK`: Only admins can seek (true/false)
- `ADMIN_ONLY_PLAYLIST`: Only admins control playlist (true/false)

#### Visual Customization
- `EMBED_COLOR_*`: Hex colors for different playback states
- `PROGRESS_BAR_LENGTH`: Length of progress bar (default: 25)
- `SHOW_THUMBNAIL`: Show movie/TV posters (true/false)

## 🚀 Usage

### Starting the Bot

1. **Run the bot:**
   ```bash
   python main.py
   ```

2. **Setup the bot in specific channel:**
   - Copy Server's ID and put in .env file
   - Copy Channel's ID and put it in .env file

### Button Controls

The bot provides an interactive control panel with the following buttons:

#### Row 1: Main Controls
- **⏮️ Previous**: Go to previous track in playlist
- **⏪ -10s**: Seek backward 10 seconds
- **⏸️ Pause**: Pause playback
- **▶️ Play**: Resume playback
- **+10s ⏩**: Seek forward 10 seconds

#### Row 2: Additional Features
- **⏭️ Next**: Go to next track in playlist
- **📊 Stats**: View bot usage statistics
- **📜 History**: See recent command history
- **🔄 Refresh**: Manually refresh the status display

### Bot Features in Action

#### Rich Media Information
The bot automatically scrapes movie and TV show information from IMDb, displaying:
- Movie/TV show titles and posters
- Plot summaries
- Ratings and genres
- Release years

#### Smart Playlist Display
- Shows current position in playlist (e.g., "3/15")
- Displays current track and upcoming items
- Clean filename formatting (removes quality tags, etc.)

#### User Activity Tracking
- Tracks who controls the player
- Shows command history
- Displays usage statistics
- Maintains pause permissions (only pauser or admin can resume)

## 🔧 Troubleshooting

### Common Issues

1. **Bot can't connect to VLC:**
   - Ensure VLC HTTP interface is enabled and running on port 8080
   - Check that the password in `.env` matches VLC settings
   - Verify VLC is running and has media loaded

2. **Bot doesn't respond to buttons:**
   - Check bot permissions (Send Messages, Embed Links)
   - Verify the bot is online and connected
   - Check console logs for error messages

3. **Media information not showing:**
   - Set `ENABLE_MEDIA_INFO_SCRAPING=true` in .env
   - Check internet connection for IMDb scraping
   - Some media files may not have available information

4. **Buttons show "Application did not respond":**
   - Check button cooldown settings in .env
   - Verify bot has proper permissions
   - Check VLC connection status

### Logs and Debugging

The bot creates detailed logs in `vlc_bot.log` (if `LOG_TO_FILE=true`). Check this file for:
- Connection errors
- Media scraping issues
- User action tracking
- VLC API responses

Set `LOG_LEVEL=DEBUG` for more detailed logging during troubleshooting.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source. Feel free to modify and distribute according to your needs.

## 🆘 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review the logs in `vlc_bot.log`
3. Ensure all dependencies are correctly installed
4. Verify VLC HTTP interface setup
5. Check Discord bot permissions

---

**Enjoy controlling your VLC Media Player through Discord! 🎉**