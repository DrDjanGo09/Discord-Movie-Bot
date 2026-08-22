import discord

from discord.ext import commands, tasks

import base64

import json

import os

import logging

import asyncio
import io

from datetime import datetime

from typing import Optional, Dict, Any, List, Set

from dotenv import load_dotenv
from logging.handlers import RotatingFileHandler

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
    
    # Error Handling
    ENABLE_ERROR_RECOVERY = os.getenv('ENABLE_ERROR_RECOVERY', 'true').lower() == 'true'
    MAX_ERROR_RETRIES = int(os.getenv('MAX_ERROR_RETRIES', '3'))
    ERROR_RECOVERY_DELAY = int(os.getenv('ERROR_RECOVERY_DELAY', '5'))
    ENABLE_ERROR_NOTIFICATIONS = os.getenv('ENABLE_ERROR_NOTIFICATIONS', 'true').lower() == 'true'
    
    # Mobile Optimization
    ENABLE_MOBILE_OPTIMIZATION = os.getenv('ENABLE_MOBILE_OPTIMIZATION', 'true').lower() == 'true'
    MOBILE_FRIENDLY_EMBEDS = os.getenv('MOBILE_FRIENDLY_EMBEDS', 'true').lower() == 'true'
    COMPACT_DISPLAY = os.getenv('COMPACT_DISPLAY', 'false').lower() == 'true'
    TOUCH_FRIENDLY_BUTTONS = os.getenv('TOUCH_FRIENDLY_BUTTONS', 'true').lower() == 'true'

    # Advanced Features

    ENABLE_RICH_PRESENCE = os.getenv('ENABLE_RICH_PRESENCE', 'true').lower() == 'true'

    AUTO_RECONNECT_VLC = os.getenv('AUTO_RECONNECT_VLC', 'true').lower() == 'true'

    MAX_RECONNECT_ATTEMPTS = int(os.getenv('MAX_RECONNECT_ATTEMPTS', '5'))

    RECONNECT_DELAY = int(os.getenv('RECONNECT_DELAY', '10'))
    
    # Voice Channel Sync
    ENABLE_VOICE_SYNC = os.getenv('ENABLE_VOICE_SYNC', 'true').lower() == 'true'
    VOICE_CHANNEL_ID = int(os.getenv('VOICE_CHANNEL_ID')) if os.getenv('VOICE_CHANNEL_ID') else None
    AUTO_PAUSE_EMPTY_VOICE = os.getenv('AUTO_PAUSE_EMPTY_VOICE', 'true').lower() == 'true'
    VOICE_SYNC_CHECK_INTERVAL = int(os.getenv('VOICE_SYNC_CHECK_INTERVAL', '10'))
    
    # Voice Channel Streaming Detection
    ENABLE_STREAM_DETECTION = os.getenv('ENABLE_STREAM_DETECTION', 'true').lower() == 'true'
    STREAM_DETECTION_INTERVAL = int(os.getenv('STREAM_DETECTION_INTERVAL', '5'))
    MIN_VIEWERS_FOR_TRACKING = int(os.getenv('MIN_VIEWERS_FOR_TRACKING', '1'))
    AUTO_TRACK_VIEWERS = os.getenv('AUTO_TRACK_VIEWERS', 'true').lower() == 'true'

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
    
    # Smart Controls
    ENABLE_SMART_CONTROLS = os.getenv('ENABLE_SMART_CONTROLS', 'true').lower() == 'true'
    AUTO_SKIP_INTROS = os.getenv('AUTO_SKIP_INTROS', 'false').lower() == 'true'
    INTRO_SKIP_DURATION = int(os.getenv('INTRO_SKIP_DURATION', '90'))  # seconds
    VOLUME_NORMALIZATION = os.getenv('VOLUME_NORMALIZATION', 'false').lower() == 'true'
    AUTO_QUALITY_ADJUSTMENT = os.getenv('AUTO_QUALITY_ADJUSTMENT', 'false').lower() == 'true'
    SMART_PAUSE_DETECTION = os.getenv('SMART_PAUSE_DETECTION', 'true').lower() == 'true'
    
    # Social Features
    ENABLE_SOCIAL_FEATURES = os.getenv('ENABLE_SOCIAL_FEATURES', 'true').lower() == 'true'
    ENABLE_REACTIONS = os.getenv('ENABLE_REACTIONS', 'true').lower() == 'true'
    ENABLE_COMMENTS = os.getenv('ENABLE_COMMENTS', 'true').lower() == 'true'
    ENABLE_WATCH_PARTY = os.getenv('ENABLE_WATCH_PARTY', 'true').lower() == 'true'
    REACTION_EMOJIS = os.getenv('REACTION_EMOJIS', '👍👎❤️😂😮😢😡').split(',')
    MAX_COMMENT_LENGTH = int(os.getenv('MAX_COMMENT_LENGTH', '200'))

    # Persistence
    STATS_SAVE_PATH = os.getenv('STATS_SAVE_PATH', 'watch_stats.json')
    STATS_SAVE_INTERVAL = int(os.getenv('STATS_SAVE_INTERVAL', '30'))

    # Log rotation
    LOG_MAX_BYTES = int(os.getenv('LOG_MAX_BYTES', str(1_000_000)))  # ~1MB
    LOG_BACKUP_COUNT = int(os.getenv('LOG_BACKUP_COUNT', '3'))

# Setup logging

def setup_logging():

    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    level = getattr(logging, Config.LOG_LEVEL.upper(), logging.INFO)

    handlers = [logging.StreamHandler()]

    if Config.LOG_TO_FILE:

        # Use rotating file handler to limit log file size
        file_handler = RotatingFileHandler(
            Config.LOG_FILE,
            maxBytes=Config.LOG_MAX_BYTES,
            backupCount=Config.LOG_BACKUP_COUNT,
            encoding='utf-8'
        )
        handlers.append(file_handler)

    logging.basicConfig(

        level=level,

        format=log_format,

        handlers=handlers

    )
    # Reduce noisy third-party loggers
    logging.getLogger('discord').setLevel(logging.WARNING if level > logging.DEBUG else level)
    logging.getLogger('aiohttp').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)

setup_logging()

logger = logging.getLogger(__name__)

class ErrorHandler:
    """Enhanced error handling with recovery mechanisms"""
    
    def __init__(self):
        self.error_counts = {}
        self.last_error_time = {}
        self.recovery_attempts = {}
    
    def should_retry(self, error_type: str, max_retries: int = None) -> bool:
        """Check if we should retry after an error"""
        max_retries = max_retries or Config.MAX_ERROR_RETRIES
        error_count = self.error_counts.get(error_type, 0)
        return error_count < max_retries
    
    def record_error(self, error_type: str):
        """Record an error occurrence"""
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
        self.last_error_time[error_type] = datetime.now()
    
    def reset_error_count(self, error_type: str):
        """Reset error count for successful recovery"""
        self.error_counts[error_type] = 0
        if error_type in self.recovery_attempts:
            del self.recovery_attempts[error_type]
    
    def get_error_info(self, error_type: str) -> Dict:
        """Get error information"""
        return {
            "count": self.error_counts.get(error_type, 0),
            "last_time": self.last_error_time.get(error_type),
            "should_retry": self.should_retry(error_type)
        }
    
    async def handle_vlc_error(self, error: Exception, context: str = "") -> bool:
        """Handle VLC-specific errors with recovery"""
        error_type = f"vlc_{type(error).__name__}"
        
        if not self.should_retry(error_type):
            logger.error(f"VLC error limit exceeded for {error_type}: {error}")
            return False
        
        self.record_error(error_type)
        
        # Try to recover
        try:
            if "connection" in str(error).lower():
                await asyncio.sleep(Config.ERROR_RECOVERY_DELAY)
                # Try to reconnect
                status = await vlc.get_status()
                if status:
                    self.reset_error_count(error_type)
                    logger.info(f"VLC connection recovered after {error_type}")
                    return True
            elif "timeout" in str(error).lower():
                await asyncio.sleep(Config.ERROR_RECOVERY_DELAY)
                # Retry the operation
                return True
        except Exception as recovery_error:
            logger.error(f"Error recovery failed: {recovery_error}")
        
        return False
    
    async def handle_discord_error(self, error: Exception, context: str = "") -> bool:
        """Handle Discord-specific errors"""
        error_type = f"discord_{type(error).__name__}"
        
        if not self.should_retry(error_type):
            logger.error(f"Discord error limit exceeded for {error_type}: {error}")
            return False
        
        self.record_error(error_type)
        
        # Discord errors usually don't need recovery, just logging
        logger.warning(f"Discord error in {context}: {error}")
        return True

# Global error handler
error_handler = ErrorHandler()

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

