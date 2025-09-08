"""
Comprehensive Test Suite for Enhanced Historical Validation Service

Tests the sophisticated historical analysis functionality for EquityScope v2.0
10-Year DCF System, covering:

- Multi-period CAGR analysis (3yr, 5yr, 7yr)
- Growth stage recommendations for Simple and Agentic modes
- Data quality validation and reliability scoring
- GDP blending logic and through-cycle adjustments
- Integration with Multi-Stage Growth Engine
- Educational content generation for progressive disclosure

Author: EquityScope Development Team
Date: July 29, 2025
Version: v2.0-enhanced-historical-validation
"""

import pytest
import asyncio
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch, MagicMock

from app.services.historical_validation import HistoricalValidationService, historical_validation_service
from app.models.dcf import DCFMode


class TestHistoricalValidationService:
    """Test suite for Enhanced Historical Validation Service."""
    
    @pytest.fixture
    def service(self):
        """Create service instance for testing."""
        return HistoricalValidationService()
    
    @pytest.fixture
    def mock_company_data(self):
        """Mock company data for testing."""
        return {
            'info': {
                'ticker': 'TCS.NS',
                'sector': 'Information Technology',
                'marketCap': 1000000000000,  # 1T market cap
                'quarterlyRevenueGrowth': 0.12
            }
        }
    
    @pytest.fixture
    def mock_historical_financials(self):
        """Mock 5 years of quarterly financial data."""
        
        # Generate realistic quarterly revenue data with growth
        base_revenue = 1000000000  # 1B base
        quarters = []
        revenues = {}
        
        # 5 years = 20 quarters
        for i in range(20):
            quarter_date = datetime.now() - timedelta(days=90 * (20-i))
            date_str = quarter_date.strftime('%Y-%m-%d')
            
            # Simulate growth with some seasonality
            growth_factor = (1.10) ** (i / 4)  # 10% annual growth
            seasonal_factor = 1.0 + 0.05 * np.sin(i * np.pi / 2)  # Small seasonal variation
            
            revenue = base_revenue * growth_factor * seasonal_factor
            revenues[date_str] = {
                'Total Revenue': revenue,
                'Operating Income': revenue * 0.2,  # 20% operating margin
                'Net Income': revenue * 0.15  # 15% net margin
            }
        
        return revenues
    
    @pytest.fixture
    def mock_comprehensive_historical_data(self, mock_historical_financials):
        """Mock comprehensive historical data structure."""
        return {
            'ticker': 'TCS.NS',
            'data_period': {
                'start_date': (datetime.now() - timedelta(days=365*7)).isoformat(),
                'end_date': datetime.now().isoformat(),
                'years_of_data': 7,
                'extended_analysis': True
            },
            'quarterly_financials': mock_historical_financials,
            'quarterly_balance_sheet': {},
            'quarterly_cashflow': {},
            'price_history': {},
            'fetched_at': datetime.now().isoformat(),
            'data_quality_flags': {
                'financials_available': True,
                'balance_sheet_available': True,
                'critical_data_missing': False
            }
        }


class TestDataQualityValidation:
    """Test data quality validation functionality."""
    
    @pytest.fixture
    def service(self):
        return HistoricalValidationService()
    
    def test_validate_data_quality_enhanced_sufficient_data(self, service, mock_comprehensive_historical_data):
        """Test data quality validation with sufficient data."""
        
        result = service._validate_data_quality_enhanced(mock_comprehensive_historical_data)
        
        assert result is True
    
    def test_validate_data_quality_enhanced_insufficient_data_points(self, service):
        """Test data quality validation with insufficient data points."""
        
        # Create data with only 2 quarters (insufficient)
        insufficient_data = {
            'quarterly_financials': {
                '2024-01-01': {'Total Revenue': 1000000},
                '2024-04-01': {'Total Revenue': 1100000}
            },
            'data_quality_flags': {'critical_data_missing': False}
        }
        
        result = service._validate_data_quality_enhanced(insufficient_data)
        
        assert result is False
    
    def test_validate_data_quality_enhanced_old_data(self, service):
        """Test data quality validation with old data."""
        
        # Create data that's 18 months old
        old_date = datetime.now() - timedelta(days=545)  # 18 months
        old_data = {
            'quarterly_financials': {
                old_date.strftime('%Y-%m-%d'): {'Total Revenue': 1000000}
                for i in range(15)  # Sufficient data points but old
            },
            'data_quality_flags': {'critical_data_missing': False}
        }
        
        result = service._validate_data_quality_enhanced(old_data)
        
        assert result is False
    
    def test_validate_data_quality_enhanced_critical_missing(self, service):
        """Test data quality validation with critical data missing."""
        
        critical_missing_data = {
            'quarterly_financials': {},
            'data_quality_flags': {'critical_data_missing': True}
        }
        
        result = service._validate_data_quality_enhanced(critical_missing_data)
        
        assert result is False


