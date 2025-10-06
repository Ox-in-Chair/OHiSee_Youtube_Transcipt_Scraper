# Test Suite

Automated test suite for YouTube Transcript Scraper.

## Overview

This directory contains unit tests and integration tests for the application. All tests use **pytest** framework.

## Test Files

### 1. `test_basic.py` - Core Functionality Tests

**Purpose**: Validate basic imports and module initialization
**Runtime**: ~2 seconds

```bash
python -m pytest tests/test_basic.py -v
```

**What it tests**:

- ✅ Module imports (scraper_engine, search_optimizer, config)
- ✅ Filter options configuration
- ✅ Config class initialization
- ✅ Scraper engine class existence
- ✅ Search optimizer module

### 2. `test_app.py` - Application Integration Tests

**Purpose**: Test GUI and core application features
**Runtime**: ~5 seconds

```bash
python -m pytest tests/test_app.py -v
```

**What it tests**:

- ✅ Application imports
- ✅ Config manager (save/load API key)
- ✅ Scraper search functionality
- ✅ AI optimization infrastructure
- ✅ GUI initialization (headless)

### 3. `test_scrolling.py` - Transcript Extraction Tests

**Purpose**: Validate scrolling logic for long transcripts
**Runtime**: ~2 seconds

```bash
python -m pytest tests/test_scrolling.py -v
```

**What it tests**:

- ✅ Scrolling function exists
- ✅ Transcript extraction handles lazy-loaded content

### 4. `test_token_efficiency.py` - Token Efficiency Validation

**Purpose**: Validate AI summarization cost/benefit analysis
**Runtime**: ~5 seconds

```bash
python -m pytest tests/test_token_efficiency.py -v
```

**What it tests**:

- ✅ Token savings for short transcripts (99.0% reduction)
- ✅ Token savings for long transcripts (97.8% reduction)
- ✅ Cost calculations per video ($0.0011)
- ✅ Batch processing cost (100 videos: $0.11)
- ✅ Research handover scenario (50 videos: 97.8% savings)
- ✅ Short transcript skip threshold

## Running All Tests

```bash
# Run full test suite
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html

# Run specific test
python -m pytest tests/test_basic.py::test_imports -v
```

## Test Results

**Current Status**: ✅ 18/18 tests passing

```
tests/test_app.py ..................... 5 passed
tests/test_basic.py ................... 5 passed
tests/test_scrolling.py ............... 1 passed
tests/test_token_efficiency.py ........ 7 passed
```

## Quality Gates

All tests must pass before committing code:

```bash
# 1. Run tests
python -m pytest tests/ -v

# 2. Check linting
python -m flake8 src/ --max-line-length=120 --extend-ignore=E203,W503,E501

# 3. Format code
python -m black src/ tests/ scripts/ --line-length 100

# 4. Verify all pass
echo "All quality gates passed ✅"
```

## Troubleshooting

**Issue**: "Module not found"
**Solution**: Ensure you're in the project root directory

**Issue**: Tests fail with import errors
**Solution**: Install dependencies: `pip install -r requirements.txt`

**Issue**: Token efficiency tests fail
**Solution**: These are mathematical validations - if failing, check test logic

## CI/CD Integration

These tests are designed to run in CI/CD pipelines:

```yaml
# GitHub Actions example
- name: Run tests
  run: |
    pip install -r requirements.txt
    python -m pytest tests/ -v --tb=short
```

## Test Coverage

Target coverage: **≥80%** for core modules

```bash
python -m pytest tests/ --cov=src --cov-report=term-missing
```

---

**For development testing**: Run `python -m pytest tests/ -v` before each commit.
