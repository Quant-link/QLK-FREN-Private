from gtts import gTTS
import pygame
import os
import platform
import subprocess
import logging
import tempfile
import hashlib
import time
from typing import Dict, Tuple, Optional, List, Any, Union
from src.app_config import app_settings  # Import the application settings

# Configure logger for this module
logger = logging.getLogger(__name__)

# Initialize pygame mixer for audio playback
pygame.mixer.init()

# Use temp audio file from app_settings if available
TEMP_AUDIO_FILE = (
    app_settings.temp_audio_file if app_settings else "temp_price_narration.mp3"
)

# Cache for recently narrated prices to avoid redundant API calls and narrations
# Format: {cache_key: (timestamp, audio_file_path)}
_narration_cache: Dict[str, Tuple[float, str]] = {}
# Cache expiration time in seconds (default: 5 minutes)
CACHE_EXPIRATION = app_settings.cache_expiration if app_settings and hasattr(app_settings, 'cache_expiration') else 300


def _generate_cache_key(text_to_narrate: str, lang: str, slow: bool) -> str:
    """Generate a unique cache key for a narration request."""
    # Create a unique key for this narration request
    key_string = f"{text_to_narrate}:{lang}:{slow}"
    return hashlib.md5(key_string.encode()).hexdigest()


def play_audio_fallback(audio_file_path: str) -> bool:
    """
    Platform-specific fallback for audio playback when pygame fails.
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
    Play an audio file using pygame mixer with fallback to platform-specific methods.
    
    Args:
        audio_file_path (str): Path to the audio file to play.
    
    Returns:
        bool: True if playback succeeded, False otherwise.
    """
    # First attempt: pygame (more reliable than playsound)
    try:
        pygame.mixer.music.load(audio_file_path)
        pygame.mixer.music.play()
        
        # Wait for playback to finish
        while pygame.mixer.music.get_busy():
            pygame.time.wait(100)
            
        return True
    except Exception as e:
        logger.warning(f"Pygame audio playback failed: {e}. Trying fallbacks...")
    
    # Second attempt: Use platform-specific fallbacks
    return play_audio_fallback(audio_file_path)


def get_cached_narration(
    text_to_narrate: str,
    lang: str = "en",
    slow: bool = False
) -> Optional[str]:
    """
    Check if we have a recent cached narration for the given parameters.
    
    Args:
        text_to_narrate (str): The text to be narrated.
        lang (str): The language for narration.
        slow (bool): Whether to use slow narration.
        
    Returns:
        Optional[str]: Path to the cached audio file if valid, None otherwise.
    """
    # Special handling for cache settings
    cache_enabled = True
    cache_expiration = CACHE_EXPIRATION
    
    if app_settings and hasattr(app_settings, 'cache_enabled'):
        cache_enabled = app_settings.cache_enabled
        
    # If cache is disabled or the narration cache array is too large, return None
    if not cache_enabled:
        return None
        
    # Check if we have too many items and need to clean up
    if app_settings and hasattr(app_settings, 'cache_max_items') and len(_narration_cache) > app_settings.cache_max_items:
        # Basic cleanup - remove oldest entries
        _cleanup_cache()
    
    cache_key = _generate_cache_key(text_to_narrate, lang, slow)
    
    if cache_key in _narration_cache:
        timestamp, file_path = _narration_cache[cache_key]
        current_time = time.time()
        
        # Check if cache is still valid and file exists
        if (current_time - timestamp) < cache_expiration and os.path.exists(file_path):
            logger.debug(f"Using cached narration from {file_path}")
            return file_path
            
        # Remove expired entry from cache
        del _narration_cache[cache_key]
    
    return None


