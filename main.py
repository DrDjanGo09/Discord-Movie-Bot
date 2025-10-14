import discord

from discord.ext import commands, tasks

import requests

import base64

import json

import os

import logging

import asyncio

from datetime import datetime, timedelta

from typing import Optional, Dict, Any, List

from dotenv import load_dotenv

import aiohttp

from pathlib import Path
from bs4 import BeautifulSoup
import re

# Load environment variables

load_dotenv()

class Config:

    """Configuration class that loads from .env file"""

    # Discord Configuration

    DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')

    BOT_PREFIX = os.getenv('BOT_PREFIX', '!')

    # VLC Configuration

    VLC_HOST = os.getenv('VLC_HOST', 'localhost')

    VLC_PORT = int(os.getenv('VLC_PORT', '8080'))

    VLC_PASSWORD = os.getenv('VLC_PASSWORD', '')

    # Channel Configuration

    STATUS_CHANNEL_ID = int(os.getenv('STATUS_CHANNEL_ID')) if os.getenv('STATUS_CHANNEL_ID') else None

    ALLOWED_GUILD_ID = int(os.getenv('ALLOWED_GUILD_ID')) if os.getenv('ALLOWED_GUILD_ID') else None
    
    # Role Configuration
    REQUIRED_ROLE_ID = int(os.getenv('REQUIRED_ROLE_ID')) if os.getenv('REQUIRED_ROLE_ID') else None

    # Bot Status Configuration

    BOT_STATUS_TYPE = os.getenv('BOT_STATUS_TYPE', 'watching')

    BOT_STATUS_TEXT = os.getenv('BOT_STATUS_TEXT', 'movies with friends')

    UPDATE_INTERVAL = int(os.getenv('UPDATE_INTERVAL', '6'))

    SHOW_PROGRESS_IN_STATUS = os.getenv('SHOW_PROGRESS_IN_STATUS', 'true').lower() == 'true'

    # Logging Configuration

    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

    LOG_TO_FILE = os.getenv('LOG_TO_FILE', 'true').lower() == 'true'

    LOG_FILE = os.getenv('LOG_FILE', 'vlc_bot.log')

    # Advanced Features

    ENABLE_RICH_PRESENCE = os.getenv('ENABLE_RICH_PRESENCE', 'true').lower() == 'true'

    AUTO_RECONNECT_VLC = os.getenv('AUTO_RECONNECT_VLC', 'true').lower() == 'true'

    MAX_RECONNECT_ATTEMPTS = int(os.getenv('MAX_RECONNECT_ATTEMPTS', '5'))

    RECONNECT_DELAY = int(os.getenv('RECONNECT_DELAY', '10'))

    # Security

    ADMIN_ONLY_SEEK = os.getenv('ADMIN_ONLY_SEEK', 'false').lower() == 'true'

    ADMIN_ONLY_PLAYLIST = os.getenv('ADMIN_ONLY_PLAYLIST', 'false').lower() == 'true'

    PAUSE_COOLDOWN = int(os.getenv('PAUSE_COOLDOWN', '2'))

    BUTTON_COOLDOWN = int(os.getenv('BUTTON_COOLDOWN', '1'))

    # Embed Customization

    EMBED_COLOR_PLAYING = int(os.getenv('EMBED_COLOR_PLAYING', '0x00ff00'), 16)

    EMBED_COLOR_PAUSED = int(os.getenv('EMBED_COLOR_PAUSED', '0xff8c00'), 16)

    EMBED_COLOR_STOPPED = int(os.getenv('EMBED_COLOR_STOPPED', '0xff0000'), 16)

    EMBED_COLOR_ERROR = int(os.getenv('EMBED_COLOR_ERROR', '0x800080'), 16)

    PROGRESS_BAR_LENGTH = int(os.getenv('PROGRESS_BAR_LENGTH', '25'))

    SHOW_THUMBNAIL = os.getenv('SHOW_THUMBNAIL', 'true').lower() == 'true'

    # Web Scraping Configuration
    ENABLE_MEDIA_INFO_SCRAPING = os.getenv('ENABLE_MEDIA_INFO_SCRAPING', 'true').lower() == 'true'
    SCRAPING_TIMEOUT = int(os.getenv('SCRAPING_TIMEOUT', '10'))

# Setup logging

def setup_logging():

    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    level = getattr(logging, Config.LOG_LEVEL.upper(), logging.INFO)

    handlers = [logging.StreamHandler()]

    if Config.LOG_TO_FILE:

        handlers.append(logging.FileHandler(Config.LOG_FILE, encoding='utf-8'))

    logging.basicConfig(

        level=level,

        format=log_format,

        handlers=handlers

    )

setup_logging()

logger = logging.getLogger(__name__)

def is_admin(user: discord.Member) -> bool:

    """Check if user has admin permissions"""

    perms = user.guild_permissions

    return perms.administrator or perms.manage_guild

# Bot configuration

intents = discord.Intents.default()

intents.message_content = True

bot = commands.Bot(

    command_prefix=Config.BOT_PREFIX,

    intents=intents,

    help_command=None

)

class VLCController:

    """Enhanced VLC controller with connection pooling and error handling"""

    def __init__(self, host: str, port: int, password: str):

        self.host = host

        self.port = port

        self.password = password

        self.base_url = f"http://{host}:{port}"

        self.auth_header = self._create_auth_header()

        self.session = None

        self.connection_attempts = 0

        self.last_error = None

    def _create_auth_header(self):

        credentials = f":{self.password}"

        encoded = base64.b64encode(credentials.encode()).decode()

        return {"Authorization": f"Basic {encoded}"}

    async def _ensure_session(self):

        if self.session is None or self.session.closed:

            timeout = aiohttp.ClientTimeout(total=5)

            self.session = aiohttp.ClientSession(

                timeout=timeout,

                headers=self.auth_header

            )

    async def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Optional[Dict]:

        try:

            await self._ensure_session()

            url = f"{self.base_url}/requests/{endpoint}"

            async with self.session.get(url, params=params or {}) as response:

                if response.status == 200:

                    self.connection_attempts = 0

                    self.last_error = None

                    text = await response.text()

                    return json.loads(text) if text.strip() else {}

                else:

                    logger.warning(f"VLC API returned status {response.status}")

                    return None

        except Exception as e:

            self.connection_attempts += 1

            self.last_error = str(e)

            logger.error(f"VLC API Error (attempt {self.connection_attempts}): {e}")

            if Config.AUTO_RECONNECT_VLC and self.connection_attempts <= Config.MAX_RECONNECT_ATTEMPTS:

                await asyncio.sleep(Config.RECONNECT_DELAY)

            return None

    async def get_status(self) -> Optional[Dict]:

        return await self._make_request("status.json")

    async def play(self) -> Optional[Dict]:

        return await self._make_request("status.json", {"command": "pl_play"})

    async def pause(self) -> Optional[Dict]:

        return await self._make_request("status.json", {"command": "pl_pause"})

    async def seek_relative(self, seconds: int) -> Optional[Dict]:

        return await self._make_request("status.json", {"command": "seek", "val": f"{seconds:+d}S"})

    async def next(self) -> Optional[Dict]:

        return await self._make_request("status.json", {"command": "pl_next"})

    async def previous(self) -> Optional[Dict]:

        return await self._make_request("status.json", {"command": "pl_previous"})

    async def get_playlist(self) -> Optional[Dict]:

        return await self._make_request("playlist.json")

    async def close(self):

        if self.session and not self.session.closed:

            await self.session.close()

    @property

    def is_connected(self) -> bool:

        return self.connection_attempts == 0 and self.last_error is None

