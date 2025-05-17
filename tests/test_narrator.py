import pytest
from unittest.mock import patch, MagicMock, call
import os # For os.path.exists

from src.narrator import narrate_price
from src.app_config import AppConfig # For spec

@pytest.fixture
def mock_narrator_app_settings_values():
    """Fixture to provide a dictionary of mock AppConfig values for narrator tests."""
    return {
        "temp_audio_file": "test_temp_audio.mp3",
        "narration_lang": "en",
        "narration_slow": False
    }

# Patch app_settings where it's imported in narrator.py
# Patch gTTS, playsound, and os functions at their source
@patch('src.narrator.app_settings', spec=AppConfig)
@patch('src.narrator.gTTS')
@patch('src.narrator.playsound')
@patch('src.narrator.os.path.exists')
@patch('src.narrator.os.remove')
def test_narrate_price_success_defaults(mock_os_remove, mock_os_exists, mock_playsound, mock_gtts_constructor, mock_app_settings_instance, mock_narrator_app_settings_values):
    """Test successful narration with default language and speed from config."""
    # Configure the patched app_settings instance
    for key, value in mock_narrator_app_settings_values.items():
        setattr(mock_app_settings_instance, key, value)
    
    mock_tts_instance = MagicMock()
    mock_gtts_constructor.return_value = mock_tts_instance
    mock_os_exists.return_value = True # Simulate temp file exists for cleanup

    crypto_name = "Bitcoin"
    price = 60000.75
    currency = "USD"
    expected_text = f"The current price for {crypto_name} is {price:,.2f} {currency}."
    expected_temp_file = mock_narrator_app_settings_values["temp_audio_file"]

    narrate_price(crypto_name, price, currency) # Uses lang/slow from app_settings via narrator's defaults

    mock_gtts_constructor.assert_called_once_with(
        text=expected_text, 
        lang=mock_narrator_app_settings_values["narration_lang"], 
        slow=mock_narrator_app_settings_values["narration_slow"]
    )
    mock_tts_instance.save.assert_called_once_with(expected_temp_file)
    mock_playsound.assert_called_once_with(expected_temp_file)
    mock_os_exists.assert_called_once_with(expected_temp_file)
    mock_os_remove.assert_called_once_with(expected_temp_file)

@patch('src.narrator.app_settings', spec=AppConfig)
@patch('src.narrator.gTTS')
@patch('src.narrator.playsound')
@patch('src.narrator.os.path.exists')
@patch('src.narrator.os.remove')
def test_narrate_price_success_override_lang_slow(mock_os_remove, mock_os_exists, mock_playsound, mock_gtts_constructor, mock_app_settings_instance, mock_narrator_app_settings_values):
    """Test successful narration with lang and slow overridden by function arguments."""
    for key, value in mock_narrator_app_settings_values.items():
        setattr(mock_app_settings_instance, key, value)
    
    mock_tts_instance = MagicMock()
    mock_gtts_constructor.return_value = mock_tts_instance
    mock_os_exists.return_value = True

    crypto_name = "Ethereum"
    price = 2000.50
    currency = "EUR"
    override_lang = "es"
    override_slow = True
    expected_text = f"The current price for {crypto_name} is {price:,.2f} {currency}."
    expected_temp_file = mock_narrator_app_settings_values["temp_audio_file"]

    narrate_price(crypto_name, price, currency, lang=override_lang, slow=override_slow)

    mock_gtts_constructor.assert_called_once_with(
        text=expected_text, 
        lang=override_lang, 
        slow=override_slow
    )
    mock_tts_instance.save.assert_called_once_with(expected_temp_file)
    mock_playsound.assert_called_once_with(expected_temp_file)
    mock_os_exists.assert_called_once_with(expected_temp_file)
    mock_os_remove.assert_called_once_with(expected_temp_file)