def _cleanup_cache() -> None:
    """
    Remove the oldest entries from the narration cache when it gets too large.
    """
    if not _narration_cache:
        return
        
    max_items = 100  # Default
    if app_settings and hasattr(app_settings, 'cache_max_items'):
        max_items = app_settings.cache_max_items
        
    # If the cache is already within limits, do nothing
    if len(_narration_cache) <= max_items:
        return
        
    # Sort by timestamp (first item in tuple)
    sorted_items = sorted(_narration_cache.items(), key=lambda x: x[1][0])
    
    # Determine how many items to remove
    items_to_remove = len(_narration_cache) - max_items
    
    # Remove the oldest items
    for i in range(items_to_remove):
        key, (_, file_path) = sorted_items[i]
        del _narration_cache[key]
        logger.debug(f"Removed old cache entry: {key}")


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

    # Format price with thousands separator and 2 decimal places
    price_str = f"{price:,.2f}"
    text_to_narrate = f"The current price for {crypto_name} is {price_str} {currency}."

    return narrate_text(
        text_to_narrate, 
        lang=narration_language, 
        slow=narration_is_slow, 
        force_new=force_new, 
        keep_on_error=keep_on_error
    )


def narrate_price_with_change(
    crypto_data: Dict[str, Any],
    include_24h: bool = True,
    include_7d: bool = False,
    include_30d: bool = False,
    lang: str = "en",
    slow: bool = False,
    force_new: bool = False,
) -> bool:
    """
    Narrates cryptocurrency price along with price changes over different time periods.
    
    Args:
        crypto_data (Dict[str, Any]): Dictionary with crypto data from get_crypto_price_with_change()
        include_24h (bool): Whether to include 24-hour price change in narration
        include_7d (bool): Whether to include 7-day price change in narration
        include_30d (bool): Whether to include 30-day price change in narration
        lang (str): The language for narration
        slow (bool): Whether to narrate slowly
        force_new (bool): Force creation of new narration even if cached version exists
        
    Returns:
        bool: True if narration was successful, False otherwise
    """
    if not crypto_data.get("success", False) or crypto_data.get("current_price") is None:
        logger.error("Cannot narrate price with change: invalid crypto data provided")
        return False
        
    # Build the narration text
    crypto_name = crypto_data.get("name", "Unknown")
    price = crypto_data.get("current_price", 0.0)
    currency = crypto_data.get("currency", "USD")
    
    # Format price with thousands separator and 2 decimal places
    price_str = f"{price:,.2f}"
    
    # Start with the current price
    narration_text = f"The current price for {crypto_name} is {price_str} {currency}."
    
    # Add 24-hour change if requested and available
    if include_24h and "price_change_24h" in crypto_data and crypto_data["price_change_24h"] is not None:
        change_24h = crypto_data["price_change_24h"]
        direction = "up" if change_24h >= 0 else "down"
        narration_text += f" It has gone {direction} {abs(change_24h):.2f} percent in the last 24 hours."
    
    # Add 7-day change if requested and available
    if include_7d and "price_change_7d" in crypto_data and crypto_data["price_change_7d"] is not None:
        change_7d = crypto_data["price_change_7d"]
        direction = "up" if change_7d >= 0 else "down"
        narration_text += f" Over the past 7 days, it has gone {direction} {abs(change_7d):.2f} percent."
    
    # Add 30-day change if requested and available
    if include_30d and "price_change_30d" in crypto_data and crypto_data["price_change_30d"] is not None:
        change_30d = crypto_data["price_change_30d"]
        direction = "up" if change_30d >= 0 else "down"
        narration_text += f" In the last 30 days, it has gone {direction} {abs(change_30d):.2f} percent."
    
    # Get default values from app_settings
    narration_language = lang
    narration_is_slow = slow
    keep_on_error = False

    if app_settings:
        if not lang or lang == "en":
            narration_language = app_settings.narration_lang
        if not isinstance(slow, bool):
            narration_is_slow = app_settings.narration_slow
        if hasattr(app_settings, 'keep_audio_on_error'):
            keep_on_error = app_settings.keep_audio_on_error
            
    return narrate_text(
        narration_text, 
        lang=narration_language, 
        slow=narration_is_slow, 
        force_new=force_new, 
        keep_on_error=keep_on_error
    )


