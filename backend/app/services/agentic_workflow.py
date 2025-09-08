import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import yfinance as yf
from .claude_service import claude_service
from .news_scraper import news_scraper

logger = logging.getLogger(__name__)

class AgenticWorkflowService:
    """
    Main service that orchestrates the AI agentic workflow for financial analysis.
    
    Implements the 4-step workflow:
    1. Data Ingestion (yfinance + news scraping)
    2. Generator Agent (initial analysis)
    3. Checker Agent (validation)
    4. Commentator Agents (bull/bear cases)
    """
    
    def __init__(self):
        self.progress_callbacks = []
    
    def _sanitize_nan_values(self, data):
        """Recursively replace NaN values with None for JSON serialization."""
        import math
        
        if isinstance(data, dict):
            return {k: self._sanitize_nan_values(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._sanitize_nan_values(item) for item in data]
        elif isinstance(data, float):
            if math.isnan(data) or math.isinf(data):
                return None
            return data
        else:
            return data
    
    def add_progress_callback(self, callback):
        """Add a progress callback function."""
        self.progress_callbacks.append(callback)
    
    def _notify_progress(self, step: str, progress: int, message: str):
        """Notify all progress callbacks."""
        for callback in self.progress_callbacks:
            try:
                callback(step, progress, message)
            except Exception as e:
                logger.error(f"Error in progress callback: {e}")
    
    async def execute_full_analysis(
        self,
        ticker: str,
        max_news_articles: int = 10,
        cancellation_checker: callable = None
    ) -> Optional[Dict[str, Any]]:
        """
        Execute the complete agentic workflow for a company.
        
        Args:
            ticker: Stock ticker symbol (e.g., 'RELIANCE.NS')
            max_news_articles: Maximum number of news articles to scrape
            
        Returns:
            Complete analysis including all agent outputs
        """
        if not claude_service.is_available():
            logger.error("Claude service not available - cannot execute agentic workflow")
            return None
        
        analysis_start = datetime.now()
        logger.info(f"Starting agentic workflow analysis for {ticker}")
        
        try:
            # Helper function to check for cancellation
            def _check_cancellation():
                if cancellation_checker and cancellation_checker():
                    raise asyncio.CancelledError("Analysis cancelled by user")
            
            # Step 1: Data Ingestion
            _check_cancellation()
            self._notify_progress("ingestion", 10, "Fetching company financial data...")
            company_data = await self._fetch_company_data(ticker)
            if not company_data:
                return None
            
            _check_cancellation()
            self._notify_progress("ingestion", 30, "Scraping recent news articles...")
            news_articles = await self._fetch_news_data(ticker, max_news_articles)
            
            _check_cancellation()
            self._notify_progress("ingestion", 50, "Data ingestion complete")
            
            # Step 2: Generator Agent
            _check_cancellation()
            self._notify_progress("generator", 55, "Running Generator Agent analysis...")
            generator_output = await claude_service.generator_agent(company_data, news_articles)
            if not generator_output:
                logger.error("Generator agent failed")
                return None
            
            _check_cancellation()
            self._notify_progress("generator", 70, "Generator Agent complete")
            
            # Step 3: Checker Agent
            _check_cancellation()
            self._notify_progress("checker", 75, "Running Checker Agent validation...")
            checker_output = await claude_service.checker_agent(generator_output)
            if not checker_output:
                logger.error("Checker agent failed")
                return None
            
            _check_cancellation()
            self._notify_progress("checker", 85, "Checker Agent complete")
            
            # Step 4: Commentator Agents (parallel execution)
            _check_cancellation()
            self._notify_progress("commentators", 90, "Running Bull/Bear Commentator Agents...")
            
            bull_task = claude_service.bull_commentator_agent(generator_output, checker_output)
            bear_task = claude_service.bear_commentator_agent(generator_output, checker_output)
            
            bull_output, bear_output = await asyncio.gather(bull_task, bear_task)
            
            if not bull_output or not bear_output:
                logger.error("Commentator agents failed")
                return None
            
            self._notify_progress("complete", 100, "Analysis complete!")
            
            # Compile final result
            analysis_duration = (datetime.now() - analysis_start).total_seconds()
            
            result = {
                "metadata": {
                    "ticker": ticker,
                    "company_name": company_data.get('info', {}).get('longName', ticker),
                    "analysis_timestamp": analysis_start.isoformat(),
                    "analysis_duration_seconds": analysis_duration,
                    "news_articles_analyzed": len(news_articles),
                    "workflow_version": "1.0"
                },
                "raw_data": {
                    "financial_data": company_data,
                    "news_articles": news_articles
                },
                "generator_analysis": generator_output,
                "validation_report": checker_output,
                "investment_commentary": {
                    "bull_case": bull_output,
                    "bear_case": bear_output
                },
                "dashboard_sections": self._format_for_dashboard(
                    company_data, generator_output, checker_output, bull_output, bear_output
                )
            }
            
            logger.info(f"Agentic workflow completed for {ticker} in {analysis_duration:.1f} seconds")
            return result
            
        except Exception as e:
            logger.error(f"Error in agentic workflow for {ticker}: {e}")
            self._notify_progress("error", 0, f"Analysis failed: {str(e)}")
            return None
    
    async def _fetch_company_data(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Fetch company financial data using yfinance."""
        try:
            logger.info(f"Fetching financial data for {ticker}")
            
            stock = yf.Ticker(ticker)
            
            # Get basic info
            info = stock.info
            if not info or not info.get('longName'):
                logger.error(f"No company info found for {ticker}")
                return None
            
            # Get historical data
            hist = stock.history(period="1y")
            
            # Get financial statements (if available)
            try:
                financials = stock.financials
                balance_sheet = stock.balance_sheet
                cash_flow = stock.cashflow
            except Exception as e:
                logger.warning(f"Could not fetch financial statements for {ticker}: {e}")
                financials = balance_sheet = cash_flow = None
            
            # Sanitize data to remove NaN values
            data = {
                "ticker": ticker,
                "info": info,
                "history": hist.to_dict() if not hist.empty else {},
                "financials": financials.to_dict() if financials is not None else {},
                "balance_sheet": balance_sheet.to_dict() if balance_sheet is not None else {},
                "cash_flow": cash_flow.to_dict() if cash_flow is not None else {},
                "fetched_at": datetime.now().isoformat()
            }
            
            return self._sanitize_nan_values(data)
            
        except Exception as e:
            logger.error(f"Error fetching company data for {ticker}: {e}")
            return None
    
    async def _fetch_news_data(self, ticker: str, max_articles: int) -> List[Dict[str, Any]]:
        """Fetch recent news articles for the company."""
        try:
            # Extract company name for better search
            stock = yf.Ticker(ticker)
            company_name = stock.info.get('longName', ticker.replace('.NS', ''))
            
            logger.info(f"Searching for news articles about {company_name}")
            
            # Set up progress tracking
            progress_callback = news_scraper.get_progress_callback()
            progress_callback.set_total(max_articles)
            
            async with news_scraper:
                articles = await news_scraper.search_company_news(
                    company_name=company_name,
                    ticker=ticker,
                    max_articles=max_articles,
                    days_back=30
                )
            
            logger.info(f"Found {len(articles)} news articles for {ticker}")
            return articles
            
        except Exception as e:
            logger.error(f"Error fetching news data for {ticker}: {e}")
            return []
    
    def _format_for_dashboard(
        self,
        company_data: Dict[str, Any],
        generator_output: Dict[str, Any],
        checker_output: Dict[str, Any],
        bull_output: Dict[str, Any],
        bear_output: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Format the analysis results for the dashboard sections."""
        try:
            info = company_data.get('info', {})
            current_price = info.get('currentPrice') or info.get('regularMarketPrice', 0)
            
            # Section 1: Qualitative Narrative
            qualitative_section = {
                "header_card": {
                    "company_name": info.get('longName', 'Unknown'),
                    "ticker": company_data.get('ticker', 'Unknown'),
                    "current_price": current_price,
                    "currency": info.get('currency', 'USD'),
                    "market_cap": info.get('marketCap', 0),
                    "sector": info.get('sector', 'Unknown'),
                    "industry": info.get('industry', 'Unknown')
                },
                "swot_analysis": generator_output.get('qualitative_analysis', {}).get('swot', {}),
                "news_sentiment": generator_output.get('qualitative_analysis', {}).get('news_sentiment', {}),
                "competitive_analysis": generator_output.get('qualitative_analysis', {}).get('competitive_analysis', {})
            }
            
            # Section 2: Interactive Quantitative Valuation
            quantitative_section = {
                "dcf_assumptions": generator_output.get('quantitative_analysis', {}).get('dcf_assumptions', {}),
                "sensitivity_analysis": generator_output.get('quantitative_analysis', {}).get('sensitivity_analysis', {})
            }
            
            # Section 3: AI Investment Committee
            investment_committee = {
                "validation_report": checker_output.get('validation_report', {}),
                "bull_commentary": bull_output.get('bull_commentary', {}),
                "bear_commentary": bear_output.get('bear_commentary', {})
            }
            
            return {
                "section_1_qualitative_narrative": qualitative_section,
                "section_2_quantitative_valuation": quantitative_section,
                "section_3_investment_committee": investment_committee
            }
            
        except Exception as e:
            logger.error(f"Error formatting dashboard data: {e}")
            return {}

# Global service instance
agentic_workflow = AgenticWorkflowService()