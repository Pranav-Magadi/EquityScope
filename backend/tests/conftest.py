import pytest
import os
from fastapi.testclient import TestClient
from unittest.mock import patch

# Set test environment
os.environ["TESTING"] = "1"

from app.main import app

@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    with TestClient(app) as client:
        yield client

@pytest.fixture
def mock_yfinance():
    """Mock yfinance for consistent testing."""
    with patch('yfinance.Ticker') as mock_ticker:
        # Mock ticker data
        mock_info = {
            'longName': 'Test Company Limited',
            'sector': 'Technology',
            'industry': 'Software',
            'marketCap': 1000000000,
            'currency': 'USD',
            'exchange': 'NASDAQ'
        }
        
        mock_history = {
            'Close': [100.0, 105.0, 102.0],
            'Volume': [1000000, 1200000, 800000]
        }
        
        mock_ticker.return_value.info = mock_info
        mock_ticker.return_value.history.return_value = mock_history
        mock_ticker.return_value.financials = None
        mock_ticker.return_value.balance_sheet = None
        mock_ticker.return_value.cashflow = None
        
        yield mock_ticker

@pytest.fixture
def sample_company_data():
    """Sample company analysis data for testing."""
    return {
        "company_info": {
            "ticker": "TEST.NS",
            "name": "Test Company Limited",
            "sector": "Technology",
            "industry": "Software",
            "market_cap": 1000000000,
            "current_price": 100.0,
            "currency": "INR",
            "exchange": "NSI"
        },
        "stock_price": {
            "current_price": 100.0,
            "change": 5.0,
            "change_percent": 5.26,
            "volume": 1000000,
            "market_cap": 1000000000,
            "pe_ratio": 20.0,
            "pb_ratio": 2.5
        }
    }

@pytest.fixture
def sample_dcf_request():
    """Sample DCF request data for testing."""
    return {
        "revenue_growth_rate": 10.0,
        "ebitda_margin": 15.0,
        "tax_rate": 25.0,
        "wacc": 12.0,
        "terminal_growth_rate": 4.0
    }