def narrate_text(
    text_to_narrate: str,
    lang: str = "en",
    slow: bool = False,
    force_new: bool = False,
    keep_on_error: bool = False,
) -> bool:
    """
    General-purpose function to narrate any text using gTTS.
    
    Args:
        text_to_narrate (str): The text to narrate
        lang (str): The language for narration
        slow (bool): Whether to narrate slowly
        force_new (bool): Force creation of new narration even if cached version exists
        keep_on_error (bool): Whether to keep the audio file if playback fails
        
    Returns:
        bool: True if narration was successful, False otherwise
    """
    logger.info(f"Preparing to narrate: {text_to_narrate}")
    
    # Check cache first if not forcing new narration
    if not force_new:
        cached_file = get_cached_narration(text_to_narrate, lang, slow)
        if cached_file:
            return play_audio(cached_file)

    # Determine output filename and path
    audio_file_created = False
    current_temp_audio_file = TEMP_AUDIO_FILE
    use_temp_dir = False
    
    if app_settings and app_settings.temp_audio_file:
        current_temp_audio_file = app_settings.temp_audio_file
    else:
        # Create a unique filename in the temp directory
        audio_dir = tempfile.gettempdir()
        cache_key = _generate_cache_key(text_to_narrate, lang, slow)
        current_temp_audio_file = os.path.join(audio_dir, f"narration_{cache_key[:8]}.mp3")
        use_temp_dir = True
        logger.debug(f"Using system temp directory for audio file: {current_temp_audio_file}")

    playback_successful = False
    
    try:
        logger.info(f"Narrating with language: '{lang}', slow: {slow}")
        tts = gTTS(
            text=text_to_narrate, lang=lang, slow=slow
        )
        logger.debug(f"Saving TTS audio to {current_temp_audio_file}")
        tts.save(current_temp_audio_file)
        audio_file_created = True
        
        # Save to cache
        cache_key = _generate_cache_key(text_to_narrate, lang, slow)
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


def narrate_multiple_prices(
    crypto_data_list: List[Dict[str, Any]],
    include_changes: bool = False,
    narrate_intro: bool = True,
    lang: str = "en",
    slow: bool = False,
    force_new: bool = False,
) -> int:
    """
    Narrates prices for multiple cryptocurrencies in sequence.
    
    Args:
        crypto_data_list (List[Dict[str, Any]]): List of crypto data dictionaries
        include_changes (bool): Whether to include price changes in the narration
        narrate_intro (bool): Whether to narrate an introduction
        lang (str): The language for narration
        slow (bool): Whether to narrate slowly
        force_new (bool): Force creation of new narrations even if cached versions exist
        
    Returns:
        int: Number of successfully narrated cryptocurrencies
    """
    if not crypto_data_list:
        logger.warning("No cryptocurrency data provided for narration")
        return 0
        
    # Get default values from app_settings
    narration_language = lang
    narration_is_slow = slow
    keep_on_error = False

    if app_settings:
        if not lang or lang == "en":
            narration_language = app_settings.narration_lang
        if not isinstance(slow, bool):
            narration_is_slow = app_settings.narration_slow
        if hasattr(app_settings, 'keep_audio_on_error'):
            keep_on_error = app_settings.keep_audio_on_error
    
    # Narrate introduction if requested
    if narrate_intro and crypto_data_list:
        intro_text = f"Here are the current prices for {len(crypto_data_list)} cryptocurrencies."
        narrate_text(intro_text, lang=narration_language, slow=narration_is_slow, force_new=force_new)
        
    success_count = 0
    
    # Narrate each cryptocurrency
    for crypto_data in crypto_data_list:
        if not crypto_data.get("success", False) or crypto_data.get("current_price") is None:
            logger.warning(f"Skipping invalid crypto data: {crypto_data.get('name', 'Unknown')}")
            continue
            
        # Use the appropriate narration function based on whether changes should be included
        if include_changes:
            success = narrate_price_with_change(
                crypto_data,
                include_24h=True,
                include_7d=False,
                include_30d=False,
                lang=narration_language,
                slow=narration_is_slow,
                force_new=force_new
            )
        else:
            success = narrate_price(
                crypto_data.get("name", "Unknown"),
                crypto_data.get("current_price", 0.0),
                crypto_data.get("currency", "USD"),
                lang=narration_language,
                slow=narration_is_slow,
                force_new=force_new
            )
            
        if success:
            success_count += 1
            # Add a small pause between narrations
            time.sleep(0.5)
    
    # Narrate conclusion if more than one crypto was successfully narrated
    if success_count > 1:
        conclusion_text = "That concludes the cryptocurrency price update."
        narrate_text(conclusion_text, lang=narration_language, slow=narration_is_slow, force_new=force_new)
    
    return success_count
