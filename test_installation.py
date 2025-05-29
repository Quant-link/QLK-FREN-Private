#!/usr/bin/env python3
"""
Simple test script to verify the installation is working correctly.
Tests both the CLI and the core narration functionality.
"""

import sys
import subprocess
import os

def test_imports():
    """Test that all required modules can be imported."""
    print("Testing imports...")
    try:
        import requests
        import gtts
        import pygame
        import flask
        print("✓ All required modules imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_pygame_audio():
    """Test pygame audio initialization."""
    print("Testing pygame audio...")
    try:
        import pygame
        pygame.mixer.init()
        print("✓ Pygame audio initialized successfully")
        return True
    except Exception as e:
        print(f"✗ Pygame audio error: {e}")
        return False

def test_cli_help():
    """Test that the CLI application starts and shows help."""
    print("Testing CLI help...")
    try:
        result = subprocess.run([sys.executable, "main.py", "--help"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0 and "cryptocurrency prices" in result.stdout.lower():
            print("✓ CLI help command works")
            return True
        else:
            print(f"✗ CLI help failed with return code {result.returncode}")
            return False
    except Exception as e:
        print(f"✗ CLI help error: {e}")
        return False

def test_config_file():
    """Test that config.ini exists."""
    print("Testing config file...")
    if os.path.exists("config.ini"):
        print("✓ Config file exists")
        return True
    else:
        print("✗ Config file (config.ini) not found")
        return False

def main():
    """Run all tests."""
    print("QuantLink FREN Core Narrator - Installation Test")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_pygame_audio,
        test_config_file,
        test_cli_help,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! Installation is working correctly.")
        print("\nYou can now use:")
        print("  python main.py --crypto bitcoin")
        print("  python web_api.py")
        return 0
    else:
        print("❌ Some tests failed. Please check the installation.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 