@patch('src.narrator.app_settings', spec=AppConfig)
@patch('src.narrator.gTTS')
@patch('src.narrator.playsound')
@patch('src.narrator.os.path.exists')
@patch('src.narrator.os.remove')
def test_narrate_price_temp_file_does_not_exist_for_cleanup(mock_os_remove, mock_os_exists, mock_playsound, mock_gtts_constructor, mock_app_settings_instance, mock_narrator_app_settings_values):
    """Test cleanup logic when the temporary audio file doesn't exist."""
    for key, value in mock_narrator_app_settings_values.items():
        setattr(mock_app_settings_instance, key, value)

    mock_tts_instance = MagicMock()
    mock_gtts_constructor.return_value = mock_tts_instance
    mock_os_exists.return_value = False # Simulate temp file does NOT exist

    narrate_price("TestCoin", 100, "USD")

    expected_temp_file = mock_narrator_app_settings_values["temp_audio_file"]
    mock_os_exists.assert_called_once_with(expected_temp_file)
    mock_os_remove.assert_not_called() # os.remove should not be called if file doesn't exist

@patch('src.narrator.app_settings', spec=AppConfig)
@patch('src.narrator.gTTS')
@patch('src.narrator.playsound')
@patch('src.narrator.os.path.exists')
@patch('src.narrator.os.remove')
def test_narrate_price_error_during_gtts_init(mock_os_remove, mock_os_exists, mock_playsound, mock_gtts_constructor, mock_app_settings_instance, mock_narrator_app_settings_values):
    """Test error handling when gTTS constructor raises an exception."""
    for key, value in mock_narrator_app_settings_values.items():
        setattr(mock_app_settings_instance, key, value)

    mock_gtts_constructor.side_effect = Exception("gTTS init failed")
    # os.path.exists might be called if the exception occurs after file creation, but for gTTS init error, it won't proceed to save/play.
    # Depending on exact structure, ensure os.path.exists is set if temp file interaction is possible before this point.
    # For now, assume error is before any file interaction for this specific test.
    mock_os_exists.return_value = False 

    narrate_price("TestCoin", 100, "USD")

    mock_tts_instance = MagicMock() # Need a ref if we were to check its calls
    mock_gtts_constructor.return_value = mock_tts_instance
    mock_tts_instance.save.assert_not_called()
    mock_playsound.assert_not_called()
    mock_os_remove.assert_not_called() # File cleanup shouldn't happen if save didn't occur.

@patch('src.narrator.app_settings', spec=AppConfig)
@patch('src.narrator.gTTS')
@patch('src.narrator.playsound')
@patch('src.narrator.os.path.exists')
@patch('src.narrator.os.remove')
def test_narrate_price_error_during_save(mock_os_remove, mock_os_exists, mock_playsound, mock_gtts_constructor, mock_app_settings_instance, mock_narrator_app_settings_values):
    """Test error handling when tts.save() raises an exception."""
    for key, value in mock_narrator_app_settings_values.items():
        setattr(mock_app_settings_instance, key, value)

    mock_tts_instance = MagicMock()
    mock_tts_instance.save.side_effect = Exception("Save failed")
    mock_gtts_constructor.return_value = mock_tts_instance
    # If save fails, the file might or might not exist. Let's assume it might have been created then failed to write.
    # Or, it might fail before creation. For this test, let's say it doesn't exist or the status is ambiguous.
    # The key is that playsound isn't called and cleanup is attempted.
    mock_os_exists.return_value = False # Or True, depending on how robust you want the test for partial file creation

    narrate_price("TestCoin", 100, "USD")

    mock_playsound.assert_not_called()
    # Assert that cleanup is still attempted
    expected_temp_file = mock_narrator_app_settings_values["temp_audio_file"]
    mock_os_exists.assert_called_once_with(expected_temp_file)
    if mock_os_exists.return_value:
        mock_os_remove.assert_called_once_with(expected_temp_file)
    else:
        mock_os_remove.assert_not_called()

