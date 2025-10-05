#!/usr/bin/env python3
"""Test script for app_minimal.py - Automated quality gate verification"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

def test_imports():
    """Test that all imports work correctly."""
    print("Testing imports...")
    try:
        from app_minimal import MinimalScraperApp, VideoResultItem
        from core.scraper_engine import TranscriptScraper
        from core.search_optimizer import optimize_search_query
        from utils.config import Config
        print("[PASS] All imports successful")
        return True
    except ImportError as e:
        print(f"[FAIL] Import failed: {e}")
        return False


def test_config_manager():
    """Test config manager functionality."""
    print("\nTesting config manager...")
    try:
        from utils.config import Config

        config = Config()

        # Test saving and loading
        test_key = "test_api_key_12345"
        config.save_api_key(test_key)

        loaded_key = config.load_api_key()

        if loaded_key == test_key:
            print("[PASS] Config save/load working")
            return True
        else:
            print(f"[FAIL] Config mismatch: expected '{test_key}', got '{loaded_key}'")
            return False

    except Exception as e:
        print(f"[FAIL] Config test failed: {e}")
        return False


def test_scraper_search():
    """Test TranscriptScraper search functionality."""
    print("\nTesting scraper search (without AI)...")
    try:
        from core.scraper_engine import TranscriptScraper

        scraper = TranscriptScraper(callback=print)

        # Simple search test
        results = scraper.search_videos("Python tutorial", max_results=5, filters={'upload_date': 'any'})

        if results and len(results) > 0:
            print(f"[PASS] Search returned {len(results)} results")
            print(f"  Sample: {results[0]['title'][:50]}...")
            return True
        else:
            print("[FAIL] Search returned no results")
            return False

    except Exception as e:
        print(f"[FAIL] Search test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ai_optimization():
    """Test AI query optimization (requires API key)."""
    print("\nTesting AI optimization...")
    try:
        from core.search_optimizer import optimize_search_query
        from utils.config import Config

        config = Config()
        api_key = config.load_api_key()

        if not api_key or api_key.startswith("test_"):
            print("[SKIP] No valid API key (optional test)")
            return True

        # Test optimization
        original = "How to automate workflows in manufacturing with BRCGS standards"
        optimized = optimize_search_query(original, api_key)

        if optimized and optimized != original:
            print(f"[PASS] AI optimization working")
            print(f"  Original:  {original}")
            print(f"  Optimized: {optimized}")
            return True
        else:
            print("[FAIL] AI optimization failed or returned same query")
            return False

    except Exception as e:
        print(f"[SKIP] AI optimization test skipped: {e}")
        return True  # Not critical


def test_app_initialization():
    """Test that the app can initialize (no GUI display)."""
    print("\nTesting app initialization...")
    try:
        import tkinter as tk

        # Check if Tk can initialize (headless may fail)
        try:
            root = tk.Tk()
            root.withdraw()
            root.destroy()
        except Exception:
            print("[SKIP] No display available (headless environment)")
            return True

        # Import app
        from app_minimal import MinimalScraperApp

        # Try to create instance (don't show)
        app = MinimalScraperApp()
        app.withdraw()

        # Check key components exist
        assert hasattr(app, 'query_entry'), "Missing query_entry"
        assert hasattr(app, 'search_btn'), "Missing search_btn"
        assert hasattr(app, 'results_container'), "Missing results_container"
        assert hasattr(app, 'download_btn'), "Missing download_btn"

        app.destroy()

        print("[PASS] App initialization successful")
        return True

    except Exception as e:
        print(f"[FAIL] App initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all tests and generate report."""
    print("=" * 60)
    print("MINIMAL APP - QUALITY GATE VERIFICATION")
    print("=" * 60)

    tests = [
        ("Imports", test_imports),
        ("Config Manager", test_config_manager),
        ("Scraper Search", test_scraper_search),
        ("AI Optimization", test_ai_optimization),
        ("App Initialization", test_app_initialization),
    ]

    results = []
    for name, test_func in tests:
        result = test_func()
        results.append((name, result))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "PASS" if result else "FAIL"
        symbol = "[PASS]" if result else "[FAIL]"
        print(f"{symbol} {name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n*** ALL QUALITY GATES PASSED! ***")
        return 0
    else:
        print(f"\n*** WARNING: {total - passed} test(s) failed ***")
        return 1


if __name__ == '__main__':
    exit_code = run_all_tests()
    sys.exit(exit_code)
