VLC Discord Bot 🎬
A comprehensive Discord bot that provides full remote control for VLC Media Player with an elegant interface, persistent status tracking, playlist management, and advanced user permissions.

Python
Discord.py
License

✨ Features
🎮 Complete Media Controls
Play/Pause/Stop: Full playback control with user tracking

Seek Controls: Jump forward/backward by 10 seconds

Playlist Navigation: Previous/Next track with permission controls

Real-time Status: Live updates every 6 seconds with progress bars

📊 Rich Status Display
Spotify-style Progress Bar: Visual progress indication with timestamps

Comprehensive Media Info: Title, artist, album, duration, bitrate

Playlist Information: Shows current position and upcoming tracks

Connection Status: Real-time VLC connection monitoring

👥 Advanced User Management
Role-based Permissions: Configurable role requirements for bot access

Admin Controls: Special permissions for seeking and playlist management

Pause Protection: Only the person who paused (or admin) can resume

Button Cooldowns: Prevents spam and accidental rapid commands

📈 Activity Tracking
Command History: Track all user interactions with timestamps

User Statistics: Monitor most active users and total actions

Persistent Logging: File-based logging with configurable levels

🔧 Configuration Management
Environment Variables: Secure configuration via .env file

Customizable Colors: Embed colors for different playback states

Flexible Updates: Configurable update intervals and display options

Auto-reconnection: Automatic VLC reconnection with retry logic

🚀 Quick Start
Prerequisites
Python 3.8 or higher

VLC Media Player with HTTP interface enabled

Discord Bot Token

Installation
Clone the repository

bash
git clone https://github.com/yourusername/vlc-discord-bot.git
cd vlc-discord-bot
Install dependencies

bash
pip install -r requirements.txt
Setup VLC HTTP Interface

Open VLC → Tools → Preferences

Click "Show settings: All" (bottom left)

Navigate to Interface → Main interfaces

Check "Web"

Go to Interface → Main interfaces → Lua

Set HTTP password (remember this for .env)

Restart VLC

Configure Environment Variables
Create a .env file in the project directory:

text
# Discord Configuration
DISCORD_BOT_TOKEN=your_discord_bot_token_here
BOT_PREFIX=!

# VLC Configuration
VLC_HOST=localhost
VLC_PORT=8080
VLC_PASSWORD=your_vlc_password

# Channel Configuration
STATUS_CHANNEL_ID=123456789012345678
ALLOWED_GUILD_ID=123456789012345678

# Optional: Role Configuration
REQUIRED_ROLE_ID=123456789012345678

# Optional: Advanced Settings
UPDATE_INTERVAL=6
LOG_LEVEL=INFO
BOT_STATUS_TEXT=movies with friends
Run the bot

bash
python start.py
📋 Requirements
Create a requirements.txt file with the following dependencies:

text
discord.py>=2.0.0
python-dotenv>=0.19.0
aiohttp>=3.8.0
requests>=2.28.0
🎛️ Commands
Slash Commands
/setup - Initialize the VLC control panel (Admin only)

/who_paused - See who last paused the playbook

/force_play - Force resume playbook (Admin only)

/playlist - Display current playlist information

Interactive Controls
The bot provides an always-visible control panel with buttons for:

⏮️ Previous Track - Go to previous item in playlist

⏪ -10s - Seek backward 10 seconds

⏸️ Pause - Pause playback

▶️ Play - Resume playback

+10s ⏩ - Seek forward 10 seconds

⏭️ Next Track - Go to next item in playlist

📊 Stats - View bot and user statistics

📜 History - View recent command history

🔄 Refresh - Manually refresh status

