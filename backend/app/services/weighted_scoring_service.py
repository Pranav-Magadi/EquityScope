# Weighted Scoring Framework Service
# Implements v3 weighted scoring: DCF 35%, Financial 25%, Technical 20%, Peer 20%

import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from ..models.summary import InvestmentLabel, FairValueBand
from .sector_dcf.banking_dcf import BankingDCFCalculator, BankingMetrics
from .sector_dcf.pharma_dcf import PharmaDCFCalculator, PharmaMetrics  
from .sector_dcf.realestate_dcf import RealEstateDCFCalculator, RealEstateMetrics
from .sector_dcf_service import SectorDCFService

logger = logging.getLogger(__name__)

class ComponentWeight(Enum):
    """v3 Weighted scoring component weights"""
    DCF = 0.35          # 35% - Valuation foundation
    FINANCIAL = 0.25    # 25% - Financial health
    TECHNICAL = 0.20    # 20% - Market signals
    PEER = 0.20         # 20% - Relative positioning

@dataclass
class ComponentScore:
    """Individual component scoring result"""
    component: str
    raw_score: float        # -100 to +100 scale
    weighted_score: float   # Raw score * weight
    confidence: float       # 0.0 to 1.0
    reasoning: List[str]    # Explanation of scoring
    data_quality: str       # "High", "Medium", "Low"

@dataclass
class WeightedScoringResult:
    """Complete weighted scoring result"""
    ticker: str
    total_score: float              # Final weighted score
    investment_label: InvestmentLabel
    component_scores: Dict[str, ComponentScore]
    
    # Score breakdown
    dcf_score: float
    financial_score: float
    technical_score: float
    peer_score: float
    
    # Meta information
    confidence: float
    sector: str
    scoring_timestamp: datetime
    data_warnings: List[str]

