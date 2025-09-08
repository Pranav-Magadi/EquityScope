import asyncio
import logging
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
import yfinance as yf
from .optimized_ai_service import optimized_ai_service
from .multi_model_dcf import multi_model_dcf_service
from .news_scraper import news_scraper
from .intelligent_cache import intelligent_cache, CacheType
from ..models.dcf import DCFAssumptions, DCFValuation

logger = logging.getLogger(__name__)

class OptimizedWorkflowService:
    """
    Optimized workflow service implementing 2-agent architecture for cost efficiency.
    
    Target Cost Reduction: 50% (from ~$0.60-1.20 to ~$0.30 per analysis)
    Target Response Time: 30 seconds (from 45-90 seconds)
    
    Architecture:
    1. Analysis Engine Agent (8K tokens) - Consolidated financial analysis  
    2. DCF Validator Agent (2K tokens) - Focused assumption validation
    
    Total: ~10K tokens vs original ~24K tokens
    """
    
    def __init__(self):
        self.progress_callbacks = []
        self.cache_manager = intelligent_cache
    
    def _sanitize_nan_values(self, data):
        """Recursively replace NaN values with None for JSON serialization."""
        import math
        
        if isinstance(data, dict):
            return {k: self._sanitize_nan_values(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._sanitize_nan_values(item) for item in data]
        elif isinstance(data, float):
            if math.isnan(data) or math.isinf(data):
                return None
            return data
        else:
            return data
    
    def add_progress_callback(self, callback: Callable):
        """Add a progress callback function."""
        self.progress_callbacks.append(callback)
    
    def _notify_progress(self, step: str, progress: int, message: str):
        """Notify all progress callbacks."""
        for callback in self.progress_callbacks:
            try:
                callback(step, progress, message)
            except Exception as e:
                logger.error(f"Error in progress callback: {e}")
    
    async def execute_optimized_analysis(
        self,
        ticker: str,
        user_assumptions: Optional[DCFAssumptions] = None,
        max_news_articles: int = 5,  # Reduced from 10 for cost optimization
        cancellation_checker: Optional[Callable] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Execute optimized 2-agent workflow for financial analysis.
        
        Args:
            ticker: Stock ticker symbol (e.g., 'RELIANCE.NS')
            user_assumptions: Optional DCF assumptions from user
            max_news_articles: Maximum news articles to process (reduced for cost)
            cancellation_checker: Function to check if analysis should be cancelled
            
        Returns:
            Optimized analysis with cost and performance improvements
        """
        if not optimized_ai_service.is_available():
            logger.error("Optimized AI service not available")
            return None
        
        analysis_start = datetime.now()
        logger.info(f"Starting optimized workflow analysis for {ticker}")
        
        try:
            # Helper function to check for cancellation
            def _check_cancellation():
                if cancellation_checker and cancellation_checker():
                    raise asyncio.CancelledError("Analysis cancelled by user")
            
            # Step 1: Data Ingestion (Optimized)
            _check_cancellation()
            self._notify_progress("ingestion", 10, f"Gathering {ticker} financial data...")
            
            # Parallel data fetching for speed optimization
            company_task = self._fetch_company_data(ticker)
            news_task = self._fetch_news_data(ticker, max_news_articles)
            
            company_data, news_articles = await asyncio.gather(
                company_task, news_task, return_exceptions=True
            )
            
            # Handle exceptions from parallel execution
            if isinstance(company_data, Exception):
                logger.error(f"Company data fetch failed: {company_data}")
                return None
            if isinstance(news_articles, Exception):
                logger.warning(f"News fetch failed: {news_articles}, continuing with empty news")
                news_articles = []
            
            _check_cancellation()
            self._notify_progress("ingestion", 30, "Data ingestion complete")
            
            # Step 2: Multi-Model DCF Analysis
            _check_cancellation()
            self._notify_progress("model_selection", 35, "Selecting optimal valuation model...")
            
            # Check cache for model recommendations (24hr TTL)
            cache_key_params = {'has_user_assumptions': user_assumptions is not None}
            cached_multi_model = await self.cache_manager.get(
                CacheType.MODEL_RECOMMENDATIONS, ticker, **cache_key_params
            )
            
            if cached_multi_model:
                logger.info(f"Using cached model recommendations for {ticker}")
                multi_model_result = cached_multi_model
            else:
                # Get fresh model recommendation and multi-model analysis
                multi_model_result = await multi_model_dcf_service.calculate_multi_model_valuation(
                    ticker, company_data, user_assumptions.revenue_growth_rate if user_assumptions else None
                )
                
                # Cache model recommendations for 24 hours
                if multi_model_result:
                    await self.cache_manager.set(
                        CacheType.MODEL_RECOMMENDATIONS, ticker, multi_model_result, **cache_key_params
                    )
            
            _check_cancellation()
            self._notify_progress("analysis", 50, "Running AI Analysis Engine...")
            
            # Check cache for AI insights (6hr TTL)
            news_hash = str(hash(str(news_articles[:2])))  # Hash first 2 articles for cache key
            ai_cache_params = {
                'news_hash': news_hash,
                'news_count': len(news_articles),
                'has_user_assumptions': user_assumptions is not None
            }
            
            cached_analysis = await self.cache_manager.get(
                CacheType.AI_INSIGHTS, ticker, **ai_cache_params
            )
            
            if cached_analysis:
                logger.info(f"Using cached AI analysis for {ticker}")
                analysis_result = cached_analysis
            else:
                # Enhanced analysis with model-specific context
                analysis_result = await optimized_ai_service.analysis_engine_agent(
                    company_data, news_articles
                )
                
                if not analysis_result:
                    logger.error("Analysis Engine failed")
                    return None
                
                # Cache AI insights for 6 hours
                await self.cache_manager.set(
                    CacheType.AI_INSIGHTS, ticker, analysis_result, **ai_cache_params
                )
            
            _check_cancellation()
            self._notify_progress("analysis", 70, "Analysis Engine complete")
            
            # Step 3: DCF Validator (Focused Validation)
            _check_cancellation()
            self._notify_progress("validation", 80, "Running DCF Validator (assumption validation)...")
            
            # Use user assumptions if provided, otherwise use AI-generated ones
            dcf_assumptions = user_assumptions or DCFAssumptions(
                revenue_growth_rate=analysis_result.get('dcf_assumptions', {}).get('revenue_growth_rate', 8.0),
                ebitda_margin=analysis_result.get('dcf_assumptions', {}).get('ebitda_margin', 15.0),
                tax_rate=analysis_result.get('dcf_assumptions', {}).get('tax_rate', 25.0),
                wacc=analysis_result.get('dcf_assumptions', {}).get('wacc', 12.0),
                terminal_growth_rate=analysis_result.get('dcf_assumptions', {}).get('terminal_growth_rate', 3.0)
            )
            
            validation_result = await optimized_ai_service.dcf_validator_agent(
                analysis_result, company_data
            )
            
            if not validation_result:
                logger.error("DCF Validator failed")
                return None
            
            _check_cancellation()
            self._notify_progress("validation", 90, "DCF validation complete")
            
            # Step 4: Result Compilation
            self._notify_progress("compilation", 95, "Compiling final analysis...")
            
            analysis_duration = (datetime.now() - analysis_start).total_seconds()
            
            # Get cache statistics for metadata
            cache_stats = await self.cache_manager.get_cache_stats()
            
            # Optimized result structure with multi-model integration
            result = {
                "metadata": {
                    "ticker": ticker,
                    "company_name": company_data.get('info', {}).get('longName', ticker),
                    "analysis_timestamp": analysis_start.isoformat(),
                    "analysis_duration_seconds": analysis_duration,
                    "news_articles_analyzed": len(news_articles),
                    "workflow_version": "2.0-optimized-multimodel-cached",
                    "cost_optimization": {
                        "agent_count": 2,
                        "estimated_tokens": 10000,
                        "estimated_cost_usd": 0.30,
                        "cost_reduction_vs_v1": "50%"
                    },
                    "cache_performance": {
                        "hit_rate_percentage": cache_stats['cache_statistics']['hit_rate_percentage'],
                        "total_cost_saved_usd": cache_stats['cache_statistics']['total_cost_saved_usd'],
                        "cache_enabled": True
                    }
                },
                "raw_data": {
                    "financial_data": company_data,
                    "news_articles": news_articles[:3]  # Limited for cost
                },
                "multi_model_analysis": multi_model_result,
                "analysis_engine_output": analysis_result,
                "dcf_validation_output": validation_result,
                "enhanced_insights": self._generate_enhanced_insights(
                    analysis_result, validation_result, company_data, multi_model_result
                ),
                "user_guidance": self._generate_user_guidance(
                    analysis_result, validation_result, multi_model_result
                )
            }
            
            self._notify_progress("complete", 100, f"Analysis complete in {analysis_duration:.1f}s!")
            
            logger.info(f"Optimized workflow completed for {ticker} in {analysis_duration:.1f} seconds")
            return self._sanitize_nan_values(result)
            
        except asyncio.CancelledError:
            logger.info(f"Analysis cancelled for {ticker}")
            self._notify_progress("cancelled", 0, "Analysis cancelled by user")
            return None
            
        except Exception as e:
            logger.error(f"Error in optimized workflow for {ticker}: {e}")
            self._notify_progress("error", 0, f"Analysis failed: {str(e)}")
            return None
    
    async def _fetch_company_data(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Fetch company financial data with intelligent caching (24hr TTL)."""
        try:
            # Check cache first
            cached_data = await self.cache_manager.get(CacheType.FINANCIAL_DATA, ticker)
            if cached_data:
                logger.info(f"Using cached financial data for {ticker}")
                return cached_data
            
            logger.info(f"Fetching fresh financial data for {ticker}")
            
            stock = yf.Ticker(ticker)
            
            # Get basic info
            info = stock.info
            if not info or not info.get('longName'):
                logger.error(f"No company info found for {ticker}")
                return None
            
            # Get essential data only (optimization)
            hist = stock.history(period="3mo")  # Reduced from 1y
            
            # Get financial statements with error handling
            try:
                # Only fetch most recent financial data for cost optimization
                financials = stock.quarterly_financials  # Use quarterly for recency
                balance_sheet = stock.quarterly_balance_sheet
                cash_flow = stock.quarterly_cashflow
            except Exception as e:
                logger.warning(f"Could not fetch detailed financials for {ticker}: {e}")
                financials = balance_sheet = cash_flow = None
            
            # Optimized data structure
            data = {
                "ticker": ticker,
                "info": info,
                "history": hist.tail(30).to_dict() if not hist.empty else {},  # Last 30 days only
                "financials": financials.iloc[:, :4].to_dict() if financials is not None else {},  # Last 4 quarters
                "balance_sheet": balance_sheet.iloc[:, :4].to_dict() if balance_sheet is not None else {},
                "cash_flow": cash_flow.iloc[:, :4].to_dict() if cash_flow is not None else {},
                "fetched_at": datetime.now().isoformat()
            }
            
            # Cache the data for 24 hours
            await self.cache_manager.set(CacheType.FINANCIAL_DATA, ticker, data)
            
            return data
            
        except Exception as e:
            logger.error(f"Error fetching company data for {ticker}: {e}")
            return None
    
    async def _fetch_news_data(self, ticker: str, max_articles: int) -> List[Dict[str, Any]]:
        """Fetch recent news articles with intelligent caching (6hr TTL)."""
        try:
            # Check cache first
            cache_key_params = {'max_articles': max_articles}
            cached_articles = await self.cache_manager.get(
                CacheType.NEWS_ARTICLES, ticker, **cache_key_params
            )
            if cached_articles:
                logger.info(f"Using cached news data for {ticker}")
                return cached_articles
            
            # Extract company name for search
            stock = yf.Ticker(ticker)
            company_name = stock.info.get('longName', ticker.replace('.NS', ''))
            
            logger.info(f"Fetching fresh news: {max_articles} articles about {company_name}")
            
            # Optimized news scraping
            async with news_scraper:
                articles = await news_scraper.search_company_news(
                    company_name=company_name,
                    ticker=ticker,
                    max_articles=max_articles,
                    days_back=14  # Reduced from 30 for cost optimization
                )
            
            # Cache the articles for 6 hours
            if articles:
                await self.cache_manager.set(
                    CacheType.NEWS_ARTICLES, ticker, articles, **cache_key_params
                )
            
            logger.info(f"Found {len(articles)} news articles for {ticker}")
            return articles
            
        except Exception as e:
            logger.error(f"Error fetching news data for {ticker}: {e}")
            return []
    
    def _generate_enhanced_insights(
        self, 
        analysis_result: Dict[str, Any], 
        validation_result: Dict[str, Any],
        company_data: Dict[str, Any],
        multi_model_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate enhanced insights by combining analysis and validation."""
        try:
            info = company_data.get('info', {})
            current_price = info.get('currentPrice') or info.get('regularMarketPrice', 0)
            
            # Extract key insights
            investment_thesis = analysis_result.get('company_overview', {}).get('investment_thesis', '')
            key_strengths = analysis_result.get('company_overview', {}).get('key_strengths', [])
            key_risks = analysis_result.get('company_overview', {}).get('key_risks', [])
            
            # Extract validation feedback
            overall_assessment = validation_result.get('validation_summary', {}).get('overall_assessment', 'reasonable')
            key_concerns = validation_result.get('validation_summary', {}).get('key_concerns', [])
            
            # Extract multi-model insights
            model_recommendation = multi_model_result.get('model_recommendation', {})
            recommended_model = model_recommendation.get('recommended_model', {})
            valuation_summary = multi_model_result.get('valuation_summary', {})
            
            # Generate enhanced insights with multi-model context
            enhanced_insights = {
                "investment_summary": {
                    "thesis": investment_thesis,
                    "confidence_level": validation_result.get('validation_summary', {}).get('confidence_level', 'medium'),
                    "recommendation_basis": f"Analysis shows {overall_assessment} assumptions with {len(key_strengths)} key strengths identified",
                    "valuation_model": {
                        "recommended": recommended_model.get('model', 'DCF'),
                        "rationale": recommended_model.get('rationale', ''),
                        "confidence": recommended_model.get('confidence_score', 0.7)
                    }
                },
                "risk_reward_profile": {
                    "primary_strengths": key_strengths[:3],
                    "primary_risks": key_risks[:3], 
                    "validation_concerns": key_concerns[:2],
                    "overall_risk_level": self._calculate_risk_level(key_risks, key_concerns)
                },
                "assumption_insights": {
                    "most_critical": validation_result.get('sensitivity_insights', {}).get('most_sensitive_assumption', 'revenue_growth_rate'),
                    "confidence_score": validation_result.get('validation_summary', {}).get('confidence_level', 'medium'),
                    "peer_context": analysis_result.get('financial_health', {}).get('key_metrics_analysis', ''),
                    "model_specific": self._get_model_specific_insights(recommended_model.get('model', 'DCF'))
                },
                "valuation_insights": {
                    "consensus_recommendation": valuation_summary.get('consensus', {}).get('recommendation', 'Hold'),
                    "valuation_range": valuation_summary.get('valuation_range', {}),
                    "model_agreement": valuation_summary.get('consensus', {}).get('confidence', 'medium')
                },
                "action_guidance": self._generate_action_guidance(analysis_result, validation_result, current_price, valuation_summary)
            }
            
            return enhanced_insights
            
        except Exception as e:
            logger.error(f"Error generating enhanced insights: {e}")
            return {}
    
    def _generate_user_guidance(
        self,
        analysis_result: Dict[str, Any],
        validation_result: Dict[str, Any],
        multi_model_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate user-friendly guidance and education."""
        try:
            # Extract model information
            recommended_model = multi_model_result.get('model_recommendation', {}).get('recommended_model', {})
            model_name = recommended_model.get('model', 'DCF')
            
            return {
                "what_this_means": {
                    "financial_health": self._interpret_financial_health(analysis_result),
                    "valuation_context": self._interpret_valuation(validation_result),
                    "model_selection": self._interpret_model_selection(recommended_model),
                    "key_takeaways": self._generate_key_takeaways(analysis_result, validation_result, multi_model_result)
                },
                "next_steps": {
                    "immediate_actions": [
                        f"Review the {model_name} model assumptions and adjust if needed",
                        "Check the multi-model valuation range for consensus",
                        "Consider the identified risks in your investment decision"
                    ],
                    "further_research": [
                        "Compare with similar companies using the same model",
                        "Monitor the key risk factors identified",
                        "Review industry-specific trends and outlook"
                    ]
                },
                "educational_content": {
                    **analysis_result.get('education_content', {}),
                    "model_education": self._get_model_education(model_name)
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating user guidance: {e}")
            return {}
    
    def _calculate_risk_level(self, risks: List[str], concerns: List[str]) -> str:
        """Calculate overall risk level based on identified risks and concerns."""
        total_issues = len(risks) + len(concerns)
        
        if total_issues <= 2:
            return "Low"
        elif total_issues <= 4:
            return "Medium" 
        else:
            return "High"
    
    def _generate_action_guidance(
        self, 
        analysis_result: Dict[str, Any], 
        validation_result: Dict[str, Any],
        current_price: float,
        valuation_summary: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate specific action guidance for users."""
        try:
            confidence = validation_result.get('validation_summary', {}).get('confidence_level', 'medium')
            assessment = validation_result.get('validation_summary', {}).get('overall_assessment', 'reasonable')
            
            # Use valuation summary if available
            if valuation_summary and 'consensus' in valuation_summary:
                consensus = valuation_summary['consensus']
                recommendation = consensus.get('recommendation', 'Hold')
                model_confidence = consensus.get('confidence', 'medium')
                
                # Map recommendation to action and color
                action_mapping = {
                    'Strong Buy': ("Strong buy candidate - multiple models agree", "green"),
                    'Buy': ("Consider for investment - positive valuation consensus", "green"),
                    'Hold': ("Hold or do additional research - mixed signals", "yellow"),
                    'Sell': ("Exercise caution - valuation concerns identified", "red"),
                    'Strong Sell': ("Avoid investment - significant overvaluation", "red")
                }
                
                action, color = action_mapping.get(recommendation, ("Additional research recommended", "yellow"))
                rationale = f"Multi-model consensus: {recommendation} with {model_confidence} agreement"
                
            else:
                # Fallback to original logic
                if confidence == 'high' and assessment == 'conservative':
                    action = "Consider for investment - assumptions appear conservative"
                    color = "green"
                elif confidence == 'low' or assessment == 'aggressive':
                    action = "Exercise caution - review assumptions carefully"
                    color = "red"
                else:
                    action = "Reasonable investment candidate - do additional research"
                    color = "yellow"
                
                rationale = f"Based on {assessment} assumptions with {confidence} confidence"
            
            return {
                "recommended_action": action,
                "confidence_indicator": confidence,
                "color_code": color,
                "rationale": rationale
            }
            
        except Exception as e:
            logger.error(f"Error generating action guidance: {e}")
            return {}
    
    def _interpret_financial_health(self, analysis_result: Dict[str, Any]) -> str:
        """Interpret financial health for users."""
        health = analysis_result.get('financial_health', {})
        profitability = health.get('profitability_score', 'moderate')
        liquidity = health.get('liquidity_score', 'moderate')
        growth = health.get('growth_trajectory', 'stable')
        
        return f"The company shows {profitability} profitability, {liquidity} liquidity, and {growth} growth trajectory."
    
    def _interpret_valuation(self, validation_result: Dict[str, Any]) -> str:
        """Interpret valuation context for users.""" 
        assessment = validation_result.get('validation_summary', {}).get('overall_assessment', 'reasonable')
        confidence = validation_result.get('validation_summary', {}).get('confidence_level', 'medium')
        
        return f"The DCF assumptions appear {assessment} with {confidence} confidence based on peer comparisons and historical data."
    
    def _generate_key_takeaways(
        self, 
        analysis_result: Dict[str, Any],
        validation_result: Dict[str, Any],
        multi_model_result: Dict[str, Any]
    ) -> List[str]:
        """Generate key takeaways for users."""
        takeaways = []
        
        # Add key insights from analysis
        if analysis_result.get('company_overview', {}).get('key_strengths'):
            strengths = analysis_result['company_overview']['key_strengths']
            if strengths:
                takeaways.append(f"Key strength: {strengths[0]}")
        
        # Add validation insights
        if validation_result.get('validation_summary', {}).get('key_concerns'):
            concerns = validation_result['validation_summary']['key_concerns']
            if concerns:
                takeaways.append(f"Main concern: {concerns[0]}")
        
        # Add sensitivity insight
        sensitive_assumption = validation_result.get('sensitivity_insights', {}).get('most_sensitive_assumption')
        if sensitive_assumption:
            takeaways.append(f"Most important assumption: {sensitive_assumption.replace('_', ' ').title()}")
        
        # Add multi-model insight
        if multi_model_result.get('valuation_summary'):
            consensus = multi_model_result['valuation_summary'].get('consensus', {})
            recommendation = consensus.get('recommendation')
            if recommendation:
                takeaways.append(f"Multi-model consensus: {recommendation}")
        
        return takeaways[:3]  # Limit to 3 key takeaways
    
    def _get_model_specific_insights(self, model: str) -> str:
        """Get model-specific insights for user education."""
        
        insights = {
            'DCF': 'Focus on cash flow generation and growth sustainability',
            'DDM': 'Emphasis on dividend consistency and payout sustainability', 
            'Asset': 'Asset quality and replacement value considerations'
        }
        
        return insights.get(model, 'General valuation considerations')
    
    def _interpret_model_selection(self, recommended_model: Dict[str, Any]) -> str:
        """Interpret model selection for users."""
        
        model = recommended_model.get('model', 'DCF')
        rationale = recommended_model.get('rationale', '')
        confidence = recommended_model.get('confidence_score', 0.7)
        
        confidence_text = 'high' if confidence > 0.8 else 'medium' if confidence > 0.6 else 'moderate'
        
        return f"We recommend the {model} model with {confidence_text} confidence. {rationale}"
    
    def _get_model_education(self, model: str) -> Dict[str, str]:
        """Get educational content for the selected model."""
        
        education = {
            'DCF': {
                'what_it_is': 'DCF values a company based on projected future cash flows discounted to present value',
                'key_assumptions': 'Revenue growth, profit margins, capital requirements, and discount rate',
                'best_for': 'Companies with predictable cash flows like technology and consumer businesses',
                'limitations': 'Sensitive to assumption changes; less suitable for asset-heavy businesses'
            },
            'DDM': {
                'what_it_is': 'DDM values companies based on expected future dividend payments',
                'key_assumptions': 'Dividend growth rate, payout ratio, and cost of equity',
                'best_for': 'Financial services companies that focus on returning capital to shareholders',
                'limitations': 'Only works for dividend-paying companies; sensitive to dividend policy changes'
            },
            'Asset': {
                'what_it_is': 'Asset-based valuation focuses on the underlying value of company assets',
                'key_assumptions': 'Book value, asset utilization, and replacement costs',
                'best_for': 'Asset-heavy companies like REITs, utilities, and infrastructure firms',
                'limitations': 'May not capture intangible value or growth potential'
            }
        }
        
        return education.get(model, education['DCF'])

# Global service instance
optimized_workflow = OptimizedWorkflowService()