# Initialize VLC controller

vlc = VLCController(Config.VLC_HOST, Config.VLC_PORT, Config.VLC_PASSWORD)

# Global state management

class MediaScraper:
    """Scrapes media information from public websites without API keys"""
    
    def __init__(self):
        self.session = None
        self.cache = {}
        
    async def _ensure_session(self):
        if self.session is None or self.session.closed:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            timeout = aiohttp.ClientTimeout(total=Config.SCRAPING_TIMEOUT)
            self.session = aiohttp.ClientSession(timeout=timeout, headers=headers)
    
    async def extract_media_name(self, filename: str) -> str:
        """Extract clean media name from filename for searching"""
        if not filename or filename == "Unknown":
            return ""
    
        # Remove file extension and get base name
        name = os.path.splitext(filename)[0]
    
        # Common patterns to remove (both movie and TV show patterns)
        patterns_to_remove = [
            # Quality and format patterns
            r'\b(?:brrip|webrip|webdl|web-dl|bluray|dvdrip|bdrip|hdtv)\b',
            r'\b(?:x264|x265|hevc|avc|aac|ac3|ddp|dts)\b',
            r'\b(?:1080p|720p|480p|4k|uhd|fhd|hd)\b',
            r'\b(?:amzn|amazon|netflix|hulu|disney|hbo|max)\b',
            r'\b(?:web|dl|download|stream|online)\b',
        
            # Release group patterns
            r'\[.*?\]',  # Anything in brackets
            r'\(.*?\)',  # Anything in parentheses (but be careful with years)
        
            # Special characters
            r'[\._]',  # Replace dots and underscores with spaces
        ]
    
        # Apply removal patterns
        for pattern in patterns_to_remove:
            name = re.sub(pattern, ' ', name, flags=re.IGNORECASE)
    
        # Clean up extra spaces
        name = re.sub(r'\s+', ' ', name).strip()
    
        # Try to detect if it's a TV show and extract series name
        tv_patterns = [
            r'^(.*?)\s*[sS](\d{1,2})[eE](\d{1,2})',  # S01E01 format
            r'^(.*?)\s*season\s*(\d{1,2})\s*episode\s*(\d{1,2})',  # Season 1 Episode 1
            r'^(.*?)\s*(\d{1,2})[xX](\d{1,2})',  # 1x01 format
        ]
    
        for pattern in tv_patterns:
            match = re.search(pattern, name)
            if match:
                series_name = match.group(1).strip()
                season_num = match.group(2)
                episode_num = match.group(3)
                logger.info(f"📺 Detected TV show: {series_name} S{season_num}E{episode_num}")
                return series_name
    
        # For movies, try to preserve the year but clean everything else
        movie_year_pattern = r'^(.*?)\s*\((\d{4})\)\s*$'
        movie_match = re.search(movie_year_pattern, name)
        if movie_match:
            movie_name = movie_match.group(1).strip()
            year = movie_match.group(2)
            logger.info(f"🎬 Detected movie: {movie_name} ({year})")
            return f"{movie_name} {year}"
    
        # Final cleanup - remove any remaining numbers that might be years at the end
        name = re.sub(r'\s+\d{4}$', '', name)
    
        # If the name is still too long, take the first few words
        words = name.split()
        if len(words) > 5:
            name = ' '.join(words[:4])  # Take first 4 words
    
        logger.info(f"🔧 Cleaned filename: '{filename}' -> '{name}'")
        return name
    
    async def search_media_info(self, media_name: str) -> Dict[str, Any]:
        """Search for media information using multiple strategies"""
        if not Config.ENABLE_MEDIA_INFO_SCRAPING:
            return {}
        
        cache_key = media_name.lower()
        if cache_key in self.cache:
            return self.cache[cache_key]
    
        clean_name = await self.extract_media_name(media_name)
        if not clean_name:
            return {}
    
        logger.info(f"🔍 Searching for media info: '{clean_name}' (original: '{media_name}')")
    
        try:
            await self._ensure_session()
        
            # Strategy 1: Try exact search
            info = await self._search_imdb_public(clean_name)
        
            # Strategy 2: If exact search fails, try without year
            if not info:
                name_without_year = re.sub(r'\s+\d{4}$', '', clean_name).strip()
                if name_without_year != clean_name:
                    logger.info(f"🔄 Trying search without year: '{name_without_year}'")
                    info = await self._search_imdb_public(name_without_year)
        
            # Strategy 3: If still no results, try with just the first few words
            if not info:
                words = clean_name.split()
                if len(words) > 3:
                    simplified_name = ' '.join(words[:3])  # Just first 3 words
                    logger.info(f"🔄 Trying simplified search: '{simplified_name}'")
                    info = await self._search_imdb_public(simplified_name)
        
            # Strategy 4: Try alternative search methods
            if not info:
                info = await self._search_tmdb_alternative(clean_name)
        
            if info:
                logger.info(f"✅ Found media info: {info.get('title', 'Unknown')}")
                if info.get('plot'):
                    logger.info(f"📖 Plot: {info['plot'][:100]}...")
            else:
                logger.warning(f"❌ No media info found after all strategies")
            
            self.cache[cache_key] = info
            return info
        
        except Exception as e:
            logger.error(f"Error scraping media info for '{clean_name}': {e}")
            return {}
    
    async def _search_imdb_public(self, media_name: str) -> Dict[str, Any]:
        """Search IMDb public website with improved selectors"""
        try:
            search_url = "https://www.imdb.com/find"
            params = {
                'q': media_name,
                's': 'tt',
                'ttype': 'ft,tv'  # Search for both feature films and TV
            }
        
            async with self.session.get(search_url, params=params) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                
                    # Try multiple selectors for search results
                    selectors = [
                        'li.find-result-item',
                        '.find-result',
                        '.find-title-result',
                        '[data-testid="find-results-section-title"] .ipc-metadata-list-summary-item',
                        '.findSection:first-child .findList tr'  # Older IMDb layout
                    ]
                
                    result = None
                    for selector in selectors:
                        results = soup.select(selector)
                        if results:
                            result = results[0]  # Take first result
                            break
                
                    if not result:
                        logger.warning(f"No IMDb results found for: {media_name}")
                        return {}
                
                    # Extract title and link
                    title_element = result.find('a') or result.select_one('a')
                    if not title_element:
                        return {}
                
                    title = title_element.get_text().strip()
                    movie_link = title_element.get('href', '')
                
                    # Get image
                    img_element = result.find('img') or result.select_one('img')
                    image_url = img_element.get('src', '') if img_element else ""
                
                    # Determine if it's a TV show or movie
                    media_type = 'movie'
                    if 'series' in str(result).lower() or 'tv' in str(result).lower():
                        media_type = 'tv'
                
                    # Get details from movie/TV page
                    details = await self._get_imdb_details_public(movie_link) if movie_link else {}
                
                    return {
                        'title': title,
                        'image': image_url,
                        'plot': details.get('plot', ''),
                        'rating': details.get('rating', ''),
                        'genre': details.get('genre', ''),
                        'year': details.get('year', ''),
                        'type': media_type
                    }
                else:
                    logger.warning(f"IMDb search returned status: {response.status}")
                    return {}
                
        except Exception as e:
            logger.error(f"IMDb public search error: {e}")
            return {}
    
    async def _get_imdb_details_public(self, movie_path: str) -> Dict[str, Any]:
        """Get details from IMDb movie page with improved selectors"""
        try:
            if not movie_path.startswith('http'):
                movie_path = f"https://www.imdb.com{movie_path}"
                
            async with self.session.get(movie_path) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    info = {}
                    
                    # Get plot with multiple selector attempts
                    plot_selectors = [
                        'span[data-testid="plot-l"]',
                        '.plot_summary .summary_text',
                        '.ipc-overflowText',
                        '[data-testid="storyline-plot-summary"]'
                    ]
                    
                    for selector in plot_selectors:
                        plot_element = soup.select_one(selector)
                        if plot_element:
                            plot = plot_element.get_text().strip()
                            if plot and plot not in ["Add a plot", "Plot summary"]:
                                info['plot'] = plot
                                break
                    
                    # Get rating with multiple selector attempts
                    rating_selectors = [
                        '[data-testid="hero-rating-bar__aggregate-rating__score"]',
                        '.imdbRating span[class*="rating"]',
                        '.ratingValue strong',
                        '.sc-bde20123-1'
                    ]
                    
                    for selector in rating_selectors:
                        rating_element = soup.select_one(selector)
                        if rating_element:
                            rating_text = rating_element.get_text().strip()
                            if rating_text:
                                info['rating'] = rating_text
                                break
                    
                    # Get genres
                    genre_selectors = [
                        '[data-testid="genres"] a',
                        '.genres a',
                        '.ipc-chip-list a'
                    ]
                    
                    for selector in genre_selectors:
                        genre_elements = soup.select(selector)
                        if genre_elements:
                            genres = [genre.get_text().strip() for genre in genre_elements[:3]]
                            info['genre'] = ", ".join(genres)
                            break
                    
                    # Get year
                    year_selectors = [
                        '[data-testid="hero-title-block__metadata"] li',
                        '.title_wrapper .subtext a',
                        '.sc-d8941411-1'
                    ]
                    
                    for selector in year_selectors:
                        year_element = soup.select_one(selector)
                        if year_element:
                            year_text = year_element.get_text().strip()
                            if year_text and year_text.isdigit():
                                info['year'] = year_text
                                break
                    
                    return info
                else:
                    logger.warning(f"IMDb details returned status: {response.status}")
                    return {}
                    
        except Exception as e:
            logger.error(f"IMDb details error: {e}")
            return {}
    
    async def _search_tmdb_alternative(self, media_name: str) -> Dict[str, Any]:
        """Alternative search using TheMovieDB style (without API key)"""
        try:
            # This is a placeholder - you could implement alternative sources here
            # For now, we'll return empty but you could add other public sites
            return {}
        except Exception as e:
            logger.error(f"Alternative search error: {e}")
            return {}
    
    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()

