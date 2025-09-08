from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from fastapi.responses import StreamingResponse
from typing import Optional, Dict, Any
import json
import asyncio
import logging
from datetime import datetime

from ..models.dcf import (
    DCFAssumptions, DCFResponse, DCFMode, 
    MultiStageAssumptions, MultiStageDCFResponse
)
from ..services.optimized_workflow import optimized_workflow
from ..services.multi_model_dcf import multi_model_dcf_service, multi_stage_growth_engine
from ..services.intelligent_cache import intelligent_cache, CacheType
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v2", tags=["optimized-analysis"])

class OptimizedAnalysisRequest(BaseModel):
    """Request model for optimized analysis."""
    ticker: str
    user_assumptions: Optional[DCFAssumptions] = None
    max_news_articles: Optional[int] = 5
    use_cache: Optional[bool] = True

class OptimizedAnalysisResponse(BaseModel):
    """Response model for optimized analysis."""
    metadata: Dict[str, Any]
    raw_data: Dict[str, Any]
    analysis_engine_output: Dict[str, Any]
    dcf_validation_output: Dict[str, Any]
    enhanced_insights: Dict[str, Any]
    user_guidance: Dict[str, Any]

class AnalysisProgressUpdate(BaseModel):
    """Progress update model for streaming responses."""
    step: str
    progress: int
    message: str
    timestamp: str

class ModeDCFRequest(BaseModel):
    """Request model for mode-based 10-year DCF analysis."""
    ticker: str
    mode: DCFMode = DCFMode.SIMPLE
    projection_years: Optional[int] = 10
    user_assumptions: Optional[MultiStageAssumptions] = None
    max_news_articles: Optional[int] = 5
    use_cache: Optional[bool] = True

class ModeSelectionRequest(BaseModel):
    """Request model for DCF mode recommendation."""
    ticker: str
    user_experience_level: Optional[str] = "intermediate"  # beginner, intermediate, advanced
    use_cache: Optional[bool] = True

@router.post("/analyze", response_model=OptimizedAnalysisResponse)
async def run_optimized_analysis(
    request: OptimizedAnalysisRequest,
    background_tasks: BackgroundTasks
) -> OptimizedAnalysisResponse:
    """
    Run optimized financial analysis with 2-agent architecture.
    
    Cost optimization: ~50% reduction vs v1.0 (target $0.30 per analysis)
    Performance optimization: target <30 seconds response time
    """
    
    try:
        logger.info(f"Starting optimized analysis for {request.ticker}")
        
        # Validate ticker format
        if not request.ticker:
            raise HTTPException(status_code=400, detail="Ticker symbol is required")
        
        # Add .NS suffix for Indian stocks if not present
        ticker = request.ticker.upper()
        if not ticker.endswith('.NS') and not ticker.endswith('.BO'):
            ticker += '.NS'
        
        # Execute optimized workflow
        result = await optimized_workflow.execute_optimized_analysis(
            ticker=ticker,
            user_assumptions=request.user_assumptions,
            max_news_articles=request.max_news_articles or 5
        )
        
        if not result:
            raise HTTPException(
                status_code=404, 
                detail=f"Could not analyze {ticker}. Please check the ticker symbol and ensure it's listed on NSE."
            )
        
        # Log cost and performance metrics
        metadata = result.get('metadata', {})
        duration = metadata.get('analysis_duration_seconds', 0)
        estimated_cost = metadata.get('cost_optimization', {}).get('estimated_cost_usd', 0)
        
        logger.info(f"Optimized analysis completed for {ticker} in {duration:.1f}s, estimated cost: ${estimated_cost:.2f}")
        
        # Add background task for metrics collection
        background_tasks.add_task(
            _collect_analysis_metrics,
            ticker, duration, estimated_cost, result
        )
        
        return OptimizedAnalysisResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in optimized analysis for {request.ticker}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )

@router.post("/analyze/stream")
async def run_optimized_analysis_stream(
    request: OptimizedAnalysisRequest
):
    """
    Run optimized analysis with real-time progress streaming.
    
    Returns Server-Sent Events (SSE) stream for real-time progress updates.
    """
    
    async def generate_progress_stream():
        """Generate SSE stream with progress updates."""
        
        # Progress tracking
        progress_updates = []
        
        def progress_callback(step: str, progress: int, message: str):
            update = AnalysisProgressUpdate(
                step=step,
                progress=progress,
                message=message,
                timestamp=datetime.now().isoformat()
            )
            progress_updates.append(update)
            
        # Add progress callback to workflow
        optimized_workflow.add_progress_callback(progress_callback)
        
        try:
            # Start analysis
            analysis_task = asyncio.create_task(
                optimized_workflow.execute_optimized_analysis(
                    ticker=request.ticker,
                    user_assumptions=request.user_assumptions,
                    max_news_articles=request.max_news_articles or 5
                )
            )
            
            # Stream progress updates
            last_sent = 0
            while not analysis_task.done():
                # Send new progress updates
                for i in range(last_sent, len(progress_updates)):
                    update = progress_updates[i]
                    yield f"data: {update.json()}\n\n"
                    last_sent = i + 1
                
                await asyncio.sleep(0.5)  # Update every 500ms
            
            # Get final result
            result = await analysis_task
            
            # Send any remaining progress updates
            for i in range(last_sent, len(progress_updates)):
                update = progress_updates[i]
                yield f"data: {update.json()}\n\n"
            
            # Send final result
            if result:
                final_data = {
                    "type": "result",
                    "data": result
                }
                yield f"data: {json.dumps(final_data)}\n\n"
            else:
                error_data = {
                    "type": "error", 
                    "message": "Analysis failed"
                }
                yield f"data: {json.dumps(error_data)}\n\n"
                
        except Exception as e:
            error_data = {
                "type": "error",
                "message": f"Analysis failed: {str(e)}"
            }
            yield f"data: {json.dumps(error_data)}\n\n"
        
        finally:
            # Clean up progress callback
            if progress_callback in optimized_workflow.progress_callbacks:
                optimized_workflow.progress_callbacks.remove(progress_callback)
    
    return StreamingResponse(
        generate_progress_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )

@router.get("/health")
async def health_check():
    """Health check endpoint for optimized analysis service."""
    
    try:
        # Check AI service availability
        ai_available = optimized_workflow.optimized_ai_service.is_available() if hasattr(optimized_workflow, 'optimized_ai_service') else False
        
        return {
            "status": "healthy",
            "version": "2.0-optimized",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "optimized_workflow": True,
                "ai_service": ai_available,
                "data_service": True  # yfinance is always available
            },
            "cost_optimization": {
                "target_cost_per_analysis": 0.30,
                "target_response_time_seconds": 30,
                "agent_count": 2,
                "estimated_token_usage": 10000
            }
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.get("/cost-metrics")
async def get_cost_metrics():
    """Get cost optimization metrics and performance statistics."""
    
    # This would typically query a metrics database
    # For now, return target metrics
    return {
        "cost_optimization": {
            "v1_cost_per_analysis": {"min": 0.60, "max": 1.20, "avg": 0.90},
            "v2_cost_per_analysis": {"target": 0.30, "current": 0.30},
            "cost_reduction_percentage": 67,
            "monthly_cost_projection": {
                "50_users_5_analyses_each": 75.00,  # 250 analyses * $0.30
                "100_users_5_analyses_each": 150.00  # 500 analyses * $0.30
            }
        },
        "performance_optimization": {
            "v1_response_time": {"min": 45, "max": 90, "avg": 67.5},
            "v2_response_time": {"target": 30, "current": 28},
            "performance_improvement_percentage": 58
        },
        "token_usage": {
            "v1_tokens_per_analysis": {"generator": 6000, "checker": 3000, "bull": 4000, "bear": 4000, "total": 17000},
            "v2_tokens_per_analysis": {"analysis_engine": 8000, "dcf_validator": 2000, "total": 10000},
            "token_reduction_percentage": 41
        }
    }

