# QuantLink FREN Core Narrator MVP

MVP for QuantLink's FREN: A command-line application that fetches real-time cryptocurrency price data for a specified asset from a public API (CoinGecko) and uses Text-to-Speech (TTS) to narrate the price. This serves as the foundational proof-of-concept for AI-narrated data feeds.

## Features

*   Fetches real-time cryptocurrency prices from CoinGecko API.
*   Narrates the price using Google Text-to-Speech (gTTS).
*   Supports specifying cryptocurrency ID and currency (default: Bitcoin in USD).
*   Command-line interface for ease of use.
*   Cross-platform audio playback with automatic fallback mechanisms.
*   Configurable narration language and speed.
*   Smart caching system to avoid redundant API calls and narrations.
*   Robust error handling and configuration management.
*   Historical price change narration (24h, 7d, 30d) with trend analysis.
*   Batch narration of multiple cryptocurrencies in sequence.
*   Customizable watchlists for frequently monitored assets.
*   **Web API** interface for HTTP access to all narration features.
*   **Web UI** with an intuitive interface for narrating cryptocurrency prices and custom text.

## Prerequisites

*   Python 3.7+

## Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Quant-link/quantlink-fren-core-narrator.git
    cd quantlink-fren-core-narrator
    ```

2.  **Create and activate a virtual environment:**
    *   On macOS and Linux:
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```
    *   On Windows:
        ```bash
        python -m venv venv
        .\venv\Scripts\activate
        ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Usage

The application can be used in two modes:

1. **Command-line Interface (CLI)**: Run as a traditional command-line application
2. **Web API Server**: Run as a web server offering HTTP endpoints

### Command-line Interface

Run the script from the command line with various options based on your needs:

#### Single Cryptocurrency Mode

```bash
python main.py --crypto <crypto_id> --currency <currency_code> [additional options]
```

#### Multiple Cryptocurrencies (Batch) Mode

```bash
python main.py --cryptos <comma_separated_crypto_ids> --currency <currency_code> [additional options]
```

**Arguments:**

*   `--crypto`: (Optional) The CoinGecko ID of a single cryptocurrency (e.g., `bitcoin`, `ethereum`, `solana`). Defaults to `bitcoin`.
*   `--cryptos`: (Optional) Comma-separated list of cryptocurrency IDs for batch narration (e.g., `bitcoin,ethereum,solana`). Cannot be used with `--crypto`.
*   `--currency`: (Optional) The currency code for the price (e.g., `usd`, `eur`). Defaults to `usd`.
*   `--lang`: (Optional) Language for narration (e.g., `en`, `es`, `fr`). Defaults to value in config.ini.
*   `--slow`: (Optional) Use slower narration speed. Use `--no-slow` for normal speed. Defaults to value in config.ini.
*   `--force-new`: (Optional) Force creation of new narration even if a cached version exists.
*   `--debug`: (Optional) Enable debug level logging.

**Price Change Options:**

*   `--with-24h-change`: Include 24-hour price change in the narration.
*   `--with-7d-change`: Include 7-day price change in the narration (requires additional API call).
*   `--with-30d-change`: Include 30-day price change in the narration (requires additional API call).

**Examples:**

*   Fetch and narrate the price of Bitcoin in USD (default):
    ```bash
    python main.py
    ```
*   Fetch and narrate the price of Ethereum in USD:
    ```bash
    python main.py --crypto ethereum
    ```
*   Fetch and narrate the price of Solana in EUR:
    ```bash
    python main.py --crypto solana --currency eur
    ```
*   Narrate Bitcoin price in Spanish with slow speed:
    ```bash
    python main.py --lang es --slow
    ```
*   Force a new narration, bypassing the cache:
    ```bash
    python main.py --force-new
    ```
*   Fetch Bitcoin price with 24-hour price change:
    ```bash
    python main.py --with-24h-change
    ```
*   Fetch Bitcoin price with 24-hour, 7-day, and 30-day price changes:
    ```bash
    python main.py --with-24h-change --with-7d-change --with-30d-change
    ```
*   Narrate multiple cryptocurrencies in sequence:
    ```bash
    python main.py --cryptos "bitcoin,ethereum,solana"
    ```
*   Narrate multiple cryptocurrencies with 24-hour price changes:
    ```bash
    python main.py --cryptos "bitcoin,ethereum,solana" --with-24h-change
    ```

### Web API Server

Run the Web API server to access all narration features via HTTP:

```bash
python web_api.py [--host <host>] [--port <port>] [--debug]
```

**Arguments:**

*   `--host`: (Optional) Host to run the server on. Defaults to `127.0.0.1`.
*   `--port`: (Optional) Port to run the server on. Defaults to `5000`.
*   `--debug`: (Optional) Run in debug mode.

Once the server is running, you can access:

1. **Web User Interface**: Open your browser and visit `http://localhost:5000/` (or your configured host/port) to access the interactive web interface.

2. **API Endpoints**:

#### Health Check

```
GET /api/health
```

Returns basic health information about the API.

#### Get Cryptocurrency Price

