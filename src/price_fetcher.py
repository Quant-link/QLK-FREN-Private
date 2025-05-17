import requests

# CoinGecko API endpoint for simple price fetching
COINGECKO_API_URL = "https://api.coingecko.com/api/v3/simple/price"

def get_crypto_price(crypto_id: str, vs_currency: str = "usd") -> tuple[str | None, float | None]:
    """
    Fetches the current price of a specified cryptocurrency from the CoinGecko API.

    Args:
        crypto_id (str): The CoinGecko ID of the cryptocurrency (e.g., "bitcoin", "ethereum").
        vs_currency (str): The currency to compare against (e.g., "usd", "eur"). Defaults to "usd".

    Returns:
        tuple[str | None, float | None]: A tuple containing the capitalized cryptocurrency name
                                         and its price. Returns (None, None) if an error occurs
                                         or the price cannot be found.
    """
    params = {
        "ids": crypto_id,
        "vs_currencies": vs_currency
    }
    try:
        response = requests.get(COINGECKO_API_URL, params=params, timeout=10)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        data = response.json()

        if crypto_id in data and vs_currency in data[crypto_id]:
            price = data[crypto_id][vs_currency]
            # Capitalize the first letter of the crypto_id for better display
            return crypto_id.capitalize(), float(price)
        else:
            print(f"Error: Price not found for '{crypto_id}' in '{vs_currency}'. Response: {data}")
            return None, None
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP Error Occurred: {http_err} - Status Code: {response.status_code} - Response: {response.text}")
        return None, None
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Connection Error Occurred: {conn_err}")
        return None, None
    except requests.exceptions.Timeout as timeout_err:
        print(f"Timeout Error Occurred: {timeout_err}")
        return None, None
    except requests.exceptions.RequestException as req_err:
        print(f"An Unexpected Error Occurred with the Request: {req_err}")
        return None, None
    except ValueError:  # Includes JSONDecodeError
        print(f"Error: Could not decode JSON response from API. Response: {response.text if 'response' in locals() else 'No response object'}")
        return None, None 