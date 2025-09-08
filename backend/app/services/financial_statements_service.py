# Financial Statements Service
# Provides 5-year historical financial statement analysis with real data from yfinance
# Implements Tab 1 functionality from Financial Analysis blueprint

import logging
import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd
import numpy as np
from functools import lru_cache

from .intelligent_cache import intelligent_cache, CacheType

logger = logging.getLogger(__name__)

@dataclass
class FinancialStatementYear:
    """Single year financial statement data"""
    year: str
    fiscal_year_end: datetime
    
    # Income Statement
    total_revenue: float = 0
    gross_profit: float = 0
    operating_income: float = 0
    ebitda: float = 0
    net_income: float = 0
    basic_eps: float = 0
    
    # Balance Sheet  
    total_assets: float = 0
    total_liabilities: float = 0
    stockholders_equity: float = 0
    cash_and_equivalents: float = 0
    total_debt: float = 0
    
    # Cash Flow Statement
    operating_cash_flow: float = 0
    free_cash_flow: float = 0
    capital_expenditure: float = 0
    
    # Calculated YoY Changes (%)
    revenue_yoy_change: Optional[float] = None
    net_income_yoy_change: Optional[float] = None
    assets_yoy_change: Optional[float] = None
    equity_yoy_change: Optional[float] = None
    ocf_yoy_change: Optional[float] = None

@dataclass
class FinancialStatementsAnalysis:
    """Complete 5-year financial statements analysis"""
    ticker: str
    company_name: str
    currency: str
    analysis_date: datetime
    
    # Historical data (5 years)
    annual_data: List[FinancialStatementYear]
    
    # Calculated metrics
    revenue_cagr_5y: float
    net_income_cagr_5y: float
    book_value_cagr_5y: float
    
    # Quality indicators
    earnings_quality_score: float  # OCF vs Net Income consistency
    revenue_consistency_score: float  # Revenue growth volatility
    margin_stability_score: float  # Profit margin stability
    
    # Simple vs Agentic Mode content
    simple_mode_summary: str
    
    # Data quality
    data_completeness: float  # % of required fields populated
    data_warnings: List[str]
    last_updated: datetime
    
    # Optional fields with defaults
    agentic_mode_interpretation: Optional[str] = None