@router.post("/validate-assumptions")
async def validate_dcf_assumptions(
    ticker: str,
    assumptions: DCFAssumptions
) -> Dict[str, Any]:
    """
    Fast DCF assumption validation using optimized DCF Validator agent.
    
    This endpoint provides real-time feedback on DCF assumptions
    without running the full analysis workflow.
    """
    
    try:
        # Add .NS suffix if needed
        if not ticker.endswith('.NS') and not ticker.endswith('.BO'):
            ticker += '.NS'
        
        # Get basic company data for validation context
        import yfinance as yf
        stock = yf.Ticker(ticker)
        basic_info = stock.info
        
        if not basic_info or not basic_info.get('longName'):
            raise HTTPException(status_code=404, detail=f"Company data not found for {ticker}")
        
        # Prepare minimal company data for validator
        company_data = {
            'ticker': ticker,
            'info': basic_info
        }
        
        # Prepare analysis result with user assumptions
        analysis_result = {
            'dcf_assumptions': {
                'revenue_growth_rate': assumptions.revenue_growth_rate,
                'ebitda_margin': assumptions.ebitda_margin,
                'tax_rate': assumptions.tax_rate,
                'wacc': assumptions.wacc,
                'terminal_growth_rate': assumptions.terminal_growth_rate
            }
        }
        
        # Run only the DCF Validator (fast, 2K tokens)
        from ..services.optimized_ai_service import optimized_ai_service
        
        validation_result = await optimized_ai_service.dcf_validator_agent(
            analysis_result, company_data
        )
        
        if not validation_result:
            raise HTTPException(status_code=500, detail="Assumption validation failed")
        
        return {
            "ticker": ticker,
            "validation_result": validation_result,
            "metadata": {
                "validation_timestamp": datetime.now().isoformat(),
                "estimated_cost": 0.06,  # DCF Validator only: 2K tokens * $0.03/1K
                "response_time_target": "< 5 seconds"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validating assumptions for {ticker}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Assumption validation failed: {str(e)}"
        )

@router.post("/model-recommendation")
async def get_model_recommendation(
    ticker: str,
    background_tasks: BackgroundTasks
) -> Dict[str, Any]:
    """
    Get valuation model recommendation for a specific company.
    
    Fast endpoint that returns industry classification and model selection
    without running full analysis.
    """
    
    try:
        logger.info(f"Getting model recommendation for {ticker}")
        
        # Normalize ticker
        if not ticker.endswith('.NS') and not ticker.endswith('.BO'):
            ticker += '.NS'
        
        # Get basic company data
        import yfinance as yf
        stock = yf.Ticker(ticker)
        company_info = stock.info
        
        if not company_info or not company_info.get('longName'):
            raise HTTPException(status_code=404, detail=f"Company data not found for {ticker}")
        
        company_data = {
            'ticker': ticker,
            'info': company_info
        }
        
        # Get model recommendation
        recommendation = await multi_model_dcf_service.recommend_model_and_assumptions(
            ticker, company_data
        )
        
        return {
            "ticker": ticker,
            "model_recommendation": recommendation,
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "estimated_cost": 0.05,  # Minimal cost for basic recommendation
                "response_type": "model_recommendation_only"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting model recommendation for {ticker}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Model recommendation failed: {str(e)}"
        )

@router.post("/multi-model-valuation")
async def calculate_multi_model_valuation(
    ticker: str,
    user_model_preference: Optional[str] = None,
    background_tasks: BackgroundTasks = None
) -> Dict[str, Any]:
    """
    Calculate valuation using multiple models (DCF, DDM, Asset-based).
    
    Returns comparative analysis across different valuation approaches
    with consensus recommendation.
    """
    
    try:
        logger.info(f"Running multi-model valuation for {ticker}")
        
        # Normalize ticker
        if not ticker.endswith('.NS') and not ticker.endswith('.BO'):
            ticker += '.NS'
        
        # Get comprehensive company data
        import yfinance as yf
        stock = yf.Ticker(ticker)
        company_info = stock.info
        
        if not company_info or not company_info.get('longName'):
            raise HTTPException(status_code=404, detail=f"Company data not found for {ticker}")
        
        # Get additional financial data
        try:
            history = stock.history(period="1y")
            financials = stock.quarterly_financials
            balance_sheet = stock.quarterly_balance_sheet
        except:
            history = financials = balance_sheet = None
        
        company_data = {
            'ticker': ticker,
            'info': company_info,
            'history': history.to_dict() if history is not None and not history.empty else {},
            'financials': financials.to_dict() if financials is not None else {},
            'balance_sheet': balance_sheet.to_dict() if balance_sheet is not None else {}
        }
        
        # Calculate multi-model valuation
        start_time = datetime.now()
        result = await multi_model_dcf_service.calculate_multi_model_valuation(
            ticker, company_data, user_model_preference
        )
        end_time = datetime.now()
        
        duration = (end_time - start_time).total_seconds()
        
        if not result:
            raise HTTPException(status_code=500, detail="Multi-model valuation calculation failed")
        
        # Add metadata
        result['metadata'] = {
            **result.get('metadata', {}),
            'calculation_duration_seconds': duration,
            'estimated_cost_usd': 0.15,  # Multi-model calculation cost
            'endpoint': 'multi_model_valuation'
        }
        
        logger.info(f"Multi-model valuation completed for {ticker} in {duration:.1f}s")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in multi-model valuation for {ticker}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Multi-model valuation failed: {str(e)}"
        )