class TestMultiPeriodGrowthAnalysis:
    """Test multi-period CAGR analysis functionality."""
    
    @pytest.fixture
    def service(self):
        return HistoricalValidationService()
    
    @pytest.mark.asyncio
    async def test_analyze_multi_period_growth_complete_analysis(self, service, mock_comprehensive_historical_data):
        """Test complete multi-period growth analysis."""
        
        result = await service._analyze_multi_period_growth(mock_comprehensive_historical_data)
        
        # Should have analysis for 3, 5, and 7 year periods
        assert 'multi_period_cagr' in result
        assert '3yr' in result['multi_period_cagr']
        assert '5yr' in result['multi_period_cagr']
        
        # Check CAGR structure
        five_yr_analysis = result['multi_period_cagr']['5yr']
        assert 'cagr' in five_yr_analysis
        assert 'consistency_score' in five_yr_analysis
        assert 'reliability' in five_yr_analysis
        assert five_yr_analysis['reliability'] in ['high', 'medium', 'low']
        
        # Should have recommended base growth
        assert 'recommended_base_growth' in result
        assert isinstance(result['recommended_base_growth'], (int, float))
        
        # Should have GDP blending recommendations
        assert 'gdp_blending_recommendations' in result
    
    @pytest.mark.asyncio
    async def test_analyze_multi_period_growth_insufficient_data(self, service):
        """Test multi-period growth analysis with insufficient data."""
        
        insufficient_data = {
            'quarterly_financials': {
                '2024-01-01': {'Total Revenue': 1000000},
                '2024-04-01': {'Total Revenue': 1100000}
            }
        }
        
        result = await service._analyze_multi_period_growth(insufficient_data)
        
        assert result['insufficient_data'] is True
        assert 'reason' in result
    
    def test_calculate_growth_consistency_high_consistency(self, service):
        """Test growth consistency calculation with consistent growth rates."""
        
        # Consistent growth rates around 10%
        consistent_rates = [9.5, 10.2, 9.8, 10.5, 9.9]
        
        consistency = service._calculate_growth_consistency(consistent_rates)
        
        assert consistency > 0.8  # Should be high consistency
    
    def test_calculate_growth_consistency_low_consistency(self, service):
        """Test growth consistency calculation with volatile growth rates."""
        
        # Volatile growth rates
        volatile_rates = [5.0, 15.0, -2.0, 20.0, 8.0]
        
        consistency = service._calculate_growth_consistency(volatile_rates)
        
        assert consistency < 0.5  # Should be low consistency
    
    def test_determine_recommended_cagr_prioritizes_five_year(self, service):
        """Test that 5-year CAGR is prioritized when reliable."""
        
        cagr_analysis = {
            '3yr': {'cagr': 15.0, 'reliability': 'medium'},
            '5yr': {'cagr': 12.0, 'reliability': 'high'},
            '7yr': {'cagr': 10.0, 'reliability': 'high'}
        }
        
        recommended = service._determine_recommended_cagr(cagr_analysis)
        
        assert recommended == 12.0  # Should pick 5yr
    
    def test_determine_recommended_cagr_fallback_to_three_year(self, service):
        """Test fallback to 3-year when 5-year is unreliable."""
        
        cagr_analysis = {
            '3yr': {'cagr': 15.0, 'reliability': 'medium'},
            '5yr': {'cagr': 12.0, 'reliability': 'low'},
            '7yr': {'cagr': 10.0, 'reliability': 'low'}
        }
        
        recommended = service._determine_recommended_cagr(cagr_analysis)
        
        assert recommended == 15.0  # Should pick 3yr


