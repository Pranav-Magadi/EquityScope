import yfinance as yf
import pandas as pd
import numpy as np
from typing import Optional, Dict, Any, List
from ..models.company import CompanyInfo, StockPrice
from ..models.dcf import FinancialData
from .price_service import price_service
import logging

logger = logging.getLogger(__name__)

class DataService:
    @staticmethod
    def get_company_info(ticker: str) -> Optional[CompanyInfo]:
        """Fetch company information using unified price service"""
        try:
            # Use unified price service for consistent data
            company_data = price_service.get_company_info(ticker)
            if not company_data:
                return None
            
            return CompanyInfo(
                ticker=company_data['ticker'],
                name=company_data['name'],
                sector=company_data['sector'],
                industry=company_data['industry'],
                market_cap=company_data['market_cap'],
                current_price=company_data['current_price'],
                currency=company_data['currency'],
                exchange=company_data['exchange']
            )
        except Exception as e:
            logger.error(f"Error fetching company info for {ticker}: {e}")
            return None

    @staticmethod
    def get_stock_price(ticker: str) -> Optional[StockPrice]:
        """Fetch current stock price and metrics using unified price service"""
        try:
            # Use unified price service for consistent data
            price_data = price_service.get_price_for_company_header(ticker)
            if not price_data:
                return None
            
            return StockPrice(
                current_price=price_data['current_price'],
                change=price_data['change'],
                change_percent=price_data['change_percent'],
                volume=price_data['volume'],
                market_cap=price_data['market_cap'],
                pe_ratio=price_data['pe_ratio'],
                pb_ratio=price_data['pb_ratio']
            )
        except Exception as e:
            logger.error(f"Error fetching stock price for {ticker}: {e}")
            return None

    @staticmethod
    def get_financial_data(ticker: str, years: int = 5) -> Optional[FinancialData]:
        """Fetch historical financial data for DCF analysis"""
        try:
            stock = yf.Ticker(ticker)
            
            # Get financial statements
            income_stmt = stock.financials.T
            balance_sheet = stock.balance_sheet.T
            cash_flow = stock.cashflow.T
            
            if income_stmt.empty or balance_sheet.empty or cash_flow.empty:
                logger.warning(f"Empty financial data for {ticker}")
                return None
            
            # Sort by year (most recent first)
            income_stmt = income_stmt.sort_index(ascending=False).head(years)
            balance_sheet = balance_sheet.sort_index(ascending=False).head(years)
            cash_flow = cash_flow.sort_index(ascending=False).head(years)
            
            years_list = [year.year for year in income_stmt.index]
            
            # Extract key metrics
            revenue = DataService._safe_extract(income_stmt, 'Total Revenue')
            ebitda = DataService._calculate_ebitda(income_stmt)
            net_income = DataService._safe_extract(income_stmt, 'Net Income')
            free_cash_flow = DataService._safe_extract(cash_flow, 'Free Cash Flow')
            total_debt = DataService._safe_extract(balance_sheet, 'Total Debt')
            cash = DataService._safe_extract(balance_sheet, 'Cash And Cash Equivalents')
            shares = DataService._safe_extract(balance_sheet, 'Ordinary Shares Number')
            
            # CRITICAL: Extract capital intensity metrics for dynamic calculation
            capex = DataService._safe_extract(cash_flow, 'Capital Expenditure')
            working_capital_change = DataService._safe_extract(cash_flow, 'Change In Working Capital')
            depreciation_amortization = DataService._safe_extract(cash_flow, 'Depreciation And Amortization')
            
            logger.info(f"📊 Financial data extracted for {ticker}: {len(revenue)} years, CapEx: {len([x for x in capex if x != 0])} non-zero values, WC: {len([x for x in working_capital_change if x != 0])} non-zero values, D&A: {len([x for x in depreciation_amortization if x != 0])} non-zero values")
            
            return FinancialData(
                ticker=ticker,
                years=years_list,
                revenue=revenue,
                ebitda=ebitda,
                net_income=net_income,
                free_cash_flow=free_cash_flow,
                total_debt=total_debt,
                cash=cash,
                shares_outstanding=shares,
                # Include capital intensity metrics
                capex=capex,
                working_capital_change=working_capital_change,
                depreciation_amortization=depreciation_amortization
            )
            
        except Exception as e:
            logger.error(f"Error fetching financial data for {ticker}: {e}")
            return None

    @staticmethod
    def _safe_extract(df: pd.DataFrame, column: str) -> List[float]:
        """Safely extract values from dataframe, handling missing data"""
        if column in df.columns:
            values = df[column].fillna(0).tolist()
        else:
            # Try alternative column names
            alt_names = {
                'Total Revenue': ['Revenue', 'Total Revenues'],
                'Net Income': ['Net Income Common Stockholders', 'Net Income Applicable To Common Shares'],
                'Free Cash Flow': ['Operating Cash Flow'],
                'Total Debt': ['Long Term Debt', 'Total Liabilities'],
                'Cash And Cash Equivalents': ['Cash', 'Cash Equivalents'],
                'Ordinary Shares Number': ['Share Issued', 'Common Stock Shares Outstanding'],
                # Capital intensity metrics alternative names
                'Capital Expenditure': ['Capital Expenditures', 'Capital Expenditure', 'Capex', 'Purchase Of Property Plant Equipment'],
                'Change In Working Capital': ['Working Capital', 'Change In Working Capital', 'Changes In Working Capital'],
                'Depreciation And Amortization': ['Depreciation Amortization', 'Depreciation And Amortization', 'Depreciation', 'Amortization']
            }
            
            found = False
            for alt_name in alt_names.get(column, []):
                if alt_name in df.columns:
                    values = df[alt_name].fillna(0).tolist()
                    found = True
                    break
            
            if not found:
                values = [0] * len(df)
        
        return [float(v) for v in values]

    @staticmethod
    def _calculate_ebitda(income_stmt: pd.DataFrame) -> List[float]:
        """Calculate EBITDA from income statement"""
        try:
            # Try to get EBITDA directly
            if 'EBITDA' in income_stmt.columns:
                return DataService._safe_extract(income_stmt, 'EBITDA')
            
            # Calculate EBITDA = EBIT + Depreciation & Amortization
            ebit = DataService._safe_extract(income_stmt, 'EBIT')
            if not ebit or all(x == 0 for x in ebit):
                # EBITDA = Net Income + Interest + Taxes + Depreciation + Amortization
                net_income = DataService._safe_extract(income_stmt, 'Net Income')
                interest = DataService._safe_extract(income_stmt, 'Interest Expense')
                tax = DataService._safe_extract(income_stmt, 'Tax Provision')
                depreciation = DataService._safe_extract(income_stmt, 'Depreciation And Amortization')
                
                ebitda = []
                for i in range(len(net_income)):
                    ebitda_val = net_income[i] + interest[i] + tax[i] + depreciation[i]
                    ebitda.append(ebitda_val)
                return ebitda
            else:
                depreciation = DataService._safe_extract(income_stmt, 'Depreciation And Amortization')
                return [ebit[i] + depreciation[i] for i in range(len(ebit))]
                
        except Exception as e:
            logger.error(f"Error calculating EBITDA: {e}")
            return [0] * len(income_stmt)

    @staticmethod
    def get_industry_multiples(ticker: str) -> Dict[str, float]:
        """Get industry average multiples for comparison"""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Return some default industry multiples
            # In a real application, you'd fetch these from a financial data provider
            return {
                'pe_ratio': info.get('trailingPE', 15.0),
                'pb_ratio': info.get('priceToBook', 2.0),
                'ev_ebitda': 10.0,  # Default assumption
                'price_to_sales': 2.5  # Default assumption
            }
        except Exception as e:
            logger.error(f"Error fetching industry multiples: {e}")
            return {
                'pe_ratio': 15.0,
                'pb_ratio': 2.0,
                'ev_ebitda': 10.0,
                'price_to_sales': 2.5
            }