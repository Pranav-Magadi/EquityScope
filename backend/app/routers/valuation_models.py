# Valuation Models API Endpoints
# Provides multiple valuation approaches for comprehensive analysis

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, List, Optional
import logging
from datetime import datetime

from ..services.sector_dcf_service import SectorDCFService
from ..services.generic_dcf_service import GenericDCFService
from ..services.multiples_valuation_service import MultiplesValuationService
from ..models.valuation_models import (
    ValuationModelResponse,
    ValuationComparison,
    ModelAssumptions,
    ValuationSummary
)

router = APIRouter(prefix="/api/valuation", tags=["valuation_models"])
logger = logging.getLogger(__name__)

# Initialize services
sector_dcf_service = SectorDCFService()
generic_dcf_service = GenericDCFService()
multiples_service = MultiplesValuationService()

@router.get("/{ticker}/models", response_model=List[str])
async def get_available_models(ticker: str):
    """Get list of available valuation models for a ticker"""
    try:
        # Classify sector to determine available models
        sector = sector_dcf_service.classify_sector(ticker)
        
        available_models = [
            "sector_dcf",      # Sector-specific DCF
            "generic_dcf",     # Standard DCF
            "pe_valuation",    # P/E multiple based
            "ev_ebitda"        # EV/EBITDA multiple based
        ]
        
        # Add sector-specific models
        if sector == "BFSI":
            available_models.append("banking_roe")
        elif sector == "PHARMA":
            available_models.append("pharma_pipeline")
        elif sector == "REALESTATE":
            available_models.append("nav_based")
            
        return available_models
        
    except Exception as e:
        logger.error(f"Error getting available models for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{ticker}/sector-dcf", response_model=ValuationModelResponse)
async def calculate_sector_dcf(
    ticker: str,
    mode: str = Query("simple", enum=["simple", "agentic"]),
    force_refresh: bool = Query(False)
):
    """Calculate sector-specific DCF valuation"""
    try:
        logger.info(f"Calculating sector DCF for {ticker} in {mode} mode")
        
        # Get sector classification
        sector = sector_dcf_service.classify_sector(ticker)
        
        # Calculate sector DCF
        result = await sector_dcf_service.calculate_sector_dcf(
            ticker=ticker,
            sector=sector,
            mode=mode,
            force_refresh=force_refresh
        )
        
        # Format response
        return ValuationModelResponse(
            model_id="sector_dcf",
            model_name=f"{sector} DCF Model",
            ticker=ticker,
            fair_value=result.fair_value,
            current_price=result.current_price,
            upside_downside_pct=result.upside_downside_pct,
            confidence=result.confidence,
            method=result.dcf_method,
            assumptions=ModelAssumptions(
                growth_assumptions=result.sector_rules.get("growth", {}),
                risk_assumptions=result.sector_rules.get("risk", {}),
                terminal_assumptions=result.sector_rules.get("terminal", {}),
                sector_specific=result.sector_rules.get("sector", {})
            ),
            key_factors=result.sector_rules.get("reasoning", []),
            calculation_timestamp=result.calculation_timestamp,
            data_sources=["financial_data", "sector_benchmarks"],
            limitations=[
                f"Model optimized for {sector} sector characteristics",
                "Requires sector-specific metrics for optimal accuracy"
            ]
        )
        
    except Exception as e:
        logger.error(f"Error calculating sector DCF for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{ticker}/generic-dcf", response_model=ValuationModelResponse)
