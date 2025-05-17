from gtts import gTTS
from playsound import playsound
import os
import logging
from src.app_config import app_settings  # Import the application settings

# Configure logger for this module
logger = logging.getLogger(__name__)

# Use temp audio file from app_settings if available
TEMP_AUDIO_FILE = (
    app_settings.temp_audio_file if app_settings else "temp_price_narration.mp3"
)


def narrate_price(
    crypto_name: str,
    price: float,
    currency: str = "USD",
    lang: str = "en",
    slow: bool = False,
) -> None:
    """
    Narrates the given cryptocurrency name and price using gTTS.

    Args:
        crypto_name (str): The name of the cryptocurrency.
        price (float): The price of the cryptocurrency.
        currency (str): The currency of the price (e.g., "USD", "EUR").
        lang (str): The language for narration.
        slow (bool): Whether to narrate slowly.
    """
    if not app_settings:
        logger.error(
            "App settings not loaded. Narration may use defaults & might not function as expected."
        )

    price_str = f"{price:,.2f}"
    text_to_narrate = f"The current price for {crypto_name} is {price_str} {currency}."
    logger.info(f"Preparing to narrate: {text_to_narrate}")

    current_temp_audio_file = TEMP_AUDIO_FILE
    # Use provided lang and slow parameters, falling back to app_settings or defaults if necessary
    narration_language = lang
    narration_is_slow = slow

    if app_settings:
        if app_settings.temp_audio_file:
            current_temp_audio_file = app_settings.temp_audio_file
        # CLI/direct parameters take precedence. If they were not default, they are used.
        # If they were default, then config settings are effectively used (via main.py defaults for CLI).
    else:
        logger.warning(
            f"Using default temporary audio file name: {current_temp_audio_file}"
        )
        logger.warning(
            f"Using narr. lang: {narration_language} (app_settings not available)"
        )  # noqa: E501
        logger.warning(
            f"Using narr. speed (slow={narration_is_slow}) (app_settings not available)"
        )

    try:
        logger.info(
            f"Narrating with language: '{narration_language}', slow: {narration_is_slow}"
        )
        tts = gTTS(
            text=text_to_narrate, lang=narration_language, slow=narration_is_slow
        )
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
                logger.debug(
                    f"Attempting to delete temporary audio file: {current_temp_audio_file}"
                )
                os.remove(current_temp_audio_file)
                logger.debug(
                    f"Temporary audio file {current_temp_audio_file} deleted successfully."
                )
            except Exception as e:
                logger.error(
                    f"Error deleting temp audio file '{current_temp_audio_file}': {e}",
                    exc_info=True,
                )
