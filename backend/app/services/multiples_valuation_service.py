# Multiples Valuation Service
# P/E, EV/EBITDA, and other multiple-based valuation models

import logging
import asyncio
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import statistics

from ..models.valuation_models import MultiplesResult
from .intelligent_cache import intelligent_cache, CacheType

logger = logging.getLogger(__name__)

@dataclass
class CompanyMetrics:
    """Company financial metrics for multiples calculation"""
    ticker: str
    current_price: float
    market_cap: float
    enterprise_value: float
    
    # P&L Metrics
    revenue_ttm: float
    ebitda_ttm: float
    ebit_ttm: float
    net_income_ttm: float
    earnings_per_share: float
    
    # Growth Metrics
    revenue_growth_3y: float
    earnings_growth_3y: float
    
    # Quality Metrics
    roe: float
    roic: float
    debt_to_equity: float

class MultiplesValuationService:
    """
    Multiple-based valuation service
    
    Provides P/E, EV/EBITDA, PEG and other relative valuation methods
    using peer group analysis and industry benchmarks
    """
    
    def __init__(self, use_cache: bool = True):
        self.use_cache = use_cache
        self.cache_manager = intelligent_cache
        
        # Sector peer mappings (subset for major companies)
        self.sector_peers = {
            "BFSI": {
                "HDFCBANK": ["ICICIBANK", "AXISBANK", "KOTAKBANK", "SBIN"],
                "ICICIBANK": ["HDFCBANK", "AXISBANK", "KOTAKBANK", "SBIN"],
                "AXISBANK": ["HDFCBANK", "ICICIBANK", "KOTAKBANK", "INDUSINDBK"],
                "KOTAKBANK": ["HDFCBANK", "ICICIBANK", "AXISBANK", "INDUSINDBK"],
                "SBIN": ["HDFCBANK", "ICICIBANK", "BANKBARODA", "PNB"]
            },
            "IT": {
                "TCS": ["INFY", "WIPRO", "HCLTECH", "TECHM"],
                "INFY": ["TCS", "WIPRO", "HCLTECH", "TECHM"],
                "WIPRO": ["TCS", "INFY", "HCLTECH", "LTI"],
                "HCLTECH": ["TCS", "INFY", "WIPRO", "TECHM"],
                "TECHM": ["TCS", "INFY", "WIPRO", "HCLTECH"]
            },
            "PHARMA": {
                "SUNPHARMA": ["DRREDDY", "CIPLA", "LUPIN", "DIVISLAB"],
                "DRREDDY": ["SUNPHARMA", "CIPLA", "LUPIN", "DIVISLAB"],
                "CIPLA": ["SUNPHARMA", "DRREDDY", "LUPIN", "AUROPHARMA"],
                "LUPIN": ["SUNPHARMA", "DRREDDY", "CIPLA", "AUROPHARMA"]
            },
            "FMCG": {
                "HINDUNILVR": ["ITC", "NESTLEIND", "BRITANNIA", "DABUR"],
                "ITC": ["HINDUNILVR", "GODREJCP", "MARICO", "DABUR"],
                "NESTLEIND": ["HINDUNILVR", "BRITANNIA", "MARICO", "TATACONSUM"]
            }
        }
        
        # Industry benchmark multiples
        self.industry_benchmarks = {
            "BFSI": {"pe": 12.0, "pb": 1.5, "ev_ebitda": 8.0},
            "IT": {"pe": 22.0, "pb": 4.0, "ev_ebitda": 14.0},
            "PHARMA": {"pe": 18.0, "pb": 2.5, "ev_ebitda": 12.0},
            "FMCG": {"pe": 35.0, "pb": 6.0, "ev_ebitda": 18.0},
            "REALESTATE": {"pe": 8.0, "pb": 0.8, "ev_ebitda": 6.0},
            "ENERGY": {"pe": 10.0, "pb": 1.0, "ev_ebitda": 8.0}
        }

    async def calculate_pe_valuation(
        self,
        ticker: str,
        force_refresh: bool = False
    ) -> MultiplesResult:
        """Calculate P/E multiple based valuation"""
        try:
            logger.info(f"Calculating P/E valuation for {ticker}")
            
            # Check cache
            if self.use_cache and not force_refresh:
                cache_key = f"{ticker}_pe_valuation"
                cached_result = await self.cache_manager.get(
                    cache_key, CacheType.FINANCIAL_DATA
                )
                if cached_result:
                    logger.info(f"Cache hit for {ticker} P/E valuation")
                    return MultiplesResult(**cached_result)
            
            # Get company metrics
            company_metrics = await self._get_company_metrics(ticker)
            
            # Get peer group P/E multiples
            peer_multiples = await self._get_peer_pe_multiples(ticker)
            
            # Calculate target P/E
            target_pe = self._calculate_target_pe(
                company_metrics, peer_multiples
            )
            
            # Calculate fair value
            fair_value = company_metrics.earnings_per_share * target_pe
            
            # Calculate upside/downside
            upside_downside_pct = (
                (fair_value - company_metrics.current_price) / company_metrics.current_price
            ) * 100
            
            # Assess confidence
            confidence = self._assess_pe_confidence(
                company_metrics, peer_multiples, target_pe
            )
            
            # Generate reasoning
            reasoning = self._generate_pe_reasoning(
                company_metrics, target_pe, peer_multiples
            )
            
            result = MultiplesResult(
                ticker=ticker,
                fair_value=fair_value,
                current_price=company_metrics.current_price,
                upside_downside_pct=upside_downside_pct,
                confidence=confidence,
                method="PE_Multiple",
                applied_multiple=target_pe,
                peer_multiples=peer_multiples,
                industry_median=statistics.median(peer_multiples.values()) if peer_multiples else target_pe,
                quality_premium_discount=self._calculate_quality_premium(company_metrics),
                reasoning=reasoning,
                assumptions={
                    "target_pe": f"{target_pe:.1f}x",
                    "current_pe": f"{company_metrics.current_price / company_metrics.earnings_per_share:.1f}x",
                    "peer_count": len(peer_multiples),
                    "earnings_growth": f"{company_metrics.earnings_growth_3y:.1%}",
                    "quality_premium": f"{self._calculate_quality_premium(company_metrics):.1%}"
                }
            )
            
            # Cache result
            if self.use_cache:
                cache_key = f"{ticker}_pe_valuation"
                await self.cache_manager.set(
                    cache_key, result.dict(), CacheType.FINANCIAL_DATA
                )
            
            return result
            
        except Exception as e:
            logger.error(f"Error calculating P/E valuation for {ticker}: {str(e)}")
            raise

    async def calculate_ev_ebitda_valuation(
        self,
        ticker: str,
        force_refresh: bool = False
    ) -> MultiplesResult:
        """Calculate EV/EBITDA multiple based valuation"""
        try:
            logger.info(f"Calculating EV/EBITDA valuation for {ticker}")
            
            # Check cache
            if self.use_cache and not force_refresh:
                cache_key = f"{ticker}_ev_ebitda_valuation"
                cached_result = await self.cache_manager.get(
                    cache_key, CacheType.FINANCIAL_DATA
                )
                if cached_result:
                    logger.info(f"Cache hit for {ticker} EV/EBITDA valuation")
                    return MultiplesResult(**cached_result)
            
            # Get company metrics
            company_metrics = await self._get_company_metrics(ticker)
            
            # Get peer group EV/EBITDA multiples
            peer_multiples = await self._get_peer_ev_ebitda_multiples(ticker)
            
            # Calculate target EV/EBITDA
            target_ev_ebitda = self._calculate_target_ev_ebitda(
                company_metrics, peer_multiples
            )
            
            # Calculate enterprise value and equity value
            target_enterprise_value = company_metrics.ebitda_ttm * target_ev_ebitda
            net_debt = self._estimate_net_debt(company_metrics)
            equity_value = target_enterprise_value - net_debt
            shares_outstanding = company_metrics.market_cap / company_metrics.current_price
            fair_value = equity_value / shares_outstanding
            
            # Calculate upside/downside
            upside_downside_pct = (
                (fair_value - company_metrics.current_price) / company_metrics.current_price
            ) * 100
            
            # Assess confidence
            confidence = self._assess_ev_ebitda_confidence(
                company_metrics, peer_multiples, target_ev_ebitda
            )
            
            # Generate reasoning
            reasoning = self._generate_ev_ebitda_reasoning(
                company_metrics, target_ev_ebitda, peer_multiples
            )
            
            result = MultiplesResult(
                ticker=ticker,
                fair_value=fair_value,
                current_price=company_metrics.current_price,
                upside_downside_pct=upside_downside_pct,
                confidence=confidence,
                method="EV_EBITDA_Multiple",
                applied_multiple=target_ev_ebitda,
                peer_multiples=peer_multiples,
                industry_median=statistics.median(peer_multiples.values()) if peer_multiples else target_ev_ebitda,
                quality_premium_discount=self._calculate_quality_premium(company_metrics),
                reasoning=reasoning,
                assumptions={
                    "target_ev_ebitda": f"{target_ev_ebitda:.1f}x",
                    "current_ev_ebitda": f"{company_metrics.enterprise_value / company_metrics.ebitda_ttm:.1f}x",
                    "peer_count": len(peer_multiples),
                    "ebitda_growth": f"{company_metrics.revenue_growth_3y * 1.2:.1%}",  # Assume margin expansion
                    "net_debt_adjustment": f"₹{net_debt:,.0f}M"
                }
            )
            
            # Cache result
            if self.use_cache:
                cache_key = f"{ticker}_ev_ebitda_valuation"
                await self.cache_manager.set(
                    cache_key, result.dict(), CacheType.FINANCIAL_DATA
                )
            
            return result
            
        except Exception as e:
            logger.error(f"Error calculating EV/EBITDA valuation for {ticker}: {str(e)}")
            raise

    async def _get_company_metrics(self, ticker: str) -> CompanyMetrics:
        """Get company financial metrics"""
        try:
            # In production, this would integrate with financial data services
            # For now, using placeholder implementation
            
            # Remove .NS suffix for mapping
            base_ticker = ticker.replace(".NS", "")
            
            # Placeholder metrics - replace with actual data service integration
            placeholder_metrics = {
                "TCS": CompanyMetrics(
                    ticker=ticker, current_price=3500, market_cap=1300000,
                    enterprise_value=1295000, revenue_ttm=250000, ebitda_ttm=62500,
                    ebit_ttm=60000, net_income_ttm=45000, earnings_per_share=120,
                    revenue_growth_3y=0.08, earnings_growth_3y=0.10,
                    roe=0.45, roic=0.35, debt_to_equity=0.05
                ),
                "HDFCBANK": CompanyMetrics(
                    ticker=ticker, current_price=1600, market_cap=900000,
                    enterprise_value=900000, revenue_ttm=180000, ebitda_ttm=None,  # Banks use different metrics
                    ebit_ttm=None, net_income_ttm=36000, earnings_per_share=65,
                    revenue_growth_3y=0.12, earnings_growth_3y=0.15,
                    roe=0.16, roic=0.12, debt_to_equity=8.0  # High leverage for banks
                )
            }
            
            if base_ticker in placeholder_metrics:
                return placeholder_metrics[base_ticker]
            else:
                # Default placeholder metrics
                return CompanyMetrics(
                    ticker=ticker, current_price=1000, market_cap=100000,
                    enterprise_value=105000, revenue_ttm=50000, ebitda_ttm=10000,
                    ebit_ttm=8000, net_income_ttm=6000, earnings_per_share=60,
                    revenue_growth_3y=0.08, earnings_growth_3y=0.10,
                    roe=0.15, roic=0.12, debt_to_equity=0.5
                )
                
        except Exception as e:
            logger.error(f"Error getting company metrics for {ticker}: {str(e)}")
            raise

    async def _get_peer_pe_multiples(self, ticker: str) -> Dict[str, float]:
        """Get P/E multiples for peer companies"""
        try:
            base_ticker = ticker.replace(".NS", "")
            sector = self._classify_sector(base_ticker)
            
            if sector in self.sector_peers and base_ticker in self.sector_peers[sector]:
                peer_tickers = self.sector_peers[sector][base_ticker]
                
                # In production, fetch actual P/E multiples for peers
                # For now, using sector benchmarks with variations
                benchmark_pe = self.industry_benchmarks[sector]["pe"]
                
                peer_multiples = {}
                for i, peer in enumerate(peer_tickers):
                    # Add realistic variation around benchmark
                    variation = 0.8 + (i * 0.1)  # 0.8 to 1.2 range
                    peer_multiples[peer] = benchmark_pe * variation
                
                return peer_multiples
            else:
                # Fallback to industry benchmark
                benchmark_pe = self.industry_benchmarks.get(sector, {"pe": 16})["pe"]
                return {"Industry_Avg": benchmark_pe}
                
        except Exception as e:
            logger.error(f"Error getting peer P/E multiples: {str(e)}")
            return {"Industry_Avg": 16.0}

    async def _get_peer_ev_ebitda_multiples(self, ticker: str) -> Dict[str, float]:
        """Get EV/EBITDA multiples for peer companies"""
        try:
            base_ticker = ticker.replace(".NS", "")
            sector = self._classify_sector(base_ticker)
            
            if sector in self.sector_peers and base_ticker in self.sector_peers[sector]:
                peer_tickers = self.sector_peers[sector][base_ticker]
                
                benchmark_ev_ebitda = self.industry_benchmarks[sector]["ev_ebitda"]
                
                peer_multiples = {}
                for i, peer in enumerate(peer_tickers):
                    variation = 0.85 + (i * 0.08)  # 0.85 to 1.15 range
                    peer_multiples[peer] = benchmark_ev_ebitda * variation
                
                return peer_multiples
            else:
                benchmark_ev_ebitda = self.industry_benchmarks.get(sector, {"ev_ebitda": 10})["ev_ebitda"]
                return {"Industry_Avg": benchmark_ev_ebitda}
                
        except Exception as e:
            logger.error(f"Error getting peer EV/EBITDA multiples: {str(e)}")
            return {"Industry_Avg": 10.0}

    def _classify_sector(self, ticker: str) -> str:
        """Classify ticker into sector"""
        for sector, companies in self.sector_peers.items():
            if ticker in companies:
                return sector
        
        # Fallback classification based on known patterns
        if ticker in ["RELIANCE", "ONGC", "IOC"]:
            return "ENERGY"
        elif ticker in ["DLF", "GODREJPROP"]:
            return "REALESTATE"
        else:
            return "IT"  # Default fallback

    def _calculate_target_pe(
        self, 
        company_metrics: CompanyMetrics, 
        peer_multiples: Dict[str, float]
    ) -> float:
        """Calculate target P/E multiple"""
        try:
            if not peer_multiples:
                return 16.0  # Default P/E
            
            # Base P/E from peer median
            base_pe = statistics.median(peer_multiples.values())
            
            # Quality adjustments
            quality_premium = self._calculate_quality_premium(company_metrics)
            
            # Growth adjustments (PEG-based)
            if company_metrics.earnings_growth_3y > 0:
                growth_adjustment = min(0.3, company_metrics.earnings_growth_3y - 0.08)  # Cap at 30%
            else:
                growth_adjustment = -0.2  # Penalty for negative growth
            
            # Apply adjustments
            target_pe = base_pe * (1 + quality_premium + growth_adjustment)
            
            # Sanity checks
            return max(5.0, min(50.0, target_pe))
            
        except Exception as e:
            logger.error(f"Error calculating target P/E: {str(e)}")
            return 16.0

    def _calculate_target_ev_ebitda(
        self,
        company_metrics: CompanyMetrics,
        peer_multiples: Dict[str, float]
    ) -> float:
        """Calculate target EV/EBITDA multiple"""
        try:
            if not peer_multiples:
                return 10.0  # Default EV/EBITDA
            
            base_multiple = statistics.median(peer_multiples.values())
            quality_premium = self._calculate_quality_premium(company_metrics)
            
            # Growth adjustment based on revenue growth
            growth_adjustment = min(0.25, company_metrics.revenue_growth_3y - 0.06)
            
            target_multiple = base_multiple * (1 + quality_premium + growth_adjustment)
            return max(3.0, min(25.0, target_multiple))
            
        except Exception as e:
            logger.error(f"Error calculating target EV/EBITDA: {str(e)}")
            return 10.0

    def _calculate_quality_premium(self, company_metrics: CompanyMetrics) -> float:
        """Calculate quality premium/discount based on financial metrics"""
        try:
            premium = 0.0
            
            # ROE premium
            if company_metrics.roe > 0.20:
                premium += 0.15  # High ROE premium
            elif company_metrics.roe > 0.15:
                premium += 0.10  # Good ROE premium
            elif company_metrics.roe < 0.10:
                premium -= 0.10  # Low ROE penalty
            
            # ROIC premium
            if company_metrics.roic > 0.15:
                premium += 0.10
            elif company_metrics.roic < 0.08:
                premium -= 0.10
            
            # Leverage penalty (except for banks)
            if company_metrics.debt_to_equity > 1.0 and company_metrics.debt_to_equity < 5.0:  # Non-bank
                premium -= 0.05
            elif company_metrics.debt_to_equity > 2.0 and company_metrics.debt_to_equity < 5.0:  # High leverage
                premium -= 0.10
            
            return max(-0.3, min(0.3, premium))  # Cap at +/- 30%
            
        except Exception as e:
            logger.error(f"Error calculating quality premium: {str(e)}")
            return 0.0

    def _estimate_net_debt(self, company_metrics: CompanyMetrics) -> float:
        """Estimate net debt from available metrics"""
        # Simplified estimation - in production would use balance sheet data
        return max(0, company_metrics.enterprise_value - company_metrics.market_cap)

    def _assess_pe_confidence(
        self,
        company_metrics: CompanyMetrics,
        peer_multiples: Dict[str, float],
        target_pe: float
    ) -> float:
        """Assess confidence in P/E valuation"""
        try:
            confidence_factors = []
            
            # Peer group quality
            if len(peer_multiples) >= 3:
                confidence_factors.append(0.2)
            
            # Earnings quality
            if company_metrics.earnings_per_share > 0:
                confidence_factors.append(0.2)
            
            # Growth consistency
            if company_metrics.earnings_growth_3y > 0:
                confidence_factors.append(0.15)
            
            # ROE quality
            if company_metrics.roe > 0.12:
                confidence_factors.append(0.15)
            
            # Base confidence
            confidence_factors.append(0.3)
            
            return min(1.0, sum(confidence_factors))
            
        except Exception as e:
            logger.error(f"Error assessing P/E confidence: {str(e)}")
            return 0.6

    def _assess_ev_ebitda_confidence(
        self,
        company_metrics: CompanyMetrics,
        peer_multiples: Dict[str, float],
        target_multiple: float
    ) -> float:
        """Assess confidence in EV/EBITDA valuation"""
        try:
            confidence_factors = []
            
            # EBITDA quality
            if company_metrics.ebitda_ttm and company_metrics.ebitda_ttm > 0:
                confidence_factors.append(0.25)
                
            # Peer group quality
            if len(peer_multiples) >= 3:
                confidence_factors.append(0.2)
            
            # Revenue growth
            if company_metrics.revenue_growth_3y > 0:
                confidence_factors.append(0.15)
            
            # Base confidence
            confidence_factors.append(0.4)
            
            return min(1.0, sum(confidence_factors))
            
        except Exception as e:
            logger.error(f"Error assessing EV/EBITDA confidence: {str(e)}")
            return 0.6

    def _generate_pe_reasoning(
        self,
        company_metrics: CompanyMetrics,
        target_pe: float,
        peer_multiples: Dict[str, float]
    ) -> List[str]:
        """Generate reasoning for P/E valuation"""
        reasoning = []
        
        current_pe = company_metrics.current_price / company_metrics.earnings_per_share if company_metrics.earnings_per_share > 0 else 0
        peer_median = statistics.median(peer_multiples.values()) if peer_multiples else target_pe
        
        reasoning.append(f"Applied {target_pe:.1f}x P/E vs peer median of {peer_median:.1f}x")
        
        if target_pe > peer_median:
            reasoning.append(f"Premium justified by superior financial metrics")
        elif target_pe < peer_median:
            reasoning.append(f"Discount applied due to quality concerns")
        
        if company_metrics.earnings_growth_3y > 0.1:
            reasoning.append(f"Strong {company_metrics.earnings_growth_3y:.1%} earnings growth supports premium")
        
        if company_metrics.roe > 0.15:
            reasoning.append(f"High ROE of {company_metrics.roe:.1%} indicates quality")
        
        return reasoning

    def _generate_ev_ebitda_reasoning(
        self,
        company_metrics: CompanyMetrics,
        target_multiple: float,
        peer_multiples: Dict[str, float]
    ) -> List[str]:
        """Generate reasoning for EV/EBITDA valuation"""
        reasoning = []
        
        peer_median = statistics.median(peer_multiples.values()) if peer_multiples else target_multiple
        reasoning.append(f"Applied {target_multiple:.1f}x EV/EBITDA vs peer median of {peer_median:.1f}x")
        
        if company_metrics.revenue_growth_3y > 0.08:
            reasoning.append(f"Revenue growth of {company_metrics.revenue_growth_3y:.1%} supports multiple")
        
        if company_metrics.roic > 0.12:
            reasoning.append(f"Strong ROIC of {company_metrics.roic:.1%} indicates efficiency")
        
        reasoning.append("Enterprise value approach accounts for capital structure")
        
        return reasoning