import argparse
import logging
import sys  # For exiting if config is missing
from src.price_fetcher import get_crypto_price, get_crypto_price_with_change, get_multiple_crypto_prices
from src.narrator import narrate_price, narrate_price_with_change, narrate_multiple_prices
from src.app_config import app_settings  # Import the application settings

# Get a logger for this module (configuration will be set up after loading app_settings)
logger = logging.getLogger(__name__)


def setup_logging():
    """Configures logging based on settings from config.ini or defaults."""
    log_level_str = "INFO"  # Default log level
    if app_settings and app_settings.log_level:
        log_level_str = app_settings.log_level
    else:
        # Fallback if app_settings isn't available or log_level isn't set
        print(
            "Warning: Application settings or log_level not found. Defaulting to INFO log level.",
            file=sys.stderr,
        )

    numeric_log_level = getattr(logging, log_level_str.upper(), logging.INFO)

    logging.basicConfig(
        level=numeric_log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logger.info(f"Logging configured to level: {log_level_str}")


def process_single_crypto(args):
    """
    Processes and narrates a single cryptocurrency based on command-line arguments.
    
    Args:
        args: Command-line arguments parsed by argparse
        
    Returns:
        bool: True if successful, False otherwise
    """
    crypto_id_to_fetch = args.crypto.lower()
    currency_to_fetch = args.currency.lower()
    
    # Determine if we need to fetch price changes
    need_price_changes = args.with_24h_change or args.with_7d_change or args.with_30d_change
    
    if need_price_changes:
        logger.info(
            f"Fetching {crypto_id_to_fetch.capitalize()} with price changes in {currency_to_fetch.upper()}"
        )
        crypto_data = get_crypto_price_with_change(
            crypto_id_to_fetch, 
            currency_to_fetch,
            include_24h=args.with_24h_change,
            include_7d=args.with_7d_change,
            include_30d=args.with_30d_change
        )
        
        if crypto_data["success"] and crypto_data["current_price"] is not None:
            logger.info(
                f"Fetched Price: {crypto_data['name']} - {crypto_data['current_price']:,.2f} {crypto_data['currency']}"
            )
            
            # Narrate the price with changes
            narration_result = narrate_price_with_change(
                crypto_data,
                include_24h=args.with_24h_change,
                include_7d=args.with_7d_change,
                include_30d=args.with_30d_change,
                lang=args.lang,
                slow=args.slow,
                force_new=args.force_new
            )
            
            if not narration_result:
                logger.error("Narration failed. Check logs for more details.")
                return False
            return True
        else:
            logger.error(
                f"Could not retrieve price data for {crypto_id_to_fetch.capitalize()}. Check logs."
            )
            return False
    else:
        # Traditional single price fetch without changes
        logger.info(
            f"Starting application for {crypto_id_to_fetch.capitalize()} in {currency_to_fetch.upper()}"
        )
        crypto_name, price = get_crypto_price(crypto_id_to_fetch, currency_to_fetch)

        if crypto_name and price is not None:
            logger.info(
                f"Fetched Price: {crypto_name} - {price:,.2f} {currency_to_fetch.upper()}"
            )
            
            # Narrate the price
            narration_result = narrate_price(
                crypto_name,
                price,
                currency_to_fetch.upper(),
                lang=args.lang,
                slow=args.slow,
                force_new=args.force_new,
            )
            
            if not narration_result:
                logger.error("Narration failed. Check logs for more details.")
                return False
            return True
        else:
            logger.error(
                f"Could not retrieve price for {crypto_id_to_fetch.capitalize()}. Check logs."
            )
            return False


def process_multiple_cryptos(args):
    """
    Processes and narrates multiple cryptocurrencies based on command-line arguments.
    
    Args:
        args: Command-line arguments parsed by argparse
        
    Returns:
        bool: True if at least one crypto was successfully narrated, False otherwise
    """
    crypto_ids = [crypto.strip().lower() for crypto in args.cryptos.split(',')]
    currency_to_fetch = args.currency.lower()
    
    logger.info(f"Fetching prices for multiple cryptocurrencies: {', '.join(crypto_ids)}")
    
    # Determine if 24h changes should be included
    include_change = args.with_24h_change
    
    # Fetch prices for all requested cryptocurrencies in a single API call
    crypto_data_dict = get_multiple_crypto_prices(
        crypto_ids,
        currency_to_fetch,
        include_change=include_change
    )
    
    if not crypto_data_dict:
        logger.error("Failed to fetch any cryptocurrency prices")
        return False
    
    # Convert dict to list for narration
    crypto_data_list = [data for _, data in crypto_data_dict.items() if data["success"]]
    
    if not crypto_data_list:
        logger.error("No valid cryptocurrency data found for narration")
        return False
    
    # Log the fetched prices
    for crypto_data in crypto_data_list:
        price_str = f"{crypto_data['current_price']:,.2f}" if crypto_data['current_price'] is not None else "N/A"
        logger.info(f"Fetched: {crypto_data['name']} - {price_str} {crypto_data['currency']}")
    
    # Narrate all prices in sequence
    success_count = narrate_multiple_prices(
        crypto_data_list,
        include_changes=include_change,
        narrate_intro=True,
        lang=args.lang,
        slow=args.slow,
        force_new=args.force_new
    )
    
    if success_count > 0:
        logger.info(f"Successfully narrated {success_count} out of {len(crypto_data_list)} cryptocurrencies")
        return True
    else:
        logger.error("Failed to narrate any cryptocurrencies")
        return False


def main():
    """Main function to parse arguments, fetch price(s), and narrate them."""
    if not app_settings:
        # This check is critical. If app_settings is None, it means config.ini was not loaded.
        logger.critical(
            "CRITICAL: app_settings is None. Config file 'config.ini' might be missing or "
            "corrupted. Exiting."
        )
        # Optionally, print to stderr as logging might not be fully set up if config is missing
        print(
            "CRITICAL: Config file 'config.ini' is missing or corrupted. "
            "Ensure it exists and is valid. Exiting.",
            file=sys.stderr,
        )
        sys.exit(1)  # Exit the application as it cannot run without config

    # Setup logging now that we are sure app_settings is loaded (or handled the failure)
    setup_logging()

    default_crypto = app_settings.default_crypto_id
    default_currency = app_settings.default_vs_currency
    default_narration_lang = app_settings.narration_lang
    default_narration_slow = app_settings.narration_slow

    parser = argparse.ArgumentParser(
        description="Fetches cryptocurrency prices and narrates them.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    
    # Create a group for single versus multiple crypto mode
    mode_group = parser.add_mutually_exclusive_group()
    
    mode_group.add_argument(
        "--crypto",
        type=str,
        default=default_crypto,
        help=(
            f"CoinGecko ID of the cryptocurrency (e.g., bitcoin, ethereum, solana).\n"
            f"Default: {default_crypto}"
        ),
    )
    
    mode_group.add_argument(
        "--cryptos",
        type=str,
        help=(
            "Comma-separated list of CoinGecko cryptocurrency IDs for batch narration.\n"
            "Example: 'bitcoin,ethereum,solana'\n"
            "When this option is used, the application narrates multiple cryptocurrencies in sequence."
        ),
    )
    
    parser.add_argument(
        "--currency",
        type=str,
        default=default_currency,
        help=(
            f"Currency code for the price (e.g., usd, eur).\n"
            f"Default: {default_currency}"
        ),
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug level logging (overrides config file setting).",
    )
    
    parser.add_argument(
        "--lang",
        type=str,
        default=default_narration_lang,
        help=(
            f"Language for narration (e.g., en, es, fr). \n"
            f"Default from config: {default_narration_lang}"
        ),
    )
    
    parser.add_argument(
        "--slow",
        action=argparse.BooleanOptionalAction,  # Allows --slow or --no-slow
        default=default_narration_slow,
        help=(
            f"Use slow narration speed. \n"
            f"Default from config: {default_narration_slow}"
        ),
    )
    
    parser.add_argument(
        "--force-new",
        action="store_true",
        help="Force creation of new narration even if a cached version exists.",
    )
    
    # Add price change period options
    price_change_group = parser.add_argument_group("Price Change Options")
    
    price_change_group.add_argument(
        "--with-24h-change",
        action="store_true",
        help="Include 24-hour price change in the narration.",
    )
    
    price_change_group.add_argument(
        "--with-7d-change",
        action="store_true",
        help="Include 7-day price change in the narration (requires additional API call).",
    )
    
    price_change_group.add_argument(
        "--with-30d-change",
        action="store_true",
        help="Include 30-day price change in the narration (requires additional API call).",
    )
    
    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)  # Set root logger level to DEBUG
        logger.debug("Debug mode enabled by command line argument (overrides config).")

    # Process based on whether we're in single or multiple crypto mode
    if args.cryptos:
        result = process_multiple_cryptos(args)
    else:
        result = process_single_crypto(args)
        
    if not result:
        sys.exit(2)  # Exit with error code 2 for narration/fetching failure


if __name__ == "__main__":
    main()
 