class WeightedScoringService:
    """
    v3 Weighted Scoring Framework implementing:
    
    DCF (35%): Sector-specific valuation models
    Financial (25%): Profitability, growth, efficiency metrics  
    Technical (20%): Price momentum, volume, RSI signals
    Peer (20%): Relative valuation vs sector peers
    
    Total Score Range: -100 to +100
    Investment Labels: Strongly Bearish (-60+), Cautiously Bearish (-20+), 
                     Neutral (-20 to +20), Cautiously Bullish (+20+), Strongly Bullish (+60+)
    """
    
    def __init__(self):
        # Initialize sector DCF service (replaces individual calculators)
        self.sector_dcf_service = SectorDCFService()
        
        # Score thresholds for investment labels
        self.label_thresholds = {
            InvestmentLabel.STRONGLY_BULLISH: 60,
            InvestmentLabel.CAUTIOUSLY_BULLISH: 20,
            InvestmentLabel.NEUTRAL: -20,           # -20 to +20 range
            InvestmentLabel.CAUTIOUSLY_BEARISH: -60,
            InvestmentLabel.STRONGLY_BEARISH: -100
        }
        
        # Component scoring ranges
        self.score_ranges = {
            "excellent": (70, 100),
            "good": (30, 70),
            "neutral": (-30, 30),
            "poor": (-70, -30),
            "very_poor": (-100, -70)
        }
    
    async def calculate_weighted_score(
        self,
        ticker: str,
        company_data: Dict,
        sector: str,
        peer_data: Dict = None,
        technical_data: Dict = None,
        force_refresh: bool = False
    ) -> WeightedScoringResult:
        """
        Calculate comprehensive weighted score for a stock with intelligent caching
        
        Args:
            ticker: Stock ticker symbol
            company_data: Company financial and market data
            sector: Sector classification (for DCF model selection)
            peer_data: Peer comparison data
            technical_data: Technical analysis data
            force_refresh: Skip cache and force fresh calculations
        
        Returns:
            WeightedScoringResult with detailed scoring breakdown
        """
        try:
            logger.info(f"Calculating weighted score for {ticker} in {sector} sector")
            
            component_scores = {}
            data_warnings = []
            
            # Component 1: DCF Score (35%)
            dcf_result = await self._calculate_dcf_score(ticker, company_data, sector, force_refresh)
            component_scores["DCF"] = dcf_result
            
            # Component 2: Financial Score (25%)  
            financial_result = self._calculate_financial_score(ticker, company_data, sector)
            component_scores["Financial"] = financial_result
            
            # Component 3: Technical Score (20%)
            technical_result = await self._calculate_technical_score(ticker, technical_data or {})
            component_scores["Technical"] = technical_result
            
            # Component 4: Peer Score (20%)
            peer_result = await self._calculate_peer_score(ticker, company_data, peer_data or {})
            component_scores["Peer"] = peer_result
            
            # Calculate total weighted score
            total_score = sum(score.weighted_score for score in component_scores.values())
            
            # Determine investment label
            investment_label = self._determine_investment_label(total_score)
            
            # Calculate overall confidence
            overall_confidence = self._calculate_overall_confidence(component_scores)
            
            # Collect data warnings
            for score in component_scores.values():
                if score.data_quality == "Low":
                    data_warnings.append(f"{score.component} analysis limited by data quality")
            
            result = WeightedScoringResult(
                ticker=ticker,
                total_score=total_score,
                investment_label=investment_label,
                component_scores=component_scores,
                dcf_score=component_scores["DCF"].weighted_score,
                financial_score=component_scores["Financial"].weighted_score,
                technical_score=component_scores["Technical"].weighted_score,
                peer_score=component_scores["Peer"].weighted_score,
                confidence=overall_confidence,
                sector=sector,
                scoring_timestamp=datetime.now(),
                data_warnings=data_warnings
            )
            
            logger.info(f"Weighted scoring completed for {ticker}: Total Score = {total_score:.1f}, Label = {investment_label}")
            return result
            
        except Exception as e:
            logger.error(f"Error in weighted scoring for {ticker}: {e}")
            raise
    
    async def _calculate_dcf_score(self, ticker: str, company_data: Dict, sector: str, force_refresh: bool = False) -> ComponentScore:
        """Calculate DCF component score (35% weight) using SectorDCFService"""
        
        try:
            reasoning = []
            raw_score = 0.0
            confidence = 0.5
            data_quality = "Medium"
            
            current_price = company_data.get("current_price", 0)
            if current_price <= 0:
                return ComponentScore(
                    component="DCF",
                    raw_score=0,
                    weighted_score=0,
                    confidence=0.1,
                    reasoning=["Current price data unavailable"],
                    data_quality="Low"
                )
            
            # Use SectorDCFService for sector-specific DCF calculation
            sector_dcf_result = await self.sector_dcf_service.calculate_sector_dcf(
                ticker=ticker,
                sector=sector,
                mode="simple",  # WeightedScoring always uses simple mode
                company_data=company_data,
                force_refresh=force_refresh
            )
            
            fair_value = sector_dcf_result.fair_value
            
            if fair_value and fair_value > 0:
                # Use the already calculated upside/downside from SectorDCFService
                upside_pct = sector_dcf_result.upside_downside_pct
                
                # Convert upside percentage to score (-100 to +100)
                if upside_pct >= 50:        # 50%+ upside
                    raw_score = 90
                    reasoning.append(f"Significant undervaluation: {upside_pct:.1f}% upside to {sector_dcf_result.dcf_method} fair value")
                elif upside_pct >= 25:      # 25-50% upside
                    raw_score = 60
                    reasoning.append(f"Substantial undervaluation: {upside_pct:.1f}% upside to fair value")
                elif upside_pct >= 10:      # 10-25% upside
                    raw_score = 30
                    reasoning.append(f"Moderate undervaluation: {upside_pct:.1f}% upside to fair value")
                elif upside_pct >= -10:     # Fair value range
                    raw_score = 0
                    reasoning.append(f"Trading near fair value: {upside_pct:.1f}% from {sector_dcf_result.dcf_method}")
                elif upside_pct >= -25:     # 10-25% overvalued
                    raw_score = -30
                    reasoning.append(f"Moderate overvaluation: {abs(upside_pct):.1f}% above fair value")
                elif upside_pct >= -50:     # 25-50% overvalued
                    raw_score = -60
                    reasoning.append(f"Substantial overvaluation: {abs(upside_pct):.1f}% above fair value")
                else:                       # 50%+ overvalued
                    raw_score = -90
                    reasoning.append(f"Significant overvaluation: {abs(upside_pct):.1f}% above {sector_dcf_result.dcf_method} fair value")
                
                # Use confidence from sector DCF result
                confidence = sector_dcf_result.confidence
                data_quality = "High" if confidence > 0.7 else "Medium" if confidence > 0.4 else "Low"
                
                # Add sector-specific insights to reasoning
                reasoning.append(f"Using {sector} sector-specific {sector_dcf_result.dcf_method} model")
                
            else:
                # DCF calculation failed, use fallback
                reasoning.append("DCF calculation unavailable, using PE-based estimate")
                raw_score = self._fallback_valuation_score(company_data)
                confidence = 0.4
                data_quality = "Low"
            
        except Exception as e:
            logger.warning(f"DCF scoring failed for {ticker}: {e}")
            reasoning.append("DCF analysis failed - using neutral score")
            raw_score = 0
            confidence = 0.2
            data_quality = "Low"
        
        weighted_score = raw_score * ComponentWeight.DCF.value
        
        return ComponentScore(
            component="DCF",
            raw_score=raw_score,
            weighted_score=weighted_score,
            confidence=confidence,
            reasoning=reasoning,
            data_quality=data_quality
        )
    
    def _calculate_financial_score(self, ticker: str, company_data: Dict, sector: str) -> ComponentScore:
        """Calculate Financial Health component score (25% weight)"""
        
        reasoning = []
        raw_score = 0.0
        confidence = 0.5
        data_quality = "Medium"
        
        try:
            info = company_data.get("info", {})
            
            # Financial metrics
            roe = info.get("returnOnEquity", 0)
            profit_margin = info.get("profitMargins", 0)
            revenue_growth = info.get("revenueGrowth", 0)
            debt_to_equity = info.get("debtToEquity", 0)
            current_ratio = info.get("currentRatio", 0)
            
            score_components = []
            
            # ROE scoring
            if roe > 0.20:      # >20% ROE
                roe_score = 25
                reasoning.append(f"Excellent ROE of {roe*100:.1f}%")
            elif roe > 0.15:    # 15-20% ROE
                roe_score = 15
                reasoning.append(f"Strong ROE of {roe*100:.1f}%")
            elif roe > 0.10:    # 10-15% ROE
                roe_score = 5
                reasoning.append(f"Decent ROE of {roe*100:.1f}%")
            elif roe > 0:       # Positive ROE
                roe_score = -5
                reasoning.append(f"Low ROE of {roe*100:.1f}%")
            else:               # Negative ROE
                roe_score = -25
                reasoning.append(f"Negative ROE of {roe*100:.1f}%")
            
            score_components.append(roe_score)
            
            # Profit Margin scoring
            if profit_margin > 0.15:    # >15% margin
                margin_score = 20
                reasoning.append(f"High profit margins of {profit_margin*100:.1f}%")
            elif profit_margin > 0.10:  # 10-15% margin
                margin_score = 10
                reasoning.append(f"Good profit margins of {profit_margin*100:.1f}%")
            elif profit_margin > 0.05:  # 5-10% margin
                margin_score = 0
                reasoning.append(f"Average profit margins of {profit_margin*100:.1f}%")
            elif profit_margin > 0:     # Positive margin
                margin_score = -10
                reasoning.append(f"Low profit margins of {profit_margin*100:.1f}%")
            else:                       # Negative margin
                margin_score = -20
                reasoning.append(f"Negative profit margins of {profit_margin*100:.1f}%")
            
            score_components.append(margin_score)
            
            # Revenue Growth scoring
            if revenue_growth > 0.20:    # >20% growth
                growth_score = 20
                reasoning.append(f"Strong revenue growth of {revenue_growth*100:.1f}%")
            elif revenue_growth > 0.10:  # 10-20% growth
                growth_score = 10
                reasoning.append(f"Good revenue growth of {revenue_growth*100:.1f}%")
            elif revenue_growth > 0:     # Positive growth
                growth_score = 0
                reasoning.append(f"Modest revenue growth of {revenue_growth*100:.1f}%")
            elif revenue_growth > -0.05: # Slight decline
                growth_score = -10
                reasoning.append(f"Slight revenue decline of {abs(revenue_growth)*100:.1f}%")
            else:                        # Significant decline
                growth_score = -20
                reasoning.append(f"Revenue declining by {abs(revenue_growth)*100:.1f}%")
            
            score_components.append(growth_score)
            
            # Debt management scoring
            if debt_to_equity == 0 or debt_to_equity < 0.3:  # Very low debt
                debt_score = 15
                reasoning.append("Strong balance sheet with low debt")
            elif debt_to_equity < 0.6:   # Moderate debt
                debt_score = 5
                reasoning.append("Moderate debt levels")
            elif debt_to_equity < 1.0:   # High debt
                debt_score = -5
                reasoning.append("Elevated debt levels")
            else:                        # Very high debt
                debt_score = -15
                reasoning.append("High debt burden may constrain growth")
            
            score_components.append(debt_score)
            
            # Liquidity scoring (if available)
            if current_ratio > 2.0:      # Strong liquidity
                liquidity_score = 10
                reasoning.append("Strong liquidity position")
            elif current_ratio > 1.5:    # Good liquidity
                liquidity_score = 5
                reasoning.append("Adequate liquidity")
            elif current_ratio > 1.0:    # Acceptable liquidity
                liquidity_score = 0
            elif current_ratio > 0:      # Weak liquidity
                liquidity_score = -10
                reasoning.append("Weak liquidity position")
            else:                        # No data
                liquidity_score = 0
            
            score_components.append(liquidity_score)
            
            # Calculate final financial score
            raw_score = sum(score_components)
            
            # Cap score between -100 and +100
            raw_score = max(min(raw_score, 100), -100)
            
            confidence = 0.7 if len([s for s in score_components if s != 0]) >= 3 else 0.5
            data_quality = "High" if confidence > 0.6 else "Medium"
            
        except Exception as e:
            logger.warning(f"Financial scoring failed for {ticker}: {e}")
            reasoning.append("Limited financial data available")
            raw_score = 0
            confidence = 0.3
            data_quality = "Low"
        
        weighted_score = raw_score * ComponentWeight.FINANCIAL.value
        
        return ComponentScore(
            component="Financial",
            raw_score=raw_score,
            weighted_score=weighted_score,
            confidence=confidence,
            reasoning=reasoning,
            data_quality=data_quality
        )
    
    async def _calculate_technical_score(self, ticker: str, technical_data: Dict) -> ComponentScore:
        """Calculate Technical Analysis component score (20% weight)"""
        
        reasoning = []
        raw_score = 0.0
        confidence = 0.5
        data_quality = "Medium"
        
        try:
            # Extract technical indicators
            rsi = technical_data.get("rsi", 50)  # Default to neutral
            macd_signal = technical_data.get("macd_signal", "neutral")
            volume_trend = technical_data.get("volume_trend", "neutral")
            price_momentum = technical_data.get("price_momentum", 0)  # % change
            support_resistance = technical_data.get("support_resistance", "neutral")
            
            score_components = []
            
            # RSI scoring
            if rsi < 30:                 # Oversold
                rsi_score = 25
                reasoning.append(f"RSI at {rsi:.1f} indicates oversold conditions")
            elif rsi < 40:               # Approaching oversold
                rsi_score = 10
                reasoning.append(f"RSI at {rsi:.1f} suggests selling pressure")
            elif 40 <= rsi <= 60:        # Neutral zone
                rsi_score = 0
                reasoning.append(f"RSI at {rsi:.1f} shows neutral momentum")
            elif rsi < 70:               # Approaching overbought
                rsi_score = -10
                reasoning.append(f"RSI at {rsi:.1f} suggests buying pressure")
            else:                        # Overbought
                rsi_score = -25
                reasoning.append(f"RSI at {rsi:.1f} indicates overbought conditions")
            
            score_components.append(rsi_score)
            
            # MACD scoring
            if macd_signal == "bullish_crossover":
                macd_score = 20
                reasoning.append("MACD shows bullish crossover signal")
            elif macd_signal == "bullish":
                macd_score = 10
                reasoning.append("MACD trend remains bullish")
            elif macd_signal == "neutral":
                macd_score = 0
                reasoning.append("MACD shows neutral signals")
            elif macd_signal == "bearish":
                macd_score = -10
                reasoning.append("MACD trend is bearish")
            elif macd_signal == "bearish_crossover":
                macd_score = -20
                reasoning.append("MACD shows bearish crossover signal")
            else:
                macd_score = 0
            
            score_components.append(macd_score)
            
            # Volume trend scoring
            if volume_trend == "high_bullish":
                volume_score = 15
                reasoning.append("High volume supports price strength")
            elif volume_trend == "normal_bullish":
                volume_score = 5
                reasoning.append("Volume supports upward movement")
            elif volume_trend == "neutral":
                volume_score = 0
            elif volume_trend == "low_volume":
                volume_score = -5
                reasoning.append("Low volume raises sustainability concerns")
            elif volume_trend == "high_bearish":
                volume_score = -15
                reasoning.append("High volume indicates selling pressure")
            else:
                volume_score = 0
            
            score_components.append(volume_score)
            
            # Price momentum scoring
            if price_momentum > 10:       # >10% momentum
                momentum_score = 20
                reasoning.append(f"Strong positive momentum: {price_momentum:.1f}%")
            elif price_momentum > 5:      # 5-10% momentum
                momentum_score = 10
                reasoning.append(f"Good positive momentum: {price_momentum:.1f}%")
            elif price_momentum > -5:     # -5% to +5%
                momentum_score = 0
                reasoning.append("Neutral price momentum")
            elif price_momentum > -10:    # -10% to -5%
                momentum_score = -10
                reasoning.append(f"Negative momentum: {price_momentum:.1f}%")
            else:                         # <-10%
                momentum_score = -20
                reasoning.append(f"Strong negative momentum: {price_momentum:.1f}%")
            
            score_components.append(momentum_score)
            
            # Support/Resistance scoring
            if support_resistance == "above_strong_support":
                sr_score = 10
                reasoning.append("Trading above strong support level")
            elif support_resistance == "near_resistance":
                sr_score = -5
                reasoning.append("Approaching resistance level")
            elif support_resistance == "below_support":
                sr_score = -15
                reasoning.append("Trading below support level")
            else:
                sr_score = 0
            
            score_components.append(sr_score)
            
            # Calculate final technical score
            raw_score = sum(score_components)
            
            # Cap score between -100 and +100
            raw_score = max(min(raw_score, 100), -100)
            
            # Adjust confidence based on data availability
            non_zero_components = len([s for s in score_components if s != 0])
            confidence = min(0.8, 0.4 + (non_zero_components * 0.1))
            data_quality = "High" if confidence > 0.7 else "Medium" if confidence > 0.4 else "Low"
            
        except Exception as e:
            logger.warning(f"Technical scoring failed for {ticker}: {e}")
            reasoning.append("Technical analysis data limited")
            raw_score = 0
            confidence = 0.3
            data_quality = "Low"
        
        weighted_score = raw_score * ComponentWeight.TECHNICAL.value
        
        return ComponentScore(
            component="Technical",
            raw_score=raw_score,
            weighted_score=weighted_score,
            confidence=confidence,
            reasoning=reasoning,
            data_quality=data_quality
        )
    
    async def _calculate_peer_score(self, ticker: str, company_data: Dict, peer_data: Dict) -> ComponentScore:
        """Calculate Peer Comparison component score (20% weight)"""
        
        reasoning = []
        raw_score = 0.0
        confidence = 0.5
        data_quality = "Medium"
        
        try:
            if not peer_data or "peers" not in peer_data:
                reasoning.append("Peer comparison data unavailable")
                return ComponentScore(
                    component="Peer",
                    raw_score=0,
                    weighted_score=0,
                    confidence=0.2,
                    reasoning=reasoning,
                    data_quality="Low"
                )
            
            peers = peer_data["peers"]
            company_info = company_data.get("info", {})
            
            score_components = []
            
            # PE Ratio comparison
            company_pe = company_info.get("trailingPE", 0)
            peer_pes = [peer.get("pe_ratio", 0) for peer in peers if peer.get("pe_ratio", 0) > 0]
            
            if company_pe > 0 and peer_pes:
                median_peer_pe = sorted(peer_pes)[len(peer_pes)//2]
                pe_discount = ((median_peer_pe - company_pe) / median_peer_pe) * 100
                
                if pe_discount > 30:      # 30%+ discount
                    pe_score = 25
                    reasoning.append(f"Trading at {pe_discount:.0f}% discount to peer PE")
                elif pe_discount > 15:    # 15-30% discount
                    pe_score = 15
                    reasoning.append(f"Attractive {pe_discount:.0f}% discount to peer PE")
                elif pe_discount > -15:   # Within 15% of peers
                    pe_score = 0
                    reasoning.append("PE valuation in line with peers")
                elif pe_discount > -30:   # 15-30% premium
                    pe_score = -15
                    reasoning.append(f"Trading at {abs(pe_discount):.0f}% premium to peers")
                else:                     # 30%+ premium
                    pe_score = -25
                    reasoning.append(f"Expensive at {abs(pe_discount):.0f}% premium to peers")
                
                score_components.append(pe_score)
            
            # Revenue Growth comparison
            company_growth = company_info.get("revenueGrowth", 0)
            peer_growths = [peer.get("revenue_growth", 0) for peer in peers if "revenue_growth" in peer]
            
            if peer_growths:
                median_peer_growth = sorted(peer_growths)[len(peer_growths)//2]
                growth_advantage = (company_growth - median_peer_growth) * 100
                
                if growth_advantage > 10:     # 10%+ higher growth
                    growth_score = 20
                    reasoning.append(f"Revenue growth {growth_advantage:.1f}pp above peers")
                elif growth_advantage > 5:    # 5-10%+ higher
                    growth_score = 10
                    reasoning.append(f"Revenue growth {growth_advantage:.1f}pp above peers")
                elif growth_advantage > -5:   # Within 5% of peers
                    growth_score = 0
                    reasoning.append("Revenue growth similar to peers")
                elif growth_advantage > -10:  # 5-10% lower
                    growth_score = -10
                    reasoning.append(f"Revenue growth {abs(growth_advantage):.1f}pp below peers")
                else:                         # 10%+ lower
                    growth_score = -20
                    reasoning.append(f"Revenue growth {abs(growth_advantage):.1f}pp below peers")
                
                score_components.append(growth_score)
            
            # Profitability comparison
            company_margin = company_info.get("profitMargins", 0)
            peer_margins = [peer.get("profit_margin", 0) for peer in peers if "profit_margin" in peer]
            
            if company_margin > 0 and peer_margins:
                median_peer_margin = sorted(peer_margins)[len(peer_margins)//2]
                margin_advantage = (company_margin - median_peer_margin) * 100
                
                if margin_advantage > 5:      # 5%+ higher margin
                    margin_score = 15
                    reasoning.append(f"Profit margins {margin_advantage:.1f}pp above peers")
                elif margin_advantage > 2:    # 2-5% higher
                    margin_score = 8
                    reasoning.append(f"Profit margins {margin_advantage:.1f}pp above peers")
                elif margin_advantage > -2:   # Within 2% of peers
                    margin_score = 0
                    reasoning.append("Profit margins similar to peers")
                elif margin_advantage > -5:   # 2-5% lower
                    margin_score = -8
                    reasoning.append(f"Profit margins {abs(margin_advantage):.1f}pp below peers")
                else:                         # 5%+ lower
                    margin_score = -15
                    reasoning.append(f"Profit margins {abs(margin_advantage):.1f}pp below peers")
                
                score_components.append(margin_score)
            
            # Calculate final peer score
            raw_score = sum(score_components) if score_components else 0
            
            # Cap score between -100 and +100
            raw_score = max(min(raw_score, 100), -100)
            
            confidence = 0.7 if len(score_components) >= 2 else 0.4
            data_quality = "High" if confidence > 0.6 else "Medium"
            
        except Exception as e:
            logger.warning(f"Peer scoring failed for {ticker}: {e}")
            reasoning.append("Peer comparison analysis failed")
            raw_score = 0
            confidence = 0.2
            data_quality = "Low"
        
        weighted_score = raw_score * ComponentWeight.PEER.value
        
        return ComponentScore(
            component="Peer",
            raw_score=raw_score,
            weighted_score=weighted_score,
            confidence=confidence,
            reasoning=reasoning,
            data_quality=data_quality
        )
    
    def _determine_investment_label(self, total_score: float) -> InvestmentLabel:
        """Determine investment label based on total weighted score"""
        
        if total_score >= self.label_thresholds[InvestmentLabel.STRONGLY_BULLISH]:
            return InvestmentLabel.STRONGLY_BULLISH
        elif total_score >= self.label_thresholds[InvestmentLabel.CAUTIOUSLY_BULLISH]:
            return InvestmentLabel.CAUTIOUSLY_BULLISH
        elif total_score >= self.label_thresholds[InvestmentLabel.NEUTRAL]:
            return InvestmentLabel.NEUTRAL
        elif total_score >= self.label_thresholds[InvestmentLabel.CAUTIOUSLY_BEARISH]:
            return InvestmentLabel.CAUTIOUSLY_BEARISH
        else:
            return InvestmentLabel.STRONGLY_BEARISH
    
    def _calculate_overall_confidence(self, component_scores: Dict[str, ComponentScore]) -> float:
        """Calculate overall confidence as weighted average of component confidences"""
        
        weights = {
            "DCF": ComponentWeight.DCF.value,
            "Financial": ComponentWeight.FINANCIAL.value,
            "Technical": ComponentWeight.TECHNICAL.value,
            "Peer": ComponentWeight.PEER.value
        }
        
        weighted_confidences = []
        for component, score in component_scores.items():
            weight = weights.get(component, 0)
            weighted_confidences.append(score.confidence * weight)
        
        return sum(weighted_confidences)
    
    # DCF calculations now handled by SectorDCFService
    
    def _fallback_valuation_score(self, company_data: Dict) -> float:
        """Fallback valuation scoring when DCF is unavailable"""
        try:
            info = company_data.get("info", {})
            pe_ratio = info.get("trailingPE", 0)
            pb_ratio = info.get("priceToBook", 0)
            
            score = 0
            
            # PE-based scoring
            if 0 < pe_ratio < 15:
                score += 20  # Attractive PE
            elif 15 <= pe_ratio < 25:
                score += 5   # Reasonable PE
            elif pe_ratio >= 25:
                score -= 15  # Expensive PE
            
            # PB-based scoring
            if 0 < pb_ratio < 1.5:
                score += 10  # Attractive PB
            elif pb_ratio >= 3:
                score -= 10  # Expensive PB
            
            return max(min(score, 30), -30)  # Conservative scoring for fallback
            
        except Exception:
            return 0