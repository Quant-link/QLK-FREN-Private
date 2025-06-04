import requests
import logging
import time
from typing import Dict, Any, Tuple, Optional, List
from src.app_config import app_settings  # Import the application settings
import json
import os
from datetime import datetime, timedelta

# Configure logger for this module
logger = logging.getLogger(__name__)

# Cache system to reduce API calls
class APICache:
    def __init__(self, cache_duration_minutes=5):
        self.cache = {}
        self.cache_duration = timedelta(minutes=cache_duration_minutes)
        self.cache_file = "api_cache.json"
        self.load_cache()
    
    def load_cache(self):
        """Load cache from file if exists"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    cache_data = json.load(f)
                    # Convert string timestamps back to datetime objects
                    for key, value in cache_data.items():
                        if 'timestamp' in value:
                            value['timestamp'] = datetime.fromisoformat(value['timestamp'])
                    self.cache = cache_data
        except Exception as e:
            logger.warning(f"Failed to load cache: {e}")
            self.cache = {}
    
    def save_cache(self):
        """Save cache to file"""
        try:
            cache_data = {}
            for key, value in self.cache.items():
                cache_copy = value.copy()
                if 'timestamp' in cache_copy:
                    cache_copy['timestamp'] = cache_copy['timestamp'].isoformat()
                cache_data[key] = cache_copy
            
            with open(self.cache_file, 'w') as f:
                json.dump(cache_data, f)
        except Exception as e:
            logger.warning(f"Failed to save cache: {e}")
    
    def get(self, key):
        """Get cached data if not expired"""
        if key in self.cache:
            cached_item = self.cache[key]
            if datetime.now() - cached_item['timestamp'] < self.cache_duration:
                logger.info(f"Using cached data for {key}")
                return cached_item['data']
            else:
                # Remove expired item
                del self.cache[key]
        return None
    
    def set(self, key, data):
        """Cache data with timestamp"""
        self.cache[key] = {
            'data': data,
            'timestamp': datetime.now()
        }
        self.save_cache()

# Global cache instance
api_cache = APICache(cache_duration_minutes=3)  # 3 minute cache

# Add a small delay between API calls to respect rate limits
def _api_rate_limit_delay():
    """Add a small delay to respect CoinGecko's rate limits"""
    time.sleep(1.5)  # Increased from 0.5 to 1.5 seconds

# Use settings from app_config if available, otherwise fall back to hardcoded (less ideal)
COINGECKO_API_URL = (
    app_settings.coingecko_api_url
    if app_settings
    else "https://api.coingecko.com/api/v3/simple/price"
)
MAX_RETRIES = app_settings.retry_max_retries if app_settings else 2  # Reduced retries
INITIAL_BACKOFF_DELAY = app_settings.retry_initial_backoff if app_settings else 5  # Increased from 3 to 5
BACKOFF_FACTOR = app_settings.retry_backoff_factor if app_settings else 4  # Increased from 3 to 4
RETRYABLE_STATUS_CODES = (
    app_settings.retryable_status_codes if app_settings else {429, 500, 502, 503, 504}
)
REQUEST_TIMEOUT = app_settings.api_request_timeout if app_settings else 20  # Increased from 15 to 20


