import numpy as np
from typing import List, Dict, Tuple
from datetime import datetime
import logging
from .price_service import price_service
from .sector_intelligence_service import sector_intelligence_service
from ..models.dcf import (
    DCFAssumptions, DCFProjection, DCFValuation, 
    SensitivityAnalysis, DCFDefaults, FinancialData
)

logger = logging.getLogger(__name__)

class DCFService:
    """Service for DCF (Discounted Cash Flow) valuation calculations"""
    
    @staticmethod
    def calculate_dcf(financial_data: FinancialData, assumptions: DCFAssumptions, current_price: float = None) -> DCFValuation:
        """Calculate DCF valuation based on financial data and assumptions"""
        try:
            logger.info(f"Starting DCF calculation for ticker: {financial_data.ticker}")
            logger.info(f"Assumptions: {assumptions}")
            
            # Validate inputs
            if not financial_data.revenue or len(financial_data.revenue) == 0:
                raise ValueError("No revenue data available for DCF calculation")
            
            if not financial_data.shares_outstanding or len(financial_data.shares_outstanding) == 0:
                raise ValueError("No shares outstanding data available for DCF calculation")
            
            projections = DCFService._project_cash_flows(financial_data, assumptions)
            logger.info(f"Projected {len(projections)} years of cash flows")
            
            terminal_value = DCFService._calculate_terminal_value(projections[-1], assumptions)
            logger.info(f"Terminal value calculated: {terminal_value:,.2f}")
            
            enterprise_value = DCFService._calculate_enterprise_value(projections, terminal_value, assumptions)
            logger.info(f"Enterprise value: {enterprise_value:,.2f}")
            
            equity_value = DCFService._calculate_equity_value(enterprise_value, financial_data)
            logger.info(f"Equity value: {equity_value:,.2f}")
            
            intrinsic_value_per_share = DCFService._calculate_intrinsic_value_per_share(equity_value, financial_data)
            logger.info(f"Intrinsic value per share: {intrinsic_value_per_share:.2f}")
            
            # Use provided current price or fallback to a basic calculation
            if current_price is not None and current_price > 0:
                current_stock_price = current_price
                logger.info(f"Using provided current price: {current_price}")
            else:
                # Fallback: use basic calculation if current price not provided
                current_stock_price = financial_data.revenue[-1] / financial_data.shares_outstanding[-1] if financial_data.shares_outstanding[-1] > 0 else 0
                logger.warning(f"No current price provided, using fallback calculation: {current_stock_price}")
                
            upside_downside = ((intrinsic_value_per_share - current_stock_price) / current_stock_price) * 100 if current_stock_price > 0 else 0
            logger.info(f"Upside/Downside: {upside_downside:.2f}%")
            
            result = DCFValuation(
                intrinsic_value_per_share=intrinsic_value_per_share,
                terminal_value=terminal_value,
                enterprise_value=enterprise_value,
                equity_value=equity_value,
                current_stock_price=current_stock_price,
                upside_downside=upside_downside,
                projections=projections,
                assumptions=assumptions
            )
            
            logger.info("DCF calculation completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error calculating DCF for {financial_data.ticker if financial_data else 'unknown ticker'}: {str(e)}")
            logger.error(f"Error type: {type(e).__name__}")
            raise e

    @staticmethod
    def _project_cash_flows(financial_data: FinancialData, assumptions: DCFAssumptions) -> List[DCFProjection]:
        """Project future cash flows based on assumptions"""
        projections = []
        
        # Get base year data (most recent year)
        base_revenue = financial_data.revenue[0] if financial_data.revenue else 0
        base_year = financial_data.years[0] if financial_data.years else datetime.now().year
        
        for year in range(1, assumptions.projection_years + 1):
            projection_year = base_year + year
            
            # Project revenue with growth rate
            revenue = base_revenue * ((1 + assumptions.revenue_growth_rate / 100) ** year)
            
            # Calculate EBITDA
            ebitda = revenue * (assumptions.ebitda_margin / 100)
            
            # Estimate depreciation (assume 3% of revenue)
            depreciation = revenue * 0.03
            
            # Calculate EBIT
            ebit = ebitda - depreciation
            
            # Calculate tax
            tax = ebit * (assumptions.tax_rate / 100)
            
            # Calculate NOPAT (Net Operating Profit After Tax)
            nopat = ebit - tax
            
            # Estimate CapEx (assume 2% of revenue)
            capex = revenue * 0.02
            
            # Estimate working capital change (assume 1% of revenue change)
            revenue_change = revenue - (base_revenue * ((1 + assumptions.revenue_growth_rate / 100) ** (year - 1)) if year > 1 else base_revenue)
            working_capital_change = revenue_change * 0.01
            
            # Calculate Free Cash Flow
            free_cash_flow = nopat + depreciation - capex - working_capital_change
            
            # Calculate present value
            discount_factor = (1 + assumptions.wacc / 100) ** year
            present_value = free_cash_flow / discount_factor
            
            projections.append(DCFProjection(
                year=projection_year,
                revenue=revenue,
                revenue_growth_rate=assumptions.revenue_growth_rate,
                ebitda=ebitda,
                ebit=ebit,
                tax=tax,
                nopat=nopat,
                capex=capex,
                working_capital_change=working_capital_change,
                free_cash_flow=free_cash_flow,
                present_value=present_value,
                growth_stage="simple",
                growth_method="constant_growth"
            ))
        
        return projections

    @staticmethod
    def _calculate_terminal_value(final_projection: DCFProjection, assumptions: DCFAssumptions) -> float:
        """Calculate terminal value using Gordon Growth Model"""
        terminal_fcf = final_projection.free_cash_flow * (1 + assumptions.terminal_growth_rate / 100)
        terminal_value = terminal_fcf / (assumptions.wacc / 100 - assumptions.terminal_growth_rate / 100)
        
        # Discount terminal value to present value
        discount_factor = (1 + assumptions.wacc / 100) ** assumptions.projection_years
        return terminal_value / discount_factor

    @staticmethod
    def _calculate_enterprise_value(projections: List[DCFProjection], terminal_value: float, assumptions: DCFAssumptions) -> float:
        """Calculate enterprise value by summing present values"""
        pv_cash_flows = sum(projection.present_value for projection in projections)
        return pv_cash_flows + terminal_value

    @staticmethod
    def _calculate_equity_value(enterprise_value: float, financial_data: FinancialData) -> float:
        """Calculate equity value by adjusting for net debt"""
        latest_debt = financial_data.total_debt[0] if financial_data.total_debt else 0
        latest_cash = financial_data.cash[0] if financial_data.cash else 0
        net_debt = latest_debt - latest_cash
        
        return enterprise_value - net_debt

    @staticmethod
    def _calculate_intrinsic_value_per_share(equity_value: float, financial_data: FinancialData) -> float:
        """Calculate intrinsic value per share"""
        # Find the most recent non-zero shares outstanding value
        shares_outstanding = 1  # Default fallback
        if financial_data.shares_outstanding:
            # Try to find a valid shares outstanding value, starting from most recent
            for i in range(len(financial_data.shares_outstanding) - 1, -1, -1):
                if financial_data.shares_outstanding[i] > 0:
                    shares_outstanding = financial_data.shares_outstanding[i]
                    break
        
        # Debug logging to identify units issue
        logger.info(f"Equity value: {equity_value:,.2f}")
        logger.info(f"Shares outstanding: {shares_outstanding:,.0f}")
        
        intrinsic_value = equity_value / shares_outstanding if shares_outstanding > 0 else 0
        
        # Check for potential units mismatch
        # If intrinsic value is very low compared to typical stock prices, there might be a units issue
        if intrinsic_value < 1 and equity_value > 1000000:
            logger.warning(f"Potential units mismatch detected - intrinsic value too low: {intrinsic_value}")
            # Try converting shares from millions to actual count
            if shares_outstanding < 100000:  # Likely in millions
                adjusted_shares = shares_outstanding * 1000000
                adjusted_intrinsic = equity_value / adjusted_shares
                logger.info(f"Adjusted calculation with shares in millions: {adjusted_intrinsic}")
                return adjusted_intrinsic
        
        return intrinsic_value

    @staticmethod
    def generate_sensitivity_analysis(financial_data: FinancialData, base_assumptions: DCFAssumptions) -> SensitivityAnalysis:
        """Generate sensitivity analysis by varying WACC and terminal growth rate"""
        try:
            # Define ranges for sensitivity analysis
            wacc_base = base_assumptions.wacc
            terminal_growth_base = base_assumptions.terminal_growth_rate
            
            wacc_range = [wacc_base - 1, wacc_base - 0.5, wacc_base, wacc_base + 0.5, wacc_base + 1]
            terminal_growth_range = [terminal_growth_base - 1, terminal_growth_base - 0.5, terminal_growth_base, terminal_growth_base + 0.5, terminal_growth_base + 1]
            
            sensitivity_matrix = []
            
            for wacc in wacc_range:
                row = []
                for terminal_growth in terminal_growth_range:
                    # Create modified assumptions
                    modified_assumptions = DCFAssumptions(
                        revenue_growth_rate=base_assumptions.revenue_growth_rate,
                        ebitda_margin=base_assumptions.ebitda_margin,
                        tax_rate=base_assumptions.tax_rate,
                        wacc=wacc,
                        terminal_growth_rate=terminal_growth,
                        projection_years=base_assumptions.projection_years
                    )
                    
                    # Calculate DCF with modified assumptions
                    # Note: For sensitivity analysis, we don't need the current price comparison
                    valuation = DCFService.calculate_dcf(financial_data, modified_assumptions)
                    row.append(valuation.intrinsic_value_per_share)
                
                sensitivity_matrix.append(row)
            
            return SensitivityAnalysis(
                wacc_range=wacc_range,
                terminal_growth_range=terminal_growth_range,
                sensitivity_matrix=sensitivity_matrix
            )
            
        except Exception as e:
            logger.error(f"Error generating sensitivity analysis: {e}")
            return SensitivityAnalysis(
                wacc_range=[],
                terminal_growth_range=[],
                sensitivity_matrix=[]
            )

    @staticmethod
    async def calculate_default_assumptions(financial_data: FinancialData, ticker: str = None, sector: str = None) -> DCFDefaults:
        """Calculate intelligent default assumptions combining historical data and sector intelligence"""
        try:
            # Company-specific data from historical financials
            revenue_growth_rate = DCFService._calculate_average_growth_rate(financial_data.revenue)
            ebitda_margin = DCFService._calculate_average_margin(financial_data.revenue, financial_data.ebitda)
            
            # Get current stock price using unified price service
            current_price = 0.0
            if ticker:
                try:
                    current_price = price_service.get_price_for_dcf(ticker) or 0.0
                    logger.info(f"Using unified price service for {ticker}: ₹{current_price:.2f}")
                except Exception as e:
                    logger.warning(f"Could not fetch current price for {ticker}: {e}")
                    current_price = 0.0
            
            # Sector-specific data from SectorIntelligenceService
            sector_wacc = 12.0  # Fallback
            sector_terminal_growth = 4.0  # Fallback  
            sector_tax_rate = 25.0  # Fallback
            
            if sector:
                try:
                    # Get sector intelligence
                    sector_intel = sector_intelligence_service.get_sector_intelligence(sector)
                    if sector_intel:
                        sector_terminal_growth = sector_intel.terminal_growth_rate * 100  # Convert to percentage
                        sector_tax_rate = sector_intel.effective_tax_rate * 100  # Convert to percentage
                        logger.info(f"Using sector terminal growth: {sector_terminal_growth}% and tax rate: {sector_tax_rate}%")
                    
                    # Calculate sector-specific WACC
                    sector_wacc = await sector_intelligence_service.calculate_wacc(sector) * 100  # Convert to percentage
                    logger.info(f"Calculated sector WACC for {sector}: {sector_wacc}%")
                    
                except Exception as e:
                    logger.warning(f"Could not get sector intelligence for {sector}: {e}")
                    logger.info("Using fallback sector assumptions")
            
            rationale = {
                'revenue_growth_rate': f"Based on {len(financial_data.revenue)} years of historical company data",
                'ebitda_margin': f"Average margin from company's historical financial statements", 
                'tax_rate': f"Sector-specific effective tax rate from Damodaran data ({sector})" if sector else "Standard corporate tax rate for Indian companies",
                'wacc': f"Calculated using Damodaran sector data + live risk-free rate ({sector})" if sector else "Industry average cost of capital for Indian equity markets",
                'terminal_growth_rate': f"Sector-specific long-term growth rate from Damodaran data ({sector})" if sector else "Long-term GDP growth assumption for India"
            }
            
            return DCFDefaults(
                revenue_growth_rate=revenue_growth_rate,
                ebitda_margin=ebitda_margin,
                tax_rate=sector_tax_rate,
                wacc=sector_wacc,
                terminal_growth_rate=sector_terminal_growth,
                projection_years=5,
                capex_percentage=4.0,  # Default assumption - could be sector-specific
                working_capital_percentage=2.0,  # Default assumption - could be sector-specific
                current_price=current_price,
                rationale=rationale
            )
            
        except Exception as e:
            logger.error(f"Error calculating default assumptions: {e}")
            
            # Return fallback defaults with basic company data
            fallback_revenue_growth = DCFService._calculate_average_growth_rate(financial_data.revenue) if financial_data.revenue else 8.0
            fallback_ebitda_margin = DCFService._calculate_average_margin(financial_data.revenue, financial_data.ebitda) if financial_data.revenue and financial_data.ebitda else 20.0
            
            return DCFDefaults(
                revenue_growth_rate=fallback_revenue_growth,
                ebitda_margin=fallback_ebitda_margin,
                tax_rate=25.0,
                wacc=12.0,
                terminal_growth_rate=4.0,
                projection_years=5,
                capex_percentage=4.0,
                working_capital_percentage=2.0,
                current_price=0.0,
                rationale={
                    'revenue_growth_rate': "Fallback: Basic historical average",
                    'ebitda_margin': "Fallback: Basic historical average", 
                    'tax_rate': "Fallback: Standard corporate tax rate",
                    'wacc': "Fallback: Standard Indian market WACC",
                    'terminal_growth_rate': "Fallback: GDP growth assumption"
                }
            )

    @staticmethod
    def _calculate_average_growth_rate(values: List[float]) -> float:
        """Calculate average growth rate from historical values"""
        if len(values) < 2:
            return 8.0  # Default assumption
        
        growth_rates = []
        for i in range(1, len(values)):
            if values[i] > 0:
                growth_rate = ((values[i-1] / values[i]) - 1) * 100  # Note: values are in reverse chronological order
                growth_rates.append(growth_rate)
        
        return np.mean(growth_rates) if growth_rates else 8.0

    @staticmethod
    def _calculate_average_margin(revenue: List[float], ebitda: List[float]) -> float:
        """Calculate average EBITDA margin from historical data"""
        if len(revenue) != len(ebitda) or len(revenue) == 0:
            return 15.0  # Default assumption
        
        margins = []
        for i in range(len(revenue)):
            if revenue[i] > 0:
                margin = (ebitda[i] / revenue[i]) * 100
                margins.append(margin)
        
        if not margins:
            return 15.0
            
        calculated_margin = np.mean(margins)
        
        # Handle edge cases for financial companies (banks, insurance, etc.)
        # EBITDA margins > 100% often indicate accounting/calculation issues for financial services
        if calculated_margin > 100:
            logger.warning(f"Unusually high EBITDA margin detected: {calculated_margin:.2f}%. This may indicate a financial services company.")
            # For financial companies, use a more conservative default
            return min(calculated_margin, 50.0)  # Cap at 50% for financial companies
            
        return calculated_margin