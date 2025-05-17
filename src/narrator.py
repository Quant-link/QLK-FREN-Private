from gtts import gTTS
from playsound import playsound
import os
import logging

# Configure logger for this module
logger = logging.getLogger(__name__)

TEMP_AUDIO_FILE = "temp_price_narration.mp3"

def narrate_price(crypto_name: str, price: float, currency: str = "USD") -> None:
    """
    Narrates the given cryptocurrency name and price using gTTS.

    Args:
        crypto_name (str): The name of the cryptocurrency.
        price (float): The price of the cryptocurrency.
        currency (str): The currency of the price (e.g., "USD", "EUR").
    """
    # Format the price for a more natural narration
    # e.g., 60123.45 -> "sixty thousand one hundred twenty-three dollars and forty-five cents"
    # For this MVP, we'll keep it simple and use English.
    price_str = f"{price:,.2f}" # Format with commas and two decimal places
    text_to_narrate = f"The current price for {crypto_name} is {price_str} {currency}."
    logger.info(f"Preparing to narrate: {text_to_narrate}")

    try:
        tts = gTTS(text=text_to_narrate, lang='en', slow=False)
        logger.debug(f"Saving TTS audio to {TEMP_AUDIO_FILE}")
        tts.save(TEMP_AUDIO_FILE)
        logger.debug(f"Playing audio file: {TEMP_AUDIO_FILE}")
        playsound(TEMP_AUDIO_FILE)
        logger.info("Narration completed successfully.")
    except Exception as e:
        logger.error(f"An error occurred during narration: {e}", exc_info=True)
    finally:
        # Clean up the temporary audio file
        if os.path.exists(TEMP_AUDIO_FILE):
            try:
                logger.debug(f"Attempting to delete temporary audio file: {TEMP_AUDIO_FILE}")
                os.remove(TEMP_AUDIO_FILE)
                logger.debug(f"Temporary audio file {TEMP_AUDIO_FILE} deleted successfully.")
            except Exception as e:
                logger.error(f"Error deleting temporary audio file '{TEMP_AUDIO_FILE}': {e}", exc_info=True) 