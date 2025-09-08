# Peer Comparison Service
# Implements comprehensive peer analysis for v3 Summary Engine

import logging
import asyncio
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import yfinance as yf
from functools import lru_cache

from ..models.summary import InvestmentLabel

logger = logging.getLogger(__name__)

@dataclass
class PeerMetrics:
    """Comprehensive peer company metrics"""
    ticker: str
    company_name: str
    sector: str
    market_cap: float
    
    # Valuation metrics
    pe_ratio: float
    pb_ratio: float
    ev_ebitda: float
    price_to_sales: float
    
    # Financial metrics
    revenue_growth: float
    profit_margin: float
    roe: float
    roa: float
    debt_to_equity: float
    
    # Market performance
    price_performance_1m: float
    price_performance_3m: float
    price_performance_1y: float
    
    # Quality scores
    data_quality: str
    last_updated: datetime

@dataclass
class PeerComparisonResult:
    """Result of peer comparison analysis"""
    primary_ticker: str
    primary_metrics: PeerMetrics
    peers: List[PeerMetrics]
    
    # Comparative analysis
    valuation_percentile: float    # Where primary ranks in valuation (0-100)
    financial_percentile: float    # Where primary ranks in financial health
    performance_percentile: float  # Where primary ranks in market performance
    
    # Sector insights
    sector_median_pe: float
    sector_median_roe: float
    sector_median_growth: float
    
    # Recommendations
    relative_attractiveness: str   # "Attractive", "Neutral", "Expensive"
    key_differentiators: List[str]
    peer_advantages: List[str]
    
    # Meta
    analysis_timestamp: datetime
    peer_count: int
    data_warnings: List[str]

