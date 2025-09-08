import pytest
from unittest.mock import patch
import yfinance as yf

class TestCompanyAPI:
    """Test cases for company analysis API endpoints."""
    
    def test_health_endpoint(self, client):
        """Test the health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "qualitative-edge-api"
        assert data["version"] == "2.0.0"
    
    def test_root_endpoint(self, client):
        """Test the root endpoint returns API information."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "endpoints" in data
        assert data["version"] == "2.0.0"
    
    @pytest.mark.asyncio
    async def test_company_analysis_success(self, client, mock_yfinance):
        """Test successful company analysis."""
        response = client.get("/api/company/RELIANCE.NS")
        assert response.status_code == 200
        
        data = response.json()
        
        # Check required fields
        assert "company_info" in data
        assert "stock_price" in data
        assert "swot" in data
        assert "news_sentiment" in data
        assert "market_landscape" in data
        assert "employee_sentiment" in data
        
        # Check company info structure
        company_info = data["company_info"]
        assert "ticker" in company_info
        assert "name" in company_info
        assert "sector" in company_info
        assert "industry" in company_info
        
        # Check stock price structure
        stock_price = data["stock_price"]
        assert "current_price" in stock_price
        assert "change" in stock_price
        assert "change_percent" in stock_price
        assert "volume" in stock_price
    
    def test_company_analysis_invalid_ticker(self, client):
        """Test company analysis with invalid ticker."""
        response = client.get("/api/company/INVALID")
        assert response.status_code == 404
        
        data = response.json()
        assert data["error"] is True
        assert "not found" in data["message"].lower()
    
    @pytest.mark.asyncio
    async def test_company_analysis_network_error(self, client):
        """Test company analysis with network error."""
        with patch('yfinance.Ticker') as mock_ticker:
            mock_ticker.side_effect = Exception("Network error")
            
            response = client.get("/api/company/TEST.NS")
            assert response.status_code == 500
            
            data = response.json()
            assert data["error"] is True
    
    def test_data_sources_endpoint(self, client):
        """Test data sources information endpoint."""
        response = client.get("/api/data-sources")
        assert response.status_code == 200
        
        data = response.json()
        assert "kite_connect" in data
        assert "yfinance" in data
        assert "ai_analysis" in data
        
        # Check yfinance configuration
        yfinance_info = data["yfinance"]
        assert yfinance_info["authentication_required"] is False
        assert "features" in yfinance_info
        assert "endpoints" in yfinance_info
    
    @pytest.mark.parametrize("ticker", [
        "RELIANCE.NS",
        "TCS.NS", 
        "HDFCBANK.NS",
        "INFY.NS"
    ])
    def test_company_analysis_multiple_tickers(self, client, mock_yfinance, ticker):
        """Test company analysis with multiple valid NSE tickers."""
        response = client.get(f"/api/company/{ticker}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["company_info"]["ticker"] == ticker
    
    def test_company_analysis_response_time(self, client, mock_yfinance):
        """Test that company analysis responds within reasonable time."""
        import time
        
        start_time = time.time()
        response = client.get("/api/company/RELIANCE.NS")
        end_time = time.time()
        
        response_time = end_time - start_time
        assert response_time < 5.0  # Should respond within 5 seconds
        assert response.status_code == 200
    
    def test_company_analysis_concurrent_requests(self, client, mock_yfinance):
        """Test handling of concurrent requests."""
        import threading
        import time
        
        results = []
        
        def make_request():
            response = client.get("/api/company/RELIANCE.NS")
            results.append(response.status_code)
        
        # Create multiple threads
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All requests should succeed
        assert all(status == 200 for status in results)
        assert len(results) == 5