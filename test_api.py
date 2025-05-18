#!/usr/bin/env python3
"""
Test script for the QuantLink FREN Narrator Web API.

This script tests all the available endpoints to ensure they are working correctly.
It's a simple way to verify the functionality of the API server.

Usage:
  python test_api.py [--host HOST] [--port PORT]
"""

import argparse
import requests
import json
import time
import sys


def print_success(message):
    """Print a success message with green color."""
    print(f"\033[92m✓ {message}\033[0m")


def print_error(message):
    """Print an error message with red color."""
    print(f"\033[91m✗ {message}\033[0m")


def print_info(message):
    """Print an info message with blue color."""
    print(f"\033[94m→ {message}\033[0m")


def print_header(message):
    """Print a header message with yellow background."""
    print(f"\033[43m\033[30m {message} \033[0m")


def test_health_endpoint(base_url):
    """Test the health check endpoint."""
    print_header("Testing Health Check Endpoint")
    
    try:
        response = requests.get(f"{base_url}/api/health", timeout=5)
        response.raise_for_status()
        data = response.json()
        
        if data.get("status") == "healthy":
            print_success("Health check passed")
            return True
        else:
            print_error(f"Health check failed: {data}")
            return False
    except Exception as e:
        print_error(f"Health check failed with error: {str(e)}")
        return False


def test_crypto_price_endpoint(base_url):
    """Test the cryptocurrency price endpoint."""
    print_header("Testing Cryptocurrency Price Endpoint")
    
    # Test basic price
    try:
        response = requests.get(f"{base_url}/api/crypto/price?crypto=bitcoin&currency=usd", timeout=5)
        response.raise_for_status()
        data = response.json()
        
        if data.get("success") and data.get("current_price") is not None:
            print_success("Basic price fetch passed")
        else:
            print_error(f"Basic price fetch failed: {data}")
            return False
    except Exception as e:
        print_error(f"Basic price fetch failed with error: {str(e)}")
        return False
    
    # Test price with 24h change
    try:
        response = requests.get(
            f"{base_url}/api/crypto/price?crypto=bitcoin&currency=usd&with_24h_change=true", 
            timeout=5
        )
        response.raise_for_status()
        data = response.json()
        
        if (data.get("success") and data.get("current_price") is not None and 
                "price_change_24h" in data):
            print_success("Price with 24h change fetch passed")
            return True
        else:
            print_error(f"Price with 24h change fetch failed: {data}")
            return False
    except Exception as e:
        print_error(f"Price with 24h change fetch failed with error: {str(e)}")
        return False


def test_multiple_prices_endpoint(base_url):
    """Test the multiple cryptocurrency prices endpoint."""
    print_header("Testing Multiple Cryptocurrency Prices Endpoint")
    
    try:
        response = requests.get(
            f"{base_url}/api/crypto/prices?cryptos=bitcoin,ethereum,solana&currency=usd", 
            timeout=5
        )
        response.raise_for_status()
        data = response.json()
        
        if (data.get("success") and 
                isinstance(data.get("prices"), dict) and 
                len(data.get("prices", {})) == 3):
            print_success("Multiple prices fetch passed")
            return True
        else:
            print_error(f"Multiple prices fetch failed: {data}")
            return False
    except Exception as e:
        print_error(f"Multiple prices fetch failed with error: {str(e)}")
        return False


def test_narrate_text_endpoint(base_url):
    """Test the narrate text endpoint."""
    print_header("Testing Narrate Text Endpoint")
    
    try:
        payload = {
            "text": "Hello world, this is a test of the narration API.",
            "return_audio": False
        }
        
        response = requests.post(
            f"{base_url}/api/narrator/text", 
            json=payload,
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        
        if data.get("success") and "file_id" in data:
            file_id = data["file_id"]
            print_success(f"Text narration passed, got file ID: {file_id}")
            return file_id
        else:
            print_error(f"Text narration failed: {data}")
            return None
    except Exception as e:
        print_error(f"Text narration failed with error: {str(e)}")
        return None


def test_get_audio_file_endpoint(base_url, file_id):
    """Test the get audio file endpoint."""
    print_header("Testing Get Audio File Endpoint")
    
    if not file_id:
        print_info("Skipping audio file fetch because no file ID is available")
        return True
    
    try:
        response = requests.head(
            f"{base_url}/api/narrator/audio/{file_id}", 
            timeout=5
        )
        response.raise_for_status()
        
        content_type = response.headers.get("Content-Type")
        if content_type and "audio" in content_type:
            print_success(f"Audio file fetch passed with content type: {content_type}")
            return True
        else:
            print_error(f"Audio file fetch returned unexpected content type: {content_type}")
            return False
    except Exception as e:
        print_error(f"Audio file fetch failed with error: {str(e)}")
        return False


def test_narrate_crypto_endpoint(base_url):
    """Test the narrate cryptocurrency price endpoint."""
    print_header("Testing Narrate Cryptocurrency Price Endpoint")
    
    try:
        payload = {
            "crypto": "bitcoin",
            "currency": "usd",
            "with_24h_change": True,
            "return_audio": False
        }
        
        response = requests.post(
            f"{base_url}/api/narrator/crypto", 
            json=payload,
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        
        if (data.get("success") and 
                "file_id" in data and 
                "narration_text" in data and 
                "price_data" in data):
            print_success(f"Cryptocurrency narration passed")
            return True
        else:
            print_error(f"Cryptocurrency narration failed: {data}")
            return False
    except Exception as e:
        print_error(f"Cryptocurrency narration failed with error: {str(e)}")
        return False


def main():
    """Main function to run all tests."""
    parser = argparse.ArgumentParser(description="Test the QuantLink FREN Narrator Web API")
    parser.add_argument('--host', type=str, default='localhost', help='Host of the API server')
    parser.add_argument('--port', type=int, default=5001, help='Port of the API server')
    
    args = parser.parse_args()
    base_url = f"http://{args.host}:{args.port}"
    
    print_info(f"Testing API at {base_url}")
    print_info("==================================")
    
    # Track overall test success
    all_tests_passed = True
    
    # Test health endpoint
    if not test_health_endpoint(base_url):
        all_tests_passed = False
    
    print("\n")  # Add some spacing
    
    # Test crypto price endpoint
    if not test_crypto_price_endpoint(base_url):
        all_tests_passed = False
    
    print("\n")  # Add some spacing
    
    # Test multiple prices endpoint
    if not test_multiple_prices_endpoint(base_url):
        all_tests_passed = False
    
    print("\n")  # Add some spacing
    
    # Test narrate text endpoint
    file_id = test_narrate_text_endpoint(base_url)
    if not file_id:
        all_tests_passed = False
    
    print("\n")  # Add some spacing
    
    # Test get audio file endpoint
    if not test_get_audio_file_endpoint(base_url, file_id):
        all_tests_passed = False
    
    print("\n")  # Add some spacing
    
    # Test narrate crypto endpoint
    if not test_narrate_crypto_endpoint(base_url):
        all_tests_passed = False
    
    print("\n")  # Add some spacing
    
    # Print summary
    print_header("Test Summary")
    if all_tests_passed:
        print_success("All tests passed successfully!")
        return 0
    else:
        print_error("Some tests failed. See above for details.")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 