# ADD THIS LINE:
media_scraper = MediaScraper()

class BotState:

    def __init__(self):

        self.last_pauser_id: Optional[int] = None

        self.last_pauser_name: Optional[str] = None  # Store pauser name

        self.last_pause_time: Optional[datetime] = None  # Store pause time

        self.user_actions: Dict[int, Dict] = {}

        self.command_history: List[Dict] = []  # New: store command history

        self.status_message: Optional[discord.Message] = None

        self.last_status: Dict = {}

        self.last_update: datetime = datetime.now()

        self.button_cooldowns: Dict[int, datetime] = {}

        self.current_media: Dict = {}

        self.playlist: List[Dict] = []

        self.current_playlist_index: int = -1

state = BotState()

def log_user_action(user_id: int, username: str, action: str):

    """Log user actions with enhanced tracking"""

    timestamp = datetime.now()

    if user_id not in state.user_actions:

        state.user_actions[user_id] = {

            "username": username,

            "actions": [],

            "total_actions": 0

        }

    state.user_actions[user_id]["actions"].append({

        "action": action,

        "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S")

    })

    state.user_actions[user_id]["total_actions"] += 1

    state.user_actions[user_id]["username"] = username  # Update in case of nickname change

    # Keep only last 20 actions per user

    if len(state.user_actions[user_id]["actions"]) > 20:

        state.user_actions[user_id]["actions"] = state.user_actions[user_id]["actions"][-20:]

    # NEW: Add to command history

    state.command_history.append({

        "user_id": user_id,

        "username": username,

        "action": action,

        "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S")

    })

    # Keep only last 50 commands in history

    if len(state.command_history) > 50:

        state.command_history = state.command_history[-50:]

def seconds_to_time(seconds: float) -> str:

    """Convert seconds to human readable time format"""

    if seconds <= 0:

        return "00:00"

    total_seconds = int(seconds)

    hours = total_seconds // 3600

    minutes = (total_seconds % 3600) // 60

    seconds = total_seconds % 60

    if hours > 0:

        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    return f"{minutes:02d}:{seconds:02d}"

