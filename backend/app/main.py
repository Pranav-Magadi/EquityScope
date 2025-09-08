from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
from .api.company import router as company_router
from .api.valuation import router as valuation_router
from .api.settings import router as settings_router
from .api.agentic_analysis import router as agentic_router
from .api.demo_analysis import router as demo_router
from .api.technical_analysis import router as technical_router
from .api.multi_stage_dcf import router as multi_stage_dcf_router
from .api.v3_summary import router as v3_summary_router
from .api.v1.financial_analysis import router as financial_analysis_router
from .api.dcf_insights import router as dcf_insights_router
from .api.news_analysis import router as news_analysis_router
from .routers.valuation_models import router as valuation_models_router
# from .api.enhanced_company import router as enhanced_company_router
# from .api.enhanced_valuation import router as enhanced_valuation_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="EquityScope API",
    description="API for comprehensive company analysis and DCF valuation platform - v3 Summary Engine",
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://127.0.0.1:3000",
        "http://localhost:3001", 
        "http://127.0.0.1:3001",
        "http://localhost:3002",
        "http://127.0.0.1:3002"
    ],  # React dev server (multiple ports)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
# V1 APIs (original yfinance-based)
app.include_router(company_router)
app.include_router(valuation_router)
app.include_router(settings_router)
app.include_router(agentic_router)
app.include_router(demo_router)
app.include_router(technical_router)
app.include_router(multi_stage_dcf_router)

# V3 APIs (Summary Engine)
app.include_router(v3_summary_router)

# DCF AI Insights APIs
app.include_router(dcf_insights_router)

# News Analysis APIs
app.include_router(news_analysis_router)

# Financial Analysis APIs (3-Tab Financial Analysis System)
app.include_router(financial_analysis_router, prefix="/api")

# Valuation Models APIs (Multiple Models Comparison)
app.include_router(valuation_models_router)

# V2 APIs (enhanced with Kite Connect) - Disabled for Standard Mode
# app.include_router(enhanced_company_router)
# app.include_router(enhanced_valuation_router)

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to EquityScope API v2.0 - Optimized",
        "version": "2.0.0",
        "description": "Comprehensive company analysis and DCF valuation platform with Kite Connect integration",
        "features": {
            "real_time_data": "Live market data via Kite Connect",
            "enhanced_dcf": "DCF valuation with real-time price updates",
            "intraday_charts": "Minute-level price data",
            "market_depth": "Order book analysis",
            "portfolio_tracking": "Holdings analysis (with auth)"
        },
        "endpoints": {
            "docs": "/docs",
            "v1_company_analysis": "/api/company/{ticker}",
            "v2_enhanced_analysis": "/api/v2/company/{ticker}",
            "v1_dcf_valuation": "/api/valuation/dcf",
            "v2_enhanced_dcf": "/api/v2/valuation/dcf",
            "v3_summary_simple": "/api/v3/summary/{ticker}/simple",
            "v3_summary_agentic": "/api/v3/summary/{ticker}/agentic",
            "v3_peer_analysis": "/api/v3/peers/{ticker}",
            "real_time_quotes": "/api/v2/company/{ticker}/price",
            "intraday_data": "/api/v2/company/{ticker}/intraday",
            "market_depth": "/api/v2/company/{ticker}/market-depth",
            "symbol_search": "/api/v2/company/search/{query}",
            "market_status": "/api/v2/company/market/status"
        },
        "data_sources": {
            "primary": "Kite Connect (real-time Indian market data)",
            "fallback": "yfinance (global market data)",
            "qualitative": "AI-powered analysis with placeholder functions"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "equityscope-api", "version": "2.0.0"}

@app.get("/api/data-sources")
async def get_data_sources_info():
    """Get information about available data sources"""
    return {
        "kite_connect": {
            "description": "Real-time Indian market data via Zerodha Kite Connect",
            "features": [
                "Live quotes and market depth",
                "Intraday historical data",
                "Market status and trading hours",
                "Portfolio holdings (with authentication)"
            ],
            "endpoints": "/api/v2/*",
            "authentication_required": True,
            "setup_instructions": "Use /api/v2/company/kite/login-url to get authentication URL"
        },
        "yfinance": {
            "description": "Global market data via Yahoo Finance",
            "features": [
                "Historical price data",
                "Financial statements",
                "Company fundamentals",
                "Global market coverage"
            ],
            "endpoints": "/api/*",
            "authentication_required": False,
            "limitations": "Delayed data, limited to daily granularity"
        },
        "ai_analysis": {
            "description": "AI-powered qualitative analysis",
            "features": [
                "SWOT analysis",
                "News sentiment analysis",
                "Market landscape assessment",
                "Employee sentiment analysis"
            ],
            "note": "Currently uses placeholder functions - integrate with AI services in production"
        }
    }

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "status_code": exc.status_code,
            "api_version": "2.0.0"
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "Internal server error",
            "status_code": 500,
            "api_version": "2.0.0"
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)