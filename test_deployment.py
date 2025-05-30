#!/usr/bin/env python3
"""
Deployment testing script for QuantLink FREN Narrator Web API.
Tests various endpoints and functionality in a deployed environment.
"""

import requests
import time
import sys
import os
from urllib.parse import urljoin

def test_health_endpoint(base_url):
    """Test the health check endpoint."""
    print("🧪 Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/api/health", timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get("status") == "healthy":
            print("✅ Health endpoint working correctly")
            return True
        else:
            print(f"❌ Health endpoint returned unexpected status: {data}")
            return False
            
    except Exception as e:
        print(f"❌ Health endpoint failed: {e}")
        return False

def test_crypto_price_endpoint(base_url):
    """Test the crypto price endpoint."""
    print("🧪 Testing crypto price endpoint...")
    try:
        response = requests.get(f"{base_url}/api/crypto/price?crypto=bitcoin&currency=usd", timeout=15)
        response.raise_for_status()
        data = response.json()
        
        if data.get("success") and "current_price" in data:
            print(f"✅ Crypto price endpoint working: Bitcoin = ${data['current_price']:,.2f}")
            return True
        else:
            print(f"❌ Crypto price endpoint returned unexpected data: {data}")
            return False
            
    except Exception as e:
        print(f"❌ Crypto price endpoint failed: {e}")
        return False

def test_audio_system():
    """Test that audio system can be initialized without errors."""
    print("🧪 Testing audio system compatibility...")
    try:
        # Set dummy audio driver for testing
        os.environ['SDL_AUDIODRIVER'] = 'dummy'
        
        import pygame
        pygame.mixer.init()
        print("✅ Audio system initialized successfully with dummy driver")
        return True
        
    except Exception as e:
        print(f"❌ Audio system test failed: {e}")
        return False

def test_narration_endpoint(base_url):
    """Test the text narration endpoint."""
    print("🧪 Testing narration endpoint...")
    try:
        payload = {
            "text": "This is a test narration for deployment verification.",
            "lang": "en",
            "slow": False,
            "return_audio": True
        }
        
        response = requests.post(
            f"{base_url}/api/narrator/text", 
            json=payload, 
            timeout=30
        )
        response.raise_for_status()
        
        # Check if we got audio data back
        content_type = response.headers.get('content-type', '')
        if 'audio' in content_type and len(response.content) > 0:
            print(f"✅ Narration endpoint working: Generated {len(response.content)} bytes of audio")
            return True
        else:
            print(f"❌ Narration endpoint returned unexpected content type: {content_type}")
            return False
            
    except Exception as e:
        print(f"❌ Narration endpoint failed: {e}")
        return False

def test_crypto_narration_endpoint(base_url):
    """Test the crypto narration endpoint."""
    print("🧪 Testing crypto narration endpoint...")
    try:
        payload = {
            "crypto": "bitcoin",
            "currency": "usd",
            "with_24h_change": True,
            "return_audio": True
        }
        
        response = requests.post(
            f"{base_url}/api/narrator/crypto", 
            json=payload, 
            timeout=30
        )
        response.raise_for_status()
        
        # Check if we got audio data back
        content_type = response.headers.get('content-type', '')
        if 'audio' in content_type and len(response.content) > 0:
            print(f"✅ Crypto narration endpoint working: Generated {len(response.content)} bytes of audio")
            return True
        else:
            print(f"❌ Crypto narration endpoint returned unexpected content type: {content_type}")
            return False
            
    except Exception as e:
        print(f"❌ Crypto narration endpoint failed: {e}")
        return False

def test_web_interface(base_url):
    """Test that the web interface is accessible."""
    print("🧪 Testing web interface...")
    try:
        response = requests.get(base_url, timeout=10)
        response.raise_for_status()
        
        content = response.text
        if "QuantLink FREN Narrator" in content and "API_BASE_URL" in content:
            print("✅ Web interface accessible and properly configured")
            return True
        else:
            print("❌ Web interface missing expected content")
            return False
            
    except Exception as e:
        print(f"❌ Web interface test failed: {e}")
        return False

def main():
    """Run all deployment tests."""
    if len(sys.argv) < 2:
        print("Usage: python test_deployment.py <base_url>")
        print("Example: python test_deployment.py http://localhost:8000")
        print("Example: python test_deployment.py https://your-app.onrender.com")
        sys.exit(1)
    
    base_url = sys.argv[1].rstrip('/')
    
    print("🚀 QuantLink FREN Narrator - Deployment Test")
    print("=" * 50)
    print(f"📍 Testing deployment at: {base_url}")
    print()
    
    tests = [
        lambda: test_audio_system(),
        lambda: test_health_endpoint(base_url),
        lambda: test_crypto_price_endpoint(base_url),
        lambda: test_web_interface(base_url),
        lambda: test_narration_endpoint(base_url),
        lambda: test_crypto_narration_endpoint(base_url),
    ]
    
    passed = 0
    total = len(tests)
    
    for i, test in enumerate(tests, 1):
        print(f"[{i}/{total}]", end=" ")
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All deployment tests passed!")
        print("✅ Your deployment is working correctly.")
        return 0
    else:
        print("❌ Some deployment tests failed.")
        print("🔍 Check the logs above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 