def create_progress_bar(position: float, length: int = None) -> str:

    """Create a visual progress bar that spans full width"""

    length = length or Config.PROGRESS_BAR_LENGTH

    if position < 0:

        position = 0

    elif position > 1:

        position = 1

    filled = int(position * length)

    empty = length - filled

    # Spotify-style progress bar

    filled_char = "▬"

    empty_char = "▬"

    current_pos_char = "🔘"

    # Create the progress bar with current position indicator

    if filled == length:

        progress_bar = filled_char * (length - 1) + current_pos_char

    elif filled == 0:

        progress_bar = current_pos_char + empty_char * (length - 1)

    else:

        progress_bar = filled_char * (filled - 1) + current_pos_char + empty_char * empty

    return progress_bar

def get_media_info(status_data: Dict) -> Dict:
    """Extract comprehensive media information"""
    info = {
        "filename": "Unknown",
        "title": "",
        "artist": "",
        "album": "",
        "duration": "",
        "bitrate": "",
        "codec": "",
        "now_playing": "",
        "scraped_info": {}
    }

    if not status_data:

        return info

    # Try multiple ways to extract filename/title

    filename = "Unknown"

    # Method 1: Check information->meta

    if 'information' in status_data and 'meta' in status_data['information']:

        meta = status_data['information']['meta']

        if 'filename' in meta:

            filename = meta['filename']

        elif 'title' in meta:

            filename = meta['title']

    # Method 2: Check direct filename in status

    if filename == "Unknown" and 'filename' in status_data:

        filename = status_data['filename']

    # Method 3: Check information->category

    if filename == "Unknown" and 'information' in status_data and 'category' in status_data['information']:

        category = status_data['information']['category']

        if 'filename' in category:

            filename = category['filename']

        elif 'meta' in category and 'filename' in category['meta']:

            filename = category['meta']['filename']

    # Clean up filename

    if filename != "Unknown":

        # Extract just the filename without path

        filename = os.path.basename(filename)

        # Remove file extension but keep it clean

        name_without_ext = os.path.splitext(filename)[0]

        # Only use the cleaned name if it's not empty

        if name_without_ext.strip():

            filename = name_without_ext

        # Replace underscores and dashes with spaces

        filename = filename.replace('_', ' ').replace('-', ' ').strip()

        # Limit length for display

        if len(filename) > 60:

            filename = filename[:57] + "..."

    info['filename'] = filename

    # Get title from meta if available, otherwise use filename

    title = ""

    if 'information' in status_data and 'meta' in status_data['information']:

        meta = status_data['information']['meta']

        title = meta.get('title', '')

        info['artist'] = meta.get('artist', '')

        info['album'] = meta.get('album', '')

        info['now_playing'] = meta.get('now_playing', '')

    # Use title if available, otherwise use cleaned filename

    info['title'] = title if title else info['filename']

    # Technical info

    if 'length' in status_data:

        info['duration'] = seconds_to_time(status_data['length'])

    return info

async def get_playlist_info() -> List[Dict]:

    """Get current playlist information"""

    try:

        playlist_data = await vlc.get_playlist()

        if not playlist_data:

            return []

        playlist_items = []

        # VLC playlist structure can vary, try different access patterns

        if 'children' in playlist_data:

            # Standard playlist structure

            for child in playlist_data['children']:

                if 'children' in child:

                    # This is a node with children (like Playlist)

                    for item in child['children']:

                        if item.get('type') == 'node':

                            continue

                        playlist_items.append({

                            'name': item.get('name', 'Unknown'),

                            'duration': item.get('duration', 0),

                            'uri': item.get('uri', ''),

                            'current': item.get('current', False)

                        })

                else:

                    # Direct playlist items

                    if child.get('type') == 'node':

                        continue

                    playlist_items.append({

                        'name': child.get('name', 'Unknown'),

                        'duration': child.get('duration', 0),

                        'uri': child.get('uri', ''),

                        'current': child.get('current', False)

                    })

        state.playlist = playlist_items

        # Find current item index

        for i, item in enumerate(playlist_items):

            if item.get('current'):

                state.current_playlist_index = i

                break

        return playlist_items

    except Exception as e:

        logger.error(f"Error getting playlist: {e}")

        return []