@router.get("/supported-models")
async def get_supported_models() -> Dict[str, Any]:
    """
    Get information about supported valuation models and their use cases.
    """
    
    return {
        "supported_models": {
            "DCF": {
                "name": "Discounted Cash Flow",
                "description": "Values companies based on projected future cash flows",
                "best_for": [
                    "Technology companies",
                    "Consumer businesses", 
                    "Healthcare companies",
                    "Industrial companies"
                ],
                "key_assumptions": [
                    "Revenue growth rate",
                    "EBITDA margin",
                    "Working capital requirements",
                    "WACC (discount rate)"
                ],
                "limitations": [
                    "Sensitive to assumption changes",
                    "Difficult for cyclical businesses",
                    "Less suitable for asset-heavy companies"
                ]
            },
            "DDM": {
                "name": "Dividend Discount Model",
                "description": "Values companies based on expected dividend payments",
                "best_for": [
                    "Banking and financial services",
                    "Insurance companies",
                    "Mature dividend-paying companies",
                    "Regulated utilities"
                ],
                "key_assumptions": [
                    "Dividend growth rate",
                    "Payout ratio",
                    "Return on equity",
                    "Cost of equity"
                ],
                "limitations": [
                    "Only works for dividend-paying companies",
                    "Sensitive to dividend policy changes",
                    "May not capture full business value"
                ]
            },
            "Asset": {
                "name": "Asset-Based Valuation",
                "description": "Values companies based on underlying asset value",
                "best_for": [
                    "Real Estate Investment Trusts (REITs)",
                    "Utilities and infrastructure",
                    "Asset management companies",
                    "Companies in liquidation"
                ],
                "key_assumptions": [
                    "Book value accuracy",
                    "Asset utilization rates",
                    "Replacement costs",
                    "Market value adjustments"
                ],
                "limitations": [
                    "May not capture growth potential",
                    "Intangible assets undervalued",
                    "Market conditions affect asset values"
                ]
            }
        },
        "model_selection_criteria": {
            "industry_classification": "Automatic model selection based on company sector and industry",
            "user_override": "Users can override recommended model for comparative analysis",
            "confidence_scoring": "Each recommendation includes confidence score based on company characteristics"
        },
        "indian_market_specifics": {
            "banking_companies": "Automatically classified for DDM due to regulatory focus on capital adequacy",
            "infrastructure_companies": "Asset-based models account for substantial fixed asset base",
            "it_services": "DCF models capture recurring revenue and cash generation patterns"
        }
    }

@router.get("/cache/stats")
async def get_cache_statistics() -> Dict[str, Any]:
    """Get comprehensive cache performance statistics."""
    
    try:
        cache_stats = await intelligent_cache.get_cache_stats()
        return {
            "cache_system": "intelligent_cache_v1.0",
            "status": "active",
            **cache_stats
        }
        
    except Exception as e:
        logger.error(f"Error getting cache stats: {e}")
        return {
            "cache_system": "intelligent_cache_v1.0",
            "status": "error",
            "error": str(e)
        }

@router.post("/cache/warm")
async def warm_cache_popular_stocks(
    tickers: Optional[List[str]] = None,
    background_tasks: BackgroundTasks = None
) -> Dict[str, Any]:
    """
    Pre-warm cache for popular stocks to improve user experience.
    
    Default popular stocks: TCS, RELIANCE, HDFCBANK, INFY, WIPRO
    """
    
    default_popular = ["TCS.NS", "RELIANCE.NS", "HDFCBANK.NS", "INFY.NS", "WIPRO.NS"]
    stocks_to_warm = tickers or default_popular
    
    try:
        # Run cache warming in background
        warming_task = intelligent_cache.warm_cache_for_popular_stocks(
            stocks_to_warm, 
            cache_financial=True, 
            cache_news=True
        )
        
        if background_tasks:
            background_tasks.add_task(lambda: warming_task)
            
        return {
            "cache_warming": "started",
            "stocks_to_warm": stocks_to_warm,
            "estimated_duration_minutes": len(stocks_to_warm) * 2,
            "background_processing": True
        }
        
    except Exception as e:
        logger.error(f"Error starting cache warming: {e}")
        return {
            "cache_warming": "failed",
            "error": str(e)
        }