def get_crypto_price(
    crypto_id: str, vs_currency: str = "usd"
) -> Tuple[Optional[str], Optional[float]]:
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
    # Check cache first
    cache_key = f"price_{crypto_id}_{vs_currency}"
    cached_result = api_cache.get(cache_key)
    if cached_result:
        return cached_result
    
    if not app_settings:
        logger.error(
            "App settings not loaded. Price fetching may use defaults & might not function."
        )
        # Potentially raise an error here or ensure fallback values are robust

    params = {"ids": crypto_id, "vs_currencies": vs_currency}
    logger.debug(
        f"Attempting to fetch price for {crypto_id} in {vs_currency} from {COINGECKO_API_URL}"
    )

    current_delay = INITIAL_BACKOFF_DELAY
    last_exception = None

    for attempt in range(MAX_RETRIES):
        logger.info(
            f"API request attempt {attempt + 1} of {MAX_RETRIES} for {crypto_id}"
        )
        try:
            # Add rate limiting delay before API call
            _api_rate_limit_delay()
            
            response = requests.get(
                COINGECKO_API_URL, params=params, timeout=REQUEST_TIMEOUT
            )
            logger.debug(f"API Request URL: {response.url}")

            if response.status_code in RETRYABLE_STATUS_CODES:
                logger.warning(
                    f"Retryable HTTP status {response.status_code}. Will retry if attempts remain."
                )
                response.raise_for_status()

            response.raise_for_status()

            data = response.json()
            logger.debug(f"API Response Data: {data}")

            if crypto_id in data and vs_currency in data[crypto_id]:
                price = data[crypto_id][vs_currency]
                result = (crypto_id.capitalize(), float(price))
                # Cache the result
                api_cache.set(cache_key, result)
                logger.info(
                    f"Fetched {crypto_id.capitalize()}: {price} {vs_currency.upper()} (attempt {attempt + 1})"
                )
                return result
            else:
                log_msg = f"Price not for '{crypto_id}' in '{vs_currency}'."
                logger.error(f"{log_msg} Response: {data}")
                return None, None

        except requests.exceptions.HTTPError as http_err:
            last_exception = http_err
            if hasattr(response, 'status_code') and response.status_code == 429:
                logger.warning(f"Rate limited (429) - waiting longer before retry...")
                time.sleep(current_delay * 2)  # Wait longer for rate limiting
            logger.warning(
                f"HTTP Error on attempt {attempt + 1}: {http_err} - Status Code: {response.status_code if 'response' in locals() else 'Unknown'}"
            )
            if 'response' in locals() and response.status_code not in RETRYABLE_STATUS_CODES:
                logger.error(
                    f"Non-retryable HTTP error occurred: {response.status_code}. Aborting retries."
                )
                break
        except (
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
        ) as conn_timeout_err:
            last_exception = conn_timeout_err
            logger.warning(
                f"Connection/Timeout Error on attempt {attempt + 1}: {conn_timeout_err}"
            )
        except requests.exceptions.RequestException as req_err:
            last_exception = req_err
            logger.error(
                f"An Unexpected Request Error Occurred on attempt {attempt + 1}: {req_err}",
                exc_info=True,
            )
            break
        except ValueError as val_err:
            last_exception = val_err
            logger.error(
                f"JSON decode error on attempt {attempt + 1}. "
                f"Resp: {response.text if 'response' in locals() else 'No resp'}",
                exc_info=True,
            )
            return None, None

        if attempt < MAX_RETRIES - 1:
            logger.info(f"Waiting {current_delay} seconds before next retry...")
            time.sleep(current_delay)
            current_delay *= BACKOFF_FACTOR
        else:
            logger.error(f"All {MAX_RETRIES} retries failed for {crypto_id}.")
            if last_exception:
                logger.error(
                    f"Last encountered error: {last_exception}", exc_info=last_exception
                )
            return None, None

    logger.error(
        f"Failed to fetch price for {crypto_id} after all retries. Last error: {last_exception}",
        exc_info=last_exception,
    )
    return None, None