async def create_vlc_embed(status_data: Optional[Dict] = None, last_action_by: str = None, action_type: str = None) -> discord.Embed:
    """Create comprehensive VLC status embed"""

    # Handle disconnected state
    if not status_data:
        embed = discord.Embed(
            title="🎬 VLC Player - Disconnected",
            description="❌ Cannot connect to VLC Media Player\n\n**Troubleshooting:**\n• Check VLC is running\n• Verify HTTP interface is enabled\n• Confirm password is correct",
            color=Config.EMBED_COLOR_ERROR,
            timestamp=datetime.now()
        )
        if vlc.last_error:
            embed.add_field(
                name="🔧 Connection Error",
                value=f"```{vlc.last_error[:200]}```",
                inline=False
            )
        embed.add_field(
            name="🔗 Connection Info",
            value=f"**Host:** {Config.VLC_HOST}:{Config.VLC_PORT}\n**Attempts:** {vlc.connection_attempts}/{Config.MAX_RECONNECT_ATTEMPTS}",
            inline=True
        )
        return embed

    # Extract status information
    state_raw = status_data.get('state', 'unknown')
    position = status_data.get('position', 0)
    length = status_data.get('length', 0)
    volume = status_data.get('volume', 0)

    # Get media information
    media_info = get_media_info(status_data)

    # FOR SCRAPING:
    scraped_info = {}
    if Config.ENABLE_MEDIA_INFO_SCRAPING and media_info['title'] and media_info['title'] != "Unknown":
        logger.info(f"🎬 Attempting to scrape info for: {media_info['title']}")
        scraped_info = await media_scraper.search_media_info(media_info['title'])
        media_info['scraped_info'] = scraped_info
        if scraped_info:
            logger.info(f"✅ Scraped info: {scraped_info.get('title', 'Unknown')}")
        else:
            logger.warning("❌ No scraped info found")

    # Get playlist information
    playlist_info = await get_playlist_info()
    has_playlist = len(playlist_info) > 1  # More than current item

    # Calculate times
    current_seconds = position * length if length > 0 else 0
    total_seconds = length if length > 0 else 0
    remaining_seconds = max(0, total_seconds - current_seconds)
    current_time = seconds_to_time(current_seconds)
    total_time = seconds_to_time(total_seconds)
    remaining_time = seconds_to_time(remaining_seconds)

    # Create progress bar (full width)
    progress_bar = create_progress_bar(position) if length > 0 else create_progress_bar(0)

    # Determine embed color and state icon
    state_colors = {
        'playing': (Config.EMBED_COLOR_PLAYING, "▶️ Playing"),
        'paused': (Config.EMBED_COLOR_PAUSED, "⏸️ Paused"),
        'stopped': (Config.EMBED_COLOR_STOPPED, "⏹️ Stopped")
    }
    color, state_icon = state_colors.get(state_raw, (discord.Color.blue(), f"❓ {state_raw.title()}"))

    # ENHANCE TITLE AND DESCRIPTION:
    display_title = media_info['title']
    if scraped_info and scraped_info.get('title'):
        display_title = scraped_info['title']

    # Start with title
    description = f"**{display_title}**"
    
    # Add artist/album info if available (for music)
    if media_info['artist']:
        description = f"**{display_title}**\nby {media_info['artist']}"
        if media_info['album']:
            description += f"\n*from {media_info['album']}*"

    # Create embed
    embed = discord.Embed(
        title="🎬 VLC Media Player",
        color=color,
        timestamp=datetime.now()
    )

    # Set the main description (title + artist info)
    embed.description = description

    # ADD PLOT SUMMARY with smart truncation
    if scraped_info and scraped_info.get('plot'):
        plot = scraped_info['plot']
        # Smart truncation - find natural breaking points
        if len(plot) > 300:
            # Try to break at the last sentence end before 300 characters
            last_period = plot[:300].rfind('. ')
            last_exclamation = plot[:300].rfind('! ')
            last_question = plot[:300].rfind('? ')
            
            # Find the latest natural breaking point
            break_point = max(last_period, last_exclamation, last_question)
            
            if break_point > 150:  # Ensure we have enough content
                plot = plot[:break_point + 1] + ".."  # Include the punctuation
            else:
                # If no good breaking point, break at last space before 297 chars
                last_space = plot[:297].rfind(' ')
                if last_space > 100:
                    plot = plot[:last_space] + "..."
                else:
                    plot = plot[:297] + "..."
        
        embed.add_field(
            name="📖 Plot",
            value=plot,
            inline=False
        )

    # ADD MEDIA INFO BAR:
    if scraped_info:
        rating_info = []
        if scraped_info.get('rating'):
            rating_info.append(f"⭐ {scraped_info['rating']}")
        if scraped_info.get('genre'):
            rating_info.append(f"🎭 {scraped_info['genre']}")
        
        if rating_info:
            embed.add_field(
                name="🎭 Media Info",
                value=" • ".join(rating_info),
                inline=False
            )

    # Status fields
    embed.add_field(
        name="📊 Status",
        value=state_icon,
        inline=True
    )

    embed.add_field(
        name="🔊 Volume",
        value=f"{volume}%",
        inline=True
    )

    if total_seconds > 0:
        embed.add_field(
            name="⏱️ Duration",
            value=media_info['duration'],
            inline=True
        )

    # Progress information
    if total_seconds > 0:
        # Modified: Show both start and end time in same field
        embed.add_field(
            name="🕐 Progress",
            value=f"{current_time} / {total_time}",
            inline=True
        )

        embed.add_field(
            name="⏳ Remaining",
            value=remaining_time,
            inline=True
        )

        # Progress percentage
        progress_percent = (position * 100) if position > 0 else 0
        embed.add_field(
            name="📈 Complete",
            value=f"{progress_percent:.1f}%",
            inline=True
        )

        # Visual progress bar with times at start and end - Spotify style
        embed.add_field(
            name="🎵 Progress",
            value=f"{current_time} {progress_bar} {total_time}",
            inline=False
        )

    # Playlist information
    if has_playlist:
        current_idx = state.current_playlist_index
        total_items = len(playlist_info)

        # Get list of playlist items with their names
        playlist_text = f"**{current_idx + 1}/{total_items}** items in playlist\n\n"

        # Show current and next few items with their sequence numbers
        items_to_show = []
        start_idx = max(0, current_idx - 1)  # Show one before current if available
        end_idx = min(total_items, current_idx + 4)  # Show current + next 3

        for i in range(start_idx, end_idx):
            item_name = playlist_info[i]['name']
            # Clean up item name same way as current media
            if item_name != "Unknown":
                item_name = os.path.basename(item_name)
                name_without_ext = os.path.splitext(item_name)[0]
                if name_without_ext.strip():
                    item_name = name_without_ext
                item_name = item_name.replace('_', ' ').replace('-', ' ').strip()

            if len(item_name) > 35:
                item_name = item_name[:32] + "..."

            if i == current_idx:
                items_to_show.append(f"**▶ {i + 1}. {item_name}** (Now Playing)")
            else:
                items_to_show.append(f"{i + 1}. {item_name}")

        playlist_text += "\n".join(items_to_show)

        embed.add_field(
            name="📋 Playlist",
            value=playlist_text,
            inline=False
        )

    # Connection status
    connection_status = "🟢 Connected" if vlc.is_connected else f"🔴 Connection Issues ({vlc.connection_attempts} attempts)"
    embed.add_field(
        name="🔗 VLC Connection",
        value=connection_status,
        inline=True
    )

    # ADD THUMBNAIL:
    if Config.SHOW_THUMBNAIL and scraped_info and scraped_info.get('image'):
        embed.set_thumbnail(url=scraped_info['image'])

    # Modified footer to show persistent pause info
    footer_text = "Use the buttons below to control playback • Updates every 3 seconds"

    # Show who paused until media is played back
    if state.last_pauser_id is not None and state_raw == 'paused':
        pauser_name = state.last_pauser_name or "Unknown"
        if state.last_pause_time:
            time_ago = datetime.now() - state.last_pause_time
            if time_ago.total_seconds() < 60:
                time_str = f"{int(time_ago.total_seconds())}s ago"
            elif time_ago.total_seconds() < 3600:
                time_str = f"{int(time_ago.total_seconds()/60)}m ago"
            else:
                time_str = f"{int(time_ago.total_seconds()/3600)}h ago"
            footer_text = f"Paused by {pauser_name} ({time_str}) • Use buttons to control playback"
        else:
            footer_text = f"Paused by {pauser_name} • Use buttons to control playback"
    elif last_action_by and action_type:
        footer_text = f"Last action: {action_type} by {last_action_by} • Updates every 3 seconds"

    embed.set_footer(text=footer_text)

    # Store current media info for bot status
    state.current_media = {
        'title': display_title,
        'state': state_raw,
        'position': position,
        'length': length,
        'has_playlist': has_playlist,
        'playlist_index': state.current_playlist_index,
        'playlist_total': len(playlist_info)
    }

    return embed

