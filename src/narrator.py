from gtts import gTTS
from playsound import playsound
import os

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
    print(f"Narrating: {text_to_narrate}")

    try:
        tts = gTTS(text=text_to_narrate, lang='en', slow=False)
        tts.save(TEMP_AUDIO_FILE)
        playsound(TEMP_AUDIO_FILE)
    except Exception as e:
        print(f"An error occurred during narration: {e}")
    finally:
        # Clean up the temporary audio file
        if os.path.exists(TEMP_AUDIO_FILE):
            try:
                os.remove(TEMP_AUDIO_FILE)
            except Exception as e:
                print(f"Error deleting temporary audio file '{TEMP_AUDIO_FILE}': {e}") 