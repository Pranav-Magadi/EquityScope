import pytest
import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from backend.app.services.optimized_workflow import OptimizedWorkflowService
from backend.app.models.dcf import DCFAssumptions

class TestOptimizedWorkflowService:
    """
    Comprehensive TDD tests for OptimizedWorkflowService.
    
    Test Coverage:
    - Cost optimization (50% reduction target)
    - Performance optimization (30s target)
    - Error handling and edge cases
    - User guidance generation
    - Integration with optimized AI service
    """
    
    @pytest.fixture
    def workflow_service(self):
        """Create workflow service instance for testing."""
        return OptimizedWorkflowService()
    
    @pytest.fixture
    def sample_dcf_assumptions(self):
        """Sample DCF assumptions for testing."""
        return DCFAssumptions(
            revenue_growth_rate=10.0,
            ebitda_margin=18.0,
            tax_rate=25.0,
            wacc=11.5,
            terminal_growth_rate=3.5
        )
    
    @pytest.fixture
    def mock_company_data(self):
        """Mock company data for testing."""
        return {
            'ticker': 'TCS.NS',
            'info': {
                'longName': 'Tata Consultancy Services',
                'sector': 'Technology',
                'industry': 'Information Technology Services',
                'marketCap': 1200000000000,
                'currentPrice': 3850.0,
                'profitMargins': 0.22,
                'returnOnEquity': 0.45
            },
            'history': {'Close': {'2025-07-28': 3850.0}},
            'financials': {},
            'balance_sheet': {},
            'cash_flow': {},
            'fetched_at': datetime.now().isoformat()
        }
    
    @pytest.fixture
    def mock_news_articles(self):
        """Mock news articles for testing."""
        return [
            {
                'title': 'TCS reports strong Q4 results',
                'url': 'https://example.com/tcs-q4',
                'content': 'TCS reported strong quarterly earnings...'
            },
            {
                'title': 'TCS wins major cloud deal',
                'url': 'https://example.com/tcs-cloud',
                'content': 'Tata Consultancy Services secured a significant cloud transformation contract...'
            }
        ]
    
    @pytest.fixture
    def mock_analysis_result(self):
        """Mock analysis engine result."""
        return {
            'company_overview': {
                'investment_thesis': 'TCS is a market leader with consistent growth and strong margins',
                'key_strengths': ['Market leadership in IT services', 'Strong client relationships', 'Robust digital capabilities'],
                'key_risks': ['Currency fluctuation impact', 'Increased competition', 'Talent retention challenges'],
                'competitive_position': 'Leading position in Indian IT services sector'
            },
            'news_insights': {
                'sentiment_score': 0.75,
                'key_developments': [
                    {'headline': 'Strong Q4 results', 'impact': 'positive', 'significance': 'high'}
                ],
                'market_sentiment': 'Positive outlook based on earnings performance'
            },
            'financial_health': {
                'profitability_score': 'strong',
                'liquidity_score': 'strong',
                'growth_trajectory': 'stable',
                'key_metrics_analysis': 'Healthy financial metrics with strong ROE and margins'
            },
            'dcf_assumptions': {
                'revenue_growth_rate': 10.0,
                'ebitda_margin': 18.0,
                'tax_rate': 25.0,
                'wacc': 11.5,
                'terminal_growth_rate': 3.5,
                'rationale': {
                    'revenue_growth_rate': 'Based on historical performance and market outlook',
                    'ebitda_margin': 'Conservative estimate based on operational efficiency'
                }
            },
            'ai_insights': {
                'price_momentum': 'Positive technical indicators',
                'unique_value_drivers': ['Digital transformation leadership', 'Strong recurring revenue'],
                'red_flags': ['High valuation multiples']
            },
            'education_content': {
                'dcf_explanation': 'DCF calculates intrinsic value by projecting future cash flows...',
                'industry_context': {
                    'recommended_model': 'DCF',
                    'model_rationale': 'Technology companies have predictable cash flows'
                }
            }
        }
    
    @pytest.fixture
    def mock_validation_result(self):
        """Mock DCF validation result."""
        return {
            'validation_summary': {
                'overall_assessment': 'reasonable',
                'confidence_level': 'high',
                'key_concerns': ['Revenue growth slightly above historical average'],
                'strengths': ['Conservative margin assumptions', 'Appropriate WACC calculation']
            },
            'assumption_feedback': {
                'revenue_growth_rate': {
                    'assessment': 'reasonable',
                    'peer_comparison': 'vs industry average of 8.5%',
                    'suggestion': 'Growth assumption is slightly optimistic but defensible',
                    'confidence': 'medium'
                },
                'ebitda_margin': {
                    'assessment': 'reasonable',
                    'peer_comparison': 'vs industry average of 19.2%',
                    'suggestion': 'Margin assumption appears conservative',
                    'confidence': 'high'
                }
            },
            'sensitivity_insights': {
                'most_sensitive_assumption': 'revenue_growth_rate',
                'downside_scenario': 'Economic slowdown could impact client spending',
                'upside_scenario': 'Digital transformation acceleration could drive higher growth',
                'recommended_ranges': {
                    'revenue_growth_low': 8.0,
                    'revenue_growth_high': 12.0,
                    'wacc_low': 10.5,
                    'wacc_high': 12.5
                }
            }
        }
    
    def test_initialization(self, workflow_service):
        """Test workflow service initialization."""
        assert workflow_service is not None
        assert workflow_service.progress_callbacks == []
        assert workflow_service.cache_manager is None  # Will be implemented later
    
    def test_progress_callback_management(self, workflow_service):
        """Test progress callback management."""
        callback_results = []
        
        def test_callback(step, progress, message):
            callback_results.append((step, progress, message))
        
        workflow_service.add_progress_callback(test_callback)
        workflow_service._notify_progress("test", 50, "Test message")
        
        assert len(callback_results) == 1
        assert callback_results[0] == ("test", 50, "Test message")
    
    def test_nan_value_sanitization(self, workflow_service):
        """Test NaN value sanitization for JSON serialization."""
        import math
        
        test_data = {
            'normal_value': 42,
            'nan_value': float('nan'),
            'inf_value': float('inf'),
            'nested_dict': {
                'nan_nested': float('nan'),
                'normal_nested': 'test'
            },
            'list_with_nan': [1, float('nan'), 3]
        }
        
        sanitized = workflow_service._sanitize_nan_values(test_data)
        
        assert sanitized['normal_value'] == 42
        assert sanitized['nan_value'] is None
        assert sanitized['inf_value'] is None
        assert sanitized['nested_dict']['nan_nested'] is None
        assert sanitized['nested_dict']['normal_nested'] == 'test'
        assert sanitized['list_with_nan'] == [1, None, 3]
    
    @pytest.mark.asyncio
    async def test_optimized_analysis_full_workflow(
        self, 
        workflow_service, 
        sample_dcf_assumptions,
        mock_company_data,
        mock_news_articles,
        mock_analysis_result,
        mock_validation_result
    ):
        """Test complete optimized analysis workflow."""
        
        # Mock the external dependencies
        with patch.object(workflow_service, '_fetch_company_data', return_value=mock_company_data) as mock_company, \
             patch.object(workflow_service, '_fetch_news_data', return_value=mock_news_articles) as mock_news, \
             patch('backend.app.services.optimized_workflow.optimized_ai_service.is_available', return_value=True), \
             patch('backend.app.services.optimized_workflow.optimized_ai_service.analysis_engine_agent', return_value=mock_analysis_result) as mock_analysis, \
             patch('backend.app.services.optimized_workflow.optimized_ai_service.dcf_validator_agent', return_value=mock_validation_result) as mock_validation:
            
            # Track progress callbacks
            progress_updates = []
            workflow_service.add_progress_callback(lambda step, progress, msg: progress_updates.append((step, progress, msg)))
            
            # Execute the workflow
            start_time = datetime.now()
            result = await workflow_service.execute_optimized_analysis(
                ticker='TCS.NS',
                user_assumptions=sample_dcf_assumptions,
                max_news_articles=5
            )
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # Validate result structure
            assert result is not None
            assert 'metadata' in result
            assert 'raw_data' in result
            assert 'analysis_engine_output' in result
            assert 'dcf_validation_output' in result
            assert 'enhanced_insights' in result
            assert 'user_guidance' in result
            
            # Validate metadata
            metadata = result['metadata']
            assert metadata['ticker'] == 'TCS.NS'
            assert metadata['workflow_version'] == '2.0-optimized'
            assert 'cost_optimization' in metadata
            
            # Validate cost optimization metrics
            cost_opt = metadata['cost_optimization']
            assert cost_opt['agent_count'] == 2
            assert cost_opt['estimated_tokens'] == 10000
            assert cost_opt['estimated_cost_usd'] == 0.30
            assert cost_opt['cost_reduction_vs_v1'] == '50%'
            
            # Validate enhanced insights structure
            insights = result['enhanced_insights']
            assert 'investment_summary' in insights
            assert 'risk_reward_profile' in insights
            assert 'assumption_insights' in insights
            assert 'action_guidance' in insights
            
            # Validate user guidance structure
            guidance = result['user_guidance']
            assert 'what_this_means' in guidance
            assert 'next_steps' in guidance
            assert 'educational_content' in guidance
            
            # Validate progress tracking
            assert len(progress_updates) >= 5  # Should have multiple progress updates
            assert progress_updates[-1][1] == 100  # Final progress should be 100%
            
            # Validate mock calls
            mock_company.assert_called_once_with('TCS.NS')
            mock_news.assert_called_once_with('TCS.NS', 5)
            mock_analysis.assert_called_once()
            mock_validation.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_performance_optimization_target(self, workflow_service):
        """Test that workflow meets 30-second performance target."""
        
        # Mock fast responses
        with patch.object(workflow_service, '_fetch_company_data', return_value={'ticker': 'TEST.NS'}) as mock_company, \
             patch.object(workflow_service, '_fetch_news_data', return_value=[]) as mock_news, \
             patch('backend.app.services.optimized_workflow.optimized_ai_service.is_available', return_value=True), \
             patch('backend.app.services.optimized_workflow.optimized_ai_service.analysis_engine_agent', return_value={'dcf_assumptions': {}}) as mock_analysis, \
             patch('backend.app.services.optimized_workflow.optimized_ai_service.dcf_validator_agent', return_value={'validation_summary': {}}) as mock_validation:
            
            start_time = datetime.now()
            result = await workflow_service.execute_optimized_analysis('TEST.NS')
            end_time = datetime.now()
            
            duration = (end_time - start_time).total_seconds()
            
            # Should complete well under 30 seconds with mocked responses
            assert duration < 30
            assert result is not None
            assert result['metadata']['analysis_duration_seconds'] < 30
    
    @pytest.mark.asyncio
    async def test_cost_optimization_validation(self, workflow_service):
        """Test that cost optimization targets are met."""
        
        # Mock responses to validate cost structure
        mock_analysis_result = {'dcf_assumptions': {'revenue_growth_rate': 8.0}}
        mock_validation_result = {'validation_summary': {'confidence_level': 'medium'}}
        
        with patch.object(workflow_service, '_fetch_company_data', return_value={'ticker': 'TEST.NS'}) as mock_company, \
             patch.object(workflow_service, '_fetch_news_data', return_value=[]) as mock_news, \
             patch('backend.app.services.optimized_workflow.optimized_ai_service.is_available', return_value=True), \
             patch('backend.app.services.optimized_workflow.optimized_ai_service.analysis_engine_agent', return_value=mock_analysis_result) as mock_analysis, \
             patch('backend.app.services.optimized_workflow.optimized_ai_service.dcf_validator_agent', return_value=mock_validation_result) as mock_validation:
            
            result = await workflow_service.execute_optimized_analysis('TEST.NS')
            
            # Validate cost optimization metrics
            cost_opt = result['metadata']['cost_optimization']
            
            # Should use only 2 agents (vs 4 in v1.0)
            assert cost_opt['agent_count'] == 2
            
            # Should target 10K tokens (vs ~24K in v1.0)
            assert cost_opt['estimated_tokens'] <= 10000
            
            # Should target $0.30 cost (vs $0.60-1.20 in v1.0)  
            assert cost_opt['estimated_cost_usd'] <= 0.30
            
            # Should achieve 50% cost reduction
            assert '50%' in cost_opt['cost_reduction_vs_v1']
    
    @pytest.mark.asyncio
    async def test_parallel_data_fetching_optimization(self, workflow_service):
        """Test that data fetching is parallelized for performance."""
        
        # Mock slow individual functions
        async def slow_company_fetch(ticker):
            await asyncio.sleep(0.1)
            return {'ticker': ticker}
        
        async def slow_news_fetch(ticker, max_articles):
            await asyncio.sleep(0.1)
            return []
        
        with patch.object(workflow_service, '_fetch_company_data', side_effect=slow_company_fetch), \
             patch.object(workflow_service, '_fetch_news_data', side_effect=slow_news_fetch), \
             patch('backend.app.services.optimized_workflow.optimized_ai_service.is_available', return_value=True), \
             patch('backend.app.services.optimized_workflow.optimized_ai_service.analysis_engine_agent', return_value={'dcf_assumptions': {}}), \
             patch('backend.app.services.optimized_workflow.optimized_ai_service.dcf_validator_agent', return_value={'validation_summary': {}}):
            
            start_time = datetime.now()
            result = await workflow_service.execute_optimized_analysis('TEST.NS')
            end_time = datetime.now()
            
            duration = (end_time - start_time).total_seconds()
            
            # Parallel execution should take ~0.1s, not ~0.2s
            # Add some buffer for test execution overhead
            assert duration < 0.5  # Much less than sequential 0.2s + overhead
            assert result is not None
    
    @pytest.mark.asyncio
    async def test_error_handling_company_data_failure(self, workflow_service):
        """Test handling when company data fetch fails."""
        
        with patch.object(workflow_service, '_fetch_company_data', side_effect=Exception("API Error")) as mock_company, \
             patch.object(workflow_service, '_fetch_news_data', return_value=[]) as mock_news, \
             patch('backend.app.services.optimized_workflow.optimized_ai_service.is_available', return_value=True):
            
            result = await workflow_service.execute_optimized_analysis('INVALID.NS')
            
            # Should return None when company data fetch fails
            assert result is None
            mock_company.assert_called_once_with('INVALID.NS')
    
    @pytest.mark.asyncio
    async def test_error_handling_news_failure_graceful_degradation(self, workflow_service):
        """Test graceful degradation when news fetch fails."""
        
        mock_company_data = {'ticker': 'TEST.NS', 'info': {'longName': 'Test Company'}}
        
        with patch.object(workflow_service, '_fetch_company_data', return_value=mock_company_data) as mock_company, \
             patch.object(workflow_service, '_fetch_news_data', side_effect=Exception("News API Error")) as mock_news, \
             patch('backend.app.services.optimized_workflow.optimized_ai_service.is_available', return_value=True), \
             patch('backend.app.services.optimized_workflow.optimized_ai_service.analysis_engine_agent', return_value={'dcf_assumptions': {}}) as mock_analysis, \
             patch('backend.app.services.optimized_workflow.optimized_ai_service.dcf_validator_agent', return_value={'validation_summary': {}}) as mock_validation:
            
            result = await workflow_service.execute_optimized_analysis('TEST.NS')
            
            # Should continue with empty news array
            assert result is not None
            assert result['metadata']['news_articles_analyzed'] == 0
            
            # Should still call analysis with empty news
            mock_analysis.assert_called_once()
            args, kwargs = mock_analysis.call_args
            assert len(args[1]) == 0  # Empty news articles
    
    @pytest.mark.asyncio
    async def test_error_handling_ai_service_unavailable(self, workflow_service):
        """Test handling when AI service is unavailable."""
        
        with patch('backend.app.services.optimized_workflow.optimized_ai_service.is_available', return_value=False):
            
            result = await workflow_service.execute_optimized_analysis('TEST.NS')
            
            # Should return None when AI service unavailable
            assert result is None
    
    @pytest.mark.asyncio
    async def test_cancellation_handling(self, workflow_service):
        """Test that analysis can be cancelled gracefully."""
        
        # Create a cancellation checker that cancels after first call
        call_count = 0
        def cancellation_checker():
            nonlocal call_count
            call_count += 1
            return call_count > 1  # Cancel after first check
        
        with patch.object(workflow_service, '_fetch_company_data', return_value={'ticker': 'TEST.NS'}), \
             patch.object(workflow_service, '_fetch_news_data', return_value=[]), \
             patch('backend.app.services.optimized_workflow.optimized_ai_service.is_available', return_value=True):
            
            result = await workflow_service.execute_optimized_analysis(
                'TEST.NS',
                cancellation_checker=cancellation_checker
            )
            
            # Should return None when cancelled
            assert result is None
    
    def test_enhanced_insights_generation(self, workflow_service, mock_analysis_result, mock_validation_result, mock_company_data):
        """Test enhanced insights generation."""
        
        insights = workflow_service._generate_enhanced_insights(
            mock_analysis_result, mock_validation_result, mock_company_data
        )
        
        assert 'investment_summary' in insights
        assert 'risk_reward_profile' in insights
        assert 'assumption_insights' in insights
        assert 'action_guidance' in insights
        
        # Validate investment summary
        inv_summary = insights['investment_summary']
        assert 'thesis' in inv_summary
        assert 'confidence_level' in inv_summary
        assert 'recommendation_basis' in inv_summary
        
        # Validate risk-reward profile
        risk_reward = insights['risk_reward_profile']
        assert 'primary_strengths' in risk_reward
        assert 'primary_risks' in risk_reward
        assert 'validation_concerns' in risk_reward
        assert 'overall_risk_level' in risk_reward
        
        # Validate that strengths and risks are limited appropriately
        assert len(risk_reward['primary_strengths']) <= 3
        assert len(risk_reward['primary_risks']) <= 3
    
    def test_user_guidance_generation(self, workflow_service, mock_analysis_result, mock_validation_result):
        """Test user guidance generation."""
        
        guidance = workflow_service._generate_user_guidance(
            mock_analysis_result, mock_validation_result
        )
        
        assert 'what_this_means' in guidance
        assert 'next_steps' in guidance
        assert 'educational_content' in guidance
        
        # Validate what_this_means structure
        what_means = guidance['what_this_means']
        assert 'financial_health' in what_means
        assert 'valuation_context' in what_means
        assert 'key_takeaways' in what_means
        
        # Validate next_steps structure
        next_steps = guidance['next_steps']
        assert 'immediate_actions' in next_steps
        assert 'further_research' in next_steps
        assert isinstance(next_steps['immediate_actions'], list)
        assert isinstance(next_steps['further_research'], list)
    
    def test_risk_level_calculation(self, workflow_service):
        """Test risk level calculation logic."""
        
        # Low risk scenario
        low_risk = workflow_service._calculate_risk_level(['Minor risk'], ['Small concern'])
        assert low_risk == 'Low'
        
        # Medium risk scenario
        medium_risk = workflow_service._calculate_risk_level(['Risk 1', 'Risk 2'], ['Concern 1', 'Concern 2'])
        assert medium_risk == 'Medium'
        
        # High risk scenario
        high_risk = workflow_service._calculate_risk_level(
            ['Risk 1', 'Risk 2', 'Risk 3'], 
            ['Concern 1', 'Concern 2', 'Concern 3']
        )
        assert high_risk == 'High'
    
    def test_action_guidance_generation(self, workflow_service, mock_analysis_result, mock_validation_result):
        """Test action guidance generation logic."""
        
        # Test conservative/high confidence scenario
        validation_conservative = {
            'validation_summary': {
                'confidence_level': 'high',
                'overall_assessment': 'conservative'
            }
        }
        
        action = workflow_service._generate_action_guidance(
            mock_analysis_result, validation_conservative, 3850.0
        )
        
        assert 'recommended_action' in action
        assert 'confidence_indicator' in action
        assert 'color_code' in action
        assert action['color_code'] == 'green'
        assert 'Consider for investment' in action['recommended_action']
        
        # Test aggressive/low confidence scenario
        validation_aggressive = {
            'validation_summary': {
                'confidence_level': 'low',
                'overall_assessment': 'aggressive'
            }
        }
        
        action_caution = workflow_service._generate_action_guidance(
            mock_analysis_result, validation_aggressive, 3850.0
        )
        
        assert action_caution['color_code'] == 'red'
        assert 'Exercise caution' in action_caution['recommended_action']
    
    def test_key_takeaways_generation(self, workflow_service, mock_analysis_result, mock_validation_result):
        """Test key takeaways generation."""
        
        takeaways = workflow_service._generate_key_takeaways(
            mock_analysis_result, mock_validation_result
        )
        
        assert isinstance(takeaways, list)
        assert len(takeaways) <= 3  # Should limit to 3 key takeaways
        assert len(takeaways) > 0  # Should generate at least one takeaway
        
        # Should include key insights from the analysis
        takeaway_text = ' '.join(takeaways)
        assert any(keyword in takeaway_text.lower() for keyword in ['strength', 'concern', 'assumption'])
    
    @pytest.mark.asyncio
    async def test_optimized_data_fetching(self, workflow_service):
        """Test that data fetching is optimized for cost and performance."""
        
        # Test company data optimization
        with patch('yfinance.Ticker') as mock_ticker:
            mock_stock = MagicMock()
            mock_stock.info = {'longName': 'Test Company', 'sector': 'Technology'}
            mock_stock.history.return_value.empty = False
            mock_stock.history.return_value.tail.return_value.to_dict.return_value = {'Close': {}}
            mock_stock.quarterly_financials = None
            mock_stock.quarterly_balance_sheet = None
            mock_stock.quarterly_cashflow = None
            mock_ticker.return_value = mock_stock
            
            result = await workflow_service._fetch_company_data('TEST.NS')
            
            assert result is not None
            
            # Should use quarterly data (more recent) instead of annual
            # Should limit history to 30 days instead of full year
            mock_stock.history.assert_called_with(period="3mo")
            mock_stock.history.return_value.tail.assert_called_with(30)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])