class VLCControlView(discord.ui.View):
    """Enhanced control view with cooldowns, role restrictions, and better error handling"""
    
    def __init__(self):
        super().__init__(timeout=None)

    def has_required_role(self, user: discord.Member) -> bool:
        """Check if user has the required role"""
        # If no role is configured, allow all users
        if not Config.REQUIRED_ROLE_ID:
            return True
        
        # Check if user has the required role
        return any(role.id == Config.REQUIRED_ROLE_ID for role in user.roles)

    def check_cooldown(self, user_id: int) -> bool:
        """Check if user is on cooldown"""
        now = datetime.now()
        if user_id in state.button_cooldowns:
            time_diff = (now - state.button_cooldowns[user_id]).total_seconds()
            return time_diff >= Config.BUTTON_COOLDOWN
        return True

    def set_cooldown(self, user_id: int):
        """Set cooldown for user"""
        state.button_cooldowns[user_id] = datetime.now()

    def check_playlist_permission(self, user: discord.Member) -> bool:
        """Check if user has permission to control playlist"""
        if not Config.ADMIN_ONLY_PLAYLIST:
            return True
        return is_admin(user)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Global check for all button interactions"""
        if not self.has_required_role(interaction.user):
            await interaction.response.send_message(
                f"❌ You need the required role to use VLC controls.", 
                ephemeral=True
            )
            return False
        
        if not self.check_cooldown(interaction.user.id):
            await interaction.response.send_message("⏱️ Please wait before using buttons again.", ephemeral=True)
            return False
        
        return True

    # Row 0: Playlist navigation and main controls
    @discord.ui.button(label="⏮️", style=discord.ButtonStyle.secondary, custom_id="previous_track", row=0)
    async def previous_track(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.check_playlist_permission(interaction.user):
            await interaction.response.send_message("❌ Only admins can control playlist navigation.", ephemeral=True)
            return

        result = await vlc.previous()
        if result is not None:
            self.set_cooldown(interaction.user.id)
            log_user_action(interaction.user.id, interaction.user.display_name, "previous_track")
            await self.update_status_embed(interaction, "⏮️ Previous Track", interaction.user.display_name)
        else:
            await interaction.response.send_message("❌ Failed to go to previous track. VLC might be disconnected.", ephemeral=True)

    @discord.ui.button(label="⏪ -10s", style=discord.ButtonStyle.secondary, custom_id="seek_back", row=0)
    async def seek_back(self, interaction: discord.Interaction, button: discord.ui.Button):
        if Config.ADMIN_ONLY_SEEK and not is_admin(interaction.user):
            await interaction.response.send_message("❌ Only admins can seek in this server.", ephemeral=True)
            return

        result = await vlc.seek_relative(-10)
        if result is not None:
            self.set_cooldown(interaction.user.id)
            log_user_action(interaction.user.id, interaction.user.display_name, "seek_back_10s")
            await self.update_status_embed(interaction, "⏪ Seeked -10s", interaction.user.display_name)
        else:
            await interaction.response.send_message("❌ Failed to seek backward. VLC might be disconnected.", ephemeral=True)

    @discord.ui.button(label="⏸️", style=discord.ButtonStyle.danger, custom_id="pause_btn", row=0)
    async def pause_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        result = await vlc.pause()
        if result is not None:
            # Store pauser info persistently
            state.last_pauser_id = interaction.user.id
            state.last_pauser_name = interaction.user.display_name
            state.last_pause_time = datetime.now()

            self.set_cooldown(interaction.user.id)
            log_user_action(interaction.user.id, interaction.user.display_name, "pause")
            await self.update_status_embed(interaction, "⏸️ Paused", interaction.user.display_name)
        else:
            await interaction.response.send_message("❌ Failed to pause. VLC might be disconnected.", ephemeral=True)

    @discord.ui.button(label="▶️", style=discord.ButtonStyle.success, custom_id="play_btn", row=0)
    async def play_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Admin override check
        if state.last_pauser_id is not None and interaction.user.id != state.last_pauser_id and not is_admin(interaction.user):
            pauser_name = state.last_pauser_name or "Unknown"
            await interaction.response.send_message(
                f"❌ Only **{pauser_name}** or an admin can resume playback.\nUse `/who_paused` to see who paused last.",
                ephemeral=True
            )
            return

        result = await vlc.play()
        if result is not None:
            # Clear pauser info when resumed
            state.last_pauser_id = None
            state.last_pauser_name = None
            state.last_pause_time = None

            self.set_cooldown(interaction.user.id)
            log_user_action(interaction.user.id, interaction.user.display_name, "play")
            await self.update_status_embed(interaction, "▶️ Resumed", interaction.user.display_name)
        else:
            await interaction.response.send_message("❌ Failed to resume. VLC might be disconnected.", ephemeral=True)

    @discord.ui.button(label="+10s ⏩", style=discord.ButtonStyle.secondary, custom_id="seek_forward", row=0)
    async def seek_forward(self, interaction: discord.Interaction, button: discord.ui.Button):
        if Config.ADMIN_ONLY_SEEK and not is_admin(interaction.user):
            await interaction.response.send_message("❌ Only admins can seek in this server.", ephemeral=True)
            return

        result = await vlc.seek_relative(10)
        if result is not None:
            self.set_cooldown(interaction.user.id)
            log_user_action(interaction.user.id, interaction.user.display_name, "seek_forward_10s")
            await self.update_status_embed(interaction, "⏩ Seeked +10s", interaction.user.display_name)
        else:
            await interaction.response.send_message("❌ Failed to seek forward. VLC might be disconnected.", ephemeral=True)

    # Row 1: Additional controls and next track
    @discord.ui.button(label="⏭️", style=discord.ButtonStyle.secondary, custom_id="next_track", row=1)
    async def next_track(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.check_playlist_permission(interaction.user):
            await interaction.response.send_message("❌ Only admins can control playlist navigation.", ephemeral=True)
            return

        result = await vlc.next()
        if result is not None:
            self.set_cooldown(interaction.user.id)
            log_user_action(interaction.user.id, interaction.user.display_name, "next_track")
            await self.update_status_embed(interaction, "⏭️ Next Track", interaction.user.display_name)
        else:
            await interaction.response.send_message("❌ Failed to go to next track. VLC might be disconnected.", ephemeral=True)

    @discord.ui.button(label="📊 Stats", style=discord.ButtonStyle.primary, custom_id="show_stats", row=1)
    async def show_stats(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Show detailed statistics"""
        embed = discord.Embed(
            title="📊 VLC Bot Statistics",
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )
        # Connection stats
        embed.add_field(
            name="🔗 Connection Status",
            value=f"{'🟢 Connected' if vlc.is_connected else '🔴 Disconnected'}\nHost: {Config.VLC_HOST}:{Config.VLC_PORT}",
            inline=True
        )
        # User activity stats
        total_actions = sum(user_data["total_actions"] for user_data in state.user_actions.values())
        active_users = len(state.user_actions)
        embed.add_field(
            name="👥 Activity",
            value=f"Active Users: {active_users}\nTotal Actions: {total_actions}",
            inline=True
        )
        # Current media info
        if state.current_media:
            embed.add_field(
                name="🎵 Current Media",
                value=f"**{state.current_media['title']}**\nState: {state.current_media['state'].title()}",
                inline=False
            )
        # Playlist info
        if state.playlist:
            embed.add_field(
                name="📋 Playlist",
                value=f"{len(state.playlist)} items\nCurrent: {state.current_playlist_index + 1}/{len(state.playlist)}",
                inline=True
            )
        # Top users
        if state.user_actions:
            top_users = sorted(
                state.user_actions.items(),
                key=lambda x: x[1]["total_actions"],
                reverse=True
            )[:3]
            top_users_text = "\n".join([
                f"{i+1}. **{user_data['username']}**: {user_data['total_actions']} actions"
                for i, (user_id, user_data) in enumerate(top_users)
            ])
            embed.add_field(
                name="🏆 Most Active Users",
                value=top_users_text,
                inline=False
            )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    # History button
    @discord.ui.button(label="📜 History", style=discord.ButtonStyle.gray, custom_id="show_history", row=1)
    async def show_history(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Show command history"""
        if not state.command_history:
            await interaction.response.send_message("📭 No command history available yet.", ephemeral=True)
            return
        embed = discord.Embed(
            title="📜 Command History",
            description="Recent commands executed by users",
            color=discord.Color.gold(),
            timestamp=datetime.now()
        )
        # Show last 10 commands
        recent_commands = state.command_history[-10:]
        history_text = ""

        for i, cmd in enumerate(reversed(recent_commands), 1):
            action_emoji = {
                "pause": "⏸️",
                "play": "▶️", 
                "next_track": "⏭️",
                "previous_track": "⏮️",
                "seek_forward_10s": "⏩",
                "seek_back_10s": "⏪",
                "force_play": "🔓"
            }.get(cmd["action"], "🎛️")

            history_text += f"{action_emoji} **{cmd['username']}** used `{cmd['action']}` at {cmd['timestamp']}\n"

        embed.add_field(
            name="Recent Commands",
            value=history_text,
            inline=False
        )

        embed.set_footer(text=f"Showing last {len(recent_commands)} commands")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="🔄 Refresh", style=discord.ButtonStyle.gray, custom_id="manual_refresh", row=1)
    async def manual_refresh(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Manually refresh the status"""
        await self.update_status_embed(interaction, "🔄 Refreshed", interaction.user.display_name)

    async def update_status_embed(self, interaction: discord.Interaction, action_type: str, username: str):
        """Update the status embed with new information"""
        await interaction.response.defer()
        # Small delay to let VLC process the command
        await asyncio.sleep(0.2)
        try:
            status_data = await vlc.get_status()
            embed = await create_vlc_embed(status_data, username, action_type)
            await interaction.edit_original_response(embed=embed, view=self)
        except Exception as e:
            logger.error(f"Error updating status embed: {e}")
            await interaction.followup.send("❌ Failed to update status. Please try again.", ephemeral=True)

async def update_bot_status():

    """Update bot's Discord status to show current media with Spotify-style display"""

    if not Config.SHOW_PROGRESS_IN_STATUS or not state.current_media:

        # Set default status if no media

        activity_type = getattr(discord.ActivityType, Config.BOT_STATUS_TYPE, discord.ActivityType.watching)

        activity = discord.Activity(type=activity_type, name=Config.BOT_STATUS_TEXT)

        await bot.change_presence(activity=activity)

        return

    try:

        title = state.current_media.get('title', 'Unknown Media')

        state_raw = state.current_media.get('state', 'unknown')

        # Truncate title if too long (Discord status has character limit)

        if len(title) > 40:

            title = title[:37] + "..."

        if state_raw == 'playing':

            # Show playing status with title

            status_text = f"{title}"

        elif state_raw == 'paused':

            status_text = f"⏸️ {title}"

        else:

            status_text = Config.BOT_STATUS_TEXT

        # Add playlist info if available

        if state.current_media.get('has_playlist'):

            current_idx = state.current_media.get('playlist_index', 0) + 1

            total_items = state.current_media.get('playlist_total', 0)

            status_text = f"[{current_idx}/{total_items}] {status_text}"

        # Set bot activity

        activity_type = getattr(discord.ActivityType, Config.BOT_STATUS_TYPE, discord.ActivityType.watching)

        activity = discord.Activity(type=activity_type, name=status_text)

        await bot.change_presence(activity=activity)

    except Exception as e:

        logger.error(f"Error updating bot status: {e}")

        # Fallback to default status

        activity_type = getattr(discord.ActivityType, Config.BOT_STATUS_TYPE, discord.ActivityType.watching)

        activity = discord.Activity(type=activity_type, name=Config.BOT_STATUS_TEXT)

        await bot.change_presence(activity=activity)

@bot.event

async def on_ready():

    logger.info(f'{bot.user} has connected to Discord!')

    logger.info(f'Bot is ready to control VLC at {Config.VLC_HOST}:{Config.VLC_PORT}')

    # Validate configuration

    if not Config.DISCORD_BOT_TOKEN:

        logger.error("DISCORD_BOT_TOKEN not found in .env file!")

        return

    if not Config.STATUS_CHANNEL_ID:

        logger.warning("STATUS_CHANNEL_ID not set - persistent embed will not work")

    # Add persistent view

    bot.add_view(VLCControlView())

    # Test VLC connection

    status = await vlc.get_status()

    if status:

        logger.info("✓ VLC connection successful")

    else:

        logger.warning("✗ VLC connection failed - check configuration")

    # Start status update loop

    if Config.STATUS_CHANNEL_ID:

        update_status_embed.start()

    # Sync slash commands

    try:

        if Config.ALLOWED_GUILD_ID:

            guild = discord.Object(id=Config.ALLOWED_GUILD_ID)

            synced = await bot.tree.sync(guild=guild)

            logger.info(f"Synced {len(synced)} command(s) to guild {Config.ALLOWED_GUILD_ID}")

        else:

            synced = await bot.tree.sync()

            logger.info(f"Synced {len(synced)} global command(s)")

    except Exception as e:

        logger.error(f"Failed to sync commands: {e}")

@tasks.loop(seconds=Config.UPDATE_INTERVAL)

async def update_status_embed():

    """Periodically update the status embed"""

    if not Config.STATUS_CHANNEL_ID:

        return

    try:

        channel = bot.get_channel(Config.STATUS_CHANNEL_ID)

        if not channel:

            logger.error(f"Could not find channel with ID {Config.STATUS_CHANNEL_ID}")

            return

        # Get current VLC status

        status_data = await vlc.get_status()

        # Update bot's Discord status

        await update_bot_status()

        # Only update embed if status changed or no message exists

        if not state.status_message or status_has_changed(status_data, state.last_status):

            embed = await create_vlc_embed(status_data)

            view = VLCControlView()

            if state.status_message:

                try:

                    await state.status_message.edit(embed=embed, view=view)

                except discord.NotFound:

                    # Message was deleted, send new one

                    state.status_message = await channel.send(embed=embed, view=view)

            else:

                # Find existing bot message or send new one

                async for message in channel.history(limit=10):

                    if message.author.id == bot.user.id:

                        state.status_message = message

                        await state.status_message.edit(embed=embed, view=view)

                        break

                else:

                    state.status_message = await channel.send(embed=embed, view=view)

            state.last_status = status_data or {}

            state.last_update = datetime.now()

    except Exception as e:

        logger.error(f"Error in status update loop: {e}")

def status_has_changed(new_status: Dict, old_status: Dict) -> bool:

    """Check if status has changed significantly"""

    if not new_status and not old_status:

        return False

    if bool(new_status) != bool(old_status):

        return True

    # Compare key fields

    fields_to_check = ['state', 'position', 'volume', 'length']

    for field in fields_to_check:

        if new_status.get(field) != old_status.get(field):

            return True

    return False

# Slash commands

@bot.tree.command(name="setup", description="Setup the VLC control panel")

async def setup_command(interaction: discord.Interaction):

    """Setup command to initialize the control panel"""

    if Config.ALLOWED_GUILD_ID and interaction.guild_id != Config.ALLOWED_GUILD_ID:

        await interaction.response.send_message("❌ This bot is not authorized for this server.", ephemeral=True)

        return

    if not is_admin(interaction.user):

        await interaction.response.send_message("❌ You need administrator permissions to setup the bot.", ephemeral=True)

        return

    embed = await create_vlc_embed()

    view = VLCControlView()

    await interaction.response.send_message(embed=embed, view=view)

    state.status_message = await interaction.original_response()

    logger.info(f"VLC control panel setup by {interaction.user.display_name}")

@bot.tree.command(name="who_paused", description="Find out who paused the playback")

async def who_paused(interaction: discord.Interaction):

    """Show who last paused the playback"""

    if state.last_pauser_id is None:

        await interaction.response.send_message("🎬 Playbook hasn't been paused yet.", ephemeral=True)

        return

    pauser_name = state.last_pauser_name or "Unknown"

    time_info = ""

    if state.last_pause_time:

        time_ago = datetime.now() - state.last_pause_time

        if time_ago.total_seconds() < 60:

            time_info = f" ({int(time_ago.total_seconds())} seconds ago)"

        elif time_ago.total_seconds() < 3600:

            time_info = f" ({int(time_ago.total_seconds()/60)} minutes ago)"

        else:

            time_info = f" ({int(time_ago.total_seconds()/3600)} hours ago)"

    embed = discord.Embed(

        title="⏸️ Last Paused By",

        description=f"**{pauser_name}** was the last to pause playback{time_info}.\n\nOnly this user or an admin can resume playback.",

        color=Config.EMBED_COLOR_PAUSED,

        timestamp=datetime.now()

    )

    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="force_play", description="Admin command to force resume playback")