@patch('src.narrator.app_settings', spec=AppConfig)
@patch('src.narrator.gTTS')
@patch('src.narrator.playsound')
@patch('src.narrator.os.path.exists')
@patch('src.narrator.os.remove')
def test_narrate_price_error_during_playsound(mock_os_remove, mock_os_exists, mock_playsound, mock_gtts_constructor, mock_app_settings_instance, mock_narrator_app_settings_values):
    """Test error handling when playsound() raises an exception."""
    for key, value in mock_narrator_app_settings_values.items():
        setattr(mock_app_settings_instance, key, value)
    
    mock_tts_instance = MagicMock()
    mock_gtts_constructor.return_value = mock_tts_instance
    mock_playsound.side_effect = Exception("Playsound failed")
    mock_os_exists.return_value = True # File was saved, now playing fails

    narrate_price("TestCoin", 100, "USD")

    expected_temp_file = mock_narrator_app_settings_values["temp_audio_file"]
    mock_tts_instance.save.assert_called_once_with(expected_temp_file)
    mock_playsound.assert_called_once_with(expected_temp_file)
    # Assert that cleanup is still attempted
    mock_os_exists.assert_called_once_with(expected_temp_file)
    mock_os_remove.assert_called_once_with(expected_temp_file)

@patch('src.narrator.app_settings', spec=AppConfig)
@patch('src.narrator.gTTS')
@patch('src.narrator.playsound')
@patch('src.narrator.os.path.exists')
@patch('src.narrator.os.remove')
def test_narrate_price_error_during_remove(mock_os_remove, mock_os_exists, mock_playsound, mock_gtts_constructor, mock_app_settings_instance, mock_narrator_app_settings_values):
    """Test error handling when os.remove() raises an exception during cleanup."""
    for key, value in mock_narrator_app_settings_values.items():
        setattr(mock_app_settings_instance, key, value)

    mock_tts_instance = MagicMock()
    mock_gtts_constructor.return_value = mock_tts_instance
    mock_os_exists.return_value = True
    mock_os_remove.side_effect = OSError("Failed to delete file") # Simulate an OS error

    # We don't need to assert an exception from narrate_price itself, as it catches this.
    # We just check that the functions were called as expected up to the point of error.
    narrate_price("TestCoin", 100, "USD") 

    expected_temp_file = mock_narrator_app_settings_values["temp_audio_file"]
    mock_tts_instance.save.assert_called_once_with(expected_temp_file)
    mock_playsound.assert_called_once_with(expected_temp_file)
    mock_os_exists.assert_called_once_with(expected_temp_file)
    mock_os_remove.assert_called_once_with(expected_temp_file)
    # Logger should have an error message, but testing logger output is more involved (caplog fixture)

# Test for when app_settings is None (config file failed to load)
@patch('src.narrator.app_settings', None) # Set app_settings to None in narrator.py
@patch('src.narrator.gTTS')
@patch('src.narrator.playsound')
@patch('src.narrator.os.path.exists')
@patch('src.narrator.os.remove')
def test_narrate_price_app_settings_none(mock_os_remove, mock_os_exists, mock_playsound, mock_gtts_constructor):
    """Test behavior when app_settings is None (config failed to load)."""
    mock_tts_instance = MagicMock()
    mock_gtts_constructor.return_value = mock_tts_instance
    mock_os_exists.return_value = True

    crypto_name = "FallbackCoin"
    price = 50
    currency = "CAD"
    expected_text = f"The current price for {crypto_name} is {price:,.2f} {currency}."
    
    # These are the hardcoded defaults in narrator.py when app_settings is None
    default_temp_file = "temp_price_narration.mp3" 
    default_lang = 'en'
    default_slow = False

    narrate_price(crypto_name, price, currency)

    mock_gtts_constructor.assert_called_once_with(
        text=expected_text, 
        lang=default_lang,  # Expecting hardcoded default lang in narrator
        slow=default_slow   # Expecting hardcoded default slow in narrator
    )
    mock_tts_instance.save.assert_called_once_with(default_temp_file)
    mock_playsound.assert_called_once_with(default_temp_file)
    mock_os_exists.assert_called_once_with(default_temp_file)
    mock_os_remove.assert_called_once_with(default_temp_file) 