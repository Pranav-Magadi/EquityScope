from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from typing import Optional, Dict, Any
import json
import asyncio
import logging
from datetime import datetime
from ..services.agentic_workflow import agentic_workflow
from ..services.claude_service import claude_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/agentic", tags=["agentic-analysis"])

# Store for ongoing analyses (in production, use Redis or database)
ongoing_analyses: Dict[str, Dict[str, Any]] = {}

@router.post("/analyze/{ticker}")
async def start_agentic_analysis(
    ticker: str,
    background_tasks: BackgroundTasks,
    max_news_articles: int = 10
):
    """
    Start the agentic workflow analysis for a company.
    This runs in the background and can be polled for status.
    """
    if not claude_service.is_available():
        raise HTTPException(
            status_code=503,
            detail="AI analysis service not available. Please check Claude API configuration."
        )
    
    # Check if analysis is already running
    if ticker in ongoing_analyses:
        return {
            "message": "Analysis already in progress",
            "ticker": ticker,
            "status": "running",
            "analysis_id": ongoing_analyses[ticker]["analysis_id"]
        }
    
    # Initialize analysis tracking
    analysis_id = f"{ticker}_{int(datetime.now().timestamp())}"
    ongoing_analyses[ticker] = {
        "analysis_id": analysis_id,
        "status": "starting",
        "progress": 0,
        "current_step": "initialization",
        "message": "Starting agentic workflow...",
        "started_at": datetime.now().isoformat(),
        "result": None,
        "error": None
    }
    
    # Start analysis in background
    background_tasks.add_task(
        _run_agentic_analysis,
        ticker,
        analysis_id,
        max_news_articles
    )
    
    return {
        "message": "Agentic analysis started",
        "ticker": ticker,
        "analysis_id": analysis_id,
        "status": "starting",
        "estimated_duration_seconds": 60
    }

@router.get("/status/{ticker}")
async def get_analysis_status(ticker: str):
    """Get the status of an ongoing agentic analysis."""
    if ticker not in ongoing_analyses:
        raise HTTPException(
            status_code=404,
            detail=f"No analysis found for ticker {ticker}"
        )
    
    analysis = ongoing_analyses[ticker]
    
    # Clean up completed analyses after returning result
    status = analysis["status"]
    if status in ["completed", "failed"] and analysis.get("result_returned", False):
        del ongoing_analyses[ticker]
    
    return analysis

@router.get("/result/{ticker}")
async def get_analysis_result(ticker: str):
    """Get the final result of a completed agentic analysis."""
    if ticker not in ongoing_analyses:
        raise HTTPException(
            status_code=404,
            detail=f"No analysis found for ticker {ticker}"
        )
    
    analysis = ongoing_analyses[ticker]
    
    if analysis["status"] == "running":
        raise HTTPException(
            status_code=202,
            detail="Analysis still in progress. Check status endpoint."
        )
    
    if analysis["status"] == "failed":
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {analysis.get('error', 'Unknown error')}"
        )
    
    if analysis["status"] == "completed":
        # Mark as returned so it can be cleaned up
        analysis["result_returned"] = True
        return analysis["result"]
    
    raise HTTPException(
        status_code=400,
        detail=f"Analysis in unexpected state: {analysis['status']}"
    )

@router.get("/stream/{ticker}")
async def stream_analysis_progress(ticker: str):
    """Stream real-time progress updates for an analysis."""
    
    async def generate_progress_stream():
        """Generate server-sent events for progress updates."""
        while ticker in ongoing_analyses:
            analysis = ongoing_analyses[ticker]
            
            # Send current status
            yield f"data: {json.dumps(analysis)}\n\n"
            
            # Break if completed or failed
            if analysis["status"] in ["completed", "failed"]:
                break
            
            # Wait before next update
            await asyncio.sleep(2)
        
        # Send final completion message
        yield f"data: {json.dumps({'status': 'stream_ended'})}\n\n"
    
    if ticker not in ongoing_analyses:
        raise HTTPException(
            status_code=404,
            detail=f"No analysis found for ticker {ticker}"
        )
    
    return StreamingResponse(
        generate_progress_stream(),
        media_type="text/plain",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
    )

