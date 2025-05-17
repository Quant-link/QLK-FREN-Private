from gtts import gTTS
from playsound import playsound
import os
import logging
from src.app_config import app_settings # Import the application settings

# Configure logger for this module
logger = logging.getLogger(__name__)

# Use temp audio file from app_settings if available
TEMP_AUDIO_FILE = app_settings.temp_audio_file if app_settings else "temp_price_narration.mp3"

def narrate_price(crypto_name: str, price: float, currency: str = "USD") -> None:
    """
    Narrates the given cryptocurrency name and price using gTTS.

    Args:
        crypto_name (str): The name of the cryptocurrency.
        price (float): The price of the cryptocurrency.
        currency (str): The currency of the price (e.g., "USD", "EUR").
    """
    if not app_settings:
        logger.error("Application settings not loaded. Narration may use default or hardcoded values and might not function as expected.")

    price_str = f"{price:,.2f}"
    text_to_narrate = f"The current price for {crypto_name} is {price_str} {currency}."
    logger.info(f"Preparing to narrate: {text_to_narrate}")

    current_temp_audio_file = TEMP_AUDIO_FILE
    if app_settings and app_settings.temp_audio_file:
        current_temp_audio_file = app_settings.temp_audio_file
    else:
        logger.warning(f"Using default temporary audio file name: {current_temp_audio_file}")

    try:
        tts = gTTS(text=text_to_narrate, lang='en', slow=False)
        logger.debug(f"Saving TTS audio to {current_temp_audio_file}")
        tts.save(current_temp_audio_file)
        logger.debug(f"Playing audio file: {current_temp_audio_file}")
        playsound(current_temp_audio_file)
        logger.info("Narration completed successfully.")
    except Exception as e:
        logger.error(f"An error occurred during narration: {e}", exc_info=True)
    finally:
        if os.path.exists(current_temp_audio_file):
            try:
                logger.debug(f"Attempting to delete temporary audio file: {current_temp_audio_file}")
                os.remove(current_temp_audio_file)
                logger.debug(f"Temporary audio file {current_temp_audio_file} deleted successfully.")
            except Exception as e:
                logger.error(f"Error deleting temporary audio file '{current_temp_audio_file}': {e}", exc_info=True) 