async def calculate_generic_dcf(
    ticker: str,
    forecast_years: int = Query(10, ge=5, le=15),
    force_refresh: bool = Query(False)
):
    """Calculate generic DCF valuation"""
    try:
        logger.info(f"Calculating generic DCF for {ticker}")
        
        result = await generic_dcf_service.calculate_dcf(
            ticker=ticker,
            forecast_years=forecast_years,
            force_refresh=force_refresh
        )
        
        return ValuationModelResponse(
            model_id="generic_dcf",
            model_name="Generic DCF Model",
            ticker=ticker,
            fair_value=result.fair_value,
            current_price=result.current_price,
            upside_downside_pct=result.upside_downside_pct,
            confidence=result.confidence,
            method="Discounted_Cash_Flow",
            assumptions=ModelAssumptions(
                growth_assumptions={
                    "revenue_growth_y1_3": "8-12%",
                    "revenue_growth_y4_7": "6-10%",
                    "revenue_growth_y8_10": "4-8%"
                },
                risk_assumptions={
                    "wacc": "11-13%",
                    "beta": "1.0-1.2",
                    "risk_free_rate": "6.5%"
                },
                terminal_assumptions={
                    "terminal_growth": "3.0%",
                    "terminal_ebitda_margin": "18-22%"
                },
                sector_specific={}
            ),
            key_factors=result.reasoning,
            calculation_timestamp=datetime.now(),
            data_sources=["financial_statements", "market_data"],
            limitations=[
                "Uses standard assumptions across all sectors",
                "May not capture sector-specific dynamics"
            ]
        )
        
    except Exception as e:
        logger.error(f"Error calculating generic DCF for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{ticker}/pe-valuation", response_model=ValuationModelResponse)
async def calculate_pe_valuation(
    ticker: str,
    force_refresh: bool = Query(False)
):
    """Calculate P/E multiple based valuation"""
    try:
        logger.info(f"Calculating P/E valuation for {ticker}")
        
        result = await multiples_service.calculate_pe_valuation(
            ticker=ticker,
            force_refresh=force_refresh
        )
        
        return ValuationModelResponse(
            model_id="pe_valuation",
            model_name="P/E Multiple Valuation",
            ticker=ticker,
            fair_value=result.fair_value,
            current_price=result.current_price,
            upside_downside_pct=result.upside_downside_pct,
            confidence=result.confidence,
            method="PE_Multiple",
            assumptions=ModelAssumptions(
                growth_assumptions={
                    "earnings_growth": result.assumptions.get("earnings_growth", "10-15%"),
                    "peg_ratio": result.assumptions.get("peg_ratio", "1.0-1.5")
                },
                risk_assumptions={
                    "peer_group_size": str(result.assumptions.get("peer_count", 5)),
                    "market_cycle_adjustment": result.assumptions.get("cycle_adjustment", "Neutral")
                },
                terminal_assumptions={},
                sector_specific={
                    "industry_pe": f"{result.assumptions.get('industry_pe', 16)}x",
                    "quality_premium": result.assumptions.get("quality_premium", "5-10%")
                }
            ),
            key_factors=result.reasoning,
            calculation_timestamp=datetime.now(),
            data_sources=["peer_multiples", "earnings_estimates"],
            limitations=[
                "Dependent on peer group selection quality",
                "May not reflect company-specific growth prospects"
            ]
        )
        
    except Exception as e:
        logger.error(f"Error calculating P/E valuation for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{ticker}/ev-ebitda", response_model=ValuationModelResponse)
async def calculate_ev_ebitda_valuation(
    ticker: str,
    force_refresh: bool = Query(False)
):
    """Calculate EV/EBITDA multiple based valuation"""
    try:
        logger.info(f"Calculating EV/EBITDA valuation for {ticker}")
        
        result = await multiples_service.calculate_ev_ebitda_valuation(
            ticker=ticker,
            force_refresh=force_refresh
        )
        
        return ValuationModelResponse(
            model_id="ev_ebitda",
            model_name="EV/EBITDA Multiple Valuation", 
            ticker=ticker,
            fair_value=result.fair_value,
            current_price=result.current_price,
            upside_downside_pct=result.upside_downside_pct,
            confidence=result.confidence,
            method="EV_EBITDA_Multiple",
            assumptions=ModelAssumptions(
                growth_assumptions={
                    "ebitda_growth": result.assumptions.get("ebitda_growth", "10-15%"),
                    "margin_expansion": result.assumptions.get("margin_expansion", "50-100bps")
                },
                risk_assumptions={
                    "peer_group_size": str(result.assumptions.get("peer_count", 5)),
                    "debt_adjustment": result.assumptions.get("debt_adjustment", "Net Cash")
                },
                terminal_assumptions={},
                sector_specific={
                    "industry_ev_ebitda": f"{result.assumptions.get('industry_ev_ebitda', 10)}x",
                    "capital_intensity": result.assumptions.get("capex_intensity", "Low-Medium")
                }
            ),
            key_factors=result.reasoning,
            calculation_timestamp=datetime.now(),
            data_sources=["peer_multiples", "ebitda_projections", "debt_data"],
            limitations=[
                "Does not account for capital intensity differences",
                "Sensitive to EBITDA quality and sustainability"
            ]
        )
        
    except Exception as e:
        logger.error(f"Error calculating EV/EBITDA valuation for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{ticker}/comparison", response_model=ValuationComparison)
