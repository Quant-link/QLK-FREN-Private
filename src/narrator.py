from gtts import gTTS
from playsound import playsound
import os
import platform
import subprocess
import logging
import tempfile
import hashlib
import time
from typing import Dict, Tuple, Optional
from src.app_config import app_settings  # Import the application settings

# Configure logger for this module
logger = logging.getLogger(__name__)

# Use temp audio file from app_settings if available
TEMP_AUDIO_FILE = (
    app_settings.temp_audio_file if app_settings else "temp_price_narration.mp3"
)

# Cache for recently narrated prices to avoid redundant API calls and narrations
# Format: {cache_key: (timestamp, audio_file_path)}
_narration_cache: Dict[str, Tuple[float, str]] = {}
# Cache expiration time in seconds (default: 5 minutes)
CACHE_EXPIRATION = 300  # 5 minutes


def _generate_cache_key(crypto_name: str, price: float, currency: str, lang: str, slow: bool) -> str:
    """Generate a unique cache key for a price narration request."""
    # Create a unique key for this narration request
    key_string = f"{crypto_name}:{price:.2f}:{currency}:{lang}:{slow}"
    return hashlib.md5(key_string.encode()).hexdigest()


def play_audio_fallback(audio_file_path: str) -> bool:
    """
    Platform-specific fallback for audio playback when playsound fails.
    Returns True if playback succeeded, False otherwise.
    
    Args:
        audio_file_path (str): Path to the audio file to play.
    
    Returns:
        bool: True if playback succeeded, False otherwise.
    """
    system = platform.system().lower()
    success = False
    
    logger.debug(f"Attempting fallback audio playback on {system} platform")
    
    try:
        if system == "windows":
            # Windows fallback using PowerShell
            command = [
                "powershell",
                "-c", 
                f"(New-Object Media.SoundPlayer '{audio_file_path}').PlaySync()"
            ]
            subprocess.run(command, check=True)
            success = True
        elif system == "darwin":  # macOS
            # macOS fallback using afplay
            command = ["afplay", audio_file_path]
            subprocess.run(command, check=True)
            success = True
        elif system == "linux":
            # Try multiple Linux audio players in order
            players = [
                ["paplay", audio_file_path],
                ["aplay", "-q", audio_file_path],
                ["mpg123", "-q", audio_file_path],
                ["mpg321", "-q", audio_file_path],
            ]
            
            for player in players:
                try:
                    subprocess.run(player, check=True)
                    success = True
                    break
                except (subprocess.SubprocessError, FileNotFoundError):
                    continue
        
        if success:
            logger.info("Fallback audio playback succeeded")
        else:
            logger.warning(f"No suitable audio player found on {system} platform")
            
    except Exception as e:
        logger.error(f"Fallback audio playback failed: {e}", exc_info=True)
    
    return success


def play_audio(audio_file_path: str) -> bool:
    """
    Play an audio file using the most reliable method for the current platform.
    Tries playsound first, then falls back to platform-specific methods if needed.
    
    Args:
        audio_file_path (str): Path to the audio file to play.
    
    Returns:
        bool: True if playback succeeded, False otherwise.
    """
    # First attempt: playsound (for compatibility with existing code)
    try:
        playsound(audio_file_path)
        return True
    except Exception as e:
        logger.warning(f"Primary playsound playback failed: {e}. Trying fallbacks...")
    
    # Second attempt: Use platform-specific fallbacks
    return play_audio_fallback(audio_file_path)


def get_cached_narration(
    crypto_name: str,
    price: float,
    currency: str,
    lang: str = "en",
    slow: bool = False
) -> Optional[str]:
    """
    Check if we have a recent cached narration for the given parameters.
    
    Args:
        crypto_name (str): The name of the cryptocurrency.
        price (float): The price of the cryptocurrency.
        currency (str): The currency of the price.
        lang (str): The language for narration.
        slow (bool): Whether to use slow narration.
        
    Returns:
        Optional[str]: Path to the cached audio file if valid, None otherwise.
    """
    cache_key = _generate_cache_key(crypto_name, price, currency, lang, slow)
    
    if cache_key in _narration_cache:
        timestamp, file_path = _narration_cache[cache_key]
        current_time = time.time()
        
        # Check if cache is still valid and file exists
        if (current_time - timestamp) < CACHE_EXPIRATION and os.path.exists(file_path):
            logger.debug(f"Using cached narration from {file_path}")
            return file_path
            
        # Remove expired entry from cache
        del _narration_cache[cache_key]
    
    return None


