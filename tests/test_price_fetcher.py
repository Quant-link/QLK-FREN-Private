import pytest
from unittest.mock import (
    patch,
    MagicMock,
)  # pytest-mock provides the mocker fixture, but unittest.mock is often used directly too
import requests
from src.price_fetcher import get_crypto_price, get_crypto_price_with_change, get_multiple_crypto_prices
from src.app_config import AppConfig  # To allow testing with mocked app_settings

# Sample successful API response
SUCCESSFUL_RESPONSE_DATA = {"bitcoin": {"usd": 60000.75}}

# Sample successful response with 24h change
SUCCESSFUL_RESPONSE_WITH_CHANGE = {
    "bitcoin": {
        "usd": 60000.75,
        "usd_24h_change": 5.25
    }
}

# Sample successful multiple crypto response
SUCCESSFUL_MULTIPLE_RESPONSE = {
    "bitcoin": {
        "usd": 60000.75,
        "usd_24h_change": 5.25
    },
    "ethereum": {
        "usd": 3000.50,
        "usd_24h_change": -2.10
    }
}

# Sample market data response (used for 7d and 30d changes)
SUCCESSFUL_MARKET_DATA_RESPONSE = {
    "id": "bitcoin",
    "name": "Bitcoin",
    "market_data": {
        "current_price": {
            "usd": 60000.75
        },
        "price_change_percentage": {
            "24h": 5.25,
            "7d": 10.5,
            "30d": 15.75
        }
    }
}

# Sample error response (e.g., currency not found for id)
ERROR_RESPONSE_DATA_NO_CURRENCY = {"bitcoin": {}}


@pytest.fixture
def mock_app_settings_values():
    """Fixture to provide a dictionary of mock AppConfig values."""
    return {
        "coingecko_api_url": "https://api.coingecko.com/api/v3/simple/price",
        "retry_max_retries": 3,
        "retry_initial_backoff": 1.0,  # Updated to match the value used in price_fetcher.py (1.0 instead of 0.01)
        "retry_backoff_factor": 2,
        "retryable_status_codes": {429, 500, 502, 503, 504},
        "api_request_timeout": 10,  # Updated to match the value used in price_fetcher.py (10 instead of 5)
    }


# The target for patching app_settings is where it's imported and used.
@patch(
    "src.price_fetcher.app_settings", spec=AppConfig
)  # Patch app_settings in price_fetcher.py
@patch("requests.get")
def test_get_crypto_price_success(
    mock_requests_get, mock_app_settings_instance, mock_app_settings_values
):
    """Test successful price fetching."""
    # Configure the attributes of the patched app_settings instance
    for key, value in mock_app_settings_values.items():
        setattr(mock_app_settings_instance, key, value)

    mock_response = MagicMock()
    mock_response.json.return_value = SUCCESSFUL_RESPONSE_DATA
    mock_response.status_code = 200
    mock_response.url = "http://testurl.com"
    mock_requests_get.return_value = mock_response

    name, price = get_crypto_price("bitcoin", "usd")

    assert name == "Bitcoin"
    assert price == 60000.75
    mock_requests_get.assert_called_once()
    # Check if the correct URL and timeout were used from mocked settings
    expected_url = mock_app_settings_values["coingecko_api_url"]
    expected_params = {"ids": "bitcoin", "vs_currencies": "usd"}
    expected_timeout = mock_app_settings_values["api_request_timeout"]
    mock_requests_get.assert_called_with(
        expected_url,
        params=expected_params,
        timeout=expected_timeout,
    )  # noqa: E501


