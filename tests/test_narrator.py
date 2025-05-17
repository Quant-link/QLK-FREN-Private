import pytest
from unittest.mock import patch, MagicMock

from src.narrator import narrate_price, play_audio_fallback
from src.app_config import AppConfig  # For spec
import subprocess


@pytest.fixture
def mock_narrator_app_settings_values():
    """Fixture to provide a dictionary of mock AppConfig values for narrator tests."""
    return {
        "temp_audio_file": "test_temp_audio.mp3",
        "narration_lang": "en",
        "narration_slow": False,
        "keep_audio_on_error": False,
    }


# Patch app_settings where it's imported in narrator.py
# Patch gTTS, playsound, and os functions at their source
@patch("src.narrator.app_settings", spec=AppConfig)
@patch("src.narrator.gTTS")
@patch("src.narrator.playsound")
@patch("src.narrator.os.path.exists")
@patch("src.narrator.os.remove")
def test_narrate_price_success_defaults(
    mock_os_remove,
    mock_os_exists,
    mock_playsound,
    mock_gtts_constructor,
    mock_app_settings_instance,
    mock_narrator_app_settings_values,
):
    """Test successful narration with default language and speed from config."""
    # Configure the patched app_settings instance
    for key, value in mock_narrator_app_settings_values.items():
        setattr(mock_app_settings_instance, key, value)

    mock_tts_instance = MagicMock()
    mock_gtts_constructor.return_value = mock_tts_instance
    mock_os_exists.return_value = True  # Simulate temp file exists for cleanup

    crypto_name = "Bitcoin"
    price = 60000.75
    currency = "USD"
    expected_text = f"The current price for {crypto_name} is {price:,.2f} {currency}."
    expected_temp_file = mock_narrator_app_settings_values["temp_audio_file"]

    narrate_price(
        crypto_name, price, currency
    )  # Uses lang/slow from app_settings via narrator's defaults

    mock_gtts_constructor.assert_called_once_with(
        text=expected_text,
        lang=mock_narrator_app_settings_values["narration_lang"],
        slow=mock_narrator_app_settings_values["narration_slow"],
    )
    mock_tts_instance.save.assert_called_once_with(expected_temp_file)
    mock_playsound.assert_called_once_with(expected_temp_file)
    # We no longer expect os.path.exists to be called as we're using audio_file_created flag
    mock_os_remove.assert_called_once_with(expected_temp_file)


@patch("src.narrator.app_settings", spec=AppConfig)
@patch("src.narrator.gTTS")
@patch("src.narrator.playsound")
@patch("src.narrator.os.path.exists")
@patch("src.narrator.os.remove")
def test_narrate_price_success_override_lang_slow(
    mock_os_remove,
    mock_os_exists,
    mock_playsound,
    mock_gtts_constructor,
    mock_app_settings_instance,
    mock_narrator_app_settings_values,
):
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
        text=expected_text, lang=override_lang, slow=override_slow
    )
    mock_tts_instance.save.assert_called_once_with(expected_temp_file)
    mock_playsound.assert_called_once_with(expected_temp_file)
    # We no longer expect os.path.exists to be called
    mock_os_remove.assert_called_once_with(expected_temp_file)


@patch("src.narrator.app_settings", spec=AppConfig)
@patch("src.narrator.gTTS")
@patch("src.narrator.playsound")
@patch("src.narrator.os.path.exists")
@patch("src.narrator.os.remove")
def test_narrate_price_temp_file_does_not_exist_for_cleanup(
    mock_os_remove,
    mock_os_exists,
    mock_playsound,
    mock_gtts_constructor,
    mock_app_settings_instance,
    mock_narrator_app_settings_values,
):
    """Test cleanup logic when the temporary audio file doesn't exist."""
    for key, value in mock_narrator_app_settings_values.items():
        setattr(mock_app_settings_instance, key, value)

    mock_tts_instance = MagicMock()
    mock_gtts_constructor.return_value = mock_tts_instance
    mock_os_exists.return_value = False  # Simulate temp file does NOT exist

    narrate_price("TestCoin", 100, "USD")

    expected_temp_file = mock_narrator_app_settings_values["temp_audio_file"]
    # We no longer expect os.path.exists to be called
    mock_os_remove.assert_called_once_with(expected_temp_file)


