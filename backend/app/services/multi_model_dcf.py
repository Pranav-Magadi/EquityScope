import logging
from typing import Dict, Any, Optional, List, Tuple
from enum import Enum
from datetime import datetime
import yfinance as yf
from ..models.dcf import (
    DCFAssumptions, DCFValuation, DCFProjection, 
    DCFMode, GrowthStage, MultiStageAssumptions,
    MultiStageDCFResponse
)
from .historical_validation import historical_validation_service

logger = logging.getLogger(__name__)

class ValuationModel(Enum):
    """Supported valuation models for different industries."""
    DCF = "DCF"           # Discounted Cash Flow - Default for most companies
    DDM = "DDM"           # Dividend Discount Model - For banks and financial services  
    ASSET = "Asset"       # Asset-based valuation - For REITs and utilities

class IndustryClassifier:
    """
    Industry classification system for automatic valuation model selection.
    
    Maps company sectors/industries to appropriate valuation models based on
    financial structure and business characteristics.
    """
    
    def __init__(self):
        self._setup_industry_mappings()
        self._setup_model_rationales()
    
    def _setup_industry_mappings(self):
        """Set up industry to model mappings based on financial characteristics."""
        
        # Banking and Financial Services - DDM preferred
        self.banking_keywords = {
            'Banking', 'Banks', 'Commercial Banks', 'Regional Banks',
            'Financial Services', 'Insurance', 'Asset Management',
            'Investment Banking', 'Credit Services', 'Mortgage Finance'
        }
        
        # Real Estate and Asset-Heavy - Asset-based preferred
        self.asset_heavy_keywords = {
            'REIT', 'Real Estate', 'Real Estate Investment Trust',
            'Utilities', 'Electric Utilities', 'Gas Utilities', 'Water Utilities',
            'Infrastructure', 'Pipelines', 'Telecommunications Infrastructure',
            'Power Generation', 'Energy Infrastructure'
        }
        
        # Technology and Growth - DCF preferred
        self.dcf_preferred_keywords = {
            'Technology', 'Software', 'Internet', 'E-commerce',
            'Biotechnology', 'Pharmaceuticals', 'Healthcare',
            'Consumer Discretionary', 'Consumer Staples',
            'Retail', 'Manufacturing', 'Industrial',
            'Media', 'Entertainment', 'Gaming'
        }
        
        # Indian specific sector mappings
        self.indian_sector_mappings = {
            'Private Sector Bank': ValuationModel.DDM,
            'Public Sector Bank': ValuationModel.DDM,
            'Foreign Bank': ValuationModel.DDM,
            'Non Banking Financial Company': ValuationModel.DDM,
            'Life Insurance': ValuationModel.DDM,
            'General Insurance': ValuationModel.DDM,
            'Information Technology': ValuationModel.DCF,
            'Software': ValuationModel.DCF,
            'Pharmaceuticals': ValuationModel.DCF,
            'Oil & Gas': ValuationModel.DCF,
            'Automobile': ValuationModel.DCF,
            'Cement': ValuationModel.ASSET,
            'Steel': ValuationModel.ASSET,
            'Power': ValuationModel.ASSET,
            'Infrastructure': ValuationModel.ASSET
        }
    
    def _setup_model_rationales(self):
        """Set up explanations for why each model is recommended."""
        
        self.model_rationales = {
            ValuationModel.DCF: {
                'description': 'Discounted Cash Flow (DCF) Model',
                'best_for': 'Companies with predictable free cash flows',
                'reasoning': 'DCF works well for businesses where operating cash flows are the primary value driver',
                'examples': 'Technology, Consumer, Healthcare, Industrial companies'
            },
            ValuationModel.DDM: {
                'description': 'Dividend Discount Model (DDM)',
                'best_for': 'Financial services and dividend-focused companies',
                'reasoning': 'Banks and financial firms are regulated and dividend-focused, making DDM more appropriate than FCF-based DCF',
                'examples': 'Commercial banks, Insurance companies, Asset managers'
            },
            ValuationModel.ASSET: {
                'description': 'Asset-Based Valuation',
                'best_for': 'Asset-heavy companies with substantial tangible assets',
                'reasoning': 'Companies with significant physical assets where book value and asset replacement cost matter',
                'examples': 'REITs, Utilities, Infrastructure, Cement, Steel companies'
            }
        }
    
    def classify_company(
        self, 
        ticker: str, 
        company_info: Dict[str, Any]
    ) -> Tuple[ValuationModel, str, float]:
        """
        Classify company and recommend appropriate valuation model.
        
        Args:
            ticker: Stock ticker symbol
            company_info: Company information from yfinance
            
        Returns:
            Tuple of (recommended_model, rationale, confidence_score)
        """
        
        try:
            sector = company_info.get('sector', '').strip()
            industry = company_info.get('industry', '').strip()
            
            logger.info(f"Classifying {ticker}: Sector='{sector}', Industry='{industry}'")
            
            # Priority 1: Check Indian-specific sector mappings
            if sector in self.indian_sector_mappings:
                model = self.indian_sector_mappings[sector]
                rationale = f"Indian {sector} companies typically use {model.value} model"
                confidence = 0.9
                return model, rationale, confidence
            
            # Priority 2: Check banking/financial keywords
            banking_match = self._check_keywords([sector, industry], self.banking_keywords)
            if banking_match:
                rationale = f"Financial services company ({banking_match}) - DDM accounts for regulatory requirements and dividend focus"
                return ValuationModel.DDM, rationale, 0.85
            
            # Priority 3: Check asset-heavy keywords  
            asset_match = self._check_keywords([sector, industry], self.asset_heavy_keywords)
            if asset_match:
                rationale = f"Asset-heavy company ({asset_match}) - Asset model reflects tangible asset value"
                return ValuationModel.ASSET, rationale, 0.80
            
            # Priority 4: Check DCF-preferred keywords
            dcf_match = self._check_keywords([sector, industry], self.dcf_preferred_keywords)
            if dcf_match:
                rationale = f"Cash flow generating business ({dcf_match}) - DCF captures operational value"
                return ValuationModel.DCF, rationale, 0.75
            
            # Default: Use DCF with lower confidence
            rationale = f"Default DCF model for {sector} sector - suitable for most businesses"
            return ValuationModel.DCF, rationale, 0.60
            
        except Exception as e:
            logger.error(f"Error classifying company {ticker}: {e}")
            return ValuationModel.DCF, "Default DCF model due to classification error", 0.50
    
    def _check_keywords(self, text_fields: List[str], keywords: set) -> Optional[str]:
        """Check if any keywords match in the text fields."""
        
        for text in text_fields:
            if not text:
                continue
            
            text_upper = text.upper()
            for keyword in keywords:
                if keyword.upper() in text_upper:
                    return keyword
        
        return None
    
    def get_model_info(self, model: ValuationModel) -> Dict[str, str]:
        """Get detailed information about a valuation model."""
        return self.model_rationales.get(model, {})