class TestGrowthStageRecommendations:
    """Test growth stage recommendation functionality."""
    
    @pytest.fixture
    def service(self):
        return HistoricalValidationService()
    
    @pytest.mark.asyncio
    async def test_generate_growth_stage_recommendations_simple_mode(self, service, mock_comprehensive_historical_data):
        """Test growth stage recommendations for Simple Mode."""
        
        with patch.object(service, '_analyze_multi_period_growth') as mock_analysis:
            mock_analysis.return_value = {
                'recommended_base_growth': 12.0,
                'analysis_quality': {'overall_reliability': 0.8}
            }
            
            recommendations = await service._generate_growth_stage_recommendations(
                mock_comprehensive_historical_data, DCFMode.SIMPLE
            )
        
        # Should have 4 stages
        assert len(recommendations) == 4
        
        # Check stage structure
        stage_1_2 = recommendations[0]
        assert stage_1_2['years'] == '1-2'
        assert 'recommended_rate' in stage_1_2
        assert 'methodology' in stage_1_2
        assert 'confidence' in stage_1_2
        assert 'rationale' in stage_1_2
        
        # Should have conservative GDP blending for Simple Mode
        assert stage_1_2['methodology'] == 'historical_gdp_blend'
    
    @pytest.mark.asyncio
    async def test_generate_growth_stage_recommendations_agentic_mode(self, service, mock_comprehensive_historical_data):
        """Test growth stage recommendations for Agentic Mode."""
        
        with patch.object(service, '_analyze_multi_period_growth') as mock_analysis:
            mock_analysis.return_value = {
                'recommended_base_growth': 12.0,
                'analysis_quality': {'overall_reliability': 0.8}
            }
            
            recommendations = await service._generate_growth_stage_recommendations(
                mock_comprehensive_historical_data, DCFMode.AGENTIC
            )
        
        # Should have 4 stages
        assert len(recommendations) == 4
        
        # Check Agentic-specific methodology
        stage_1_2 = recommendations[0]
        assert stage_1_2['methodology'] == 'ai_enhanced_blend'
        
        # Early stages should have higher growth rates in Agentic mode
        stage_9_10 = recommendations[3]
        assert stage_9_10['years'] == '9-10'
        assert stage_9_10['recommended_rate'] == 3.0  # Should converge to GDP
    
    @pytest.mark.asyncio
    async def test_generate_growth_stage_recommendations_insufficient_data(self, service, mock_comprehensive_historical_data):
        """Test growth stage recommendations with insufficient data."""
        
        with patch.object(service, '_analyze_multi_period_growth') as mock_analysis:
            mock_analysis.return_value = {'insufficient_data': True}
            
            recommendations = await service._generate_growth_stage_recommendations(
                mock_comprehensive_historical_data, DCFMode.SIMPLE
            )
        
        # Should get conservative fallback recommendations
        assert len(recommendations) == 4
        
        # Should have conservative methodology
        stage_1_2 = recommendations[0]
        assert stage_1_2['methodology'] == 'conservative_estimate'
        assert stage_1_2['confidence'] == 'low'


