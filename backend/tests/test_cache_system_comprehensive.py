"""
Comprehensive test suite for Intelligent Cache System
Tests MARKET_DATA enum issues and cache integration problems
"""

import pytest
from unittest.mock import patch, AsyncMock
from datetime import datetime, timedelta
import json
import tempfile
import shutil
from pathlib import Path

from app.services.intelligent_cache import CacheType, IntelligentCacheManager


class TestCacheTypeEnum:
    """Test CacheType enum completeness and consistency"""

    def test_all_required_cache_types_exist(self):
        """Test that all required cache types are defined"""
        required_types = [
            'FINANCIAL_DATA',
            'NEWS_ARTICLES', 
            'AI_INSIGHTS',
            'AI_ANALYSIS',
            'MODEL_RECOMMENDATIONS',
            'COMPANY_PROFILES',
            'MARKET_DATA'  # This was missing and caused errors
        ]
        
        for cache_type in required_types:
            assert hasattr(CacheType, cache_type), f"CacheType.{cache_type} is missing"
            
    def test_cache_type_values(self):
        """Test that cache type values are correctly set"""
        expected_values = {
            CacheType.FINANCIAL_DATA: "financial_data",
            CacheType.NEWS_ARTICLES: "news_articles",
            CacheType.AI_INSIGHTS: "ai_insights",
            CacheType.AI_ANALYSIS: "ai_analysis",
            CacheType.MODEL_RECOMMENDATIONS: "model_recs",
            CacheType.COMPANY_PROFILES: "company_profiles",
            CacheType.MARKET_DATA: "market_data"
        }
        
        for cache_type, expected_value in expected_values.items():
            assert cache_type.value == expected_value


class TestCacheManagerConfiguration:
    """Test IntelligentCacheManager configuration and TTL settings"""

    def test_cache_manager_initialization(self):
        """Test that cache manager initializes with all required configurations"""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_manager = IntelligentCacheManager(cache_dir=temp_dir)
            
            # Test TTL configuration exists for all cache types
            for cache_type in CacheType:
                assert cache_type in cache_manager.ttl_config, f"TTL not configured for {cache_type}"
                
            # Test specific TTL values
            assert cache_manager.ttl_config[CacheType.MARKET_DATA] == timedelta(hours=4)
            assert cache_manager.ttl_config[CacheType.AI_ANALYSIS] == timedelta(hours=6)
            assert cache_manager.ttl_config[CacheType.FINANCIAL_DATA] == timedelta(hours=24)
            
    def test_cost_savings_configuration(self):
        """Test that cost savings are configured for all cache types"""
        cache_manager = IntelligentCacheManager()
        
        for cache_type in CacheType:
            cost_savings = cache_manager._calculate_cost_savings(cache_type)
            assert cost_savings >= 0.0, f"Cost savings not configured for {cache_type}"
            
        # Test specific cost savings
        assert cache_manager._calculate_cost_savings(CacheType.AI_ANALYSIS) == 0.25  # Highest cost
        assert cache_manager._calculate_cost_savings(CacheType.MARKET_DATA) == 0.03


class TestCacheOperations:
    """Test cache CRUD operations"""

    @pytest.fixture
    def cache_manager(self):
        """Create cache manager with temporary directory"""
        temp_dir = tempfile.mkdtemp()
        manager = IntelligentCacheManager(cache_dir=temp_dir)
        yield manager
        shutil.rmtree(temp_dir)

    @pytest.mark.asyncio
    async def test_market_data_cache_operations(self, cache_manager):
        """Test caching market data (the type that was missing)"""
        
        test_data = {
            "risk_free_rate": 0.06,
            "market_return": 0.12,
            "beta": 1.2,
            "timestamp": datetime.now().isoformat()
        }
        
        # Test cache set
        result = await cache_manager.set(
            cache_type=CacheType.MARKET_DATA,
            identifier="NSE_RISK_FREE_RATE",
            data=test_data,
            extra_param="test"
        )
        assert result is True
        
        # Test cache get
        cached_data = await cache_manager.get(
            cache_type=CacheType.MARKET_DATA,
            identifier="NSE_RISK_FREE_RATE",
            extra_param="test"
        )
        assert cached_data is not None
        assert cached_data["risk_free_rate"] == 0.06
        
        # Verify cache hit stats
        assert cache_manager.stats['hits'] > 0

    @pytest.mark.asyncio
    async def test_ai_analysis_cache_operations(self, cache_manager):
        """Test caching AI analysis responses"""
        
        ai_response = {
            "reasoning": ["Analysis point 1", "Analysis point 2"],
            "thesis": "Investment thesis",
            "financial_health": ["Strong metrics"],
            "cost_info": {"tokens": 1500, "cost": 0.05}
        }
        
        # Test cache set
        result = await cache_manager.set(
            cache_type=CacheType.AI_ANALYSIS,
            identifier="RELIANCE.NS",
            data=ai_response,
            mode="agentic"
        )
        assert result is True
        
        # Test cache get
        cached_analysis = await cache_manager.get(
            cache_type=CacheType.AI_ANALYSIS,
            identifier="RELIANCE.NS",
            mode="agentic"
        )
        assert cached_analysis is not None
        assert cached_analysis["reasoning"] == ["Analysis point 1", "Analysis point 2"]

    @pytest.mark.asyncio
    async def test_cache_key_generation_consistency(self, cache_manager):
        """Test that cache keys are generated consistently"""
        
        # Same parameters should generate same key
        key1 = cache_manager._generate_cache_key(
            CacheType.MARKET_DATA, 
            "TEST_TICKER",
            param1="value1",
            param2="value2"
        )
        
        key2 = cache_manager._generate_cache_key(
            CacheType.MARKET_DATA,
            "TEST_TICKER", 
            param2="value2",  # Different order
            param1="value1"
        )
        
        assert key1 == key2  # Should be same due to sorted keys
        
        # Different parameters should generate different keys
        key3 = cache_manager._generate_cache_key(
            CacheType.MARKET_DATA,
            "TEST_TICKER",
            param1="different_value",
            param2="value2"
        )
        
        assert key1 != key3