class FinancialStatementsService:
    """
    Financial Statements Service providing comprehensive 5-year analysis
    
    Features:
    - Real historical data from yfinance
    - Automatic YoY change calculations  
    - Financial health scoring
    - Earnings quality assessment
    - Simple + Agentic mode content
    - Intelligent caching with 4-hour refresh
    """
    
    def __init__(self, use_cache: bool = True):
        self.use_cache = use_cache
        self.cache_manager = intelligent_cache
        self.cache_duration = timedelta(hours=4)  # 4-hour cache for financial data
        
        # Required financial statement fields mapping
        self.income_statement_fields = {
            'total_revenue': ['Total Revenue', 'Operating Revenue'],
            'gross_profit': ['Gross Profit'],  
            'operating_income': ['Operating Income'],
            'ebitda': ['EBITDA', 'Normalized EBITDA'],
            'net_income': ['Net Income', 'Net Income Common Stockholders'],
            'basic_eps': ['Basic EPS']
        }
        
        self.balance_sheet_fields = {
            'total_assets': ['Total Assets'],
            'total_liabilities': ['Total Liabilities Net Minority Interest', 'Total Liabilities'],
            'stockholders_equity': ['Stockholders Equity', 'Total Equity Gross Minority Interest'],
            'cash_and_equivalents': ['Cash And Cash Equivalents', 'Cash Cash Equivalents And Short Term Investments'],
            'total_debt': ['Total Debt', 'Net Debt']
        }
        
        self.cashflow_fields = {
            'operating_cash_flow': ['Operating Cash Flow', 'Cash Flow From Continuing Operating Activities'],
            'free_cash_flow': ['Free Cash Flow'],
            'capital_expenditure': ['Capital Expenditure']
        }
    
    async def get_financial_statements_analysis(
        self,
        ticker: str,
        force_refresh: bool = False
    ) -> FinancialStatementsAnalysis:
        """
        Get comprehensive 5-year financial statements analysis
        
        Args:
            ticker: Stock ticker symbol (e.g., 'RELIANCE.NS')
            force_refresh: Skip cache and fetch fresh data
            
        Returns:
            FinancialStatementsAnalysis with 5 years of data and calculated metrics
        """
        try:
            logger.info(f"Fetching financial statements analysis for {ticker}")
            
            # Check cache first
            if self.use_cache and not force_refresh:
                cached_result = await self.cache_manager.get(
                    CacheType.FINANCIAL_DATA, ticker
                )
                if cached_result:
                    logger.info(f"Cache hit for {ticker} financial statements - reconstructing objects")
                    # Reconstruct objects from cached dict
                    try:
                        return self._reconstruct_from_cache(cached_result)
                    except Exception as e:
                        logger.warning(f"Failed to reconstruct from cache for {ticker}: {e}, proceeding with fresh calculation")
            
            # Fetch real financial data from yfinance
            stock = yf.Ticker(ticker)
            
            # Get basic company info
            info = stock.info
            company_name = info.get('longName', ticker)
            currency = info.get('financialCurrency', 'INR')
            
            # Fetch 5-year financial statements
            annual_data = await self._fetch_historical_statements(stock)
            
            if not annual_data:
                raise ValueError(f"No financial statement data available for {ticker}")
            
            # Calculate derived metrics
            revenue_cagr = self._calculate_cagr([year.total_revenue for year in annual_data])
            net_income_cagr = self._calculate_cagr([year.net_income for year in annual_data])
            book_value_cagr = self._calculate_cagr([year.stockholders_equity for year in annual_data])
            
            # Calculate quality scores
            earnings_quality = self._calculate_earnings_quality_score(annual_data)
            revenue_consistency = self._calculate_revenue_consistency_score(annual_data)
            margin_stability = self._calculate_margin_stability_score(annual_data)
            
            # Generate content for both modes
            simple_summary = self._generate_simple_mode_summary(
                annual_data, revenue_cagr, net_income_cagr, earnings_quality
            )
            
            # Calculate data completeness
            data_completeness = self._calculate_data_completeness(annual_data)
            data_warnings = self._generate_data_warnings(annual_data, data_completeness)
            
            # Create result
            result = FinancialStatementsAnalysis(
                ticker=ticker,
                company_name=company_name,
                currency=currency,
                analysis_date=datetime.now(),
                annual_data=annual_data,
                revenue_cagr_5y=revenue_cagr,
                net_income_cagr_5y=net_income_cagr,
                book_value_cagr_5y=book_value_cagr,
                earnings_quality_score=earnings_quality,
                revenue_consistency_score=revenue_consistency,
                margin_stability_score=margin_stability,
                simple_mode_summary=simple_summary,
                data_completeness=data_completeness,
                data_warnings=data_warnings,
                last_updated=datetime.now()
            )
            
            # Cache the result
            if self.use_cache:
                await self.cache_manager.set(
                    CacheType.FINANCIAL_DATA,
                    ticker,
                    asdict(result)
                )
            
            logger.info(f"Financial statements analysis completed for {ticker}: {len(annual_data)} years, {data_completeness:.1%} complete")
            return result
            
        except Exception as e:
            logger.error(f"Error fetching financial statements for {ticker}: {e}")
            raise
    
    async def _fetch_historical_statements(self, stock: yf.Ticker) -> List[FinancialStatementYear]:
        """Fetch and process 5-year historical financial statements"""
        
        try:
            # Get financial statements (yfinance provides up to 5 years)
            financials = stock.financials
            balance_sheet = stock.balance_sheet  
            cashflow = stock.cashflow
            
            if financials.empty or balance_sheet.empty or cashflow.empty:
                logger.warning("One or more financial statements are empty")
                return []
            
            annual_data = []
            
            # Process each year (columns are years in reverse chronological order)
            for i, year_timestamp in enumerate(financials.columns):
                # Convert to proper fiscal year label (FY25, FY24, etc.)
                fiscal_year = year_timestamp.year
                
                # For Indian companies: FY ends in March, so if month <= 3, it's the fiscal year ending in that calendar year
                # If month > 3, it's the fiscal year ending in the next calendar year
                if year_timestamp.month <= 3:
                    fiscal_year_label = f"FY{str(fiscal_year)[-2:]}"  # e.g., "FY25" for 2025
                else:
                    fiscal_year_label = f"FY{str(fiscal_year + 1)[-2:]}"  # e.g., "FY25" for 2024
                
                year_str = fiscal_year_label
                
                # Extract data for this year
                year_data = FinancialStatementYear(
                    year=year_str,
                    fiscal_year_end=year_timestamp,
                    
                    # Income Statement
                    total_revenue=self._safe_extract_value(financials, year_timestamp, self.income_statement_fields['total_revenue']),
                    gross_profit=self._safe_extract_value(financials, year_timestamp, self.income_statement_fields['gross_profit']),  
                    operating_income=self._safe_extract_value(financials, year_timestamp, self.income_statement_fields['operating_income']),
                    ebitda=self._safe_extract_value(financials, year_timestamp, self.income_statement_fields['ebitda']),
                    net_income=self._safe_extract_value(financials, year_timestamp, self.income_statement_fields['net_income']),
                    basic_eps=self._safe_extract_value(financials, year_timestamp, self.income_statement_fields['basic_eps']),
                    
                    # Balance Sheet
                    total_assets=self._safe_extract_value(balance_sheet, year_timestamp, self.balance_sheet_fields['total_assets']),
                    total_liabilities=self._safe_extract_value(balance_sheet, year_timestamp, self.balance_sheet_fields['total_liabilities']),
                    stockholders_equity=self._safe_extract_value(balance_sheet, year_timestamp, self.balance_sheet_fields['stockholders_equity']),
                    cash_and_equivalents=self._safe_extract_value(balance_sheet, year_timestamp, self.balance_sheet_fields['cash_and_equivalents']),
                    total_debt=self._safe_extract_value(balance_sheet, year_timestamp, self.balance_sheet_fields['total_debt']),
                    
                    # Cash Flow Statement  
                    operating_cash_flow=self._safe_extract_value(cashflow, year_timestamp, self.cashflow_fields['operating_cash_flow']),
                    free_cash_flow=self._safe_extract_value(cashflow, year_timestamp, self.cashflow_fields['free_cash_flow']),
                    capital_expenditure=self._safe_extract_value(cashflow, year_timestamp, self.cashflow_fields['capital_expenditure'])
                )
                
                annual_data.append(year_data)
            
            # Calculate YoY changes (compare each year to previous year)  
            for i in range(len(annual_data) - 1):
                current_year = annual_data[i]
                previous_year = annual_data[i + 1]
                
                current_year.revenue_yoy_change = self._calculate_yoy_change(current_year.total_revenue, previous_year.total_revenue)
                current_year.net_income_yoy_change = self._calculate_yoy_change(current_year.net_income, previous_year.net_income)  
                current_year.assets_yoy_change = self._calculate_yoy_change(current_year.total_assets, previous_year.total_assets)
                current_year.equity_yoy_change = self._calculate_yoy_change(current_year.stockholders_equity, previous_year.stockholders_equity)
                current_year.ocf_yoy_change = self._calculate_yoy_change(current_year.operating_cash_flow, previous_year.operating_cash_flow)
            
            # Sort by year (newest first)
            annual_data.sort(key=lambda x: x.fiscal_year_end, reverse=True)
            
            return annual_data
            
        except Exception as e:
            logger.error(f"Error processing historical statements: {e}")
            return []
    
    def _safe_extract_value(self, df: pd.DataFrame, year_col, field_names: List[str]) -> float:
        """Safely extract value from financial statement DataFrame"""
        
        if df.empty or year_col not in df.columns:
            return 0.0
            
        for field_name in field_names:
            if field_name in df.index:
                value = df.loc[field_name, year_col]
                if pd.notna(value) and value != 0:
                    return float(value)
        
        return 0.0
    
    def _calculate_yoy_change(self, current: float, previous: float) -> Optional[float]:
        """Calculate year-over-year percentage change"""
        
        # Handle None or NaN values
        if pd.isna(current) or pd.isna(previous):
            return None
            
        # Convert to float to handle any type issues
        try:
            current = float(current) if current is not None else 0.0
            previous = float(previous) if previous is not None else 0.0
        except (ValueError, TypeError):
            return None
        
        # If previous year is zero or very small (less than 1), we can't calculate meaningful YoY
        if abs(previous) < 1:
            return None
            
        # Calculate YoY change
        yoy_change = ((current - previous) / abs(previous)) * 100
        
        # Return None for extreme values (likely data errors)
        if abs(yoy_change) > 1000:  # More than 1000% change is likely a data issue
            return None
            
        return yoy_change
    
    def _calculate_cagr(self, values: List[float]) -> float:
        """Calculate Compound Annual Growth Rate"""
        
        # Filter out zero and nan values
        valid_values = [v for v in values if v > 0 and not pd.isna(v)]
        
        if len(valid_values) < 2:
            return 0.0
        
        # CAGR = (Ending Value / Beginning Value)^(1/number of years) - 1
        ending_value = valid_values[0]  # Most recent (first in list)
        beginning_value = valid_values[-1]  # Oldest (last in list)
        years = len(valid_values) - 1
        
        if beginning_value <= 0 or years <= 0:
            return 0.0
            
        cagr = (ending_value / beginning_value) ** (1/years) - 1
        return cagr * 100  # Return as percentage
    
    def _calculate_earnings_quality_score(self, annual_data: List[FinancialStatementYear]) -> float:
        """
        Calculate earnings quality score based on OCF vs Net Income consistency
        Score: 0-100 (higher is better)
        """
        
        ocf_vs_ni_ratios = []
        
        for year_data in annual_data:
            if year_data.operating_cash_flow > 0 and year_data.net_income > 0:
                ratio = year_data.operating_cash_flow / year_data.net_income
                ocf_vs_ni_ratios.append(ratio)
        
        if not ocf_vs_ni_ratios:
            return 50.0  # Neutral score if no data
        
        # Good earnings quality: OCF consistently >= Net Income  
        avg_ratio = np.mean(ocf_vs_ni_ratios)
        ratio_stability = 1 - (np.std(ocf_vs_ni_ratios) / avg_ratio) if avg_ratio > 0 else 0
        
        # Score based on average ratio and consistency
        base_score = min(avg_ratio * 50, 75)  # Max 75 for ratio component
        consistency_bonus = ratio_stability * 25  # Max 25 for consistency
        
        return min(base_score + consistency_bonus, 100)
    
    def _calculate_revenue_consistency_score(self, annual_data: List[FinancialStatementYear]) -> float:
        """Calculate revenue growth consistency score (0-100)"""
        
        revenue_changes = [year.revenue_yoy_change for year in annual_data if year.revenue_yoy_change is not None]
        
        if len(revenue_changes) < 2:
            return 50.0
        
        # Lower volatility = higher consistency score
        avg_growth = np.mean(revenue_changes)
        growth_volatility = np.std(revenue_changes)
        
        # Normalize volatility (0-50% volatility maps to 100-0 score)
        max_volatility = 50.0
        volatility_score = max(0, 100 - (growth_volatility / max_volatility) * 100)
        
        # Bonus for positive average growth
        growth_bonus = 10 if avg_growth > 0 else 0
        
        return min(volatility_score + growth_bonus, 100)
    
    def _calculate_margin_stability_score(self, annual_data: List[FinancialStatementYear]) -> float:
        """Calculate profit margin stability score (0-100)"""
        
        margins = []
        for year_data in annual_data:
            if year_data.total_revenue > 0 and year_data.net_income != 0:
                margin = (year_data.net_income / year_data.total_revenue) * 100
                margins.append(margin)
        
        if len(margins) < 2:
            return 50.0
        
        # Lower margin volatility = higher stability
        margin_volatility = np.std(margins)
        avg_margin = np.mean(margins)
        
        # Score based on margin volatility (0-10% volatility maps to 100-0 score)
        max_volatility = 10.0
        stability_score = max(0, 100 - (margin_volatility / max_volatility) * 100)
        
        # Bonus for positive margins
        profitability_bonus = 10 if avg_margin > 0 else 0
        
        return min(stability_score + profitability_bonus, 100)
    
    def _generate_simple_mode_summary(
        self,
        annual_data: List[FinancialStatementYear],
        revenue_cagr: float,
        net_income_cagr: float,
        earnings_quality: float
    ) -> str:
        """Generate Simple Mode summary based on financial data analysis"""
        
        if not annual_data:
            return "Financial statement data unavailable for analysis."
        
        latest_year = annual_data[0]
        
        # Revenue analysis
        if revenue_cagr > 15:
            revenue_insight = f"Strong revenue growth at {revenue_cagr:.1f}% CAGR over 5 years."
        elif revenue_cagr > 8:
            revenue_insight = f"Steady revenue growth at {revenue_cagr:.1f}% CAGR."  
        elif revenue_cagr > 0:
            revenue_insight = f"Modest revenue growth at {revenue_cagr:.1f}% CAGR."
        else:
            revenue_insight = f"Revenue declining at {revenue_cagr:.1f}% CAGR - concerning trend."
        
        # Profitability analysis
        if net_income_cagr > 12:
            profit_insight = f"Excellent profit growth at {net_income_cagr:.1f}% CAGR."
        elif net_income_cagr > 0:
            profit_insight = f"Positive profit growth at {net_income_cagr:.1f}% CAGR."
        else:
            profit_insight = f"Profit declining at {net_income_cagr:.1f}% CAGR."
        
        # Earnings quality
        if earnings_quality > 75:
            quality_insight = "High earnings quality with consistent cash generation."
        elif earnings_quality > 50:
            quality_insight = "Reasonable earnings quality."  
        else:
            quality_insight = "Earnings quality concerns - cash flow inconsistent with profits."
        
        # Cash flow analysis
        if latest_year.operating_cash_flow > latest_year.net_income:
            cash_insight = "Cash from operations exceeds net income - good earnings quality."
        elif latest_year.operating_cash_flow > 0:
            cash_insight = "Positive operating cash flow generation."
        else:
            cash_insight = "Operating cash flow challenges require attention."
        
        return f"{revenue_insight} {profit_insight} {quality_insight} {cash_insight}"
    
    def _calculate_data_completeness(self, annual_data: List[FinancialStatementYear]) -> float:
        """Calculate what percentage of required financial data is available"""
        
        if not annual_data:
            return 0.0
        
        total_fields = 0
        populated_fields = 0
        
        for year_data in annual_data:
            # Count key financial statement fields
            key_fields = [
                year_data.total_revenue, year_data.net_income, year_data.total_assets,
                year_data.stockholders_equity, year_data.operating_cash_flow
            ]
            
            total_fields += len(key_fields)
            populated_fields += sum(1 for field in key_fields if field != 0)
        
        return populated_fields / total_fields if total_fields > 0 else 0.0
    
    def _generate_data_warnings(self, annual_data: List[FinancialStatementYear], completeness: float) -> List[str]:
        """Generate data quality warnings"""
        
        warnings = []
        
        if len(annual_data) < 5:
            warnings.append(f"Limited historical data: only {len(annual_data)} years available")
        
        if completeness < 0.8:
            warnings.append(f"Financial data {completeness:.1%} complete - some metrics may be unreliable")
        
        # Check for missing key metrics in latest year
        if annual_data:
            latest = annual_data[0]
            if latest.total_revenue == 0:
                warnings.append("Revenue data missing for latest year")
            if latest.net_income == 0:
                warnings.append("Net income data missing for latest year")
            if latest.operating_cash_flow == 0:
                warnings.append("Operating cash flow data missing for latest year")
        
        return warnings
    
    def _reconstruct_from_cache(self, cached_data: Dict) -> FinancialStatementsAnalysis:
        """Reconstruct FinancialStatementsAnalysis from cached dictionary"""
        
        # Reconstruct annual_data list of FinancialStatementYear objects
        annual_data = []
        if 'annual_data' in cached_data:
            for year_dict in cached_data['annual_data']:
                # Convert dict back to FinancialStatementYear object
                if isinstance(year_dict, dict):
                    # Parse fiscal_year_end back to datetime if it's a string
                    fiscal_year_end = year_dict.get('fiscal_year_end')
                    if isinstance(fiscal_year_end, str):
                        try:
                            from datetime import datetime
                            fiscal_year_end = datetime.fromisoformat(fiscal_year_end.replace('Z', '+00:00'))
                        except:
                            fiscal_year_end = datetime.now()
                    
                    year_obj = FinancialStatementYear(
                        year=year_dict.get('year', ''),
                        fiscal_year_end=fiscal_year_end,
                        
                        # Income Statement
                        total_revenue=year_dict.get('total_revenue', 0),
                        gross_profit=year_dict.get('gross_profit', 0),
                        operating_income=year_dict.get('operating_income', 0),
                        ebitda=year_dict.get('ebitda', 0),
                        net_income=year_dict.get('net_income', 0),
                        basic_eps=year_dict.get('basic_eps', 0),
                        
                        # Balance Sheet
                        total_assets=year_dict.get('total_assets', 0),
                        total_liabilities=year_dict.get('total_liabilities', 0),
                        stockholders_equity=year_dict.get('stockholders_equity', 0),
                        cash_and_equivalents=year_dict.get('cash_and_equivalents', 0),
                        total_debt=year_dict.get('total_debt', 0),
                        
                        # Cash Flow Statement
                        operating_cash_flow=year_dict.get('operating_cash_flow', 0),
                        free_cash_flow=year_dict.get('free_cash_flow', 0),
                        capital_expenditure=year_dict.get('capital_expenditure', 0),
                        
                        # YoY Changes
                        revenue_yoy_change=year_dict.get('revenue_yoy_change', 0),
                        net_income_yoy_change=year_dict.get('net_income_yoy_change', 0),
                        assets_yoy_change=year_dict.get('assets_yoy_change', 0),
                        equity_yoy_change=year_dict.get('equity_yoy_change', 0),
                        ocf_yoy_change=year_dict.get('ocf_yoy_change', 0)
                    )
                    annual_data.append(year_obj)
                else:
                    # It's already a proper object
                    annual_data.append(year_dict)
        
        # Parse datetime fields if they're strings
        analysis_date = cached_data.get('analysis_date')
        last_updated = cached_data.get('last_updated')
        
        if isinstance(analysis_date, str):
            try:
                from datetime import datetime
                analysis_date = datetime.fromisoformat(analysis_date.replace('Z', '+00:00'))
            except:
                analysis_date = datetime.now()
        
        if isinstance(last_updated, str):
            try:
                from datetime import datetime  
                last_updated = datetime.fromisoformat(last_updated.replace('Z', '+00:00'))
            except:
                last_updated = datetime.now()
        
        # Reconstruct main result
        return FinancialStatementsAnalysis(
            ticker=cached_data.get('ticker', ''),
            company_name=cached_data.get('company_name', ''),
            currency=cached_data.get('currency', 'INR'),
            analysis_date=analysis_date,
            annual_data=annual_data,
            revenue_cagr_5y=cached_data.get('revenue_cagr_5y', 0),
            net_income_cagr_5y=cached_data.get('net_income_cagr_5y', 0),
            book_value_cagr_5y=cached_data.get('book_value_cagr_5y', 0),
            earnings_quality_score=cached_data.get('earnings_quality_score', 50),
            simple_mode_summary=cached_data.get('simple_mode_summary', ''),
            agentic_mode_interpretation=cached_data.get('agentic_mode_interpretation', ''),
            data_completeness=cached_data.get('data_completeness', 0),
            data_warnings=cached_data.get('data_warnings', []),
            last_updated=last_updated
        )