@patch("src.price_fetcher.app_settings", spec=AppConfig)
@patch("requests.get")
def test_get_crypto_price_id_not_found_in_response(
    mock_requests_get, mock_app_settings_instance, mock_app_settings_values
):
    """Test when crypto ID is not in the API response."""
    mock_app_settings_instance.coingecko_api_url = mock_app_settings_values[
        "coingecko_api_url"
    ]
    mock_app_settings_instance.retry_max_retries = 1  # No retry needed here
    mock_app_settings_instance.api_request_timeout = mock_app_settings_values[
        "api_request_timeout"
    ]
    # Ensure other retry params are set if they were accessed by the code under test, even if not used for this path
    mock_app_settings_instance.retry_initial_backoff = mock_app_settings_values[
        "retry_initial_backoff"
    ]
    mock_app_settings_instance.retry_backoff_factor = mock_app_settings_values[
        "retry_backoff_factor"
    ]
    mock_app_settings_instance.retryable_status_codes = mock_app_settings_values[
        "retryable_status_codes"
    ]

    mock_response = MagicMock()
    mock_response.json.return_value = {"ethereum": {"usd": 2000}}
    mock_response.status_code = 200
    mock_requests_get.return_value = mock_response

    name, price = get_crypto_price("bitcoin", "usd")
    assert name is None
    assert price is None


@patch("src.price_fetcher.app_settings", spec=AppConfig)
@patch("requests.get")
def test_get_crypto_price_currency_not_found_in_response(
    mock_requests_get, mock_app_settings_instance, mock_app_settings_values
):
    """Test when currency is not in the API response for the crypto ID."""
    mock_app_settings_instance.coingecko_api_url = mock_app_settings_values[
        "coingecko_api_url"
    ]
    mock_app_settings_instance.retry_max_retries = 1
    mock_app_settings_instance.api_request_timeout = mock_app_settings_values[
        "api_request_timeout"
    ]
    mock_app_settings_instance.retry_initial_backoff = mock_app_settings_values[
        "retry_initial_backoff"
    ]
    mock_app_settings_instance.retry_backoff_factor = mock_app_settings_values[
        "retry_backoff_factor"
    ]
    mock_app_settings_instance.retryable_status_codes = mock_app_settings_values[
        "retryable_status_codes"
    ]

    mock_response = MagicMock()
    mock_response.json.return_value = ERROR_RESPONSE_DATA_NO_CURRENCY
    mock_response.status_code = 200
    mock_requests_get.return_value = mock_response

    name, price = get_crypto_price("bitcoin", "usd")
    assert name is None
    assert price is None


@patch("src.price_fetcher.time.sleep")
@patch("src.price_fetcher.app_settings", spec=AppConfig)
@patch("requests.get")
def test_get_crypto_price_http_error_retry_and_fail(
    mock_requests_get,
    mock_app_settings_instance,
    mock_time_sleep,
    mock_app_settings_values,
):
    """Test HTTP 500 error, retries, and eventual failure."""
    for key, value in mock_app_settings_values.items():
        setattr(mock_app_settings_instance, key, value)

    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
        "Server Error"
    )
    mock_response.text = "Server Error Text"
    mock_requests_get.return_value = mock_response

    name, price = get_crypto_price("bitcoin", "usd")

    assert name is None
    assert price is None
    assert mock_requests_get.call_count == mock_app_settings_values["retry_max_retries"]
    assert (
        mock_time_sleep.call_count == mock_app_settings_values["retry_max_retries"] - 1
    )


@patch("src.price_fetcher.time.sleep")
@patch("src.price_fetcher.app_settings", spec=AppConfig)
@patch("requests.get")
def test_get_crypto_price_http_error_non_retryable(
    mock_requests_get,
    mock_app_settings_instance,
    mock_time_sleep,
    mock_app_settings_values,
):
    """Test a non-retryable HTTP error (e.g., 404)."""
    mock_app_settings_instance.coingecko_api_url = mock_app_settings_values[
        "coingecko_api_url"
    ]
    mock_app_settings_instance.retry_max_retries = mock_app_settings_values[
        "retry_max_retries"
    ]
    mock_app_settings_instance.retryable_status_codes = mock_app_settings_values[
        "retryable_status_codes"
    ]
    mock_app_settings_instance.api_request_timeout = mock_app_settings_values[
        "api_request_timeout"
    ]
    mock_app_settings_instance.retry_initial_backoff = mock_app_settings_values[
        "retry_initial_backoff"
    ]
    mock_app_settings_instance.retry_backoff_factor = mock_app_settings_values[
        "retry_backoff_factor"
    ]

    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
        "Not Found"
    )
    mock_response.text = "Not Found Text"
    mock_requests_get.return_value = mock_response

    name, price = get_crypto_price("bitcoin", "usd")

    assert name is None
    assert price is None
    assert mock_requests_get.call_count == 1
    assert mock_time_sleep.call_count == 0