class TestGDPBlendingLogic:
    """Test GDP blending logic and calculations."""
    
    @pytest.fixture
    def service(self):
        return HistoricalValidationService()
    
    def test_generate_gdp_blending_recommendations(self, service):
        """Test GDP blending recommendations generation."""
        
        base_cagr = 12.0
        cagr_analysis = {'5yr': {'cagr': 12.0, 'reliability': 'high'}}
        
        recommendations = service._generate_gdp_blending_recommendations(base_cagr, cagr_analysis)
        
        # Should have all required blending stages
        assert 'stage_1_2_blend' in recommendations
        assert 'stage_3_5_blend' in recommendations
        assert 'stage_6_8_blend' in recommendations
        assert 'stage_9_10_terminal' in recommendations
        
        # Check stage 1-2 blending (20% GDP weight)
        stage_1_2 = recommendations['stage_1_2_blend']
        assert stage_1_2['historical_weight'] == 0.8
        assert stage_1_2['gdp_weight'] == 0.2
        expected = (12.0 * 0.8) + (3.0 * 0.2)
        assert stage_1_2['result'] == round(expected, 1)
        
        # Check terminal stage (100% GDP)
        terminal = recommendations['stage_9_10_terminal']
        assert terminal['gdp_weight'] == 1.0
        assert terminal['result'] == 3.0


class TestEducationalContent:
    """Test educational content generation for progressive disclosure."""
    
    @pytest.fixture
    def service(self):
        return HistoricalValidationService()
    
    def test_generate_educational_insights(self, service, mock_comprehensive_historical_data):
        """Test educational insights generation."""
        
        insights = service._generate_educational_insights(mock_comprehensive_historical_data, DCFMode.SIMPLE)
        
        assert 'key_insight' in insights
        assert 'learning_point' in insights
        assert isinstance(insights['key_insight'], str)
        assert isinstance(insights['learning_point'], str)
    
    def test_generate_progressive_disclosure_content(self, service, mock_comprehensive_historical_data):
        """Test progressive disclosure content generation."""
        
        content = service._generate_progressive_disclosure_content(mock_comprehensive_historical_data, DCFMode.SIMPLE)
        
        # Should have content for all experience levels
        assert 'beginner' in content
        assert 'intermediate' in content
        assert 'advanced' in content
        
        # Content should be appropriate for each level
        assert 'Historical growth analysis' in content['beginner']
        assert 'Multi-period CAGR' in content['intermediate']
        assert 'Statistical reliability' in content['advanced']


class TestMainIntegrationMethod:
    """Test the main integration method for Multi-Stage Growth Engine."""
    
    @pytest.fixture
    def service(self):
        return HistoricalValidationService()
    
    @pytest.mark.asyncio
    async def test_generate_multi_stage_historical_validation_complete_flow(self, service, mock_company_data):
        """Test complete multi-stage historical validation flow."""
        
        with patch.object(service, '_fetch_comprehensive_historical_data') as mock_fetch, \
             patch.object(service, '_validate_data_quality_enhanced') as mock_validate, \
             patch.object(service, '_analyze_multi_period_growth') as mock_growth, \
             patch.object(service, '_analyze_margin_expansion_potential') as mock_margin, \
             patch.object(service, '_generate_growth_stage_recommendations') as mock_stages:
            
            # Setup mocks
            mock_fetch.return_value = {'ticker': 'TCS.NS', 'quarterly_financials': {}}
            mock_validate.return_value = True
            mock_growth.return_value = {
                'recommended_base_growth': 12.0,
                'multi_period_cagr': {'5yr': {'cagr': 12.0, 'reliability': 'high'}}
            }
            mock_margin.return_value = {'historical_margins': {'average_5yr': 20.0}}
            mock_stages.return_value = [
                {'years': '1-2', 'recommended_rate': 11.0, 'methodology': 'historical_gdp_blend'}
            ]
            
            result = await service.generate_multi_stage_historical_validation(
                'TCS.NS', DCFMode.SIMPLE, mock_company_data
            )
        
        # Should have all required components
        assert result['ticker'] == 'TCS.NS'
        assert result['mode'] == 'simple'
        assert 'multi_period_growth_analysis' in result
        assert 'margin_expansion_analysis' in result
        assert 'growth_stage_recommendations' in result
        assert 'validation_confidence' in result
        assert 'educational_insights' in result
    
    @pytest.mark.asyncio
    async def test_generate_multi_stage_historical_validation_insufficient_data(self, service, mock_company_data):
        """Test multi-stage validation with insufficient data."""
        
        with patch.object(service, '_fetch_comprehensive_historical_data') as mock_fetch, \
             patch.object(service, '_validate_data_quality_enhanced') as mock_validate:
            
            mock_fetch.return_value = {}
            mock_validate.return_value = False
            
            result = await service.generate_multi_stage_historical_validation(
                'TCS.NS', DCFMode.SIMPLE, mock_company_data
            )
        
        # Should return conservative validation
        assert result['validation_type'] == 'conservative_fallback'
        assert result['validation_confidence'] == 0.4
        assert 'educational_insights' in result
        assert 'data_limitation' in result['educational_insights']
    
    @pytest.mark.asyncio 
    async def test_generate_multi_stage_historical_validation_caching(self, service, mock_company_data):
        """Test caching functionality in multi-stage validation."""
        
        with patch('app.services.historical_validation.intelligent_cache') as mock_cache:
            # Mock cache hit
            cached_result = {
                'ticker': 'TCS.NS',
                'cached': True,
                'validation_confidence': 0.8
            }
            mock_cache.get.return_value = cached_result
            
            result = await service.generate_multi_stage_historical_validation(
                'TCS.NS', DCFMode.SIMPLE, mock_company_data
            )
        
        # Should return cached result
        assert result == cached_result
        mock_cache.get.assert_called_once()