def get_crypto_price_with_change(
    crypto_id: str, vs_currency: str = "usd", include_24h: bool = True, 
    include_7d: bool = False, include_30d: bool = False
) -> Dict[str, Any]:
    """
    Fetches the current price and price changes over different time periods for a 
    specified cryptocurrency from the CoinGecko API.

    Args:
        crypto_id (str): The CoinGecko ID of the cryptocurrency (e.g., "bitcoin", "ethereum").
        vs_currency (str): The currency to compare against (e.g., "usd", "eur"). Defaults to "usd".
        include_24h (bool): Whether to include 24-hour price change. Defaults to True.
        include_7d (bool): Whether to include 7-day price change. Defaults to False.
        include_30d (bool): Whether to include 30-day price change. Defaults to False.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - "name": Capitalized cryptocurrency name
            - "current_price": Current price as float
            - "price_change_24h": 24-hour price change percentage (if requested)
            - "price_change_7d": 7-day price change percentage (if requested)
            - "price_change_30d": 30-day price change percentage (if requested)
            - "currency": The currency of the prices (e.g., "usd", "eur")
            - "success": Boolean indicating if the request was successful
    """
    if not app_settings:
        logger.error(
            "App settings not loaded. Price fetching may use defaults & might not function."
        )

    # Prepare result dictionary with default values
    result = {
        "name": crypto_id.capitalize(),
        "current_price": None,
        "currency": vs_currency.upper(),
        "success": False,
    }
    
    # Add requested change percentages with default values
    if include_24h:
        result["price_change_24h"] = None
    if include_7d:
        result["price_change_7d"] = None
    if include_30d:
        result["price_change_30d"] = None
    
    # Build price parameters
    params = {"ids": crypto_id, "vs_currencies": vs_currency, "include_market_cap": "false", 
              "include_24hr_vol": "false", "include_24hr_change": str(include_24h).lower(),
              "include_last_updated_at": "false"}
    
    # Use a different endpoint for 7d and 30d changes
    if include_7d or include_30d:
        market_data_url = f"https://api.coingecko.com/api/v3/coins/{crypto_id}"
        need_market_data = True
    else:
        market_data_url = None
        need_market_data = False

    # Fetch current price and 24h change
    current_delay = INITIAL_BACKOFF_DELAY
    
    for attempt in range(MAX_RETRIES):
        logger.info(
            f"API request attempt {attempt + 1} of {MAX_RETRIES} for {crypto_id} with change data"
        )
        try:
            # Add rate limiting delay before API call
            _api_rate_limit_delay()
            
            # Fetch price data
            response = requests.get(
                COINGECKO_API_URL, params=params, timeout=REQUEST_TIMEOUT
            )
            logger.debug(f"API Request URL: {response.url}")
            
            if response.status_code in RETRYABLE_STATUS_CODES:
                logger.warning(
                    f"Retryable HTTP status {response.status_code}. Will retry if attempts remain."
                )
                response.raise_for_status()
                
            response.raise_for_status()
            data = response.json()
            
            if crypto_id in data and vs_currency in data[crypto_id]:
                result["current_price"] = float(data[crypto_id][vs_currency])
                
                # Get 24h change if available in the response
                if include_24h and f"{vs_currency}_24h_change" in data[crypto_id]:
                    result["price_change_24h"] = float(data[crypto_id][f"{vs_currency}_24h_change"])
                
                # If we need 7d or 30d data, make a second request to the market data endpoint
                if need_market_data:
                    market_response = requests.get(
                        market_data_url, 
                        params={"localization": "false", "tickers": "false", "market_data": "true", 
                                "community_data": "false", "developer_data": "false", "sparkline": "false"},
                        timeout=REQUEST_TIMEOUT
                    )
                    market_response.raise_for_status()
                    market_data = market_response.json()
                    
                    # Extract market data if available
                    if "market_data" in market_data:
                        price_change = market_data["market_data"]["price_change_percentage"]
                        
                        if include_7d and "7d" in price_change:
                            result["price_change_7d"] = float(price_change["7d"])
                            
                        if include_30d and "30d" in price_change:
                            result["price_change_30d"] = float(price_change["30d"])
                
                result["success"] = True
                logger.info(f"Successfully fetched price and change data for {crypto_id}")
                return result
            else:
                log_msg = f"Price data not found for '{crypto_id}' in '{vs_currency}'."
                logger.error(f"{log_msg} Response: {data}")
                return result
                
        except requests.exceptions.HTTPError as http_err:
            logger.warning(
                f"HTTP Error on attempt {attempt + 1}: {http_err} - Status Code: {response.status_code if 'response' in locals() else 'Unknown'}"
            )
            if 'response' in locals() and response.status_code not in RETRYABLE_STATUS_CODES:
                logger.error(
                    f"Non-retryable HTTP error occurred: {response.status_code}. Aborting retries."
                )
                break
        except (
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
        ) as conn_timeout_err:
            logger.warning(
                f"Connection/Timeout Error on attempt {attempt + 1}: {conn_timeout_err}"
            )
        except requests.exceptions.RequestException as req_err:
            logger.error(
                f"An Unexpected Request Error Occurred on attempt {attempt + 1}: {req_err}",
                exc_info=True,
            )
            break
        except ValueError as val_err:
            logger.error(
                f"JSON decode error on attempt {attempt + 1}. "
                f"Resp: {response.text if 'response' in locals() else 'No resp'}",
                exc_info=True,
            )
            return result

        if attempt < MAX_RETRIES - 1:
            logger.info(f"Waiting {current_delay} seconds before next retry...")
            time.sleep(current_delay)
            current_delay *= BACKOFF_FACTOR
        else:
            logger.error(f"All {MAX_RETRIES} retries failed for {crypto_id}.")
            
    logger.error(f"Failed to fetch price change data for {crypto_id} after all retries.")
    return result