async def force_play(interaction: discord.Interaction):

    """Force resume playback (admin only)"""

    if not is_admin(interaction.user):

        await interaction.response.send_message("❌ You need administrator permissions to use this command.", ephemeral=True)

        return

    result = await vlc.play()

    if result is not None:

        state.last_pauser_id = None

        state.last_pauser_name = None

        state.last_pause_time = None

        log_user_action(interaction.user.id, interaction.user.display_name, "force_play")

        await interaction.response.send_message("✅ Playback force resumed by admin.", ephemeral=True)

    else:

        await interaction.response.send_message("❌ Failed to resume playback. VLC might be disconnected.", ephemeral=True)

@bot.tree.command(name="playlist", description="Show current playlist")

async def playlist_command(interaction: discord.Interaction):

    """Show current playlist information"""

    try:

        playlist_info = await get_playlist_info()

        if not playlist_info:

            await interaction.response.send_message("📭 Playlist is empty.", ephemeral=True)

            return

        embed = discord.Embed(

            title="📋 Current Playlist",

            color=discord.Color.green(),

            timestamp=datetime.now()

        )

        # Show current and next few items

        current_idx = state.current_playlist_index

        total_items = len(playlist_info)

        embed.add_field(

            name="📊 Playlist Info",

            value=f"**{total_items}** items total\nCurrently playing **#{current_idx + 1}**",

            inline=False

        )

        # Show current item

        if current_idx >= 0:

            current_item = playlist_info[current_idx]

            current_name = current_item.get('name', 'Unknown')

            if len(current_name) > 50:

                current_name = current_name[:47] + "..."

            embed.add_field(

                name="🎵 Now Playing",

                value=f"**{current_name}**",

                inline=False

            )

        # Show next items

        next_items = []

        for i in range(current_idx + 1, min(current_idx + 6, total_items)):

            item = playlist_info[i]

            item_name = item.get('name', 'Unknown')

            if len(item_name) > 40:

                item_name = item_name[:37] + "..."

            next_items.append(f"**{i + 1}.** {item_name}")

        if next_items:

            embed.add_field(

                name="⏭️ Up Next",

                value="\n".join(next_items),

                inline=False

            )

        await interaction.response.send_message(embed=embed, ephemeral=True)

    except Exception as e:

        logger.error(f"Error in playlist command: {e}")

        await interaction.response.send_message("❌ Failed to get playlist information.", ephemeral=True)

@bot.event

async def on_command_error(ctx, error):

    """Handle command errors gracefully"""

    if isinstance(error, commands.CommandNotFound):

        return

    elif isinstance(error, commands.MissingPermissions):

        await ctx.send("❌ You don't have permission to use this command.")

    else:

        logger.error(f"Command error: {error}")

        await ctx.send("❌ An error occurred while executing the command.")

async def main():
    """Main async function to run the bot"""
    try:
        await bot.start(Config.DISCORD_BOT_TOKEN)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot crashed: {e}")
    finally:
        await vlc.close()
        await media_scraper.close()  # ADD THIS LINE
        if bot.is_ready():
            await bot.close()

# Run the bot
if __name__ == "__main__":
    asyncio.run(main())            