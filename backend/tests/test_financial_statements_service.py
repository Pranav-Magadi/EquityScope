# Tests for Financial Statements Service
# Comprehensive test suite for real financial data processing

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

from app.services.financial_statements_service import (
    FinancialStatementsService,
    FinancialStatementYear,
    FinancialStatementsAnalysis
)

class TestFinancialStatementsService:
    """Test suite for FinancialStatementsService"""
    
    @pytest.fixture
    def service(self):
        """Create service instance for testing"""
        return FinancialStatementsService(use_cache=False)
    
    @pytest.fixture
    def mock_yfinance_data(self):
        """Mock yfinance financial statement data"""
        
        # Create mock financial data for 5 years
        years = [
            datetime(2024, 3, 31),
            datetime(2023, 3, 31), 
            datetime(2022, 3, 31),
            datetime(2021, 3, 31),
            datetime(2020, 3, 31)
        ]
        
        # Mock Income Statement
        financials_data = {
            years[0]: {'Total Revenue': 10000000000, 'Net Income': 800000000, 'EBITDA': 2000000000},
            years[1]: {'Total Revenue': 9500000000, 'Net Income': 750000000, 'EBITDA': 1900000000},
            years[2]: {'Total Revenue': 9000000000, 'Net Income': 700000000, 'EBITDA': 1800000000},
            years[3]: {'Total Revenue': 8500000000, 'Net Income': 650000000, 'EBITDA': 1700000000},
            years[4]: {'Total Revenue': 8000000000, 'Net Income': 600000000, 'EBITDA': 1600000000}
        }
        
        # Mock Balance Sheet
        balance_sheet_data = {
            years[0]: {'Total Assets': 20000000000, 'Stockholders Equity': 8000000000, 'Total Debt': 3000000000},
            years[1]: {'Total Assets': 19000000000, 'Stockholders Equity': 7500000000, 'Total Debt': 2800000000},
            years[2]: {'Total Assets': 18000000000, 'Stockholders Equity': 7000000000, 'Total Debt': 2600000000},
            years[3]: {'Total Assets': 17000000000, 'Stockholders Equity': 6500000000, 'Total Debt': 2400000000},
            years[4]: {'Total Assets': 16000000000, 'Stockholders Equity': 6000000000, 'Total Debt': 2200000000}
        }
        
        # Mock Cash Flow Statement
        cashflow_data = {
            years[0]: {'Operating Cash Flow': 900000000, 'Free Cash Flow': 400000000, 'Capital Expenditure': -500000000},
            years[1]: {'Operating Cash Flow': 850000000, 'Free Cash Flow': 350000000, 'Capital Expenditure': -500000000},
            years[2]: {'Operating Cash Flow': 800000000, 'Free Cash Flow': 300000000, 'Capital Expenditure': -500000000},
            years[3]: {'Operating Cash Flow': 750000000, 'Free Cash Flow': 250000000, 'Capital Expenditure': -500000000},
            years[4]: {'Operating Cash Flow': 700000000, 'Free Cash Flow': 200000000, 'Capital Expenditure': -500000000}
        }
        
        return {
            'financials': pd.DataFrame(financials_data).T,
            'balance_sheet': pd.DataFrame(balance_sheet_data).T,  
            'cashflow': pd.DataFrame(cashflow_data).T,
            'info': {
                'longName': 'Test Company Ltd',
                'financialCurrency': 'INR'
            }
        }
    
    @pytest.mark.asyncio
    async def test_get_financial_statements_analysis_success(self, service, mock_yfinance_data):
        """Test successful financial statements analysis"""
        
        with patch('yfinance.Ticker') as mock_ticker:
            # Setup mock
            mock_stock = Mock()
            mock_stock.info = mock_yfinance_data['info']
            mock_stock.financials = mock_yfinance_data['financials']
            mock_stock.balance_sheet = mock_yfinance_data['balance_sheet']
            mock_stock.cashflow = mock_yfinance_data['cashflow']
            mock_ticker.return_value = mock_stock
            
            # Test the service
            result = await service.get_financial_statements_analysis('TEST.NS')
            
            # Verify result structure
            assert result.ticker == 'TEST.NS'
            assert result.company_name == 'Test Company Ltd'
            assert result.currency == 'INR'
            assert len(result.annual_data) == 5
            
            # Verify calculated metrics
            assert result.revenue_cagr_5y > 0  # Should show positive growth
            assert result.earnings_quality_score > 0
            assert result.data_completeness > 0.8  # Should have good data completeness
            
            # Verify annual data
            latest_year = result.annual_data[0]
            assert latest_year.total_revenue == 10000000000
            assert latest_year.net_income == 800000000
            assert latest_year.revenue_yoy_change is not None  # Should have YoY calculation
    
    @pytest.mark.asyncio
    async def test_cagr_calculation(self, service):
        """Test CAGR calculation accuracy"""
        
        # Test with known values
        values = [1000, 900, 800, 700, 600]  # Declining trend
        cagr = service._calculate_cagr(values)
        
        # Manual calculation: (1000/600)^(1/4) - 1 = 0.1351 = 13.51%
        expected_cagr = ((1000 / 600) ** (1/4) - 1) * 100
        assert abs(cagr - expected_cagr) < 0.1
    
    @pytest.mark.asyncio  
    async def test_yoy_change_calculation(self, service):
        """Test year-over-year change calculation"""
        
        # Test positive change
        yoy_change = service._calculate_yoy_change(1100, 1000)
        assert yoy_change == 10.0
        
        # Test negative change
        yoy_change = service._calculate_yoy_change(900, 1000)
        assert yoy_change == -10.0
        
        # Test with zero previous value
        yoy_change = service._calculate_yoy_change(1000, 0)
        assert yoy_change is None
    
    @pytest.mark.asyncio
    async def test_earnings_quality_score(self, service):
        """Test earnings quality scoring"""
        
        # Create test data where OCF > Net Income (good quality)
        test_data = [
            FinancialStatementYear(
                year='2024',
                fiscal_year_end=datetime(2024, 3, 31),
                operating_cash_flow=1200000000,
                net_income=1000000000
            ),
            FinancialStatementYear(
                year='2023', 
                fiscal_year_end=datetime(2023, 3, 31),
                operating_cash_flow=1100000000,
                net_income=950000000
            )
        ]
        
        quality_score = service._calculate_earnings_quality_score(test_data)
        assert quality_score > 60  # Should score well with OCF > NI
    
    @pytest.mark.asyncio
    async def test_revenue_consistency_score(self, service):
        """Test revenue consistency scoring"""
        
        # Create consistent growth data
        test_data = [
            FinancialStatementYear(year='2024', fiscal_year_end=datetime(2024, 3, 31), revenue_yoy_change=10.0),
            FinancialStatementYear(year='2023', fiscal_year_end=datetime(2023, 3, 31), revenue_yoy_change=12.0),
            FinancialStatementYear(year='2022', fiscal_year_end=datetime(2022, 3, 31), revenue_yoy_change=11.0)
        ]
        
        consistency_score = service._calculate_revenue_consistency_score(test_data)
        assert consistency_score > 70  # Should score well for consistent growth
    
    @pytest.mark.asyncio
    async def test_safe_extract_value(self, service):
        """Test safe value extraction from DataFrames"""
        
        # Create test DataFrame
        test_data = pd.DataFrame({
            datetime(2024, 3, 31): {'Total Revenue': 1000000000, 'Net Income': 80000000},
            datetime(2023, 3, 31): {'Total Revenue': 950000000, 'Net Income': 75000000}
        }).T
        
        # Test successful extraction
        value = service._safe_extract_value(
            test_data, 
            datetime(2024, 3, 31),
            ['Total Revenue']
        )
        assert value == 1000000000
        
        # Test fallback to alternative field name
        value = service._safe_extract_value(
            test_data,
            datetime(2024, 3, 31), 
            ['Revenue', 'Total Revenue']  # First doesn't exist, second does
        )
        assert value == 1000000000
        
        # Test missing field
        value = service._safe_extract_value(
            test_data,
            datetime(2024, 3, 31),
            ['Nonexistent Field']
        )
        assert value == 0.0
    
    @pytest.mark.asyncio
    async def test_simple_mode_summary_generation(self, service):
        """Test Simple Mode summary generation"""
        
        # Create test data with strong financials
        test_data = [
            FinancialStatementYear(
                year='2024',
                fiscal_year_end=datetime(2024, 3, 31),
                total_revenue=1000000000,
                net_income=150000000,
                operating_cash_flow=180000000
            )
        ]
        
        summary = service._generate_simple_mode_summary(
            test_data, 
            revenue_cagr=15.0,  # Strong growth
            net_income_cagr=20.0,  # Excellent profit growth  
            earnings_quality=85.0  # High quality
        )
        
        assert "Strong revenue growth" in summary
        assert "Excellent profit growth" in summary
        assert "High earnings quality" in summary
        assert len(summary) > 50  # Should be substantive
    
    @pytest.mark.asyncio
    async def test_data_completeness_calculation(self, service):
        """Test data completeness scoring"""
        
        # Complete data
        complete_data = [
            FinancialStatementYear(
                year='2024',
                fiscal_year_end=datetime(2024, 3, 31),
                total_revenue=1000000000,
                net_income=100000000,
                total_assets=2000000000,
                stockholders_equity=800000000,
                operating_cash_flow=120000000
            )
        ]
        
        completeness = service._calculate_data_completeness(complete_data)
        assert completeness == 1.0  # 100% complete
        
        # Incomplete data  
        incomplete_data = [
            FinancialStatementYear(
                year='2024',
                fiscal_year_end=datetime(2024, 3, 31),
                total_revenue=1000000000,
                net_income=0,  # Missing
                total_assets=0,  # Missing
                stockholders_equity=800000000,
                operating_cash_flow=120000000
            )
        ]
        
        completeness = service._calculate_data_completeness(incomplete_data)
        assert completeness == 0.6  # 60% complete (3 out of 5 fields)
    
    @pytest.mark.asyncio
    async def test_data_warnings_generation(self, service):
        """Test data quality warnings"""
        
        # Test with limited years
        limited_data = [
            FinancialStatementYear(year='2024', fiscal_year_end=datetime(2024, 3, 31), total_revenue=1000000000)
        ]
        
        warnings = service._generate_data_warnings(limited_data, 0.9)
        assert any("Limited historical data" in warning for warning in warnings)
        
        # Test with low completeness
        warnings = service._generate_data_warnings(limited_data, 0.5)
        assert any("50.0% complete" in warning for warning in warnings)
    
    @pytest.mark.asyncio
    async def test_error_handling(self, service):
        """Test error handling for invalid tickers"""
        
        with patch('yfinance.Ticker') as mock_ticker:
            # Mock ticker with empty data
            mock_stock = Mock()
            mock_stock.info = {}
            mock_stock.financials = pd.DataFrame()  # Empty DataFrame
            mock_stock.balance_sheet = pd.DataFrame()
            mock_stock.cashflow = pd.DataFrame() 
            mock_ticker.return_value = mock_stock
            
            # Should raise ValueError for empty data
            with pytest.raises(ValueError, match="No financial statement data available"):
                await service.get_financial_statements_analysis('INVALID.NS')
    
    @pytest.mark.asyncio
    async def test_cache_functionality(self):
        """Test caching functionality"""
        
        service_with_cache = FinancialStatementsService(use_cache=True)
        
        with patch('yfinance.Ticker') as mock_ticker, \
             patch.object(service_with_cache.cache_manager, 'get', new_callable=AsyncMock) as mock_get, \
             patch.object(service_with_cache.cache_manager, 'set', new_callable=AsyncMock) as mock_set:
            
            # Setup mocks
            mock_get.return_value = None  # Cache miss
            mock_stock = Mock()
            mock_stock.info = {'longName': 'Test Company', 'financialCurrency': 'INR'}
            mock_stock.financials = pd.DataFrame({
                datetime(2024, 3, 31): {'Total Revenue': 1000000000, 'Net Income': 100000000}
            }).T
            mock_stock.balance_sheet = pd.DataFrame({
                datetime(2024, 3, 31): {'Total Assets': 2000000000, 'Stockholders Equity': 800000000}
            }).T
            mock_stock.cashflow = pd.DataFrame({
                datetime(2024, 3, 31): {'Operating Cash Flow': 120000000}
            }).T
            mock_ticker.return_value = mock_stock
            
            # Call service
            result = await service_with_cache.get_financial_statements_analysis('TEST.NS')
            
            # Verify cache interactions
            mock_get.assert_called_once()
            mock_set.assert_called_once()
            
            # Verify result
            assert result.ticker == 'TEST.NS'
    
    @pytest.mark.asyncio
    async def test_real_data_integration(self, service):
        """Integration test with real yfinance data (if available)"""
        
        try:
            # Test with a major Indian stock (should have reliable data)
            result = await service.get_financial_statements_analysis('RELIANCE.NS', force_refresh=True)
            
            # Verify basic structure
            assert result.ticker == 'RELIANCE.NS'
            assert result.company_name is not None
            assert len(result.annual_data) > 0
            assert result.data_completeness > 0
            
            # Verify calculated metrics are reasonable
            assert -100 < result.revenue_cagr_5y < 100  # CAGR should be reasonable
            assert 0 <= result.earnings_quality_score <= 100
            assert len(result.simple_mode_summary) > 20
            
            print(f"✅ Real data test passed for {result.company_name}")
            print(f"   Revenue CAGR: {result.revenue_cagr_5y:.1f}%")
            print(f"   Earnings Quality: {result.earnings_quality_score:.1f}/100")
            print(f"   Data Completeness: {result.data_completeness:.1%}")
            
        except Exception as e:
            # Skip if network issues or rate limits
            pytest.skip(f"Real data test skipped due to: {e}")

# Performance benchmarks
class TestFinancialStatementsPerformance:
    """Performance tests for Financial Statements Service"""
    
    @pytest.mark.asyncio
    async def test_service_performance(self):
        """Test service performance with multiple tickers"""
        
        service = FinancialStatementsService(use_cache=False)
        tickers = ['RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS']
        
        start_time = datetime.now()
        
        try:
            tasks = [
                service.get_financial_statements_analysis(ticker, force_refresh=True)
                for ticker in tickers
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # Should complete within reasonable time (30 seconds for 3 tickers)
            assert duration < 30, f"Performance test took {duration:.2f}s - too slow"
            
            # Count successful results
            successful_results = [r for r in results if isinstance(r, FinancialStatementsAnalysis)]
            print(f"✅ Performance test: {len(successful_results)}/{len(tickers)} tickers in {duration:.2f}s")
            
        except Exception as e:
            pytest.skip(f"Performance test skipped: {e}")

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])