def get_multiple_crypto_prices(
    crypto_ids: List[str], vs_currency: str = "usd", include_change: bool = False
) -> Dict[str, Dict[str, Any]]:
    """
    Fetch prices for multiple cryptocurrencies in a single API call to minimize rate limiting issues.
    
    Args:
        crypto_ids (List[str]): List of CoinGecko IDs for cryptocurrencies
        vs_currency (str): Currency to get prices in (e.g., "usd", "eur")
        include_change (bool): Whether to include 24h price change
        
    Returns:
        Dict[str, Dict[str, Any]]: Dictionary of results keyed by crypto ID
    """
    if not crypto_ids:
        logger.warning("No cryptocurrency IDs provided to fetch")
        return {}
    
    # Check cache first
    cache_key = f"multiple_prices_{','.join(sorted(crypto_ids))}_{vs_currency}_{include_change}"
    cached_result = api_cache.get(cache_key)
    if cached_result:
        return cached_result
        
    # Join crypto IDs with commas for the API
    ids_param = ",".join(crypto_ids)
    
    params = {
        "ids": ids_param, 
        "vs_currencies": vs_currency,
        "include_market_cap": "false",
        "include_24hr_vol": "false", 
        "include_24hr_change": str(include_change).lower(),
        "include_last_updated_at": "false"
    }
    
    logger.debug(f"Fetching prices for multiple cryptocurrencies: {ids_param}")
    
    results = {}
    current_delay = INITIAL_BACKOFF_DELAY
    
    for attempt in range(MAX_RETRIES):
        try:
            # Add rate limiting delay before API call
            _api_rate_limit_delay()
            
            response = requests.get(
                COINGECKO_API_URL, params=params, timeout=REQUEST_TIMEOUT
            )
            
            if response.status_code in RETRYABLE_STATUS_CODES:
                if response.status_code == 429:
                    logger.warning(f"Rate limited (429) - waiting longer before retry...")
                    time.sleep(current_delay * 2)  # Wait longer for rate limiting
                logger.warning(
                    f"Retryable HTTP status {response.status_code}. Will retry if attempts remain."
                )
                response.raise_for_status()
                
            response.raise_for_status()
            data = response.json()
            
            # Process each cryptocurrency in the response
            for crypto_id in crypto_ids:
                result = {
                    "name": crypto_id.capitalize(),
                    "current_price": None,
                    "currency": vs_currency.upper(),
                    "success": False
                }
                
                if include_change:
                    result["price_change_24h"] = None
                
                if crypto_id in data and vs_currency in data[crypto_id]:
                    result["current_price"] = float(data[crypto_id][vs_currency])
                    
                    if include_change and f"{vs_currency}_24h_change" in data[crypto_id]:
                        result["price_change_24h"] = float(data[crypto_id][f"{vs_currency}_24h_change"])
                        
                    result["success"] = True
                
                results[crypto_id] = result
            
            # Cache the result
            api_cache.set(cache_key, results)
            logger.info(f"Successfully fetched prices for {len(results)} cryptocurrencies")
            return results
            
        except requests.exceptions.HTTPError as http_err:
            logger.warning(
                f"HTTP Error on attempt {attempt + 1}: {http_err} - Status Code: {response.status_code if 'response' in locals() else 'Unknown'}"
            )
            if 'response' in locals() and response.status_code not in RETRYABLE_STATUS_CODES:
                break
        except (
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
        ) as conn_timeout_err:
            logger.warning(
                f"Connection/Timeout Error on attempt {attempt + 1}: {conn_timeout_err}"
            )
        except requests.exceptions.RequestException as req_err:
            logger.error(
                f"An Unexpected Request Error Occurred on attempt {attempt + 1}: {req_err}",
                exc_info=True,
            )
            break
        except ValueError as val_err:
            logger.error(
                f"JSON decode error on attempt {attempt + 1}. "
                f"Resp: {response.text if 'response' in locals() else 'No resp'}",
                exc_info=True,
            )
            return results

        if attempt < MAX_RETRIES - 1:
            logger.info(f"Waiting {current_delay} seconds before next retry...")
            time.sleep(current_delay)
            current_delay *= BACKOFF_FACTOR
        else:
            logger.error(f"All {MAX_RETRIES} retries failed for multiple crypto fetch.")
    
    # Return whatever results we have, which might be empty or partial
    return results


