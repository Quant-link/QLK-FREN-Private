import pytest
from unittest.mock import (
    patch,
    MagicMock,
)  # pytest-mock provides the mocker fixture, but unittest.mock is often used directly too
import requests
from src.price_fetcher import get_crypto_price
from src.app_config import AppConfig  # To allow testing with mocked app_settings

# Sample successful API response
SUCCESSFUL_RESPONSE_DATA = {"bitcoin": {"usd": 60000.75}}

# Sample error response (e.g., currency not found for id)
ERROR_RESPONSE_DATA_NO_CURRENCY = {"bitcoin": {}}


@pytest.fixture
def mock_app_settings_values():
    """Fixture to provide a dictionary of mock AppConfig values."""
    return {
        "coingecko_api_url": "https://api.coingecko.com/api/v3/simple/price",
        "retry_max_retries": 3,
        "retry_initial_backoff": 0.01,  # Use a very small backoff for tests
        "retry_backoff_factor": 2,
        "retryable_status_codes": {429, 500, 502, 503, 504},
        "api_request_timeout": 5,
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