# Tracks whether on_ready's one-time startup work has already run, since
# on_ready can fire again after a reconnect and must not repeat it.
_bot_ready_once = False

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
            
            # Use enhanced error handling
            if Config.ENABLE_ERROR_RECOVERY:
                recovery_success = await error_handler.handle_vlc_error(e, f"VLC API request to {endpoint}")
                if recovery_success:
                    # Retry the request
                    try:
                        await self._ensure_session()
                        async with self.session.get(url, params=params or {}) as response:
                            if response.status == 200:
                                self.connection_attempts = 0
                                self.last_error = None
                                text = await response.text()
                                return json.loads(text) if text.strip() else {}
                    except Exception as retry_error:
                        logger.error(f"VLC retry failed: {retry_error}")
            
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

    async def set_volume(self, volume: int) -> Optional[Dict]:
        """Set VLC volume (0-100 mapped to 0-512)"""
        # Map Discord's 0-100% to VLC's 0-512%
        vlc_volume = int((volume / 100) * 512)
        return await self._make_request("status.json", {"command": "volume", "val": str(vlc_volume)})
    
    async def get_volume(self) -> Optional[int]:
        """Get current VLC volume (512 range mapped back to 0-100)"""
        status = await self.get_status()
        if status and 'volume' in status:
            vlc_volume = status['volume']
            # Map VLC's 0-512 back to Discord's 0-100
            return int((vlc_volume / 512) * 100)
        return None
    
    async def set_playback_rate(self, rate: float) -> Optional[Dict]:
        """Set playback rate (0.25-4.0)"""
        return await self._make_request("status.json", {"command": "rate", "val": str(rate)})
    
    async def get_playback_rate(self) -> Optional[float]:
        """Get current playback rate"""
        status = await self.get_status()
        return status.get('rate', 1.0) if status else None
    
    async def set_audio_track(self, track_id: int) -> Optional[Dict]:
        """Set audio track by ID"""
        return await self._make_request("status.json", {"command": "audio_track", "val": str(track_id)})
    
    async def set_subtitle_track(self, track_id: int) -> Optional[Dict]:
        """Set subtitle track by ID"""
        return await self._make_request("status.json", {"command": "subtitle_track", "val": str(track_id)})
    
    async def toggle_subtitles(self) -> Optional[Dict]:
        """Toggle subtitles on/off"""
        return await self._make_request("status.json", {"command": "subtitle_track", "val": "-1"})
    
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
    """Enhanced media scraper with multiple sources and better fallback strategies"""
    
    def __init__(self):
        self.session = None
        self.cache = {}
        self.source_priority = ['imdb', 'tmdb', 'omdb', 'justwatch']
        
    async def _ensure_session(self):
        if self.session is None or self.session.closed:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Cache-Control': 'max-age=0'
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
    
        # If the name is still too long, take the first few words (less aggressive)
        words = name.split()
        if len(words) > 8:
            name = ' '.join(words[:6])  # Keep first 6 words to preserve context
    
        logger.info(f"🔧 Cleaned filename: '{filename}' -> '{name}'")
        return name
    
    async def search_media_info(self, media_name: str) -> Dict[str, Any]:
        """Enhanced search for media information using multiple sources and strategies"""
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
            
            # Try multiple sources in priority order
            info = {}
            for source in self.source_priority:
                try:
                    if source == 'imdb':
                        info = await self._search_imdb_enhanced(clean_name)
                    elif source == 'tmdb':
                        info = await self._search_tmdb_public(clean_name)
                    elif source == 'omdb':
                        info = await self._search_omdb_public(clean_name)
                    elif source == 'justwatch':
                        info = await self._search_justwatch_public(clean_name)
                    
                    if info and info.get('title'):
                        logger.info(f"✅ Found info via {source.upper()}: {info.get('title')}")
                        break
                        
                except Exception as e:
                    logger.warning(f"⚠️ {source.upper()} search failed: {e}")
                    continue
            
            # If no results, try fallback strategies
            if not info or not info.get('title'):
                info = await self._fallback_search_strategies(clean_name)
            
            if info and info.get('title'):
                logger.info(f"✅ Final result: {info.get('title')}")
                if info.get('plot'):
                    logger.info(f"📖 Plot: {info['plot'][:100]}...")
            else:
                logger.warning(f"❌ No media info found after all strategies")
            
            self.cache[cache_key] = info
            return info
        
        except Exception as e:
            logger.error(f"Error scraping media info for '{clean_name}': {e}")
            return {}
    
    async def _fallback_search_strategies(self, clean_name: str) -> Dict[str, Any]:
        """Try various fallback search strategies"""
        strategies = [
            # Strategy 1: Remove year
            lambda: re.sub(r'\s+\d{4}$', '', clean_name).strip(),
            # Strategy 2: First 3 words only
            lambda: ' '.join(clean_name.split()[:3]) if len(clean_name.split()) > 3 else clean_name,
            # Strategy 3: Remove common words
            lambda: re.sub(r'\b(the|a|an|and|or|but|in|on|at|to|for|of|with|by)\b', '', clean_name, flags=re.IGNORECASE).strip(),
            # Strategy 4: Remove special characters
            lambda: re.sub(r'[^\w\s]', ' ', clean_name).strip()
        ]
        
        for i, strategy in enumerate(strategies, 1):
            try:
                modified_name = strategy()
                if modified_name != clean_name and modified_name.strip():
                    logger.info(f"🔄 Fallback strategy {i}: '{modified_name}'")
                    # Try IMDb with modified name
                    info = await self._search_imdb_enhanced(modified_name)
                    if info and info.get('title'):
                        return info
            except Exception as e:
                logger.warning(f"Fallback strategy {i} failed: {e}")
                continue
        
        return {}
    
    async def _search_imdb_enhanced(self, media_name: str) -> Dict[str, Any]:
        """Enhanced IMDb search with better selectors and error handling"""
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
                
                    # Enhanced selectors for different IMDb layouts
                    selectors = [
                        '[data-testid="find-results-section-title"] .ipc-metadata-list-summary-item',
                        'li.find-result-item',
                        '.find-result',
                        '.find-title-result',
                        '.findSection:first-child .findList tr',
                        '.result_text a'  # Alternative selector
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
                
                    # Extract title and link with multiple methods
                    title_element = None
                    for method in [result.find, result.select_one]:
                        title_element = method('a')
                        if title_element:
                            break
                    
                    if not title_element:
                        return {}
                
                    title = title_element.get_text().strip()
                    movie_link = title_element.get('href', '')
                
                    # Get image with fallback
                    img_element = None
                    for method in [result.find, result.select_one]:
                        img_element = method('img')
                        if img_element:
                            break
                    
                    image_url = img_element.get('src', '') if img_element else ""
                
                    # Determine media type with better detection
                    media_type = 'movie'
                    result_text = str(result).lower()
                    if any(keyword in result_text for keyword in ['series', 'tv', 'episode', 'season']):
                        media_type = 'tv'
                
                    # Get details from movie/TV page
                    details = await self._get_imdb_details_enhanced(movie_link) if movie_link else {}
                
                    return {
                        'title': title,
                        'image': image_url,
                        'plot': details.get('plot', ''),
                        'rating': details.get('rating', ''),
                        'genre': details.get('genre', ''),
                        'year': details.get('year', ''),
                        'type': media_type,
                        'source': 'imdb'
                    }
                else:
                    logger.warning(f"IMDb search returned status: {response.status}")
                    return {}
                
        except Exception as e:
            logger.error(f"IMDb enhanced search error: {e}")
            return {}
    
    async def _search_tmdb_public(self, media_name: str) -> Dict[str, Any]:
        """Search TheMovieDB public website"""
        try:
            # TMDB search without API key using their public search
            search_url = "https://www.themoviedb.org/search"
            params = {'query': media_name}
            
            async with self.session.get(search_url, params=params) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Find first result
                    result = soup.select_one('.card.v4 .title a') or soup.select_one('.search_results .title a')
                    if not result:
                        return {}
                    
                    title = result.get_text().strip()
                    link = result.get('href', '')
                    
                    # Get details from TMDB page
                    details = await self._get_tmdb_details_public(link) if link else {}
                    
                    return {
                        'title': title,
                        'image': details.get('image', ''),
                        'plot': details.get('plot', ''),
                        'rating': details.get('rating', ''),
                        'genre': details.get('genre', ''),
                        'year': details.get('year', ''),
                        'type': details.get('type', 'movie'),
                        'source': 'tmdb'
                    }
                else:
                    return {}
                    
        except Exception as e:
            logger.error(f"TMDB search error: {e}")
            return {}
    
    async def _search_omdb_public(self, media_name: str) -> Dict[str, Any]:
        """Search OMDB public website"""
        try:
            # OMDB has a public search interface
            search_url = "https://www.omdb.org/search"
            params = {'q': media_name}
            
            async with self.session.get(search_url, params=params) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Find first result
                    result = soup.select_one('.search-result-item') or soup.select_one('.movie-item')
                    if not result:
                        return {}
                    
                    title_elem = result.select_one('h3 a') or result.select_one('.title a')
                    if not title_elem:
                        return {}
                    
                    title = title_elem.get_text().strip()
                    link = title_elem.get('href', '')
                    
                    # Get details from OMDB page
                    details = await self._get_omdb_details_public(link) if link else {}
                    
                    return {
                        'title': title,
                        'image': details.get('image', ''),
                        'plot': details.get('plot', ''),
                        'rating': details.get('rating', ''),
                        'genre': details.get('genre', ''),
                        'year': details.get('year', ''),
                        'type': details.get('type', 'movie'),
                        'source': 'omdb'
                    }
                else:
                    return {}
                    
        except Exception as e:
            logger.error(f"OMDB search error: {e}")
            return {}
    
    async def _search_justwatch_public(self, media_name: str) -> Dict[str, Any]:
        """Search JustWatch public website"""
        try:
            search_url = "https://www.justwatch.com/search"
            params = {'q': media_name}
            
            async with self.session.get(search_url, params=params) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Find first result
                    result = soup.select_one('.title-list-row__row') or soup.select_one('.title-card')
                    if not result:
                        return {}
                    
                    title_elem = result.select_one('h3 a') or result.select_one('.title a')
                    if not title_elem:
                        return {}
                    
                    title = title_elem.get_text().strip()
                    link = title_elem.get('href', '')
                    
                    # Get image
                    img_elem = result.select_one('img')
                    image_url = img_elem.get('src', '') if img_elem else ""
                    
                    return {
                        'title': title,
                        'image': image_url,
                        'plot': '',
                        'rating': '',
                        'genre': '',
                        'year': '',
                        'type': 'movie',
                        'source': 'justwatch'
                    }
                else:
                    return {}
                    
        except Exception as e:
            logger.error(f"JustWatch search error: {e}")
            return {}
    
    async def _get_imdb_details_enhanced(self, movie_path: str) -> Dict[str, Any]:
        """Enhanced IMDb details extraction with better error handling"""
        try:
            if not movie_path.startswith('http'):
                movie_path = f"https://www.imdb.com{movie_path}"
                
            async with self.session.get(movie_path) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    info = {}
                    
                    # Enhanced plot extraction
                    plot_selectors = [
                        'span[data-testid="plot-l"]',
                        '.plot_summary .summary_text',
                        '.ipc-overflowText',
                        '[data-testid="storyline-plot-summary"]',
                        '.plot_summary_wrapper .summary_text',
                        '.summary_text'
                    ]
                    
                    for selector in plot_selectors:
                        plot_element = soup.select_one(selector)
                        if plot_element:
                            plot = plot_element.get_text().strip()
                            if plot and plot not in ["Add a plot", "Plot summary", "See full summary"]:
                                # Clean up plot text
                                plot = re.sub(r'\s+', ' ', plot)
                                info['plot'] = plot
                                break
                    
                    # Enhanced rating extraction
                    rating_selectors = [
                        '[data-testid="hero-rating-bar__aggregate-rating__score"]',
                        '.imdbRating span[class*="rating"]',
                        '.ratingValue strong',
                        '.sc-bde20123-1',
                        '.rating-other-user-rating span',
                        '.ratingValue'
                    ]
                    
                    for selector in rating_selectors:
                        rating_element = soup.select_one(selector)
                        if rating_element:
                            rating_text = rating_element.get_text().strip()
                            if rating_text and re.match(r'^\d+\.?\d*', rating_text):
                                info['rating'] = f"{rating_text}/10"
                                break
                    
                    # Enhanced genre extraction
                    genre_selectors = [
                        '[data-testid="genres"] a',
                        '.genres a',
                        '.ipc-chip-list a',
                        '.subtext a[href*="genres"]',
                        '.title_wrapper .subtext a'
                    ]
                    
                    for selector in genre_selectors:
                        genre_elements = soup.select(selector)
                        if genre_elements:
                            genres = []
                            for genre in genre_elements[:5]:  # Get up to 5 genres
                                genre_text = genre.get_text().strip()
                                if genre_text and not genre_text.isdigit():  # Skip year
                                    genres.append(genre_text)
                            if genres:
                                info['genre'] = ", ".join(genres)
                                break
                    
                    # Enhanced year extraction
                    year_selectors = [
                        '[data-testid="hero-title-block__metadata"] li',
                        '.title_wrapper .subtext a',
                        '.sc-d8941411-1',
                        '.title_wrapper .subtext',
                        '.titleYear a'
                    ]
                    
                    for selector in year_selectors:
                        year_element = soup.select_one(selector)
                        if year_element:
                            year_text = year_element.get_text().strip()
                            # Extract year from text like "2023" or "(2023)"
                            year_match = re.search(r'\(?(\d{4})\)?', year_text)
                            if year_match:
                                info['year'] = year_match.group(1)
                                break
                    
                    # Get poster image
                    poster_selectors = [
                        '[data-testid="hero-media__poster"] img',
                        '.poster img',
                        '.title-overview .poster img',
                        '.ipc-media img'
                    ]
                    
                    for selector in poster_selectors:
                        poster_element = soup.select_one(selector)
                        if poster_element:
                            poster_url = poster_element.get('src', '')
                            if poster_url and 'imdb' in poster_url:
                                info['image'] = poster_url
                                break
                    
                    return info
                else:
                    logger.warning(f"IMDb details returned status: {response.status}")
                    return {}
                    
        except Exception as e:
            logger.error(f"IMDb enhanced details error: {e}")
            return {}
    
    async def _get_tmdb_details_public(self, movie_path: str) -> Dict[str, Any]:
        """Get details from TMDB public page"""
        try:
            if not movie_path.startswith('http'):
                movie_path = f"https://www.themoviedb.org{movie_path}"
                
            async with self.session.get(movie_path) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    info = {}
                    
                    # Get plot
                    plot_element = soup.select_one('.overview') or soup.select_one('.summary')
                    if plot_element:
                        info['plot'] = plot_element.get_text().strip()
                    
                    # Get rating
                    rating_element = soup.select_one('.user_score_chart') or soup.select_one('.rating')
                    if rating_element:
                        rating_text = rating_element.get_text().strip()
                        if rating_text:
                            info['rating'] = f"{rating_text}/10"
                    
                    # Get genres
                    genre_elements = soup.select('.genres a') or soup.select('.genre a')
                    if genre_elements:
                        genres = [genre.get_text().strip() for genre in genre_elements[:3]]
                        info['genre'] = ", ".join(genres)
                    
                    # Get year
                    year_element = soup.select_one('.release_date') or soup.select_one('.year')
                    if year_element:
                        year_text = year_element.get_text().strip()
                        year_match = re.search(r'(\d{4})', year_text)
                        if year_match:
                            info['year'] = year_match.group(1)
                    
                    # Get poster
                    poster_element = soup.select_one('.poster img') or soup.select_one('.backdrop img')
                    if poster_element:
                        poster_url = poster_element.get('src', '')
                        if poster_url:
                            info['image'] = f"https://www.themoviedb.org{poster_url}" if poster_url.startswith('/') else poster_url
                    
                    return info
                else:
                    return {}
                    
        except Exception as e:
            logger.error(f"TMDB details error: {e}")
            return {}
    
    async def _get_omdb_details_public(self, movie_path: str) -> Dict[str, Any]:
        """Get details from OMDB public page"""
        try:
            if not movie_path.startswith('http'):
                movie_path = f"https://www.omdb.org{movie_path}"
                
            async with self.session.get(movie_path) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    info = {}
                    
                    # Get plot
                    plot_element = soup.select_one('.plot') or soup.select_one('.summary')
                    if plot_element:
                        info['plot'] = plot_element.get_text().strip()
                    
                    # Get rating
                    rating_element = soup.select_one('.rating') or soup.select_one('.imdb-rating')
                    if rating_element:
                        rating_text = rating_element.get_text().strip()
                        if rating_text:
                            info['rating'] = rating_text
                    
                    # Get genres
                    genre_element = soup.select_one('.genre')
                    if genre_element:
                        info['genre'] = genre_element.get_text().strip()
                    
                    # Get year
                    year_element = soup.select_one('.year') or soup.select_one('.release-date')
                    if year_element:
                        year_text = year_element.get_text().strip()
                        year_match = re.search(r'(\d{4})', year_text)
                        if year_match:
                            info['year'] = year_match.group(1)
                    
                    return info
                else:
                    return {}
                    
        except Exception as e:
            logger.error(f"OMDB details error: {e}")
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
        
        # Voice channel sync
        self.voice_channel_members: Set[int] = set()
        self.last_voice_check: datetime = datetime.now()
        self.voice_sync_enabled: bool = False
        
        # Voice channel streaming detection
        self.current_streamer: Optional[int] = None  # user_id of current streamer
        self.current_viewers: Set[int] = set()  # user_ids of current viewers
        self.stream_start_time: Optional[datetime] = None
        self.last_stream_check: datetime = datetime.now()
        self.streaming_media: Optional[str] = None  # current streaming media title
        self.viewer_sessions: Dict[int, Dict] = {}  # user_id -> {start_time, media, duration}
        self.stream_history: List[Dict] = []  # List of streaming sessions
        self.user_display_names: Dict[int, str] = {}  # user_id -> display_name
        
        # Smart controls
        self.volume_history: List[int] = []
        self.last_volume_adjustment: datetime = datetime.now()
        self.intro_skip_times: Dict[str, List[tuple]] = {}  # filename -> [(start, end), ...]
        self.quality_adjustments: Dict[str, str] = {}  # filename -> quality setting

        # Media scraping control
        self.last_scraped_query: Optional[str] = None
        
        # Social features
        self.media_reactions: Dict[str, Dict[str, List[int]]] = {}  # filename -> {emoji: [user_ids]}
        self.media_comments: Dict[str, List[Dict]] = {}  # filename -> [{"user": str, "comment": str, "timestamp": datetime}]
        self.watch_party_members: Set[int] = set()
        self.current_watch_party: Optional[str] = None
        
        # Enhanced analytics
        self.user_watch_time: Dict[int, float] = {}  # user_id -> total watch time in seconds
        self.user_genre_preferences: Dict[int, Dict[str, int]] = {}  # user_id -> {genre: count}
        self.user_media_history: Dict[int, List[Dict]] = {}  # user_id -> [{"media": str, "duration": float, "timestamp": datetime}]
        self.session_start_times: Dict[int, datetime] = {}  # user_id -> session start time
        self.daily_stats: Dict[str, Dict] = {}  # date -> {"total_watch_time": float, "unique_users": int}
        
        # Debug counters
        self.periodic_tracking_runs = 0
        self.total_watch_time_tracked = 0.0
        
        # Media recommendations
        self.recommendation_cache: Dict[str, List[Dict]] = {}  # user_id -> [recommendations]
        self.last_recommendation_update: Dict[str, datetime] = {}  # user_id -> last update time

        # Server analytics
        self.server_watch_time: Dict[int, float] = {}  # guild_id -> total watch time seconds
        self.server_user_watch_time: Dict[int, Dict[int, float]] = {}  # guild_id -> {user_id -> seconds}
        self.server_media_history: Dict[int, List[Dict]] = {}  # guild_id -> [{media, duration, user_id, timestamp}]
        self.server_genre_preferences: Dict[int, Dict[str, int]] = {}  # guild_id -> {genre -> count}

        # Persistence bookkeeping
        self.last_save_time: Optional[datetime] = None

state = BotState()

def log_user_action(user_id: int, username: str, action: str):
    """Log user actions with enhanced tracking and analytics"""
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

    # Add to command history
    state.command_history.append({
        "user_id": user_id,
        "username": username,
        "action": action,
        "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S")
    })

    # Keep only last 50 commands in history
    if len(state.command_history) > 50:
        state.command_history = state.command_history[-50:]

# --------------------
# Persistence utilities
# --------------------
def _serialize_datetime(dt: Optional[datetime]) -> Optional[str]:
    return dt.isoformat() if isinstance(dt, datetime) else None

def _deserialize_datetime(s: Optional[str]) -> Optional[datetime]:
    try:
        return datetime.fromisoformat(s) if s else None
    except Exception:
        return None

