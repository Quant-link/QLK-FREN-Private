import os
import tempfile
import logging
import argparse
import time
import uuid
from flask import Flask, request, jsonify, send_file, Response, send_from_directory
from flask_cors import CORS
from src.price_fetcher import get_crypto_price, get_crypto_price_with_change, get_multiple_crypto_prices
from src.narrator import narrate_text
from src.app_config import app_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__, static_folder='static')
CORS(app)  # Enable CORS for all routes

# Dictionary to store temporary audio files
# Format: {file_id: (filepath, expiration_timestamp)}
temp_files = {}


@app.route('/api/health', methods=['GET'])
def health_check():
    """Simple health check endpoint."""
    return jsonify({"status": "healthy", "version": "1.0.0"})


@app.route('/api/crypto/price', methods=['GET'])
def get_price():
    """
    Get cryptocurrency price data without narration.
    
    Query parameters:
        crypto: Cryptocurrency ID (e.g., bitcoin)
        currency: Currency code (e.g., usd)
        with_24h_change: Whether to include 24h price change (true/false)
        with_7d_change: Whether to include 7d price change (true/false)
        with_30d_change: Whether to include 30d price change (true/false)
    """
    try:
        crypto_id = request.args.get('crypto', app_settings.default_crypto_id).lower()
        currency = request.args.get('currency', app_settings.default_vs_currency).lower()
        
        # Check if we should include price changes
        include_24h = request.args.get('with_24h_change', 'false').lower() == 'true'
        include_7d = request.args.get('with_7d_change', 'false').lower() == 'true'
        include_30d = request.args.get('with_30d_change', 'false').lower() == 'true'
        
        if include_24h or include_7d or include_30d:
            # Get price with changes
            result = get_crypto_price_with_change(
                crypto_id, 
                currency,
                include_24h=include_24h,
                include_7d=include_7d,
                include_30d=include_30d
            )
            return jsonify(result)
        else:
            # Get basic price without changes
            name, price = get_crypto_price(crypto_id, currency)
            if name and price is not None:
                return jsonify({
                    "name": name,
                    "current_price": price,
                    "currency": currency.upper(),
                    "success": True
                })
            else:
                return jsonify({
                    "name": crypto_id.capitalize(),
                    "current_price": None,
                    "currency": currency.upper(),
                    "success": False,
                    "error": "Failed to fetch price"
                }), 404
    
    except Exception as e:
        logger.error(f"Error in get_price endpoint: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/crypto/prices', methods=['GET'])
def get_prices():
    """
    Get prices for multiple cryptocurrencies without narration.
    
    Query parameters:
        cryptos: Comma-separated list of cryptocurrency IDs
        currency: Currency code (e.g., usd)
        with_24h_change: Whether to include 24h price change (true/false)
    """
    try:
        crypto_ids_param = request.args.get('cryptos')
        if not crypto_ids_param:
            return jsonify({"success": False, "error": "No cryptocurrencies specified"}), 400
            
        crypto_ids = [crypto.strip().lower() for crypto in crypto_ids_param.split(',')]
        currency = request.args.get('currency', app_settings.default_vs_currency).lower()
        include_change = request.args.get('with_24h_change', 'false').lower() == 'true'
        
        results = get_multiple_crypto_prices(crypto_ids, currency, include_change=include_change)
        
        # Convert dictionary of results to a list for the API response
        response_data = {
            "prices": results,
            "success": any(item["success"] for item in results.values()),
            "count": len(results)
        }
        
        return jsonify(response_data)
    
    except Exception as e:
        logger.error(f"Error in get_prices endpoint: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/narrator/text', methods=['POST'])
def narrate_custom_text():
    """
    Generate audio narration for custom text.
    
    Request JSON body:
        text: The text to narrate
        lang: Language code (default: en)
        slow: Whether to use slow narration speed (default: false)
        return_audio: Whether to return the audio file (default: false)
        
    Returns:
        If return_audio is false: JSON with success status and file ID
        If return_audio is true: The audio file as attachment
    """
    try:
        data = request.json
        if not data or 'text' not in data:
            return jsonify({"success": False, "error": "No text provided"}), 400
            
        text = data.get('text')
        lang = data.get('lang', 'en')
        slow = data.get('slow', False)
        return_audio = data.get('return_audio', False)
        
        # Create temporary file for the audio
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
            temp_filepath = temp_file.name
        
        # Generate audio without playing it
        try:
            from gtts import gTTS
            tts = gTTS(text=text, lang=lang, slow=slow)
            tts.save(temp_filepath)
            
            # Generate a unique ID for the file
            file_id = str(uuid.uuid4())
            
            # Store the file path with an expiration time (30 minutes from now)
            expiration = time.time() + (30 * 60)  # 30 minutes
            temp_files[file_id] = (temp_filepath, expiration)
            
            # Clean up expired files
            _cleanup_expired_files()
            
            if return_audio:
                return send_file(
                    temp_filepath,
                    mimetype="audio/mpeg",
                    as_attachment=True,
                    download_name=f"narration_{file_id}.mp3"
                )
            else:
                return jsonify({
                    "success": True,
                    "file_id": file_id,
                    "expires_in_seconds": 30 * 60
                })
                
        except Exception as e:
            # Clean up the temporary file if narration failed
            if os.path.exists(temp_filepath):
                os.remove(temp_filepath)
            raise e
    
    except Exception as e:
        logger.error(f"Error in narrate_custom_text endpoint: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/narrator/audio/<file_id>', methods=['GET'])
def get_audio_file(file_id):
    """
    Get a previously generated audio file by its ID.
    
    Path parameters:
        file_id: The ID of the audio file
    """
    try:
        # Check if the file exists and is not expired
        if file_id in temp_files:
            filepath, expiration = temp_files[file_id]
            
            if time.time() > expiration:
                # File has expired
                del temp_files[file_id]
                if os.path.exists(filepath):
                    os.remove(filepath)
                return jsonify({"success": False, "error": "Audio file has expired"}), 404
                
            if os.path.exists(filepath):
                return send_file(
                    filepath,
                    mimetype="audio/mpeg",
                    as_attachment=True,
                    download_name=f"narration_{file_id}.mp3"
                )
            else:
                # File was removed from disk
                del temp_files[file_id]
                return jsonify({"success": False, "error": "Audio file not found"}), 404
        else:
            return jsonify({"success": False, "error": "Invalid file ID"}), 404
    
    except Exception as e:
        logger.error(f"Error in get_audio_file endpoint: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/narrator/crypto', methods=['POST'])
def narrate_crypto_price():
    """
    Generate audio narration for a cryptocurrency price.
    
    Request JSON body:
        crypto: Cryptocurrency ID
        currency: Currency code
        with_24h_change: Whether to include 24h price change
        with_7d_change: Whether to include 7d price change
        with_30d_change: Whether to include 30d price change
        lang: Language code
        slow: Whether to use slow narration speed
        return_audio: Whether to return the audio file
        
    Returns:
        If return_audio is false: JSON with success status, price data, and file ID
        If return_audio is true: The audio file as attachment
    """
    try:
        data = request.json
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400
            
        crypto_id = data.get('crypto', app_settings.default_crypto_id).lower()
        currency = data.get('currency', app_settings.default_vs_currency).lower()
        
        # Check if we should include price changes
        include_24h = data.get('with_24h_change', False)
        include_7d = data.get('with_7d_change', False)
        include_30d = data.get('with_30d_change', False)
        
        lang = data.get('lang', 'en')
        slow = data.get('slow', False)
        return_audio = data.get('return_audio', False)
        
        # Fetch price data with changes if requested
        if include_24h or include_7d or include_30d:
            price_data = get_crypto_price_with_change(
                crypto_id, 
                currency,
                include_24h=include_24h,
                include_7d=include_7d,
                include_30d=include_30d
            )
            
            if not price_data["success"]:
                return jsonify({
                    "success": False,
                    "error": "Failed to fetch price data",
                    "price_data": price_data
                }), 404
                
            # Build narration text
            crypto_name = price_data.get("name", "Unknown")
            price = price_data.get("current_price", 0.0)
            currency_code = price_data.get("currency", "USD")
            
            narration_text = f"The current price for {crypto_name} is {price:,.2f} {currency_code}."
            
            # Add 24-hour change if available
            if include_24h and "price_change_24h" in price_data and price_data["price_change_24h"] is not None:
                change_24h = price_data["price_change_24h"]
                direction = "up" if change_24h >= 0 else "down"
                narration_text += f" It has gone {direction} {abs(change_24h):.2f} percent in the last 24 hours."
            
            # Add 7-day change if available
            if include_7d and "price_change_7d" in price_data and price_data["price_change_7d"] is not None:
                change_7d = price_data["price_change_7d"]
                direction = "up" if change_7d >= 0 else "down"
                narration_text += f" Over the past 7 days, it has gone {direction} {abs(change_7d):.2f} percent."
            
            # Add 30-day change if available
            if include_30d and "price_change_30d" in price_data and price_data["price_change_30d"] is not None:
                change_30d = price_data["price_change_30d"]
                direction = "up" if change_30d >= 0 else "down"
                narration_text += f" In the last 30 days, it has gone {direction} {abs(change_30d):.2f} percent."
        else:
            # Fetch basic price without changes
            name, price = get_crypto_price(crypto_id, currency)
            if not (name and price is not None):
                return jsonify({
                    "success": False,
                    "error": "Failed to fetch price data"
                }), 404
                
            # Build price data object
            price_data = {
                "name": name,
                "current_price": price,
                "currency": currency.upper(),
                "success": True
            }
            
            # Build narration text
            narration_text = f"The current price for {name} is {price:,.2f} {currency.upper()}."
        
        # Create temporary file for the audio
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
            temp_filepath = temp_file.name
        
        # Generate audio without playing it
        try:
            from gtts import gTTS
            tts = gTTS(text=narration_text, lang=lang, slow=slow)
            tts.save(temp_filepath)
            
            # Generate a unique ID for the file
            file_id = str(uuid.uuid4())
            
            # Store the file path with an expiration time (30 minutes from now)
            expiration = time.time() + (30 * 60)  # 30 minutes
            temp_files[file_id] = (temp_filepath, expiration)
            
            # Clean up expired files
            _cleanup_expired_files()
            
            if return_audio:
                return send_file(
                    temp_filepath,
                    mimetype="audio/mpeg",
                    as_attachment=True,
                    download_name=f"narration_{file_id}.mp3"
                )
            else:
                return jsonify({
                    "success": True,
                    "price_data": price_data,
                    "narration_text": narration_text,
                    "file_id": file_id,
                    "expires_in_seconds": 30 * 60
                })
                
        except Exception as e:
            # Clean up the temporary file if narration failed
            if os.path.exists(temp_filepath):
                os.remove(temp_filepath)
            raise e
    
    except Exception as e:
        logger.error(f"Error in narrate_crypto_price endpoint: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


def _cleanup_expired_files():
    """Clean up expired temporary files."""
    current_time = time.time()
    expired_ids = []
    
    for file_id, (filepath, expiration) in temp_files.items():
        if current_time > expiration:
            expired_ids.append(file_id)
            if os.path.exists(filepath):
                try:
                    os.remove(filepath)
                    logger.debug(f"Removed expired audio file: {filepath}")
                except Exception as e:
                    logger.error(f"Error removing expired file {filepath}: {e}")
    
    for file_id in expired_ids:
        del temp_files[file_id]


@app.route('/', methods=['GET'])
def index():
    """Serve the main HTML interface."""
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/logo.svg')
def logo():
    """Serve the logo file."""
    return send_from_directory(app.static_folder, 'logo.svg')


@app.route('/<path:filename>')
def static_files(filename):
    """Serve static files for React app with SPA routing support."""
    try:
        # Try to serve the requested file
        return send_from_directory(app.static_folder, filename)
    except Exception:
        # If file doesn't exist, serve index.html for client-side routing
        return send_from_directory(app.static_folder, 'index.html')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="QuantLink FREN Narrator Web API")
    parser.add_argument('--host', type=str, default='127.0.0.1', help='Host to run the server on')
    parser.add_argument('--port', type=int, default=5000, help='Port to run the server on')
    parser.add_argument('--debug', action='store_true', help='Run in debug mode')
    
    args = parser.parse_args()
    
    if args.debug:
        app.logger.setLevel(logging.DEBUG)
        logger.setLevel(logging.DEBUG)
    
    # Inform user about the web server
    print(f"Starting QuantLink FREN Narrator Web API on http://{args.host}:{args.port}")
    print("Available endpoints:")
    print("  GET  /api/health                  - Health check")
    print("  GET  /api/crypto/price            - Get cryptocurrency price")
    print("  GET  /api/crypto/prices           - Get multiple cryptocurrency prices")
    print("  POST /api/narrator/text           - Narrate custom text")
    print("  GET  /api/narrator/audio/<file_id> - Get audio file by ID")
    print("  POST /api/narrator/crypto         - Narrate cryptocurrency price")
    
    # Run the Flask app
    app.run(host=args.host, port=args.port, debug=args.debug) 