def get_crypto_historical_data(
    crypto_id: str, vs_currency: str = "usd", days: int = 7
) -> Dict[str, Any]:
    """
    Fetches historical price data for a specified cryptocurrency from the CoinGecko API.

    Args:
        crypto_id (str): The CoinGecko ID of the cryptocurrency (e.g., "bitcoin", "ethereum").
        vs_currency (str): The currency to compare against (e.g., "usd", "eur"). Defaults to "usd".
        days (int): Number of days to fetch data for (1, 7, 14, 30, 90, 180, 365). Defaults to 7.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - "name": Capitalized cryptocurrency name
            - "data": List of [timestamp, price] pairs
            - "currency": The currency of the prices
            - "days": Number of days of data
            - "success": Boolean indicating if the request was successful
    """
    # Check cache first
    cache_key = f"historical_{crypto_id}_{vs_currency}_{days}"
    cached_result = api_cache.get(cache_key)
    if cached_result:
        return cached_result
        
    result = {
        "name": crypto_id.capitalize(),
        "data": [],
        "currency": vs_currency.upper(),
        "days": days,
        "success": False,
    }

    # CoinGecko historical data endpoint
    url = f"https://api.coingecko.com/api/v3/coins/{crypto_id}/market_chart"
    params = {
        "vs_currency": vs_currency,
        "days": days,
        "interval": "hourly" if days <= 1 else "daily"
    }

    current_delay = INITIAL_BACKOFF_DELAY
    last_exception = None

    for attempt in range(MAX_RETRIES):
        logger.info(
            f"Historical data request attempt {attempt + 1} of {MAX_RETRIES} for {crypto_id} ({days} days)"
        )
        try:
            # Add rate limiting delay before API call
            _api_rate_limit_delay()
            
            response = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
            logger.debug(f"API Request URL: {response.url}")

            if response.status_code in RETRYABLE_STATUS_CODES:
                if response.status_code == 429:
                    logger.warning(f"Rate limited (429) - waiting much longer before retry...")
                    time.sleep(current_delay * 3)  # Wait even longer for historical data rate limiting
                logger.warning(
                    f"Retryable HTTP status {response.status_code}. Will retry if attempts remain."
                )
                response.raise_for_status()

            response.raise_for_status()
            data = response.json()

            if "prices" in data:
                # CoinGecko returns prices as [[timestamp, price], [timestamp, price], ...]
                prices = data["prices"]
                result["data"] = prices
                result["success"] = True
                
                # Cache the result for longer since historical data doesn't change as often
                api_cache.set(cache_key, result)
                
                logger.info(
                    f"Fetched {len(prices)} historical data points for {crypto_id} "
                    f"({days} days in {vs_currency.upper()})"
                )
                return result
            else:
                logger.error(f"No price data found for {crypto_id}. Response: {data}")
                return result

        except requests.exceptions.HTTPError as http_err:
            last_exception = http_err
            logger.warning(
                f"HTTP Error on attempt {attempt + 1}: {http_err} - Status Code: {response.status_code if 'response' in locals() else 'Unknown'}"
            )
            if 'response' in locals() and response.status_code not in RETRYABLE_STATUS_CODES:
                logger.error(
                    f"Non-retryable HTTP error occurred: {response.status_code}. Aborting retries."
                )
                break
        except (
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
        ) as conn_timeout_err:
            last_exception = conn_timeout_err
            logger.warning(
                f"Connection/Timeout Error on attempt {attempt + 1}: {conn_timeout_err}"
            )
        except requests.exceptions.RequestException as req_err:
            last_exception = req_err
            logger.error(
                f"Unexpected Request Error on attempt {attempt + 1}: {req_err}",
                exc_info=True,
            )
            break
        except ValueError as val_err:
            last_exception = val_err
            logger.error(
                f"JSON decode error on attempt {attempt + 1}. "
                f"Response: {response.text if 'response' in locals() else 'No response'}",
                exc_info=True,
            )
            return result

        if attempt < MAX_RETRIES - 1:
            logger.info(f"Waiting {current_delay} seconds before next retry...")
            time.sleep(current_delay)
            current_delay *= BACKOFF_FACTOR
        else:
            logger.error(f"All {MAX_RETRIES} retries failed for {crypto_id} historical data.")
            if last_exception:
                logger.error(
                    f"Last encountered error: {last_exception}", exc_info=last_exception
                )

    logger.error(
        f"Failed to fetch historical data for {crypto_id} after all retries. Last error: {last_exception}",
        exc_info=last_exception,
    )
    return result
 