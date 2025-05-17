import requests
import logging
import time
from src.app_config import app_settings # Import the application settings

# Configure logger for this module
logger = logging.getLogger(__name__)

# Use settings from app_config if available, otherwise fall back to hardcoded (less ideal)
COINGECKO_API_URL = app_settings.coingecko_api_url if app_settings else "https://api.coingecko.com/api/v3/simple/price"
MAX_RETRIES = app_settings.retry_max_retries if app_settings else 3
INITIAL_BACKOFF_DELAY = app_settings.retry_initial_backoff if app_settings else 1
BACKOFF_FACTOR = app_settings.retry_backoff_factor if app_settings else 2
RETRYABLE_STATUS_CODES = app_settings.retryable_status_codes if app_settings else {429, 500, 502, 503, 504}
REQUEST_TIMEOUT = app_settings.api_request_timeout if app_settings else 10

def get_crypto_price(crypto_id: str, vs_currency: str = "usd") -> tuple[str | None, float | None]:
    """
    Fetches the current price of a specified cryptocurrency from the CoinGecko API
    with a retry mechanism for transient errors, using configured settings.

    Args:
        crypto_id (str): The CoinGecko ID of the cryptocurrency (e.g., "bitcoin", "ethereum").
        vs_currency (str): The currency to compare against (e.g., "usd", "eur"). Defaults to "usd".

    Returns:
        tuple[str | None, float | None]: A tuple containing the capitalized cryptocurrency name
                                         and its price. Returns (None, None) if an error occurs
                                         or the price cannot be found after retries.
    """
    if not app_settings:
        logger.error("Application settings not loaded. Price fetching may use default or hardcoded values and might not function as expected.")
        # Potentially raise an error here or ensure fallback values are robust

    params = {
        "ids": crypto_id,
        "vs_currencies": vs_currency
    }
    logger.debug(f"Attempting to fetch price for {crypto_id} in {vs_currency} with params: {params} from {COINGECKO_API_URL}")
    
    current_delay = INITIAL_BACKOFF_DELAY
    last_exception = None

    for attempt in range(MAX_RETRIES):
        logger.info(f"API request attempt {attempt + 1} of {MAX_RETRIES} for {crypto_id}")
        try:
            response = requests.get(COINGECKO_API_URL, params=params, timeout=REQUEST_TIMEOUT)
            logger.debug(f"API Request URL: {response.url}")
            
            if response.status_code in RETRYABLE_STATUS_CODES:
                logger.warning(f"Received retryable HTTP status code {response.status_code}. Will retry if attempts remain.")
                response.raise_for_status()
            
            response.raise_for_status()
            
            data = response.json()
            logger.debug(f"API Response Data: {data}")

            if crypto_id in data and vs_currency in data[crypto_id]:
                price = data[crypto_id][vs_currency]
                logger.info(f"Successfully fetched price for {crypto_id.capitalize()}: {price} {vs_currency.upper()} on attempt {attempt + 1}")
                return crypto_id.capitalize(), float(price)
            else:
                logger.error(f"Price not found for '{crypto_id}' in '{vs_currency}' in API response. API Response: {data}")
                return None, None

        except requests.exceptions.HTTPError as http_err:
            last_exception = http_err
            logger.warning(f"HTTP Error on attempt {attempt + 1}: {http_err} - Status Code: {response.status_code}")
            if response.status_code not in RETRYABLE_STATUS_CODES:
                logger.error(f"Non-retryable HTTP error occurred: {response.status_code}. Aborting retries.")
                break
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as conn_timeout_err:
            last_exception = conn_timeout_err
            logger.warning(f"Connection/Timeout Error on attempt {attempt + 1}: {conn_timeout_err}")
        except requests.exceptions.RequestException as req_err:
            last_exception = req_err
            logger.error(f"An Unexpected Request Error Occurred on attempt {attempt + 1}: {req_err}", exc_info=True)
            break
        except ValueError as val_err:
            last_exception = val_err
            logger.error(f"Error: Could not decode JSON response from API on attempt {attempt + 1}. Response Text: {response.text if 'response' in locals() else 'No response object'}", exc_info=True)
            return None, None
        
        if attempt < MAX_RETRIES - 1:
            logger.info(f"Waiting {current_delay} seconds before next retry...")
            time.sleep(current_delay)
            current_delay *= BACKOFF_FACTOR
        else:
            logger.error(f"All {MAX_RETRIES} retries failed for {crypto_id}.")
            if last_exception:
                 logger.error(f"Last encountered error: {last_exception}", exc_info=last_exception)
            return None, None

    logger.error(f"Failed to fetch price for {crypto_id} after all retries. Last exception: {last_exception}", exc_info=last_exception)
    return None, None 