def serialize_state_for_save() -> Dict[str, Any]:
    try:
        # Convert complex objects to JSON-friendly structures
        return {
            "user_watch_time": state.user_watch_time,
            "user_genre_preferences": state.user_genre_preferences,
            "user_media_history": {
                str(uid): [
                    {
                        "media": item.get("media"),
                        "duration": float(item.get("duration", 0.0)),
                        "timestamp": _serialize_datetime(item.get("timestamp")),
                        "type": item.get("type")
                    }
                    for item in items
                ]
                for uid, items in state.user_media_history.items()
            },
            "daily_stats": {
                day: {
                    "total_watch_time": float(data.get("total_watch_time", 0.0)),
                    "unique_users": list(data.get("unique_users", set()))
                }
                for day, data in state.daily_stats.items()
            },
            "stream_history": [
                {
                    "streamer": entry.get("streamer"),
                    "streamer_name": entry.get("streamer_name"),
                    "media": entry.get("media"),
                    "start_time": _serialize_datetime(entry.get("start_time")),
                    "end_time": _serialize_datetime(entry.get("end_time")),
                    "duration": float(entry.get("duration", 0.0)),
                    "total_watch_time": float(entry.get("total_watch_time", 0.0)),
                    "viewers": entry.get("viewers", []),
                    "viewer_names": entry.get("viewer_names", []),
                }
                for entry in state.stream_history
            ],
            # Server-level analytics
            "server_watch_time": state.server_watch_time,
            "server_user_watch_time": {
                str(gid): {str(uid): float(sec) for uid, sec in users.items()}
                for gid, users in state.server_user_watch_time.items()
            },
            "server_media_history": {
                str(gid): [
                    {
                        "media": item.get("media"),
                        "duration": float(item.get("duration", 0.0)),
                        "user_id": item.get("user_id"),
                        "timestamp": _serialize_datetime(item.get("timestamp"))
                    }
                    for item in items
                ]
                for gid, items in state.server_media_history.items()
            },
            "server_genre_preferences": state.server_genre_preferences,
        }
    except Exception as e:
        logger.error(f"Error serializing state: {e}")
        return {}

def save_stats():
    try:
        payload = serialize_state_for_save()
        path = Path(Config.STATS_SAVE_PATH)
        tmp_path = path.with_suffix(path.suffix + ".tmp")
        with tmp_path.open('w', encoding='utf-8') as f:
            json.dump(payload, f, ensure_ascii=False)
        tmp_path.replace(path)
        state.last_save_time = datetime.now()
        logger.debug(f"Saved stats to {path}")
    except Exception as e:
        logger.error(f"Failed to save stats: {e}")

def load_stats():
    try:
        path = Path(Config.STATS_SAVE_PATH)
        if not path.exists():
            return
        with path.open('r', encoding='utf-8') as f:
            data = json.load(f)

        # Users
        state.user_watch_time = {int(k): float(v) for k, v in data.get("user_watch_time", {}).items()}
        state.user_genre_preferences = {
            int(k): {g: int(c) for g, c in v.items()}
            for k, v in data.get("user_genre_preferences", {}).items()
        }
        state.user_media_history = {
            int(uid): [
                {
                    "media": item.get("media"),
                    "duration": float(item.get("duration", 0.0)),
                    "timestamp": _deserialize_datetime(item.get("timestamp")),
                    "type": item.get("type")
                }
                for item in items
            ]
            for uid, items in data.get("user_media_history", {}).items()
        }
        state.daily_stats = {
            day: {
                "total_watch_time": float(stats.get("total_watch_time", 0.0)),
                "unique_users": set(int(u) for u in stats.get("unique_users", []))
            }
            for day, stats in data.get("daily_stats", {}).items()
        }
        state.stream_history = [
            {
                "streamer": entry.get("streamer"),
                "streamer_name": entry.get("streamer_name"),
                "media": entry.get("media"),
                "start_time": _deserialize_datetime(entry.get("start_time")),
                "end_time": _deserialize_datetime(entry.get("end_time")),
                "duration": float(entry.get("duration", 0.0)),
                "total_watch_time": float(entry.get("total_watch_time", 0.0)),
                "viewers": entry.get("viewers", []),
                "viewer_names": entry.get("viewer_names", []),
            }
            for entry in data.get("stream_history", [])
        ]

        # Servers
        state.server_watch_time = {int(g): float(sec) for g, sec in data.get("server_watch_time", {}).items()}
        state.server_user_watch_time = {
            int(gid): {int(uid): float(sec) for uid, sec in users.items()}
            for gid, users in data.get("server_user_watch_time", {}).items()
        }
        state.server_media_history = {
            int(gid): [
                {
                    "media": item.get("media"),
                    "duration": float(item.get("duration", 0.0)),
                    "user_id": int(item.get("user_id")) if item.get("user_id") is not None else None,
                    "timestamp": _deserialize_datetime(item.get("timestamp"))
                }
                for item in items
            ]
            for gid, items in data.get("server_media_history", {}).items()
        }
        state.server_genre_preferences = {
            int(gid): {g: int(c) for g, c in prefs.items()}
            for gid, prefs in data.get("server_genre_preferences", {}).items()
        }

        logger.info("Loaded persisted watch stats")
    except Exception as e:
        logger.error(f"Failed to load stats: {e}")

def track_watch_time(user_id: int, media_title: str, duration: float, genres: List[str] = None):
    """Track user watch time and preferences"""
    try:
        # Initialize user analytics if not exists
        if user_id not in state.user_watch_time:
            state.user_watch_time[user_id] = 0.0
        if user_id not in state.user_genre_preferences:
            state.user_genre_preferences[user_id] = {}
        if user_id not in state.user_media_history:
            state.user_media_history[user_id] = []
        
        # Add watch time
        state.user_watch_time[user_id] += duration
        
        # Track genre preferences
        if genres:
            for genre in genres:
                if genre not in state.user_genre_preferences[user_id]:
                    state.user_genre_preferences[user_id][genre] = 0
                state.user_genre_preferences[user_id][genre] += 1
        
        # Add to media history
        state.user_media_history[user_id].append({
            "media": media_title,
            "duration": duration,
            "timestamp": datetime.now()
        })
        
        # Keep only last 100 media items per user
        if len(state.user_media_history[user_id]) > 100:
            state.user_media_history[user_id] = state.user_media_history[user_id][-100:]
        
        # Update daily stats
        today = datetime.now().strftime('%Y-%m-%d')
        if today not in state.daily_stats:
            state.daily_stats[today] = {"total_watch_time": 0.0, "unique_users": set()}
        
        state.daily_stats[today]["total_watch_time"] += duration
        state.daily_stats[today]["unique_users"].add(user_id)
        
    except Exception as e:
        logger.error(f"Error tracking watch time: {e}")