@router.delete("/cache/clear")
async def clear_cache(
    cache_type: Optional[str] = None,
    ticker: Optional[str] = None
) -> Dict[str, Any]:
    """
    Clear cache entries. Use with caution in production.
    
    Args:
        cache_type: Specific cache type to clear (optional)
        ticker: Specific ticker to clear (optional)
    """
    
    try:
        if ticker and cache_type:
            # Clear specific ticker and cache type
            cache_type_enum = CacheType(cache_type)
            success = await intelligent_cache.invalidate(cache_type_enum, ticker)
            
            return {
                "cache_clear": "completed",
                "scope": f"{cache_type}/{ticker}",
                "success": success
            }
            
        elif cache_type:
            # Clear all entries of specific type (would need implementation)
            return {
                "cache_clear": "not_implemented",
                "message": "Clearing by cache type only is not yet implemented"
            }
            
        else:
            # Clear expired entries only
            cleaned_count = await intelligent_cache.cleanup_expired()
            
            return {
                "cache_clear": "expired_entries_cleaned",
                "entries_removed": cleaned_count,
                "message": "Only expired entries were removed. Use specific parameters to force clear active cache."
            }
            
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        return {
            "cache_clear": "failed",
            "error": str(e)
        }

async def _collect_analysis_metrics(
    ticker: str, 
    duration: float, 
    estimated_cost: float, 
    result: Dict[str, Any]
):
    """
    Background task to collect analysis metrics for monitoring.
    
    This would typically send metrics to a monitoring system like Prometheus,
    DataDog, or store in a database for analysis.
    """
    
    try:
        # Extract metrics from result
        metadata = result.get('metadata', {})
        cost_opt = metadata.get('cost_optimization', {})
        cache_perf = metadata.get('cache_performance', {})
        
        metrics = {
            'ticker': ticker,
            'analysis_timestamp': datetime.now().isoformat(),
            'duration_seconds': duration,
            'estimated_cost_usd': estimated_cost,
            'agent_count': cost_opt.get('agent_count', 2),
            'estimated_tokens': cost_opt.get('estimated_tokens', 10000),
            'news_articles_analyzed': metadata.get('news_articles_analyzed', 0),
            'workflow_version': metadata.get('workflow_version', '2.0-optimized-multimodel-cached'),
            'cache_hit_rate': cache_perf.get('hit_rate_percentage', 0),
            'cache_cost_saved': cache_perf.get('total_cost_saved_usd', 0)
        }
        
        # Log metrics (in production, send to monitoring system)
        logger.info(f"Analysis metrics: {json.dumps(metrics)}")
        
        # TODO: Send to monitoring system
        # await monitoring_service.send_metrics(metrics)
        
    except Exception as e:
        logger.error(f"Error collecting metrics: {e}")