@patch("src.narrator.app_settings", spec=AppConfig)
@patch("src.narrator.gTTS")
@patch("src.narrator.playsound")
@patch("src.narrator.os.path.exists")
@patch("src.narrator.os.remove")
def test_narrate_price_error_during_gtts_init(
    mock_os_remove,
    mock_os_exists,
    mock_playsound,
    mock_gtts_constructor,
    mock_app_settings_instance,
    mock_narrator_app_settings_values,
):
    """Test gTTS constructor error handling."""  # noqa: E501
    for key, value in mock_narrator_app_settings_values.items():  # noqa: E501
        setattr(mock_app_settings_instance, key, value)

    mock_gtts_constructor.side_effect = Exception("gTTS init failed")
    # os.path.exists might be called if the exception occurs after file creation, but for gTTS init error, it won't proceed to save/play.
    # Depending on exact structure, ensure os.path.exists is set if temp file interaction is possible before this point.
    # For now, assume error is before any file interaction for this specific test.
    mock_os_exists.return_value = False

    crypto_name = "TestCoin"
    price = 100
    currency = "USD"

    narrate_price(crypto_name, price, currency)  # noqa: E501

    mock_tts_instance = MagicMock()  # Need a ref if we were to check its calls
    mock_gtts_constructor.return_value = mock_tts_instance
    mock_tts_instance.save.assert_not_called()
    mock_playsound.assert_not_called()
    mock_os_remove.assert_not_called()  # File cleanup shouldn't happen if save didn't occur.


@patch("src.narrator.app_settings", spec=AppConfig)
@patch("src.narrator.gTTS")
@patch("src.narrator.playsound")
@patch("src.narrator.os.path.exists")
@patch("src.narrator.os.remove")
def test_narrate_price_error_during_save(
    mock_os_remove,
    mock_os_exists,
    mock_playsound,
    mock_gtts_constructor,
    mock_app_settings_instance,
    mock_narrator_app_settings_values,
):
    """Test tts.save() error handling."""  # noqa: E501
    for key, value in mock_narrator_app_settings_values.items():  # noqa: E501
        setattr(mock_app_settings_instance, key, value)

    mock_tts_instance = MagicMock()
    mock_tts_instance.save.side_effect = Exception("Save failed")  # noqa: E501
    mock_gtts_constructor.return_value = mock_tts_instance
    mock_os_exists.return_value = False  # Or True, depending on how robust you want the test for partial file creation

    crypto_name = "TestCoin"
    price = 100
    currency = "USD"

    narrate_price(crypto_name, price, currency)  # noqa: E501

    mock_playsound.assert_not_called()
    # When save fails, audio_file_created stays False, so os.remove shouldn't be called
    mock_os_remove.assert_not_called()


@patch("src.narrator.app_settings", spec=AppConfig)
@patch("src.narrator.gTTS")
@patch("src.narrator.playsound")
@patch("src.narrator.os.path.exists")
@patch("src.narrator.os.remove")
def test_narrate_price_error_during_playsound(
    mock_os_remove,
    mock_os_exists,
    mock_playsound,
    mock_gtts_constructor,
    mock_app_settings_instance,
    mock_narrator_app_settings_values,
):
    """Test error handling if playsound() raises Exception."""
    for key, value in mock_narrator_app_settings_values.items():
        setattr(mock_app_settings_instance, key, value)

    mock_tts_instance = MagicMock()
    mock_gtts_constructor.return_value = mock_tts_instance
    mock_playsound.side_effect = Exception("Playsound failed")
    mock_os_exists.return_value = True  # File was saved, now playing fails

    narrate_price("TestCoin", 100, "USD")

    expected_temp_file = mock_narrator_app_settings_values["temp_audio_file"]
    mock_tts_instance.save.assert_called_once_with(expected_temp_file)
    mock_playsound.assert_called_once_with(expected_temp_file)
    # Assert that cleanup is still attempted (keep_audio_on_error is False so we remove even on failed playback)
    mock_os_remove.assert_called_once_with(expected_temp_file)


