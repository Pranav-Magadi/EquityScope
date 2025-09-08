import pytest
from unittest.mock import MagicMock, patch
from backend.app.services.multi_model_dcf import (
    ValuationModel, IndustryClassifier, MultiModelDCFService
)

class TestIndustryClassifier:
    """
    TDD tests for IndustryClassifier.
    
    Test Coverage:
    - Industry classification accuracy
    - Model recommendation logic
    - Indian market specific mappings
    - Edge cases and error handling
    """
    
    @pytest.fixture
    def classifier(self):
        """Create classifier instance for testing."""
        return IndustryClassifier()
    
    def test_initialization(self, classifier):
        """Test classifier initialization."""
        assert classifier is not None
        assert hasattr(classifier, 'banking_keywords')
        assert hasattr(classifier, 'asset_heavy_keywords')
        assert hasattr(classifier, 'dcf_preferred_keywords')
        assert hasattr(classifier, 'indian_sector_mappings')
        
        # Check that model rationales are set up
        assert ValuationModel.DCF in classifier.model_rationales
        assert ValuationModel.DDM in classifier.model_rationales
        assert ValuationModel.ASSET in classifier.model_rationales
    
    def test_banking_company_classification(self, classifier):
        """Test classification of banking companies."""
        
        # HDFC Bank - should recommend DDM
        hdfc_info = {
            'sector': 'Private Sector Bank',
            'industry': 'Commercial Banks'
        }
        
        model, rationale, confidence = classifier.classify_company('HDFCBANK.NS', hdfc_info)
        
        assert model == ValuationModel.DDM
        assert 'DDM' in rationale
        assert confidence >= 0.8
        
        # SBI - Public sector bank
        sbi_info = {
            'sector': 'Public Sector Bank',
            'industry': 'Commercial Banks'
        }
        
        model, rationale, confidence = classifier.classify_company('SBIN.NS', sbi_info)
        
        assert model == ValuationModel.DDM
        assert confidence >= 0.8
    
    def test_technology_company_classification(self, classifier):
        """Test classification of technology companies."""
        
        # TCS - should recommend DCF
        tcs_info = {
            'sector': 'Information Technology',
            'industry': 'Information Technology Services'
        }
        
        model, rationale, confidence = classifier.classify_company('TCS.NS', tcs_info)
        
        assert model == ValuationModel.DCF
        assert 'DCF' in rationale
        assert confidence >= 0.7
        
        # Generic technology company
        tech_info = {
            'sector': 'Technology',
            'industry': 'Software'
        }
        
        model, rationale, confidence = classifier.classify_company('TECH.NS', tech_info)
        
        assert model == ValuationModel.DCF
    
    def test_asset_heavy_company_classification(self, classifier):
        """Test classification of asset-heavy companies."""
        
        # REIT company
        reit_info = {
            'sector': 'Real Estate',
            'industry': 'REIT'
        }
        
        model, rationale, confidence = classifier.classify_company('REIT.NS', reit_info)
        
        assert model == ValuationModel.ASSET
        assert 'Asset' in rationale
        assert confidence >= 0.7
        
        # Utility company
        utility_info = {
            'sector': 'Utilities',
            'industry': 'Electric Utilities'
        }
        
        model, rationale, confidence = classifier.classify_company('POWER.NS', utility_info)
        
        assert model == ValuationModel.ASSET
        
        # Infrastructure company
        infra_info = {
            'sector': 'Infrastructure',
            'industry': 'Infrastructure'
        }
        
        model, rationale, confidence = classifier.classify_company('INFRA.NS', infra_info)
        
        assert model == ValuationModel.ASSET
    
    def test_indian_sector_priority(self, classifier):
        """Test that Indian sector mappings take priority."""
        
        # Case where Indian sector mapping should override generic keywords
        mixed_info = {
            'sector': 'Private Sector Bank',  # Indian specific
            'industry': 'Technology Services'  # Generic tech keyword
        }
        
        model, rationale, confidence = classifier.classify_company('MIXED.NS', mixed_info)
        
        # Should prioritize Indian sector mapping (DDM) over generic industry (DCF)
        assert model == ValuationModel.DDM
        assert confidence >= 0.8
    
    def test_default_classification(self, classifier):
        """Test default classification for unknown sectors."""
        
        unknown_info = {
            'sector': 'Unknown Sector',
            'industry': 'Unknown Industry'
        }
        
        model, rationale, confidence = classifier.classify_company('UNKNOWN.NS', unknown_info)
        
        assert model == ValuationModel.DCF  # Default to DCF
        assert 'Default DCF' in rationale
        assert confidence <= 0.7  # Lower confidence for defaults
    
    def test_missing_sector_info(self, classifier):
        """Test handling of missing sector information."""
        
        # Empty info
        empty_info = {}
        model, rationale, confidence = classifier.classify_company('EMPTY.NS', empty_info)
        assert model == ValuationModel.DCF
        
        # None values
        none_info = {'sector': None, 'industry': None}
        model, rationale, confidence = classifier.classify_company('NONE.NS', none_info)
        assert model == ValuationModel.DCF
    
    def test_keyword_matching(self, classifier):
        """Test keyword matching logic."""
        
        # Test partial keyword matching
        partial_banking = {
            'sector': 'Financial Services',
            'industry': 'Investment Banking Services'
        }
        
        model, rationale, confidence = classifier.classify_company('INVEST.NS', partial_banking)
        assert model == ValuationModel.DDM
        
        # Test case insensitive matching
        case_test = {
            'sector': 'BANKING',
            'industry': 'commercial banks'
        }
        
        model, rationale, confidence = classifier.classify_company('CASE.NS', case_test)
        assert model == ValuationModel.DDM
    
    def test_model_info_retrieval(self, classifier):
        """Test model information retrieval."""
        
        dcf_info = classifier.get_model_info(ValuationModel.DCF)
        assert 'description' in dcf_info
        assert 'best_for' in dcf_info
        assert 'reasoning' in dcf_info
        assert 'examples' in dcf_info
        
        ddm_info = classifier.get_model_info(ValuationModel.DDM)
        assert 'Dividend Discount Model' in ddm_info['description']
        
        asset_info = classifier.get_model_info(ValuationModel.ASSET)
        assert 'Asset-Based' in asset_info['description']