⚙️ Configuration Options
Discord Settings
Variable	Description	Default
DISCORD_BOT_TOKEN	Your Discord bot token	Required
BOT_PREFIX	Command prefix for text commands	!
STATUS_CHANNEL_ID	Channel for persistent status embed	None
ALLOWED_GUILD_ID	Restrict bot to specific server	None
VLC Connection
Variable	Description	Default
VLC_HOST	VLC server hostname	localhost
VLC_PORT	VLC HTTP interface port	8080
VLC_PASSWORD	VLC HTTP interface password	Empty
Security & Permissions
Variable	Description	Default
REQUIRED_ROLE_ID	Role required to use bot	None
ADMIN_ONLY_SEEK	Restrict seeking to admins	false
ADMIN_ONLY_PLAYLIST	Restrict playlist controls to admins	false
PAUSE_COOLDOWN	Cooldown between pause commands (seconds)	2
BUTTON_COOLDOWN	Cooldown between button presses (seconds)	1
Display & Updates
Variable	Description	Default
UPDATE_INTERVAL	Status update frequency (seconds)	6
SHOW_PROGRESS_IN_STATUS	Show progress in bot status	true
PROGRESS_BAR_LENGTH	Length of progress bar	25
BOT_STATUS_TYPE	Bot activity type (watching/playing/listening)	watching
BOT_STATUS_TEXT	Default bot status text	movies with friends
Logging
Variable	Description	Default
LOG_LEVEL	Logging level (DEBUG/INFO/WARNING/ERROR)	INFO
LOG_TO_FILE	Enable file logging	true
LOG_FILE	Log file path	vlc_bot.log
Advanced Features
Variable	Description	Default
AUTO_RECONNECT_VLC	Auto-reconnect to VLC on failure	true
MAX_RECONNECT_ATTEMPTS	Maximum reconnection attempts	5
RECONNECT_DELAY	Delay between reconnection attempts (seconds)	10
Embed Customization
Variable	Description	Default
EMBED_COLOR_PLAYING	Embed color when playing (hex)	0x00ff00
EMBED_COLOR_PAUSED	Embed color when paused (hex)	0xff8c00
EMBED_COLOR_STOPPED	Embed color when stopped (hex)	0xff0000
EMBED_COLOR_ERROR	Embed color for errors (hex)	0x800080
🔒 Security Features
Role-Based Access Control
Configure REQUIRED_ROLE_ID to restrict bot usage

Admin-only commands for sensitive operations

Separate permissions for seeking and playlist controls

Pause Protection System
Only the user who paused can resume (or admins)

Persistent tracking of pause actions

Anti-spam measures with configurable cooldowns

Connection Security
Secure VLC authentication with password protection

Automatic connection monitoring and recovery

Error handling to prevent crashes

🐛 Troubleshooting
Common Issues
Bot can't connect to VLC

Ensure VLC HTTP interface is enabled

Check VLC_HOST and VLC_PORT in .env

Verify VLC_PASSWORD matches VLC settings

Try accessing http://localhost:8080 in browser

Commands not working

Check bot permissions in Discord server

Verify ALLOWED_GUILD_ID is correct

Ensure STATUS_CHANNEL_ID exists and bot can access it

Status not updating

Check UPDATE_INTERVAL setting

Verify bot has permission to edit messages

Look for errors in bot logs

Permission errors

Check REQUIRED_ROLE_ID configuration

Verify admin permissions for restricted commands

Review role hierarchy in Discord server

Debug Mode
Enable debug logging by setting LOG_LEVEL=DEBUG in your .env file for detailed troubleshooting information.

🤝 Contributing
Fork the repository

Create a feature branch (git checkout -b feature/amazing-feature)

Commit your changes (git commit -m 'Add amazing feature')

Push to the branch (git push origin feature/amazing-feature)

Open a Pull Request

📝 License
This project is licensed under the MIT License - see the LICENSE file for details.

🙏 Acknowledgments
Built with discord.py

VLC Media Player HTTP interface

Inspired by the need for seamless movie night controls

📞 Support
If you encounter any issues or have questions:

Check the troubleshooting section above

Look through existing Issues

Create a new issue with detailed information about your problem
