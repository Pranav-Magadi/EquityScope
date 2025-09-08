import pytest
import asyncio
import tempfile
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch, MagicMock

from backend.app.services.intelligent_cache import (
    IntelligentCacheManager, CacheType
)

class TestIntelligentCacheManager:
    """
    TDD tests for IntelligentCacheManager.
    
    Test Coverage:
    - Cache storage and retrieval
    - TTL expiration logic
    - Cache statistics and monitoring
    - Background cleanup tasks
    - Performance optimization scenarios
    """
    
    @pytest.fixture
    def temp_cache_dir(self):
        """Create temporary directory for cache testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def cache_manager(self, temp_cache_dir):
        """Create cache manager instance for testing."""
        return IntelligentCacheManager(cache_dir=temp_cache_dir)
    
    @pytest.fixture
    def sample_financial_data(self):
        """Sample financial data for testing."""
        return {
            'ticker': 'TCS.NS',
            'info': {
                'longName': 'Tata Consultancy Services',
                'sector': 'Information Technology',
                'currentPrice': 3850.0,
                'marketCap': 12000000000000
            },
            'history': {'2024-01-01': 3800.0, '2024-01-02': 3820.0},
            'financials': {'revenue': 500000000000}
        }
    
    @pytest.fixture
    def sample_news_data(self):
        """Sample news data for testing."""
        return [
            {
                'title': 'TCS Reports Strong Q4 Results',
                'summary': 'TCS posted strong growth in Q4',
                'url': 'https://example.com/news1',
                'published': '2024-01-15T10:00:00Z'
            },
            {
                'title': 'TCS Wins Major Contract',
                'summary': 'TCS secures large digital transformation deal',
                'url': 'https://example.com/news2', 
                'published': '2024-01-14T15:30:00Z'
            }
        ]
    
    def test_cache_manager_initialization(self, cache_manager, temp_cache_dir):
        """Test cache manager initialization."""
        assert cache_manager is not None
        assert cache_manager.cache_dir == Path(temp_cache_dir)
        assert cache_manager.cache_dir.exists()
        
        # Check TTL configuration
        assert CacheType.FINANCIAL_DATA in cache_manager.ttl_config
        assert CacheType.NEWS_ARTICLES in cache_manager.ttl_config
        assert CacheType.AI_INSIGHTS in cache_manager.ttl_config
        
        # Check statistics initialization
        assert cache_manager.stats['hits'] == 0
        assert cache_manager.stats['misses'] == 0
    
    def test_cache_key_generation(self, cache_manager):
        """Test consistent cache key generation."""
        
        # Same parameters should generate same key
        key1 = cache_manager._generate_cache_key(
            CacheType.FINANCIAL_DATA, 'TCS.NS'
        )
        key2 = cache_manager._generate_cache_key(
            CacheType.FINANCIAL_DATA, 'TCS.NS'
        )
        assert key1 == key2
        
        # Different parameters should generate different keys
        key3 = cache_manager._generate_cache_key(
            CacheType.NEWS_ARTICLES, 'TCS.NS'
        )
        assert key1 != key3
        
        # Additional parameters should affect key
        key4 = cache_manager._generate_cache_key(
            CacheType.NEWS_ARTICLES, 'TCS.NS', max_articles=5
        )
        key5 = cache_manager._generate_cache_key(
            CacheType.NEWS_ARTICLES, 'TCS.NS', max_articles=10
        )
        assert key4 != key5
    
    @pytest.mark.asyncio
    async def test_cache_set_and_get(self, cache_manager, sample_financial_data):
        """Test basic cache storage and retrieval."""
        
        ticker = 'TCS.NS'
        
        # Initially no cache hit
        cached_data = await cache_manager.get(CacheType.FINANCIAL_DATA, ticker)
        assert cached_data is None
        assert cache_manager.stats['misses'] == 1
        
        # Store data in cache
        success = await cache_manager.set(
            CacheType.FINANCIAL_DATA, ticker, sample_financial_data
        )
        assert success is True
        
        # Retrieve cached data
        cached_data = await cache_manager.get(CacheType.FINANCIAL_DATA, ticker)
        assert cached_data is not None
        assert cached_data == sample_financial_data
        assert cache_manager.stats['hits'] == 1
        
        # Verify cache file exists
        cache_files = list(cache_manager.cache_dir.glob('*.json'))
        assert len(cache_files) == 1
    
    @pytest.mark.asyncio
    async def test_cache_ttl_expiration(self, cache_manager, sample_financial_data):
        """Test cache TTL expiration logic."""
        
        ticker = 'TCS.NS'
        
        # Mock TTL to be very short for testing
        original_ttl = cache_manager.ttl_config[CacheType.FINANCIAL_DATA]
        cache_manager.ttl_config[CacheType.FINANCIAL_DATA] = timedelta(milliseconds=100)
        
        try:
            # Store data
            await cache_manager.set(CacheType.FINANCIAL_DATA, ticker, sample_financial_data)
            
            # Immediately retrieve - should hit
            cached_data = await cache_manager.get(CacheType.FINANCIAL_DATA, ticker)
            assert cached_data is not None
            assert cache_manager.stats['hits'] == 1
            
            # Wait for expiration
            await asyncio.sleep(0.2)  # 200ms > 100ms TTL
            
            # Should be expired now
            cached_data = await cache_manager.get(CacheType.FINANCIAL_DATA, ticker)
            assert cached_data is None
            assert cache_manager.stats['misses'] == 1
            assert cache_manager.stats['evictions'] == 1
            
        finally:
            # Restore original TTL
            cache_manager.ttl_config[CacheType.FINANCIAL_DATA] = original_ttl
    
    @pytest.mark.asyncio
    async def test_cache_with_parameters(self, cache_manager, sample_news_data):
        """Test cache key generation with additional parameters."""
        
        ticker = 'TCS.NS'
        
        # Cache with different parameters
        await cache_manager.set(
            CacheType.NEWS_ARTICLES, ticker, sample_news_data, max_articles=5
        )
        
        # Retrieve with same parameters - should hit
        cached_data = await cache_manager.get(
            CacheType.NEWS_ARTICLES, ticker, max_articles=5
        )
        assert cached_data == sample_news_data
        assert cache_manager.stats['hits'] == 1
        
        # Retrieve with different parameters - should miss
        cached_data = await cache_manager.get(
            CacheType.NEWS_ARTICLES, ticker, max_articles=10
        )
        assert cached_data is None
        assert cache_manager.stats['misses'] == 1
    
    @pytest.mark.asyncio
    async def test_cache_invalidation(self, cache_manager, sample_financial_data):
        """Test manual cache invalidation."""
        
        ticker = 'TCS.NS'
        
        # Store and verify
        await cache_manager.set(CacheType.FINANCIAL_DATA, ticker, sample_financial_data)
        cached_data = await cache_manager.get(CacheType.FINANCIAL_DATA, ticker)
        assert cached_data is not None
        
        # Invalidate
        success = await cache_manager.invalidate(CacheType.FINANCIAL_DATA, ticker)
        assert success is True
        
        # Should be gone now
        cached_data = await cache_manager.get(CacheType.FINANCIAL_DATA, ticker)
        assert cached_data is None
        
        # Invalidating non-existent cache should return False
        success = await cache_manager.invalidate(CacheType.FINANCIAL_DATA, 'NONEXISTENT')
        assert success is False
    
    @pytest.mark.asyncio
    async def test_cache_cleanup_expired(self, cache_manager, sample_financial_data):
        """Test cleanup of expired cache entries."""
        
        # Create multiple cache entries with short TTL
        tickers = ['TCS.NS', 'RELIANCE.NS', 'HDFCBANK.NS']
        original_ttl = cache_manager.ttl_config[CacheType.FINANCIAL_DATA]
        cache_manager.ttl_config[CacheType.FINANCIAL_DATA] = timedelta(milliseconds=50)
        
        try:
            # Store multiple entries
            for ticker in tickers:
                await cache_manager.set(CacheType.FINANCIAL_DATA, ticker, sample_financial_data)
            
            # Verify all are cached
            cache_files = list(cache_manager.cache_dir.glob('*.json'))
            assert len(cache_files) == 3
            
            # Wait for expiration
            await asyncio.sleep(0.1)  # 100ms > 50ms TTL
            
            # Run cleanup
            cleaned_count = await cache_manager.cleanup_expired()
            assert cleaned_count == 3
            
            # Verify files are gone
            cache_files = list(cache_manager.cache_dir.glob('*.json'))
            assert len(cache_files) == 0
            
        finally:
            cache_manager.ttl_config[CacheType.FINANCIAL_DATA] = original_ttl
    
    @pytest.mark.asyncio
    async def test_cache_statistics(self, cache_manager, sample_financial_data):
        """Test cache statistics calculation."""
        
        ticker = 'TCS.NS'
        
        # Generate some cache activity
        await cache_manager.get(CacheType.FINANCIAL_DATA, ticker)  # Miss
        await cache_manager.set(CacheType.FINANCIAL_DATA, ticker, sample_financial_data)
        await cache_manager.get(CacheType.FINANCIAL_DATA, ticker)  # Hit
        await cache_manager.get(CacheType.FINANCIAL_DATA, ticker)  # Hit
        await cache_manager.get(CacheType.NEWS_ARTICLES, ticker)  # Miss
        
        stats = await cache_manager.get_cache_stats()
        
        # Verify statistics structure
        assert 'cache_statistics' in stats
        assert 'cache_storage' in stats
        assert 'ttl_configuration' in stats
        
        cache_stats = stats['cache_statistics']
        assert cache_stats['total_requests'] == 4  # 3 gets after set
        assert cache_stats['cache_hits'] == 2
        assert cache_stats['cache_misses'] == 2
        assert cache_stats['hit_rate_percentage'] == 50.0
        assert cache_stats['total_cost_saved_usd'] > 0
        
        # Verify storage stats
        storage_stats = stats['cache_storage']
        assert storage_stats['cache_files'] == 1
        assert storage_stats['storage_size_mb'] >= 0
        
        # Verify TTL config
        ttl_config = stats['ttl_configuration']
        assert 'financial_data' in ttl_config
        assert ttl_config['financial_data']['ttl_hours'] == 24.0
        assert ttl_config['news_articles']['ttl_hours'] == 6.0
        assert ttl_config['ai_insights']['ttl_hours'] == 6.0
    
    def test_cost_savings_calculation(self, cache_manager):
        """Test cost savings calculation for different cache types."""
        
        # AI insights should have highest savings
        ai_savings = cache_manager._calculate_cost_savings(CacheType.AI_INSIGHTS)
        financial_savings = cache_manager._calculate_cost_savings(CacheType.FINANCIAL_DATA)
        news_savings = cache_manager._calculate_cost_savings(CacheType.NEWS_ARTICLES)
        
        assert ai_savings > financial_savings
        assert news_savings > financial_savings
        assert ai_savings > 0.20  # Should save significant AI costs
    
    @pytest.mark.asyncio
    async def test_cache_warming_functionality(self, cache_manager):
        """Test cache warming for popular stocks."""
        
        popular_tickers = ['TCS.NS', 'RELIANCE.NS', 'HDFCBANK.NS']
        
        # Test cache warming (mocked since we don't want real API calls)
        with patch.object(cache_manager, 'get') as mock_get:
            mock_get.return_value = None  # Simulate cache miss
            
            results = await cache_manager.warm_cache_for_popular_stocks(
                popular_tickers, cache_financial=True, cache_news=False
            )
            
            assert 'financial_cached' in results
            assert 'news_cached' in results
            assert 'errors' in results
            assert results['errors'] == 0
    
    @pytest.mark.asyncio
    async def test_concurrent_cache_access(self, cache_manager, sample_financial_data):
        """Test concurrent cache access doesn't cause issues."""
        
        ticker = 'TCS.NS'
        
        # Store initial data
        await cache_manager.set(CacheType.FINANCIAL_DATA, ticker, sample_financial_data)
        
        # Create concurrent get operations
        async def get_cached_data():
            return await cache_manager.get(CacheType.FINANCIAL_DATA, ticker)
        
        # Run multiple concurrent gets
        tasks = [get_cached_data() for _ in range(10)]
        results = await asyncio.gather(*tasks)
        
        # All should return the same data
        for result in results:
            assert result == sample_financial_data
        
        # Should register multiple hits
        assert cache_manager.stats['hits'] >= 10
    
    @pytest.mark.asyncio
    async def test_cache_error_handling(self, cache_manager):
        """Test cache error handling with corrupted data."""
        
        ticker = 'TCS.NS'
        
        # Create corrupted cache file
        cache_key = cache_manager._generate_cache_key(CacheType.FINANCIAL_DATA, ticker)
        cache_path = cache_manager._get_cache_path(cache_key)
        
        # Write invalid JSON
        with open(cache_path, 'w') as f:
            f.write('invalid json content')
        
        # Should handle gracefully and return None
        cached_data = await cache_manager.get(CacheType.FINANCIAL_DATA, ticker)
        assert cached_data is None
        assert cache_manager.stats['misses'] == 1
    
    @pytest.mark.asyncio
    async def test_multiple_cache_types(self, cache_manager, sample_financial_data, sample_news_data):
        """Test different cache types with different TTLs."""
        
        ticker = 'TCS.NS'
        
        # Store different types of data
        await cache_manager.set(CacheType.FINANCIAL_DATA, ticker, sample_financial_data)
        await cache_manager.set(CacheType.NEWS_ARTICLES, ticker, sample_news_data)
        
        # Both should be retrievable
        financial_data = await cache_manager.get(CacheType.FINANCIAL_DATA, ticker)
        news_data = await cache_manager.get(CacheType.NEWS_ARTICLES, ticker)
        
        assert financial_data == sample_financial_data
        assert news_data == sample_news_data
        assert cache_manager.stats['hits'] == 2
        
        # Should have 2 cache files
        cache_files = list(cache_manager.cache_dir.glob('*.json'))
        assert len(cache_files) == 2

if __name__ == "__main__":
    pytest.main([__file__, "-v"])