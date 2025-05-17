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

Run the script from the command line, specifying the cryptocurrency ID and currency:

```bash
python main.py --crypto <crypto_id> --currency <currency_code>
```

**Arguments:**

*   `--crypto`: (Optional) The CoinGecko ID of the cryptocurrency (e.g., `bitcoin`, `ethereum`, `solana`). Defaults to `bitcoin`.
*   `--currency`: (Optional) The currency code for the price (e.g., `usd`, `eur`). Defaults to `usd`.
*   `--lang`: (Optional) Language for narration (e.g., `en`, `es`, `fr`). Defaults to value in config.ini.
*   `--slow`: (Optional) Use slower narration speed. Use `--no-slow` for normal speed. Defaults to value in config.ini.
*   `--force-new`: (Optional) Force creation of new narration even if a cached version exists.
*   `--debug`: (Optional) Enable debug level logging.

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

## Project Structure

```
quantlink-fren-core-narrator/
├── config.ini          # Application configuration
├── src/
│   ├── __init__.py
│   ├── app_config.py   # Configuration management
│   ├── price_fetcher.py
│   └── narrator.py
├── tests/              # Unit tests
│   ├── __init__.py
│   ├── test_price_fetcher.py
│   └── test_narrator.py
├── main.py
├── requirements.txt
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

## Project Purpose, Roadmap, and Development Plan

### Purpose

The **QuantLink FREN Core Narrator** serves as the Minimum Viable Product (MVP) for a more extensive system aimed at providing AI-narrated data feeds. The primary goal of this repository is to establish a foundational command-line application that can:

1.  Fetch real-time data for a specified asset (initially cryptocurrencies) from a public API.
2.  Convert this data into a human-readable textual format.
3.  Utilize Text-to-Speech (TTS) technology to audibly narrate the information.

This MVP validates the core concept of fetching and narrating financial data, paving the way for future enhancements and integrations within the broader QuantLink ecosystem. It demonstrates the technical feasibility of combining data retrieval with AI-driven voice output for delivering timely information.

### Current Status: MVP Achieved and Enhanced

The current version of this repository successfully implements the core MVP functionalities with several enhancements:

*   **Price Fetching:** Connects to the CoinGecko API to retrieve current prices for specified cryptocurrencies against various fiat currencies. Includes robust error handling and retries.
*   **Narration:** Uses `gTTS` (Google Text-to-Speech) to convert the fetched price into an audio narration with reliable cross-platform playback.
*   **Command-Line Interface:** Allows users to specify the cryptocurrency, target currency, language, narration speed, and caching behavior via command-line arguments.
*   **Caching System:** Implements a smart caching system to avoid redundant API calls and narrations for repeated queries, improving performance and reducing resource usage.
*   **Modular Structure:** A well-organized, modular structure with separate components for configuration, price fetching, and narration.

### Development Plan & Future Enhancements

While the enhanced MVP is functional, the following steps and enhancements are planned to evolve this project into a more robust and feature-rich application. These are iterative steps and can be prioritized based on evolving requirements.

**Phase 1: Stabilisation & Refinement (Short-Term)**

1.  **Enhanced Error Handling & Resilience:**
    *   Implement more sophisticated error handling for API rate limits, network interruptions, and invalid API responses (e.g., retries with backoff).
    *   Add more detailed logging for debugging and monitoring (e.g., using the `logging` module).
    *   Validate API responses more thoroughly.
2.  **Configuration Management:**
    *   Introduce a configuration file (e.g., `config.ini` or `config.yaml`) for API keys (if needed in the future), default settings, and other parameters to avoid hardcoding.
3.  **Improved Narration:**
    *   Allow selection of different TTS voices or engines if `gTTS` proves limiting.
    *   Provide options for narration speed and language (currently defaults to English).
    *   More natural phrasing for prices (e.g., handling cents, large numbers more gracefully).
4.  **Code Quality & Testing:**
    *   Add unit tests for `price_fetcher.py` and `narrator.py` modules (using `unittest` or `pytest`).
    *   Implement integration tests for the main application flow.
    *   Enforce code style (e.g., using Black, Flake8) and add linting to the development workflow.
5.  **Dependency Management & Cross-Platform Compatibility:**
    *   Review `playsound` alternatives if cross-platform issues persist (e.g., `pygame.mixer`, `simpleaudio`).
    *   Ensure consistent behavior across Windows, macOS, and Linux.

**Phase 2: Feature Expansion (Mid-Term)**

1.  **Support for More Data Sources & Asset Types:**
    *   Abstract the data fetching module to support other APIs (e.g., stock prices, commodity prices).
    *   Allow users to specify different data providers.
2.  **Advanced Narration Features:**
    *   Ability to narrate historical data, price changes (e.g., "Bitcoin is up 5% at $60,000").
    *   Narration of multiple assets in a sequence.
    *   Potentially explore more advanced, natural-sounding cloud-based TTS services (e.g., Google Cloud TTS, Amazon Polly), which might require API keys.
3.  **User Interface (Beyond CLI):**
    *   Develop a simple GUI (e.g., using Tkinter, PyQt, or a web-based interface like Flask/Streamlit) for users not comfortable with CLI.
4.  **Scheduling & Background Operation:**
    *   Allow scheduling of price narrations at regular intervals (e.g., every hour).
    *   Enable the application to run as a background service.

**Phase 3: Integration & Advanced AI (Long-Term)**

1.  **Integration with QuantLink Ecosystem:**
    *   Develop APIs or methods for this narrator to be triggered by other QuantLink services.
    *   Feed narrated data into other QuantLink dashboards or applications.
2.  **Personalized Narration & AI Insights:**
    *   Allow users to create watchlists for narrated assets.
    *   Incorporate basic AI/ML to provide simple insights alongside the price (e.g., "Price is trending upwards," "Significant volume change detected").
    *   Natural Language Understanding (NLU) for voice commands (e.g., "What's the price of Ethereum?").

By following this development plan, the `quantlink-fren-core-narrator` will evolve from a proof-of-concept into a valuable tool for AI-driven data narration.
