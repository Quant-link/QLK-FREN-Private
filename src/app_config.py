import configparser
import logging
import os

logger = logging.getLogger(__name__)

CONFIG_FILE_PATH = 'config.ini'

class AppConfig:
    """Loads and provides access to application configuration settings."""

    def __init__(self, config_file_path=CONFIG_FILE_PATH):
        self.config = configparser.ConfigParser()
        
        if not os.path.exists(config_file_path):
            logger.critical(f"Configuration file '{config_file_path}' not found. Application cannot start.")
            # In a real app, you might want to create a default config or raise a specific error
            raise FileNotFoundError(f"Configuration file '{config_file_path}' not found.")

        try:
            self.config.read(config_file_path)
            self._load_settings()
            logger.info(f"Successfully loaded configuration from '{config_file_path}'")
        except configparser.Error as e:
            logger.critical(f"Error parsing configuration file '{config_file_path}': {e}", exc_info=True)
            raise

    def _load_settings(self):
        """Loads settings from the parsed config file into instance attributes."""
        # API Settings
        self.api_base_url = self.config.get('API', 'BASE_URL', fallback='https://api.coingecko.com/api/v3')
        self.api_price_endpoint = self.config.get('API', 'PRICE_ENDPOINT', fallback='/simple/price')
        self.api_request_timeout = self.config.getint('API', 'REQUEST_TIMEOUT', fallback=10)
        self.coingecko_api_url = f"{self.api_base_url}{self.api_price_endpoint}"

        # Retry Settings
        self.retry_max_retries = self.config.getint('Retry', 'MAX_RETRIES', fallback=3)
        self.retry_initial_backoff = self.config.getfloat('Retry', 'INITIAL_BACKOFF_DELAY', fallback=1.0)
        self.retry_backoff_factor = self.config.getfloat('Retry', 'BACKOFF_FACTOR', fallback=2.0)
        retry_codes_str = self.config.get('Retry', 'RETRYABLE_STATUS_CODES', fallback='429,500,502,503,504')
        self.retryable_status_codes = {int(code.strip()) for code in retry_codes_str.split(',') if code.strip()}

        # Default CLI argument values
        self.default_crypto_id = self.config.get('Defaults', 'CRYPTO_ID', fallback='bitcoin')
        self.default_vs_currency = self.config.get('Defaults', 'VS_CURRENCY', fallback='usd')

        # Narrator Settings
        self.temp_audio_file = self.config.get('Logging', 'TEMP_AUDIO_FILE', fallback='temp_price_narration.mp3')
        
        # Logging Settings
        self.log_level = self.config.get('Logging', 'LOG_LEVEL', fallback='INFO').upper()

# Create a single instance of the config to be imported by other modules
# This ensures the config is loaded only once.
try:
    app_settings = AppConfig()
except FileNotFoundError:
    # Fallback or error handling if config.ini is essential and not found
    logger.critical("Failed to initialize AppConfig due to missing config file. Application may not function correctly.")
    # You could set app_settings to None or a default config object, or re-raise
    # For this application, we'll let it be None and dependent modules must handle it.
    app_settings = None 
except configparser.Error:
    logger.critical("Failed to initialize AppConfig due to parsing error. Application may not function correctly.")
    app_settings = None 