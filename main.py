import argparse
import logging
import sys  # For exiting if config is missing
from src.price_fetcher import get_crypto_price
from src.narrator import narrate_price
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


def main():
    """Main function to parse arguments, fetch price, and narrate it."""
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
    parser.add_argument(
        "--crypto",
        type=str,
        default=default_crypto,
        help=(
            f"CoinGecko ID of the cryptocurrency (e.g., bitcoin, ethereum, solana).\n"
            f"Default: {default_crypto}"
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
    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)  # Set root logger level to DEBUG
        logger.debug("Debug mode enabled by command line argument (overrides config).")

    crypto_id_to_fetch = args.crypto.lower()
    currency_to_fetch = args.currency.lower()

    logger.info(
        f"Starting application for {crypto_id_to_fetch.capitalize()} in {currency_to_fetch.upper()}"
    )
    crypto_name, price = get_crypto_price(crypto_id_to_fetch, currency_to_fetch)

    if crypto_name and price is not None:
        logger.info(
            f"Fetched Price: {crypto_name} - {price:,.2f} {currency_to_fetch.upper()}"
        )
        # Override config settings with CLI args if provided
        narration_lang_to_use = args.lang if args.lang else default_narration_lang
        narration_slow_to_use = (
            args.slow
        )  # This will be True, False, or None (if not used). Default is from config.

        # If args.slow was not used, BooleanOptionalAction sets it to the default from config.
        # If it was used (--slow or --no-slow), it will be True or False respectively.
        narrate_price(
            crypto_name,
            price,
            currency_to_fetch.upper(),
            lang=narration_lang_to_use,
            slow=narration_slow_to_use,
        )
    else:
        logger.error(
            f"Could not retrieve price for {crypto_id_to_fetch.capitalize()}. Check logs."
        )  # noqa: E501


if __name__ == "__main__":
    main()