@router.delete("/cancel/{ticker}")
async def cancel_analysis(ticker: str):
    """Cancel an ongoing analysis."""
    if ticker not in ongoing_analyses:
        raise HTTPException(
            status_code=404,
            detail=f"No analysis found for ticker {ticker}"
        )
    
    analysis = ongoing_analyses[ticker]
    
    if analysis["status"] == "completed":
        return {"message": "Analysis already completed", "ticker": ticker}
    
    # Mark as cancelled
    analysis["status"] = "cancelled"
    analysis["message"] = "Analysis cancelled by user"
    
    return {"message": "Analysis cancelled", "ticker": ticker}

@router.get("/health")
async def check_agentic_health():
    """Check the health of the agentic analysis system."""
    return {
        "status": "healthy" if claude_service.is_available() else "degraded",
        "claude_available": claude_service.is_available(),
        "ongoing_analyses": len(ongoing_analyses),
        "features": {
            "generator_agent": True,
            "checker_agent": True,
            "commentator_agents": True,
            "news_scraping": True,
            "progress_streaming": True
        }
    }

async def _run_agentic_analysis(ticker: str, analysis_id: str, max_news_articles: int):
    """
    Background task to run the complete agentic analysis.
    Updates the ongoing_analyses dict with progress.
    """
    try:
        # Set up progress callback
        def progress_callback(step: str, progress: int, message: str):
            if ticker in ongoing_analyses:
                ongoing_analyses[ticker].update({
                    "progress": progress,
                    "current_step": step,
                    "message": message,
                    "status": "running"
                })
        
        agentic_workflow.add_progress_callback(progress_callback)
        
        # Create cancellation checker
        def is_cancelled():
            return ticker in ongoing_analyses and ongoing_analyses[ticker]["status"] == "cancelled"
        
        # Run the analysis
        result = await agentic_workflow.execute_full_analysis(
            ticker=ticker,
            max_news_articles=max_news_articles,
            cancellation_checker=is_cancelled
        )
        
        if result:
            # Analysis completed successfully
            ongoing_analyses[ticker].update({
                "status": "completed",
                "progress": 100,
                "current_step": "complete",
                "message": "Analysis completed successfully",
                "completed_at": datetime.now().isoformat(),
                "result": result
            })
        else:
            # Analysis failed
            ongoing_analyses[ticker].update({
                "status": "failed",
                "progress": 0,
                "current_step": "error",
                "message": "Analysis failed - no result generated",
                "error": "Analysis returned no result",
                "failed_at": datetime.now().isoformat()
            })
    
    except asyncio.CancelledError:
        logger.info(f"Agentic analysis cancelled for {ticker}")
        # Status should already be set to "cancelled" by the cancel endpoint
        
    except Exception as e:
        logger.error(f"Error in background agentic analysis for {ticker}: {e}")
        
        # Update with error status
        if ticker in ongoing_analyses:
            ongoing_analyses[ticker].update({
                "status": "failed",
                "progress": 0,
                "current_step": "error",
                "message": f"Analysis failed: {str(e)}",
                "error": str(e),
                "failed_at": datetime.now().isoformat()
            })

@router.get("/examples")
async def get_analysis_examples():
    """Get example analysis results for demonstration."""
    return {
        "supported_tickers": {
            "indian_companies": [
                "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", 
                "INFY.NS", "HINDUNILVR.NS", "ITC.NS", "SBIN.NS"
            ],
            "global_companies": [
                "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META"
            ]
        },
        "analysis_sections": {
            "section_1": "Qualitative Narrative (Header, SWOT, News Sentiment)",
            "section_2": "Interactive Quantitative Valuation (DCF, Sensitivity)",
            "section_3": "AI Investment Committee (Validation, Bull/Bear Cases)"
        },
        "typical_duration": "45-90 seconds",
        "news_sources": "Financial news sites, company filings, analyst reports"
    }