```
GET /api/crypto/price?crypto=<crypto_id>&currency=<currency_code>&with_24h_change=<true|false>&with_7d_change=<true|false>&with_30d_change=<true|false>
```

Fetches and returns price data for a single cryptocurrency.

#### Get Multiple Cryptocurrency Prices

```
GET /api/crypto/prices?cryptos=<comma_separated_crypto_ids>&currency=<currency_code>&with_24h_change=<true|false>
```

Fetches and returns price data for multiple cryptocurrencies in a single request.

#### Narrate Custom Text

```
POST /api/narrator/text
Content-Type: application/json

{
  "text": "Text to narrate",
  "lang": "en",
  "slow": false,
  "return_audio": false
}
```

Generates audio narration for custom text. If `return_audio` is `false`, returns a file ID that can be used to retrieve the audio file. If `return_audio` is `true`, returns the audio file directly.

#### Get Audio File

```
GET /api/narrator/audio/<file_id>
```

Retrieves a previously generated audio file by its ID.

#### Narrate Cryptocurrency Price

```
POST /api/narrator/crypto
Content-Type: application/json

{
  "crypto": "bitcoin",
  "currency": "usd",
  "with_24h_change": true,
  "with_7d_change": false,
  "with_30d_change": false,
  "lang": "en",
  "slow": false,
  "return_audio": false
}
```

Fetches cryptocurrency price data and generates audio narration. If `return_audio` is `false`, returns price data and a file ID that can be used to retrieve the audio file. If `return_audio` is `true`, returns the audio file directly.

**Example using curl:**

```bash
# Get Bitcoin price
curl "http://localhost:5000/api/crypto/price?crypto=bitcoin&currency=usd"

# Narrate Bitcoin price and get file ID
curl -X POST "http://localhost:5000/api/narrator/crypto" \
  -H "Content-Type: application/json" \
  -d '{"crypto":"bitcoin","currency":"usd","with_24h_change":true}'

# Get audio file using file ID
curl -O -J "http://localhost:5000/api/narrator/audio/<file_id>"
```

## Project Structure

```
quantlink-fren-core-narrator/
├── config.ini          # Application configuration
├── src/
│   ├── __init__.py
│   ├── app_config.py   # Configuration management
│   ├── price_fetcher.py  # Fetches cryptocurrency prices
│   └── narrator.py     # Handles text-to-speech narration
├── tests/              # Unit tests
│   ├── __init__.py
│   ├── test_price_fetcher.py
│   └── test_narrator.py
├── main.py             # CLI application entry point
├── web_api.py          # Web API server entry point
├── requirements.txt    # Python dependencies
└── README.md
```

## Configuration

The application uses a `config.ini` file for configuration with these key sections:

### [API]
- `BASE_URL`: Base URL for the CoinGecko API
- `PRICE_ENDPOINT`: API endpoint for price data
- `REQUEST_TIMEOUT`: Timeout for API requests in seconds

### [Retry]
- `MAX_RETRIES`: Maximum number of API request retry attempts
- `INITIAL_BACKOFF_DELAY`: Initial delay before the first retry (seconds)
- `BACKOFF_FACTOR`: Multiplier for backoff between retries
- `RETRYABLE_STATUS_CODES`: HTTP status codes that warrant a retry

### [Defaults]
- `CRYPTO_ID`: Default cryptocurrency ID to fetch
- `VS_CURRENCY`: Default currency for price data
- `INCLUDE_24H_CHANGE`: Whether to include 24h price change by default
- `INCLUDE_7D_CHANGE`: Whether to include 7d price change by default
- `INCLUDE_30D_CHANGE`: Whether to include 30d price change by default
- `CRYPTO_WATCHLIST`: Default list of cryptocurrencies for batch narration

### [BatchNarration]
- `NARRATE_INTRO`: Whether to narrate an introduction in batch mode
- `NARRATION_PAUSE`: Pause duration between narrations in seconds
- `MAX_CRYPTOS`: Maximum number of cryptocurrencies to narrate in one batch

### [Logging]
- `TEMP_AUDIO_FILE`: Temporary audio file name
- `LOG_LEVEL`: Logging verbosity (DEBUG, INFO, WARNING, ERROR, CRITICAL)

### [Narrator]
- `NARRATION_LANG`: Language for TTS narration
- `NARRATION_SLOW`: Whether to use slow narration speed
- `KEEP_AUDIO_ON_ERROR`: Whether to keep audio files when playback fails

### [Cache]
- `ENABLED`: Whether to enable the narration cache
- `EXPIRATION`: How long to keep cached narrations (in seconds)
- `MAX_ITEMS`: Maximum number of items to keep in the cache

## Notes

*   Cross-platform audio playback is supported with automatic fallbacks:
    - Windows: Falls back to PowerShell SoundPlayer if playsound fails
    - macOS: Falls back to afplay if playsound fails
    - Linux: Tries multiple players (paplay, aplay, mpg123, mpg321) if playsound fails