@patch("src.narrator.app_settings", spec=AppConfig)
@patch("src.narrator.gTTS")
@patch("src.narrator.playsound")
@patch("src.narrator.os.path.exists")
@patch("src.narrator.os.remove")
def test_narrate_price_error_during_remove(
    mock_os_remove,
    mock_os_exists,
    mock_playsound,
    mock_gtts_constructor,
    mock_app_settings_instance,
    mock_narrator_app_settings_values,
):
    """Test error handling if os.remove() raises OSError during cleanup."""
    for key, value in mock_narrator_app_settings_values.items():
        setattr(mock_app_settings_instance, key, value)

    mock_tts_instance = MagicMock()
    mock_gtts_constructor.return_value = mock_tts_instance
    mock_os_exists.return_value = True
    mock_os_remove.side_effect = OSError(
        "Failed to delete file"
    )  # Simulate an OS error

    # We don't need to assert an exception from narrate_price itself, as it catches this.
    # We just check that the functions were called as expected up to the point of error.
    narrate_price("TestCoin", 100, "USD")

    expected_temp_file = mock_narrator_app_settings_values["temp_audio_file"]
    mock_tts_instance.save.assert_called_once_with(expected_temp_file)
    mock_playsound.assert_called_once_with(expected_temp_file)
    # We no longer expect os.path.exists to be called
    mock_os_remove.assert_called_once_with(expected_temp_file)


# Test for when app_settings is None (config file failed to load)
@patch("src.narrator.app_settings", None)  # Set app_settings to None in narrator.py
@patch("src.narrator.gTTS")
@patch("src.narrator.playsound")
@patch("src.narrator.os.path.exists")
@patch("src.narrator.os.remove")
def test_narrate_price_app_settings_none(
    mock_os_remove, mock_os_exists, mock_playsound, mock_gtts_constructor
):
    """Test behavior when app_settings is None (config failed to load)."""
    mock_tts_instance = MagicMock()
    mock_gtts_constructor.return_value = mock_tts_instance
    mock_os_exists.return_value = True

    crypto_name = "FallbackCoin"
    price = 50
    currency = "CAD"
    expected_text = f"The current price for {crypto_name} is {price:,.2f} {currency}."

    # These are the hardcoded defaults in narrator.py when app_settings is None
    expected_temp_file = "temp_price_narration.mp3"  # Define expected_temp_file
    default_lang = "en"
    default_slow = False

    narrate_price(crypto_name, price, currency)

    mock_gtts_constructor.assert_called_once_with(
        text=expected_text,
        lang=default_lang,
        slow=default_slow
    )
    mock_tts_instance.save.assert_called_once_with(expected_temp_file)
    mock_playsound.assert_called_once_with(expected_temp_file)
    # We no longer expect os.path.exists to be called
    mock_os_remove.assert_called_once_with(expected_temp_file)


@patch("platform.system")
@patch("subprocess.run")
def test_play_audio_fallback_windows(mock_subprocess_run, mock_platform_system):
    """Test the Windows-specific audio playback fallback."""
    mock_platform_system.return_value = "Windows"
    mock_subprocess_run.return_value = subprocess.CompletedProcess(args=[], returncode=0)
    
    audio_file = "test_audio.mp3"
    result = play_audio_fallback(audio_file)
    
    assert result is True
    mock_platform_system.assert_called_once()
    mock_subprocess_run.assert_called_once()
    # Verify the correct Windows PowerShell command is used
    args = mock_subprocess_run.call_args[0][0]
    assert args[0] == "powershell"
    assert "-c" in args
    assert "Media.SoundPlayer" in args[2]
    assert audio_file in args[2]
    assert mock_subprocess_run.call_args[1]['check'] is True


@patch("platform.system")
@patch("subprocess.run")
def test_play_audio_fallback_macos(mock_subprocess_run, mock_platform_system):
    """Test the macOS-specific audio playback fallback."""
    mock_platform_system.return_value = "Darwin"
    mock_subprocess_run.return_value = subprocess.CompletedProcess(args=[], returncode=0)
    
    audio_file = "test_audio.mp3"
    result = play_audio_fallback(audio_file)
    
    assert result is True
    mock_platform_system.assert_called_once()
    mock_subprocess_run.assert_called_once()
    # Verify the correct macOS afplay command is used
    args = mock_subprocess_run.call_args[0][0]
    assert args[0] == "afplay"
    assert args[1] == audio_file
    assert mock_subprocess_run.call_args[1]['check'] is True