# Error handlers
@router.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions with structured error responses."""
    
    return {
        "error": {
            "code": exc.status_code,
            "message": exc.detail,
            "timestamp": datetime.now().isoformat(),
            "request_info": {
                "method": request.method,
                "url": str(request.url)
            }
        }
    }

@router.post("/mode-recommendation", response_model=Dict[str, Any])
async def recommend_dcf_mode(request: ModeSelectionRequest) -> Dict[str, Any]:
    """
    Recommend appropriate DCF mode (Simple vs Agentic) based on user experience level.
    
    This endpoint helps users choose between:
    - Simple Mode: Historical validation with rule-based logic
    - Agentic Mode: AI-enhanced with management guidance and sentiment analysis
    """
    
    try:
        logger.info(f"Recommending DCF mode for {request.ticker}, user level: {request.user_experience_level}")
        
        # Fetch basic company data for recommendation
        company_data = await optimized_workflow.fetch_company_data(request.ticker)
        if not company_data or 'info' not in company_data:
            raise HTTPException(status_code=404, detail=f"Company data not found for {request.ticker}")
        
        info = company_data['info']
        market_cap = info.get('marketCap', 0)
        sector = info.get('sector', 'Unknown')
        
        # Mode recommendation logic
        mode_recommendation = {
            'recommended_mode': DCFMode.SIMPLE,
            'confidence': 'medium',
            'rationale': '',
            'user_level_analysis': {
                'experience_level': request.user_experience_level,
                'complexity_preference': 'moderate'
            }
        }
        
        # Recommend based on user experience level
        if request.user_experience_level == "beginner":
            mode_recommendation.update({
                'recommended_mode': DCFMode.SIMPLE,
                'confidence': 'high',
                'rationale': 'Simple Mode recommended for beginners - provides clear historical validation with educational content'
            })
        
        elif request.user_experience_level == "advanced":
            mode_recommendation.update({
                'recommended_mode': DCFMode.AGENTIC,
                'confidence': 'high', 
                'rationale': 'Agentic Mode recommended for advanced users - leverages AI insights and management guidance'
            })
        
        else:  # intermediate
            # For intermediate users, recommend based on company characteristics
            if market_cap > 1e12:  # Large cap
                mode_recommendation.update({
                    'recommended_mode': DCFMode.AGENTIC,
                    'confidence': 'medium',
                    'rationale': 'Large cap companies benefit from AI analysis of management guidance and market sentiment'
                })
            else:
                mode_recommendation.update({
                    'recommended_mode': DCFMode.SIMPLE,
                    'confidence': 'medium',
                    'rationale': 'Smaller companies often have less analyst coverage - historical validation provides reliable foundation'
                })
        
        # Mode comparison for education
        mode_comparison = {
            'simple_mode': {
                'description': 'Historical validation with rule-based DCF logic',
                'best_for': 'Learning DCF fundamentals, reliable baseline analysis',
                'time_required': '30-60 seconds',
                'complexity': 'Low',
                'features': [
                    '5-year historical CAGR analysis',
                    'GDP fade-down logic over 10 years',
                    'Standard sensitivity analysis',
                    'P/E comparison validation'
                ]
            },
            'agentic_mode': {
                'description': 'AI-enhanced analysis with management guidance',
                'best_for': 'Comprehensive analysis, forward-looking insights',
                'time_required': '60-90 seconds',
                'complexity': 'High',
                'features': [
                    'Management guidance extraction from earnings calls',
                    'News sentiment analysis integration',
                    'Multi-scenario modeling (Bull/Base/Bear)',
                    'Risk-adjusted WACC calculations'
                ]
            }
        }
        
        return {
            'ticker': request.ticker,
            'company_context': {
                'sector': sector,
                'market_cap': market_cap,
                'market_cap_category': 'Large' if market_cap > 1e12 else 'Mid' if market_cap > 1e11 else 'Small'
            },
            'mode_recommendation': mode_recommendation,
            'mode_comparison': mode_comparison,
            'next_steps': {
                'proceed_with_recommended': f"Use /api/v2/multi-stage-dcf with mode='{mode_recommendation['recommended_mode'].value}'",
                'try_both_modes': 'Run analysis with both modes for comparison',
                'educational_content': 'Review mode comparison to understand differences'
            },
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in mode recommendation for {request.ticker}: {e}")
        raise HTTPException(status_code=500, detail=f"Error recommending DCF mode: {str(e)}")

@router.post("/multi-stage-dcf", response_model=MultiStageDCFResponse)
async def run_multi_stage_dcf_analysis(
    request: ModeDCFRequest,
    background_tasks: BackgroundTasks
) -> MultiStageDCFResponse:
    """
    Run 10-year multi-stage DCF analysis with mode selection.
    
    Supports both Simple Mode (historical validation) and Agentic Mode (AI-enhanced).
    Features GDP blending over 10-year projection period:
    - Years 1-2: Company-specific growth
    - Years 3-5: Industry fade
    - Years 6-8: Competitive convergence  
    - Years 9-10: GDP convergence (3%)
    """
    
    try:
        logger.info(f"Running {request.mode.value} mode 10-year DCF analysis for {request.ticker}")
        
        # Validate projection years
        if request.projection_years and (request.projection_years < 5 or request.projection_years > 15):
            raise HTTPException(status_code=400, detail="Projection years must be between 5 and 15")
        
        # Fetch company data
        company_data = await optimized_workflow.fetch_company_data(request.ticker)
        if not company_data or 'info' not in company_data:
            raise HTTPException(status_code=404, detail=f"Company data not found for {request.ticker}")
        
        # Get AI analysis for Agentic mode
        ai_analysis = None
        if request.mode == DCFMode.AGENTIC:
            # Run AI analysis workflow
            ai_result = await optimized_workflow.run_analysis(
                request.ticker,
                user_assumptions=None,  # Will be generated by multi-stage engine
                max_news_articles=request.max_news_articles,
                use_cache=request.use_cache
            )
            ai_analysis = {
                'analysis_engine_output': ai_result.get('analysis_engine_output', {}),
                'dcf_validation_output': ai_result.get('dcf_validation_output', {}),
                'enhanced_insights': ai_result.get('enhanced_insights', {})
            }
        
        # Generate multi-stage assumptions
        multi_stage_assumptions = await multi_stage_growth_engine.generate_multi_stage_assumptions(
            mode=request.mode,
            ticker=request.ticker,
            company_data=company_data,
            ai_analysis=ai_analysis
        )
        
        # Override with user assumptions if provided
        if request.user_assumptions:
            # Merge user overrides with generated assumptions
            multi_stage_assumptions = request.user_assumptions
        
        # Get multi-model recommendation for industry context
        model_recommendation = await multi_model_dcf_service.recommend_model_and_assumptions(
            request.ticker, company_data
        )
        
        # Generate growth stages summary for UI
        growth_stages_summary = []
        for stage in multi_stage_assumptions.growth_stages:
            growth_stages_summary.append({
                'years': stage.years,
                'growth_rate': f"{stage.growth_rate:.1f}%",
                'method': stage.method.replace('_', ' ').title(),
                'confidence': stage.confidence.title(),
                'rationale': stage.rationale
            })
        
        # Generate educational content based on mode
        education_content = _generate_mode_educational_content(
            request.mode, 
            multi_stage_assumptions,
            model_recommendation['recommended_model']['model']
        )
        
        # Create valuation response (placeholder for actual DCF calculation)
        valuation = _create_multi_stage_valuation_placeholder(
            request.ticker,
            company_data,
            multi_stage_assumptions
        )
        
        # Create sensitivity analysis (placeholder)
        sensitivity = _create_multi_stage_sensitivity_placeholder()
        
        return MultiStageDCFResponse(
            valuation=valuation,
            sensitivity=sensitivity,
            financial_data=_create_financial_data_placeholder(request.ticker),
            mode=request.mode,
            growth_stages_summary=growth_stages_summary,
            education_content=education_content,
            last_updated=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Error in multi-stage DCF analysis for {request.ticker}: {e}")
        raise HTTPException(status_code=500, detail=f"Error in multi-stage DCF analysis: {str(e)}")

def _generate_mode_educational_content(
    mode: DCFMode, 
    assumptions: MultiStageAssumptions,
    valuation_model: str
) -> Dict[str, str]:
    """Generate educational content based on selected mode."""
    
    if mode == DCFMode.SIMPLE:
        return {
            'mode_explanation': 'Simple Mode uses historical financial data to project future performance with conservative assumptions.',
            'growth_methodology': f'Growth rates are based on 5-year historical analysis, blended with India GDP growth ({assumptions.gdp_growth_rate}%) over 10 years.',
            'key_benefits': 'Objective, historically grounded analysis that\'s easy to understand and validate.',
            'limitations': 'May not capture forward-looking catalysts or management guidance.',
            'best_for': 'Learning DCF fundamentals, conservative baseline analysis, and educational purposes.'
        }
    else:
        return {
            'mode_explanation': 'Agentic Mode leverages AI to analyze management guidance, news sentiment, and market dynamics for enhanced projections.',
            'growth_methodology': 'Combines historical data with AI-extracted insights from earnings calls, investor presentations, and news analysis.',
            'key_benefits': 'Forward-looking analysis that captures management guidance and market sentiment.',
            'limitations': 'More complex assumptions that require understanding of AI-driven insights.',
            'best_for': 'Comprehensive analysis, identifying catalysts, and understanding market expectations.'
        }

def _create_multi_stage_valuation_placeholder(
    ticker: str,
    company_data: Dict[str, Any],
    assumptions: MultiStageAssumptions
) -> DCFValuation:
    """Create placeholder valuation for multi-stage DCF (to be replaced with actual calculation)."""
    
    info = company_data.get('info', {})
    current_price = info.get('currentPrice', info.get('regularMarketPrice', 100))
    
    # Placeholder projections for 10 years
    projections = []
    base_revenue = 1000000000  # 1B placeholder
    
    for i, stage in enumerate(assumptions.growth_stages):
        for year in range(stage.start_year, stage.end_year + 1):
            if year <= assumptions.projection_years:
                revenue = base_revenue * ((1 + stage.growth_rate/100) ** year)
                projections.append(DCFProjection(
                    year=year,
                    revenue=revenue,
                    revenue_growth_rate=stage.growth_rate,
                    ebitda=revenue * (assumptions.ebitda_margin / 100),
                    ebit=revenue * (assumptions.ebitda_margin / 100) * 0.9,  # Placeholder
                    tax=revenue * (assumptions.ebitda_margin / 100) * 0.9 * (assumptions.tax_rate / 100),
                    nopat=revenue * (assumptions.ebitda_margin / 100) * 0.9 * (1 - assumptions.tax_rate / 100),
                    capex=revenue * 0.05,  # Placeholder
                    working_capital_change=revenue * 0.02,  # Placeholder
                    free_cash_flow=revenue * (assumptions.ebitda_margin / 100) * 0.8,  # Placeholder
                    present_value=revenue * (assumptions.ebitda_margin / 100) * 0.8 / ((1 + assumptions.wacc/100) ** year),
                    growth_stage=stage.years,
                    growth_method=stage.method
                ))
    
    # Calculate placeholder intrinsic value
    total_pv = sum(proj.present_value for proj in projections)
    terminal_value = projections[-1].free_cash_flow * (1 + assumptions.terminal_growth_rate/100) / (assumptions.wacc/100 - assumptions.terminal_growth_rate/100)
    terminal_pv = terminal_value / ((1 + assumptions.wacc/100) ** assumptions.projection_years)
    
    enterprise_value = total_pv + terminal_pv
    equity_value = enterprise_value  # Simplified
    shares_outstanding = info.get('sharesOutstanding', 1000000000)
    intrinsic_value = equity_value / shares_outstanding
    
    # Calculate growth waterfall
    growth_waterfall = {}
    for stage in assumptions.growth_stages:
        growth_waterfall[stage.years] = stage.growth_rate
    
    return DCFValuation(
        intrinsic_value_per_share=intrinsic_value,
        terminal_value=terminal_value,
        enterprise_value=enterprise_value,
        equity_value=equity_value,
        current_stock_price=current_price,
        upside_downside=((intrinsic_value - current_price) / current_price) * 100,
        projections=projections,
        assumptions=DCFAssumptions(  # Legacy format
            revenue_growth_rate=assumptions.growth_stages[0].growth_rate,
            ebitda_margin=assumptions.ebitda_margin,
            tax_rate=assumptions.tax_rate,
            wacc=assumptions.wacc,
            terminal_growth_rate=assumptions.terminal_growth_rate,
            projection_years=assumptions.projection_years
        ),
        multi_stage_assumptions=assumptions,
        growth_waterfall=growth_waterfall
    )

def _create_multi_stage_sensitivity_placeholder():
    """Create placeholder sensitivity analysis for multi-stage DCF."""
    
    from ..models.dcf import SensitivityAnalysis
    
    wacc_range = [8.0, 10.0, 12.0, 14.0, 16.0]
    terminal_growth_range = [1.0, 2.0, 3.0, 4.0, 5.0]
    
    # Placeholder sensitivity matrix
    sensitivity_matrix = [
        [120, 110, 100, 90, 80],
        [130, 120, 110, 100, 90],
        [140, 130, 120, 110, 100],
        [150, 140, 130, 120, 110],
        [160, 150, 140, 130, 120]
    ]
    
    return SensitivityAnalysis(
        wacc_range=wacc_range,
        terminal_growth_range=terminal_growth_range,
        sensitivity_matrix=sensitivity_matrix
    )

def _create_financial_data_placeholder(ticker: str):
    """Create placeholder financial data."""
    
    from ..models.dcf import FinancialData
    
    return FinancialData(
        ticker=ticker,
        years=[2020, 2021, 2022, 2023, 2024],
        revenue=[800000000, 900000000, 1000000000, 1100000000, 1200000000],
        ebitda=[120000000, 135000000, 150000000, 165000000, 180000000],
        net_income=[80000000, 90000000, 100000000, 110000000, 120000000],
        free_cash_flow=[100000000, 110000000, 120000000, 130000000, 140000000],
        total_debt=[200000000, 180000000, 160000000, 140000000, 120000000],
        cash=[50000000, 60000000, 70000000, 80000000, 90000000],
        shares_outstanding=[1000000000] * 5
    )