class TestCacheExpiration:
    """Test cache expiration and cleanup"""

    @pytest.fixture
    def cache_manager(self):
        """Create cache manager with temporary directory"""
        temp_dir = tempfile.mkdtemp()
        manager = IntelligentCacheManager(cache_dir=temp_dir)
        yield manager
        shutil.rmtree(temp_dir)

    @pytest.mark.asyncio
    async def test_expired_cache_cleanup(self, cache_manager):
        """Test that expired cache entries are properly cleaned up"""
        
        # Mock short TTL for testing
        original_ttl = cache_manager.ttl_config[CacheType.MARKET_DATA]
        cache_manager.ttl_config[CacheType.MARKET_DATA] = timedelta(seconds=1)
        
        try:
            # Set cache data
            await cache_manager.set(
                cache_type=CacheType.MARKET_DATA,
                identifier="EXPIRED_TEST",
                data={"test": "data"}
            )
            
            # Verify data exists
            data = await cache_manager.get(
                cache_type=CacheType.MARKET_DATA,
                identifier="EXPIRED_TEST"
            )
            assert data is not None
            
            # Wait for expiration
            import asyncio
            await asyncio.sleep(2)
            
            # Verify data is expired
            expired_data = await cache_manager.get(
                cache_type=CacheType.MARKET_DATA,
                identifier="EXPIRED_TEST"
            )
            assert expired_data is None
            
        finally:
            # Restore original TTL
            cache_manager.ttl_config[CacheType.MARKET_DATA] = original_ttl


class TestSectorIntelligenceServiceCacheIntegration:
    """Test that SectorIntelligenceService properly uses MARKET_DATA cache"""

    @pytest.mark.asyncio
    async def test_risk_free_rate_caching(self):
        """Test that risk-free rate fetching uses MARKET_DATA cache correctly"""
        from app.services.sector_intelligence_service import SectorIntelligenceService
        
        service = SectorIntelligenceService()
        
        # This should not raise AttributeError: 'CacheType' object has no attribute 'MARKET_DATA'
        # (which was the original error we encountered)
        try:
            with patch.object(service.data_service, 'get_indian_10y_bond_yield', return_value=6.5):
                risk_free_rate = await service._fetch_risk_free_rate()
                assert risk_free_rate >= 0.0
                
        except AttributeError as e:
            if "MARKET_DATA" in str(e):
                pytest.fail("MARKET_DATA cache type still not properly configured")
            else:
                raise


class TestCacheStatsAndMetrics:
    """Test cache statistics and performance metrics"""

    @pytest.fixture
    def cache_manager(self):
        """Create cache manager with temporary directory"""
        temp_dir = tempfile.mkdtemp()
        manager = IntelligentCacheManager(cache_dir=temp_dir)
        yield manager
        shutil.rmtree(temp_dir)

    @pytest.mark.asyncio
    async def test_cache_stats_tracking(self, cache_manager):
        """Test that cache statistics are properly tracked"""
        
        # Initial stats should be zero
        initial_stats = await cache_manager.get_cache_stats()
        assert initial_stats['cache_statistics']['total_requests'] == 0
        
        # Perform cache operations
        await cache_manager.set(CacheType.AI_ANALYSIS, "TEST", {"data": "test"})
        
        # Cache hit
        data = await cache_manager.get(CacheType.AI_ANALYSIS, "TEST")
        assert data is not None
        
        # Cache miss  
        missing = await cache_manager.get(CacheType.AI_ANALYSIS, "MISSING")
        assert missing is None
        
        # Check updated stats
        final_stats = await cache_manager.get_cache_stats()
        assert final_stats['cache_statistics']['cache_hits'] == 1
        assert final_stats['cache_statistics']['cache_misses'] == 1
        assert final_stats['cache_statistics']['total_requests'] == 2
        
    @pytest.mark.asyncio
    async def test_cost_savings_calculation(self, cache_manager):
        """Test that cost savings are properly calculated and tracked"""
        
        # Set and get data to trigger cost savings calculation
        await cache_manager.set(CacheType.AI_ANALYSIS, "COST_TEST", {"expensive": "analysis"})
        await cache_manager.get(CacheType.AI_ANALYSIS, "COST_TEST")
        
        stats = await cache_manager.get_cache_stats()
        
        # Should have recorded cost savings
        assert stats['cache_statistics']['total_cost_saved_usd'] > 0
        assert stats['ttl_configuration']['ai_analysis']['estimated_cost_savings_per_hit'] == 0.25


if __name__ == "__main__":
    pytest.main([__file__, "-v"])