@patch("platform.system")
@patch("subprocess.run")
def test_play_audio_fallback_linux(mock_subprocess_run, mock_platform_system):
    """Test the Linux-specific audio playback fallback with the first player succeeding."""
    mock_platform_system.return_value = "Linux"
    mock_subprocess_run.return_value = subprocess.CompletedProcess(args=[], returncode=0)
    
    audio_file = "test_audio.mp3"
    result = play_audio_fallback(audio_file)
    
    assert result is True
    mock_platform_system.assert_called_once()
    mock_subprocess_run.assert_called_once()
    # Verify that the first Linux player (paplay) is tried and succeeds
    args = mock_subprocess_run.call_args[0][0]
    assert args[0] == "paplay"
    assert args[1] == audio_file
    assert mock_subprocess_run.call_args[1]['check'] is True


@patch("platform.system")
@patch("subprocess.run")
def test_play_audio_fallback_linux_multiple_players(mock_subprocess_run, mock_platform_system):
    """Test the Linux-specific audio playback fallback with the first player failing."""
    mock_platform_system.return_value = "Linux"
    
    # First three players fail with FileNotFoundError, fourth one succeeds
    side_effects = [
        FileNotFoundError("No such file or directory: 'paplay'"),
        FileNotFoundError("No such file or directory: 'aplay'"),
        FileNotFoundError("No such file or directory: 'mpg123'"),
        subprocess.CompletedProcess(args=[], returncode=0)
    ]
    mock_subprocess_run.side_effect = side_effects
    
    audio_file = "test_audio.mp3"
    result = play_audio_fallback(audio_file)
    
    assert result is True
    mock_platform_system.assert_called_once()
    # Should call subprocess.run 4 times for each player
    assert mock_subprocess_run.call_count == 4
    
    # Check the last call was for mpg321
    last_call = mock_subprocess_run.call_args
    args = last_call[0][0]
    assert args[0] == "mpg321"
    assert args[1] == "-q"
    assert args[2] == audio_file
    assert last_call[1]['check'] is True


@patch("platform.system")
@patch("subprocess.run")
def test_play_audio_fallback_linux_all_players_fail(mock_subprocess_run, mock_platform_system):
    """Test the Linux-specific audio playback fallback when all players fail."""
    mock_platform_system.return_value = "Linux"
    
    # All players fail with FileNotFoundError
    mock_subprocess_run.side_effect = FileNotFoundError("No such file or directory")
    
    audio_file = "test_audio.mp3"
    result = play_audio_fallback(audio_file)
    
    assert result is False
    mock_platform_system.assert_called_once()
    # Should have tried all players (4 in total)
    assert mock_subprocess_run.call_count == 4


@patch("platform.system")
@patch("subprocess.run")
def test_play_audio_fallback_unsupported_platform(mock_subprocess_run, mock_platform_system):
    """Test audio playback fallback on an unsupported platform."""
    mock_platform_system.return_value = "Unknown"
    
    audio_file = "test_audio.mp3"
    result = play_audio_fallback(audio_file)
    
    assert result is False
    mock_platform_system.assert_called_once()
    # Should not attempt to run any commands on unsupported platforms
    mock_subprocess_run.assert_not_called()


@patch("platform.system")
@patch("subprocess.run")
def test_play_audio_fallback_exception(mock_subprocess_run, mock_platform_system):
    """Test graceful handling of unexpected exceptions during audio playback fallback."""
    mock_platform_system.return_value = "Windows"
    mock_subprocess_run.side_effect = subprocess.SubprocessError("Command failed")
    
    audio_file = "test_audio.mp3"
    result = play_audio_fallback(audio_file)
    
    assert result is False
    mock_platform_system.assert_called_once()
    mock_subprocess_run.assert_called_once()