@patch(
    "src.price_fetcher.time.sleep"
)  # Added sleep mock as it might be called if retries > 1
@patch("src.price_fetcher.app_settings", spec=AppConfig)
@patch("requests.get")
def test_get_crypto_price_connection_error_retry_and_fail(
    mock_requests_get,
    mock_app_settings_instance,
    mock_time_sleep,
    mock_app_settings_values,
):
    """Test handling of ConnectionError with retries."""
    for key, value in mock_app_settings_values.items():
        setattr(mock_app_settings_instance, key, value)

    mock_requests_get.side_effect = requests.exceptions.ConnectionError(
        "Connection failed"
    )

    name, price = get_crypto_price("bitcoin", "usd")

    assert name is None
    assert price is None
    assert mock_requests_get.call_count == mock_app_settings_values["retry_max_retries"]
    assert (
        mock_time_sleep.call_count == mock_app_settings_values["retry_max_retries"] - 1
    )


@patch("src.price_fetcher.app_settings", spec=AppConfig)
@patch("requests.get")
def test_get_crypto_price_invalid_json(
    mock_requests_get, mock_app_settings_instance, mock_app_settings_values
):
    """Test handling of invalid JSON response."""
    mock_app_settings_instance.coingecko_api_url = mock_app_settings_values[
        "coingecko_api_url"
    ]
    mock_app_settings_instance.retry_max_retries = 1
    mock_app_settings_instance.api_request_timeout = mock_app_settings_values[
        "api_request_timeout"
    ]
    mock_app_settings_instance.retry_initial_backoff = mock_app_settings_values[
        "retry_initial_backoff"
    ]
    mock_app_settings_instance.retry_backoff_factor = mock_app_settings_values[
        "retry_backoff_factor"
    ]
    mock_app_settings_instance.retryable_status_codes = mock_app_settings_values[
        "retryable_status_codes"
    ]

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.side_effect = ValueError("Decoding JSON has failed")
    mock_response.text = "Invalid JSON string"
    mock_requests_get.return_value = mock_response

    name, price = get_crypto_price("bitcoin", "usd")

    assert name is None
    assert price is None
    assert mock_requests_get.call_count == 1


@patch("src.price_fetcher.time.sleep")
@patch("src.price_fetcher.app_settings", spec=AppConfig)
@patch("requests.get")
def test_get_crypto_price_retry_then_success(
    mock_requests_get,
    mock_app_settings_instance,
    mock_time_sleep,
    mock_app_settings_values,
):
    """Test scenario where API fails first then succeeds on retry."""
    for key, value in mock_app_settings_values.items():
        setattr(mock_app_settings_instance, key, value)

    mock_response_fail = MagicMock()
    mock_response_fail.status_code = 500
    mock_response_fail.raise_for_status.side_effect = requests.exceptions.HTTPError(
        "Server Error"
    )
    mock_response_fail.text = "Server Error Text"

    mock_response_success = MagicMock()
    mock_response_success.status_code = 200
    mock_response_success.json.return_value = SUCCESSFUL_RESPONSE_DATA
    mock_response_success.url = "http://testurl.com/success"

    mock_requests_get.side_effect = [mock_response_fail, mock_response_success]

    name, price = get_crypto_price("bitcoin", "usd")

    assert name == "Bitcoin"
    assert price == 60000.75
    assert mock_requests_get.call_count == 2
    assert mock_time_sleep.call_count == 1
    # Check that sleep was called with the correct initial backoff
    mock_time_sleep.assert_called_once_with(
        mock_app_settings_values["retry_initial_backoff"]
    )


