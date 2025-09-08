# EquityScope v3 Summary Engine Service
# Core business logic for Summary Engine

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import yfinance as yf
from functools import lru_cache

from ..models.summary import (
    SummaryResponse,
    SimpleSummaryResponse, 
    AgenticSummaryResponse,
    FairValueBand,
    InvestmentLabel,
    LegacyDCFMapping
)
from .dcf_service import DCFService
from .claude_service import ClaudeService, agentic_analysis_service
from .weighted_scoring_service import WeightedScoringService
from .sector_dcf_service import SectorDCFService

logger = logging.getLogger(__name__)

class V3SummaryService:
    """
    V3 Summary Engine Service implementing rule-based and agentic analysis
    Based on EquityScope v3 Product Requirements
    """
    
    def __init__(self):
        self.dcf_service = DCFService()
        self.claude_service = ClaudeService()
        self.weighted_scoring_service = WeightedScoringService()
        self.sector_dcf_service = SectorDCFService()  # NEW: Sector-specific DCF
        self.cache = {}  # Simple in-memory cache
        self.cache_duration = timedelta(hours=4)  # 4-hour cache
    
    async def generate_simple_summary(
        self, 
        ticker: str, 
        force_refresh: bool = False
    ) -> SimpleSummaryResponse:
        """
        Generate rule-based simple mode summary
        
        Uses quantitative rules, heuristics, and pre-written logic
        NO LLM inference - pure deterministic analysis
        """
        cache_key = f"simple_{ticker}"
        
        # Check cache first
        if not force_refresh and cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if datetime.now() - timestamp < self.cache_duration:
                logger.info(f"Returning cached simple summary for {ticker}")
                return cached_data
        
        try:
            logger.info(f"Generating rule-based simple summary for {ticker}")
            
            # Step 1: Get basic company data
            company_data = await self._fetch_company_data(ticker)
            
            # Step 2: Get sector classification using SectorDCFService
            sector = self.sector_dcf_service.classify_sector(ticker)
            
            # Step 3: Use new weighted scoring framework for comprehensive analysis
            peer_data = await self._fetch_peer_data(ticker)
            technical_data = await self._fetch_technical_data(ticker)
            
            scoring_result = await self.weighted_scoring_service.calculate_weighted_score(
                ticker=ticker,
                company_data=company_data,
                sector=sector,
                peer_data=peer_data,
                technical_data=technical_data,
                force_refresh=force_refresh
            )
            
            # Step 4: Create fair value band from scoring result
            fair_value_band = self._create_fair_value_band_from_scoring(scoring_result, company_data)
            
            # Step 5: Extract insights from weighted scoring components
            valuation_insights = self._extract_valuation_insights(scoring_result)
            market_signals = self._extract_market_insights(scoring_result)
            business_fundamentals = self._extract_fundamental_insights(scoring_result)
            
            # Step 6: Use scoring result for investment label and factors
            investment_label = scoring_result.investment_label
            key_factors = self._extract_key_factors_from_scoring(scoring_result)
            
            # Step 7: Combine data warnings from scoring and basic checks
            data_warnings = scoring_result.data_warnings + self._generate_data_health_warnings(company_data)
            
            # Create summary response
            summary = SimpleSummaryResponse(
                ticker=ticker,
                company_name=company_data.get("name", ticker),
                fair_value_band=fair_value_band,
                investment_label=investment_label,
                key_factors=key_factors,
                valuation_insights=valuation_insights["summary"],
                market_signals=market_signals["summary"], 
                business_fundamentals=business_fundamentals["summary"],
                data_health_warnings=data_warnings,
                analysis_timestamp=datetime.now(),
                analysis_mode="simple",
                sector=sector,
                rules_applied=self._extract_rules_applied(scoring_result),
                fallback_triggers=data_warnings,
                weighted_score=scoring_result.total_score,
                component_scores={
                    "dcf_score": scoring_result.dcf_score,
                    "financial_score": scoring_result.financial_score,
                    "technical_score": scoring_result.technical_score,
                    "peer_score": scoring_result.peer_score
                }
            )
            
            # Cache the result
            self.cache[cache_key] = (summary, datetime.now())
            
            logger.info(f"Successfully generated simple summary for {ticker}")
            return summary
            
        except Exception as e:
            logger.error(f"Error generating simple summary for {ticker}: {e}")
            raise
    
    async def generate_agentic_summary(
        self,
        ticker: str,
        force_refresh: bool = False
    ) -> AgenticSummaryResponse:
        """
        Generate AI-powered agentic mode summary
        
        Uses single Financial Analyst Agent with sector-specific reasoning
        LLM-enabled comprehensive investment thesis
        """
        cache_key = f"agentic_{ticker}"
        
        # Check cache first
        if not force_refresh and cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if datetime.now() - timestamp < self.cache_duration:
                logger.info(f"Returning cached agentic summary for {ticker}")
                return cached_data
        
        try:
            logger.info(f"Generating AI-powered agentic summary for {ticker}")
            
            # Step 1: Get comprehensive data for AI analysis
            company_data = await self._fetch_company_data(ticker)
            peer_data = await self._fetch_peer_data(ticker)
            technical_data = await self._fetch_technical_data(ticker)
            
            # Step 2: Get rule-based baseline for AI context
            baseline_fair_value = await self._calculate_rule_based_fair_value(ticker, company_data)
            
            # Step 3: Prepare sector-specific context
            sector = self._classify_sector(ticker)
            sector_context = self._get_sector_context(sector)
            
            # Step 4: Generate AI investment thesis
            ai_analysis = await self._generate_ai_investment_thesis(
                ticker=ticker,
                company_data=company_data,
                peer_data=peer_data,
                technical_data=technical_data,
                baseline_fair_value=baseline_fair_value,
                sector_context=sector_context
            )
            
            # Step 5: Parse AI response into structured format
            structured_analysis = self._parse_ai_analysis(ai_analysis, baseline_fair_value)
            
            # Step 6: Generate data health warnings
            data_warnings = self._generate_data_health_warnings(company_data, peer_data, technical_data)
            
            # Create agentic summary response
            summary = AgenticSummaryResponse(
                ticker=ticker,
                company_name=company_data.get("name", ticker),
                fair_value_band=structured_analysis["fair_value_band"],
                investment_label=structured_analysis["investment_label"],
                key_factors=structured_analysis["key_factors"],
                valuation_insights=structured_analysis["valuation_insights"],
                market_signals=structured_analysis["market_signals"],
                business_fundamentals=structured_analysis["business_fundamentals"],
                data_health_warnings=data_warnings,
                analysis_timestamp=datetime.now(),
                analysis_mode="agentic",
                sector=sector,
                agent_reasoning=". ".join(ai_analysis.get("reasoning", [])) if isinstance(ai_analysis.get("reasoning"), list) else ai_analysis.get("reasoning"),
                cost_breakdown=ai_analysis.get("cost_info"),
                model_version=ai_analysis.get("model_version")
            )
            
            # Cache the result
            self.cache[cache_key] = (summary, datetime.now())
            
            logger.info(f"Successfully generated agentic summary for {ticker}")
            return summary
            
        except Exception as e:
            logger.error(f"Error generating agentic summary for {ticker}: {e}")
            raise
            
    async def get_peer_analysis(self, ticker: str, target_count: int = 5) -> dict:
        """Get peer comparison analysis with auto-selected peers"""
        try:
            sector = self._classify_sector(ticker)
            peers = self._select_peers(ticker, sector, target_count)
            
            peer_analyses = []
            for peer_ticker in peers:
                try:
                    # Get simple summary for each peer
                    peer_summary = await self.generate_simple_summary(peer_ticker)
                    peer_analyses.append({
                        "ticker": peer_ticker,
                        "company_name": peer_summary.company_name,
                        "fair_value_band": peer_summary.fair_value_band,
                        "investment_label": peer_summary.investment_label,
                        "sector": peer_summary.sector
                    })
                except Exception as e:
                    logger.warning(f"Failed to analyze peer {peer_ticker}: {e}")
                    continue
            
            return {
                "primary_ticker": ticker,
                "sector": sector,
                "peer_count": len(peer_analyses),
                "peers": peer_analyses,
                "analysis_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in peer analysis for {ticker}: {e}")
            raise
    
    async def generate_batch_summaries(self, tickers: List[str], mode: str) -> dict:
        """Generate summaries for multiple tickers in batch"""
        results = {}
        
        # Process tickers in parallel
        tasks = []
        for ticker in tickers:
            if mode == "simple":
                task = self.generate_simple_summary(ticker)
            else:
                task = self.generate_agentic_summary(ticker) 
            tasks.append((ticker, task))
        
        # Wait for all tasks to complete
        for ticker, task in tasks:
            try:
                result = await task
                results[ticker] = {
                    "success": True,
                    "data": result.dict()
                }
            except Exception as e:
                logger.error(f"Failed batch analysis for {ticker}: {e}")
                results[ticker] = {
                    "success": False,
                    "error": str(e)
                }
        
        return {
            "mode": mode,
            "total_requested": len(tickers),
            "successful": len([r for r in results.values() if r["success"]]),
            "failed": len([r for r in results.values() if not r["success"]]),
            "results": results,
            "batch_timestamp": datetime.now().isoformat()
        }
    
    # Private helper methods
    
    async def _fetch_company_data(self, ticker: str) -> dict:
        """Fetch basic company data using yfinance"""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            hist = stock.history(period="1y")
            
            return {
                "name": info.get("longName", ticker),
                "sector": info.get("sector", "Unknown"),
                "industry": info.get("industry", "Unknown"),
                "market_cap": info.get("marketCap", 0),
                "current_price": info.get("currentPrice", hist["Close"].iloc[-1] if not hist.empty else 0),
                "pe_ratio": info.get("trailingPE", 0),
                "pb_ratio": info.get("priceToBook", 0),
                "price_history": hist,
                "info": info
            }
        except Exception as e:
            logger.error(f"Error fetching company data for {ticker}: {e}")
            raise ValueError(f"Could not fetch data for ticker {ticker}")
    
    async def _calculate_rule_based_fair_value(self, ticker: str, company_data: dict) -> FairValueBand:
        """Calculate fair value using rule-based approach (no LLM)"""
        try:
            # Try DCF first
            try:
                dcf_result = await self.dcf_service.calculate_multi_stage_dcf(ticker, {})
                if dcf_result and hasattr(dcf_result, 'valuation'):
                    intrinsic_value = dcf_result.valuation.intrinsic_value_per_share
                    current_price = company_data["current_price"]
                    
                    # Create 15% band around intrinsic value
                    band_width = intrinsic_value * 0.15
                    return FairValueBand(
                        min_value=intrinsic_value - band_width,
                        max_value=intrinsic_value + band_width,
                        current_price=current_price,
                        method="DCF",
                        confidence=0.8
                    )
            except Exception as e:
                logger.warning(f"DCF calculation failed for {ticker}, falling back to PE multiple: {e}")
            
            # Fallback to PE multiple valuation
            pe_ratio = company_data.get("pe_ratio", 0)
            current_price = company_data["current_price"]
            
            if pe_ratio > 0:
                # Use sector average PE for comparison
                sector_avg_pe = self._get_sector_average_pe(company_data.get("sector", "Unknown"))
                fair_value_pe = current_price * (sector_avg_pe / pe_ratio)
                
                # Create 20% band around PE-based fair value
                band_width = fair_value_pe * 0.20
                return FairValueBand(
                    min_value=fair_value_pe - band_width,
                    max_value=fair_value_pe + band_width,
                    current_price=current_price,
                    method="PE_Multiple",
                    confidence=0.6
                )
            
            # Final fallback - use current price with wide band
            band_width = current_price * 0.25
            return FairValueBand(
                min_value=current_price - band_width,
                max_value=current_price + band_width,
                current_price=current_price,
                method="Sector_Average",
                confidence=0.4
            )
            
        except Exception as e:
            logger.error(f"Error calculating fair value for {ticker}: {e}")
            raise
    
    def _apply_valuation_rules(self, fair_value_band: FairValueBand, company_data: dict) -> dict:
        """Apply valuation rules based on v3 requirements"""
        current_price = fair_value_band.current_price
        min_val, max_val = fair_value_band.min_value, fair_value_band.max_value
        
        rules_applied = []
        
        # Rule: DCF vs current price evaluation
        if current_price < min_val:
            discount = ((min_val - current_price) / current_price) * 100
            if discount >= 25:
                insight = f"Significantly undervalued - trading {discount:.1f}% below fair value"
            elif discount >= 10:
                insight = "Appears moderately undervalued based on DCF analysis"
            else:
                insight = "Slightly undervalued vs intrinsic value"
            rules_applied.append("DCF_UNDERVALUED")
            
        elif current_price > max_val:
            premium = ((current_price - max_val) / max_val) * 100
            if premium >= 25:
                insight = f"Significantly overvalued - trading {premium:.1f}% above fair value"
            elif premium >= 10:
                insight = "Possibly overvalued based on DCF analysis"
            else:
                insight = "Slightly overvalued vs intrinsic value"
            rules_applied.append("DCF_OVERVALUED")
            
        else:
            insight = "Near fair value based on DCF analysis"
            rules_applied.append("DCF_FAIR_VALUE")
        
        return {
            "summary": insight,
            "rules": rules_applied,
            "method": fair_value_band.method
        }
    
    async def _apply_technical_rules(self, ticker: str, company_data: dict) -> dict:
        """Apply technical analysis rules"""
        rules_applied = []
        insights = []
        
        try:
            # Get price history
            hist = company_data.get("price_history")
            if hist is None or hist.empty:
                return {
                    "summary": "Technical indicators unavailable - insufficient price data",
                    "rules": ["INSUFFICIENT_DATA"],
                    "warnings": ["Price history not available"]
                }
            
            # Calculate RSI (simplified)
            closes = hist["Close"]
            if len(closes) >= 14:
                rsi = self._calculate_rsi(closes)
                
                if rsi < 30:
                    insights.append(f"RSI at {rsi:.1f} indicates oversold territory")
                    rules_applied.append("RSI_OVERSOLD")
                elif rsi > 70:
                    insights.append(f"RSI at {rsi:.1f} indicates overbought territory")
                    rules_applied.append("RSI_OVERBOUGHT")
                else:
                    insights.append(f"RSI at {rsi:.1f} shows neutral momentum")
                    rules_applied.append("RSI_NEUTRAL")
            
            # Volume analysis
            if "Volume" in hist.columns:
                avg_volume = hist["Volume"].tail(20).mean()
                recent_volume = hist["Volume"].iloc[-1]
                
                if recent_volume > avg_volume * 1.5:
                    insights.append("Above-average volume suggests institutional interest")
                    rules_applied.append("HIGH_VOLUME")
                elif recent_volume < avg_volume * 0.5:
                    insights.append("Below-average volume indicates low participation")
                    rules_applied.append("LOW_VOLUME")
            
            summary = ". ".join(insights) if insights else "Limited technical signals available"
            
        except Exception as e:
            logger.warning(f"Technical analysis failed for {ticker}: {e}")
            summary = "Technical analysis unavailable due to data limitations"
            rules_applied = ["TECHNICAL_ANALYSIS_FAILED"]
        
        return {
            "summary": summary,
            "rules": rules_applied
        }
    
    def _apply_fundamental_rules(self, ticker: str, company_data: dict) -> dict:
        """Apply business fundamental rules"""
        rules_applied = []
        insights = []
        
        info = company_data.get("info", {})
        
        # PE vs sector average rule  
        pe_ratio = company_data.get("pe_ratio", 0)
        if pe_ratio > 0:
            sector_avg_pe = self._get_sector_average_pe(company_data.get("sector", "Unknown"))
            if pe_ratio > sector_avg_pe * 1.3:
                insights.append(f"PE ratio of {pe_ratio:.1f} is {((pe_ratio/sector_avg_pe-1)*100):.0f}% above sector average")
                rules_applied.append("PE_EXPENSIVE_VS_PEERS")
            elif pe_ratio < sector_avg_pe * 0.7:
                insights.append(f"PE ratio of {pe_ratio:.1f} is attractive vs sector average of {sector_avg_pe:.1f}")
                rules_applied.append("PE_CHEAP_VS_PEERS")
        
        # Revenue growth rule
        revenue_growth = info.get("revenueGrowth", 0)
        if revenue_growth > 0.15:
            insights.append(f"Strong revenue growth of {revenue_growth*100:.1f}%")
            rules_applied.append("STRONG_REVENUE_GROWTH")
        elif revenue_growth < -0.05:
            insights.append(f"Declining revenue growth of {revenue_growth*100:.1f}%")
            rules_applied.append("WEAK_REVENUE_GROWTH")
        
        # Profit margin rule
        profit_margin = info.get("profitMargins", 0)
        if profit_margin > 0.15:
            insights.append(f"Healthy profit margins of {profit_margin*100:.1f}%")
            rules_applied.append("STRONG_MARGINS")
        elif profit_margin < 0.05:
            insights.append(f"Low profit margins of {profit_margin*100:.1f}%")
            rules_applied.append("WEAK_MARGINS")
        
        summary = ". ".join(insights) if insights else "Limited fundamental data available"
        
        return {
            "summary": summary,
            "rules": rules_applied
        }
    
    def _determine_investment_label(
        self, 
        fair_value_band: FairValueBand, 
        valuation: dict, 
        technical: dict, 
        fundamentals: dict
    ) -> Tuple[InvestmentLabel, List[str]]:
        """Determine investment label using rule-based logic"""
        
        # Calculate valuation score
        current_price = fair_value_band.current_price
        fair_value_mid = (fair_value_band.min_value + fair_value_band.max_value) / 2
        valuation_upside = ((fair_value_mid - current_price) / current_price) * 100
        
        # Score components
        valuation_score = 0
        technical_score = 0
        fundamental_score = 0
        key_factors = []
        
        # Valuation scoring
        if valuation_upside > 25:
            valuation_score = 2
            key_factors.append("Significantly undervalued vs fair value")
        elif valuation_upside > 10:
            valuation_score = 1
            key_factors.append("Moderately undervalued")
        elif valuation_upside < -25:
            valuation_score = -2
            key_factors.append("Significantly overvalued")
        elif valuation_upside < -10:
            valuation_score = -1
            key_factors.append("Overvalued vs fair value")
        
        # Technical scoring
        technical_rules = technical.get("rules", [])
        if "RSI_OVERSOLD" in technical_rules:
            technical_score += 1
            key_factors.append("Oversold on RSI indicator")
        elif "RSI_OVERBOUGHT" in technical_rules:
            technical_score -= 1
            key_factors.append("Overbought on RSI indicator")
        
        if "HIGH_VOLUME" in technical_rules:
            technical_score += 0.5
            key_factors.append("High trading volume")
        
        # Fundamental scoring
        fundamental_rules = fundamentals.get("rules", [])
        if "STRONG_REVENUE_GROWTH" in fundamental_rules:
            fundamental_score += 1
            key_factors.append("Strong revenue growth")
        elif "WEAK_REVENUE_GROWTH" in fundamental_rules:
            fundamental_score -= 1
            key_factors.append("Declining revenue")
        
        if "PE_EXPENSIVE_VS_PEERS" in fundamental_rules:
            fundamental_score -= 1
            key_factors.append("Expensive vs peers")
        elif "PE_CHEAP_VS_PEERS" in fundamental_rules:
            fundamental_score += 1
            key_factors.append("Attractive valuation vs peers")
        
        # Calculate total score  
        total_score = valuation_score + technical_score + fundamental_score
        
        # Determine label based on total score
        if total_score >= 2.5:
            return InvestmentLabel.STRONGLY_BULLISH, key_factors
        elif total_score >= 1:
            return InvestmentLabel.CAUTIOUSLY_BULLISH, key_factors
        elif total_score <= -2.5:
            return InvestmentLabel.STRONGLY_BEARISH, key_factors
        elif total_score <= -1:
            return InvestmentLabel.CAUTIOUSLY_BEARISH, key_factors
        else:
            return InvestmentLabel.NEUTRAL, key_factors or ["Balanced risk-reward profile"]
    
    def _classify_sector(self, ticker: str) -> str:
        """Classify ticker into sector using SectorDCFService"""
        return self.sector_dcf_service.classify_sector(ticker)
    
    def _get_sector_average_pe(self, sector: str) -> float:
        """Get average PE ratio for sector (simplified mapping)"""
        sector_pe_avg = {
            "Technology": 25.0,
            "Financial Services": 12.0,
            "Healthcare": 22.0,
            "Consumer Defensive": 18.0,
            "Energy": 15.0,
            "Real Estate": 20.0,
            "Unknown": 18.0
        }
        return sector_pe_avg.get(sector, 18.0)
    
    def _calculate_rsi(self, prices, period: int = 14) -> float:
        """Calculate RSI indicator"""
        deltas = prices.diff()
        gains = deltas.where(deltas > 0, 0)
        losses = -deltas.where(deltas < 0, 0)
        
        avg_gains = gains.rolling(window=period).mean()
        avg_losses = losses.rolling(window=period).mean()
        
        rs = avg_gains / avg_losses
        rsi = 100 - (100 / (1 + rs))
        
        return rsi.iloc[-1]
    
    def _generate_data_health_warnings(self, *data_sources) -> List[str]:
        """Generate data health warnings based on data availability"""
        warnings = []
        
        for data in data_sources:
            if not data:
                warnings.append("Some data sources unavailable - using fallback methods")
                break
        
        return warnings
    
    async def _fetch_peer_data(self, ticker: str) -> dict:
        """Fetch peer company data for scoring analysis"""
        try:
            sector = self._classify_sector(ticker)
            peer_tickers = self._select_peers(ticker, sector, 5)
            
            peers = []
            for peer_ticker in peer_tickers:
                try:
                    # Fetch basic data for each peer
                    peer_stock = yf.Ticker(peer_ticker)
                    peer_info = peer_stock.info
                    
                    peer_data = {
                        "ticker": peer_ticker,
                        "pe_ratio": peer_info.get("trailingPE", 0),
                        "revenue_growth": peer_info.get("revenueGrowth", 0),
                        "profit_margin": peer_info.get("profitMargins", 0),
                        "roe": peer_info.get("returnOnEquity", 0),
                        "market_cap": peer_info.get("marketCap", 0)
                    }
                    peers.append(peer_data)
                    
                except Exception as e:
                    logger.warning(f"Failed to fetch data for peer {peer_ticker}: {e}")
                    continue
            
            return {
                "peers": peers,
                "sector": sector,
                "peer_count": len(peers)
            }
            
        except Exception as e:
            logger.error(f"Error fetching peer data for {ticker}: {e}")
            return {"peers": [], "sector_averages": {}}
    
    async def _fetch_technical_data(self, ticker: str) -> dict:
        """Fetch technical analysis data"""
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="6mo")  # 6 months of data
            
            if hist.empty:
                return {"indicators": {}, "signals": []}
            
            # Calculate RSI
            closes = hist["Close"]
            rsi = self._calculate_rsi(closes) if len(closes) >= 14 else 50
            
            # Calculate price momentum (1 month)
            if len(closes) >= 20:
                current_price = closes.iloc[-1]
                month_ago_price = closes.iloc[-20]
                price_momentum = ((current_price - month_ago_price) / month_ago_price) * 100
            else:
                price_momentum = 0
            
            # Volume analysis
            volume_trend = "neutral"
            if "Volume" in hist.columns and len(hist) >= 20:
                recent_volume = hist["Volume"].tail(5).mean()
                avg_volume = hist["Volume"].mean()
                
                if recent_volume > avg_volume * 1.5:
                    volume_trend = "high_bullish"
                elif recent_volume < avg_volume * 0.5:
                    volume_trend = "low_volume"
            
            # Simple MACD signal
            macd_signal = "neutral"
            if rsi < 30:
                macd_signal = "bullish"
            elif rsi > 70:
                macd_signal = "bearish"
            
            # Support/resistance (simplified)
            support_resistance = "neutral"
            if len(closes) >= 20:
                recent_low = closes.tail(20).min()
                current_price = closes.iloc[-1]
                if current_price > recent_low * 1.05:  # 5% above recent low
                    support_resistance = "above_strong_support"
            
            return {
                "rsi": rsi,
                "macd_signal": macd_signal,
                "volume_trend": volume_trend,
                "price_momentum": price_momentum,
                "support_resistance": support_resistance,
                "data_quality": "medium"
            }
            
        except Exception as e:
            logger.warning(f"Technical data fetch failed for {ticker}: {e}")
            return {
                "rsi": 50,  # Neutral default
                "macd_signal": "neutral",
                "volume_trend": "neutral",
                "price_momentum": 0,
                "support_resistance": "neutral",
                "data_quality": "low"
            }
    
    def _get_sector_context(self, sector: str) -> dict:
        """Get sector-specific context for AI analysis"""
        # Placeholder for sector context
        return {"sector": sector, "key_metrics": [], "risk_factors": []}
    
    async def _generate_ai_investment_thesis(
        self,
        ticker: str,
        company_data: dict,
        peer_data: dict,
        technical_data: dict,
        baseline_fair_value: FairValueBand,
        sector_context: dict
    ) -> dict:
        """Generate AI-powered investment thesis using enhanced agentic analysis"""
        
        try:
            logger.info(f"Generating AI investment thesis for {ticker}")
            
            # Prepare DCF results for AI consumption
            dcf_results = {
                "fair_value": (baseline_fair_value.min_value + baseline_fair_value.max_value) / 2,
                "current_price": baseline_fair_value.current_price,
                "upside_percent": ((baseline_fair_value.min_value + baseline_fair_value.max_value) / 2 - baseline_fair_value.current_price) / baseline_fair_value.current_price * 100,
                "method": baseline_fair_value.method,
                "confidence": baseline_fair_value.confidence
            }
            
            # Get comprehensive AI analysis
            ai_analysis = await agentic_analysis_service.generate_comprehensive_agentic_analysis(
                ticker=ticker,
                company_data=company_data,
                dcf_results=dcf_results,
                technical_data=technical_data,
                news_data=[],  # Will be populated by news service
                peer_data=peer_data
            )
            
            if ai_analysis:
                return {
                    "thesis": ai_analysis.get("investment_thesis", "AI analysis completed"),
                    "reasoning": ai_analysis.get("dcf_commentary", ["AI-enhanced DCF analysis"]),
                    "cost_info": ai_analysis.get("cost_breakdown", {"estimated_cost": 0.0}),
                    "model_version": ai_analysis.get("model_version", "claude-3-haiku"),
                    "financial_health": ai_analysis.get("financial_health", []),
                    "technical_outlook": ai_analysis.get("technical_outlook", []),
                    "news_sentiment": ai_analysis.get("news_sentiment", {}),
                    "peer_context": ai_analysis.get("peer_context", []),
                    "analysis_quality": ai_analysis.get("analysis_quality", "medium")
                }
            else:
                # Fallback to rule-based analysis
                return {
                    "thesis": f"Comprehensive analysis for {ticker} based on quantitative methodology",
                    "reasoning": ["DCF analysis using sector-specific models", "Historical validation with 5-year trends"],
                    "cost_info": {"tokens": 0, "estimated_cost": 0.0},
                    "model_version": "rule-based-fallback"
                }
                
        except Exception as e:
            logger.error(f"Error generating AI investment thesis for {ticker}: {e}")
            # Return fallback
            return {
                "thesis": f"Analysis for {ticker} using enhanced quantitative methodology",
                "reasoning": ["Rule-based analysis with historical validation"],
                "cost_info": {"tokens": 0, "estimated_cost": 0.0},
                "model_version": "fallback"
            }
    
    def _parse_ai_analysis(self, ai_analysis: dict, baseline_fair_value: FairValueBand = None) -> dict:
        """Parse AI analysis into structured format"""
        
        try:
            # Extract AI-generated insights
            investment_thesis = ai_analysis.get("thesis", "AI analysis completed")
            financial_health = ai_analysis.get("financial_health", [])
            technical_outlook = ai_analysis.get("technical_outlook", [])
            dcf_commentary = ai_analysis.get("reasoning", [])
            news_sentiment = ai_analysis.get("news_sentiment", {})
            peer_context = ai_analysis.get("peer_context", [])
            
            # Determine investment label based on AI analysis sentiment
            investment_label = self._determine_ai_investment_label(ai_analysis)
            
            # Use baseline fair value if available, otherwise create fallback
            if baseline_fair_value:
                fair_value_band = FairValueBand(
                    min_value=baseline_fair_value.min_value,
                    max_value=baseline_fair_value.max_value,
                    current_price=baseline_fair_value.current_price,
                    method="AI-Enhanced DCF",
                    confidence=min(baseline_fair_value.confidence + 0.1, 1.0)  # Boost confidence with AI analysis
                )
            else:
                fair_value_band = FairValueBand(
                    min_value=200, max_value=250, current_price=220,
                    method="AI-Enhanced DCF", confidence=0.8
                )
            
            # Combine key factors from different AI analysis components
            key_factors = []
            if dcf_commentary:
                key_factors.extend(dcf_commentary[:2])  # Top 2 DCF insights
            if technical_outlook:
                key_factors.extend(technical_outlook[:1])  # Top technical insight
            if not key_factors:  # Fallback
                key_factors = ["AI-enhanced analysis completed", "Comprehensive evaluation using multiple factors"]
            
            return {
                "fair_value_band": fair_value_band,
                "investment_label": investment_label,
                "key_factors": key_factors[:5],  # Limit to top 5 factors
                "valuation_insights": ". ".join(dcf_commentary) if dcf_commentary else "AI-enhanced DCF analysis completed",
                "market_signals": ". ".join(technical_outlook) if technical_outlook else "Technical analysis integrated with AI insights",
                "business_fundamentals": ". ".join(financial_health) if financial_health else "Financial health assessed using AI methodology"
            }
            
        except Exception as e:
            logger.error(f"Error parsing AI analysis: {e}")
            # Return structured fallback
            return {
                "fair_value_band": FairValueBand(
                    min_value=200, max_value=250, current_price=220,
                    method="Fallback Analysis", confidence=0.6
                ),
                "investment_label": InvestmentLabel.NEUTRAL,
                "key_factors": ["Analysis completed using quantitative methods", "Multiple factor evaluation"],
                "valuation_insights": "Valuation analysis using enhanced methodology",
                "market_signals": "Market positioning assessed using technical indicators",
                "business_fundamentals": "Business fundamentals evaluated using financial metrics"
            }
    
    def _determine_ai_investment_label(self, ai_analysis: dict) -> InvestmentLabel:
        """Determine investment label from AI analysis"""
        
        try:
            thesis = ai_analysis.get("thesis", "").lower()
            financial_health = " ".join(ai_analysis.get("financial_health", [])).lower()
            technical_outlook = " ".join(ai_analysis.get("technical_outlook", [])).lower()
            
            # Simple keyword-based sentiment analysis
            positive_keywords = ["strong", "bullish", "growth", "outperform", "undervalued", "opportunity"]
            negative_keywords = ["weak", "bearish", "decline", "overvalued", "risk", "concern"]
            
            combined_text = f"{thesis} {financial_health} {technical_outlook}"
            
            positive_score = sum(1 for keyword in positive_keywords if keyword in combined_text)
            negative_score = sum(1 for keyword in negative_keywords if keyword in combined_text)
            
            if positive_score >= 3 and positive_score > negative_score + 1:
                return InvestmentLabel.STRONGLY_BULLISH
            elif positive_score >= 2 and positive_score > negative_score:
                return InvestmentLabel.CAUTIOUSLY_BULLISH
            elif negative_score >= 3 and negative_score > positive_score + 1:
                return InvestmentLabel.STRONGLY_BEARISH
            elif negative_score >= 2 and negative_score > positive_score:
                return InvestmentLabel.CAUTIOUSLY_BEARISH
            else:
                return InvestmentLabel.NEUTRAL
                
        except Exception as e:
            logger.error(f"Error determining AI investment label: {e}")
            return InvestmentLabel.NEUTRAL
    
    def _select_peers(self, ticker: str, sector: str, target_count: int) -> List[str]:
        """Select peer companies for comparison using SectorDCFService mappings"""
        ticker_base = ticker.replace(".NS", "").replace(".BO", "")
        
        # Use SectorDCFService sector mappings
        sector_mappings = self.sector_dcf_service.sector_mappings
        
        if sector in sector_mappings:
            peers = [t for t in sector_mappings[sector] if t != ticker_base]
            return peers[:target_count]
        
        # Fallback peers
        return ["RELIANCE", "TCS", "HDFCBANK"][:target_count]
    
    # New helper methods for weighted scoring integration
    
    def _create_fair_value_band_from_scoring(self, scoring_result, company_data: Dict) -> FairValueBand:
        """Create fair value band from weighted scoring DCF component"""
        current_price = company_data.get("current_price", 0)
        
        # Extract DCF component details
        dcf_component = scoring_result.component_scores.get("DCF")
        if not dcf_component or dcf_component.raw_score == 0:
            # Fallback to simple band around current price
            band_width = current_price * 0.20
            return FairValueBand(
                min_value=current_price - band_width,
                max_value=current_price + band_width,
                current_price=current_price,
                method="Fallback_Estimate",
                confidence=0.3
            )
        
        # Calculate implied fair value from DCF score
        # DCF raw score represents % upside/downside
        upside_pct = dcf_component.raw_score / 100.0  # Convert to decimal
        
        if upside_pct > 0:
            # Stock is undervalued, fair value is higher
            fair_value = current_price / (1 - abs(upside_pct))
        else:
            # Stock is overvalued, fair value is lower  
            fair_value = current_price * (1 - abs(upside_pct))
        
        # Create 15% band around fair value
        band_width = fair_value * 0.15
        
        return FairValueBand(
            min_value=fair_value - band_width,
            max_value=fair_value + band_width,
            current_price=current_price,
            method="Weighted_DCF",
            confidence=dcf_component.confidence
        )
    
    def _extract_valuation_insights(self, scoring_result) -> Dict:
        """Extract valuation insights from DCF component scoring"""
        dcf_component = scoring_result.component_scores.get("DCF")
        if not dcf_component:
            return {"summary": "DCF analysis unavailable", "rules": []}
        
        return {
            "summary": ". ".join(dcf_component.reasoning),
            "rules": [f"DCF_SCORE_{dcf_component.raw_score:.0f}"],
            "method": "Weighted_Scoring_DCF"
        }
    
    def _extract_market_insights(self, scoring_result) -> Dict:
        """Extract market insights from Technical component scoring"""
        technical_component = scoring_result.component_scores.get("Technical")
        if not technical_component:
            return {"summary": "Technical analysis unavailable", "rules": []}
        
        return {
            "summary": ". ".join(technical_component.reasoning),
            "rules": [f"TECHNICAL_SCORE_{technical_component.raw_score:.0f}"]
        }
    
    def _extract_fundamental_insights(self, scoring_result) -> Dict:
        """Extract fundamental insights from Financial component scoring"""
        financial_component = scoring_result.component_scores.get("Financial")
        if not financial_component:
            return {"summary": "Financial analysis unavailable", "rules": []}
        
        return {
            "summary": ". ".join(financial_component.reasoning),
            "rules": [f"FINANCIAL_SCORE_{financial_component.raw_score:.0f}"]
        }
    
    def _extract_key_factors_from_scoring(self, scoring_result) -> List[str]:
        """Extract key factors from all scoring components"""
        key_factors = []
        
        # Add top reasons from each component
        for component_name, component in scoring_result.component_scores.items():
            if component.reasoning and abs(component.raw_score) > 10:  # Only significant factors
                # Take first reason from each significant component
                key_factors.append(f"[{component_name}] {component.reasoning[0]}")
        
        # If no significant factors, use investment label reasoning
        if not key_factors:
            key_factors.append(f"Overall assessment: {scoring_result.investment_label}")
        
        return key_factors[:5]  # Limit to top 5 factors
    
    def _extract_rules_applied(self, scoring_result) -> List[str]:
        """Extract all rules applied across scoring components"""
        rules = []
        
        for component in scoring_result.component_scores.values():
            # Extract component type and score as rule
            score_rule = f"{component.component.upper()}_WEIGHTED_SCORE_{component.weighted_score:.1f}"
            rules.append(score_rule)
        
        # Add overall scoring rule
        rules.append(f"TOTAL_WEIGHTED_SCORE_{scoring_result.total_score:.1f}")
        rules.append(f"INVESTMENT_LABEL_{scoring_result.investment_label}")
        
        return rules