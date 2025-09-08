# Sector-Specific DCF Service
# Main orchestrator for sector-aware DCF calculations as per v3 implementation plan

import logging
from typing import Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime

from .sector_dcf.banking_dcf import BankingDCFCalculator, BankingMetrics
from .sector_dcf.pharma_dcf import PharmaDCFCalculator, PharmaMetrics
from .sector_dcf.realestate_dcf import RealEstateDCFCalculator, RealEstateMetrics
from .dcf_service import DCFService
from .intelligent_cache import intelligent_cache, CacheType
from ..models.dcf import FinancialData, DCFAssumptions
from .enhanced_data_service import EnhancedDataService

logger = logging.getLogger(__name__)

@dataclass
class SectorDCFResult:
    """Result of sector-specific DCF calculation"""
    ticker: str
    sector: str
    fair_value: float
    current_price: float
    upside_downside_pct: float
    dcf_method: str
    confidence: float
    sector_rules: Dict
    calculation_timestamp: datetime

class SectorDCFService:
    """
    Main orchestrator for sector-specific DCF calculations
    
    Supported Sectors:
    - BFSI: Excess Return Model
    - Pharma: DCF + EV/EBITDA hybrid  
    - Real Estate: NAV-based valuation
    - IT/FMCG/Energy: Generic DCF model
    """
    
    def __init__(self, use_cache: bool = True):
        # Initialize sector-specific calculators
        self.use_cache = use_cache
        self.cache_manager = intelligent_cache
        
        self.calculators = {
            "BFSI": BankingDCFCalculator(),
            "Pharma": PharmaDCFCalculator(), 
            "Real Estate": RealEstateDCFCalculator(),
            "IT": DCFService(),  # Generic DCF for IT
            "FMCG": DCFService(),  # Generic DCF for FMCG
            "Energy": DCFService()  # Generic DCF for Energy
        }
        
        # Sector mappings for company classification
        self.sector_mappings = {
            "BFSI": ["HDFCBANK", "SBIN", "ICICIBANK", "AXISBANK", "KOTAKBANK", 
                    "INDUSINDBK", "FEDERALBNK", "BANKBARODA", "PNB", "CANBK"],
            "PHARMA": ["SUNPHARMA", "DRREDDY", "CIPLA", "LUPIN", "AUROPHARMA",
                      "DIVISLAB", "BIOCON", "CADILAHC", "TORNTPHARM", "GLENMARK"],
            "REALESTATE": ["DLF", "GODREJPROP", "OBEROIRLTY", "PRESTIGE", "BRIGADE",
                          "SOBHA", "PHOENIXLTD", "MAHLIFE", "KOLTEPATIL"],
            "IT": ["TCS", "INFY", "WIPRO", "HCLTECH", "TECHM", "LTI", "MINDTREE",
                  "MPHASIS", "LTTS", "COFORGE"],
            "FMCG": ["HINDUNILVR", "ITC", "NESTLEIND", "BRITANNIA", "DABUR",
                    "GODREJCP", "MARICO", "VBL", "TATACONSUM", "EMAMILTD"],
            "ENERGY": ["RELIANCE", "ONGC", "IOC", "BPCL", "GAIL", "HINDPETRO",
                      "MGL", "IGL", "PETRONET", "ADANIGAS"]
        }
    
    def classify_sector(self, ticker: str) -> str:
        """
        Classify company sector based on ticker symbol
        
        Args:
            ticker: Stock ticker symbol (with or without .NS suffix)
        
        Returns:
            Sector name or "IT" as default
        """
        # Clean ticker (remove .NS suffix if present)
        clean_ticker = ticker.replace('.NS', '').upper()
        
        for sector, tickers in self.sector_mappings.items():
            if clean_ticker in tickers:
                logger.info(f"Classified {ticker} as {sector} sector")
                return sector
        
        # Default to IT sector for unknown companies
        logger.info(f"Unknown ticker {ticker}, defaulting to IT sector")
        return "IT"
    
    async def calculate_sector_dcf(
        self, 
        ticker: str, 
        sector: str, 
        mode: str,
        company_data: Dict = None,
        force_refresh: bool = False
    ) -> SectorDCFResult:
        """
        Calculate sector-specific DCF based on company sector with intelligent caching
        
        Args:
            ticker: Stock ticker symbol
            sector: Sector classification
            mode: Analysis mode ("simple" or "agentic")
            company_data: Company financial data
            force_refresh: Skip cache and force fresh calculation
        
        Returns:
            SectorDCFResult with valuation and sector insights
        """
        
        # Check cache first (unless force refresh)
        if self.use_cache and not force_refresh:
            cached_result = await self._get_cached_dcf(ticker, sector, mode)
            if cached_result:
                logger.info(f"Cache hit for {ticker} {sector} DCF calculation")
                return cached_result
        try:
            logger.info(f"Calculating {sector} sector DCF for {ticker} in {mode} mode")
            
            # Get sector-specific calculator
            calculator = self.calculators.get(sector, self.calculators["IT"])
            current_price = company_data.get("current_price", 0) if company_data else 0
            
            # Calculate based on sector
            if sector == "BFSI":
                result = await self._calculate_banking_dcf(ticker, company_data, calculator)
            elif sector == "PHARMA":
                result = await self._calculate_pharma_dcf(ticker, company_data, calculator)
            elif sector == "REALESTATE":
                result = await self._calculate_realestate_dcf(ticker, company_data, calculator)
            else:
                # Generic DCF for IT/FMCG/Energy
                result = await self._calculate_generic_dcf(ticker, company_data, calculator)
            
            # Calculate upside/downside
            upside_pct = 0.0
            if current_price > 0 and result.get("fair_value", 0) > 0:
                upside_pct = ((result["fair_value"] - current_price) / current_price) * 100
            
            # Get sector-specific rules
            sector_rules = self._get_sector_rules(sector)
            
            sector_result = SectorDCFResult(
                ticker=ticker,
                sector=sector,
                fair_value=result.get("fair_value", 0),
                current_price=current_price,
                upside_downside_pct=upside_pct,
                dcf_method=result.get("method", f"{sector}_DCF"),
                confidence=result.get("confidence", 0.7),
                sector_rules=sector_rules,
                calculation_timestamp=datetime.now()
            )
            
            # Cache the result
            if self.use_cache:
                await self._cache_dcf_result(ticker, sector, mode, sector_result)
            
            return sector_result
            
        except Exception as e:
            logger.error(f"Sector DCF calculation failed for {ticker}: {e}")
            # Return fallback result (don't cache failures)
            return SectorDCFResult(
                ticker=ticker,
                sector=sector,
                fair_value=0,
                current_price=current_price,
                upside_downside_pct=0,
                dcf_method="Fallback",
                confidence=0.3,
                sector_rules={},
                calculation_timestamp=datetime.now()
            )
    
    async def _calculate_banking_dcf(self, ticker: str, company_data: Dict, calculator) -> Dict:
        """Calculate banking DCF using Excess Return Model"""
        try:
            info = company_data.get("info", {}) if company_data else {}
            
            # Create banking metrics from company data
            banking_metrics = BankingMetrics(
                net_interest_margin=info.get("netInterestMargin", 0.03),
                return_on_assets=info.get("returnOnAssets", 0.01),
                return_on_equity=info.get("returnOnEquity", 0.12),
                cost_to_income=info.get("costToIncome", 0.50),
                gnpa_ratio=info.get("gnpaRatio", 0.03),
                provision_coverage=info.get("provisionCoverage", 0.75),
                credit_growth=info.get("creditGrowth", 0.10),
                casa_ratio=info.get("casaRatio", 0.40),
                capital_adequacy=info.get("capitalAdequacy", 0.15),
                book_value_per_share=info.get("bookValue", 100),
                tangible_book_value=info.get("tangibleBookValue", 95)
            )
            
            result = await calculator.calculate_fair_value(ticker, banking_metrics)
            return {
                "fair_value": result.fair_value_per_share,
                "method": "Excess_Return_Model",
                "confidence": result.confidence
            }
            
        except Exception as e:
            logger.warning(f"Banking DCF failed for {ticker}: {e}")
            return {"fair_value": 0, "method": "Banking_DCF_Failed", "confidence": 0.3}
    
    async def _calculate_pharma_dcf(self, ticker: str, company_data: Dict, calculator) -> Dict:
        """Calculate pharma DCF using hybrid model"""
        try:
            info = company_data.get("info", {}) if company_data else {}
            
            # Create pharma metrics from company data
            pharma_metrics = PharmaMetrics(
                revenue=info.get("totalRevenue", 1000000000),
                ebitda=info.get("ebitda", 200000000),
                ebitda_margin=info.get("ebitdaMargins", 0.20),
                rd_expense=info.get("rdExpense", 80000000),
                rd_percentage=info.get("rdPercentage", 0.08),
                free_cash_flow=info.get("freeCashflow", 150000000),
                working_capital=info.get("workingCapital", 50000000),
                capex=info.get("capitalExpenditures", 30000000),
                us_revenue_percentage=info.get("usRevenuePercentage", 0.40),
                domestic_revenue_percentage=info.get("domesticRevenuePercentage", 0.35),
                anda_filings=info.get("andaFilings", 15),
                dmf_filings=info.get("dmfFilings", 8),
                usfda_observations=info.get("usfda_observations", 2),
                patent_expiry_risk=info.get("patentExpiryRisk", 0.15),
                shares_outstanding=info.get("sharesOutstanding", 10000000),
                market_cap=info.get("marketCap", 5000000000),
                enterprise_value=info.get("enterpriseValue", 4800000000),
                current_price=company_data.get("current_price", 500)
            )
            
            result = await calculator.calculate_fair_value(ticker, pharma_metrics)
            return {
                "fair_value": result.hybrid_fair_value,
                "method": "Pharma_Hybrid_DCF",
                "confidence": result.confidence
            }
            
        except Exception as e:
            logger.warning(f"Pharma DCF failed for {ticker}: {e}")
            return {"fair_value": 0, "method": "Pharma_DCF_Failed", "confidence": 0.3}
    
    async def _calculate_realestate_dcf(self, ticker: str, company_data: Dict, calculator) -> Dict:
        """Calculate real estate NAV"""
        try:
            info = company_data.get("info", {}) if company_data else {}
            
            # Simplified NAV calculation (would need detailed project data in reality)
            book_value = info.get("bookValue", 100)
            nav_per_share = book_value * 1.2  # 20% premium to book value
            
            return {
                "fair_value": nav_per_share,
                "method": "NAV_Based_Valuation",
                "confidence": 0.6
            }
            
        except Exception as e:
            logger.warning(f"Real Estate NAV failed for {ticker}: {e}")
            return {"fair_value": 0, "method": "RealEstate_NAV_Failed", "confidence": 0.3}
    
    async def _calculate_generic_dcf(self, ticker: str, company_data: Dict, calculator) -> Dict:
        """Calculate generic DCF for IT/FMCG/Energy sectors"""
        try:
            # Check if we have the required data
            if not company_data:
                logger.warning(f"No company data provided for {ticker}")
                return {"fair_value": 0, "method": "Generic_DCF_No_Data", "confidence": 0.3}
            
            # Extract financial data from company_data
            info = company_data.get("info", {})
            current_price = company_data.get("current_price", 0)
            
            # Create FinancialData object with available data
            # Note: For generic DCF, we need historical financial data which might not be available
            # in the company_data structure. We'll use conservative estimates based on current metrics.
            
            # Extract basic financial metrics
            market_cap = info.get("marketCap", 0)
            shares_outstanding = info.get("sharesOutstanding", 0)
            
            if shares_outstanding == 0 or market_cap == 0:
                logger.warning(f"Missing essential financial data for {ticker} - shares outstanding or market cap")
                return {"fair_value": 0, "method": "Generic_DCF_Insufficient_Data", "confidence": 0.3}
            
            # Estimate revenue from market cap and typical metrics
            # This is a rough estimation - ideally we'd have historical data
            revenue_estimate = market_cap * 0.5  # Conservative P/S ratio of 2
            ebitda_estimate = revenue_estimate * 0.15  # Assume 15% EBITDA margin
            net_income_estimate = ebitda_estimate * 0.6  # After depreciation and taxes
            fcf_estimate = net_income_estimate * 0.8  # Assume 80% FCF conversion
            debt_estimate = market_cap * 0.2  # Assume some debt
            cash_estimate = market_cap * 0.1  # Assume some cash
            
            # Create simplified financial data (single year)
            financial_data = FinancialData(
                ticker=ticker,
                years=[2023],  # Use current year
                revenue=[revenue_estimate],
                ebitda=[ebitda_estimate],
                net_income=[net_income_estimate],
                free_cash_flow=[fcf_estimate],
                total_debt=[debt_estimate],
                cash=[cash_estimate],
                shares_outstanding=[shares_outstanding]
            )
            
            # Create default DCF assumptions
            assumptions = DCFAssumptions(
                revenue_growth_rate=info.get("revenueGrowth", 0.1) * 100,  # Convert to percentage
                ebitda_margin=15.0,  # Default 15% EBITDA margin
                tax_rate=25.0,  # Standard corporate tax rate
                wacc=12.0,  # Default WACC for Indian companies
                terminal_growth_rate=4.0,  # Long-term GDP growth
                projection_years=5
            )
            
            # Calculate DCF (remove await since calculate_dcf is not async)
            result = calculator.calculate_dcf(financial_data, assumptions, current_price)
            
            return {
                "fair_value": result.intrinsic_value_per_share,
                "method": "Generic_DCF",
                "confidence": 0.6  # Lower confidence due to estimated data
            }
                
        except Exception as e:
            logger.warning(f"Generic DCF failed for {ticker}: {e}")
            logger.error(f"Error details: {type(e).__name__}: {str(e)}")
            return {"fair_value": 0, "method": "Generic_DCF_Failed", "confidence": 0.3}
    
    def _get_sector_rules(self, sector: str) -> Dict:
        """Get sector-specific business rules and red flags"""
        
        rules = {
            "BFSI": {
                "red_flags": {
                    "gnpa_threshold": 5.0,  # GNPA > 5% = red flag
                    "nim_compression": -0.5,  # NIM decline > 0.5% = concern
                    "cost_to_income_high": 60.0,  # C/I > 60% = inefficiency
                    "capital_adequacy_low": 11.0  # CAR < 11% = regulatory risk
                },
                "positive_signals": {
                    "roe_threshold": 15.0,  # ROE > 15% = strong
                    "cost_efficiency": 40.0,  # Cost/Income < 40% = efficient
                    "casa_ratio_good": 40.0,  # CASA > 40% = low cost deposits
                    "credit_growth_healthy": 15.0  # Credit growth 10-15% = optimal
                }
            },
            "PHARMA": {
                "red_flags": {
                    "rd_spend_low": 5.0,  # R&D < 5% of revenue = concern
                    "usfda_issues_high": 3,  # >3 observations = regulatory risk
                    "patent_cliff_risk": 20.0,  # >20% revenue from expiring patents
                    "us_exposure_low": 30.0  # <30% US revenue = limited growth
                },
                "positive_signals": {
                    "anda_pipeline_strong": 10,  # >10 ANDAs = strong pipeline
                    "us_revenue_exposure": 40.0,  # >40% US revenue = premium
                    "rd_intensity_good": 8.0,  # >8% R&D spend = innovation focus
                    "ebitda_margin_strong": 20.0  # >20% EBITDA margin = efficiency
                }
            },
            "REALESTATE": {
                "red_flags": {
                    "inventory_turnover_low": 0.5,  # <0.5x = monetization risk
                    "debt_equity_high": 1.5,  # D/E > 1.5x = leverage concern
                    "presales_low": 50.0,  # <50% pre-sales = execution risk
                    "tier2_exposure_high": 60.0  # >60% Tier 2+ cities = demand risk
                },
                "positive_signals": {
                    "tier1_exposure": 60.0,  # >60% Tier 1 cities = premium
                    "pre_sales_strong": 70.0,  # >70% pre-sales = execution
                    "inventory_turnover_good": 1.0,  # >1.0x = good monetization
                    "debt_equity_low": 0.8  # D/E < 0.8x = financial strength
                }
            },
            "IT": {
                "red_flags": {
                    "revenue_growth_low": 5.0,  # <5% growth = demand concern
                    "margin_compression": -2.0,  # >2% margin decline = pricing pressure
                    "client_concentration_high": 30.0,  # >30% from single client = risk
                    "utilization_low": 75.0  # <75% utilization = bench concern
                },
                "positive_signals": {
                    "revenue_growth_good": 15.0,  # >15% growth = strong demand
                    "margin_expansion": 1.0,  # >1% margin improvement = efficiency
                    "digital_revenue_high": 60.0,  # >60% digital revenue = transformation
                    "client_mining_good": 5.0  # >5% revenue growth from top clients
                }
            },
            "FMCG": {
                "red_flags": {
                    "volume_growth_negative": 0.0,  # Negative volume growth = demand issue
                    "margin_pressure": -1.0,  # >1% margin decline = input cost pressure
                    "rural_weakness": -5.0,  # >5% rural revenue decline = concern
                    "market_share_loss": -2.0  # >2% market share loss = competitive pressure
                },
                "positive_signals": {
                    "volume_growth_good": 8.0,  # >8% volume growth = strong demand
                    "margin_expansion": 0.5,  # >0.5% margin improvement = pricing power
                    "premium_portfolio": 40.0,  # >40% premium products = brand strength
                    "distribution_expansion": 10.0  # >10% distribution growth = reach
                }
            },
            "ENERGY": {
                "red_flags": {
                    "refining_margin_low": 5.0,  # <$5/bbl GRM = profitability pressure
                    "inventory_losses_high": 2.0,  # >2% inventory losses = volatility impact
                    "capex_intensity_high": 15.0,  # >15% of revenue = capital intensive
                    "debt_equity_high": 1.2  # D/E > 1.2x = leverage concern
                },
                "positive_signals": {
                    "refining_margin_good": 8.0,  # >$8/bbl GRM = strong profitability
                    "marketing_margin_stable": 3.0,  # >₹3/L marketing margin = stable
                    "petrochemical_integration": 30.0,  # >30% petchem revenue = diversification
                    "renewable_transition": 20.0  # >20% capex in renewables = future ready
                }
            }
        }
        
        return rules.get(sector, {})
    
    async def _get_cached_dcf(self, ticker: str, sector: str, mode: str) -> Optional[SectorDCFResult]:
        """
        Retrieve cached DCF result if available
        
        Args:
            ticker: Stock ticker symbol
            sector: Sector classification  
            mode: Analysis mode
            
        Returns:
            Cached SectorDCFResult or None if not found/expired
        """
        try:
            cached_data = await self.cache_manager.get(
                cache_type=CacheType.FINANCIAL_DATA,
                identifier=ticker,
                sector=sector,
                mode=mode,
                calculation_type="sector_dcf"
            )
            
            if cached_data:
                # Convert cached dict back to SectorDCFResult
                return SectorDCFResult(
                    ticker=cached_data['ticker'],
                    sector=cached_data['sector'],
                    fair_value=cached_data['fair_value'],
                    current_price=cached_data['current_price'],
                    upside_downside_pct=cached_data['upside_downside_pct'],
                    dcf_method=cached_data['dcf_method'],
                    confidence=cached_data['confidence'],
                    sector_rules=cached_data['sector_rules'],
                    calculation_timestamp=datetime.fromisoformat(cached_data['calculation_timestamp'])
                )
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving cached DCF for {ticker}: {e}")
            return None
    
    async def _cache_dcf_result(self, ticker: str, sector: str, mode: str, result: SectorDCFResult) -> bool:
        """
        Cache DCF calculation result
        
        Args:
            ticker: Stock ticker symbol
            sector: Sector classification
            mode: Analysis mode
            result: SectorDCFResult to cache
            
        Returns:
            True if successfully cached, False otherwise
        """
        try:
            # Convert SectorDCFResult to dict for caching
            cache_data = {
                'ticker': result.ticker,
                'sector': result.sector,
                'fair_value': result.fair_value,
                'current_price': result.current_price,
                'upside_downside_pct': result.upside_downside_pct,
                'dcf_method': result.dcf_method,
                'confidence': result.confidence,
                'sector_rules': result.sector_rules,
                'calculation_timestamp': result.calculation_timestamp.isoformat()
            }
            
            success = await self.cache_manager.set(
                cache_type=CacheType.FINANCIAL_DATA,
                identifier=ticker,
                data=cache_data,
                sector=sector,
                mode=mode,
                calculation_type="sector_dcf"
            )
            
            if success:
                logger.info(f"Cached {sector} DCF result for {ticker} (mode: {mode})")
            else:
                logger.warning(f"Failed to cache DCF result for {ticker}")
                
            return success
            
        except Exception as e:
            logger.error(f"Error caching DCF result for {ticker}: {e}")
            return False
    
    async def invalidate_cache(self, ticker: str, sector: str = None, mode: str = None) -> int:
        """
        Invalidate cached DCF results for a ticker
        
        Args:
            ticker: Stock ticker symbol
            sector: Optional sector filter
            mode: Optional mode filter
            
        Returns:
            Number of cache entries invalidated
        """
        invalidated_count = 0
        
        try:
            # If sector and mode specified, invalidate specific entry
            if sector and mode:
                success = await self.cache_manager.invalidate(
                    cache_type=CacheType.FINANCIAL_DATA,
                    identifier=ticker,
                    sector=sector,
                    mode=mode,
                    calculation_type="sector_dcf"
                )
                if success:
                    invalidated_count = 1
                    logger.info(f"Invalidated {sector} DCF cache for {ticker} (mode: {mode})")
            else:
                # Invalidate all sector DCF entries for ticker
                # This requires iterating through possible combinations
                sectors = ["BFSI", "PHARMA", "REALESTATE", "IT", "FMCG", "ENERGY"]
                modes = ["simple", "agentic"]
                
                for s in sectors:
                    for m in modes:
                        success = await self.cache_manager.invalidate(
                            cache_type=CacheType.FINANCIAL_DATA,
                            identifier=ticker,
                            sector=s,
                            mode=m,
                            calculation_type="sector_dcf"
                        )
                        if success:
                            invalidated_count += 1
                
                logger.info(f"Invalidated {invalidated_count} sector DCF cache entries for {ticker}")
            
            return invalidated_count
            
        except Exception as e:
            logger.error(f"Error invalidating cache for {ticker}: {e}")
            return 0