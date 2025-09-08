import pytest
from unittest.mock import patch

class TestValuationAPI:
    """Test cases for DCF valuation API endpoints."""
    
    @pytest.mark.asyncio
    async def test_dcf_valuation_success(self, client, mock_yfinance, sample_dcf_request):
        """Test successful DCF valuation calculation."""
        response = client.post(
            "/api/valuation/dcf?ticker=RELIANCE.NS",
            json=sample_dcf_request
        )
        assert response.status_code == 200
        
        data = response.json()
        
        # Check required fields
        assert "valuation" in data
        assert "sensitivity" in data
        assert "financial_data" in data
        assert "last_updated" in data
        
        # Check valuation structure
        valuation = data["valuation"]
        assert "intrinsic_value_per_share" in valuation
        assert "terminal_value" in valuation
        assert "enterprise_value" in valuation
        assert "equity_value" in valuation
        assert "current_stock_price" in valuation
        assert "upside_downside" in valuation
        assert "projections" in valuation
        assert "assumptions" in valuation
        
        # Check sensitivity analysis
        sensitivity = data["sensitivity"]
        assert "wacc_range" in sensitivity
        assert "terminal_growth_range" in sensitivity
        assert "sensitivity_matrix" in sensitivity
    
    def test_dcf_valuation_missing_ticker(self, client, sample_dcf_request):
        """Test DCF valuation without ticker parameter."""
        response = client.post("/api/valuation/dcf", json=sample_dcf_request)
        assert response.status_code == 422  # Validation error
    
    def test_dcf_valuation_invalid_ticker(self, client, sample_dcf_request):
        """Test DCF valuation with invalid ticker."""
        response = client.post(
            "/api/valuation/dcf?ticker=INVALID",
            json=sample_dcf_request
        )
        assert response.status_code == 404
        
        data = response.json()
        assert data["error"] is True
        assert "not found" in data["message"].lower()
    
    @pytest.mark.parametrize("field,value,expected_status", [
        ("revenue_growth_rate", -100, 400),  # Negative growth
        ("revenue_growth_rate", 1000, 400),  # Unrealistic growth
        ("ebitda_margin", -50, 400),  # Negative margin
        ("ebitda_margin", 150, 400),  # Unrealistic margin
        ("tax_rate", -10, 400),  # Negative tax rate
        ("tax_rate", 110, 400),  # Tax rate over 100%
        ("wacc", -5, 400),  # Negative WACC
        ("wacc", 100, 400),  # Unrealistic WACC
        ("terminal_growth_rate", -10, 400),  # Negative terminal growth
        ("terminal_growth_rate", 50, 400),  # Unrealistic terminal growth
    ])
    def test_dcf_valuation_invalid_assumptions(self, client, sample_dcf_request, field, value, expected_status):
        """Test DCF valuation with invalid assumption values."""
        invalid_request = sample_dcf_request.copy()
        invalid_request[field] = value
        
        response = client.post(
            "/api/valuation/dcf?ticker=RELIANCE.NS",
            json=invalid_request
        )
        assert response.status_code == expected_status
    
    def test_dcf_valuation_missing_fields(self, client):
        """Test DCF valuation with missing required fields."""
        incomplete_request = {
            "revenue_growth_rate": 10.0,
            # Missing other required fields
        }
        
        response = client.post(
            "/api/valuation/dcf?ticker=RELIANCE.NS",
            json=incomplete_request
        )
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.parametrize("growth_rate,margin,tax_rate,wacc,terminal_growth", [
        (5.0, 10.0, 25.0, 10.0, 3.0),  # Conservative assumptions
        (15.0, 20.0, 30.0, 15.0, 5.0),  # Aggressive assumptions
        (0.0, 5.0, 15.0, 8.0, 2.0),     # Low growth scenario
    ])
    def test_dcf_valuation_different_scenarios(self, client, mock_yfinance, growth_rate, margin, tax_rate, wacc, terminal_growth):
        """Test DCF valuation with different assumption scenarios."""
        request_data = {
            "revenue_growth_rate": growth_rate,
            "ebitda_margin": margin,
            "tax_rate": tax_rate,
            "wacc": wacc,
            "terminal_growth_rate": terminal_growth
        }
        
        response = client.post(
            "/api/valuation/dcf?ticker=RELIANCE.NS",
            json=request_data
        )
        assert response.status_code == 200
        
        data = response.json()
        valuation = data["valuation"]
        
        # Verify assumptions are reflected in response
        assumptions = valuation["assumptions"]
        assert assumptions["revenue_growth_rate"] == growth_rate
        assert assumptions["ebitda_margin"] == margin
        assert assumptions["tax_rate"] == tax_rate
        assert assumptions["wacc"] == wacc
        assert assumptions["terminal_growth_rate"] == terminal_growth
    
    def test_dcf_valuation_projections_length(self, client, mock_yfinance, sample_dcf_request):
        """Test that DCF valuation returns expected number of projections."""
        response = client.post(
            "/api/valuation/dcf?ticker=RELIANCE.NS",
            json=sample_dcf_request
        )
        assert response.status_code == 200
        
        data = response.json()
        projections = data["valuation"]["projections"]
        
        # Should have 5 years of projections by default
        assert len(projections) == 5
        
        # Each projection should have required fields
        for projection in projections:
            assert "year" in projection
            assert "revenue" in projection
            assert "ebitda" in projection
            assert "free_cash_flow" in projection
            assert "present_value" in projection
    
    def test_dcf_valuation_sensitivity_matrix(self, client, mock_yfinance, sample_dcf_request):
        """Test sensitivity analysis matrix structure."""
        response = client.post(
            "/api/valuation/dcf?ticker=RELIANCE.NS",
            json=sample_dcf_request
        )
        assert response.status_code == 200
        
        data = response.json()
        sensitivity = data["sensitivity"]
        
        # Check matrix dimensions
        wacc_range = sensitivity["wacc_range"]
        terminal_growth_range = sensitivity["terminal_growth_range"]
        matrix = sensitivity["sensitivity_matrix"]
        
        assert len(matrix) == len(wacc_range)
        assert all(len(row) == len(terminal_growth_range) for row in matrix)
        
        # All values should be positive
        assert all(all(val > 0 for val in row) for row in matrix)
    
    def test_dcf_valuation_response_time(self, client, mock_yfinance, sample_dcf_request):
        """Test that DCF valuation responds within reasonable time."""
        import time
        
        start_time = time.time()
        response = client.post(
            "/api/valuation/dcf?ticker=RELIANCE.NS",
            json=sample_dcf_request
        )
        end_time = time.time()
        
        response_time = end_time - start_time
        assert response_time < 10.0  # Should respond within 10 seconds
        assert response.status_code == 200