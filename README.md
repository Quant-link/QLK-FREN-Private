# QuantLink FREN Core Narrator MVP

MVP for QuantLink's FREN: A command-line application that fetches real-time cryptocurrency price data for a specified asset from a public API (CoinGecko) and uses Text-to-Speech (TTS) to narrate the price. This serves as the foundational proof-of-concept for AI-narrated data feeds.

## Features

*   Fetches real-time cryptocurrency prices from CoinGecko API.
*   Narrates the price using Google Text-to-Speech (gTTS).
*   Supports specifying cryptocurrency ID and currency (default: Bitcoin in USD).
*   Command-line interface for ease of use.

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

## Project Structure

```
quantlink-fren-core-narrator/
├── src/
│   ├── __init__.py
│   ├── price_fetcher.py
│   └── narrator.py
├── main.py
├── requirements.txt
└── README.md
```

## Notes

*   The `playsound` library might require additional codecs or libraries on some systems (e.g., GStreamer on Linux).
*   This application creates a temporary audio file (`temp_price_narration.mp3`) in the project root during narration, which is deleted afterward.
