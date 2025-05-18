import requests
import logging
import time
from typing import Dict, Any, Tuple, Optional, List
from src.app_config import app_settings  # Import the application settings

# Configure logger for this module
logger = logging.getLogger(__name__)

# Use settings from app_config if available, otherwise fall back to hardcoded (less ideal)
COINGECKO_API_URL = (
    app_settings.coingecko_api_url
    if app_settings
    else "https://api.coingecko.com/api/v3/simple/price"
)
MAX_RETRIES = app_settings.retry_max_retries if app_settings else 3
INITIAL_BACKOFF_DELAY = app_settings.retry_initial_backoff if app_settings else 1
BACKOFF_FACTOR = app_settings.retry_backoff_factor if app_settings else 2
RETRYABLE_STATUS_CODES = (
    app_settings.retryable_status_codes if app_settings else {429, 500, 502, 503, 504}
)
REQUEST_TIMEOUT = app_settings.api_request_timeout if app_settings else 10


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
                logger.info(
                    f"Fetched {crypto_id.capitalize()}: {price} {vs_currency.upper()} (attempt {attempt + 1})"
                )
                return crypto_id.capitalize(), float(price)
            else:
                log_msg = f"Price not for '{crypto_id}' in '{vs_currency}'."
                logger.error(f"{log_msg} Response: {data}")
                return None, None

        except requests.exceptions.HTTPError as http_err:
            last_exception = http_err
            logger.warning(
                f"HTTP Error on attempt {attempt + 1}: {http_err} - Status Code: {response.status_code}"
            )
            if response.status_code not in RETRYABLE_STATUS_CODES:
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
            response = requests.get(
                COINGECKO_API_URL, params=params, timeout=REQUEST_TIMEOUT
            )
            
            if response.status_code in RETRYABLE_STATUS_CODES:
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