class TestMarginAnalysis:
    """Test margin expansion analysis functionality."""
    
    @pytest.fixture
    def service(self):
        return HistoricalValidationService()
    
    @pytest.mark.asyncio
    async def test_analyze_margin_expansion_potential_complete(self, service, mock_comprehensive_historical_data):
        """Test complete margin expansion analysis."""
        
        result = await service._analyze_margin_expansion_potential(mock_comprehensive_historical_data)
        
        # Should have complete margin analysis
        assert 'historical_margins' in result
        assert 'trend_analysis' in result
        assert 'expansion_potential' in result
        assert 'recommended_margin_assumption' in result
        
        # Check historical margins structure
        historical = result['historical_margins']
        assert 'average_5yr' in historical
        assert 'recent_2yr' in historical
        assert 'trend_direction' in historical
        assert 'volatility' in historical
    
    def test_analyze_margin_trends_detailed_improving(self, service):
        """Test detailed margin trend analysis with improving trend."""
        
        # Create improving margin series
        improving_margins = pd.Series([15.0, 16.0, 17.0, 18.0, 19.0, 20.0])
        
        result = service._analyze_margin_trends_detailed(improving_margins)
        
        assert result['direction'] == 'improving'
        assert result['slope'] > 0.1
        assert result['recent_trend'] > 0  # Recent should be higher than early
    
    def test_analyze_margin_trends_detailed_deteriorating(self, service):
        """Test detailed margin trend analysis with deteriorating trend."""
        
        # Create deteriorating margin series
        deteriorating_margins = pd.Series([20.0, 19.0, 18.0, 17.0, 16.0, 15.0])
        
        result = service._analyze_margin_trends_detailed(deteriorating_margins)
        
        assert result['direction'] == 'deteriorating'
        assert result['slope'] < -0.1
        assert result['recent_trend'] < 0  # Recent should be lower than early
    
    def test_assess_margin_expansion_potential_high(self, service):
        """Test margin expansion potential assessment - high potential."""
        
        # Current margin below historical average
        margins = pd.Series([20.0, 22.0, 25.0, 23.0, 18.0])  # Current: 18%, Avg: ~21.6%
        
        result = service._assess_margin_expansion_potential_detailed(margins)
        
        assert result['potential'] == 'high'
        assert result['current_vs_avg'] < 0  # Current below average
        assert result['expansion_opportunity'] > 0


