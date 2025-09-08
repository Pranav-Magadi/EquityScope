import pytest
from unittest.mock import patch, MagicMock
from app.services.data_service import DataService

class TestDataService:
    """Test cases for the data service."""
    
    @pytest.fixture
    def data_service(self):
        """Create a DataService instance for testing."""
        return DataService()
    
    @pytest.mark.asyncio
    async def test_get_company_info_success(self, data_service):
        """Test successful company info retrieval."""
        with patch('yfinance.Ticker') as mock_ticker:
            mock_ticker.return_value.info = {
                'longName': 'Test Company Limited',
                'sector': 'Technology',
                'industry': 'Software',
                'marketCap': 1000000000,
                'currency': 'USD'
            }
            
            result = await data_service.get_company_info("TEST.NS")
            
            assert result is not None
            assert result["name"] == "Test Company Limited"
            assert result["sector"] == "Technology"
            assert result["industry"] == "Software"
            assert result["market_cap"] == 1000000000
            assert result["currency"] == "USD"
    
    @pytest.mark.asyncio
    async def test_get_company_info_missing_data(self, data_service):
        """Test company info retrieval with missing data."""
        with patch('yfinance.Ticker') as mock_ticker:
            mock_ticker.return_value.info = {}
            
            result = await data_service.get_company_info("TEST.NS")
            
            # Should handle missing data gracefully
            assert result is not None
            assert result["name"] == "TEST.NS"  # Fallback to ticker
    
    @pytest.mark.asyncio
    async def test_get_stock_price_success(self, data_service):
        """Test successful stock price retrieval."""
        with patch('yfinance.Ticker') as mock_ticker:
            mock_history = MagicMock()
            mock_history.iloc = MagicMock()
            mock_history.iloc[-1] = {
                'Close': 100.0,
                'Volume': 1000000
            }
            mock_history.iloc[-2] = {
                'Close': 95.0
            }
            
            mock_ticker.return_value.history.return_value = mock_history
            mock_ticker.return_value.info = {'marketCap': 1000000000}
            
            result = await data_service.get_stock_price("TEST.NS")
            
            assert result is not None
            assert result["current_price"] == 100.0
            assert result["volume"] == 1000000
            assert result["change"] == 5.0
            assert result["change_percent"] == pytest.approx(5.26, rel=1e-2)
    
    @pytest.mark.asyncio
    async def test_get_financial_data_success(self, data_service):
        """Test successful financial data retrieval."""
        with patch('yfinance.Ticker') as mock_ticker:
            # Mock financial statements
            mock_financials = MagicMock()
            mock_financials.columns = [2023, 2022, 2021]
            mock_financials.loc = {
                'Total Revenue': [1000000000, 900000000, 800000000],
                'EBITDA': [200000000, 180000000, 160000000]
            }
            
            mock_balance_sheet = MagicMock()
            mock_balance_sheet.columns = [2023, 2022, 2021]
            mock_balance_sheet.loc = {
                'Total Debt': [100000000, 120000000, 140000000],
                'Cash And Cash Equivalents': [50000000, 40000000, 30000000]
            }
            
            mock_ticker.return_value.financials = mock_financials
            mock_ticker.return_value.balance_sheet = mock_balance_sheet
            mock_ticker.return_value.info = {'sharesOutstanding': 100000000}
            
            result = await data_service.get_financial_data("TEST.NS")
            
            assert result is not None
            assert result["ticker"] == "TEST.NS"
            assert len(result["years"]) == 3
            assert len(result["revenue"]) == 3
            assert result["revenue"][0] == 1000000000  # Most recent year
    
    @pytest.mark.asyncio
    async def test_get_financial_data_missing_statements(self, data_service):
        """Test financial data retrieval with missing statements."""
        with patch('yfinance.Ticker') as mock_ticker:
            mock_ticker.return_value.financials = None
            mock_ticker.return_value.balance_sheet = None
            mock_ticker.return_value.cashflow = None
            
            result = await data_service.get_financial_data("TEST.NS")
            
            # Should return minimal structure even with missing data
            assert result is not None
            assert result["ticker"] == "TEST.NS"
            assert isinstance(result["years"], list)
            assert isinstance(result["revenue"], list)
    
    @pytest.mark.asyncio
    async def test_service_error_handling(self, data_service):
        """Test service error handling."""
        with patch('yfinance.Ticker') as mock_ticker:
            mock_ticker.side_effect = Exception("Network error")
            
            with pytest.raises(Exception):
                await data_service.get_company_info("TEST.NS")
    
    @pytest.mark.asyncio
    async def test_ticker_validation(self, data_service):
        """Test ticker validation."""
        # Test various ticker formats
        valid_tickers = ["RELIANCE.NS", "TCS.NS", "AAPL", "MSFT"]
        invalid_tickers = ["", "   ", "INVALID_TICKER_TOO_LONG"]
        
        for ticker in valid_tickers:
            with patch('yfinance.Ticker'):
                result = await data_service.get_company_info(ticker)
                assert result is not None
        
        for ticker in invalid_tickers:
            with pytest.raises((ValueError, Exception)):
                await data_service.get_company_info(ticker)
    
    @pytest.mark.asyncio
    async def test_caching_behavior(self, data_service):
        """Test data caching behavior if implemented."""
        with patch('yfinance.Ticker') as mock_ticker:
            mock_ticker.return_value.info = {'longName': 'Test Company'}
            
            # First call
            result1 = await data_service.get_company_info("TEST.NS")
            
            # Second call (should use cache if implemented)
            result2 = await data_service.get_company_info("TEST.NS")
            
            assert result1 == result2
            # In a real caching implementation, we would assert that
            # yfinance.Ticker was only called once