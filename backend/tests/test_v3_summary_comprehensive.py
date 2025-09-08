"""
Comprehensive test suite for V3 Summary Service
Tests integration issues, validation errors, and data flow problems
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime
import json

from app.services.v3_summary_service import V3SummaryService
from app.models.summary import (
    SummaryResponse, 
    SimpleSummaryResponse, 
    AgenticSummaryResponse, 
    FairValueBand, 
    InvestmentLabel
)


@pytest.fixture
def v3_service():
    """Create V3SummaryService instance for testing"""
    return V3SummaryService()


@pytest.fixture
def sample_company_data():
    """Sample company data for testing"""
    return {
        "name": "Reliance Industries Limited",
        "sector": "ENERGY",
        "marketCap": 1500000000000,
        "currentPrice": 1393.70
    }


@pytest.fixture
def sample_baseline_fair_value():
    """Sample baseline fair value for testing"""
    return FairValueBand(
        min_value=723.12,
        max_value=1084.68,
        current_price=1393.70,
        method="DCF",
        confidence=0.6
    )


class TestAgenticModeValidation:
    """Test agentic mode Pydantic validation issues"""

    @pytest.mark.asyncio
    async def test_agentic_response_creation_with_valid_data(self, v3_service, sample_company_data, sample_baseline_fair_value):
        """Test that agentic response can be created with valid data"""
        
        # Mock AI analysis response with list reasoning (the issue we encountered)
        ai_analysis = {
            "reasoning": [
                "Growth assumptions based on historical CAGR analysis",
                "Fair value calculated using sector-appropriate DCF methodology",
                "Key risks include market volatility and sector-specific challenges"
            ],
            "thesis": "Investment thesis here",
            "financial_health": ["Strong balance sheet", "Consistent revenue growth"],
            "technical_outlook": ["Technical indicators suggest current positioning"],
            "cost_info": {"tokens": 1500, "estimated_cost": 0.05},
            "model_version": "claude-3-haiku"
        }
        
        # Test parsing with baseline fair value
        structured_analysis = v3_service._parse_ai_analysis(ai_analysis, sample_baseline_fair_value)
        
        # Verify fair value band uses baseline data
        assert structured_analysis["fair_value_band"].current_price == 1393.70
        assert structured_analysis["fair_value_band"].method == "AI-Enhanced DCF"
        assert structured_analysis["fair_value_band"].confidence == 0.7  # Boosted from 0.6
        
        # Test AgenticSummaryResponse creation
        agent_reasoning = ". ".join(ai_analysis.get("reasoning", [])) if isinstance(ai_analysis.get("reasoning"), list) else ai_analysis.get("reasoning")
        
        summary = AgenticSummaryResponse(
            ticker="RELIANCE.NS",
            company_name=sample_company_data["name"],
            fair_value_band=structured_analysis["fair_value_band"],
            investment_label=structured_analysis["investment_label"],
            key_factors=structured_analysis["key_factors"],
            valuation_insights=structured_analysis["valuation_insights"],
            market_signals=structured_analysis["market_signals"],
            business_fundamentals=structured_analysis["business_fundamentals"],
            data_health_warnings=[],
            analysis_timestamp=datetime.now(),
            analysis_mode="agentic",
            sector="ENERGY",
            agent_reasoning=agent_reasoning,  # This was causing validation error
            cost_breakdown=ai_analysis.get("cost_info"),
            model_version=ai_analysis.get("model_version")
        )
        
        # Verify all fields are correctly set
        assert summary.ticker == "RELIANCE.NS"
        assert summary.analysis_mode == "agentic"
        assert isinstance(summary.agent_reasoning, str)  # Must be string, not list
        assert "Growth assumptions based on historical CAGR analysis" in summary.agent_reasoning
        
        
    @pytest.mark.asyncio
    async def test_agentic_response_validation_error_handling(self, v3_service):
        """Test handling of validation errors in agentic response creation"""
        
        # Test with invalid data types that would cause validation errors
        with pytest.raises(Exception):  # Should raise Pydantic validation error
            AgenticSummaryResponse(
                ticker="RELIANCE.NS",
                company_name="Test Company",
                fair_value_band="invalid_data",  # Wrong type
                investment_label="Invalid Label",  # Not in enum
                key_factors="not_a_list",  # Should be list
                valuation_insights="",
                market_signals="",
                business_fundamentals="",
                data_health_warnings=[],
                analysis_timestamp=datetime.now(),
                analysis_mode="agentic",
                sector="ENERGY",
                agent_reasoning=["list", "instead", "of", "string"],  # Wrong type - should be string
            )


class TestCacheSystemIntegration:
    """Test cache system with MARKET_DATA type"""

    @pytest.mark.asyncio
    async def test_cache_type_market_data_exists(self):
        """Test that MARKET_DATA cache type exists and is configured"""
        from app.services.intelligent_cache import CacheType, IntelligentCacheManager
        
        # Verify MARKET_DATA enum exists
        assert hasattr(CacheType, 'MARKET_DATA')
        assert CacheType.MARKET_DATA.value == "market_data"
        
        # Verify cache manager has TTL configuration
        cache_manager = IntelligentCacheManager()
        assert CacheType.MARKET_DATA in cache_manager.ttl_config
        assert cache_manager.ttl_config[CacheType.MARKET_DATA].total_seconds() == 4 * 3600  # 4 hours


class TestCurrentPriceDataFlow:
    """Test current price data flow from DCF to agentic response"""

    @pytest.mark.asyncio
    async def test_current_price_propagation(self, v3_service, sample_baseline_fair_value):
        """Test that current price from DCF properly flows to agentic response"""
        
        ai_analysis = {
            "reasoning": ["Test reasoning"],
            "thesis": "Test thesis",
            "financial_health": [],
            "technical_outlook": [],
        }
        
        # Test with baseline fair value containing real current price
        structured_analysis = v3_service._parse_ai_analysis(ai_analysis, sample_baseline_fair_value)
        
        # Verify current price is preserved from baseline
        assert structured_analysis["fair_value_band"].current_price == 1393.70
        assert structured_analysis["fair_value_band"].min_value == 723.12
        assert structured_analysis["fair_value_band"].max_value == 1084.68
        
        # Test without baseline (fallback scenario)
        structured_analysis_fallback = v3_service._parse_ai_analysis(ai_analysis, None)
        
        # Verify fallback values are used
        assert structured_analysis_fallback["fair_value_band"].current_price == 220
        assert structured_analysis_fallback["fair_value_band"].min_value == 200
        assert structured_analysis_fallback["fair_value_band"].max_value == 250


class TestAgenticEndpointIntegration:
    """Integration tests for the full agentic endpoint"""

    @pytest.mark.asyncio
    async def test_agentic_endpoint_end_to_end(self, v3_service):
        """Test agentic endpoint from request to response without external dependencies"""
        
        # Mock all external dependencies
        with patch.object(v3_service, '_fetch_company_data') as mock_company, \
             patch.object(v3_service, '_get_baseline_fair_value') as mock_baseline, \
             patch.object(v3_service, '_fetch_technical_data') as mock_technical, \
             patch.object(v3_service, 'get_peer_analysis') as mock_peer, \
             patch.object(v3_service, '_generate_ai_investment_thesis') as mock_ai:
            
            # Setup mocks
            mock_company.return_value = {
                "name": "Reliance Industries Limited",
                "sector": "ENERGY"
            }
            
            mock_baseline.return_value = FairValueBand(
                min_value=723.12,
                max_value=1084.68,
                current_price=1393.70,
                method="DCF",
                confidence=0.6
            )
            
            mock_technical.return_value = {"indicators": {}}
            mock_peer.return_value = {"peers": []}
            
            # Mock AI response that caused the original validation error
            mock_ai.return_value = {
                "reasoning": [  # List type that was causing validation error
                    "Growth assumptions based on historical analysis",
                    "Sector-appropriate methodology applied"
                ],
                "thesis": "Bullish outlook based on fundamentals",
                "financial_health": ["Strong balance sheet"],
                "technical_outlook": ["Positive momentum"],
                "cost_info": {"tokens": 1000, "estimated_cost": 0.03},
                "model_version": "claude-3-haiku"
            }
            
            # Test agentic summary generation
            result = await v3_service.generate_agentic_summary("RELIANCE.NS")
            
            # Verify response structure
            assert isinstance(result, AgenticSummaryResponse)
            assert result.ticker == "RELIANCE.NS"
            assert result.analysis_mode == "agentic"
            assert result.fair_value_band.current_price == 1393.70  # Real price, not fallback
            assert isinstance(result.agent_reasoning, str)  # Properly converted from list
            assert "Growth assumptions" in result.agent_reasoning


class TestErrorScenarios:
    """Test various error scenarios and edge cases"""

    @pytest.mark.asyncio
    async def test_ai_analysis_parsing_with_missing_fields(self, v3_service):
        """Test AI analysis parsing with missing or malformed fields"""
        
        # Test with minimal AI response
        minimal_ai_analysis = {}
        structured = v3_service._parse_ai_analysis(minimal_ai_analysis)
        
        # Should provide fallbacks
        assert structured["investment_label"] == InvestmentLabel.NEUTRAL
        assert len(structured["key_factors"]) >= 2
        assert "AI-enhanced analysis completed" in structured["key_factors"]
        
    @pytest.mark.asyncio
    async def test_pydantic_validation_edge_cases(self):
        """Test edge cases in Pydantic model validation"""
        
        # Test FairValueBand validation
        with pytest.raises(Exception):
            FairValueBand(
                min_value="not_a_number",  # Invalid type
                max_value=1000,
                current_price=500,
                method="DCF",
                confidence=0.5
            )
        
        # Test confidence bounds
        with pytest.raises(Exception):
            FairValueBand(
                min_value=100,
                max_value=200,
                current_price=150,
                method="DCF",
                confidence=1.5  # > 1.0, should fail
            )


@pytest.mark.integration
class TestRealEndpointCalls:
    """Integration tests with real HTTP calls"""

    @pytest.mark.asyncio
    async def test_agentic_endpoint_http_call(self):
        """Test actual HTTP call to agentic endpoint"""
        import httpx
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    "http://localhost:8000/api/v3/summary/RELIANCE.NS/agentic",
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Verify response structure
                    assert "ticker" in data
                    assert "analysis_mode" in data
                    assert data["analysis_mode"] == "agentic"
                    assert "fair_value_band" in data
                    
                    # Verify fair value band has real price data
                    fair_value = data["fair_value_band"]
                    assert "current_price" in fair_value
                    assert fair_value["current_price"] > 1000  # Should be realistic price, not 220
                    
                    # Verify agent_reasoning is string, not list
                    assert isinstance(data.get("agent_reasoning"), str)
                    
                else:
                    pytest.skip(f"Backend not available or returned {response.status_code}")
                    
            except httpx.ConnectError:
                pytest.skip("Backend server not running")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])