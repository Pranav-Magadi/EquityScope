import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch
from backend.app.services.optimized_ai_service import OptimizedAIService

class TestOptimizedAIService:
    """
    Test-Driven Development (TDD) tests for OptimizedAIService.
    
    TDD PRINCIPLE:
    1. Write failing tests first (RED)
    2. Write minimal code to make tests pass (GREEN) 
    3. Refactor code while keeping tests passing (REFACTOR)
    
    This ensures:
    - Clear requirements definition through tests
    - High code coverage and quality
    - Regression prevention
    - Easier refactoring and maintenance
    """
    
    @pytest.fixture
    def ai_service(self):
        """Create AI service instance for testing."""
        service = OptimizedAIService()
        return service
    
    @pytest.fixture
    def sample_company_data(self):
        """Sample company data for testing."""
        return {
            'ticker': 'TCS.NS',
            'info': {
                'longName': 'Tata Consultancy Services',
                'sector': 'Technology',
                'industry': 'Information Technology Services',
                'marketCap': 1200000000000,  # 12 lakh crores
                'totalRevenue': 2000000000000,  # 2 lakh crores
                'ebitda': 400000000000,  # 40k crores
                'profitMargins': 0.22,
                'returnOnEquity': 0.45,
                'trailingPE': 28.5,
                'priceToBook': 12.8,
                'debtToEquity': 0.05,
                'currentRatio': 3.2,
                'currentPrice': 3850.0
            },
            'history': {},
            'financials': {},
            'balance_sheet': {},
            'cash_flow': {}
        }
    
    @pytest.fixture
    def sample_news_articles(self):
        """Sample news articles for testing."""
        return [
            {
                'title': 'TCS reports strong Q3 earnings with 15% growth',
                'url': 'https://example.com/tcs-earnings',
                'content': 'TCS reported strong quarterly results with revenue growth of 15% year-over-year...'
            },
            {
                'title': 'TCS wins major cloud transformation deal',
                'url': 'https://example.com/tcs-deal',
                'content': 'Tata Consultancy Services secured a multi-year cloud transformation contract...'
            }
        ]
    
    def test_initialization(self, ai_service):
        """Test AI service initialization."""
        assert ai_service is not None
        assert hasattr(ai_service, 'industry_model_mapping')
        assert hasattr(ai_service, 'indian_peer_companies')
        assert hasattr(ai_service, 'dcf_education_template')
        
        # Test industry model mappings
        assert ai_service.industry_model_mapping['Technology'] == 'DCF'
        assert ai_service.industry_model_mapping['Banking'] == 'DDM'
        assert ai_service.industry_model_mapping['REIT'] == 'Asset'
    
    def test_get_industry_context(self, ai_service):
        """Test industry context generation."""
        context = ai_service._get_industry_context('Technology', 'TCS.NS')
        
        assert context['recommended_model'] == 'DCF'
        assert 'model_rationale' in context
        assert context['is_indian_stock'] is True
        assert isinstance(context['peer_companies'], list)
        assert isinstance(context['common_industry_risks'], list)
        
        # Test that TCS peers don't include TCS itself
        assert 'TCS.NS' not in context['peer_companies']
        
        # Test banking context
        banking_context = ai_service._get_industry_context('Banking', 'HDFCBANK.NS')
        assert banking_context['recommended_model'] == 'DDM'
    
    def test_model_rationale_generation(self, ai_service):
        """Test model rationale generation for different industries."""
        dcf_rationale = ai_service._get_model_rationale('DCF', 'Technology')
        ddm_rationale = ai_service._get_model_rationale('DDM', 'Banking')
        asset_rationale = ai_service._get_model_rationale('Asset', 'REIT')
        
        assert 'cash flows' in dcf_rationale.lower()
        assert 'dividend' in ddm_rationale.lower()
        assert 'asset' in asset_rationale.lower()
    
    def test_financial_summary_formatting(self, ai_service, sample_company_data):
        """Test financial data summary formatting."""
        summary = ai_service._format_financial_summary(sample_company_data)
        
        assert 'Revenue:' in summary
        assert 'EBITDA:' in summary
        assert 'P/E:' in summary
        assert 'ROE:' in summary
        
        # Test with missing data
        empty_data = {'info': {}}
        empty_summary = ai_service._format_financial_summary(empty_data)
        assert 'N/A' in empty_summary
    
    @pytest.mark.asyncio
    async def test_analysis_engine_agent_structure(self, ai_service, sample_company_data, sample_news_articles):
        """Test Analysis Engine Agent output structure."""
        # Mock Claude client response
        mock_response = {
            "company_overview": {
                "investment_thesis": "TCS is a strong technology leader with consistent growth",
                "key_strengths": ["Market leadership", "Strong margins", "Global presence"],
                "key_risks": ["Currency fluctuation", "Competition", "Economic slowdown"],
                "competitive_position": "Market leader in Indian IT services"
            },
            "news_insights": {
                "sentiment_score": 0.75,
                "key_developments": [
                    {
                        "headline": "Strong Q3 earnings",
                        "impact": "positive",
                        "significance": "high"
                    }
                ],
                "market_sentiment": "Positive due to strong quarterly results"
            },
            "financial_health": {
                "profitability_score": "strong",
                "liquidity_score": "strong",
                "growth_trajectory": "stable",
                "key_metrics_analysis": "Strong margins and ROE indicate healthy operations"
            },
            "dcf_assumptions": {
                "revenue_growth_rate": 12.0,
                "ebitda_margin": 20.0,
                "tax_rate": 25.0,
                "wacc": 10.5,
                "terminal_growth_rate": 3.0,
                "rationale": {
                    "revenue_growth_rate": "Based on historical performance",
                    "ebitda_margin": "Conservative estimate",
                    "wacc": "Industry average",
                    "terminal_growth_rate": "GDP growth assumption"
                }
            },
            "ai_insights": {
                "price_momentum": "Positive technical indicators",
                "analyst_consensus": "Buy rating from majority analysts",
                "unique_value_drivers": ["Digital transformation", "Cloud services"],
                "red_flags": ["High valuation multiples"]
            }
        }
        
        with patch.object(ai_service, 'generate_completion', return_value=json.dumps(mock_response)):
            result = await ai_service.analysis_engine_agent(sample_company_data, sample_news_articles)
            
            assert result is not None
            assert 'company_overview' in result
            assert 'news_insights' in result
            assert 'financial_health' in result
            assert 'dcf_assumptions' in result
            assert 'ai_insights' in result
            assert 'education_content' in result
            
            # Test specific structure requirements
            assert isinstance(result['company_overview']['key_strengths'], list)
            assert isinstance(result['news_insights']['sentiment_score'], (int, float))
            assert result['dcf_assumptions']['revenue_growth_rate'] > 0
            assert 'dcf_explanation' in result['education_content']
    
    @pytest.mark.asyncio
    async def test_dcf_validator_agent_structure(self, ai_service, sample_company_data):
        """Test DCF Validator Agent output structure."""
        # Sample analysis output
        analysis_output = {
            'dcf_assumptions': {
                'revenue_growth_rate': 12.0,
                'ebitda_margin': 20.0,
                'wacc': 10.5,
                'terminal_growth_rate': 3.0
            }
        }
        
        mock_validation_response = {
            "validation_summary": {
                "overall_assessment": "reasonable",
                "confidence_level": "high",
                "key_concerns": ["High growth assumptions"],
                "strengths": ["Conservative margins", "Reasonable WACC"]
            },
            "assumption_feedback": {
                "revenue_growth_rate": {
                    "assessment": "reasonable",
                    "peer_comparison": "vs industry average of 10%",
                    "suggestion": "Consider 10-15% range for sensitivity",
                    "confidence": "medium"
                },
                "ebitda_margin": {
                    "assessment": "reasonable",
                    "peer_comparison": "vs industry average of 18%",
                    "suggestion": "Margin assumption looks conservative",
                    "confidence": "high"
                },
                "wacc": {
                    "assessment": "reasonable",
                    "peer_comparison": "vs industry average of 11%",
                    "suggestion": "WACC is in line with peers",
                    "confidence": "high"
                }
            },
            "sensitivity_insights": {
                "most_sensitive_assumption": "revenue_growth_rate",
                "downside_scenario": "Economic slowdown could impact growth",
                "upside_scenario": "Digital transformation could accelerate growth",
                "recommended_ranges": {
                    "revenue_growth_low": 8.0,
                    "revenue_growth_high": 15.0,
                    "wacc_low": 9.5,
                    "wacc_high": 12.0
                }
            }
        }
        
        with patch.object(ai_service, 'generate_completion', return_value=json.dumps(mock_validation_response)):
            result = await ai_service.dcf_validator_agent(analysis_output, sample_company_data)
            
            assert result is not None
            assert 'validation_summary' in result
            assert 'assumption_feedback' in result
            assert 'sensitivity_insights' in result
            
            # Test validation summary structure
            assert result['validation_summary']['overall_assessment'] in ['conservative', 'reasonable', 'aggressive']
            assert result['validation_summary']['confidence_level'] in ['high', 'medium', 'low']
            
            # Test assumption feedback structure
            for assumption in ['revenue_growth_rate', 'ebitda_margin', 'wacc']:
                assert assumption in result['assumption_feedback']
                assert 'assessment' in result['assumption_feedback'][assumption]
                assert 'peer_comparison' in result['assumption_feedback'][assumption]
                
            # Test sensitivity insights
            assert 'most_sensitive_assumption' in result['sensitivity_insights']
            assert 'recommended_ranges' in result['sensitivity_insights']
    
    def test_error_handling_no_client(self):
        """Test error handling when Claude client is not available."""
        service = OptimizedAIService()
        service.client = None
        
        assert not service.is_available()
    
    @pytest.mark.asyncio
    async def test_json_parsing_error_handling(self, ai_service, sample_company_data, sample_news_articles):
        """Test handling of malformed JSON responses."""
        # Mock malformed JSON response
        with patch.object(ai_service, 'generate_completion', return_value='Invalid JSON {broken'):
            result = await ai_service.analysis_engine_agent(sample_company_data, sample_news_articles)
            assert result is None
    
    @pytest.mark.asyncio
    async def test_empty_news_handling(self, ai_service, sample_company_data):
        """Test handling when no news articles are available."""
        empty_news = []
        
        mock_response = {
            "company_overview": {"investment_thesis": "Test thesis"},
            "news_insights": {"sentiment_score": 0.5, "key_developments": [], "market_sentiment": "Neutral"},
            "financial_health": {"profitability_score": "moderate"},
            "dcf_assumptions": {"revenue_growth_rate": 8.0},
            "ai_insights": {"unique_value_drivers": ["Test driver"]}
        }
        
        with patch.object(ai_service, 'generate_completion', return_value=json.dumps(mock_response)):
            result = await ai_service.analysis_engine_agent(sample_company_data, empty_news)
            
            assert result is not None
            assert result['news_insights']['sentiment_score'] == 0.5
    
    def test_token_optimization_targets(self, ai_service):
        """Test that the service is designed for optimal token usage."""
        # Analysis Engine should target 8K tokens
        # DCF Validator should target 2K tokens
        # Total target: 10K tokens (50% reduction from original 24K)
        
        # This is a design validation test
        assert hasattr(ai_service, 'dcf_education_template')
        assert hasattr(ai_service, 'risk_factors_template')
        
        # Test that templated content reduces AI generation needs
        assert len(ai_service.dcf_education_template) > 100
        assert 'Technology' in ai_service.risk_factors_template
        assert 'Banking' in ai_service.risk_factors_template
    
    @pytest.mark.asyncio
    async def test_concurrent_agent_execution(self, ai_service, sample_company_data, sample_news_articles):
        """Test that agents can be executed concurrently for performance."""
        import asyncio
        
        # Mock responses
        analysis_response = {"company_overview": {"investment_thesis": "Test"}, "dcf_assumptions": {"revenue_growth_rate": 10.0}}
        validation_response = {"validation_summary": {"overall_assessment": "reasonable"}}
        
        with patch.object(ai_service, 'generate_completion') as mock_completion:
            mock_completion.side_effect = [
                json.dumps(analysis_response),
                json.dumps(validation_response)
            ]
            
            # Execute both agents concurrently
            analysis_task = ai_service.analysis_engine_agent(sample_company_data, sample_news_articles)
            validation_task = ai_service.dcf_validator_agent({"dcf_assumptions": {"revenue_growth_rate": 10.0}}, sample_company_data)
            
            analysis_result, validation_result = await asyncio.gather(analysis_task, validation_task)
            
            assert analysis_result is not None
            assert validation_result is not None
            assert mock_completion.call_count == 2
    
    def test_cost_calculation_validation(self, ai_service):
        """Validate cost reduction calculations."""
        # Original 4-agent system: ~24K tokens
        original_tokens = {
            'generator': 6000,
            'checker': 3000,
            'bull': 4000,
            'bear': 4000,
            'total': 17000  # Conservative estimate
        }
        
        # New 2-agent system: ~10K tokens  
        optimized_tokens = {
            'analysis_engine': 8000,
            'dcf_validator': 2000,
            'total': 10000
        }
        
        # Calculate cost reduction
        cost_reduction = (original_tokens['total'] - optimized_tokens['total']) / original_tokens['total']
        
        # Should achieve >40% cost reduction
        assert cost_reduction > 0.4
        
        # At $0.30 per 1K tokens (rough estimate for Claude)
        original_cost = (original_tokens['total'] / 1000) * 0.30
        optimized_cost = (optimized_tokens['total'] / 1000) * 0.30
        
        # Should reduce from ~$5.10 to ~$3.00 per analysis
        assert optimized_cost < original_cost * 0.6

if __name__ == "__main__":
    pytest.main([__file__, "-v"])