class MultiModelDCFService:
    """
    Multi-model DCF service supporting different valuation approaches
    based on company industry and characteristics.
    """
    
    def __init__(self):
        self.classifier = IndustryClassifier()
        self._setup_model_implementations()
    
    def _setup_model_implementations(self):
        """Initialize model-specific calculators."""
        
        # Default DCF parameters by industry
        self.default_assumptions = {
            ValuationModel.DCF: {
                'revenue_growth_rate': 8.0,
                'ebitda_margin': 15.0,
                'tax_rate': 25.0,
                'wacc': 12.0,
                'terminal_growth_rate': 3.0
            },
            ValuationModel.DDM: {
                'dividend_growth_rate': 6.0,
                'roe': 12.0,
                'payout_ratio': 0.4,
                'cost_of_equity': 11.0,
                'terminal_growth_rate': 3.0
            },
            ValuationModel.ASSET: {
                'book_value_growth': 5.0,
                'roe': 10.0,
                'asset_turnover': 0.8,
                'cost_of_equity': 12.0,
                'terminal_growth_rate': 3.0
            }
        }
    
    async def recommend_model_and_assumptions(
        self,
        ticker: str,
        company_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Recommend valuation model and provide default assumptions.
        
        Args:
            ticker: Stock ticker symbol
            company_data: Company financial data
            
        Returns:
            Dictionary with model recommendation and assumptions
        """
        
        try:
            company_info = company_data.get('info', {})
            
            # Classify company and get model recommendation
            recommended_model, rationale, confidence = self.classifier.classify_company(
                ticker, company_info
            )
            
            # Get model-specific information
            model_info = self.classifier.get_model_info(recommended_model)
            
            # Generate appropriate assumptions based on company data
            assumptions = await self._generate_model_assumptions(
                recommended_model, company_data
            )
            
            # Get alternative models for comparison
            alternative_models = self._get_alternative_models(recommended_model)
            
            return {
                'recommended_model': {
                    'model': recommended_model.value,
                    'rationale': rationale,
                    'confidence_score': confidence,
                    'model_info': model_info
                },
                'default_assumptions': assumptions,
                'alternative_models': alternative_models,
                'company_context': {
                    'ticker': ticker,
                    'sector': company_info.get('sector', 'Unknown'),
                    'industry': company_info.get('industry', 'Unknown'),
                    'market_cap': company_info.get('marketCap', 0),
                    'classification_timestamp': datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error in model recommendation for {ticker}: {e}")
            
            # Fallback to DCF
            return {
                'recommended_model': {
                    'model': 'DCF',
                    'rationale': 'Default DCF model due to classification error',
                    'confidence_score': 0.5,
                    'model_info': self.classifier.get_model_info(ValuationModel.DCF)
                },
                'default_assumptions': self.default_assumptions[ValuationModel.DCF],
                'alternative_models': ['DDM', 'Asset'],
                'company_context': {
                    'ticker': ticker,
                    'error': str(e)
                }
            }
    
    async def _generate_model_assumptions(
        self,
        model: ValuationModel,
        company_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate model-specific assumptions based on company data."""
        
        try:
            info = company_data.get('info', {})
            
            if model == ValuationModel.DCF:
                return await self._generate_dcf_assumptions(info)
            elif model == ValuationModel.DDM:
                return await self._generate_ddm_assumptions(info)
            elif model == ValuationModel.ASSET:
                return await self._generate_asset_assumptions(info)
            else:
                return self.default_assumptions[ValuationModel.DCF]
                
        except Exception as e:
            logger.error(f"Error generating assumptions for {model}: {e}")
            return self.default_assumptions.get(model, self.default_assumptions[ValuationModel.DCF])
    
    async def _generate_dcf_assumptions(self, info: Dict[str, Any]) -> Dict[str, Any]:
        """Generate DCF-specific assumptions."""
        
        # Extract relevant metrics for DCF
        revenue_growth = self._estimate_revenue_growth(info)
        ebitda_margin = self._estimate_ebitda_margin(info)
        wacc = self._estimate_wacc(info)
        
        return {
            'revenue_growth_rate': revenue_growth,
            'ebitda_margin': ebitda_margin, 
            'tax_rate': 25.0,  # Standard Indian corporate tax
            'wacc': wacc,
            'terminal_growth_rate': 3.0,  # Long-term GDP growth
            'projection_years': 5
        }
    
    async def _generate_ddm_assumptions(self, info: Dict[str, Any]) -> Dict[str, Any]:
        """Generate DDM-specific assumptions for banking companies."""
        
        # Banking-specific metrics
        dividend_yield = info.get('dividendYield', 0.02) * 100  # Convert to percentage
        roe = info.get('returnOnEquity', 0.12) * 100 if info.get('returnOnEquity') else 12.0
        payout_ratio = min(dividend_yield / (roe if roe > 0 else 12.0), 0.6) if roe > 0 else 0.4
        
        # Cost of equity using CAPM approximation
        beta = info.get('beta', 1.0)
        risk_free_rate = 6.8  # Current 10-year G-sec rate
        market_premium = 6.0  # Indian equity risk premium
        cost_of_equity = risk_free_rate + (beta * market_premium)
        
        return {
            'dividend_growth_rate': min(roe * (1 - payout_ratio), 15.0),  # Sustainable growth
            'roe': roe,
            'payout_ratio': payout_ratio,
            'cost_of_equity': cost_of_equity,
            'terminal_growth_rate': 3.0,
            'current_dividend_yield': dividend_yield
        }
    
    async def _generate_asset_assumptions(self, info: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Asset-based assumptions for asset-heavy companies."""
        
        # Asset-heavy company metrics
        book_value = info.get('bookValue', 100)
        price_to_book = info.get('priceToBook', 1.5)
        roe = info.get('returnOnEquity', 0.10) * 100 if info.get('returnOnEquity') else 10.0
        asset_turnover = info.get('totalRevenue', 0) / info.get('totalAssets', 1) if info.get('totalAssets') else 0.8
        
        return {
            'book_value_growth': min(roe * 0.6, 8.0),  # Conservative reinvestment
            'roe': roe,
            'asset_turnover': asset_turnover,
            'cost_of_equity': 12.0,  # Higher for asset-heavy companies
            'terminal_growth_rate': 3.0,
            'current_book_value': book_value,
            'current_ptb_ratio': price_to_book
        }
    
    def _estimate_revenue_growth(self, info: Dict[str, Any]) -> float:
        """Estimate reasonable revenue growth based on company metrics."""
        
        try:
            # Use revenue growth rate if available
            quarterly_revenue_growth = info.get('quarterlyRevenueGrowth', 0)
            if quarterly_revenue_growth and quarterly_revenue_growth > -0.5:  # Sanity check
                return min(abs(quarterly_revenue_growth) * 100, 20.0)
            
            # Fallback based on company size (smaller companies typically grow faster)
            market_cap = info.get('marketCap', 0)
            if market_cap > 1e12:  # Large cap (>1T)
                return 6.0
            elif market_cap > 1e11:  # Mid cap (>100B)
                return 8.0
            else:  # Small cap
                return 10.0
                
        except:
            return 8.0  # Conservative default
    
    def _estimate_ebitda_margin(self, info: Dict[str, Any]) -> float:
        """Estimate EBITDA margin based on available metrics."""
        
        try:
            # Use profit margin as proxy if available
            profit_margin = info.get('profitMargins', 0)
            if profit_margin and profit_margin > 0:
                # EBITDA margin typically 1.5-2x profit margin
                ebitda_margin = min(profit_margin * 1.8 * 100, 30.0)
                return max(ebitda_margin, 10.0)  # Minimum 10%
            
            # Industry defaults
            sector = info.get('sector', '').lower()
            if 'technology' in sector or 'software' in sector:
                return 20.0
            elif 'banking' in sector or 'financial' in sector:
                return 25.0  # NIM for banks
            else:
                return 15.0
                
        except:
            return 15.0  # Conservative default
    
    def _estimate_wacc(self, info: Dict[str, Any]) -> float:
        """Estimate WACC based on company characteristics."""
        
        try:
            # Use beta for cost of equity calculation
            beta = info.get('beta', 1.0)
            risk_free_rate = 6.8  # 10-year G-sec
            market_premium = 6.0  # India equity risk premium
            
            cost_of_equity = risk_free_rate + (beta * market_premium)
            
            # Assume debt ratio and cost of debt
            debt_ratio = 0.3  # Conservative assumption
            cost_of_debt = 8.0  # Corporate lending rate
            tax_rate = 0.25
            
            wacc = (cost_of_equity * (1 - debt_ratio)) + (cost_of_debt * debt_ratio * (1 - tax_rate))
            
            return min(max(wacc, 8.0), 16.0)  # Clamp between 8-16%
            
        except:
            return 12.0  # Market average
    
    def _get_alternative_models(self, primary_model: ValuationModel) -> List[str]:
        """Get alternative models for comparison."""
        
        all_models = [model.value for model in ValuationModel]
        alternatives = [model for model in all_models if model != primary_model.value]
        return alternatives[:2]  # Return top 2 alternatives
    
    async def calculate_multi_model_valuation(
        self,
        ticker: str,
        company_data: Dict[str, Any],
        user_model_preference: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Calculate valuation using multiple models for comparison.
        
        Args:
            ticker: Stock ticker symbol
            company_data: Company financial data
            user_model_preference: User's preferred model (optional)
            
        Returns:
            Multi-model valuation results with recommendations
        """
        
        try:
            # Get model recommendation
            model_recommendation = await self.recommend_model_and_assumptions(ticker, company_data)
            
            # Use user preference if provided and valid
            primary_model = user_model_preference or model_recommendation['recommended_model']['model']
            
            # Calculate valuations for multiple models
            valuations = {}
            
            for model_name in [primary_model] + model_recommendation['alternative_models']:
                try:
                    if model_name == 'DCF':
                        valuation = await self._calculate_dcf_valuation(company_data)
                    elif model_name == 'DDM':
                        valuation = await self._calculate_ddm_valuation(company_data)
                    elif model_name == 'Asset':
                        valuation = await self._calculate_asset_valuation(company_data)
                    else:
                        continue
                    
                    valuations[model_name] = valuation
                    
                except Exception as e:
                    logger.error(f"Error calculating {model_name} valuation for {ticker}: {e}")
                    valuations[model_name] = {'error': str(e)}
            
            return {
                'ticker': ticker,
                'model_recommendation': model_recommendation,
                'valuations': valuations,
                'primary_model': primary_model,
                'valuation_summary': self._create_valuation_summary(valuations, primary_model),
                'calculation_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in multi-model valuation for {ticker}: {e}")
            return {
                'ticker': ticker,
                'error': str(e),
                'fallback': 'DCF model calculation recommended'
            }
    
    async def _calculate_dcf_valuation(self, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate traditional DCF valuation."""
        
        # This would integrate with existing DCF calculation logic
        # For now, return structure that matches expected format
        info = company_data.get('info', {})
        current_price = info.get('currentPrice', info.get('regularMarketPrice', 100))
        
        return {
            'model': 'DCF',
            'intrinsic_value': current_price * 1.1,  # Placeholder calculation
            'current_price': current_price,
            'upside_downside': 10.0,
            'confidence': 'medium',
            'key_assumptions': {
                'revenue_growth': '8.0%',
                'ebitda_margin': '15.0%',
                'wacc': '12.0%'
            }
        }
    
    async def _calculate_ddm_valuation(self, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate Dividend Discount Model valuation for banking companies."""
        
        info = company_data.get('info', {})
        current_price = info.get('currentPrice', info.get('regularMarketPrice', 100))
        dividend_yield = info.get('dividendYield', 0.02)
        
        # Simplified DDM calculation: D1 / (r - g)
        # D1 = next year dividend, r = cost of equity, g = growth rate
        current_dividend = current_price * dividend_yield
        growth_rate = 0.06  # 6% dividend growth assumption
        cost_of_equity = 0.11  # 11% cost of equity
        
        if cost_of_equity > growth_rate:
            intrinsic_value = (current_dividend * (1 + growth_rate)) / (cost_of_equity - growth_rate)
        else:
            intrinsic_value = current_price  # Fallback if growth > cost of equity
        
        return {
            'model': 'DDM',
            'intrinsic_value': intrinsic_value,
            'current_price': current_price,
            'upside_downside': ((intrinsic_value - current_price) / current_price) * 100,
            'confidence': 'high',
            'key_assumptions': {
                'dividend_growth': '6.0%',
                'cost_of_equity': '11.0%',
                'current_yield': f'{dividend_yield:.1%}'
            }
        }
    
    async def _calculate_asset_valuation(self, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate Asset-based valuation for asset-heavy companies."""
        
        info = company_data.get('info', {})
        current_price = info.get('currentPrice', info.get('regularMarketPrice', 100))
        book_value = info.get('bookValue', current_price * 0.8)
        price_to_book = info.get('priceToBook', 1.2)
        
        # Asset-based approach: Adjusted book value
        asset_multiplier = 1.1  # 10% premium to book value for going concern
        intrinsic_value = book_value * asset_multiplier
        
        return {
            'model': 'Asset',
            'intrinsic_value': intrinsic_value,
            'current_price': current_price,
            'upside_downside': ((intrinsic_value - current_price) / current_price) * 100,
            'confidence': 'medium',
            'key_assumptions': {
                'book_value': f'₹{book_value:.0f}',
                'asset_premium': '10%',
                'current_ptb': f'{price_to_book:.1f}x'
            }
        }
    
    def _create_valuation_summary(
        self, 
        valuations: Dict[str, Any], 
        primary_model: str
    ) -> Dict[str, Any]:
        """Create summary comparing different valuation models."""
        
        try:
            # Extract intrinsic values
            values = {}
            for model, valuation in valuations.items():
                if 'intrinsic_value' in valuation:
                    values[model] = valuation['intrinsic_value']
            
            if not values:
                return {'error': 'No valid valuations calculated'}
            
            # Calculate statistics
            min_value = min(values.values())
            max_value = max(values.values())
            avg_value = sum(values.values()) / len(values)
            
            # Get current price
            primary_valuation = valuations.get(primary_model, {})
            current_price = primary_valuation.get('current_price', 100)
            
            return {
                'valuation_range': {
                    'min': min_value,
                    'max': max_value,
                    'average': avg_value,
                    'spread_percentage': ((max_value - min_value) / avg_value) * 100
                },
                'primary_model_result': {
                    'model': primary_model,
                    'intrinsic_value': primary_valuation.get('intrinsic_value', 0),
                    'upside_downside': primary_valuation.get('upside_downside', 0)
                },
                'consensus': {
                    'recommendation': self._get_consensus_recommendation(avg_value, current_price),
                    'confidence': self._calculate_consensus_confidence(values)
                }
            }
            
        except Exception as e:
            logger.error(f"Error creating valuation summary: {e}")
            return {'error': 'Could not create valuation summary'}
    
    def _get_consensus_recommendation(self, avg_intrinsic_value: float, current_price: float) -> str:
        """Get consensus recommendation based on average intrinsic value."""
        
        upside = ((avg_intrinsic_value - current_price) / current_price) * 100
        
        if upside > 20:
            return 'Strong Buy'
        elif upside > 10:
            return 'Buy'
        elif upside > -10:
            return 'Hold'
        elif upside > -20:
            return 'Sell'
        else:
            return 'Strong Sell'
    
    def _calculate_consensus_confidence(self, values: Dict[str, float]) -> str:
        """Calculate confidence based on valuation consistency."""
        
        if len(values) < 2:
            return 'low'
        
        avg_value = sum(values.values()) / len(values)
        variance = sum((v - avg_value) ** 2 for v in values.values()) / len(values)
        coefficient_of_variation = (variance ** 0.5) / avg_value
        
        if coefficient_of_variation < 0.15:
            return 'high'
        elif coefficient_of_variation < 0.30:
            return 'medium'
        else:
            return 'low'

class MultiStageGrowthEngine:
    """
    10-Year Multi-Stage Growth Engine for EquityScope v2.0
    
    Implements both Simple Mode and Agentic Mode with GDP blending:
    - Years 1-2: Company-specific growth (historical/AI-guided)
    - Years 3-5: Industry fade towards market
    - Years 6-8: Competitive convergence  
    - Years 9-10: GDP convergence (3% India nominal)
    - Terminal: GDP growth (3%)
    """
    
    def __init__(self):
        self.gdp_growth_rate = 3.0  # India nominal GDP growth
        self.default_projection_years = 10
        
        # Define growth stage templates
        self.growth_stage_templates = {
            'simple_mode': [
                {'years': '1-2', 'start': 1, 'end': 2, 'gdp_weight': 0.2, 'method': 'historical_cagr'},
                {'years': '3-5', 'start': 3, 'end': 5, 'gdp_weight': 0.5, 'method': 'industry_fade'},
                {'years': '6-8', 'start': 6, 'end': 8, 'gdp_weight': 0.75, 'method': 'competitive_convergence'},
                {'years': '9-10', 'start': 9, 'end': 10, 'gdp_weight': 1.0, 'method': 'gdp_convergence'},
            ],
            'agentic_mode': [
                {'years': '1-2', 'start': 1, 'end': 2, 'gdp_weight': 0.1, 'method': 'management_guidance'},
                {'years': '3-5', 'start': 3, 'end': 5, 'gdp_weight': 0.3, 'method': 'capacity_expansion'},
                {'years': '6-8', 'start': 6, 'end': 8, 'gdp_weight': 0.6, 'method': 'market_saturation'},
                {'years': '9-10', 'start': 9, 'end': 10, 'gdp_weight': 1.0, 'method': 'gdp_convergence'},
            ]
        }
    
    async def generate_multi_stage_assumptions(
        self,
        mode: DCFMode,
        ticker: str,
        company_data: Dict[str, Any],
        ai_analysis: Optional[Dict[str, Any]] = None
    ) -> MultiStageAssumptions:
        """
        Generate multi-stage DCF assumptions based on mode.
        
        Args:
            mode: Simple or Agentic mode
            ticker: Stock ticker symbol
            company_data: Company financial data
            ai_analysis: AI analysis results (for Agentic mode)
            
        Returns:
            MultiStageAssumptions with 10-year growth stages
        """
        
        try:
            if mode == DCFMode.SIMPLE:
                return await self._generate_simple_mode_assumptions(ticker, company_data)
            else:
                return await self._generate_agentic_mode_assumptions(ticker, company_data, ai_analysis)
                
        except Exception as e:
            logger.error(f"Error generating multi-stage assumptions for {ticker}: {e}")
            return await self._generate_fallback_assumptions(ticker, company_data)
    
    async def _generate_simple_mode_assumptions(
        self,
        ticker: str,
        company_data: Dict[str, Any]
    ) -> MultiStageAssumptions:
        """Generate Simple Mode assumptions with enhanced historical validation."""
        
        info = company_data.get('info', {})
        
        # Get enhanced historical growth analysis
        historical_analysis = await self._get_historical_growth_rate_enhanced(
            ticker, company_data, DCFMode.SIMPLE
        )
        
        # Use stage recommendations from enhanced historical analysis if available
        if historical_analysis.get('stage_recommendations'):
            growth_stages = []
            for stage_rec in historical_analysis['stage_recommendations']:
                stage = GrowthStage(
                    years=stage_rec['years'],
                    start_year=int(stage_rec['years'].split('-')[0]),
                    end_year=int(stage_rec['years'].split('-')[1]) if '-' in stage_rec['years'] else int(stage_rec['years']),
                    growth_rate=stage_rec['recommended_rate'],
                    method=stage_rec['methodology'],
                    gdp_weight=stage_rec.get('gdp_component', 0) / stage_rec['recommended_rate'] if stage_rec['recommended_rate'] != 0 else 0,
                    confidence=stage_rec['confidence'],
                    rationale=stage_rec['rationale']
                )
                growth_stages.append(stage)
        else:
            # Fallback to template-based generation
            base_growth_rate = historical_analysis['base_growth_rate']
            growth_stages = []
            templates = self.growth_stage_templates['simple_mode']
            
            for template in templates:
                # Calculate blended growth rate
                if template['gdp_weight'] == 1.0:
                    # Pure GDP growth
                    growth_rate = self.gdp_growth_rate
                    confidence = "high"
                    rationale = "Long-term GDP convergence"
                else:
                    # Blend historical growth with GDP
                    gdp_weight = template['gdp_weight']
                    historical_weight = 1.0 - gdp_weight
                    growth_rate = (base_growth_rate * historical_weight) + (self.gdp_growth_rate * gdp_weight)
                    
                    # Adjust confidence based on data reliability
                    reliability = historical_analysis.get('growth_reliability', 0.5)
                    if reliability > 0.8:
                        confidence = "high"
                    elif reliability > 0.6:
                        confidence = "medium"
                    else:
                        confidence = "low"
                    
                    rationale = f"Historical growth ({base_growth_rate:.1f}%) blended with GDP ({self.gdp_growth_rate:.1f}%) at {gdp_weight:.0%} weight"
                
                stage = GrowthStage(
                    years=template['years'],
                    start_year=template['start'],
                    end_year=template['end'],
                    growth_rate=round(growth_rate, 1),
                    method=template['method'],
                    gdp_weight=template['gdp_weight'],
                    confidence=confidence,
                    rationale=rationale
                )
                growth_stages.append(stage)
        
        # Get other DCF parameters
        ebitda_margin = self._estimate_ebitda_margin_simple(info)
        wacc = self._estimate_wacc_simple(info)
        
        return MultiStageAssumptions(
            mode=DCFMode.SIMPLE,
            projection_years=self.default_projection_years,
            growth_stages=growth_stages,
            ebitda_margin=ebitda_margin,
            tax_rate=25.0,  # Indian corporate tax
            wacc=wacc,
            terminal_growth_rate=self.gdp_growth_rate,
            gdp_growth_rate=self.gdp_growth_rate
        )
    
    async def _generate_agentic_mode_assumptions(
        self,
        ticker: str,
        company_data: Dict[str, Any],
        ai_analysis: Optional[Dict[str, Any]]
    ) -> MultiStageAssumptions:
        """Generate Agentic Mode assumptions with AI-enhanced insights."""
        
        info = company_data.get('info', {})
        
        # Extract AI insights if available
        ai_growth_insights = self._extract_ai_growth_insights(ai_analysis) if ai_analysis else {}
        
        # Get base growth parameters
        base_growth_rate = self._get_historical_growth_rate(info)
        management_guidance = ai_growth_insights.get('management_guidance', base_growth_rate)
        
        # Generate AI-enhanced growth stages
        growth_stages = []
        templates = self.growth_stage_templates['agentic_mode']
        
        for i, template in enumerate(templates):
            if template['method'] == 'management_guidance':
                # Use AI-extracted management guidance
                growth_rate = management_guidance
                confidence = "high" if ai_analysis else "medium"
                rationale = "Management guidance from earnings calls and investor presentations" if ai_analysis else "Historical growth rate (AI analysis unavailable)"
            
            elif template['method'] == 'capacity_expansion':
                # AI analysis of capacity expansion plans
                capacity_factor = ai_growth_insights.get('capacity_expansion_factor', 0.8)
                growth_rate = management_guidance * capacity_factor
                confidence = "medium"
                rationale = "Capacity expansion analysis and competitive positioning"
            
            elif template['method'] == 'market_saturation':
                # Market saturation and competitive pressure analysis
                saturation_factor = ai_growth_insights.get('market_saturation_factor', 0.6)
                blended_rate = (base_growth_rate * saturation_factor) + (self.gdp_growth_rate * template['gdp_weight'])
                growth_rate = blended_rate
                confidence = "medium"
                rationale = "Market saturation modeling with competitive pressure"
            
            else:  # gdp_convergence
                growth_rate = self.gdp_growth_rate
                confidence = "high"
                rationale = "Long-term GDP convergence"
            
            stage = GrowthStage(
                years=template['years'],
                start_year=template['start'],
                end_year=template['end'],
                growth_rate=round(growth_rate, 1),
                method=template['method'],
                gdp_weight=template['gdp_weight'],
                confidence=confidence,
                rationale=rationale
            )
            growth_stages.append(stage)
        
        # Enhanced DCF parameters with AI insights
        ebitda_margin = self._estimate_ebitda_margin_agentic(info, ai_analysis)
        wacc = self._estimate_wacc_agentic(info, ai_analysis)
        
        return MultiStageAssumptions(
            mode=DCFMode.AGENTIC,
            projection_years=self.default_projection_years,
            growth_stages=growth_stages,
            ebitda_margin=ebitda_margin,
            tax_rate=25.0,
            wacc=wacc,
            terminal_growth_rate=self.gdp_growth_rate,
            gdp_growth_rate=self.gdp_growth_rate
        )
    
    async def _generate_fallback_assumptions(
        self,
        ticker: str,
        company_data: Dict[str, Any]
    ) -> MultiStageAssumptions:
        """Generate conservative fallback assumptions."""
        
        # Use simple conservative growth pattern
        growth_stages = [
            GrowthStage(
                years="1-2", start_year=1, end_year=2, growth_rate=6.0,
                method="conservative_estimate", gdp_weight=0.3, confidence="low",
                rationale="Conservative estimate due to insufficient data"
            ),
            GrowthStage(
                years="3-5", start_year=3, end_year=5, growth_rate=4.5,
                method="market_average", gdp_weight=0.5, confidence="medium",
                rationale="Market average with GDP blending"
            ),
            GrowthStage(
                years="6-8", start_year=6, end_year=8, growth_rate=3.5,
                method="gdp_convergence", gdp_weight=0.8, confidence="high",
                rationale="GDP convergence transition"
            ),
            GrowthStage(
                years="9-10", start_year=9, end_year=10, growth_rate=3.0,
                method="gdp_convergence", gdp_weight=1.0, confidence="high",
                rationale="Long-term GDP growth"
            )
        ]
        
        return MultiStageAssumptions(
            mode=DCFMode.SIMPLE,
            projection_years=self.default_projection_years,
            growth_stages=growth_stages,
            ebitda_margin=15.0,
            tax_rate=25.0,
            wacc=12.0,
            terminal_growth_rate=self.gdp_growth_rate,
            gdp_growth_rate=self.gdp_growth_rate
        )
    
    async def _get_historical_growth_rate_enhanced(
        self, 
        ticker: str, 
        company_data: Dict[str, Any], 
        mode: DCFMode
    ) -> Dict[str, Any]:
        """
        Enhanced historical growth rate analysis using Historical Validation Service.
        
        This replaces the basic _get_historical_growth_rate with sophisticated
        multi-period CAGR analysis as specified in the DCF Flow requirements.
        """
        
        try:
            # Use enhanced historical validation service
            validation_result = await historical_validation_service.generate_multi_stage_historical_validation(
                ticker=ticker,
                mode=mode,
                company_data=company_data
            )
            
            if validation_result.get('multi_period_growth_analysis', {}).get('insufficient_data'):
                logger.warning(f"Insufficient data for {ticker}, using conservative growth estimates")
                return self._get_conservative_growth_fallback(company_data.get('info', {}))
            
            growth_analysis = validation_result['multi_period_growth_analysis']
            
            return {
                'base_growth_rate': growth_analysis['recommended_base_growth'],
                'growth_reliability': validation_result['validation_confidence'],
                'multi_period_analysis': growth_analysis['multi_period_cagr'],
                'gdp_blending_recommendations': growth_analysis['gdp_blending_recommendations'],
                'educational_context': validation_result.get('educational_insights', {}),
                'data_quality': validation_result.get('data_quality_metrics', {}),
                'stage_recommendations': validation_result.get('growth_stage_recommendations', [])
            }
            
        except Exception as e:
            logger.error(f"Error in enhanced historical growth analysis for {ticker}: {e}")
            return self._get_conservative_growth_fallback(company_data.get('info', {}))
    
    def _get_conservative_growth_fallback(self, info: Dict[str, Any]) -> Dict[str, Any]:
        """Conservative fallback when enhanced analysis fails."""
        
        quarterly_growth = info.get('quarterlyRevenueGrowth', 0)
        if quarterly_growth and abs(quarterly_growth) < 0.5:
            base_rate = min(abs(quarterly_growth) * 100, 25.0)
        else:
            # Market cap based fallback
            market_cap = info.get('marketCap', 0)
            if market_cap > 1e12:
                base_rate = 8.0  # Large cap
            elif market_cap > 1e11:
                base_rate = 10.0  # Mid cap
            else:
                base_rate = 12.0  # Small cap
        
        return {
            'base_growth_rate': base_rate,
            'growth_reliability': 0.4,
            'fallback_used': True,
            'rationale': 'Conservative estimate due to data limitations'
        }
    
    def _extract_ai_growth_insights(self, ai_analysis: Dict[str, Any]) -> Dict[str, float]:
        """Extract growth insights from AI analysis."""
        
        # This will be enhanced when we connect AI agents
        insights = {}
        
        # Look for management guidance in AI analysis
        if 'growth_analysis' in ai_analysis:
            growth_data = ai_analysis['growth_analysis']
            insights['management_guidance'] = growth_data.get('management_guidance', 8.0)
            insights['capacity_expansion_factor'] = growth_data.get('capacity_expansion_factor', 0.8)
            insights['market_saturation_factor'] = growth_data.get('market_saturation_factor', 0.6)
        
        return insights
    
    def _estimate_ebitda_margin_simple(self, info: Dict[str, Any]) -> float:
        """Estimate EBITDA margin for Simple Mode."""
        
        # Enhanced version will use historical_validation.py
        profit_margin = info.get('profitMargins', 0)
        if profit_margin and profit_margin > 0:
            return min(profit_margin * 1.8 * 100, 30.0)
        
        sector = info.get('sector', '').lower()
        if 'technology' in sector:
            return 20.0
        elif 'banking' in sector:
            return 25.0
        else:
            return 15.0
    
    def _estimate_ebitda_margin_agentic(self, info: Dict[str, Any], ai_analysis: Optional[Dict[str, Any]]) -> float:
        """Estimate EBITDA margin for Agentic Mode with AI insights."""
        
        base_margin = self._estimate_ebitda_margin_simple(info)
        
        if ai_analysis and 'margin_analysis' in ai_analysis:
            margin_insights = ai_analysis['margin_analysis']
            margin_adjustment = margin_insights.get('margin_expansion_potential', 0)
            return min(base_margin + margin_adjustment, 35.0)
        
        return base_margin
    
    def _estimate_wacc_simple(self, info: Dict[str, Any]) -> float:
        """Estimate WACC for Simple Mode."""
        
        beta = info.get('beta', 1.0)
        risk_free_rate = 6.8  # Will be made dynamic with live G-sec rates
        market_premium = 6.0
        cost_of_equity = risk_free_rate + (beta * market_premium)
        
        # Simple WACC calculation
        wacc = (cost_of_equity * 0.7) + (8.0 * 0.3 * 0.75)
        return min(max(wacc, 8.0), 16.0)
    
    def _estimate_wacc_agentic(self, info: Dict[str, Any], ai_analysis: Optional[Dict[str, Any]]) -> float:
        """Estimate WACC for Agentic Mode with risk adjustments."""
        
        base_wacc = self._estimate_wacc_simple(info)
        
        if ai_analysis and 'risk_analysis' in ai_analysis:
            risk_insights = ai_analysis['risk_analysis']
            risk_premium = risk_insights.get('specific_risk_premium', 0)
            return min(base_wacc + risk_premium, 18.0)
        
        return base_wacc

# Global service instances
multi_model_dcf_service = MultiModelDCFService()
multi_stage_growth_engine = MultiStageGrowthEngine()