async def compare_valuation_models(
    ticker: str,
    models: Optional[List[str]] = Query(None),
    force_refresh: bool = Query(False)
):
    """Compare multiple valuation models for comprehensive analysis"""
    try:
        logger.info(f"Comparing valuation models for {ticker}")
        
        # Get available models if not specified
        if not models:
            models = await get_available_models(ticker)
            models = models[:4]  # Limit to top 4 models
        
        # Calculate all requested models
        model_results = {}
        calculation_errors = []
        
        for model in models:
            try:
                if model == "sector_dcf":
                    result = await calculate_sector_dcf(ticker, force_refresh=force_refresh)
                elif model == "generic_dcf":
                    result = await calculate_generic_dcf(ticker, force_refresh=force_refresh)
                elif model == "pe_valuation":
                    result = await calculate_pe_valuation(ticker, force_refresh=force_refresh)
                elif model == "ev_ebitda":
                    result = await calculate_ev_ebitda_valuation(ticker, force_refresh=force_refresh)
                else:
                    continue
                    
                model_results[model] = result
                
            except Exception as e:
                logger.warning(f"Failed to calculate {model} for {ticker}: {str(e)}")
                calculation_errors.append(f"{model}: {str(e)}")
        
        if not model_results:
            raise HTTPException(status_code=500, detail="No valuation models could be calculated")
        
        # Calculate summary statistics
        fair_values = [r.fair_value for r in model_results.values()]
        upsides = [r.upside_downside_pct for r in model_results.values()]
        confidences = [r.confidence for r in model_results.values()]
        
        summary = ValuationSummary(
            ticker=ticker,
            current_price=list(model_results.values())[0].current_price,
            fair_value_range={
                "min": min(fair_values),
                "max": max(fair_values),
                "mean": sum(fair_values) / len(fair_values),
                "median": sorted(fair_values)[len(fair_values) // 2]
            },
            upside_range={
                "min": min(upsides),
                "max": max(upsides),
                "mean": sum(upsides) / len(upsides)
            },
            consensus_confidence=sum(confidences) / len(confidences),
            model_agreement=calculate_model_agreement(fair_values),
            calculation_timestamp=datetime.now()
        )
        
        return ValuationComparison(
            ticker=ticker,
            models=model_results,
            summary=summary,
            warnings=calculation_errors,
            recommendation=generate_valuation_recommendation(model_results, summary)
        )
        
    except Exception as e:
        logger.error(f"Error comparing valuation models for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def calculate_model_agreement(fair_values: List[float]) -> float:
    """Calculate agreement between models (lower std dev = higher agreement)"""
    if len(fair_values) < 2:
        return 1.0
    
    mean_val = sum(fair_values) / len(fair_values)
    variance = sum((x - mean_val) ** 2 for x in fair_values) / len(fair_values)
    std_dev = variance ** 0.5
    coefficient_of_variation = std_dev / mean_val if mean_val > 0 else 1.0
    
    # Convert to agreement score (0-1, where 1 is perfect agreement)
    return max(0, 1 - coefficient_of_variation)

def generate_valuation_recommendation(
    model_results: Dict[str, ValuationModelResponse],
    summary: ValuationSummary
) -> str:
    """Generate investment recommendation based on model consensus"""
    mean_upside = summary.upside_range["mean"]
    agreement = summary.model_agreement
    confidence = summary.consensus_confidence
    
    if mean_upside > 20 and agreement > 0.7 and confidence > 0.75:
        return "Strong Buy - High consensus with significant upside"
    elif mean_upside > 10 and agreement > 0.6 and confidence > 0.65:
        return "Buy - Positive consensus with moderate upside"
    elif mean_upside > -10 and mean_upside < 10:
        return "Hold - Mixed signals, fair value near current price"
    elif mean_upside < -10 and agreement > 0.6:
        return "Sell - Consensus indicates overvaluation"
    else:
        return "Inconclusive - Models show significant disagreement"