def get_user_analytics(user_id: int) -> Dict:
    """Get comprehensive analytics for a user with proper watch time calculation"""
    try:
        # Initialize with default values
        analytics = {
            "total_watch_time": 0.0,
            "total_actions": state.user_actions.get(user_id, {}).get("total_actions", 0),
            "favorite_genres": [],
            "recent_media": [],
            "watch_time_formatted": "0h 0m",
            "top_genre": "",
            "media_count": 0,
            "streaming_sessions": 0,
            "total_stream_watch_time": 0.0,
            "is_currently_watching": user_id in state.current_viewers
        }
        
        # Get total watch time
        total_seconds = state.user_watch_time.get(user_id, 0.0)
        analytics["total_watch_time"] = total_seconds
        
        # Format watch time properly
        if total_seconds > 0:
            hours = int(total_seconds // 3600)
            minutes = int((total_seconds % 3600) // 60)
            seconds = int(total_seconds % 60)
            analytics["watch_time_formatted"] = f"{hours}h {minutes}m {seconds}s"
        else:
            analytics["watch_time_formatted"] = "0h 0m 0s"
        
        # Get favorite genres
        if user_id in state.user_genre_preferences:
            genres = state.user_genre_preferences[user_id]
            sorted_genres = sorted(genres.items(), key=lambda x: x[1], reverse=True)
            analytics["favorite_genres"] = [genre for genre, count in sorted_genres[:5]]
            if sorted_genres:
                analytics["top_genre"] = sorted_genres[0][0]
        
        # Get recent media with proper duration formatting
        if user_id in state.user_media_history and state.user_media_history[user_id]:
            recent_media = state.user_media_history[user_id][-10:]  # Last 10 items
            analytics["recent_media"] = [
                {
                    "title": item["media"],
                    "duration": seconds_to_time(item["duration"]),  # Format individual session duration
                    "timestamp": item["timestamp"].strftime("%Y-%m-%d %H:%M"),
                    "raw_duration": item["duration"]  # Keep raw for debugging
                }
                for item in recent_media
            ]
            analytics["media_count"] = len(state.user_media_history[user_id])
        
        # Calculate streaming statistics
        if user_id in state.user_media_history:
            stream_sessions = [item for item in state.user_media_history[user_id] if item.get("type") == "stream_viewing"]
            analytics["streaming_sessions"] = len(stream_sessions)
            analytics["total_stream_watch_time"] = sum(item["duration"] for item in stream_sessions)
        
        # Debug logging
        logger.info(f"📊 Analytics for user {user_id}: {total_seconds:.1f}s total, {analytics['media_count']} media items")
        
        return analytics
        
    except Exception as e:
        logger.error(f"❌ Error getting user analytics: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return {
            "total_watch_time": 0.0,
            "total_actions": 0,
            "favorite_genres": [],
            "recent_media": [],
            "watch_time_formatted": "0h 0m 0s",
            "top_genre": "",
            "media_count": 0,
            "streaming_sessions": 0,
            "total_stream_watch_time": 0.0,
            "is_currently_watching": False
        }

def get_server_analytics() -> Dict:
    """Get server-wide analytics"""
    try:
        total_users = len(state.user_actions)
        total_watch_time = sum(state.user_watch_time.values())
        total_actions = sum(user_data.get("total_actions", 0) for user_data in state.user_actions.values())
        
        # Get most active users
        most_active = sorted(
            state.user_actions.items(),
            key=lambda x: x[1].get("total_actions", 0),
            reverse=True
        )[:5]
        
        # Get genre popularity
        all_genres = {}
        for user_genres in state.user_genre_preferences.values():
            for genre, count in user_genres.items():
                all_genres[genre] = all_genres.get(genre, 0) + count
        
        popular_genres = sorted(all_genres.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Get daily stats
        today = datetime.now().strftime('%Y-%m-%d')
        today_stats = state.daily_stats.get(today, {"total_watch_time": 0.0, "unique_users": set()})
        
        return {
            "total_users": total_users,
            "total_watch_time": total_watch_time,
            "total_watch_time_formatted": seconds_to_time(total_watch_time),
            "total_actions": total_actions,
            "most_active_users": [
                {"username": user_data["username"], "actions": user_data["total_actions"]}
                for user_id, user_data in most_active
            ],
            "popular_genres": [{"genre": genre, "count": count} for genre, count in popular_genres],
            "today_watch_time": today_stats["total_watch_time"],
            "today_unique_users": len(today_stats["unique_users"])
        }
        
    except Exception as e:
        logger.error(f"Error getting server analytics: {e}")
        return {}

def generate_recommendations(user_id: int, current_media: str = None) -> List[Dict]:
    """Generate media recommendations for a user based on their preferences"""
    try:
        # Get user preferences
        user_genres = state.user_genre_preferences.get(user_id, {})
        user_media = state.user_media_history.get(user_id, [])
        
        # Check if user is currently watching a stream
        is_currently_watching = user_id in state.current_viewers
        current_stream_media = state.streaming_media if is_currently_watching else None
        
        if not user_genres and not user_media and not is_currently_watching:
            return []
        
        recommendations = []
        
        # Add streaming-based recommendations if user is currently watching
        if is_currently_watching and current_stream_media:
            # Get recommendations based on what's currently being streamed
            stream_recommendations = get_stream_based_recommendations(current_stream_media)
            recommendations.extend(stream_recommendations)
        
        # Get popular genres from user's history
        top_genres = sorted(user_genres.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # Generate recommendations based on genres
        for genre, count in top_genres:
            # This is a simplified recommendation system
            # In a real implementation, you'd query a movie database
            genre_recommendations = get_genre_recommendations(genre)
            recommendations.extend(genre_recommendations)
        
        # Remove duplicates and already watched media
        watched_titles = {item["media"].lower() for item in user_media}
        unique_recommendations = []
        seen_titles = set()
        
        for rec in recommendations:
            title_lower = rec["title"].lower()
            if title_lower not in watched_titles and title_lower not in seen_titles:
                unique_recommendations.append(rec)
                seen_titles.add(title_lower)
        
        # Limit to 10 recommendations
        return unique_recommendations[:10]
        
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        return []

def get_genre_recommendations(genre: str) -> List[Dict]:
    """Get sample recommendations for a genre (placeholder implementation)"""
    # This is a placeholder - in a real implementation, you'd query a movie database
    genre_samples = {
        "Action": [
            {"title": "The Dark Knight", "year": "2008", "rating": "9.0/10", "reason": "Classic action film"},
            {"title": "Mad Max: Fury Road", "year": "2015", "rating": "8.1/10", "reason": "High-octane action"},
            {"title": "John Wick", "year": "2014", "rating": "7.4/10", "reason": "Intense action sequences"}
        ],
        "Comedy": [
            {"title": "The Grand Budapest Hotel", "year": "2014", "rating": "8.1/10", "reason": "Witty comedy"},
            {"title": "Superbad", "year": "2007", "rating": "7.6/10", "reason": "Classic teen comedy"},
            {"title": "Deadpool", "year": "2016", "rating": "8.0/10", "reason": "Action-comedy blend"}
        ],
        "Drama": [
            {"title": "The Shawshank Redemption", "year": "1994", "rating": "9.3/10", "reason": "Powerful drama"},
            {"title": "Forrest Gump", "year": "1994", "rating": "8.8/10", "reason": "Heartwarming story"},
            {"title": "The Godfather", "year": "1972", "rating": "9.2/10", "reason": "Epic crime drama"}
        ],
        "Sci-Fi": [
            {"title": "Blade Runner 2049", "year": "2017", "rating": "8.0/10", "reason": "Visually stunning sci-fi"},
            {"title": "Interstellar", "year": "2014", "rating": "8.6/10", "reason": "Mind-bending sci-fi"},
            {"title": "The Matrix", "year": "1999", "rating": "8.7/10", "reason": "Revolutionary sci-fi"}
        ],
        "Horror": [
            {"title": "Hereditary", "year": "2018", "rating": "7.3/10", "reason": "Psychological horror"},
            {"title": "Get Out", "year": "2017", "rating": "7.7/10", "reason": "Social horror thriller"},
            {"title": "The Conjuring", "year": "2013", "rating": "7.5/10", "reason": "Supernatural horror"}
        ]
    }
    
    return genre_samples.get(genre, [])

def get_stream_based_recommendations(current_media: str) -> List[Dict]:
    """Get recommendations based on currently streaming media"""
    try:
        # This is a simplified implementation
        # In a real system, you'd analyze the current media and find similar content
        
        # Extract potential genre/keywords from media title
        media_lower = current_media.lower()
        
        # Simple keyword-based recommendations
        if any(keyword in media_lower for keyword in ['action', 'fight', 'battle', 'war']):
            return [
                {"title": "Mad Max: Fury Road", "year": "2015", "rating": "8.1/10", "reason": "Similar high-octane action"},
                {"title": "John Wick", "year": "2014", "rating": "7.4/10", "reason": "Intense action sequences"},
                {"title": "The Raid", "year": "2011", "rating": "7.6/10", "reason": "Martial arts action"}
            ]
        elif any(keyword in media_lower for keyword in ['comedy', 'funny', 'laugh']):
            return [
                {"title": "The Grand Budapest Hotel", "year": "2014", "rating": "8.1/10", "reason": "Witty comedy with style"},
                {"title": "Deadpool", "year": "2016", "rating": "8.0/10", "reason": "Meta comedy superhero"},
                {"title": "The Nice Guys", "year": "2016", "rating": "7.4/10", "reason": "Buddy comedy mystery"}
            ]
        elif any(keyword in media_lower for keyword in ['horror', 'scary', 'fright']):
            return [
                {"title": "Hereditary", "year": "2018", "rating": "7.3/10", "reason": "Psychological horror"},
                {"title": "The Babadook", "year": "2014", "rating": "6.8/10", "reason": "Atmospheric horror"},
                {"title": "Get Out", "year": "2017", "rating": "7.7/10", "reason": "Social horror thriller"}
            ]
        elif any(keyword in media_lower for keyword in ['drama', 'emotional', 'serious']):
            return [
                {"title": "Moonlight", "year": "2016", "rating": "7.4/10", "reason": "Powerful character drama"},
                {"title": "Manchester by the Sea", "year": "2016", "rating": "7.8/10", "reason": "Emotional family drama"},
                {"title": "The Father", "year": "2020", "rating": "8.2/10", "reason": "Intimate family drama"}
            ]
        else:
            # General recommendations based on popular streaming content
            return [
                {"title": "Stranger Things", "year": "2016", "rating": "8.7/10", "reason": "Popular streaming series"},
                {"title": "The Queen's Gambit", "year": "2020", "rating": "8.5/10", "reason": "Critically acclaimed miniseries"},
                {"title": "Squid Game", "year": "2021", "rating": "8.1/10", "reason": "Global streaming phenomenon"}
            ]
            
    except Exception as e:
        logger.error(f"Error getting stream-based recommendations: {e}")
        return []

def get_playlist_recommendations(current_playlist: List[Dict]) -> List[Dict]:
    """Get recommendations based on current playlist"""
    try:
        if not current_playlist:
            return []
        
        # Analyze current playlist genres (simplified)
        # In a real implementation, you'd analyze the actual media files
        recommendations = []
        
        # Get some general recommendations
        general_recs = [
            {"title": "Inception", "year": "2010", "rating": "8.8/10", "reason": "Mind-bending thriller"},
            {"title": "Pulp Fiction", "year": "1994", "rating": "8.9/10", "reason": "Quentin Tarantino classic"},
            {"title": "The Lord of the Rings", "year": "2001", "rating": "8.8/10", "reason": "Epic fantasy adventure"}
        ]
        
        return general_recs[:5]
        
    except Exception as e:
        logger.error(f"Error getting playlist recommendations: {e}")
        return []

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

    # FOR SCRAPING (gate by title change and cache):
    scraped_info = {}
    if Config.ENABLE_MEDIA_INFO_SCRAPING and media_info['title'] and media_info['title'] != "Unknown":
        title_query = media_info['title']
        cached = media_scraper.cache.get(title_query.lower()) if hasattr(media_scraper, 'cache') else None
        should_scrape = (state.last_scraped_query != title_query) and not (cached and cached.get('title'))
        if should_scrape:
            logger.info(f"🎬 Attempting to scrape info for: {title_query}")
            scraped_info = await media_scraper.search_media_info(title_query)
            state.last_scraped_query = title_query
            media_info['scraped_info'] = scraped_info
            if scraped_info:
                logger.info(f"✅ Scraped info: {scraped_info.get('title', 'Unknown')}")
            else:
                logger.debug("No scraped info found (suppressing warning for repeated attempts)")
        else:
            scraped_info = cached or {}
            if scraped_info:
                media_info['scraped_info'] = scraped_info

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
    footer_text = f"Use the buttons below to control playback • Updates every {Config.UPDATE_INTERVAL}s"

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
        footer_text = f"Last action: {action_type} by {last_action_by} • Updates every {Config.UPDATE_INTERVAL}s"

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
    """Enhanced control view with cooldowns, role restrictions, and mobile optimization"""
    
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
    @discord.ui.button(
        label="⏮️", 
        style=discord.ButtonStyle.secondary, 
        custom_id="previous_track", 
        row=0
    )
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

    @discord.ui.button(
        label="⏪ -10s", 
        style=discord.ButtonStyle.secondary, 
        custom_id="seek_back", 
        row=0
    )
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

    @discord.ui.button(
        label="⏸️", 
        style=discord.ButtonStyle.danger, 
        custom_id="pause_btn", 
        row=0
    )
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

    @discord.ui.button(
        label="▶️", 
        style=discord.ButtonStyle.success, 
        custom_id="play_btn", 
        row=0
    )
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

    @discord.ui.button(
        label="+10s ⏩", 
        style=discord.ButtonStyle.secondary, 
        custom_id="seek_forward", 
        row=0
    )
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
        # Streaming status
        if Config.ENABLE_STREAM_DETECTION and state.current_streamer:
            streamer = bot.get_user(state.current_streamer)
            streamer_name = streamer.display_name if streamer else f"User {state.current_streamer}"
            viewer_count = len(state.current_viewers)
            stream_duration = ""
            if state.stream_start_time:
                duration = datetime.now() - state.stream_start_time
                hours, remainder = divmod(int(duration.total_seconds()), 3600)
                minutes, seconds = divmod(remainder, 60)
                stream_duration = f" ({hours:02d}:{minutes:02d}:{seconds:02d})"
            
            embed.add_field(
                name="🎥 Streaming Status",
                value=f"**Streamer:** {streamer_name}\n**Viewers:** {viewer_count}\n**Media:** {state.streaming_media or 'Unknown'}{stream_duration}",
                inline=False
            )
        elif Config.ENABLE_STREAM_DETECTION:
            embed.add_field(
                name="🎥 Streaming Status",
                value="No active stream",
                inline=False
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

async def apply_smart_controls(status_data: Dict) -> Dict:
    """Apply smart controls to VLC playback"""
    if not Config.ENABLE_SMART_CONTROLS or not status_data:
        return status_data
    
    try:
        current_volume = status_data.get('volume', 0)
        position = status_data.get('position', 0)
        length = status_data.get('length', 0)
        
        # Volume normalization
        if Config.VOLUME_NORMALIZATION and current_volume > 0:
            await normalize_volume(current_volume)
        
        # Auto-skip intros
        if Config.AUTO_SKIP_INTROS and position < Config.INTRO_SKIP_DURATION:
            media_info = get_media_info(status_data)
            filename = media_info.get('filename', '')
            
            if filename in state.intro_skip_times:
                skip_times = state.intro_skip_times[filename]
                for start_time, end_time in skip_times:
                    current_seconds = position * length
                    if start_time <= current_seconds <= end_time:
                        await vlc.seek_relative(int(end_time - current_seconds))
                        logger.info(f"🎬 Auto-skipped intro for {filename}")
                        break
        
        # Smart pause detection (if volume is too low or no activity)
        if Config.SMART_PAUSE_DETECTION:
            await detect_smart_pause(status_data)
        
        return status_data
        
    except Exception as e:
        logger.error(f"Smart controls error: {e}")
        return status_data

async def normalize_volume(current_volume: int):
    """Normalize volume based on history"""
    try:
        # Add current volume to history
        state.volume_history.append(current_volume)
        
        # Keep only last 10 volume readings
        if len(state.volume_history) > 10:
            state.volume_history = state.volume_history[-10:]
        
        # Calculate average volume
        avg_volume = sum(state.volume_history) / len(state.volume_history)
        
        # If volume is significantly different from average, adjust
        volume_diff = abs(current_volume - avg_volume)
        if volume_diff > 20:  # More than 20% difference
            target_volume = int(avg_volume)
            await vlc.set_volume(target_volume)
            logger.info(f"🔊 Volume normalized: {current_volume}% → {target_volume}%")
            
    except Exception as e:
        logger.error(f"Volume normalization error: {e}")

async def detect_smart_pause(status_data: Dict):
    """Detect if smart pause should be applied"""
    try:
        # This is a placeholder for smart pause detection
        # Could implement based on user activity, voice channel status, etc.
        pass
    except Exception as e:
        logger.error(f"Smart pause detection error: {e}")

async def check_voice_channel_sync():
    """Check voice channel and sync playback accordingly"""
    if not Config.ENABLE_VOICE_SYNC or not Config.VOICE_CHANNEL_ID:
        return
    
    try:
        voice_channel = bot.get_channel(Config.VOICE_CHANNEL_ID)
        if not voice_channel:
            return
        
        # Get current voice channel members
        current_members = set(member.id for member in voice_channel.members if not member.bot)
        
        # Check if voice channel became empty
        if Config.AUTO_PAUSE_EMPTY_VOICE and len(current_members) == 0:
            status_data = await vlc.get_status()
            if status_data and status_data.get('state') == 'playing':
                await vlc.pause()
                logger.info("🔇 Auto-paused: Voice channel is empty")
                return
        
        # Check if members left (for potential auto-pause)
        if state.voice_channel_members and current_members:
            left_members = state.voice_channel_members - current_members
            if left_members:
                logger.info(f"👥 Members left voice channel: {len(left_members)}")
        
        # Update voice channel members
        state.voice_channel_members = current_members
        state.last_voice_check = datetime.now()
        
    except Exception as e:
        logger.error(f"Voice channel sync error: {e}")

async def detect_voice_streaming_enhanced(member=None, before=None, after=None):
    """Enhanced streaming detection with proper user name tracking"""
    if not Config.ENABLE_STREAM_DETECTION:
        return
    
    try:
        logger.debug("📊 Running streaming detection...")
        # If specific voice channel is configured, use it
        if Config.VOICE_CHANNEL_ID:
            voice_channel = bot.get_channel(Config.VOICE_CHANNEL_ID)
            if not voice_channel:
                return
            channels_to_check = [voice_channel]
        else:
            # Check all voice channels in all guilds
            channels_to_check = []
            for guild in bot.guilds:
                for channel in guild.voice_channels:
                    if channel.members:
                        channels_to_check.append(channel)
        
        active_stream_found = False
        
        for voice_channel in channels_to_check:
            # Get current voice channel members (excluding bots)
            current_members = set(member.id for member in voice_channel.members if not member.bot)
            
            # Store display names for all members
            for member in voice_channel.members:
                if not member.bot:
                    state.user_display_names[member.id] = member.display_name
            
            # Check for active screen sharing
            active_streamers = []
            for member in voice_channel.members:
                if not member.bot and member.voice:
                    is_streaming = (
                        member.voice.self_stream or
                        member.voice.self_video or
                        getattr(member.voice, 'self_video', False)
                    )
                    
                    if is_streaming:
                        active_streamers.append((member.id, voice_channel.id))
                        logger.info(f"🎥 Detected streaming: {member.display_name}")
            
            # Handle streaming state changes
            if active_streamers:
                active_stream_found = True
                primary_streamer, channel_id = active_streamers[0]
                
                if state.current_streamer != primary_streamer:
                    # New streamer
                    state.current_streamer = primary_streamer
                    state.stream_start_time = datetime.now()
                    state.current_viewers = current_members.copy()

                    # Get streamer info with proper name
                    streamer_member = voice_channel.guild.get_member(primary_streamer)
                    if streamer_member:
                        streamer_name = streamer_member.display_name
                        state.user_display_names[primary_streamer] = streamer_name
                    else:
                        streamer_name = state.user_display_names.get(primary_streamer, f"User {primary_streamer}")
                    
                    state.streaming_media = f"{streamer_name}'s Stream"
                    
                    logger.info(f"🎥 Streaming started by {streamer_name} with {len(current_members)} viewers")
                    logger.info(f"📊 Initialized {len(state.viewer_sessions)} viewer sessions")
                    
                    # Initialize viewer sessions with proper names
                    for viewer_id in state.current_viewers:
                        if viewer_id not in state.viewer_sessions:
                            viewer_member = voice_channel.guild.get_member(viewer_id)
                            viewer_name = viewer_member.display_name if viewer_member else state.user_display_names.get(viewer_id, f"User {viewer_id}")
                            state.user_display_names[viewer_id] = viewer_name
                            
                            state.viewer_sessions[viewer_id] = {
                                "start_time": datetime.now(),
                                "media": state.streaming_media,
                                "duration": 0.0,
                                "channel_id": channel_id,
                                "guild_id": voice_channel.guild.id,
                                "last_tracked_time": datetime.now()
                            }
                            logger.info(f"👀 Started tracking viewer: {viewer_name} (ID: {viewer_id})")
                            logger.info(f"📊 Created viewer session for {viewer_name}: {state.viewer_sessions[viewer_id]}")
                
                else:
                    # Same streamer, update viewers
                    new_viewers = current_members - state.current_viewers
                    left_viewers = state.current_viewers - current_members
                    
                    # Add new viewers
                    for viewer_id in new_viewers:
                        if viewer_id not in state.viewer_sessions:
                            viewer_member = voice_channel.guild.get_member(viewer_id)
                            viewer_name = viewer_member.display_name if viewer_member else state.user_display_names.get(viewer_id, f"User {viewer_id}")
                            state.user_display_names[viewer_id] = viewer_name
                            
                            state.viewer_sessions[viewer_id] = {
                                "start_time": datetime.now(),
                                "media": state.streaming_media,
                                "duration": 0.0,
                                "channel_id": channel_id,
                                "guild_id": voice_channel.guild.id,
                                "last_tracked_time": datetime.now()
                            }
                            logger.info(f"👀 New viewer joined: {viewer_name} (ID: {viewer_id})")
                            logger.info(f"📊 Created viewer session for {viewer_name}: {state.viewer_sessions[viewer_id]}")
                    
                    # Remove viewers who left and track their watch time
                    for viewer_id in left_viewers:
                        if viewer_id in state.viewer_sessions:
                            session = state.viewer_sessions[viewer_id]
                            watch_duration = (datetime.now() - session["start_time"]).total_seconds()
                            
                            # Track watch time with proper user info
                            viewer_name = state.user_display_names.get(viewer_id, f"User {viewer_id}")
                            track_viewer_watch_time(viewer_id, session["media"], watch_duration)
                            
                            logger.info(f"👋 Viewer left: {viewer_name} (watched for {watch_duration:.1f}s)")
                            del state.viewer_sessions[viewer_id]
                    
                    # Update current viewers
                    state.current_viewers = current_members.copy()
                    logger.info(f"📊 Updated viewers: {len(state.current_viewers)} current viewers")
        
        # End session if no streams found
        if not active_stream_found and state.current_streamer:
            logger.info("🎥 Streaming ended")
            end_streaming_session()
        
        state.last_stream_check = datetime.now()
        
    except Exception as e:
        logger.error(f"Enhanced stream detection error: {e}")

def track_viewer_watch_time(user_id: int, media_title: str, duration: float):
    """Track watch time for a viewer with proper accumulation"""
    try:
        logger.debug(f"📊 Tracking watch time for user {user_id}: {duration:.1f}s for '{media_title}'")
        
        # Initialize user analytics if not exists
        if user_id not in state.user_watch_time:
            state.user_watch_time[user_id] = 0.0
            logger.info(f"📊 Initialized watch time for user {user_id}")
        
        if user_id not in state.user_genre_preferences:
            state.user_genre_preferences[user_id] = {}
        
        if user_id not in state.user_media_history:
            state.user_media_history[user_id] = []
        
        # Add watch time (ensure it's a positive number)
        if duration > 0:
            # Update total watch time
            old_total = state.user_watch_time[user_id]
            state.user_watch_time[user_id] += duration
            new_total = state.user_watch_time[user_id]
            
            logger.debug(f"📊 Watch time updated: {old_total:.1f}s -> {new_total:.1f}s (+{duration:.1f}s) for user {user_id}")
            
            # Add to media history with actual duration
            state.user_media_history[user_id].append({
                "media": media_title,
                "duration": duration,  # This should be the actual duration watched
                "timestamp": datetime.now(),
                "type": "stream_viewing"
            })

            # Update server-level stats if we can infer guild
            try:
                # Find viewer's current session for guild info
                session = state.viewer_sessions.get(user_id)
                guild_id = session.get("guild_id") if session else None
                if guild_id:
                    # Total per server
                    state.server_watch_time[guild_id] = state.server_watch_time.get(guild_id, 0.0) + duration
                    # Per-user per server
                    if guild_id not in state.server_user_watch_time:
                        state.server_user_watch_time[guild_id] = {}
                    state.server_user_watch_time[guild_id][user_id] = state.server_user_watch_time[guild_id].get(user_id, 0.0) + duration
                    # Server media history
                    if guild_id not in state.server_media_history:
                        state.server_media_history[guild_id] = []
                    state.server_media_history[guild_id].append({
                        "media": media_title,
                        "duration": duration,
                        "user_id": user_id,
                        "timestamp": datetime.now()
                    })
                    # Keep server media history manageable
                    if len(state.server_media_history[guild_id]) > 500:
                        state.server_media_history[guild_id] = state.server_media_history[guild_id][-500:]
            except Exception as se:
                logger.debug(f"Server stats update skipped: {se}")
            
            # Keep only last 100 entries
            if len(state.user_media_history[user_id]) > 100:
                state.user_media_history[user_id] = state.user_media_history[user_id][-100:]
            
            # Update daily stats
            today = datetime.now().strftime('%Y-%m-%d')
            if today not in state.daily_stats:
                state.daily_stats[today] = {"total_watch_time": 0.0, "unique_users": set()}
            
            state.daily_stats[today]["total_watch_time"] += duration
            state.daily_stats[today]["unique_users"].add(user_id)
            
            user_name = state.user_display_names.get(user_id, f"User {user_id}")
            logger.debug(f"📊 Successfully tracked {duration:.1f}s for {user_name}. Total: {new_total:.1f}s")
        else:
            logger.warning(f"📊 Skipped zero/negative duration: {duration}s for user {user_id}")
        
    except Exception as e:
        logger.error(f"❌ Error tracking viewer watch time: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")

def track_active_viewers_watch_time():
    """Periodically track watch time for currently active viewers"""
    try:
        state.periodic_tracking_runs += 1
        
        if not state.current_streamer or not state.viewer_sessions:
            logger.debug("📊 No active streamer or viewer sessions to track")
            return
        
        current_time = datetime.now()
        total_tracked = 0
        tracked_viewers = 0
        
        logger.debug(f"📊 Run #{state.periodic_tracking_runs}: Checking {len(state.viewer_sessions)} active viewer sessions")
        
        for viewer_id, session in state.viewer_sessions.items():
            if session["start_time"]:
                # Calculate time since last update
                time_since_start = (current_time - session["start_time"]).total_seconds()
                
                # Only track if we have a meaningful duration (at least 5 seconds)
                if time_since_start >= 5:
                    # Calculate incremental watch time since last tracking
                    last_tracked = session.get("last_tracked_time", session["start_time"])
                    incremental_duration = (current_time - last_tracked).total_seconds()
                    
                    if incremental_duration > 0:
                        # Track the incremental watch time
                        track_viewer_watch_time(viewer_id, session["media"], incremental_duration)
                        
                        # Update session tracking
                        session["last_tracked_time"] = current_time
                        session["duration"] += incremental_duration
                        total_tracked += incremental_duration
                        tracked_viewers += 1
                        state.total_watch_time_tracked += incremental_duration
                        
                        logger.debug(f"📊 Tracked {incremental_duration:.1f}s for viewer {viewer_id} (total: {session['duration']:.1f}s)")
                else:
                    logger.debug(f"📊 Skipping viewer {viewer_id} - not enough time elapsed ({time_since_start:.1f}s < 5s)")
            else:
                logger.warning(f"📊 Viewer {viewer_id} has no start_time in session")
        
        if total_tracked > 0:
            logger.info(f"📊 Run #{state.periodic_tracking_runs}: Tracked {total_tracked:.1f}s total watch time for {tracked_viewers}/{len(state.viewer_sessions)} active viewers")
        else:
            logger.debug(f"📊 Run #{state.periodic_tracking_runs}: No watch time to track for {len(state.viewer_sessions)} active viewers")
            
    except Exception as e:
        logger.error(f"❌ Error tracking active viewers watch time: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")

def end_streaming_session():
    """End the current streaming session and track final watch times"""
    try:
        if not state.current_streamer:
            logger.info("📊 No current streamer to end session")
            return
        
        current_time = datetime.now()
        total_watch_time = 0
        viewer_count = 0
        
        # Track final watch times for all current viewers
        for viewer_id, session in list(state.viewer_sessions.items()):
            if session["start_time"]:
                watch_duration = (current_time - session["start_time"]).total_seconds()
                if watch_duration > 0:
                    logger.info(f"📊 Ending session for viewer {viewer_id}: {watch_duration:.1f}s")
                    track_viewer_watch_time(viewer_id, session["media"], watch_duration)
                    total_watch_time += watch_duration
                    viewer_count += 1
                else:
                    logger.warning(f"📊 Zero duration for viewer {viewer_id}")
            else:
                logger.warning(f"📊 No start time for viewer {viewer_id}")
        
        # Record streaming session in history
        if state.stream_start_time:
            session_duration = (current_time - state.stream_start_time).total_seconds()
            
            # Convert viewer IDs to names for history
            viewer_names = []
            for viewer_id in state.current_viewers:
                viewer_name = state.user_display_names.get(viewer_id, f"User {viewer_id}")
                viewer_names.append(viewer_name)
            
            streamer_name = state.user_display_names.get(state.current_streamer, f"User {state.current_streamer}")
            
            state.stream_history.append({
                "streamer": state.current_streamer,
                "streamer_name": streamer_name,
                "media": state.streaming_media,
                "start_time": state.stream_start_time,
                "end_time": current_time,
                "duration": session_duration,
                "total_watch_time": total_watch_time,
                "viewers": list(state.current_viewers),
                "viewer_names": viewer_names,
                "viewer_count": len(state.current_viewers)
            })
            
            # Keep only last 50 streaming sessions
            if len(state.stream_history) > 50:
                state.stream_history = state.stream_history[-50:]
            
            logger.info(f"📊 Session ended: {streamer_name} streamed for {session_duration:.1f}s, {viewer_count} viewers, total watch time: {total_watch_time:.1f}s")
        else:
            logger.warning("📊 No stream start time recorded")
        
        # Clear current streaming data
        state.current_streamer = None
        state.current_viewers.clear()
        state.stream_start_time = None
        state.streaming_media = None
        state.viewer_sessions.clear()
        
        logger.info("📊 Streaming session cleared")
        
    except Exception as e:
        logger.error(f"❌ Error ending streaming session: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")

@bot.event
async def on_voice_state_update(member, before, after):
    """Handle voice channel state changes with better streaming detection"""
    if not Config.ENABLE_VOICE_SYNC or not Config.VOICE_CHANNEL_ID:
        return
    
    target_channel_id = Config.VOICE_CHANNEL_ID
    
    try:
        # Check if the update is relevant to our target channel
        relevant_update = False
        
        # Member left target channel
        if before.channel and before.channel.id == target_channel_id:
            relevant_update = True
            logger.info(f"👋 {member.display_name} left voice channel")
        
        # Member joined target channel
        if after.channel and after.channel.id == target_channel_id:
            relevant_update = True
            logger.info(f"👋 {member.display_name} joined voice channel")
        
        # Member switched between channels (including to/from target)
        if (before.channel and after.channel and 
            (before.channel.id == target_channel_id or after.channel.id == target_channel_id)):
            relevant_update = True
        
        if not relevant_update:
            return
        
        # Update voice sync
        await check_voice_channel_sync()
        
        # Check for streaming changes with improved detection
        if Config.ENABLE_STREAM_DETECTION:
            await detect_voice_streaming_enhanced(member, before, after)
            
    except Exception as e:
        logger.error(f"Voice state update error: {e}")

@bot.event
async def on_ready():

    global _bot_ready_once

    logger.info(f'{bot.user} has connected to Discord!')

    logger.info(f'Bot is ready to control VLC at {Config.VLC_HOST}:{Config.VLC_PORT}')

    # Validate configuration

    if not Config.DISCORD_BOT_TOKEN:

        logger.error("DISCORD_BOT_TOKEN not found in .env file!")

        return

    if not Config.STATUS_CHANNEL_ID:

        logger.warning("STATUS_CHANNEL_ID not set - persistent embed will not work")

    if _bot_ready_once:
        # on_ready fires again after a reconnect - the one-time startup
        # work below (task loops, command sync) must not run twice.
        logger.info("Reconnected to Discord - skipping one-time startup steps")
        return

    _bot_ready_once = True

    # Add persistent view

    bot.add_view(VLCControlView())

    # Test VLC connection

    status = await vlc.get_status()

    if status:

        logger.info("✓ VLC connection successful")

    else:

        logger.warning("✗ VLC connection failed - check configuration")

    # Load persisted stats before starting loops
    try:
        load_stats()
    except Exception as e:
        logger.error(f"Failed to load stats on startup: {e}")

    # Start status update loop

    if Config.STATUS_CHANNEL_ID and not update_status_embed.is_running():

        update_status_embed.start()

    # Start voice sync task
    if Config.ENABLE_VOICE_SYNC and not voice_sync_task.is_running():
        voice_sync_task.start()
        logger.info("🔊 Voice channel sync enabled")

    # Start streaming detection task
    if Config.ENABLE_STREAM_DETECTION and not stream_detection_task.is_running():
        stream_detection_task.start()
        logger.info("🎥 Voice channel streaming detection enabled")
        logger.info(f"📊 Watch time tracking interval: {Config.STREAM_DETECTION_INTERVAL} seconds")

    # Start autosave loop
    try:
        if not autosave_stats_task.is_running():
            autosave_stats_task.change_interval(seconds=Config.STATS_SAVE_INTERVAL)
            autosave_stats_task.start()
            logger.info(f"💾 Autosave enabled every {Config.STATS_SAVE_INTERVAL}s → {Config.STATS_SAVE_PATH}")
    except Exception as e:
        logger.error(f"Failed to start autosave task: {e}")

    # Debug: List all registered commands
    commands = bot.tree.get_commands()
    logger.info(f"Found {len(commands)} commands before sync:")
    for cmd in commands:
        logger.info(f"  - {cmd.name}: {cmd.description}")

    # Sync slash commands
    try:
        if Config.ALLOWED_GUILD_ID:
            guild = discord.Object(id=Config.ALLOWED_GUILD_ID)
            synced = await bot.tree.sync(guild=guild)
            logger.info(f"Synced {len(synced)} command(s) to guild {Config.ALLOWED_GUILD_ID}")
            logger.info(f"Synced commands: {[cmd.name for cmd in synced]}")
        else:
            synced = await bot.tree.sync()
            logger.info(f"Synced {len(synced)} global command(s)")
            logger.info(f"Synced commands: {[cmd.name for cmd in synced]}")
    except Exception as e:
        logger.error(f"Failed to sync commands: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")

@bot.tree.command(name="sync_commands", description="Manually sync slash commands")
async def sync_commands(interaction: discord.Interaction):
    """Manually sync slash commands"""
    if not is_admin(interaction.user):
        await interaction.response.send_message("❌ Only admins can sync commands.", ephemeral=True)
        return

    try:
        if Config.ALLOWED_GUILD_ID:
            guild = discord.Object(id=Config.ALLOWED_GUILD_ID)
            synced = await bot.tree.sync(guild=guild)
            await interaction.response.send_message(f"✅ Synced {len(synced)} command(s) to guild.", ephemeral=True)
        else:
            synced = await bot.tree.sync()
            await interaction.response.send_message(f"✅ Synced {len(synced)} global command(s).", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ Failed to sync commands: {e}", ephemeral=True)

@tasks.loop(seconds=Config.VOICE_SYNC_CHECK_INTERVAL)
async def voice_sync_task():
    """Periodically check voice channel sync"""
    if Config.ENABLE_VOICE_SYNC:
        await check_voice_channel_sync()

@tasks.loop(seconds=Config.STREAM_DETECTION_INTERVAL)
async def stream_detection_task():
    """Periodically detect voice channel streaming and track viewers"""
    if Config.ENABLE_STREAM_DETECTION:
        await detect_voice_streaming_enhanced()
        # Track watch time for active viewers
        if state.current_streamer and state.viewer_sessions:
            logger.debug(f"📊 Running periodic watch time tracking for {len(state.viewer_sessions)} viewers")
        track_active_viewers_watch_time()

@tasks.loop(seconds=60)
async def autosave_stats_task():
    try:
        save_stats()
    except Exception as e:
        logger.error(f"Autosave error: {e}")

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
        
        # Apply smart controls
        if status_data:
            status_data = await apply_smart_controls(status_data)

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

# Test command to verify registration
@bot.tree.command(name="test", description="Test command to verify slash commands are working")
async def test_command(interaction: discord.Interaction):
    """Simple test command"""
    await interaction.response.send_message("✅ Slash commands are working!", ephemeral=True)

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

# (Removed duplicate simple recommend command; using advanced recommend below)
# (Removed duplicate /mystats and /serverstats - see /my_stats and /server_stats below)


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

@bot.tree.command(name="add_to_playlist", description="Add media to playlist")
async def add_to_playlist(interaction: discord.Interaction, media_path: str):
    """Add media file to VLC playlist"""
    if not is_admin(interaction.user):
        await interaction.response.send_message("❌ Only admins can add items to playlist.", ephemeral=True)
        return
    
    try:
        # VLC doesn't have a direct API to add items, but we can provide instructions
        embed = discord.Embed(
            title="📝 Add to Playlist",
            description=f"To add `{media_path}` to the playlist:\n\n1. Open VLC Media Player\n2. Go to **Media** → **Open File**\n3. Navigate to: `{media_path}`\n4. Click **Add** (not Play)\n\nOr drag and drop the file into VLC's playlist area.",
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )
        
        embed.add_field(
            name="💡 Pro Tip",
            value="You can also drag multiple files at once to add them all to the playlist!",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        log_user_action(interaction.user.id, interaction.user.display_name, f"add_to_playlist: {media_path}")
        
    except Exception as e:
        logger.error(f"Error in add_to_playlist command: {e}")
        await interaction.response.send_message("❌ Failed to process playlist addition.", ephemeral=True)

@bot.tree.command(name="clear_playlist", description="Clear the entire playlist")
async def clear_playlist(interaction: discord.Interaction):
    """Clear VLC playlist"""
    if not is_admin(interaction.user):
        await interaction.response.send_message("❌ Only admins can clear the playlist.", ephemeral=True)
        return
    
    try:
        # VLC doesn't have a direct clear API, but we can provide instructions
        embed = discord.Embed(
            title="🗑️ Clear Playlist",
            description="To clear the VLC playlist:\n\n1. Open VLC Media Player\n2. Go to **Playlist** panel (View → Playlist)\n3. Right-click in the playlist area\n4. Select **Clear** or **Remove All**\n\nOr use **Ctrl+L** to toggle the playlist panel.",
            color=discord.Color.orange(),
            timestamp=datetime.now()
        )
        
        embed.add_field(
            name="⚠️ Warning",
            value="This will remove ALL items from the playlist!",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        log_user_action(interaction.user.id, interaction.user.display_name, "clear_playlist")
        
    except Exception as e:
        logger.error(f"Error in clear_playlist command: {e}")
        await interaction.response.send_message("❌ Failed to process playlist clear.", ephemeral=True)

@bot.tree.command(name="shuffle_playlist", description="Shuffle the current playlist")
async def shuffle_playlist(interaction: discord.Interaction):
    """Shuffle VLC playlist"""
    if not is_admin(interaction.user):
        await interaction.response.send_message("❌ Only admins can shuffle the playlist.", ephemeral=True)
        return
    
    try:
        # VLC doesn't have a direct shuffle API, but we can provide instructions
        embed = discord.Embed(
            title="🔀 Shuffle Playlist",
            description="To shuffle the VLC playlist:\n\n1. Open VLC Media Player\n2. Go to **Playlist** panel (View → Playlist)\n3. Right-click in the playlist area\n4. Select **Shuffle**\n\nOr use **Ctrl+H** to toggle shuffle mode.",
            color=discord.Color.purple(),
            timestamp=datetime.now()
        )
        
        embed.add_field(
            name="🎲 Shuffle Mode",
            value="You can also enable **Random** mode in VLC's Playback menu for continuous shuffling!",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        log_user_action(interaction.user.id, interaction.user.display_name, "shuffle_playlist")
        
    except Exception as e:
        logger.error(f"Error in shuffle_playlist command: {e}")
        await interaction.response.send_message("❌ Failed to process playlist shuffle.", ephemeral=True)

@bot.tree.command(name="playlist_export", description="Export current playlist to text file")
async def playlist_export(interaction: discord.Interaction):
    """Export playlist information"""
    try:
        playlist_info = await get_playlist_info()
        
        if not playlist_info:
            await interaction.response.send_message("📭 Playlist is empty - nothing to export.", ephemeral=True)
            return
        
        # Create playlist text
        playlist_text = f"VLC Playlist Export - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        playlist_text += "=" * 50 + "\n\n"
        
        for i, item in enumerate(playlist_info, 1):
            name = item.get('name', 'Unknown')
            duration = item.get('duration', 0)
            duration_str = seconds_to_time(duration) if duration > 0 else "Unknown"
            current = " (Now Playing)" if item.get('current') else ""
            
            playlist_text += f"{i:2d}. {name}{current}\n"
            playlist_text += f"    Duration: {duration_str}\n"
            playlist_text += f"    URI: {item.get('uri', 'N/A')}\n\n"
        
        # Create file
        filename = f"playlist_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        # Send as file
        file_obj = discord.File(
            io.StringIO(playlist_text),
            filename=filename
        )
        
        embed = discord.Embed(
            title="📤 Playlist Exported",
            description=f"Exported {len(playlist_info)} items to `{filename}`",
            color=discord.Color.green(),
            timestamp=datetime.now()
        )
        
        await interaction.response.send_message(embed=embed, file=file_obj, ephemeral=True)
        log_user_action(interaction.user.id, interaction.user.display_name, "playlist_export")
        
    except Exception as e:
        logger.error(f"Error in playlist_export command: {e}")
        await interaction.response.send_message("❌ Failed to export playlist.", ephemeral=True)

@bot.tree.command(name="volume", description="Set VLC volume")
async def volume_command(interaction: discord.Interaction, volume: int):
    """Set VLC volume (0-100)"""
    if not is_admin(interaction.user):
        await interaction.response.send_message("❌ Only admins can control volume.", ephemeral=True)
        return
    
    if not 0 <= volume <= 100:
        await interaction.response.send_message("❌ Volume must be between 0 and 100.", ephemeral=True)
        return
    
    try:
        result = await vlc.set_volume(volume)
        if result is not None:
            embed = discord.Embed(
                title="🔊 Volume Set",
                description=f"Volume set to **{volume}%**",
                color=discord.Color.green(),
                timestamp=datetime.now()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            log_user_action(interaction.user.id, interaction.user.display_name, f"set_volume: {volume}%")
        else:
            await interaction.response.send_message("❌ Failed to set volume. VLC might be disconnected.", ephemeral=True)
    except Exception as e:
        logger.error(f"Error in volume command: {e}")
        await interaction.response.send_message("❌ Failed to set volume.", ephemeral=True)

@bot.tree.command(name="rate", description="Set playback rate")
async def rate_command(interaction: discord.Interaction, rate: float):
    """Set VLC playback rate (0.25-4.0)"""
    if not is_admin(interaction.user):
        await interaction.response.send_message("❌ Only admins can control playback rate.", ephemeral=True)
        return
    
    if not 0.25 <= rate <= 4.0:
        await interaction.response.send_message("❌ Playback rate must be between 0.25 and 4.0.", ephemeral=True)
        return
    
    try:
        result = await vlc.set_playback_rate(rate)
        if result is not None:
            embed = discord.Embed(
                title="⚡ Playback Rate Set",
                description=f"Playback rate set to **{rate}x**",
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            log_user_action(interaction.user.id, interaction.user.display_name, f"set_rate: {rate}x")
        else:
            await interaction.response.send_message("❌ Failed to set playback rate. VLC might be disconnected.", ephemeral=True)
    except Exception as e:
        logger.error(f"Error in rate command: {e}")
        await interaction.response.send_message("❌ Failed to set playback rate.", ephemeral=True)

@bot.tree.command(name="subtitles", description="Toggle subtitles on/off")
async def subtitles_command(interaction: discord.Interaction):
    """Toggle VLC subtitles"""
    if not is_admin(interaction.user):
        await interaction.response.send_message("❌ Only admins can control subtitles.", ephemeral=True)
        return
    
    try:
        result = await vlc.toggle_subtitles()
        if result is not None:
            embed = discord.Embed(
                title="📝 Subtitles Toggled",
                description="Subtitles have been toggled",
                color=discord.Color.orange(),
                timestamp=datetime.now()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            log_user_action(interaction.user.id, interaction.user.display_name, "toggle_subtitles")
        else:
            await interaction.response.send_message("❌ Failed to toggle subtitles. VLC might be disconnected.", ephemeral=True)
    except Exception as e:
        logger.error(f"Error in subtitles command: {e}")
        await interaction.response.send_message("❌ Failed to toggle subtitles.", ephemeral=True)

@bot.tree.command(name="smart_controls", description="Configure smart controls")
async def smart_controls_command(interaction: discord.Interaction):
    """Show smart controls configuration"""
    if not is_admin(interaction.user):
        await interaction.response.send_message("❌ Only admins can view smart controls.", ephemeral=True)
        return
    
    try:
        embed = discord.Embed(
            title="🧠 Smart Controls Configuration",
            description="Current smart controls settings:",
            color=discord.Color.purple(),
            timestamp=datetime.now()
        )
        
        embed.add_field(
            name="🔊 Volume Normalization",
            value="✅ Enabled" if Config.VOLUME_NORMALIZATION else "❌ Disabled",
            inline=True
        )
        
        embed.add_field(
            name="🎬 Auto-Skip Intros",
            value="✅ Enabled" if Config.AUTO_SKIP_INTROS else "❌ Disabled",
            inline=True
        )
        
        embed.add_field(
            name="⏱️ Intro Skip Duration",
            value=f"{Config.INTRO_SKIP_DURATION} seconds",
            inline=True
        )
        
        embed.add_field(
            name="🎯 Auto Quality Adjustment",
            value="✅ Enabled" if Config.AUTO_QUALITY_ADJUSTMENT else "❌ Disabled",
            inline=True
        )
        
        embed.add_field(
            name="⏸️ Smart Pause Detection",
            value="✅ Enabled" if Config.SMART_PAUSE_DETECTION else "❌ Disabled",
            inline=True
        )
        
        embed.add_field(
            name="🔧 Smart Controls",
            value="✅ Enabled" if Config.ENABLE_SMART_CONTROLS else "❌ Disabled",
            inline=True
        )
        
        embed.add_field(
            name="📊 Volume History",
            value=f"{len(state.volume_history)} recent readings",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        log_user_action(interaction.user.id, interaction.user.display_name, "view_smart_controls")
        
    except Exception as e:
        logger.error(f"Error in smart_controls command: {e}")
        await interaction.response.send_message("❌ Failed to get smart controls info.", ephemeral=True)

@bot.tree.command(name="react", description="React to current media")
async def react_command(interaction: discord.Interaction, emoji: str):
    """React to current media with an emoji"""
    if not Config.ENABLE_SOCIAL_FEATURES or not Config.ENABLE_REACTIONS:
        await interaction.response.send_message("❌ Social features are disabled.", ephemeral=True)
        return
    
    try:
        # Get current media info
        status_data = await vlc.get_status()
        if not status_data:
            await interaction.response.send_message("❌ No media currently playing.", ephemeral=True)
            return
        
        media_info = get_media_info(status_data)
        filename = media_info.get('filename', 'unknown')
        
        # Initialize reactions for this media if not exists
        if filename not in state.media_reactions:
            state.media_reactions[filename] = {}
        
        if emoji not in state.media_reactions[filename]:
            state.media_reactions[filename][emoji] = []
        
        # Add or remove user reaction
        user_id = interaction.user.id
        if user_id in state.media_reactions[filename][emoji]:
            state.media_reactions[filename][emoji].remove(user_id)
            action = "removed"
        else:
            state.media_reactions[filename][emoji].append(user_id)
            action = "added"
        
        # Count total reactions for this emoji
        reaction_count = len(state.media_reactions[filename][emoji])
        
        embed = discord.Embed(
            title="😊 Reaction Updated",
            description=f"{action.capitalize()} {emoji} reaction to **{filename}**",
            color=discord.Color.green() if action == "added" else discord.Color.orange(),
            timestamp=datetime.now()
        )
        
        embed.add_field(
            name="Reaction Count",
            value=f"{emoji} {reaction_count}",
            inline=True
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        log_user_action(interaction.user.id, interaction.user.display_name, f"react: {emoji}")
        
    except Exception as e:
        logger.error(f"Error in react command: {e}")
        await interaction.response.send_message("❌ Failed to add reaction.", ephemeral=True)

@bot.tree.command(name="comment", description="Add a comment to current media")
async def comment_command(interaction: discord.Interaction, comment: str):
    """Add a comment to current media"""
    if not Config.ENABLE_SOCIAL_FEATURES or not Config.ENABLE_COMMENTS:
        await interaction.response.send_message("❌ Social features are disabled.", ephemeral=True)
        return
    
    if len(comment) > Config.MAX_COMMENT_LENGTH:
        await interaction.response.send_message(f"❌ Comment too long. Maximum {Config.MAX_COMMENT_LENGTH} characters.", ephemeral=True)
        return
    
    try:
        # Get current media info
        status_data = await vlc.get_status()
        if not status_data:
            await interaction.response.send_message("❌ No media currently playing.", ephemeral=True)
            return
        
        media_info = get_media_info(status_data)
        filename = media_info.get('filename', 'unknown')
        
        # Initialize comments for this media if not exists
        if filename not in state.media_comments:
            state.media_comments[filename] = []
        
        # Add comment
        comment_data = {
            "user": interaction.user.display_name,
            "user_id": interaction.user.id,
            "comment": comment,
            "timestamp": datetime.now()
        }
        state.media_comments[filename].append(comment_data)
        
        # Keep only last 20 comments per media
        if len(state.media_comments[filename]) > 20:
            state.media_comments[filename] = state.media_comments[filename][-20:]
        
        embed = discord.Embed(
            title="💬 Comment Added",
            description=f"Added comment to **{filename}**",
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )
        
        embed.add_field(
            name="Your Comment",
            value=comment,
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        log_user_action(interaction.user.id, interaction.user.display_name, f"comment: {comment[:50]}...")
        
    except Exception as e:
        logger.error(f"Error in comment command: {e}")
        await interaction.response.send_message("❌ Failed to add comment.", ephemeral=True)

@bot.tree.command(name="comments", description="View comments for current media")
async def comments_command(interaction: discord.Interaction):
    """View comments for current media"""
    if not Config.ENABLE_SOCIAL_FEATURES or not Config.ENABLE_COMMENTS:
        await interaction.response.send_message("❌ Social features are disabled.", ephemeral=True)
        return
    
    try:
        # Get current media info
        status_data = await vlc.get_status()
        if not status_data:
            await interaction.response.send_message("❌ No media currently playing.", ephemeral=True)
            return
        
        media_info = get_media_info(status_data)
        filename = media_info.get('filename', 'unknown')
        
        if filename not in state.media_comments or not state.media_comments[filename]:
            await interaction.response.send_message("📭 No comments for this media yet.", ephemeral=True)
            return
        
        # Show last 10 comments
        recent_comments = state.media_comments[filename][-10:]
        
        embed = discord.Embed(
            title=f"💬 Comments for {filename}",
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )
        
        comments_text = ""
        for i, comment in enumerate(reversed(recent_comments), 1):
            timestamp_str = comment['timestamp'].strftime('%H:%M')
            comments_text += f"**{i}.** {comment['user']} ({timestamp_str})\n"
            comments_text += f"   {comment['comment']}\n\n"
        
        if len(comments_text) > 2000:
            comments_text = comments_text[:1997] + "..."
        
        embed.description = comments_text
        embed.set_footer(text=f"Showing last {len(recent_comments)} comments")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        log_user_action(interaction.user.id, interaction.user.display_name, "view_comments")
        
    except Exception as e:
        logger.error(f"Error in comments command: {e}")
        await interaction.response.send_message("❌ Failed to get comments.", ephemeral=True)

@bot.tree.command(name="watch_party", description="Join or leave watch party")
async def watch_party_command(interaction: discord.Interaction):
    """Join or leave the current watch party"""
    if not Config.ENABLE_SOCIAL_FEATURES or not Config.ENABLE_WATCH_PARTY:
        await interaction.response.send_message("❌ Social features are disabled.", ephemeral=True)
        return
    
    try:
        user_id = interaction.user.id
        
        if user_id in state.watch_party_members:
            state.watch_party_members.remove(user_id)
            action = "left"
        else:
            state.watch_party_members.add(user_id)
            action = "joined"
        
        member_count = len(state.watch_party_members)
        
        embed = discord.Embed(
            title="🎉 Watch Party",
            description=f"You {action} the watch party!",
            color=discord.Color.green() if action == "joined" else discord.Color.orange(),
            timestamp=datetime.now()
        )
        
        embed.add_field(
            name="Party Members",
            value=f"{member_count} member{'s' if member_count != 1 else ''}",
            inline=True
        )
        
        if member_count > 0:
            member_names = []
            for member_id in list(state.watch_party_members)[:5]:  # Show first 5
                member = interaction.guild.get_member(member_id)
                if member:
                    member_names.append(member.display_name)
            
            if member_names:
                embed.add_field(
                    name="Current Members",
                    value=", ".join(member_names) + ("..." if member_count > 5 else ""),
                    inline=False
                )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        log_user_action(interaction.user.id, interaction.user.display_name, f"watch_party_{action}")
        
    except Exception as e:
        logger.error(f"Error in watch_party command: {e}")
        await interaction.response.send_message("❌ Failed to update watch party.", ephemeral=True)

@bot.tree.command(name="my_stats", description="View your personal viewing statistics")
async def my_stats_command(interaction: discord.Interaction):
    """Show personal analytics for the user"""
    try:
        user_id = interaction.user.id
        analytics = get_user_analytics(user_id)
        
        embed = discord.Embed(
            title=f"📊 {interaction.user.display_name}'s Statistics",
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )
        
        # Basic stats
        embed.add_field(
            name="⏱️ Total Watch Time",
            value=analytics["watch_time_formatted"],
            inline=True
        )
        
        embed.add_field(
            name="🎮 Total Actions",
            value=str(analytics["total_actions"]),
            inline=True
        )
        
        embed.add_field(
            name="🎬 Media Watched",
            value=str(analytics["media_count"]),
            inline=True
        )
        
        # Favorite genres
        if analytics["favorite_genres"]:
            genres_text = ", ".join(analytics["favorite_genres"][:3])
            embed.add_field(
                name="🎭 Favorite Genres",
                value=genres_text,
                inline=False
            )
        
        # Recent media
        if analytics["recent_media"]:
            recent_text = "\n".join([
                f"• {item['title']} ({item['duration']})"
                for item in analytics["recent_media"][:5]
            ])
            embed.add_field(
                name="📺 Recent Media",
                value=recent_text,
                inline=False
            )
        
        # Current streaming status
        if Config.ENABLE_STREAM_DETECTION:
            if user_id in state.current_viewers:
                streamer = bot.get_user(state.current_streamer) if state.current_streamer else None
                streamer_name = streamer.display_name if streamer else f"User {state.current_streamer}"
                embed.add_field(
                    name="🎥 Currently Watching",
                    value=f"**Streamer:** {streamer_name}\n**Media:** {state.streaming_media or 'Unknown'}\n**Status:** 👀 Active Viewer",
                    inline=False
                )
            elif state.current_streamer:
                embed.add_field(
                    name="🎥 Streaming Status",
                    value="Not currently watching any stream",
                    inline=False
                )
            else:
                embed.add_field(
                    name="🎥 Streaming Status",
                    value="No active stream",
                    inline=False
                )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        log_user_action(user_id, interaction.user.display_name, "view_my_stats")
        
    except Exception as e:
        logger.error(f"Error in my_stats command: {e}")
        await interaction.response.send_message("❌ Failed to get your statistics.", ephemeral=True)

@bot.tree.command(name="server_stats", description="View server-wide viewing statistics")
async def server_stats_command(interaction: discord.Interaction):
    """Show server-wide analytics"""
    if not is_admin(interaction.user):
        await interaction.response.send_message("❌ Only admins can view server statistics.", ephemeral=True)
        return
    
    try:
        analytics = get_server_analytics()
        
        embed = discord.Embed(
            title="📊 Server Statistics",
            color=discord.Color.gold(),
            timestamp=datetime.now()
        )
        
        # Basic stats
        embed.add_field(
            name="👥 Total Users",
            value=str(analytics["total_users"]),
            inline=True
        )
        
        embed.add_field(
            name="⏱️ Total Watch Time",
            value=analytics["total_watch_time_formatted"],
            inline=True
        )
        
        embed.add_field(
            name="🎮 Total Actions",
            value=str(analytics["total_actions"]),
            inline=True
        )
        
        # Today's stats
        embed.add_field(
            name="📅 Today's Watch Time",
            value=seconds_to_time(analytics["today_watch_time"]),
            inline=True
        )
        
        embed.add_field(
            name="👤 Today's Active Users",
            value=str(analytics["today_unique_users"]),
            inline=True
        )
        
        # Most active users
        if analytics["most_active_users"]:
            active_text = "\n".join([
                f"{i+1}. **{user['username']}**: {user['actions']} actions"
                for i, user in enumerate(analytics["most_active_users"])
            ])
            embed.add_field(
                name="🏆 Most Active Users",
                value=active_text,
                inline=False
            )
        
        # Popular genres
        if analytics["popular_genres"]:
            genres_text = "\n".join([
                f"• **{genre['genre']}**: {genre['count']} views"
                for genre in analytics["popular_genres"]
            ])
            embed.add_field(
                name="🎭 Popular Genres",
                value=genres_text,
                inline=False
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        log_user_action(interaction.user.id, interaction.user.display_name, "view_server_stats")
        
    except Exception as e:
        logger.error(f"Error in server_stats command: {e}")
        await interaction.response.send_message("❌ Failed to get server statistics.", ephemeral=True)

@bot.tree.command(name="leaderboard", description="View user leaderboard")
async def leaderboard_command(interaction: discord.Interaction):
    """Show user leaderboard"""
    try:
        # Get top users by watch time
        top_watch_time = sorted(
            [(user_id, watch_time) for user_id, watch_time in state.user_watch_time.items()],
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        # Get top users by actions
        top_actions = sorted(
            [(user_id, user_data["total_actions"]) for user_id, user_data in state.user_actions.items()],
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        embed = discord.Embed(
            title="🏆 Leaderboard",
            color=discord.Color.gold(),
            timestamp=datetime.now()
        )
        
        # Watch time leaderboard
        if top_watch_time:
            watch_text = ""
            for i, (user_id, watch_time) in enumerate(top_watch_time, 1):
                user = interaction.guild.get_member(user_id)
                username = user.display_name if user else f"User {user_id}"
                watch_formatted = seconds_to_time(watch_time)
                watch_text += f"{i}. **{username}**: {watch_formatted}\n"
            
            embed.add_field(
                name="⏱️ Most Watch Time",
                value=watch_text,
                inline=True
            )
        
        # Actions leaderboard
        if top_actions:
            actions_text = ""
            for i, (user_id, actions) in enumerate(top_actions, 1):
                user = interaction.guild.get_member(user_id)
                username = user.display_name if user else f"User {user_id}"
                actions_text += f"{i}. **{username}**: {actions} actions\n"
            
            embed.add_field(
                name="🎮 Most Actions",
                value=actions_text,
                inline=True
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        log_user_action(interaction.user.id, interaction.user.display_name, "view_leaderboard")
        
    except Exception as e:
        logger.error(f"Error in leaderboard command: {e}")
        await interaction.response.send_message("❌ Failed to get leaderboard.", ephemeral=True)

@bot.tree.command(name="recommend", description="Get personalized media recommendations")
async def recommend_command(interaction: discord.Interaction):
    """Get personalized recommendations based on viewing history"""
    try:
        user_id = interaction.user.id
        
        # Check if we have recent recommendations
        cache_key = str(user_id)
        now = datetime.now()
        
        if (cache_key in state.recommendation_cache and 
            cache_key in state.last_recommendation_update and
            (now - state.last_recommendation_update[cache_key]).total_seconds() < 3600):  # 1 hour cache
            recommendations = state.recommendation_cache[cache_key]
        else:
            # Generate new recommendations
            recommendations = generate_recommendations(user_id)
            state.recommendation_cache[cache_key] = recommendations
            state.last_recommendation_update[cache_key] = now
        
        if not recommendations:
            embed = discord.Embed(
                title="🎬 Recommendations",
                description="I need more data about your viewing habits to provide recommendations.\n\nWatch some media and try again!",
                color=discord.Color.orange(),
                timestamp=datetime.now()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        embed = discord.Embed(
            title=f"🎬 Recommendations for {interaction.user.display_name}",
            description="Based on your viewing history and preferences:",
            color=discord.Color.purple(),
            timestamp=datetime.now()
        )
        
        # Add recommendations
        for i, rec in enumerate(recommendations[:5], 1):
            embed.add_field(
                name=f"{i}. {rec['title']} ({rec['year']})",
                value=f"⭐ {rec['rating']} • {rec['reason']}",
                inline=False
            )
        
        embed.set_footer(text="Recommendations are updated every hour")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        log_user_action(user_id, interaction.user.display_name, "get_recommendations")
        
    except Exception as e:
        logger.error(f"Error in recommend command: {e}")
        await interaction.response.send_message("❌ Failed to get recommendations.", ephemeral=True)

@bot.tree.command(name="playlist_recommend", description="Get recommendations based on current playlist")
async def playlist_recommend_command(interaction: discord.Interaction):
    """Get recommendations based on current playlist"""
    try:
        playlist_info = await get_playlist_info()
        recommendations = get_playlist_recommendations(playlist_info)
        
        if not recommendations:
            await interaction.response.send_message("📭 No playlist available for recommendations.", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="🎵 Playlist-Based Recommendations",
            description="Based on your current playlist:",
            color=discord.Color.green(),
            timestamp=datetime.now()
        )
        
        # Add recommendations
        for i, rec in enumerate(recommendations, 1):
            embed.add_field(
                name=f"{i}. {rec['title']} ({rec['year']})",
                value=f"⭐ {rec['rating']} • {rec['reason']}",
                inline=False
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        log_user_action(interaction.user.id, interaction.user.display_name, "get_playlist_recommendations")
        
    except Exception as e:
        logger.error(f"Error in playlist_recommend command: {e}")
        await interaction.response.send_message("❌ Failed to get playlist recommendations.", ephemeral=True)

@bot.tree.command(name="trending", description="View trending media recommendations")
async def trending_command(interaction: discord.Interaction):
    """Show trending media recommendations"""
    try:
        # Get trending recommendations based on server activity
        analytics = get_server_analytics()
        popular_genres = analytics.get("popular_genres", [])
        
        if not popular_genres:
            await interaction.response.send_message("📊 Not enough data for trending recommendations yet.", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="🔥 Trending Recommendations",
            description="Based on server-wide viewing activity:",
            color=discord.Color.red(),
            timestamp=datetime.now()
        )
        
        # Get recommendations for popular genres
        trending_recs = []
        for genre_data in popular_genres[:3]:  # Top 3 genres
            genre = genre_data["genre"]
            recs = get_genre_recommendations(genre)
            trending_recs.extend(recs[:2])  # 2 per genre
        
        # Remove duplicates
        seen_titles = set()
        unique_recs = []
        for rec in trending_recs:
            if rec["title"] not in seen_titles:
                unique_recs.append(rec)
                seen_titles.add(rec["title"])
        
        # Add recommendations
        for i, rec in enumerate(unique_recs[:6], 1):
            embed.add_field(
                name=f"{i}. {rec['title']} ({rec['year']})",
                value=f"⭐ {rec['rating']} • {rec['reason']}",
                inline=False
            )
        
        embed.set_footer(text="Based on server viewing patterns")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        log_user_action(interaction.user.id, interaction.user.display_name, "view_trending")
        
    except Exception as e:
        logger.error(f"Error in trending command: {e}")
        await interaction.response.send_message("❌ Failed to get trending recommendations.", ephemeral=True)

@bot.tree.command(name="viewers", description="Show current stream viewers")
async def viewers_command(interaction: discord.Interaction):
    """Show who is currently watching the stream"""
    try:
        if not Config.ENABLE_STREAM_DETECTION:
            await interaction.response.send_message("❌ Stream detection is not enabled.", ephemeral=True)
            return
        
        if not state.current_streamer:
            embed = discord.Embed(
                title="🎥 No Active Stream",
                description="No one is currently streaming in any voice channel.",
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed)
            return
        
        # Get streamer info with proper name
        streamer_name = state.user_display_names.get(state.current_streamer, f"User {state.current_streamer}")
        
        # Get viewer info with proper names
        viewer_details = []
        for viewer_id in state.current_viewers:
            viewer_name = state.user_display_names.get(viewer_id, f"User {viewer_id}")
            viewer_details.append(viewer_name)
        
        # Calculate stream duration
        stream_duration = ""
        total_seconds = 0
        if state.stream_start_time:
            total_seconds = (datetime.now() - state.stream_start_time).total_seconds()
            hours, remainder = divmod(int(total_seconds), 3600)
            minutes, seconds = divmod(remainder, 60)
            stream_duration = f" ({hours:02d}:{minutes:02d}:{seconds:02d})"
        
        embed = discord.Embed(
            title="🎥 Current Stream Viewers",
            color=discord.Color.green(),
            timestamp=datetime.now()
        )
        
        # Stream info
        embed.add_field(
            name="📺 Stream Info",
            value=f"**Streamer:** {streamer_name}\n**Media:** {state.streaming_media or 'Screen Share'}{stream_duration}",
            inline=False
        )
        
        # Viewers list - FIXED: Now properly displays viewers
        if viewer_details:
            viewers_text = "\n".join([f"👀 {viewer}" for viewer in viewer_details])
            embed.add_field(
                name=f"👥 Viewers ({len(viewer_details)})",
                value=viewers_text,
                inline=False
            )
            
            # Add watch time info for current session
            current_watch_times = []
            for viewer_id in state.current_viewers:
                if viewer_id in state.viewer_sessions:
                    session = state.viewer_sessions[viewer_id]
                    session_duration = (datetime.now() - session["start_time"]).total_seconds()
                    viewer_name = state.user_display_names.get(viewer_id, f"User {viewer_id}")
                    current_watch_times.append(f"• {viewer_name}: {seconds_to_time(session_duration)}")
            
            if current_watch_times:
                embed.add_field(
                    name="⏱️ Current Session Watch Time",
                    value="\n".join(current_watch_times[:5]),  # Show first 5
                    inline=False
                )
        else:
            embed.add_field(
                name="👥 Viewers",
                value="No viewers currently",
                inline=False
            )
        
        # Session statistics
        embed.add_field(
            name="📊 Session Stats",
            value=f"**Duration:** {seconds_to_time(total_seconds)}\n**Total Viewers:** {len(state.current_viewers)}",
            inline=True
        )
        
        await interaction.response.send_message(embed=embed)
        logger.info(f"👥 Viewers command: {len(viewer_details)} viewers displayed")
        
    except Exception as e:
        logger.error(f"Error in viewers command: {e}")
        await interaction.response.send_message("❌ Failed to get viewer information.")

@bot.tree.command(name="mobile_mode", description="Toggle mobile-optimized display")
async def mobile_mode_command(interaction: discord.Interaction):
    """Toggle mobile-optimized display mode"""
    try:
        # This is a simplified implementation - in practice, you'd store user preferences
        embed = discord.Embed(
            title="📱 Mobile Mode",
            description="Mobile optimization settings:",
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )
        
        embed.add_field(
            name="Current Settings",
            value=f"• Mobile Optimization: {'✅ Enabled' if Config.ENABLE_MOBILE_OPTIMIZATION else '❌ Disabled'}\n"
                  f"• Mobile-Friendly Embeds: {'✅ Enabled' if Config.MOBILE_FRIENDLY_EMBEDS else '❌ Disabled'}\n"
                  f"• Compact Display: {'✅ Enabled' if Config.COMPACT_DISPLAY else '❌ Disabled'}\n"
                  f"• Touch-Friendly Buttons: {'✅ Enabled' if Config.TOUCH_FRIENDLY_BUTTONS else '❌ Disabled'}",
            inline=False
        )
        
        embed.add_field(
            name="Mobile Features",
            value="• Larger, touch-friendly buttons\n• Compact embed layout\n• Optimized text length\n• Better mobile formatting",
            inline=False
        )
        
        embed.add_field(
            name="Note",
            value="Mobile optimization is automatically applied when enabled in configuration.",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        log_user_action(interaction.user.id, interaction.user.display_name, "view_mobile_mode")
        
    except Exception as e:
        logger.error(f"Error in mobile_mode command: {e}")
        await interaction.response.send_message("❌ Failed to get mobile mode info.", ephemeral=True)
        
@bot.tree.command(name="stream_debug", description="Debug streaming detection")
async def stream_debug_command(interaction: discord.Interaction):
    """Debug command to check streaming detection status"""
    try:
        if not Config.ENABLE_STREAM_DETECTION:
            await interaction.response.send_message("❌ Stream detection is disabled.", ephemeral=True)
            return
        
        if not Config.VOICE_CHANNEL_ID:
            await interaction.response.send_message("❌ Voice channel not configured.", ephemeral=True)
            return
        
        voice_channel = bot.get_channel(Config.VOICE_CHANNEL_ID)
        if not voice_channel:
            await interaction.response.send_message("❌ Voice channel not found.", ephemeral=True)
            return
        
        # Get detailed voice channel info
        embed = discord.Embed(
            title="🔍 Streaming Debug Info",
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )
        
        # Voice channel info
        embed.add_field(
            name="🎧 Voice Channel",
            value=f"**Name:** {voice_channel.name}\n**ID:** {voice_channel.id}\n**Members:** {len(voice_channel.members)}",
            inline=False
        )
        
        # Member details
        member_details = []
        for i, member in enumerate(voice_channel.members[:10]):  # Show first 10 members
            status = "Bot" if member.bot else "User"
            streaming = "🎥 Streaming" if (member.voice and (member.voice.self_stream or member.voice.self_video)) else "📱 Listening"
            member_details.append(f"{i+1}. {member.display_name} ({status}) - {streaming}")
        
        if member_details:
            embed.add_field(
                name="👥 Channel Members",
                value="\n".join(member_details),
                inline=False
            )
        
        # Streaming state
        if state.current_streamer:
            streamer = bot.get_user(state.current_streamer)
            streamer_name = streamer.display_name if streamer else f"User {state.current_streamer}"
            duration = ""
            if state.stream_start_time:
                total_seconds = (datetime.now() - state.stream_start_time).total_seconds()
                duration = f" for {seconds_to_time(total_seconds)}"
            
            embed.add_field(
                name="🎥 Current Stream",
                value=f"**Streamer:** {streamer_name}\n**Media:** {state.streaming_media}\n**Viewers:** {len(state.current_viewers)}{duration}",
                inline=False
            )
        else:
            embed.add_field(
                name="🎥 Current Stream",
                value="No active stream detected",
                inline=False
            )
        
        # Voice state details for non-bot members
        voice_states = []
        for member in voice_channel.members:
            if not member.bot and member.voice:
                voice_states.append(
                    f"**{member.display_name}:** "
                    f"stream={member.voice.self_stream}, "
                    f"video={member.voice.self_video}, "
                    f"deaf={member.voice.self_deaf}, "
                    f"mute={member.voice.self_mute}"
                )
        
        if voice_states:
            embed.add_field(
                name="🎤 Voice States",
                value="\n".join(voice_states)[:1024],  # Discord field limit
                inline=False
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
    except Exception as e:
        logger.error(f"Stream debug error: {e}")
        await interaction.response.send_message(f"❌ Debug error: {e}", ephemeral=True)
        
@bot.tree.command(name="refresh_stream", description="Manually refresh streaming detection")
async def refresh_stream_command(interaction: discord.Interaction):
    """Manually refresh streaming detection"""
    try:
        await detect_voice_streaming_enhanced()
        
        if state.current_streamer:
            streamer = bot.get_user(state.current_streamer)
            streamer_name = streamer.display_name if streamer else f"User {state.current_streamer}"
            await interaction.response.send_message(
                f"✅ Stream detection refreshed. Current streamer: **{streamer_name}** with **{len(state.current_viewers)}** viewers.",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "✅ Stream detection refreshed. No active stream detected.",
                ephemeral=True
            )
            
    except Exception as e:
        logger.error(f"Refresh stream error: {e}")
        await interaction.response.send_message(f"❌ Refresh failed: {e}", ephemeral=True)

@bot.tree.command(name="track_watch_time", description="Manually trigger watch time tracking (admin only)")
async def track_watch_time_command(interaction: discord.Interaction):
    """Manually trigger watch time tracking for active viewers"""
    if not is_admin(interaction.user):
        await interaction.response.send_message("❌ Only admins can trigger watch time tracking.", ephemeral=True)
        return
    
    try:
        # Track watch time for active viewers
        track_active_viewers_watch_time()
        
        # Get current stats
        total_viewers = len(state.viewer_sessions)
        total_watch_time = sum(state.user_watch_time.values())
        
        await interaction.response.send_message(
            f"✅ Watch time tracking triggered. Active viewers: **{total_viewers}**, Total watch time: **{total_watch_time:.1f}s**",
            ephemeral=True
        )
        
    except Exception as e:
        logger.error(f"Track watch time error: {e}")
        await interaction.response.send_message(f"❌ Failed to track watch time: {e}", ephemeral=True)

@bot.tree.command(name="viewer_sessions", description="Show current viewer sessions (admin only)")
async def viewer_sessions_command(interaction: discord.Interaction):
    """Show current viewer sessions for debugging"""
    if not is_admin(interaction.user):
        await interaction.response.send_message("❌ Only admins can view viewer sessions.", ephemeral=True)
        return
    
    try:
        if not state.viewer_sessions:
            await interaction.response.send_message("📭 No active viewer sessions.", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="👀 Current Viewer Sessions",
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )
        
        current_time = datetime.now()
        for viewer_id, session in state.viewer_sessions.items():
            viewer_name = state.user_display_names.get(viewer_id, f"User {viewer_id}")
            duration = (current_time - session["start_time"]).total_seconds()
            last_tracked = session.get("last_tracked_time", session["start_time"])
            time_since_tracked = (current_time - last_tracked).total_seconds()
            
            embed.add_field(
                name=f"👤 {viewer_name}",
                value=f"**Duration:** {duration:.1f}s\n**Last Tracked:** {time_since_tracked:.1f}s ago\n**Media:** {session['media']}",
                inline=True
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
    except Exception as e:
        logger.error(f"Viewer sessions error: {e}")
        await interaction.response.send_message(f"❌ Failed to get viewer sessions: {e}", ephemeral=True)
        
@bot.tree.command(name="watch_debug", description="Debug watch time tracking (admin only)")
async def watch_debug_command(interaction: discord.Interaction):
    """Debug command to show watch time tracking status"""
    if not is_admin(interaction.user):
        await interaction.response.send_message("❌ Only admins can use debug commands.", ephemeral=True)
        return
    
    try:
        user_id = interaction.user.id
        
        # Create debug message
        debug_lines = [
            "🐛 Watch Time Debug - Detailed",
            "🔍 State Variables",
            f"user_watch_time dict: {len(state.user_watch_time)} users",
            f"Your watch time: {'NOT FOUND' if user_id not in state.user_watch_time else f'{state.user_watch_time[user_id]:.1f}s'}",
            f"user_media_history: {len(state.user_media_history.get(user_id, []))} items",
            f"viewer_sessions: {len(state.viewer_sessions)} sessions",
            f"In viewer_sessions: {user_id in state.viewer_sessions}",
            "",
            "🎥 Current Stream",
            f"Streamer: {state.current_streamer or 'None'}",
            f"Viewers: {len(state.current_viewers)}",
            f"You are viewer: {user_id in state.current_viewers}",
        ]
        
        # Add viewer session info if user is in it
        if user_id in state.viewer_sessions:
            session = state.viewer_sessions[user_id]
            current_duration = (datetime.now() - session["start_time"]).total_seconds()
            debug_lines.extend([
                "",
                "👀 Your Viewer Session",
                f"Start time: {session['start_time']}",
                f"Current duration: {current_duration:.1f}s",
                f"Media: {session['media']}",
            ])
        
        # Add user actions info
        user_actions = state.user_actions.get(user_id, {}).get("actions", [])
        debug_lines.extend([
            "",
            "📝 User Actions",
            f"{'❌ No user actions found' if not user_actions else f'✅ {len(user_actions)} actions found'}",
            "",
            "🔧 Debug Info",
            f"Periodic tracking runs: {state.periodic_tracking_runs}",
            f"Total watch time tracked: {state.total_watch_time_tracked:.1f}s",
            f"Stream detection interval: {Config.STREAM_DETECTION_INTERVAL}s"
        ])
        
        debug_message = "\n".join(debug_lines)
        
        # Send as ephemeral message
        await interaction.response.send_message(f"```\n{debug_message}\n```", ephemeral=True)
        
    except Exception as e:
        logger.error(f"Watch debug error: {e}")
        await interaction.response.send_message(f"❌ Debug error: {e}", ephemeral=True)

@bot.tree.command(name="reset_stats", description="Reset viewing statistics (admin only)")
async def reset_stats_command(interaction: discord.Interaction):
    """Reset all viewing statistics"""
    if not is_admin(interaction.user):
        await interaction.response.send_message("❌ Only admins can reset statistics.", ephemeral=True)
        return
    
    try:
        # Reset watch time tracking
        state.user_watch_time.clear()
        state.user_genre_preferences.clear()
        state.user_media_history.clear()
        state.daily_stats.clear()
        
        await interaction.response.send_message("✅ All viewing statistics have been reset.", ephemeral=True)
        logger.info(f"📊 Statistics reset by {interaction.user.display_name}")
        
    except Exception as e:
        logger.error(f"Error resetting stats: {e}")
        await interaction.response.send_message("❌ Failed to reset statistics.", ephemeral=True)

@bot.event
async def on_command_error(ctx, error):
    """Enhanced command error handling with recovery"""
    try:
        if isinstance(error, commands.CommandNotFound):
            return
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You don't have permission to use this command.")
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"⏱️ Command is on cooldown. Try again in {error.retry_after:.1f} seconds.")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("❌ Invalid argument provided. Please check your input.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"❌ Missing required argument: {error.param.name}")
        else:
            # Use error handler for unknown errors
            if Config.ENABLE_ERROR_RECOVERY:
                await error_handler.handle_discord_error(error, f"Command: {ctx.command}")
            
            logger.error(f"Command error: {error}")
            
            # Send user-friendly error message
            embed = discord.Embed(
                title="❌ Command Error",
                description="An unexpected error occurred while executing the command.",
                color=Config.EMBED_COLOR_ERROR,
                timestamp=datetime.now()
            )
            
            if Config.ENABLE_ERROR_NOTIFICATIONS:
                embed.add_field(
                    name="Error Details",
                    value=f"```{str(error)[:200]}```",
                    inline=False
                )
            
            embed.add_field(
                name="What to do",
                value="• Try the command again\n• Check if VLC is running\n• Contact an admin if the problem persists",
                inline=False
            )
            
            await ctx.send(embed=embed)
            
    except Exception as handler_error:
        logger.error(f"Error in error handler: {handler_error}")
        await ctx.send("❌ An error occurred while executing the command.")

@bot.event
async def on_error(event, *args, **kwargs):
    """Handle general bot errors"""
    try:
        logger.error(f"Bot error in event {event}: {args}, {kwargs}")
        
        if Config.ENABLE_ERROR_RECOVERY:
            # Try to recover from the error
            await asyncio.sleep(1)  # Brief delay before recovery
            
    except Exception as recovery_error:
        logger.error(f"Error recovery failed: {recovery_error}")

async def safe_execute(func, *args, **kwargs):
    """Safely execute a function with error handling"""
    try:
        return await func(*args, **kwargs)
    except Exception as e:
        if Config.ENABLE_ERROR_RECOVERY:
            recovery_success = await error_handler.handle_vlc_error(e, f"Function: {func.__name__}")
            if recovery_success:
                try:
                    return await func(*args, **kwargs)
                except Exception as retry_error:
                    logger.error(f"Retry failed for {func.__name__}: {retry_error}")
        
        logger.error(f"Error in {func.__name__}: {e}")
        return None

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