class TestMultiModelDCFService:
    """
    TDD tests for MultiModelDCFService.
    
    Test Coverage:
    - Model recommendation accuracy
    - Multi-model calculations
    - Assumption generation
    - Valuation summaries
    """
    
    @pytest.fixture
    def dcf_service(self):
        """Create DCF service instance for testing."""
        return MultiModelDCFService()
    
    @pytest.fixture
    def sample_banking_data(self):
        """Sample banking company data."""
        return {
            'ticker': 'HDFCBANK.NS',
            'info': {
                'longName': 'HDFC Bank Limited',
                'sector': 'Private Sector Bank',
                'industry': 'Commercial Banks',
                'marketCap': 8500000000000,  # 8.5 lakh crores
                'currentPrice': 1650.0,
                'dividendYield': 0.012,  # 1.2%
                'returnOnEquity': 0.18,  # 18%
                'beta': 0.9,
                'bookValue': 450.0,
                'priceToBook': 3.67
            }
        }
    
    @pytest.fixture
    def sample_tech_data(self):
        """Sample technology company data."""
        return {
            'ticker': 'TCS.NS',
            'info': {
                'longName': 'Tata Consultancy Services',
                'sector': 'Information Technology',
                'industry': 'Information Technology Services',
                'marketCap': 12000000000000,  # 12 lakh crores
                'currentPrice': 3850.0,
                'profitMargins': 0.22,
                'returnOnEquity': 0.45,
                'beta': 0.8,
                'quarterlyRevenueGrowth': 0.08
            }
        }
    
    @pytest.fixture
    def sample_reit_data(self):
        """Sample REIT/asset-heavy company data."""
        return {
            'ticker': 'REIT.NS',
            'info': {
                'longName': 'Real Estate Investment Trust',
                'sector': 'Real Estate',
                'industry': 'REIT',
                'marketCap': 500000000000,  # 50k crores
                'currentPrice': 850.0,
                'bookValue': 750.0,
                'priceToBook': 1.13,
                'returnOnEquity': 0.12,
                'totalRevenue': 10000000000,
                'totalAssets': 15000000000
            }
        }
    
    def test_service_initialization(self, dcf_service):
        """Test service initialization."""
        assert dcf_service is not None
        assert hasattr(dcf_service, 'classifier')
        assert hasattr(dcf_service, 'default_assumptions')
        
        # Check that default assumptions are set for all models
        assert ValuationModel.DCF in dcf_service.default_assumptions
        assert ValuationModel.DDM in dcf_service.default_assumptions
        assert ValuationModel.ASSET in dcf_service.default_assumptions
    
    @pytest.mark.asyncio
    async def test_banking_model_recommendation(self, dcf_service, sample_banking_data):
        """Test model recommendation for banking company."""
        
        result = await dcf_service.recommend_model_and_assumptions(
            'HDFCBANK.NS', sample_banking_data
        )
        
        assert result is not None
        assert 'recommended_model' in result
        assert 'default_assumptions' in result
        assert 'alternative_models' in result
        assert 'company_context' in result
        
        # Should recommend DDM for banking
        recommended = result['recommended_model']
        assert recommended['model'] == 'DDM'
        assert recommended['confidence_score'] >= 0.8
        assert 'DDM' in recommended['rationale']
        
        # Should provide DDM-specific assumptions
        assumptions = result['default_assumptions']
        assert 'dividend_growth_rate' in assumptions
        assert 'roe' in assumptions
        assert 'cost_of_equity' in assumptions
        
        # Should suggest alternatives
        alternatives = result['alternative_models']
        assert 'DCF' in alternatives or 'Asset' in alternatives
    
    @pytest.mark.asyncio
    async def test_tech_model_recommendation(self, dcf_service, sample_tech_data):
        """Test model recommendation for technology company."""
        
        result = await dcf_service.recommend_model_and_assumptions(
            'TCS.NS', sample_tech_data
        )
        
        # Should recommend DCF for technology
        recommended = result['recommended_model']
        assert recommended['model'] == 'DCF'
        assert recommended['confidence_score'] >= 0.7
        
        # Should provide DCF-specific assumptions
        assumptions = result['default_assumptions']
        assert 'revenue_growth_rate' in assumptions
        assert 'ebitda_margin' in assumptions
        assert 'wacc' in assumptions
        
        # Assumptions should be reasonable for tech company
        assert 0 < assumptions['revenue_growth_rate'] <= 20.0
        assert 0 < assumptions['ebitda_margin'] <= 35.0
        assert 8.0 <= assumptions['wacc'] <= 16.0
    
    @pytest.mark.asyncio
    async def test_reit_model_recommendation(self, dcf_service, sample_reit_data):
        """Test model recommendation for REIT/asset-heavy company."""
        
        result = await dcf_service.recommend_model_and_assumptions(
            'REIT.NS', sample_reit_data
        )
        
        # Should recommend Asset model for REIT
        recommended = result['recommended_model']
        assert recommended['model'] == 'Asset'
        assert recommended['confidence_score'] >= 0.7
        
        # Should provide Asset-specific assumptions
        assumptions = result['default_assumptions']
        assert 'book_value_growth' in assumptions
        assert 'roe' in assumptions
        assert 'asset_turnover' in assumptions
    
    @pytest.mark.asyncio
    async def test_dcf_assumption_generation(self, dcf_service, sample_tech_data):
        """Test DCF assumption generation logic."""
        
        info = sample_tech_data['info']
        assumptions = await dcf_service._generate_dcf_assumptions(info)
        
        assert isinstance(assumptions, dict)
        assert 'revenue_growth_rate' in assumptions
        assert 'ebitda_margin' in assumptions
        assert 'tax_rate' in assumptions
        assert 'wacc' in assumptions
        assert 'terminal_growth_rate' in assumptions
        
        # Validate assumption reasonableness
        assert 0 <= assumptions['revenue_growth_rate'] <= 25.0  # Reasonable growth range
        assert 0 <= assumptions['ebitda_margin'] <= 40.0  # Reasonable margin range
        assert assumptions['tax_rate'] == 25.0  # Indian corporate tax
        assert 8.0 <= assumptions['wacc'] <= 18.0  # Reasonable WACC range
        assert assumptions['terminal_growth_rate'] == 3.0  # GDP growth assumption
    
    @pytest.mark.asyncio
    async def test_ddm_assumption_generation(self, dcf_service, sample_banking_data):
        """Test DDM assumption generation for banking companies."""
        
        info = sample_banking_data['info']
        assumptions = await dcf_service._generate_ddm_assumptions(info)
        
        assert isinstance(assumptions, dict)
        assert 'dividend_growth_rate' in assumptions
        assert 'roe' in assumptions
        assert 'payout_ratio' in assumptions
        assert 'cost_of_equity' in assumptions
        assert 'current_dividend_yield' in assumptions
        
        # Validate banking-specific assumptions
        assert 0 <= assumptions['dividend_growth_rate'] <= 18.0  # Reasonable for banks
        assert 5.0 <= assumptions['roe'] <= 25.0  # Banking ROE range
        assert 0.1 <= assumptions['payout_ratio'] <= 0.8  # Reasonable payout
        assert 8.0 <= assumptions['cost_of_equity'] <= 16.0  # Cost of equity range
    
    @pytest.mark.asyncio
    async def test_asset_assumption_generation(self, dcf_service, sample_reit_data):
        """Test Asset-based assumption generation."""
        
        info = sample_reit_data['info']
        assumptions = await dcf_service._generate_asset_assumptions(info)
        
        assert isinstance(assumptions, dict)
        assert 'book_value_growth' in assumptions
        assert 'roe' in assumptions
        assert 'asset_turnover' in assumptions
        assert 'cost_of_equity' in assumptions
        assert 'current_book_value' in assumptions
        
        # Validate asset-based assumptions
        assert 0 <= assumptions['book_value_growth'] <= 12.0  # Conservative growth
        assert 0 <= assumptions['roe'] <= 20.0  # ROE range
        assert assumptions['cost_of_equity'] >= 10.0  # Higher for asset-heavy
    
    @pytest.mark.asyncio
    async def test_multi_model_valuation_calculation(self, dcf_service, sample_banking_data):
        """Test multi-model valuation calculation."""
        
        result = await dcf_service.calculate_multi_model_valuation(
            'HDFCBANK.NS', sample_banking_data
        )
        
        assert result is not None
        assert 'ticker' in result
        assert 'model_recommendation' in result
        assert 'valuations' in result
        assert 'primary_model' in result
        assert 'valuation_summary' in result
        
        # Should have calculated multiple valuations
        valuations = result['valuations']
        assert len(valuations) >= 1  # At least primary model
        
        # Primary model should be DDM for banking
        assert result['primary_model'] == 'DDM'
        
        # Each valuation should have required fields
        for model, valuation in valuations.items():
            if 'error' not in valuation:
                assert 'model' in valuation
                assert 'intrinsic_value' in valuation
                assert 'current_price' in valuation
                assert 'upside_downside' in valuation
                assert 'key_assumptions' in valuation
    
    @pytest.mark.asyncio
    async def test_dcf_valuation_calculation(self, dcf_service, sample_tech_data):
        """Test DCF valuation calculation."""
        
        valuation = await dcf_service._calculate_dcf_valuation(sample_tech_data)
        
        assert valuation is not None
        assert valuation['model'] == 'DCF'
        assert 'intrinsic_value' in valuation
        assert 'current_price' in valuation
        assert 'upside_downside' in valuation
        assert 'confidence' in valuation
        assert 'key_assumptions' in valuation
        
        # Validate calculation reasonableness
        assert valuation['intrinsic_value'] > 0
        assert valuation['current_price'] > 0
        assert -100 <= valuation['upside_downside'] <= 200  # Reasonable upside/downside range
    
    @pytest.mark.asyncio
    async def test_ddm_valuation_calculation(self, dcf_service, sample_banking_data):
        """Test DDM valuation calculation."""
        
        valuation = await dcf_service._calculate_ddm_valuation(sample_banking_data)
        
        assert valuation is not None
        assert valuation['model'] == 'DDM'
        assert 'intrinsic_value' in valuation
        assert 'current_price' in valuation
        assert 'upside_downside' in valuation
        
        # DDM-specific validations
        key_assumptions = valuation['key_assumptions']
        assert 'dividend_growth' in key_assumptions
        assert 'cost_of_equity' in key_assumptions
        assert 'current_yield' in key_assumptions
        
        # Validate DDM calculation
        assert valuation['intrinsic_value'] > 0
        # DDM should work for companies with positive dividend yield
        info = sample_banking_data['info']
        if info.get('dividendYield', 0) > 0:
            assert valuation['confidence'] == 'high'
    
    @pytest.mark.asyncio
    async def test_asset_valuation_calculation(self, dcf_service, sample_reit_data):
        """Test Asset-based valuation calculation."""
        
        valuation = await dcf_service._calculate_asset_valuation(sample_reit_data)
        
        assert valuation is not None
        assert valuation['model'] == 'Asset'
        assert 'intrinsic_value' in valuation
        assert 'current_price' in valuation
        
        # Asset-specific validations
        key_assumptions = valuation['key_assumptions']
        assert 'book_value' in key_assumptions
        assert 'asset_premium' in key_assumptions
        
        # Validate asset calculation
        assert valuation['intrinsic_value'] > 0
        
        # Asset value should be related to book value
        info = sample_reit_data['info']
        book_value = info.get('bookValue', 0)
        if book_value > 0:
            # Intrinsic value should be close to adjusted book value
            assert 0.8 * book_value <= valuation['intrinsic_value'] <= 1.5 * book_value
    
    def test_valuation_summary_creation(self, dcf_service):
        """Test valuation summary creation."""
        
        # Mock valuations from multiple models
        valuations = {
            'DCF': {
                'intrinsic_value': 3900.0,
                'current_price': 3850.0,
                'upside_downside': 1.3
            },
            'DDM': {
                'intrinsic_value': 3750.0,
                'current_price': 3850.0,
                'upside_downside': -2.6
            },
            'Asset': {
                'intrinsic_value': 4000.0,
                'current_price': 3850.0,
                'upside_downside': 3.9
            }
        }
        
        summary = dcf_service._create_valuation_summary(valuations, 'DCF')
        
        assert 'valuation_range' in summary
        assert 'primary_model_result' in summary
        assert 'consensus' in summary
        
        # Validate range calculations
        range_data = summary['valuation_range']
        assert range_data['min'] == 3750.0
        assert range_data['max'] == 4000.0
        assert 3800.0 <= range_data['average'] <= 3900.0
        assert range_data['spread_percentage'] > 0
        
        # Validate primary model result
        primary = summary['primary_model_result']
        assert primary['model'] == 'DCF'
        assert primary['intrinsic_value'] == 3900.0
        
        # Validate consensus
        consensus = summary['consensus']
        assert consensus['recommendation'] in ['Strong Buy', 'Buy', 'Hold', 'Sell', 'Strong Sell']
        assert consensus['confidence'] in ['high', 'medium', 'low']
    
    def test_consensus_recommendation_logic(self, dcf_service):
        """Test consensus recommendation logic."""
        
        # Strong Buy scenario (>20% upside)
        recommendation = dcf_service._get_consensus_recommendation(1200.0, 1000.0)
        assert recommendation == 'Strong Buy'
        
        # Buy scenario (10-20% upside)
        recommendation = dcf_service._get_consensus_recommendation(1150.0, 1000.0)
        assert recommendation == 'Buy'
        
        # Hold scenario (-10% to +10%)
        recommendation = dcf_service._get_consensus_recommendation(1050.0, 1000.0)
        assert recommendation == 'Hold'
        
        # Sell scenario (-20% to -10%)
        recommendation = dcf_service._get_consensus_recommendation(850.0, 1000.0)
        assert recommendation == 'Sell'
        
        # Strong Sell scenario (<-20%)
        recommendation = dcf_service._get_consensus_recommendation(750.0, 1000.0)
        assert recommendation == 'Strong Sell'
    
    def test_consensus_confidence_calculation(self, dcf_service):
        """Test consensus confidence calculation."""
        
        # High confidence - low variation
        high_confidence_values = {'DCF': 1000.0, 'DDM': 1020.0, 'Asset': 980.0}
        confidence = dcf_service._calculate_consensus_confidence(high_confidence_values)
        assert confidence == 'high'
        
        # Medium confidence - moderate variation
        medium_confidence_values = {'DCF': 1000.0, 'DDM': 1150.0, 'Asset': 900.0}
        confidence = dcf_service._calculate_consensus_confidence(medium_confidence_values)
        assert confidence == 'medium'
        
        # Low confidence - high variation
        low_confidence_values = {'DCF': 1000.0, 'DDM': 1400.0, 'Asset': 700.0}
        confidence = dcf_service._calculate_consensus_confidence(low_confidence_values)
        assert confidence == 'low'
        
        # Single model - should be low confidence
        single_model = {'DCF': 1000.0}
        confidence = dcf_service._calculate_consensus_confidence(single_model)
        assert confidence == 'low'
    
    @pytest.mark.asyncio
    async def test_error_handling_invalid_data(self, dcf_service):
        """Test error handling with invalid data."""
        
        # Empty company data
        empty_data = {}
        result = await dcf_service.recommend_model_and_assumptions('INVALID.NS', empty_data)
        
        assert result is not None
        assert result['recommended_model']['model'] == 'DCF'  # Should fallback to DCF
        assert result['recommended_model']['confidence_score'] <= 0.6  # Lower confidence
        
        # Malformed data
        malformed_data = {'info': {'sector': None, 'industry': ''}}
        result = await dcf_service.recommend_model_and_assumptions('MALFORMED.NS', malformed_data)
        
        assert result is not None
        assert result['recommended_model']['model'] == 'DCF'  # Should fallback to DCF
    
    @pytest.mark.asyncio
    async def test_user_model_preference_override(self, dcf_service, sample_banking_data):
        """Test user model preference override."""
        
        # Banking company but user prefers DCF
        result = await dcf_service.calculate_multi_model_valuation(
            'HDFCBANK.NS', sample_banking_data, user_model_preference='DCF'
        )
        
        # Should use user preference as primary model
        assert result['primary_model'] == 'DCF'
        
        # But recommendation should still show DDM as recommended
        assert result['model_recommendation']['recommended_model']['model'] == 'DDM'
    
    def test_revenue_growth_estimation(self, dcf_service):
        """Test revenue growth estimation logic."""
        
        # Company with quarterly growth data
        with_growth_data = {
            'quarterlyRevenueGrowth': 0.12,  # 12% quarterly growth
            'marketCap': 5e11  # Mid cap
        }
        
        growth = dcf_service._estimate_revenue_growth(with_growth_data)
        assert 0 < growth <= 20.0
        assert growth == 12.0  # Should use quarterly growth * 100
        
        # Large cap without growth data
        large_cap = {'marketCap': 2e12}  # Large cap
        growth = dcf_service._estimate_revenue_growth(large_cap)
        assert growth == 6.0  # Large cap default
        
        # Mid cap without growth data
        mid_cap = {'marketCap': 5e11}  # Mid cap
        growth = dcf_service._estimate_revenue_growth(mid_cap)
        assert growth == 8.0  # Mid cap default
        
        # Small cap without growth data
        small_cap = {'marketCap': 5e10}  # Small cap
        growth = dcf_service._estimate_revenue_growth(small_cap)
        assert growth == 10.0  # Small cap default
    
    def test_ebitda_margin_estimation(self, dcf_service):
        """Test EBITDA margin estimation logic."""
        
        # Company with profit margin data
        with_margin_data = {'profitMargins': 0.15}  # 15% profit margin
        margin = dcf_service._estimate_ebitda_margin(with_margin_data)
        assert 10.0 <= margin <= 30.0  # Should be reasonable multiple of profit margin
        
        # Technology company without margin data
        tech_company = {'sector': 'Technology'}
        margin = dcf_service._estimate_ebitda_margin(tech_company)
        assert margin == 20.0  # Tech default
        
        # Banking company
        banking_company = {'sector': 'Banking'}
        margin = dcf_service._estimate_ebitda_margin(banking_company)
        assert margin == 25.0  # Banking default (NIM)
        
        # Generic company
        generic_company = {'sector': 'Unknown'}
        margin = dcf_service._estimate_ebitda_margin(generic_company)
        assert margin == 15.0  # Generic default
    
    def test_wacc_estimation(self, dcf_service):
        """Test WACC estimation logic."""
        
        # Company with beta data
        with_beta = {'beta': 1.2}
        wacc = dcf_service._estimate_wacc(with_beta)
        assert 8.0 <= wacc <= 16.0  # Should be within reasonable range
        
        # High beta company should have higher WACC
        high_beta = {'beta': 1.5}
        high_wacc = dcf_service._estimate_wacc(high_beta)
        
        low_beta = {'beta': 0.7}
        low_wacc = dcf_service._estimate_wacc(low_beta)
        
        assert high_wacc > low_wacc  # Higher beta = higher WACC
        
        # Company without beta
        no_beta = {}
        wacc = dcf_service._estimate_wacc(no_beta)
        assert wacc == 12.0  # Market average default

if __name__ == "__main__":
    pytest.main([__file__, "-v"])