*   When audio playback fails, the file location is displayed so you can play it manually if needed.
*   You can set `KEEP_AUDIO_ON_ERROR = True` in config.ini to retain audio files when playback fails.
*   Narration caching saves resources by reusing recent narrations for the same price:
    - Cache entries expire after the time specified in `EXPIRATION` (default: 5 minutes)
    - Override caching with the `--force-new` command line option
    - Disable caching by setting `ENABLED = False` in the `[Cache]` section of config.ini
*   Price change options:
    - 24-hour changes are fetched in the same API call as the current price
    - 7-day and 30-day changes require an additional API call and may be subject to stricter rate limits
*   Batch narration allows you to listen to multiple cryptocurrencies in sequence:
    - Introduces each batch with a summary of how many prices are about to be narrated
    - Each cryptocurrency is narrated with appropriate pauses between them
    - A concluding message is played after all cryptocurrencies are narrated
*   Web API:
    - Temporary audio files created by the Web API are automatically cleaned up after 30 minutes
    - The Web API does not play audio files; it generates them and allows clients to download them
    - CORS is enabled to allow cross-domain access to the API

## Project Purpose, Roadmap, and Development Plan

### Purpose

The **QuantLink FREN Core Narrator** serves as the Minimum Viable Product (MVP) for a more extensive system aimed at providing AI-narrated data feeds. The primary goal of this repository is to establish a foundational command-line application that can:

1.  Fetch real-time data for a specified asset (initially cryptocurrencies) from a public API.
2.  Convert this data into a human-readable textual format.
3.  Utilize Text-to-Speech (TTS) technology to audibly narrate the information.

This MVP validates the core concept of fetching and narrating financial data, paving the way for future enhancements and integrations within the broader QuantLink ecosystem. It demonstrates the technical feasibility of combining data retrieval with AI-driven voice output for delivering timely information.

### Current Status: Enhanced MVP

The current version of this repository successfully implements all the core MVP functionalities with several notable enhancements:

*   **Price Fetching:** Connects to the CoinGecko API to retrieve current prices and historical changes for specified cryptocurrencies against various fiat currencies. Includes robust error handling and retries.
*   **Narration:** Uses `gTTS` (Google Text-to-Speech) to convert the fetched prices and trends into audio narrations with reliable cross-platform playback.
*   **Command-Line Interface:** Allows users to specify multiple options including cryptocurrency, target currency, language, narration speed, caching behavior, and price change periods.
*   **Web API:** Provides HTTP endpoints for accessing all narration features, making the functionality available to other applications.
*   **Multi-Crypto Support:** Supports batch narration of multiple cryptocurrencies with appropriate introduction and conclusion narrations.
*   **Caching System:** Implements a smart caching system to avoid redundant API calls and narrations for repeated queries, improving performance and reducing resource usage.
*   **Modular Structure:** A well-organized, modular structure with separate components for configuration, price fetching, and narration.

### Development Plan & Future Enhancements

Moving forward, the following enhancements are planned:

**Phase 1: User Experience & Data Visualization (Short-Term)**

1.  **Interactive UI:** ✅
    *   ~~Implement a simple terminal-based UI using libraries like `curses` or `rich` for a more interactive experience.~~
    *   ~~Allow users to select cryptocurrencies from a menu and customize narration preferences.~~
    *   ~~Display price charts alongside narration for visual reinforcement.~~
    *   Implemented a full Web API with a responsive web interface for narrating cryptocurrency prices.
    *   Added ability to select cryptocurrencies, currencies, and narration options from a user-friendly interface.
    *   Created functionality for narrating custom text with language options.

2.  **Notification System:**
    *   Add price alerts for significant price movements.
    *   Set up scheduled narrations at regular intervals.
    *   Implement desktop notifications when prices cross user-defined thresholds.

**Phase 2: Advanced Narration Features (Mid-Term)**

1.  **Enhanced Voice Capabilities:**
    *   Support more advanced TTS services with more natural-sounding voices (e.g., Google Cloud TTS, Amazon Polly).
    *   Add voice personality selection to match user preferences.
    *   Implement more sophisticated phrasing for price narrations and trend analysis.

2.  **Custom Narration Templates:**
    *   Allow users to define custom narration templates (e.g., "Bitcoin is currently at $X, showing a Y% change since yesterday").
    *   Support variables and conditional logic in templates.
    *   Add preset templates for different scenarios (e.g., quick updates, detailed analysis).

**Phase 3: Integration & AI Features (Long-Term)**

1.  **Integration with Other Financial Data:**
    *   Add support for stock market data, commodities, forex, and other financial instruments.
    *   Implement portfolio narration for aggregated holdings.
    *   Create narrated data feeds that can be consumed by other applications.

2.  **AI-Powered Insights:**
    *   Generate simple trend analysis and predictions based on historical data.
    *   Add sentiment analysis from news and social media sources.
    *   Provide context-aware narrations that adapt to market conditions.

By following this development plan, the `quantlink-fren-core-narrator` will evolve from an enhanced proof-of-concept into a sophisticated tool for narrating financial data with intelligent insights.