class TestPerformanceAndReliability:
    """Test performance and reliability aspects."""
    
    @pytest.fixture
    def service(self):
        return HistoricalValidationService()
    
    def test_service_initialization(self, service):
        """Test service initializes with correct parameters."""
        
        assert service.validation_period_years == 5
        assert service.extended_period_years == 7
        assert service.min_data_points == 12
        assert service.gdp_growth_rate == 3.0
        assert service.min_confidence_threshold == 0.6
        assert service.trend_reliability_threshold == 0.7
        assert service.data_recency_months == 12
    
    def test_conservative_fallback_generates_reasonable_values(self, service):
        """Test that conservative fallback generates reasonable values."""
        
        conservative_stages = service._generate_conservative_growth_stages(DCFMode.SIMPLE)
        
        # Should have 4 stages
        assert len(conservative_stages) == 4
        
        # Growth rates should be reasonable and declining
        rates = [stage['recommended_rate'] for stage in conservative_stages]
        assert all(3.0 <= rate <= 10.0 for rate in rates)  # Reasonable range
        assert rates[-1] == 3.0  # Should end at GDP rate
        
        # Should have low confidence
        assert all(stage['confidence'] == 'low' for stage in conservative_stages)


class TestDataExtractionMethods:
    """Test data extraction helper methods."""
    
    @pytest.fixture
    def service(self):
        return HistoricalValidationService()
    
    def test_extract_revenue_data(self, service, mock_historical_financials):
        """Test revenue data extraction."""
        
        revenue_data = service._extract_revenue_data(mock_historical_financials)
        
        assert len(revenue_data) == 20  # Should extract all 20 quarters
        assert all(isinstance(value, (int, float)) for value in revenue_data.values())
        assert all(value > 0 for value in revenue_data.values())  # All revenues positive
    
    def test_assess_seasonality_enhanced_detected(self, service):
        """Test seasonality detection with seasonal data."""
        
        # Create seasonal revenue pattern (Q4 higher)
        seasonal_data = []
        for year in range(5):
            seasonal_data.extend([100, 105, 110, 130])  # Q4 spike
        
        seasonal_series = pd.Series(seasonal_data)
        
        result = service._assess_seasonality_enhanced(seasonal_series)
        
        assert result['seasonality_detected'] is True
        assert result['coefficient_of_variation'] > 0.15
        assert 'Q4' in result['quarterly_pattern']
    
    def test_assess_seasonality_enhanced_no_seasonality(self, service):
        """Test seasonality detection with non-seasonal data."""
        
        # Create non-seasonal revenue pattern
        non_seasonal_data = [100 + i for i in range(20)]  # Steady growth
        non_seasonal_series = pd.Series(non_seasonal_data)
        
        result = service._assess_seasonality_enhanced(non_seasonal_series)
        
        assert result['seasonality_detected'] is False
        assert result['coefficient_of_variation'] <= 0.15


# Integration tests
class TestHistoricalValidationIntegration:
    """Integration tests for Historical Validation Service."""
    
    @pytest.mark.asyncio
    async def test_global_service_instance(self):
        """Test that global service instance works correctly."""
        
        # Test that the global instance is properly initialized
        assert historical_validation_service is not None
        assert isinstance(historical_validation_service, HistoricalValidationService)
        assert historical_validation_service.validation_period_years == 5
    
    @pytest.mark.asyncio
    async def test_integration_with_dcf_mode_enum(self):
        """Test integration with DCF mode enumeration."""
        
        # Should work with both modes
        simple_mode = DCFMode.SIMPLE
        agentic_mode = DCFMode.AGENTIC
        
        assert simple_mode.value == 'simple'
        assert agentic_mode.value == 'agentic'
        
        # Service methods should accept both modes
        conservative_simple = historical_validation_service._generate_conservative_growth_stages(simple_mode)
        conservative_agentic = historical_validation_service._generate_conservative_growth_stages(agentic_mode)
        
        assert len(conservative_simple) == 4
        assert len(conservative_agentic) == 4


if __name__ == '__main__':
    """Run tests with proper async support."""
    pytest.main([__file__, '-v', '--tb=short'])