# Test for when app_settings is None (config file failed to load)
@patch(
    "src.price_fetcher.app_settings", None
)  # Set app_settings to None in the price_fetcher module
@patch("requests.get")
def test_get_crypto_price_app_settings_none(mock_requests_get):
    """Test behavior when app_settings is None (config failed to load)."""
    # This test relies on the hardcoded fallbacks in price_fetcher.py
    # when app_settings is None.

    mock_response = MagicMock()
    mock_response.json.return_value = SUCCESSFUL_RESPONSE_DATA
    mock_response.status_code = 200
    mock_response.url = "http://testurl.com"
    mock_requests_get.return_value = mock_response

    name, price = get_crypto_price("bitcoin", "usd")

    assert name == "Bitcoin"
    assert price == 60000.75
    mock_requests_get.assert_called_once_with(
        "https://api.coingecko.com/api/v3/simple/price",  # Fallback URL
        params={"ids": "bitcoin", "vs_currencies": "usd"},
        timeout=10,  # Fallback timeout
    )


# Tests for get_crypto_price_with_change function

@patch("src.price_fetcher.app_settings", spec=AppConfig)
@patch("requests.get")
def test_get_crypto_price_with_change_basic(
    mock_requests_get, mock_app_settings_instance, mock_app_settings_values
):
    """Test fetching price with 24h change."""
    # Configure the patched app_settings instance
    for key, value in mock_app_settings_values.items():
        setattr(mock_app_settings_instance, key, value)

    mock_response = MagicMock()
    mock_response.json.return_value = SUCCESSFUL_RESPONSE_WITH_CHANGE
    mock_response.status_code = 200
    mock_requests_get.return_value = mock_response

    result = get_crypto_price_with_change("bitcoin", "usd", include_24h=True)

    assert result["name"] == "Bitcoin"
    assert result["current_price"] == 60000.75
    assert result["price_change_24h"] == 5.25
    assert result["currency"] == "USD"
    assert result["success"] is True

    # Verify the API call had the correct parameters
    mock_requests_get.assert_called_once()
    call_args = mock_requests_get.call_args[1]
    assert call_args["params"]["include_24hr_change"] == "true"


@patch("src.price_fetcher.app_settings", spec=AppConfig)
@patch("requests.get")
def test_get_crypto_price_with_change_7d_and_30d(
    mock_requests_get, mock_app_settings_instance, mock_app_settings_values
):
    """Test fetching price with 24h, 7d, and 30d changes (requires two API calls)."""
    # Configure the patched app_settings instance
    for key, value in mock_app_settings_values.items():
        setattr(mock_app_settings_instance, key, value)

    # First response for basic price data
    mock_response1 = MagicMock()
    mock_response1.json.return_value = SUCCESSFUL_RESPONSE_WITH_CHANGE
    mock_response1.status_code = 200

    # Second response for market data (7d and 30d changes)
    mock_response2 = MagicMock()
    mock_response2.json.return_value = SUCCESSFUL_MARKET_DATA_RESPONSE
    mock_response2.status_code = 200

    mock_requests_get.side_effect = [mock_response1, mock_response2]

    result = get_crypto_price_with_change(
        "bitcoin", "usd", include_24h=True, include_7d=True, include_30d=True
    )

    assert result["name"] == "Bitcoin"
    assert result["current_price"] == 60000.75
    assert result["price_change_24h"] == 5.25
    assert result["price_change_7d"] == 10.5
    assert result["price_change_30d"] == 15.75
    assert result["currency"] == "USD"
    assert result["success"] is True

    # Verify two API calls were made
    assert mock_requests_get.call_count == 2
    
    # First call should be to the price endpoint
    first_call_args = mock_requests_get.call_args_list[0][1]
    assert "simple/price" in mock_app_settings_values["coingecko_api_url"]
    assert first_call_args["params"]["include_24hr_change"] == "true"
    
    # Second call should be to the coins endpoint
    second_call_args = mock_requests_get.call_args_list[1][0][0]  # Access the first positional argument
    assert "coins/bitcoin" in second_call_args
    second_call_params = mock_requests_get.call_args_list[1][1]["params"]
    assert second_call_params["market_data"] == "true"


