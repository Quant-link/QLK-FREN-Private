import configparser
import logging
import os
import json
from typing import Dict, Any, Optional, Set

logger = logging.getLogger(__name__)

CONFIG_FILE_PATH = "config.ini"


class AppConfig:
    """Loads and provides access to application configuration settings."""

    def __init__(self, config_file_path=CONFIG_FILE_PATH):
        self.config = configparser.ConfigParser()
        self.config_file_path = config_file_path

        if not os.path.exists(config_file_path):
            logger.critical(
                "Failed to initialize AppConfig due to missing config file. "
                "Application may not function correctly."
            )
            # In a real app, you might want to create a default config or raise a specific error
            raise FileNotFoundError(
                f"Configuration file '{config_file_path}' not found."
            )

        try:
            self.config.read(config_file_path)
            self._load_settings()
            logger.info(f"Successfully loaded configuration from '{config_file_path}'")
        except configparser.Error as e:
            logger.critical(
                f"Error parsing configuration file '{config_file_path}': {e}",
                exc_info=True,
            )
            raise

    def _load_settings(self):
        """Loads settings from the parsed config file into instance attributes."""
        # API Settings
        self.api_base_url = self.config.get(
            "API", "BASE_URL", fallback="https://api.coingecko.com/api/v3"
        )
        self.api_price_endpoint = self.config.get(
            "API", "PRICE_ENDPOINT", fallback="/simple/price"
        )
        self.api_request_timeout = self.config.getint(
            "API", "REQUEST_TIMEOUT", fallback=10
        )
        self.coingecko_api_url = f"{self.api_base_url}{self.api_price_endpoint}"

        # Retry Settings
        self.retry_max_retries = self.config.getint("Retry", "MAX_RETRIES", fallback=3)
        self.retry_initial_backoff = self.config.getfloat(
            "Retry", "INITIAL_BACKOFF_DELAY", fallback=1.0
        )
        self.retry_backoff_factor = self.config.getfloat(
            "Retry", "BACKOFF_FACTOR", fallback=2.0
        )
        retry_codes_str = self.config.get(
            "Retry", "RETRYABLE_STATUS_CODES", fallback="429,500,502,503,504"
        )
        self.retryable_status_codes = {
            int(code.strip()) for code in retry_codes_str.split(",") if code.strip()
        }

        # Default CLI argument values
        self.default_crypto_id = self.config.get(
            "Defaults", "CRYPTO_ID", fallback="bitcoin"
        )
        self.default_vs_currency = self.config.get(
            "Defaults", "VS_CURRENCY", fallback="usd"
        )

        # Narrator Settings
        self.temp_audio_file = self.config.get(
            "Logging", "TEMP_AUDIO_FILE", fallback="temp_price_narration.mp3"
        )
        self.narration_lang = self.config.get(
            "Narrator", "NARRATION_LANG", fallback="en"
        )
        self.narration_slow = self.config.getboolean(
            "Narrator", "NARRATION_SLOW", fallback=False
        )
        self.keep_audio_on_error = self.config.getboolean(
            "Narrator", "KEEP_AUDIO_ON_ERROR", fallback=False
        )
        
        # Cache Settings
        self.cache_enabled = self.config.getboolean(
            "Cache", "ENABLED", fallback=True
        )
        self.cache_expiration = self.config.getint(
            "Cache", "EXPIRATION", fallback=300
        )  # Default: 5 minutes
        self.cache_max_items = self.config.getint(
            "Cache", "MAX_ITEMS", fallback=100
        )

        # Logging Settings
        self.log_level = self.config.get(
            "Logging", "LOG_LEVEL", fallback="INFO"
        ).upper()
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the configuration to a dictionary for easy serialization/deserialization.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the configuration
        """
        result = {}
        for key, value in self.__dict__.items():
            if key != 'config' and key != 'config_file_path' and not key.startswith('_'):
                if isinstance(value, set):
                    result[key] = list(value)
                else:
                    result[key] = value
        return result
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AppConfig':
        """
        Create an AppConfig instance from a dictionary.
        
        Args:
            data (Dict[str, Any]): Dictionary with configuration values
            
        Returns:
            AppConfig: A new AppConfig instance with the values from the dictionary
        """
        instance = cls.__new__(cls)
        instance.config = None
        instance.config_file_path = None
        
        for key, value in data.items():
            if key == 'retryable_status_codes' and isinstance(value, list):
                setattr(instance, key, set(value))
            else:
                setattr(instance, key, value)
                
        return instance
        
    def save(self, config_file_path: Optional[str] = None) -> bool:
        """
        Save the current configuration to the config file.
        
        Args:
            config_file_path (Optional[str]): Path to save the config file to. 
                                             If None, uses the original path.
                                             
        Returns:
            bool: True if the save was successful, False otherwise
        """
        if not self.config:
            logger.error("Cannot save configuration: No config parser instance")
            return False
            
        save_path = config_file_path or self.config_file_path
        if not save_path:
            logger.error("Cannot save configuration: No config file path")
            return False
            
        try:
            # Update config with current values
            self._update_config_from_attributes()
            
            # Write to file
            with open(save_path, 'w') as config_file:
                self.config.write(config_file)
                
            logger.info(f"Configuration saved to {save_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save configuration to {save_path}: {e}", exc_info=True)
            return False
            
    def _update_config_from_attributes(self):
        """Update the ConfigParser instance with the current attribute values."""
        # Ensure all required sections exist
        for section in ["API", "Retry", "Defaults", "Narrator", "Logging", "Cache"]:
            if not self.config.has_section(section):
                self.config.add_section(section)
                
        # API Settings
        self.config.set("API", "BASE_URL", str(self.api_base_url))
        self.config.set("API", "PRICE_ENDPOINT", str(self.api_price_endpoint))
        self.config.set("API", "REQUEST_TIMEOUT", str(self.api_request_timeout))
        
        # Retry Settings
        self.config.set("Retry", "MAX_RETRIES", str(self.retry_max_retries))
        self.config.set("Retry", "INITIAL_BACKOFF_DELAY", str(self.retry_initial_backoff))
        self.config.set("Retry", "BACKOFF_FACTOR", str(self.retry_backoff_factor))
        self.config.set("Retry", "RETRYABLE_STATUS_CODES", 
                       ",".join(str(code) for code in self.retryable_status_codes))
        
        # Default CLI argument values
        self.config.set("Defaults", "CRYPTO_ID", str(self.default_crypto_id))
        self.config.set("Defaults", "VS_CURRENCY", str(self.default_vs_currency))
        
        # Narrator Settings
        self.config.set("Narrator", "NARRATION_LANG", str(self.narration_lang))
        self.config.set("Narrator", "NARRATION_SLOW", str(self.narration_slow))
        self.config.set("Narrator", "KEEP_AUDIO_ON_ERROR", str(self.keep_audio_on_error))
        
        # Cache Settings
        self.config.set("Cache", "ENABLED", str(self.cache_enabled))
        self.config.set("Cache", "EXPIRATION", str(self.cache_expiration))
        self.config.set("Cache", "MAX_ITEMS", str(self.cache_max_items))
        
        # Logging Settings
        self.config.set("Logging", "TEMP_AUDIO_FILE", str(self.temp_audio_file))
        self.config.set("Logging", "LOG_LEVEL", str(self.log_level))


# Create a single instance of the config to be imported by other modules
# This ensures the config is loaded only once.
try:
    app_settings = AppConfig()
except FileNotFoundError:
    # Fallback or error handling if config.ini is essential and not found
    logger.critical(
        "Failed to init AppConfig due to missing config file. App may not function."
    )
    # You could set app_settings to None or a default config object, or re-raise
    # For this application, we'll let it be None and dependent modules must handle it.
    app_settings = None
except configparser.Error:
    logger.critical(
        "Failed to init AppConfig due to parsing error. App may not function."
    )
    app_settings = None