class PeerComparisonService:
    """
    Comprehensive peer comparison service for v3 Summary Engine
    
    Features:
    - Automatic peer selection by sector
    - Multi-dimensional peer ranking
    - Sector benchmark analysis
    - Relative valuation insights
    - Performance attribution
    """
    
    def __init__(self):
        # Sector-based peer mappings
        self.sector_peers = {
            "BFSI": {
                "large_cap": ["HDFCBANK", "SBIN", "ICICIBANK", "AXISBANK", "KOTAKBANK"],
                "mid_cap": ["FEDERALBNK", "INDUSINDBK", "BANDHANBNK", "AUBANK", "IDFCFIRSTB"],
                "nbfc": ["BAJFINANCE", "CHOLAFIN", "MUTHOOTFIN", "MANAPPURAM", "IIFL"]
            },
            "IT": {
                "tier_1": ["TCS", "INFY", "WIPRO", "HCLTECH", "TECHM"],
                "tier_2": ["MINDTREE", "LTTS", "COFORGE", "PERSISTENT", "LTIM"],
                "product": ["TATAELXSI", "CYIENT", "KPIT", "SONATSOFTWARE", "RPOWER"]
            },
            "PHARMA": {
                "large_cap": ["SUNPHARMA", "DRREDDY", "CIPLA", "LUPIN", "AUROPHARMA"],
                "mid_cap": ["BIOCON", "CADILAHC", "GLENMARK", "TORNTPHARM", "ABBOTINDIA"],
                "specialty": ["DIVIS", "LAXMIMACH", "SEQUENT", "SUDARSCHEM", "HIKAL"]
            },
            "FMCG": {
                "diversified": ["HINDUNILVR", "ITC", "NESTLEIND", "BRITANNIA", "DABUR"],
                "personal_care": ["GODREJCP", "MARICO", "EMAMILTD", "JYOTHYLAB", "HONASA"],
                "food": ["TATACONSUM", "VBL", "VARUN", "HATSUN", "PARAG"]
            },
            "AUTO": {
                "passenger_cars": ["MARUTI", "TATAMOTORS", "M&M", "BAJAJ-AUTO", "EICHERMOT"],
                "two_wheelers": ["HEROMOTOCO", "BAJAJ-AUTO", "TVSMOTORS", "EICHERMOT", "MOTHERSON"],
                "auto_ancillary": ["BOSCHLTD", "MOTHERSON", "BALKRISIND", "MRF", "APOLLOTYRE"]
            },
            "REALESTATE": {
                "residential": ["DLF", "GODREJPROP", "OBEROIRLTY", "PRESTIGE", "BRIGADE"],
                "commercial": ["PHOENIXLTD", "PRESTIGE", "BRIGADE", "SOBHA", "KOLTEPATIL"],
                "infrastructure": ["SUNTECK", "PHOENIXLTD", "MAHLIFE", "KOLTEPATIL", "SIGNATURE"]
            },
            "ENERGY": {
                "oil_gas": ["RELIANCE", "ONGC", "IOC", "BPCL", "HPCL"],
                "petrochemicals": ["RELIANCE", "IOC", "BPCL", "GAIL", "MGL"],
                "exploration": ["ONGC", "OIL", "CAIRN", "VEDL", "MOTHERSON"],
                "refining": ["RELIANCE", "IOC", "BPCL", "HPCL", "MRPL"]
            },
            "GENERAL": {
                "diversified": ["RELIANCE", "TATA", "ADANIGREEN", "LT", "ITC"],
                "conglomerate": ["BHARTIARTL", "WIPRO", "GODREJIND", "MAHINDRA", "TVSMOTOR"]
            }
        }
        
        # Cache for peer data to avoid repeated API calls
        self.peer_cache = {}
        self.cache_duration = timedelta(hours=2)  # 2-hour cache
        
        # Valuation percentile ranges
        self.percentile_ranges = {
            "attractive": (0, 30),      # Bottom 30% valuation = attractive
            "neutral": (30, 70),        # Middle 40% = neutral
            "expensive": (70, 100)      # Top 30% = expensive
        }
    
    async def analyze_peers(
        self, 
        ticker: str, 
        sector: str = None,
        peer_count: int = 5,
        include_financial_health: bool = True
    ) -> PeerComparisonResult:
        """
        Perform comprehensive peer comparison analysis
        
        Args:
            ticker: Primary stock ticker to analyze
            sector: Sector classification (auto-detected if None)
            peer_count: Number of peers to include (3-10)
            include_financial_health: Include financial health metrics
        
        Returns:
            PeerComparisonResult with comprehensive peer analysis
        """
        try:
            logger.info(f"Starting peer comparison analysis for {ticker}")
            
            # Step 1: Get primary company metrics
            primary_metrics = await self._fetch_company_metrics(ticker)
            if not primary_metrics:
                raise ValueError(f"Could not fetch metrics for primary ticker {ticker}")
            
            # Step 2: Auto-detect sector if not provided
            if not sector:
                sector = self._classify_sector(ticker)
            
            # Step 3: Select and fetch peer metrics
            peer_tickers = self._select_optimal_peers(ticker, sector, peer_count)
            peer_metrics = await self._fetch_peer_metrics_batch(peer_tickers)
            
            # Filter out failed fetches
            valid_peers = [p for p in peer_metrics if p is not None]
            
            if len(valid_peers) < 2:
                raise ValueError(f"Insufficient peer data: only {len(valid_peers)} peers available")
            
            # Step 4: Calculate comparative rankings
            valuation_percentile = self._calculate_valuation_percentile(primary_metrics, valid_peers)
            financial_percentile = self._calculate_financial_percentile(primary_metrics, valid_peers)
            performance_percentile = self._calculate_performance_percentile(primary_metrics, valid_peers)
            
            # Step 5: Calculate sector benchmarks
            sector_medians = self._calculate_sector_medians(valid_peers)
            
            # Step 6: Generate insights and recommendations
            relative_attractiveness = self._determine_relative_attractiveness(valuation_percentile)
            key_differentiators = self._identify_key_differentiators(primary_metrics, valid_peers)
            peer_advantages = self._identify_peer_advantages(primary_metrics, valid_peers)
            
            # Step 7: Collect data warnings
            data_warnings = self._generate_data_warnings(primary_metrics, valid_peers)
            
            result = PeerComparisonResult(
                primary_ticker=ticker,
                primary_metrics=primary_metrics,
                peers=valid_peers,
                valuation_percentile=valuation_percentile,
                financial_percentile=financial_percentile,
                performance_percentile=performance_percentile,
                sector_median_pe=sector_medians["pe_ratio"],
                sector_median_roe=sector_medians["roe"],
                sector_median_growth=sector_medians["revenue_growth"],
                relative_attractiveness=relative_attractiveness,
                key_differentiators=key_differentiators,
                peer_advantages=peer_advantages,
                analysis_timestamp=datetime.now(),
                peer_count=len(valid_peers),
                data_warnings=data_warnings
            )
            
            logger.info(f"Peer comparison completed for {ticker}: {relative_attractiveness} vs {len(valid_peers)} peers")
            return result
            
        except Exception as e:
            logger.error(f"Error in peer comparison for {ticker}: {e}")
            raise
    
    async def get_sector_overview(self, sector: str) -> Dict:
        """Get sector-wide overview and benchmarks"""
        try:
            if sector not in self.sector_peers:
                return {"error": f"Sector {sector} not supported"}
            
            # Get all tickers for sector
            all_tickers = []
            for category in self.sector_peers[sector].values():
                all_tickers.extend(category)
            
            # Fetch metrics for sector
            sector_metrics = await self._fetch_peer_metrics_batch(all_tickers[:15])  # Limit to 15
            valid_metrics = [m for m in sector_metrics if m is not None]
            
            if not valid_metrics:
                return {"error": f"No data available for sector {sector}"}
            
            # Calculate sector statistics
            sector_stats = self._calculate_comprehensive_sector_stats(valid_metrics)
            
            # Identify top and bottom performers
            top_performers = self._identify_top_performers(valid_metrics)
            bottom_performers = self._identify_bottom_performers(valid_metrics)
            
            return {
                "sector": sector,
                "analysis_date": datetime.now().isoformat(),
                "company_count": len(valid_metrics),
                "sector_statistics": sector_stats,
                "top_performers": top_performers,
                "bottom_performers": bottom_performers,
                "valuation_ranges": self._get_valuation_ranges(valid_metrics),
                "investment_themes": self._identify_sector_themes(valid_metrics)
            }
            
        except Exception as e:
            logger.error(f"Error getting sector overview for {sector}: {e}")
            return {"error": str(e)}
    
    async def get_sector_financial_benchmarks(
        self,
        sector: str,
        metrics: List[str] = None
    ) -> Dict:
        """
        Get sector financial benchmarks for Tab 2 (Key Ratios & Health)
        
        Args:
            sector: Sector classification (BFSI, IT, PHARMA, etc.)
            metrics: Specific metrics to benchmark (default: all key ratios)
            
        Returns:
            Dict with sector median, quartiles, and ranges for key financial ratios
        """
        try:
            if sector not in self.sector_peers:
                return {"error": f"Sector {sector} not supported"}
            
            # Default metrics for Tab 2 benchmarking
            if not metrics:
                metrics = [
                    'pe_ratio', 'pb_ratio', 'roe', 'profit_margin', 
                    'debt_to_equity', 'revenue_growth'
                ]
            
            # Get all tickers for sector
            all_tickers = []
            for category in self.sector_peers[sector].values():
                all_tickers.extend(category)
            
            # Fetch metrics for sector (limit to avoid rate limits)
            sector_metrics = await self._fetch_peer_metrics_batch(all_tickers[:12])
            valid_metrics = [m for m in sector_metrics if m is not None]
            
            if not valid_metrics:
                return {"error": f"No benchmark data available for sector {sector}"}
            
            # Calculate benchmarks for each requested metric
            benchmarks = {}
            
            for metric in metrics:
                values = []
                
                # Extract values based on metric name
                for company in valid_metrics:
                    value = getattr(company, metric, 0)
                    if value > 0:  # Only include positive values
                        values.append(value)
                
                if values:
                    values.sort()
                    n = len(values)
                    
                    benchmarks[metric] = {
                        "median": self._median(values),
                        "q1": values[n//4] if n >= 4 else values[0],
                        "q3": values[3*n//4] if n >= 4 else values[-1],
                        "min": min(values),
                        "max": max(values),
                        "count": len(values),
                        "sector_average": sum(values) / len(values)
                    }
                else:
                    benchmarks[metric] = {
                        "median": 0, "q1": 0, "q3": 0, "min": 0, "max": 0,
                        "count": 0, "sector_average": 0
                    }
            
            return {
                "sector": sector,
                "analysis_date": datetime.now().isoformat(),
                "company_count": len(valid_metrics),
                "benchmarks": benchmarks,
                "interpretation": self._generate_benchmark_interpretation(sector, benchmarks)
            }
            
        except Exception as e:
            logger.error(f"Error getting sector benchmarks for {sector}: {e}")
            return {"error": str(e)}
    
    def _generate_benchmark_interpretation(self, sector: str, benchmarks: Dict) -> Dict[str, str]:
        """Generate interpretation guidance for sector benchmarks"""
        
        interpretations = {}
        
        # PE Ratio interpretation
        if 'pe_ratio' in benchmarks and benchmarks['pe_ratio']['median'] > 0:
            pe_median = benchmarks['pe_ratio']['median']
            if pe_median < 15:
                interpretations['pe_ratio'] = f"Sector trades at attractive valuation (median PE: {pe_median:.1f})"
            elif pe_median < 25:
                interpretations['pe_ratio'] = f"Sector fairly valued (median PE: {pe_median:.1f})"
            else:
                interpretations['pe_ratio'] = f"Sector trading at premium valuation (median PE: {pe_median:.1f})"
        
        # ROE interpretation  
        if 'roe' in benchmarks and benchmarks['roe']['median'] > 0:
            roe_median = benchmarks['roe']['median'] * 100
            if roe_median > 20:
                interpretations['roe'] = f"Strong sector profitability (median ROE: {roe_median:.1f}%)"
            elif roe_median > 15:
                interpretations['roe'] = f"Good sector profitability (median ROE: {roe_median:.1f}%)"
            else:
                interpretations['roe'] = f"Moderate sector profitability (median ROE: {roe_median:.1f}%)"
        
        # Debt-to-Equity interpretation
        if 'debt_to_equity' in benchmarks and benchmarks['debt_to_equity']['median'] > 0:
            de_median = benchmarks['debt_to_equity']['median']
            if de_median < 0.5:
                interpretations['debt_to_equity'] = f"Conservative sector leverage (median D/E: {de_median:.2f})"
            elif de_median < 1.0:
                interpretations['debt_to_equity'] = f"Moderate sector leverage (median D/E: {de_median:.2f})"
            else:
                interpretations['debt_to_equity'] = f"High sector leverage (median D/E: {de_median:.2f})"
        
        return interpretations
    
    # Private helper methods
    
    async def _fetch_company_metrics(self, ticker: str) -> PeerMetrics:
        """Fetch comprehensive metrics for a single company"""
        
        cache_key = f"{ticker}_{datetime.now().strftime('%Y%m%d%H')}"
        if cache_key in self.peer_cache:
            return self.peer_cache[cache_key]
        
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            hist = stock.history(period="1y")
            
            if hist.empty:
                logger.warning(f"No price history available for {ticker}")
                return None
            
            # Calculate price performance
            current_price = hist["Close"].iloc[-1]
            price_1m = hist["Close"].iloc[-22] if len(hist) >= 22 else current_price
            price_3m = hist["Close"].iloc[-66] if len(hist) >= 66 else current_price
            price_1y = hist["Close"].iloc[0] if len(hist) >= 252 else current_price
            
            metrics = PeerMetrics(
                ticker=ticker,
                company_name=info.get("longName", ticker),
                sector=info.get("sector", "Unknown"),
                market_cap=info.get("marketCap", 0),
                
                # Valuation metrics
                pe_ratio=info.get("trailingPE", 0),
                pb_ratio=info.get("priceToBook", 0),
                ev_ebitda=info.get("enterpriseToEbitda", 0),
                price_to_sales=info.get("priceToSalesTrailing12Months", 0),
                
                # Financial metrics
                revenue_growth=info.get("revenueGrowth", 0),
                profit_margin=info.get("profitMargins", 0),
                roe=info.get("returnOnEquity", 0),
                roa=info.get("returnOnAssets", 0),
                debt_to_equity=info.get("debtToEquity", 0),
                
                # Performance metrics
                price_performance_1m=((current_price - price_1m) / price_1m) * 100,
                price_performance_3m=((current_price - price_3m) / price_3m) * 100,
                price_performance_1y=((current_price - price_1y) / price_1y) * 100,
                
                # Quality
                data_quality="High" if info.get("marketCap", 0) > 0 else "Medium",
                last_updated=datetime.now()
            )
            
            # Cache the result
            self.peer_cache[cache_key] = metrics
            return metrics
            
        except Exception as e:
            logger.warning(f"Failed to fetch metrics for {ticker}: {e}")
            return None
    
    async def _fetch_peer_metrics_batch(self, tickers: List[str]) -> List[PeerMetrics]:
        """Fetch metrics for multiple tickers concurrently"""
        
        # Create tasks for concurrent execution
        tasks = [self._fetch_company_metrics(ticker) for ticker in tickers]
        
        # Execute with limited concurrency to avoid rate limits
        semaphore = asyncio.Semaphore(5)  # Max 5 concurrent requests
        
        async def bounded_fetch(task):
            async with semaphore:
                return await task
        
        bounded_tasks = [bounded_fetch(task) for task in tasks]
        results = await asyncio.gather(*bounded_tasks, return_exceptions=True)
        
        # Filter out exceptions and None results
        valid_results = []
        for result in results:
            if isinstance(result, PeerMetrics):
                valid_results.append(result)
            elif isinstance(result, Exception):
                logger.warning(f"Peer fetch failed: {result}")
        
        return valid_results
    
    def _classify_sector(self, ticker: str) -> str:
        """Classify ticker into sector based on predefined mappings (legacy method)"""
        ticker_base = ticker.replace(".NS", "").replace(".BO", "")
        
        for sector, categories in self.sector_peers.items():
            for category, tickers in categories.items():
                if ticker_base in tickers:
                    return sector
        
        return "General"
    
    def _select_optimal_peers(self, ticker: str, sector: str, count: int) -> List[str]:
        """Select optimal peer companies for comparison"""
        ticker_base = ticker.replace(".NS", "").replace(".BO", "")
        
        if sector not in self.sector_peers:
            # Fallback to general large cap stocks
            return ["RELIANCE", "TCS", "HDFCBANK", "INFY", "ITC"][:count]
        
        # Collect all peers from sector, excluding primary ticker
        all_peers = []
        for category, tickers in self.sector_peers[sector].items():
            for peer_ticker in tickers:
                if peer_ticker != ticker_base and peer_ticker not in all_peers:
                    all_peers.append(peer_ticker)
        
        # Prioritize by category relevance and return top N
        return all_peers[:count]
    
    def _calculate_valuation_percentile(self, primary: PeerMetrics, peers: List[PeerMetrics]) -> float:
        """Calculate where primary company ranks in valuation vs peers"""
        
        # Create combined list for percentile calculation
        all_companies = [primary] + peers
        
        # Calculate composite valuation score (lower is better)
        valuation_scores = []
        for company in all_companies:
            # Normalize metrics (handle zero values)
            pe_score = company.pe_ratio if company.pe_ratio > 0 else 50  # Cap at 50
            pb_score = company.pb_ratio if company.pb_ratio > 0 else 10   # Cap at 10
            
            # Weighted composite (PE gets higher weight)
            composite = (pe_score * 0.6) + (pb_score * 0.4)
            valuation_scores.append(composite)
        
        primary_score = valuation_scores[0]
        
        # Calculate percentile (what % of peers are more expensive)
        more_expensive = sum(1 for score in valuation_scores[1:] if score > primary_score)
        percentile = (more_expensive / len(peers)) * 100
        
        return round(percentile, 1)
    
    def _calculate_financial_percentile(self, primary: PeerMetrics, peers: List[PeerMetrics]) -> float:
        """Calculate financial health percentile"""
        
        all_companies = [primary] + peers
        
        # Calculate composite financial health score (higher is better)
        financial_scores = []
        for company in all_companies:
            roe_score = max(company.roe * 100, 0)  # Convert to percentage
            margin_score = max(company.profit_margin * 100, 0)
            growth_score = max(company.revenue_growth * 100, -50)  # Cap negative at -50%
            
            # Debt penalty (lower D/E is better)
            debt_penalty = min(company.debt_to_equity / 100, 20)  # Cap penalty at 20 points
            
            composite = (roe_score * 0.4) + (margin_score * 0.3) + (growth_score * 0.2) - (debt_penalty * 0.1)
            financial_scores.append(composite)
        
        primary_score = financial_scores[0]
        
        # Calculate percentile (what % of peers have lower financial health)
        lower_health = sum(1 for score in financial_scores[1:] if score < primary_score)
        percentile = (lower_health / len(peers)) * 100
        
        return round(percentile, 1)
    
    def _calculate_performance_percentile(self, primary: PeerMetrics, peers: List[PeerMetrics]) -> float:
        """Calculate market performance percentile"""
        
        all_companies = [primary] + peers
        
        # Use 3-month performance as primary metric
        performance_scores = [company.price_performance_3m for company in all_companies]
        primary_performance = performance_scores[0]
        
        # Calculate percentile
        better_performers = sum(1 for perf in performance_scores[1:] if perf > primary_performance)
        percentile = (better_performers / len(peers)) * 100
        
        return round(100 - percentile, 1)  # Invert so higher percentile = better performance
    
    def _calculate_sector_medians(self, peers: List[PeerMetrics]) -> Dict[str, float]:
        """Calculate sector median values"""
        
        pe_ratios = [p.pe_ratio for p in peers if p.pe_ratio > 0]
        roes = [p.roe for p in peers if p.roe != 0]
        growths = [p.revenue_growth for p in peers if p.revenue_growth != 0]
        
        return {
            "pe_ratio": self._median(pe_ratios) if pe_ratios else 0,
            "roe": self._median(roes) if roes else 0,
            "revenue_growth": self._median(growths) if growths else 0
        }
    
    def _determine_relative_attractiveness(self, valuation_percentile: float) -> str:
        """Determine relative attractiveness based on valuation percentile"""
        
        if valuation_percentile <= self.percentile_ranges["attractive"][1]:
            return "Attractive"
        elif valuation_percentile <= self.percentile_ranges["neutral"][1]:
            return "Neutral"
        else:
            return "Expensive"
    
    def _identify_key_differentiators(self, primary: PeerMetrics, peers: List[PeerMetrics]) -> List[str]:
        """Identify key differentiators vs peers"""
        
        differentiators = []
        
        # Calculate peer medians for comparison
        peer_pe_median = self._median([p.pe_ratio for p in peers if p.pe_ratio > 0])
        peer_roe_median = self._median([p.roe for p in peers if p.roe != 0])
        peer_growth_median = self._median([p.revenue_growth for p in peers if p.revenue_growth != 0])
        peer_margin_median = self._median([p.profit_margin for p in peers if p.profit_margin != 0])
        
        # Compare primary to peer medians
        if primary.pe_ratio > 0 and peer_pe_median > 0:
            pe_diff = ((primary.pe_ratio - peer_pe_median) / peer_pe_median) * 100
            if abs(pe_diff) > 20:  # >20% difference
                direction = "higher" if pe_diff > 0 else "lower"
                differentiators.append(f"PE ratio {abs(pe_diff):.0f}% {direction} than peers")
        
        if primary.roe != 0 and peer_roe_median != 0:
            roe_diff = ((primary.roe - peer_roe_median) / abs(peer_roe_median)) * 100
            if abs(roe_diff) > 25:  # >25% difference
                direction = "higher" if roe_diff > 0 else "lower"
                differentiators.append(f"ROE {abs(roe_diff):.0f}% {direction} than sector median")
        
        if primary.revenue_growth != 0 and peer_growth_median != 0:
            growth_diff = (primary.revenue_growth - peer_growth_median) * 100
            if abs(growth_diff) > 5:  # >5% difference
                direction = "faster" if growth_diff > 0 else "slower"
                differentiators.append(f"Revenue growth {abs(growth_diff):.0f}pp {direction} than peers")
        
        return differentiators[:3]  # Top 3 differentiators
    
    def _identify_peer_advantages(self, primary: PeerMetrics, peers: List[PeerMetrics]) -> List[str]:
        """Identify areas where peers outperform primary"""
        
        advantages = []
        
        # Find peers that significantly outperform in key metrics
        better_roe_peers = [p for p in peers if p.roe > primary.roe * 1.2]  # 20% better ROE
        better_growth_peers = [p for p in peers if p.revenue_growth > primary.revenue_growth + 0.05]  # 5pp better growth
        better_margin_peers = [p for p in peers if p.profit_margin > primary.profit_margin * 1.3]  # 30% better margins
        
        if len(better_roe_peers) > len(peers) * 0.3:  # >30% of peers
            advantages.append(f"{len(better_roe_peers)} peers have significantly higher ROE")
        
        if len(better_growth_peers) > len(peers) * 0.3:
            advantages.append(f"{len(better_growth_peers)} peers showing faster revenue growth")
        
        if len(better_margin_peers) > len(peers) * 0.3:
            advantages.append(f"{len(better_margin_peers)} peers have better profit margins")
        
        return advantages[:3]
    
    def _generate_data_warnings(self, primary: PeerMetrics, peers: List[PeerMetrics]) -> List[str]:
        """Generate data quality warnings"""
        
        warnings = []
        
        if len(peers) < 3:
            warnings.append(f"Limited peer data: only {len(peers)} peers available")
        
        if primary.data_quality != "High":
            warnings.append("Primary company data quality is limited")
        
        low_quality_peers = [p for p in peers if p.data_quality != "High"]
        if len(low_quality_peers) > len(peers) * 0.5:
            warnings.append("More than half of peer data has quality issues")
        
        return warnings
    
    def _calculate_comprehensive_sector_stats(self, metrics: List[PeerMetrics]) -> Dict:
        """Calculate comprehensive sector statistics"""
        
        pe_ratios = [m.pe_ratio for m in metrics if m.pe_ratio > 0]
        roes = [m.roe for m in metrics if m.roe != 0]
        margins = [m.profit_margin for m in metrics if m.profit_margin != 0]
        growths = [m.revenue_growth for m in metrics]
        
        return {
            "valuation": {
                "median_pe": self._median(pe_ratios),
                "pe_range": [min(pe_ratios), max(pe_ratios)] if pe_ratios else [0, 0]
            },
            "profitability": {
                "median_roe": self._median(roes) * 100,
                "median_margin": self._median(margins) * 100,
                "roe_range": [min(roes) * 100, max(roes) * 100] if roes else [0, 0]
            },
            "growth": {
                "median_growth": self._median(growths) * 100,
                "growth_range": [min(growths) * 100, max(growths) * 100]
            }
        }
    
    def _identify_top_performers(self, metrics: List[PeerMetrics]) -> List[Dict]:
        """Identify top performing companies in sector"""
        
        # Score companies on composite metric
        scored_companies = []
        for metric in metrics:
            score = (metric.roe * 0.3) + (metric.profit_margin * 0.3) + (metric.revenue_growth * 0.2) + (max(0, -metric.price_performance_3m / 100) * 0.2)
            scored_companies.append({
                "ticker": metric.ticker,
                "company_name": metric.company_name,
                "composite_score": score,
                "key_strength": self._identify_key_strength(metric)
            })
        
        # Return top 3
        return sorted(scored_companies, key=lambda x: x["composite_score"], reverse=True)[:3]
    
    def _identify_bottom_performers(self, metrics: List[PeerMetrics]) -> List[Dict]:
        """Identify bottom performing companies in sector"""
        
        scored_companies = []
        for metric in metrics:
            score = (metric.roe * 0.3) + (metric.profit_margin * 0.3) + (metric.revenue_growth * 0.2) + (max(0, -metric.price_performance_3m / 100) * 0.2)
            scored_companies.append({
                "ticker": metric.ticker,
                "company_name": metric.company_name,
                "composite_score": score,
                "key_weakness": self._identify_key_weakness(metric)
            })
        
        # Return bottom 3
        return sorted(scored_companies, key=lambda x: x["composite_score"])[:3]
    
    def _get_valuation_ranges(self, metrics: List[PeerMetrics]) -> Dict:
        """Get valuation ranges for sector"""
        
        pe_ratios = [m.pe_ratio for m in metrics if m.pe_ratio > 0]
        pb_ratios = [m.pb_ratio for m in metrics if m.pb_ratio > 0]
        
        return {
            "pe_ratio": {
                "min": min(pe_ratios) if pe_ratios else 0,
                "median": self._median(pe_ratios) if pe_ratios else 0,
                "max": max(pe_ratios) if pe_ratios else 0
            },
            "pb_ratio": {
                "min": min(pb_ratios) if pb_ratios else 0,
                "median": self._median(pb_ratios) if pb_ratios else 0,
                "max": max(pb_ratios) if pb_ratios else 0
            }
        }
    
    def _identify_sector_themes(self, metrics: List[PeerMetrics]) -> List[str]:
        """Identify key investment themes in sector"""
        
        themes = []
        
        # Growth theme
        growth_stocks = [m for m in metrics if m.revenue_growth > 0.15]  # >15% growth
        if len(growth_stocks) > len(metrics) * 0.3:
            themes.append("Strong revenue growth across sector")
        
        # Valuation theme
        cheap_stocks = [m for m in metrics if m.pe_ratio > 0 and m.pe_ratio < 15]
        if len(cheap_stocks) > len(metrics) * 0.5:
            themes.append("Attractive valuations with low PE ratios")
        
        # Profitability theme
        profitable_stocks = [m for m in metrics if m.roe > 0.15]  # >15% ROE
        if len(profitable_stocks) > len(metrics) * 0.4:
            themes.append("Strong return on equity across sector")
        
        return themes
    
    def _identify_key_strength(self, metric: PeerMetrics) -> str:
        """Identify company's key strength"""
        
        if metric.roe > 0.20:
            return "High ROE"
        elif metric.revenue_growth > 0.20:
            return "Fast growth"
        elif metric.profit_margin > 0.15:
            return "High margins"
        elif metric.price_performance_1y > 20:
            return "Strong performance"
        else:
            return "Stable business"
    
    def _identify_key_weakness(self, metric: PeerMetrics) -> str:
        """Identify company's key weakness"""
        
        if metric.roe < 0.05:
            return "Low ROE"
        elif metric.revenue_growth < -0.05:
            return "Declining revenue"
        elif metric.profit_margin < 0.02:
            return "Low margins"
        elif metric.price_performance_1y < -20:
            return "Poor performance"
        else:
            return "High debt"
    
    def _median(self, values: List[float]) -> float:
        """Calculate median of list"""
        if not values:
            return 0
        
        sorted_values = sorted(values)
        n = len(sorted_values)
        
        if n % 2 == 0:
            return (sorted_values[n//2 - 1] + sorted_values[n//2]) / 2
        else:
            return sorted_values[n//2]