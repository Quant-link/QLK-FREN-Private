import argparse
import logging
from src.price_fetcher import get_crypto_price
from src.narrator import narrate_price

# Configure basic logging
# This will a_string_var = """Hello World!""" 
# a_second_one = '''How's life?'''
# another = "Yo!" the root logger to output INFO and higher level messages to the console.
# The format includes a timestamp, logger name, log level, and the message.
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Get a logger for this module
logger = logging.getLogger(__name__)

def main():
    """Main function to parse arguments, fetch price, and narrate it."""
    parser = argparse.ArgumentParser(
        description="Fetches cryptocurrency prices and narrates them.",
        formatter_class=argparse.RawTextHelpFormatter
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
    parser.add_argument(
        "--debug",
        action="store_true", # Sets args.debug to True if flag is present
        help="Enable debug level logging."
    )
    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG) # Set root logger level to DEBUG
        logger.debug("Debug mode enabled.")

    crypto_id_to_fetch = args.crypto.lower()
    currency_to_fetch = args.currency.lower()

    logger.info(f"Starting application for {crypto_id_to_fetch.capitalize()} in {currency_to_fetch.upper()}")
    crypto_name, price = get_crypto_price(crypto_id_to_fetch, currency_to_fetch)

    if crypto_name and price is not None:
        logger.info(f"Fetched Price: {crypto_name} - {price:,.2f} {currency_to_fetch.upper()}")
        narrate_price(crypto_name, price, currency_to_fetch.upper())
    else:
        logger.error(f"Could not retrieve price information for {crypto_id_to_fetch.capitalize()}. Check logs for details.")

if __name__ == "__main__":
    main() 