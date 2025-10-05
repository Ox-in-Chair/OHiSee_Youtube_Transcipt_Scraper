#!/usr/bin/env python3
"""Basic pytest tests for YouTube Transcript Scraper"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def test_imports():
    """Test that core modules can be imported"""
    from core import scraper_engine, search_optimizer
    from utils import config, filters, prompts

    assert scraper_engine is not None
    assert search_optimizer is not None
    assert config is not None
    assert filters is not None
    assert prompts is not None


def test_filter_options():
    """Test that filter options are defined correctly"""
    from utils.filters import UPLOAD_DATE_OPTIONS, SORT_BY_OPTIONS

    assert len(UPLOAD_DATE_OPTIONS) > 0
    assert len(SORT_BY_OPTIONS) > 0
    assert "Last 7 days" in UPLOAD_DATE_OPTIONS
    assert "Relevance" in SORT_BY_OPTIONS


def test_config_class():
    """Test Config class exists and has required methods"""
    from utils.config import Config

    config = Config()
    assert hasattr(config, "load_api_key")
    assert hasattr(config, "save_api_key")


def test_scraper_engine_class():
    """Test TranscriptScraper class structure"""
    from core.scraper_engine import TranscriptScraper

    # Test class can be instantiated with required params
    scraper = TranscriptScraper(output_dir="./test_output")
    assert scraper.output_dir == "./test_output"
    assert hasattr(scraper, "scrape")


def test_search_optimizer_exists():
    """Test search optimizer function exists"""
    from core.search_optimizer import optimize_search_query

    assert callable(optimize_search_query)
