"""
Comprehensive API validation tests
Tests HTTP endpoints, Pydantic model validation, and request/response handling
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, Mock
from datetime import datetime
import json

from app.main import app
from app.models.summary import FairValueBand, InvestmentLabel, AgenticSummaryResponse
from app.services.v3_summary_service import V3SummaryService


@pytest.fixture
def client():
    """Create test client for FastAPI app"""
    return TestClient(app)


@pytest.fixture
def mock_v3_service():
    """Mock V3SummaryService for testing"""
    return Mock(spec=V3SummaryService)


class TestV3SummaryEndpoints:
    """Test V3 Summary API endpoints"""

    def test_simple_mode_endpoint(self, client):
        """Test simple mode endpoint returns valid response"""
        with patch('app.api.v3_summary.v3_summary_service') as mock_service:
            # Mock successful response
            mock_service.generate_simple_summary.return_value = {
                "ticker": "RELIANCE.NS",
                "company_name": "Reliance Industries Limited",
                "fair_value_band": {
                    "min_value": 723.12,
                    "max_value": 1084.68,
                    "current_price": 1393.70,
                    "method": "DCF",
                    "confidence": 0.6
                },
                "investment_label": "Neutral",
                "key_factors": ["Factor 1", "Factor 2"],
                "valuation_insights": "Valuation insights",
                "market_signals": "Market signals",
                "business_fundamentals": "Business fundamentals",
                "data_health_warnings": [],
                "analysis_timestamp": datetime.now().isoformat(),
                "analysis_mode": "simple",
                "sector": "ENERGY"
            }
            
            response = client.get("/api/v3/summary/RELIANCE.NS/simple")
            
            assert response.status_code == 200
            data = response.json()
            assert data["ticker"] == "RELIANCE.NS"
            assert data["analysis_mode"] == "simple"

    def test_agentic_mode_endpoint_success(self, client):
        """Test agentic mode endpoint with successful response"""
        with patch('app.api.v3_summary.v3_summary_service') as mock_service:
            
            # Create a proper AgenticSummaryResponse mock
            mock_response = AgenticSummaryResponse(
                ticker="RELIANCE.NS",
                company_name="Reliance Industries Limited",
                fair_value_band=FairValueBand(
                    min_value=723.12,
                    max_value=1084.68,
                    current_price=1393.70,
                    method="AI-Enhanced DCF",
                    confidence=0.7
                ),
                investment_label=InvestmentLabel.NEUTRAL,
                key_factors=["AI-enhanced analysis", "Comprehensive evaluation"],
                valuation_insights="AI-generated valuation insights",
                market_signals="AI-generated market signals",
                business_fundamentals="AI-generated business fundamentals",
                data_health_warnings=[],
                analysis_timestamp=datetime.now(),
                analysis_mode="agentic",
                sector="ENERGY",
                agent_reasoning="Detailed AI reasoning process",  # String, not list
                cost_breakdown={"tokens": 1500, "estimated_cost": 0.05},
                model_version="claude-3-haiku"
            )
            
            mock_service.generate_agentic_summary = AsyncMock(return_value=mock_response)
            
            response = client.get("/api/v3/summary/RELIANCE.NS/agentic")
            
            assert response.status_code == 200
            data = response.json()
            assert data["ticker"] == "RELIANCE.NS"
            assert data["analysis_mode"] == "agentic"
            assert data["fair_value_band"]["current_price"] == 1393.70  # Real price, not fallback
            assert isinstance(data.get("agent_reasoning"), str)  # Must be string

    def test_agentic_mode_validation_error(self, client):
        """Test agentic mode endpoint with validation error"""
        with patch('app.api.v3_summary.v3_summary_service') as mock_service:
            
            # Mock service to raise the validation error we encountered
            mock_service.generate_agentic_summary = AsyncMock(
                side_effect=ValueError("Invalid ticker: 1 validation error for AgenticSummaryResponse\nagent_reasoning\n  Input should be a valid string [type=string_type, input_value=['Growth assumptions base...or-specific challenges'], input_type=list]")
            )
            
            response = client.get("/api/v3/summary/RELIANCE.NS/agentic")
            
            assert response.status_code == 400
            assert "validation error" in response.json()["message"]

    def test_invalid_ticker_format(self, client):
        """Test endpoint with invalid ticker format"""
        response = client.get("/api/v3/summary/INVALID_TICKER_FORMAT_TEST/simple")
        
        # Should handle gracefully
        assert response.status_code in [400, 500]  # Either client or server error is acceptable

    def test_timeout_handling(self, client):
        """Test endpoint timeout handling"""
        with patch('app.api.v3_summary.v3_summary_service') as mock_service:
            
            # Mock service to timeout
            mock_service.generate_simple_summary = AsyncMock(
                side_effect=TimeoutError("Request timeout")
            )
            
            response = client.get("/api/v3/summary/RELIANCE.NS/simple")
            
            assert response.status_code >= 400  # Should return error status


class TestPydanticModelValidation:
    """Test Pydantic model validation edge cases"""

    def test_fair_value_band_validation(self):
        """Test FairValueBand model validation"""
        
        # Valid case
        valid_band = FairValueBand(
            min_value=100.0,
            max_value=200.0,
            current_price=150.0,
            method="DCF",
            confidence=0.8
        )
        assert valid_band.confidence == 0.8
        
        # Invalid confidence (> 1.0)
        with pytest.raises(ValueError):
            FairValueBand(
                min_value=100.0,
                max_value=200.0,
                current_price=150.0,
                method="DCF",
                confidence=1.5
            )
        
        # Invalid confidence (< 0.0)
        with pytest.raises(ValueError):
            FairValueBand(
                min_value=100.0,
                max_value=200.0,
                current_price=150.0,
                method="DCF",
                confidence=-0.1
            )

    def test_investment_label_enum_validation(self):
        """Test InvestmentLabel enum validation"""
        
        # Valid labels
        valid_labels = [
            InvestmentLabel.STRONGLY_BULLISH,
            InvestmentLabel.CAUTIOUSLY_BULLISH,
            InvestmentLabel.NEUTRAL,
            InvestmentLabel.CAUTIOUSLY_BEARISH,
            InvestmentLabel.STRONGLY_BEARISH
        ]
        
        for label in valid_labels:
            band = FairValueBand(
                min_value=100.0,
                max_value=200.0,
                current_price=150.0,
                method="DCF",
                confidence=0.8
            )
            # Should not raise
            AgenticSummaryResponse(
                ticker="TEST.NS",
                company_name="Test Company",
                fair_value_band=band,
                investment_label=label,
                key_factors=["test"],
                valuation_insights="test",
                market_signals="test",
                business_fundamentals="test",
                data_health_warnings=[],
                analysis_timestamp=datetime.now(),
                analysis_mode="agentic",
                sector="TEST"
            )

    def test_agentic_response_field_types(self):
        """Test AgenticSummaryResponse field type validation"""
        
        band = FairValueBand(
            min_value=100.0,
            max_value=200.0,
            current_price=150.0,
            method="DCF",
            confidence=0.8
        )
        
        # Valid case with all optional fields
        valid_response = AgenticSummaryResponse(
            ticker="TEST.NS",
            company_name="Test Company",
            fair_value_band=band,
            investment_label=InvestmentLabel.NEUTRAL,
            key_factors=["factor1", "factor2"],
            valuation_insights="insights",
            market_signals="signals",
            business_fundamentals="fundamentals",
            data_health_warnings=[],
            analysis_timestamp=datetime.now(),
            analysis_mode="agentic",
            sector="TEST",
            agent_reasoning="String reasoning",  # Must be string
            cost_breakdown={"tokens": 1000, "cost": 0.03},
            model_version="claude-3-haiku"
        )
        
        assert isinstance(valid_response.agent_reasoning, str)
        assert isinstance(valid_response.cost_breakdown, dict)
        
        # Invalid case - agent_reasoning as list (the bug we fixed)
        with pytest.raises(ValueError):
            AgenticSummaryResponse(
                ticker="TEST.NS",
                company_name="Test Company",
                fair_value_band=band,
                investment_label=InvestmentLabel.NEUTRAL,
                key_factors=["factor1"],
                valuation_insights="insights",
                market_signals="signals", 
                business_fundamentals="fundamentals",
                data_health_warnings=[],
                analysis_timestamp=datetime.now(),
                analysis_mode="agentic",
                sector="TEST",
                agent_reasoning=["list", "instead", "of", "string"]  # Invalid type
            )

    def test_key_factors_list_validation(self):
        """Test that key_factors field properly validates list type"""
        
        band = FairValueBand(
            min_value=100.0,
            max_value=200.0,
            current_price=150.0,
            method="DCF",
            confidence=0.8
        )
        
        # Valid list
        valid_response = AgenticSummaryResponse(
            ticker="TEST.NS",
            company_name="Test Company",
            fair_value_band=band,
            investment_label=InvestmentLabel.NEUTRAL,
            key_factors=["factor1", "factor2", "factor3"],  # List of strings
            valuation_insights="insights",
            market_signals="signals",
            business_fundamentals="fundamentals",
            data_health_warnings=[],
            analysis_timestamp=datetime.now(),
            analysis_mode="agentic",
            sector="TEST"
        )
        assert len(valid_response.key_factors) == 3
        
        # Invalid - string instead of list
        with pytest.raises(ValueError):
            AgenticSummaryResponse(
                ticker="TEST.NS",
                company_name="Test Company", 
                fair_value_band=band,
                investment_label=InvestmentLabel.NEUTRAL,
                key_factors="single string instead of list",  # Invalid type
                valuation_insights="insights",
                market_signals="signals",
                business_fundamentals="fundamentals",
                data_health_warnings=[],
                analysis_timestamp=datetime.now(),
                analysis_mode="agentic",
                sector="TEST"
            )


class TestErrorHandling:
    """Test comprehensive error handling"""

    def test_network_timeout_simulation(self, client):
        """Test handling of network timeouts"""
        with patch('app.api.v3_summary.v3_summary_service') as mock_service:
            import asyncio
            
            mock_service.generate_simple_summary = AsyncMock(
                side_effect=asyncio.TimeoutError("Network timeout")
            )
            
            response = client.get("/api/v3/summary/RELIANCE.NS/simple")
            
            # Should handle timeout gracefully
            assert response.status_code >= 400
            assert "error" in response.json()

    def test_json_parsing_error(self, client):
        """Test handling of JSON parsing errors in AI responses"""
        with patch('app.api.v3_summary.v3_summary_service') as mock_service:
            
            mock_service.generate_agentic_summary = AsyncMock(
                side_effect=json.JSONDecodeError("Invalid JSON", "", 0)
            )
            
            response = client.get("/api/v3/summary/RELIANCE.NS/agentic")
            
            assert response.status_code >= 400

    def test_missing_required_fields(self, client):
        """Test handling of missing required fields in data"""
        with patch('app.api.v3_summary.v3_summary_service') as mock_service:
            
            # Mock response missing required fields
            mock_service.generate_simple_summary.return_value = {
                "ticker": "RELIANCE.NS",
                # Missing required fields like company_name, fair_value_band, etc.
            }
            
            response = client.get("/api/v3/summary/RELIANCE.NS/simple")
            
            # Should either return error or handle gracefully with defaults
            if response.status_code == 200:
                data = response.json()
                # Check that defaults/fallbacks are provided
                assert "company_name" in data
                assert "fair_value_band" in data


class TestConcurrentRequests:
    """Test handling of concurrent requests"""

    def test_concurrent_agentic_requests(self, client):
        """Test multiple concurrent agentic requests"""
        import threading
        import time
        
        results = []
        
        def make_request():
            response = client.get("/api/v3/summary/RELIANCE.NS/agentic")
            results.append(response.status_code)
        
        # Start multiple concurrent requests
        threads = []
        for i in range(3):
            thread = threading.Thread(target=make_request)
            thread.start()
            threads.append(thread)
        
        # Wait for all requests to complete
        for thread in threads:
            thread.join(timeout=30)  # 30 second timeout
        
        # All requests should complete
        assert len(results) == 3
        # At least some should succeed (might have rate limiting)
        success_count = sum(1 for status in results if status == 200)
        assert success_count >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])