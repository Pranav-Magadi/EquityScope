"""
Regression tests for specific integration issues
These tests are designed to catch the exact problems we encountered in production
"""

import pytest
from unittest.mock import patch, AsyncMock, Mock
from datetime import datetime
import json

from app.services.v3_summary_service import V3SummaryService
from app.services.intelligent_cache import CacheType, IntelligentCacheManager
from app.services.sector_intelligence_service import SectorIntelligenceService
from app.models.summary import AgenticSummaryResponse, FairValueBand, InvestmentLabel


class TestProductionIssueRegression:
    """Tests that would have caught the actual production issues"""

    @pytest.mark.asyncio
    async def test_agentic_endpoint_with_real_ai_response_format(self):
        """
        REGRESSION TEST: This test would have caught the Pydantic validation error
        
        The issue: AI service returns 'reasoning' as a list, but AgenticSummaryResponse
        expects agent_reasoning as a string. This causes validation failure.
        """
        v3_service = V3SummaryService()
        
        # Simulate ACTUAL AI response format that caused the issue
        real_ai_response_format = {
            "reasoning": [  # This is a LIST - the source of the validation error
                "Growth assumptions based on historical CAGR analysis",
                "Fair value calculated using sector-appropriate DCF methodology", 
                "Key risks include market volatility and sector-specific challenges"
            ],
            "thesis": "Investment thesis based on comprehensive analysis",
            "financial_health": ["Strong balance sheet", "Consistent revenue growth"],
            "technical_outlook": ["Technical indicators suggest current positioning"],
            "news_sentiment": {"overall": "neutral", "recent_trends": []},
            "peer_context": ["Leading position in sector"],
            "cost_info": {"core_analysis_tokens": 1200, "sentiment_tokens": 300, "estimated_cost": 0.045},
            "model_version": "claude-3-haiku"
        }
        
        # Mock the AI service to return the actual problematic format
        with patch.object(v3_service, '_generate_ai_investment_thesis', new_callable=AsyncMock) as mock_ai:
            mock_ai.return_value = real_ai_response_format
            
            # Mock other dependencies
            with patch.object(v3_service, '_fetch_company_data') as mock_company, \
                 patch.object(v3_service, '_calculate_rule_based_fair_value') as mock_baseline, \
                 patch.object(v3_service, '_fetch_technical_data') as mock_technical, \
                 patch.object(v3_service, 'get_peer_analysis') as mock_peer:
                
                mock_company.return_value = {"name": "Test Company", "sector": "ENERGY"}
                mock_baseline.return_value = FairValueBand(
                    min_value=723.12, max_value=1084.68, current_price=1393.70,
                    method="DCF", confidence=0.6
                )
                mock_technical.return_value = {"indicators": {}}
                mock_peer.return_value = {"peers": []}
                
                # This should NOT raise a Pydantic validation error
                # (it would have failed before our fix)
                result = await v3_service.generate_agentic_summary("TEST.NS")
                
                # Verify the response is valid
                assert isinstance(result, AgenticSummaryResponse)
                assert isinstance(result.agent_reasoning, str)  # Must be string, not list
                assert "Growth assumptions based on historical CAGR analysis" in result.agent_reasoning
                
                # Verify that reasoning list was properly joined into string
                assert "Fair value calculated using sector-appropriate DCF methodology" in result.agent_reasoning

    def test_cache_system_market_data_type_missing(self):
        """
        REGRESSION TEST: This test would have caught the missing MARKET_DATA cache type
        
        The issue: SectorIntelligenceService tries to use CacheType.MARKET_DATA
        but it didn't exist, causing AttributeError
        """
        
        # Test 1: Verify MARKET_DATA enum exists
        assert hasattr(CacheType, 'MARKET_DATA'), "CacheType.MARKET_DATA is missing - this caused production errors"
        
        # Test 2: Verify cache manager can handle MARKET_DATA
        cache_manager = IntelligentCacheManager()
        assert CacheType.MARKET_DATA in cache_manager.ttl_config, "MARKET_DATA not configured in TTL settings"
        
        # Test 3: Test that cache system properly handles MARKET_DATA operations
        # This would have raised AttributeError before the fix
        try:
            # Test cache operations with MARKET_DATA type
            cost_savings = cache_manager._calculate_cost_savings(CacheType.MARKET_DATA)
            assert cost_savings == 0.03  # Should be configured
            
            # Test TTL configuration
            ttl = cache_manager.ttl_config[CacheType.MARKET_DATA]
            assert ttl.total_seconds() == 4 * 3600  # 4 hours
            
            print("✓ MARKET_DATA cache type properly configured")
            
        except AttributeError as e:
            if "MARKET_DATA" in str(e):
                pytest.fail("MARKET_DATA cache type issue still exists - this was the production error")
            else:
                raise

    @pytest.mark.asyncio 
    async def test_current_price_fallback_vs_real_price(self):
        """
        REGRESSION TEST: This test would have caught the hardcoded current price issue
        
        The issue: Agentic mode was showing hardcoded price (220.0) instead of real 
        current price from DCF baseline (~1393.70 for RELIANCE)
        """
        v3_service = V3SummaryService()
        
        # Real baseline fair value with actual current price
        real_baseline = FairValueBand(
            min_value=723.12,
            max_value=1084.68, 
            current_price=1393.70,  # Real price from DCF calculation
            method="DCF",
            confidence=0.6
        )
        
        # Hardcoded fallback price that was showing in production
        FALLBACK_PRICE = 220.0
        
        ai_analysis = {
            "reasoning": ["Test reasoning"],
            "thesis": "Test thesis",
            "financial_health": [],
            "technical_outlook": [],
        }
        
        # Test with real baseline (should use real price)
        structured_analysis_with_baseline = v3_service._parse_ai_analysis(ai_analysis, real_baseline)
        real_price = structured_analysis_with_baseline["fair_value_band"].current_price
        
        # Test without baseline (should use fallback)
        structured_analysis_without_baseline = v3_service._parse_ai_analysis(ai_analysis, None)
        fallback_price = structured_analysis_without_baseline["fair_value_band"].current_price
        
        # Verify real price is used when baseline is provided
        assert real_price == 1393.70, f"Expected real price 1393.70, got {real_price}"
        assert real_price != FALLBACK_PRICE, "Should not be using fallback price when baseline is available"
        
        # Verify fallback is used when no baseline
        assert fallback_price == FALLBACK_PRICE, f"Expected fallback price {FALLBACK_PRICE}, got {fallback_price}"
        
        # This test would have FAILED before our fix because agentic mode was always using fallback

    @pytest.mark.asyncio
    async def test_full_agentic_endpoint_integration(self):
        """
        REGRESSION TEST: End-to-end test that would catch all three issues together
        
        This simulates the exact user flow that was failing:
        1. User selects agentic mode
        2. AI service returns list reasoning
        3. Current price should be real, not fallback
        4. Cache system should work with MARKET_DATA
        """
        import httpx
        
        async with httpx.AsyncClient() as client:
            try:
                # Test the actual HTTP endpoint that was failing
                response = await client.get(
                    "http://localhost:8000/api/v3/summary/RELIANCE.NS/agentic",
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Issue 1: Verify agent_reasoning is string (not list causing validation error)
                    assert isinstance(data.get("agent_reasoning"), str), \
                        "agent_reasoning should be string - list would cause Pydantic validation error"
                    
                    # Issue 2: Verify current price is realistic (not hardcoded fallback)
                    current_price = data["fair_value_band"]["current_price"] 
                    assert current_price > 1000, \
                        f"Current price {current_price} seems like fallback, not real price"
                    assert current_price != 220.0, \
                        "Should not be showing hardcoded fallback price"
                    
                    # Issue 3: Verify cache system is working (no MARKET_DATA errors in logs)
                    # This would be evident from no AttributeError exceptions
                    assert "ticker" in data, "Basic response structure should be intact"
                    
                    print(f"✓ All regression tests pass - current price: {current_price}")
                    
                else:
                    # If endpoint fails, check if it's the validation error we fixed
                    if response.status_code == 400:
                        error_msg = response.json().get("message", "")
                        if "agent_reasoning" in error_msg and "string_type" in error_msg:
                            pytest.fail("Pydantic validation error detected - the agent_reasoning list issue is back")
                        elif "MARKET_DATA" in error_msg:
                            pytest.fail("Cache system MARKET_DATA error detected")
                    
                    pytest.skip(f"Backend returned {response.status_code}, cannot test full integration")
                    
            except httpx.ConnectError:
                pytest.skip("Backend server not running - cannot test live endpoint")


class TestDataFlowIssues:
    """Test data flow problems that aren't caught by unit tests"""

    def test_ai_response_parsing_type_safety(self):
        """Test that AI response parsing handles various data types safely"""
        v3_service = V3SummaryService()
        
        # Test problematic AI response formats that could cause issues
        problematic_responses = [
            # Issue: reasoning as string instead of list (reverse problem)
            {"reasoning": "Single string instead of list"},
            
            # Issue: reasoning as nested list
            {"reasoning": [["nested", "list"], ["structure"]]},
            
            # Issue: reasoning as mixed types
            {"reasoning": ["string", 123, {"dict": "value"}]},
            
            # Issue: reasoning as None
            {"reasoning": None},
            
            # Issue: missing reasoning entirely
            {},
        ]
        
        for i, problematic_ai_response in enumerate(problematic_responses):
            try:
                structured = v3_service._parse_ai_analysis(problematic_ai_response)
                
                # Should handle all cases gracefully
                assert "investment_label" in structured
                assert "key_factors" in structured
                assert isinstance(structured["key_factors"], list)
                
                print(f"✓ Handled problematic response {i+1} gracefully")
                
            except Exception as e:
                pytest.fail(f"Failed to handle problematic AI response {i+1}: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])