def narrate_price(
    crypto_name: str,
    price: float,
    currency: str = "USD",
    lang: str = "en",
    slow: bool = False,
    force_new: bool = False,
) -> bool:
    """
    Narrates the given cryptocurrency name and price using gTTS.
    
    Args:
        crypto_name (str): The name of the cryptocurrency.
        price (float): The price of the cryptocurrency.
        currency (str): The currency of the price (e.g., "USD", "EUR").
        lang (str): The language for narration.
        slow (bool): Whether to narrate slowly.
        force_new (bool): Force creation of new narration even if cached version exists.
        
    Returns:
        bool: True if narration was successful, False otherwise.
    """
    if not app_settings:
        logger.error(
            "App settings not loaded. Narration may use defaults & might not function as expected."
        )

    # Set default values based on app_settings
    narration_language = lang
    narration_is_slow = slow
    keep_on_error = False

    if app_settings:
        if not lang or lang == "en":  # Only use app_settings if default language was used
            narration_language = app_settings.narration_lang
        if not isinstance(slow, bool):  # Only use app_settings if default slow was used
            narration_is_slow = app_settings.narration_slow
        if hasattr(app_settings, 'keep_audio_on_error'):
            keep_on_error = app_settings.keep_audio_on_error
    else:
        logger.warning(f"Using default narration language: {narration_language}")
        logger.warning(f"Using default narration speed (slow={narration_is_slow})")

    # Check cache first if not forcing new narration
    if not force_new:
        cached_file = get_cached_narration(crypto_name, price, currency, narration_language, narration_is_slow)
        if cached_file:
            return play_audio(cached_file)

    # Format price with thousands separator and 2 decimal places
    price_str = f"{price:,.2f}"
    text_to_narrate = f"The current price for {crypto_name} is {price_str} {currency}."
    logger.info(f"Preparing to narrate: {text_to_narrate}")

    # Determine output filename and path
    audio_file_created = False
    current_temp_audio_file = TEMP_AUDIO_FILE
    use_temp_dir = False
    
    if app_settings and app_settings.temp_audio_file:
        current_temp_audio_file = app_settings.temp_audio_file
    else:
        # Create a unique filename in the temp directory
        audio_dir = tempfile.gettempdir()
        cache_key = _generate_cache_key(crypto_name, price, currency, narration_language, narration_is_slow)
        current_temp_audio_file = os.path.join(audio_dir, f"price_narration_{cache_key[:8]}.mp3")
        use_temp_dir = True
        logger.debug(f"Using system temp directory for audio file: {current_temp_audio_file}")

    playback_successful = False
    
    try:
        logger.info(f"Narrating with language: '{narration_language}', slow: {narration_is_slow}")
        tts = gTTS(
            text=text_to_narrate, lang=narration_language, slow=narration_is_slow
        )
        logger.debug(f"Saving TTS audio to {current_temp_audio_file}")
        tts.save(current_temp_audio_file)
        audio_file_created = True
        
        # Save to cache
        cache_key = _generate_cache_key(crypto_name, price, currency, narration_language, narration_is_slow)
        _narration_cache[cache_key] = (time.time(), current_temp_audio_file)
        
        logger.debug(f"Playing audio file: {current_temp_audio_file}")
        playback_successful = play_audio(current_temp_audio_file)
            
        if playback_successful:
            logger.info("Narration played successfully")
        else:
            # If audio file was created but playback failed, inform the user about the file location
            logger.error(f"Could not play audio. File saved at: {os.path.abspath(current_temp_audio_file)}")
            print(f"Audio could not be played. File saved at: {os.path.abspath(current_temp_audio_file)}")
            
    except Exception as e:
        logger.error(f"An error occurred during narration: {e}", exc_info=True)
        return False
    finally:
        # Only attempt to delete the file if:
        # 1. It was created AND
        # 2. We're not keeping it in cache AND
        # 3. Either playback was successful OR we're not keeping files on error
        if (audio_file_created and 
            not use_temp_dir and 
            (playback_successful or not keep_on_error)):
            try:
                logger.debug(f"Attempting to delete temporary audio file: {current_temp_audio_file}")
                os.remove(current_temp_audio_file)
                logger.debug(f"Temporary audio file deleted successfully")
            except Exception as e:
                logger.error(
                    f"Error deleting temp audio file '{current_temp_audio_file}': {e}",
                    exc_info=True,
                )
    
    return playback_successful