@patch("src.price_fetcher.app_settings", spec=AppConfig)
@patch("requests.get")
def test_get_crypto_price_with_change_error_handling(
    mock_requests_get, mock_app_settings_instance, mock_app_settings_values
):
    """Test error handling in price with change fetching."""
    # Configure the patched app_settings instance
    for key, value in mock_app_settings_values.items():
        setattr(mock_app_settings_instance, key, value)

    # Simulate a failed API response
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
        "Not Found"
    )
    mock_response.text = "Not Found Text"
    mock_requests_get.return_value = mock_response

    result = get_crypto_price_with_change("bitcoin", "usd", include_24h=True)

    # The function should still return a result object, but with success=False
    assert result["name"] == "Bitcoin"
    assert result["current_price"] is None
    assert result["price_change_24h"] is None
    assert result["currency"] == "USD"
    assert result["success"] is False


# Tests for get_multiple_crypto_prices function

@patch("src.price_fetcher.app_settings", spec=AppConfig)
@patch("requests.get")
def test_get_multiple_crypto_prices_success(
    mock_requests_get, mock_app_settings_instance, mock_app_settings_values
):
    """Test successful fetching of multiple cryptocurrency prices."""
    # Configure the patched app_settings instance
    for key, value in mock_app_settings_values.items():
        setattr(mock_app_settings_instance, key, value)

    mock_response = MagicMock()
    mock_response.json.return_value = SUCCESSFUL_MULTIPLE_RESPONSE
    mock_response.status_code = 200
    mock_requests_get.return_value = mock_response

    result = get_multiple_crypto_prices(["bitcoin", "ethereum"], "usd", include_change=True)

    assert len(result) == 2
    assert "bitcoin" in result
    assert "ethereum" in result
    
    # Check bitcoin data
    assert result["bitcoin"]["name"] == "Bitcoin"
    assert result["bitcoin"]["current_price"] == 60000.75
    assert result["bitcoin"]["price_change_24h"] == 5.25
    assert result["bitcoin"]["success"] is True
    
    # Check ethereum data
    assert result["ethereum"]["name"] == "Ethereum"
    assert result["ethereum"]["current_price"] == 3000.50
    assert result["ethereum"]["price_change_24h"] == -2.10
    assert result["ethereum"]["success"] is True

    # Verify the API call
    mock_requests_get.assert_called_once()
    call_args = mock_requests_get.call_args[1]
    assert call_args["params"]["ids"] == "bitcoin,ethereum"
    assert call_args["params"]["include_24hr_change"] == "true"


@patch("src.price_fetcher.app_settings", spec=AppConfig)
@patch("requests.get")
def test_get_multiple_crypto_prices_partial_success(
    mock_requests_get, mock_app_settings_instance, mock_app_settings_values
):
    """Test partially successful fetching of multiple cryptocurrency prices."""
    # Configure the patched app_settings instance
    for key, value in mock_app_settings_values.items():
        setattr(mock_app_settings_instance, key, value)

    # Only bitcoin data is returned, not litecoin
    mock_response = MagicMock()
    mock_response.json.return_value = {"bitcoin": {"usd": 60000.75}}
    mock_response.status_code = 200
    mock_requests_get.return_value = mock_response

    result = get_multiple_crypto_prices(["bitcoin", "litecoin"], "usd")

    assert len(result) == 2  # Both requested cryptos should be in the result
    
    # Bitcoin should be successful
    assert result["bitcoin"]["name"] == "Bitcoin"
    assert result["bitcoin"]["current_price"] == 60000.75
    assert result["bitcoin"]["success"] is True
    
    # Litecoin should be in the result but with success=False
    assert result["litecoin"]["name"] == "Litecoin"
    assert result["litecoin"]["current_price"] is None
    assert result["litecoin"]["success"] is False


@patch("src.price_fetcher.app_settings", spec=AppConfig)
@patch("requests.get")
def test_get_multiple_crypto_prices_empty_list(
    mock_requests_get, mock_app_settings_instance, mock_app_settings_values
):
    """Test behavior when an empty list of cryptos is provided."""
    # Configure the patched app_settings instance
    for key, value in mock_app_settings_values.items():
        setattr(mock_app_settings_instance, key, value)

    result = get_multiple_crypto_prices([], "usd")

    assert result == {}  # Should return an empty dictionary
    mock_requests_get.assert_not_called()  # No API call should be made
