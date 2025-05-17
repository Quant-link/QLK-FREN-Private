import requests
import logging
import time # Added for sleep functionality in retries

# Configure logger for this module
logger = logging.getLogger(__name__)

# CoinGecko API endpoint for simple price fetching
COINGECKO_API_URL = "https://api.coingecko.com/api/v3/simple/price"

# Retry configuration constants
MAX_RETRIES = 3
INITIAL_BACKOFF_DELAY = 1  # seconds
BACKOFF_FACTOR = 2
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504} # HTTP status codes that warrant a retry

def get_crypto_price(crypto_id: str, vs_currency: str = "usd") -> tuple[str | None, float | None]:
    """
    Fetches the current price of a specified cryptocurrency from the CoinGecko API
    with a retry mechanism for transient errors.

    Args:
        crypto_id (str): The CoinGecko ID of the cryptocurrency (e.g., "bitcoin", "ethereum").
        vs_currency (str): The currency to compare against (e.g., "usd", "eur"). Defaults to "usd".

    Returns:
        tuple[str | None, float | None]: A tuple containing the capitalized cryptocurrency name
                                         and its price. Returns (None, None) if an error occurs
                                         or the price cannot be found after retries.
    """
    params = {
        "ids": crypto_id,
        "vs_currencies": vs_currency
    }
    logger.debug(f"Attempting to fetch price for {crypto_id} in {vs_currency} with params: {params}")
    
    current_delay = INITIAL_BACKOFF_DELAY
    last_exception = None

    for attempt in range(MAX_RETRIES):
        logger.info(f"API request attempt {attempt + 1} of {MAX_RETRIES} for {crypto_id}")
        try:
            response = requests.get(COINGECKO_API_URL, params=params, timeout=10)
            logger.debug(f"API Request URL: {response.url}")
            
            # Check for specific HTTP status codes that are retryable before calling raise_for_status()
            if response.status_code in RETRYABLE_STATUS_CODES:
                logger.warning(f"Received retryable HTTP status code {response.status_code}. Will retry if attempts remain.")
                # Store exception info for logging if all retries fail
                response.raise_for_status() # This will raise an HTTPError to be caught below
            
            response.raise_for_status()  # Raise an HTTPError for other bad responses (4xx client errors not in RETRYABLE_STATUS_CODES, or 5xx not caught above)
            
            data = response.json()
            logger.debug(f"API Response Data: {data}")

            if crypto_id in data and vs_currency in data[crypto_id]:
                price = data[crypto_id][vs_currency]
                logger.info(f"Successfully fetched price for {crypto_id.capitalize()}: {price} {vs_currency.upper()} on attempt {attempt + 1}")
                return crypto_id.capitalize(), float(price)
            else:
                logger.error(f"Price not found for '{crypto_id}' in '{vs_currency}' in API response. API Response: {data}")
                return None, None # Data received but not in expected format, no retry needed

        except requests.exceptions.HTTPError as http_err:
            last_exception = http_err
            logger.warning(f"HTTP Error on attempt {attempt + 1}: {http_err} - Status Code: {response.status_code}")
            if response.status_code not in RETRYABLE_STATUS_CODES:
                logger.error(f"Non-retryable HTTP error occurred: {response.status_code}. Aborting retries.")
                break # Break out of retry loop for non-retryable HTTP errors
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as conn_timeout_err:
            last_exception = conn_timeout_err
            logger.warning(f"Connection/Timeout Error on attempt {attempt + 1}: {conn_timeout_err}")
        except requests.exceptions.RequestException as req_err:
            last_exception = req_err
            logger.error(f"An Unexpected Request Error Occurred on attempt {attempt + 1}: {req_err}", exc_info=True)
            break # Break for other unexpected request errors
        except ValueError as val_err:  # Includes JSONDecodeError
            last_exception = val_err
            # This error means we got a response, but it wasn't valid JSON. Usually not retryable.
            logger.error(f"Error: Could not decode JSON response from API on attempt {attempt + 1}. Response Text: {response.text if 'response' in locals() else 'No response object'}", exc_info=True)
            return None, None # Not retryable
        
        # If it was a retryable error and not the last attempt, wait and retry
        if attempt < MAX_RETRIES - 1:
            logger.info(f"Waiting {current_delay} seconds before next retry...")
            time.sleep(current_delay)
            current_delay *= BACKOFF_FACTOR
        else:
            logger.error(f"All {MAX_RETRIES} retries failed for {crypto_id}.")
            if last_exception:
                 logger.error(f"Last encountered error: {last_exception}", exc_info=last_exception)
            return None, None

    # This part should ideally not be reached if logic is correct, but as a fallback:
    logger.error(f"Failed to fetch price for {crypto_id} after all retries. Last exception: {last_exception}", exc_info=last_exception)
    return None, None 