import argparse
from src.price_fetcher import get_crypto_price
from src.narrator import narrate_price

def main():
    """Main function to parse arguments, fetch price, and narrate it."""
    parser = argparse.ArgumentParser(
        description="Fetches cryptocurrency prices and narrates them.",
        formatter_class=argparse.RawTextHelpFormatter # To allow for better help text formatting
    )
    parser.add_argument(
        "--crypto",
        type=str,
        default="bitcoin",
        help="The CoinGecko ID of the cryptocurrency (e.g., bitcoin, ethereum, solana).\nDefault: bitcoin"
    )
    parser.add_argument(
        "--currency",
        type=str,
        default="usd",
        help="The currency code for the price (e.g., usd, eur).\nDefault: usd"
    )
    args = parser.parse_args()

    crypto_id_to_fetch = args.crypto.lower() # Ensure consistency in ID format
    currency_to_fetch = args.currency.lower()

    print(f"Fetching price for {crypto_id_to_fetch.capitalize()} in {currency_to_fetch.upper()}...")
    crypto_name, price = get_crypto_price(crypto_id_to_fetch, currency_to_fetch)

    if crypto_name and price is not None:
        print(f"Fetched Price: {crypto_name} - {price:,.2f} {currency_to_fetch.upper()}")
        narrate_price(crypto_name, price, currency_to_fetch.upper())
    else:
        print(f"Could not retrieve price information for {crypto_id_to_fetch.capitalize()}.")

if __name__ == "__main__":
    main() 