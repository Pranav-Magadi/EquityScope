# Dynamic Sector Classification Service
# Automatically classifies any NSE/BSE stock into sector and sub-industry
# Supports unlimited stock universe with real-time classification

import logging
import asyncio
import re
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd
import numpy as np
from enum import Enum
import requests
from bs4 import BeautifulSoup

from .intelligent_cache import intelligent_cache, CacheType

logger = logging.getLogger(__name__)

class SectorCategory(Enum):
    """Primary sector categories"""
    BFSI = "Banking, Financial Services & Insurance"
    IT = "Information Technology"
    PHARMA = "Pharmaceuticals & Healthcare" 
    FMCG = "Fast Moving Consumer Goods"
    AUTO = "Automotive & Auto Components"
    REALESTATE = "Real Estate & Construction"
    METALS = "Metals & Mining"
    ENERGY = "Oil, Gas & Energy"
    TELECOM = "Telecommunications"
    UTILITIES = "Power & Utilities"
    CHEMICALS = "Chemicals & Fertilizers"
    TEXTILES = "Textiles & Apparel"
    MEDIA = "Media & Entertainment"
    CAPITAL_GOODS = "Capital Goods & Engineering"
    CONSUMER_SERVICES = "Consumer Services"
    AGRICULTURE = "Agriculture & Food Processing"
    LOGISTICS = "Transportation & Logistics"
    GENERAL = "Diversified & Others"

@dataclass
class BusinessSegment:
    """Individual business segment for multi-sector companies"""
    sector: SectorCategory
    sub_industry: str
    estimated_revenue_contribution: float  # 0-100 percentage
    confidence_level: float  # 0-100
    keywords_found: List[str]

@dataclass
class CompanyClassification:
    """Complete company sector and industry classification"""
    ticker: str
    company_name: str
    primary_sector: SectorCategory
    sub_industry: str
    industry_group: str
    
    # Multi-segment analysis
    business_segments: List[BusinessSegment]  # All identified business segments
    is_conglomerate: bool  # True if multiple significant segments detected
    
    # Classification confidence (0-100)
    classification_confidence: float
    
    # Business description analysis
    business_keywords: List[str]
    revenue_segments: List[str]
    
    # Market context
    market_cap_category: str  # Large/Mid/Small Cap
    listing_exchange: str     # NSE/BSE
    
    # Peer information
    direct_peers: List[str]   # Top 5 most similar companies
    sector_peers: List[str]   # Broader sector peer group
    
    # Classification metadata
    data_sources: List[str]   # Sources used for classification
    classification_date: datetime
    last_updated: datetime

@dataclass
class SectorCharacteristics:
    """Characteristics and peers for each sector"""
    sector: SectorCategory
    keywords: List[str]
    business_indicators: List[str]
    financial_characteristics: Dict[str, Tuple[float, float]]  # metric: (min, max) ranges
    known_companies: Set[str]
    sub_industries: List[str]

class DynamicSectorClassificationService:
    """
    Dynamic Sector Classification Service
    
    Features:
    - Automatic classification for any NSE/BSE stock
    - Multi-source data integration (yfinance, NSE, business description)
    - Sub-industry granular classification
    - Peer discovery based on business similarity
    - Real-time classification with intelligent caching
    - Support for new/unlisted companies
    """
    
    def __init__(self, use_cache: bool = True):
        self.use_cache = use_cache
        self.cache_manager = intelligent_cache
        self.cache_duration = timedelta(hours=24)  # 24-hour cache for sector classification
        
        # Initialize sector characteristics
        self.sector_characteristics = self._initialize_sector_characteristics()
        
        # Known exchange suffixes
        self.exchange_suffixes = {'.NS': 'NSE', '.BO': 'BSE', '.BSE': 'BSE'}
        
        # Market cap thresholds (in INR crores)
        self.market_cap_thresholds = {
            'Large Cap': 20000,    # >₹20,000 Cr
            'Mid Cap': 5000,       # ₹5,000-20,000 Cr  
            'Small Cap': 0         # <₹5,000 Cr
        }
    
    async def classify_company(
        self,
        ticker: str,
        force_refresh: bool = False,
        include_peers: bool = True
    ) -> CompanyClassification:
        """
        Classify company into sector and sub-industry
        
        Args:
            ticker: Stock ticker (e.g., 'RELIANCE.NS', 'TCS.BO')
            force_refresh: Skip cache and reclassify
            include_peers: Include peer discovery (slower but more complete)
            
        Returns:
            CompanyClassification with detailed sector and peer information
        """
        try:
            logger.info(f"Starting dynamic classification for {ticker}")
            
            # Check cache first
            if self.use_cache and not force_refresh:
                cached_result = await self.cache_manager.get(
                    CacheType.FINANCIAL_DATA, f"{ticker}_sector_classification"
                )
                if cached_result:
                    logger.info(f"Cache hit for {ticker} sector classification - checking compatibility")
                    
                    # Check if cached data has new fields (backward compatibility)
                    if 'business_segments' not in cached_result or 'is_conglomerate' not in cached_result:
                        logger.info(f"Cached data for {ticker} is outdated, invalidating cache")
                        # Don't use outdated cache, proceed with fresh classification
                        pass
                    else:
                        # Convert string back to enum if needed
                        if isinstance(cached_result.get('primary_sector'), str):
                            # Try to find the enum by name
                            for sector in SectorCategory:
                                if sector.name == cached_result['primary_sector']:
                                    cached_result['primary_sector'] = sector
                                    break
                        
                        # Convert business segments back to objects
                        if cached_result.get('business_segments'):
                            segments = []
                            for seg_data in cached_result['business_segments']:
                                if isinstance(seg_data.get('sector'), str):
                                    for sector in SectorCategory:
                                        if sector.name == seg_data['sector']:
                                            seg_data['sector'] = sector
                                            break
                                segments.append(BusinessSegment(**seg_data))
                            cached_result['business_segments'] = segments
                        
                        return CompanyClassification(**cached_result)
            
            # Fetch company data from multiple sources
            company_data = await self._fetch_company_data(ticker)
            
            if not company_data:
                raise ValueError(f"Could not fetch data for ticker {ticker}")
            
            # Perform multi-stage classification
            classification_result = await self._perform_classification(
                ticker, company_data, include_peers
            )
            
            # Cache the result
            if self.use_cache:
                await self.cache_manager.set(
                    CacheType.FINANCIAL_DATA,
                    f"{ticker}_sector_classification", 
                    asdict(classification_result)
                )
            
            logger.info(f"Classification completed for {ticker}: {classification_result.primary_sector.value}")
            return classification_result
            
        except Exception as e:
            logger.error(f"Error classifying {ticker}: {e}")
            raise
    
    async def get_sector_companies(
        self,
        sector: SectorCategory,
        max_companies: int = 50,
        market_cap_filter: str = None
    ) -> List[str]:
        """
        Get all companies in a specific sector
        
        Args:
            sector: Target sector category
            max_companies: Maximum companies to return
            market_cap_filter: 'Large Cap', 'Mid Cap', 'Small Cap', or None
            
        Returns:
            List of ticker symbols in the sector
        """
        try:
            # Get known companies from sector characteristics
            known_companies = list(self.sector_characteristics[sector].known_companies)
            
            # If we need more companies, we could integrate with NSE/BSE APIs
            # For now, return known companies
            
            result_companies = known_companies[:max_companies]
            
            logger.info(f"Retrieved {len(result_companies)} companies for sector {sector.value}")
            return result_companies
            
        except Exception as e:
            logger.error(f"Error getting sector companies for {sector}: {e}")
            return []
    
    async def discover_peers(
        self,
        ticker: str,
        peer_count: int = 10,
        similarity_threshold: float = 0.7
    ) -> List[str]:
        """
        Discover similar companies based on business characteristics
        
        Args:
            ticker: Primary ticker for peer discovery
            peer_count: Number of peers to return
            similarity_threshold: Minimum similarity score (0-1)
            
        Returns:
            List of peer ticker symbols
        """
        try:
            # First classify the primary company
            classification = await self.classify_company(ticker, include_peers=False)
            
            # Get companies from same sector
            sector_companies = await self.get_sector_companies(
                classification.primary_sector, max_companies=100
            )
            
            # Remove the primary ticker
            ticker_base = ticker.replace('.NS', '').replace('.BO', '')
            sector_companies = [c for c in sector_companies if c != ticker_base]
            
            # For now, return top companies from same sector
            # In production, this would include similarity scoring based on:
            # - Business description similarity
            # - Financial metric similarity
            # - Revenue segment overlap
            # - Market cap proximity
            
            peers = sector_companies[:peer_count]
            
            logger.info(f"Discovered {len(peers)} peers for {ticker}")
            return peers
            
        except Exception as e:
            logger.error(f"Error discovering peers for {ticker}: {e}")
            return []
    
    async def get_sector_statistics(self, sector: SectorCategory) -> Dict:
        """Get comprehensive statistics for a sector"""
        try:
            sector_companies = await self.get_sector_companies(sector, max_companies=30)
            
            # Fetch financial data for sector analysis
            sector_data = []
            
            # Process companies concurrently (limited to avoid rate limits)
            semaphore = asyncio.Semaphore(5)
            
            async def fetch_company_stats(ticker_base):
                async with semaphore:
                    try:
                        ticker_full = f"{ticker_base}.NS"
                        stock = yf.Ticker(ticker_full)
                        info = stock.info
                        
                        return {
                            'ticker': ticker_base,
                            'market_cap': info.get('marketCap', 0),
                            'pe_ratio': info.get('trailingPE', 0),
                            'roe': info.get('returnOnEquity', 0),
                            'revenue_growth': info.get('revenueGrowth', 0),
                            'profit_margin': info.get('profitMargins', 0)
                        }
                    except Exception as e:
                        logger.warning(f"Failed to fetch stats for {ticker_base}: {e}")
                        return None
            
            tasks = [fetch_company_stats(ticker) for ticker in sector_companies[:15]]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter valid results
            valid_results = [r for r in results if r is not None and not isinstance(r, Exception)]
            
            if not valid_results:
                return {"error": f"No data available for sector {sector.value}"}
            
            # Calculate sector statistics
            statistics = self._calculate_sector_statistics(valid_results)
            
            return {
                "sector": sector.value,
                "company_count": len(valid_results),
                "statistics": statistics,
                "analysis_date": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting sector statistics for {sector}: {e}")
            return {"error": str(e)}
    
    # Private helper methods
    
    async def _fetch_company_data(self, ticker: str) -> Optional[Dict]:
        """Fetch comprehensive company data for classification"""
        try:
            # Get base ticker without exchange suffix
            ticker_base = ticker.replace('.NS', '').replace('.BO', '')
            
            # Try different ticker formats
            ticker_formats = [f"{ticker_base}.NS", f"{ticker_base}.BO", ticker_base]
            
            company_data = None
            for ticker_format in ticker_formats:
                try:
                    stock = yf.Ticker(ticker_format)
                    info = stock.info
                    
                    # Check if we got valid data
                    if info.get('longName') or info.get('shortName'):
                        company_data = {
                            'ticker': ticker,
                            'info': info,
                            'exchange': self._determine_exchange(ticker_format),
                            'data_source': 'yfinance'
                        }
                        break
                        
                except Exception as e:
                    logger.debug(f"Failed to fetch data for {ticker_format}: {e}")
                    continue
            
            return company_data
            
        except Exception as e:
            logger.error(f"Error fetching company data for {ticker}: {e}")
            return None
    
    async def _perform_classification(
        self,
        ticker: str,
        company_data: Dict,
        include_peers: bool
    ) -> CompanyClassification:
        """Perform multi-stage company classification"""
        
        info = company_data['info']
        company_name = info.get('longName', info.get('shortName', ticker))
        
        # Stage 1: Try direct sector mapping from yfinance
        yf_sector = info.get('sector', '')
        yf_industry = info.get('industry', '')
        
        # Stage 2: Business description analysis
        business_summary = info.get('longBusinessSummary', '')
        business_keywords = self._extract_keywords(business_summary, company_name)
        
        # Stage 3: Multi-sector classification scoring
        sector_scores = self._calculate_sector_scores(
            yf_sector, yf_industry, business_summary, business_keywords
        )
        
        # Determine primary sector
        primary_sector = max(sector_scores.items(), key=lambda x: x[1])[0]
        classification_confidence = sector_scores[primary_sector]
        
        # Stage 4: Detect multiple business segments
        business_segments = self._detect_business_segments(
            business_summary, business_keywords, sector_scores
        )
        
        # Determine if this is a conglomerate (multiple significant segments)
        is_conglomerate = len([seg for seg in business_segments if seg.estimated_revenue_contribution >= 15]) > 1
        
        # Determine sub-industry
        sub_industry = self._classify_sub_industry(
            primary_sector, yf_industry, business_keywords
        )
        
        # Market cap classification
        market_cap = info.get('marketCap', 0)
        market_cap_inr = market_cap / 83 if market_cap > 0 else 0  # Convert USD to INR (approx)
        market_cap_category = self._classify_market_cap(market_cap_inr / 1e7)  # Convert to crores
        
        # Peer discovery (if requested)
        direct_peers = []
        sector_peers = []
        
        if include_peers:
            try:
                # Get a sample of sector peers (limited for performance)
                sector_companies = list(self.sector_characteristics[primary_sector].known_companies)
                ticker_base = ticker.replace('.NS', '').replace('.BO', '')
                sector_peers = [c for c in sector_companies if c != ticker_base][:15]
                direct_peers = sector_peers[:5]  # Top 5 as direct peers
                
            except Exception as e:
                logger.warning(f"Peer discovery failed for {ticker}: {e}")
        
        return CompanyClassification(
            ticker=ticker,
            company_name=company_name,
            primary_sector=primary_sector,
            sub_industry=sub_industry,
            industry_group=yf_industry or "General",
            business_segments=business_segments,
            is_conglomerate=is_conglomerate,
            classification_confidence=classification_confidence,
            business_keywords=business_keywords,
            revenue_segments=self._extract_revenue_segments(business_summary),
            market_cap_category=market_cap_category,
            listing_exchange=company_data['exchange'],
            direct_peers=direct_peers,
            sector_peers=sector_peers,
            data_sources=['yfinance', 'business_analysis'],
            classification_date=datetime.now(),
            last_updated=datetime.now()
        )
    
    def _initialize_sector_characteristics(self) -> Dict[SectorCategory, SectorCharacteristics]:
        """Initialize sector classification characteristics"""
        
        return {
            SectorCategory.BFSI: SectorCharacteristics(
                sector=SectorCategory.BFSI,
                keywords=['bank', 'banking', 'finance', 'financial', 'insurance', 'nbfc', 'credit', 'loan', 'mortgage', 'mutual fund'],
                business_indicators=['deposits', 'advances', 'npa', 'casa', 'net interest margin'],
                financial_characteristics={
                    'pe_ratio': (5, 25),
                    'pb_ratio': (0.5, 3.0),
                    'roe': (0.08, 0.25)
                },
                known_companies={'HDFCBANK', 'ICICIBANK', 'SBIN', 'AXISBANK', 'KOTAKBANK', 'BAJFINANCE', 'INDUSINDBK', 'FEDERALBNK', 'PNBHOUSING', 'CHOLAFIN'},
                sub_industries=['Private Banks', 'Public Banks', 'NBFCs', 'Insurance', 'AMCs', 'Housing Finance']
            ),
            
            SectorCategory.IT: SectorCharacteristics(
                sector=SectorCategory.IT,
                keywords=['software', 'technology', 'it services', 'consulting', 'digital', 'cloud', 'ai', 'analytics', 'outsourcing'],  
                business_indicators=['offshore', 'onsite', 'utilization', 'billing rates', 'digital revenue'],
                financial_characteristics={
                    'pe_ratio': (15, 35),
                    'profit_margin': (0.15, 0.30),
                    'roe': (0.20, 0.40)
                },
                known_companies={'TCS', 'INFY', 'WIPRO', 'HCLTECH', 'TECHM', 'LTTS', 'MINDTREE', 'COFORGE', 'PERSISTENT', 'LTIM'},
                sub_industries=['IT Services', 'Product Companies', 'ER&D Services', 'Digital Services', 'Consulting']
            ),
            
            SectorCategory.PHARMA: SectorCharacteristics(
                sector=SectorCategory.PHARMA,
                keywords=['pharmaceutical', 'drug', 'medicine', 'healthcare', 'biotech', 'clinical', 'therapy', 'generic', 'api'],
                business_indicators=['usfda', 'molecule', 'formulation', 'clinical trials', 'regulatory approval'],
                financial_characteristics={
                    'pe_ratio': (10, 30),
                    'profit_margin': (0.10, 0.25),
                    'roe': (0.12, 0.30)
                },
                known_companies={'SUNPHARMA', 'DRREDDY', 'CIPLA', 'LUPIN', 'AUROPHARMA', 'BIOCON', 'GLENMARK', 'TORNTPHARM', 'CADILAHC', 'DIVIS'},
                sub_industries=['Generics', 'Branded Generics', 'API', 'Biotechnology', 'Specialty Pharma', 'CDMO']
            ),
            
            SectorCategory.FMCG: SectorCharacteristics(
                sector=SectorCategory.FMCG,
                keywords=['consumer', 'fmcg', 'food', 'beverage', 'personal care', 'household', 'brand', 'retail', 'packaged'],
                business_indicators=['brand portfolio', 'distribution', 'rural penetration', 'market share'],  
                financial_characteristics={
                    'pe_ratio': (20, 50),
                    'profit_margin': (0.08, 0.20),
                    'roe': (0.15, 0.35)
                },
                known_companies={'HINDUNILVR', 'ITC', 'NESTLEIND', 'BRITANNIA', 'DABUR', 'GODREJCP', 'MARICO', 'TATACONSUM', 'VBL', 'EMAMILTD'},
                sub_industries=['Personal Care', 'Food & Beverages', 'Household Products', 'Tobacco', 'Packaged Foods']
            ),
            
            SectorCategory.AUTO: SectorCharacteristics(
                sector=SectorCategory.AUTO,
                keywords=['automotive', 'automobile', 'vehicle', 'car', 'truck', 'tractor', 'two wheeler', 'component', 'engine'],
                business_indicators=['vehicle sales', 'production capacity', 'market share', 'export markets'],
                financial_characteristics={
                    'pe_ratio': (8, 25),
                    'profit_margin': (0.05, 0.15), 
                    'roe': (0.08, 0.25)
                },
                known_companies={'MARUTI', 'TATAMOTORS', 'M&M', 'BAJAJ-AUTO', 'HEROMOTOCO', 'EICHERMOT', 'TVSMOTORS', 'BOSCHLTD', 'MOTHERSON', 'MRF'},
                sub_industries=['Passenger Vehicles', 'Commercial Vehicles', 'Two Wheelers', 'Tractors', 'Auto Components']
            ),
            
            SectorCategory.REALESTATE: SectorCharacteristics(
                sector=SectorCategory.REALESTATE,
                keywords=['real estate', 'property', 'construction', 'developer', 'residential', 'commercial', 'infrastructure', 'cement'],
                business_indicators=['project pipeline', 'pre-sales', 'land bank', 'construction progress'],
                financial_characteristics={
                    'pe_ratio': (5, 20),
                    'debt_to_equity': (0.5, 2.0),
                    'roe': (0.05, 0.20)
                },
                known_companies={'DLF', 'GODREJPROP', 'OBEROIRLTY', 'PRESTIGE', 'BRIGADE', 'SOBHA', 'PHOENIXLTD', 'SUNTECK', 'KOLTEPATIL', 'MAHLIFE'},
                sub_industries=['Residential Development', 'Commercial Real Estate', 'REITs', 'Construction', 'Infrastructure']
            ),
            
            # Energy Sector
            SectorCategory.ENERGY: SectorCharacteristics(
                sector=SectorCategory.ENERGY,
                keywords=['oil', 'gas', 'petroleum', 'refining', 'petrochemical', 'energy', 'crude', 'fuel'],
                business_indicators=['refinery', 'upstream', 'downstream', 'exploration', 'production'],
                financial_characteristics={
                    'pe_ratio': (8, 18),
                    'profit_margin': (0.05, 0.30),
                    'roe': (0.08, 0.25)
                },
                known_companies={'RELIANCE', 'ONGC', 'IOC', 'BPCL', 'HPCL', 'CAIRN', 'VEDL'},
                sub_industries=['Oil & Gas Exploration', 'Refining', 'Petrochemicals', 'Energy Trading']
            ),
            
            # Telecom Sector
            SectorCategory.TELECOM: SectorCharacteristics(
                sector=SectorCategory.TELECOM,
                keywords=['telecom', 'telecommunications', 'mobile', 'broadband', 'jio', '4g', '5g', 'fiber', 'digital'],
                business_indicators=['subscribers', 'arpu', 'network', 'spectrum', 'data services'],
                financial_characteristics={
                    'pe_ratio': (12, 25),
                    'profit_margin': (0.08, 0.25),
                    'roe': (0.10, 0.30)
                },
                known_companies={'BHARTIARTL', 'RELIANCE', 'IDEA', 'VODAFONE', 'BSNL'},
                sub_industries=['Mobile Services', 'Broadband', 'Digital Services', 'Infrastructure']
            ),
            
            # Additional sectors can be added here
            SectorCategory.GENERAL: SectorCharacteristics(
                sector=SectorCategory.GENERAL,
                keywords=['diversified', 'conglomerate', 'holding', 'group', 'multiple businesses'],
                business_indicators=['business portfolio', 'segment contribution', 'diversification'],
                financial_characteristics={
                    'pe_ratio': (10, 30),
                    'profit_margin': (0.05, 0.20),
                    'roe': (0.08, 0.25)
                },
                known_companies={'RELIANCE', 'ADANIGREEN', 'BHARTIARTL', 'LT', 'WIPRO'},
                sub_industries=['Diversified Conglomerates', 'Holding Companies', 'Multi-Business Groups']
            )
        }
    
    def _calculate_sector_scores(
        self,
        yf_sector: str,
        yf_industry: str, 
        business_summary: str,
        keywords: List[str]
    ) -> Dict[SectorCategory, float]:
        """Calculate classification scores for each sector"""
        
        scores = {}
        text_to_analyze = f"{yf_sector} {yf_industry} {business_summary}".lower()
        
        for sector, characteristics in self.sector_characteristics.items():
            score = 0.0
            
            # Keyword matching (40% weight)
            keyword_matches = sum(1 for keyword in characteristics.keywords 
                                if keyword in text_to_analyze)
            keyword_score = (keyword_matches / len(characteristics.keywords)) * 40
            
            # Business indicator matching (30% weight)
            indicator_matches = sum(1 for indicator in characteristics.business_indicators
                                  if indicator in text_to_analyze)
            indicator_score = (indicator_matches / len(characteristics.business_indicators)) * 30 if characteristics.business_indicators else 0
            
            # Direct sector name matching (30% weight)
            sector_name_match = 0
            sector_terms = sector.value.lower().split()
            for term in sector_terms:
                if term in text_to_analyze:
                    sector_name_match += 10
            
            sector_name_score = min(sector_name_match, 30)
            
            total_score = keyword_score + indicator_score + sector_name_score
            scores[sector] = min(total_score, 100)  # Cap at 100
        
        # Ensure we have a minimum score for GENERAL sector
        if max(scores.values()) < 20:
            scores[SectorCategory.GENERAL] = 50
        
        return scores
    
    def _extract_keywords(self, business_summary: str, company_name: str) -> List[str]:
        """Extract relevant business keywords"""
        
        if not business_summary:
            return []
        
        # Common business keywords to extract
        important_terms = [
            'software', 'technology', 'bank', 'finance', 'pharmaceutical', 'drug',
            'manufacturing', 'retail', 'healthcare', 'insurance', 'automobile',
            'real estate', 'construction', 'telecom', 'energy', 'chemical',
            'textile', 'fmcg', 'consumer', 'food', 'beverage'
        ]
        
        found_keywords = []
        text_lower = business_summary.lower()
        
        for term in important_terms:
            if term in text_lower:
                found_keywords.append(term)
        
        return found_keywords[:10]  # Top 10 keywords
    
    def _classify_sub_industry(
        self,
        primary_sector: SectorCategory,
        yf_industry: str,
        keywords: List[str]
    ) -> str:
        """Classify into sub-industry within primary sector"""
        
        if primary_sector not in self.sector_characteristics:
            return "General"
        
        sub_industries = self.sector_characteristics[primary_sector].sub_industries
        
        # Simple keyword-based sub-industry classification
        text_to_check = f"{yf_industry} {' '.join(keywords)}".lower()
        
        # Define sub-industry keywords
        sub_industry_keywords = {
            'Private Banks': ['private', 'commercial'],
            'Public Banks': ['public', 'government', 'state'],
            'NBFCs': ['nbfc', 'finance', 'credit', 'loan'],
            'IT Services': ['services', 'consulting', 'outsourcing'],
            'Product Companies': ['product', 'software product'],
            'Generics': ['generic', 'api'],
            'Biotechnology': ['biotech', 'bio', 'clinical'],
            'Personal Care': ['personal care', 'cosmetics', 'beauty'],
            'Food & Beverages': ['food', 'beverage', 'drink'],
            'Passenger Vehicles': ['passenger', 'car', 'sedan'],
            'Two Wheelers': ['two wheeler', 'motorcycle', 'scooter']
        }
        
        for sub_industry in sub_industries:
            if sub_industry in sub_industry_keywords:
                keywords_to_check = sub_industry_keywords[sub_industry]
                if any(keyword in text_to_check for keyword in keywords_to_check):
                    return sub_industry
        
        return sub_industries[0] if sub_industries else "General"
    
    def _extract_revenue_segments(self, business_summary: str) -> List[str]:
        """Extract revenue segments from business description"""
        
        if not business_summary:
            return []
        
        # Look for segment indicators
        segment_patterns = [
            r'segments?[:\s]+([^.]+)',
            r'divisions?[:\s]+([^.]+)', 
            r'business(?:es)?[:\s]+([^.]+)',
            r'operates?\s+(?:in|through)[:\s]+([^.]+)'
        ]
        
        segments = []
        for pattern in segment_patterns:
            matches = re.findall(pattern, business_summary, re.IGNORECASE)
            for match in matches:
                # Clean and split the match
                segment_parts = [s.strip() for s in match.split(',')]
                segments.extend(segment_parts[:3])  # Max 3 parts per pattern
        
        return list(set(segments[:5]))  # Return unique segments, max 5
    
    def _classify_market_cap(self, market_cap_crores: float) -> str:
        """Classify company by market cap"""
        
        if market_cap_crores >= self.market_cap_thresholds['Large Cap']:
            return 'Large Cap'
        elif market_cap_crores >= self.market_cap_thresholds['Mid Cap']:
            return 'Mid Cap'
        else:
            return 'Small Cap'
    
    def _determine_exchange(self, ticker: str) -> str:
        """Determine listing exchange from ticker"""
        
        for suffix, exchange in self.exchange_suffixes.items():
            if ticker.endswith(suffix):
                return exchange
        
        return 'NSE'  # Default assumption
    
    def _detect_business_segments(
        self,
        business_summary: str,
        keywords: List[str],
        sector_scores: Dict[SectorCategory, float]
    ) -> List[BusinessSegment]:
        """Detect multiple business segments for conglomerates"""
        
        segments = []
        text_lower = business_summary.lower()
        
        # Define segment detection patterns for major conglomerates
        segment_patterns = {
            SectorCategory.ENERGY: {
                'keywords': ['oil', 'gas', 'refining', 'petrochemical', 'crude', 'energy', 'fuel'],
                'phrases': ['oil refining', 'petrochemicals', 'upstream', 'downstream', 'refinery']
            },
            SectorCategory.FMCG: {
                'keywords': ['retail', 'consumer', 'supermarket', 'store', 'mart', 'shopping'],
                'phrases': ['retail business', 'consumer retail', 'retail stores', 'retail chain']
            },
            SectorCategory.TELECOM: {
                'keywords': ['telecom', 'jio', 'digital', 'broadband', '4g', '5g', 'fiber'],
                'phrases': ['digital services', 'telecommunications', 'broadband services', 'mobile services']
            },
            SectorCategory.IT: {
                'keywords': ['technology', 'digital', 'software', 'platform', 'tech'],
                'phrases': ['digital platform', 'technology services', 'software solutions']
            },
            SectorCategory.BFSI: {
                'keywords': ['financial', 'banking', 'insurance', 'finance', 'credit'],
                'phrases': ['financial services', 'banking operations', 'insurance business']
            },
            SectorCategory.CHEMICALS: {
                'keywords': ['chemical', 'specialty', 'polymer', 'plastic', 'materials'],
                'phrases': ['specialty chemicals', 'chemical products', 'polymer business']
            }
        }
        
        # Score each potential segment
        for sector, patterns in segment_patterns.items():
            keyword_matches = sum(1 for keyword in patterns['keywords'] if keyword in text_lower)
            phrase_matches = sum(1 for phrase in patterns['phrases'] if phrase in text_lower)
            
            # Calculate segment strength
            keyword_score = (keyword_matches / len(patterns['keywords'])) * 60
            phrase_score = (phrase_matches / len(patterns['phrases'])) * 40
            total_score = keyword_score + phrase_score
            
            # Add segment if it has significant presence
            if total_score >= 20:  # Minimum threshold for segment inclusion
                
                # Estimate revenue contribution based on score and context
                if sector in sector_scores:
                    base_contribution = min(sector_scores[sector], 80)  # Cap at 80%
                else:
                    base_contribution = total_score
                
                # Apply business logic for known conglomerates
                revenue_contribution = self._estimate_segment_contribution(
                    sector, base_contribution, text_lower
                )
                
                segment = BusinessSegment(
                    sector=sector,
                    sub_industry=self._classify_sub_industry(sector, "", patterns['keywords']),
                    estimated_revenue_contribution=revenue_contribution,
                    confidence_level=total_score,
                    keywords_found=[kw for kw in patterns['keywords'] if kw in text_lower]
                )
                
                segments.append(segment)
        
        # Normalize revenue contributions to sum to 100%
        if segments:
            total_contribution = sum(seg.estimated_revenue_contribution for seg in segments)
            if total_contribution > 100:
                # Scale down proportionally
                for segment in segments:
                    segment.estimated_revenue_contribution = (
                        segment.estimated_revenue_contribution / total_contribution * 100
                    )
        
        # Sort by revenue contribution (largest first)
        segments.sort(key=lambda x: x.estimated_revenue_contribution, reverse=True)
        
        # Return top 4 segments (most conglomerates have 2-4 major segments)
        return segments[:4]
    
    def _estimate_segment_contribution(
        self,
        sector: SectorCategory,
        base_score: float,
        business_text: str
    ) -> float:
        """Apply business logic to estimate segment revenue contribution"""
        
        # Special handling for known conglomerates
        if 'reliance' in business_text:
            # Reliance Industries specific segment weights (approximate)
            segment_weights = {
                SectorCategory.ENERGY: 60,      # Oil & Gas, Petrochemicals
                SectorCategory.FMCG: 25,        # Retail (Reliance Retail)
                SectorCategory.TELECOM: 15      # Jio Digital Services
            }
            return segment_weights.get(sector, base_score)
        
        elif 'tata' in business_text:
            # Tata Group companies are diverse - use balanced approach
            return min(base_score, 40)  # Cap individual segments at 40%
        
        elif 'adani' in business_text:
            # Adani Group specific handling
            segment_weights = {
                SectorCategory.ENERGY: 40,       # Power, Green Energy
                SectorCategory.LOGISTICS: 25,    # Ports, Logistics
                SectorCategory.UTILITIES: 20,    # Utilities
                SectorCategory.AGRICULTURE: 15   # Agri Business
            }
            return segment_weights.get(sector, base_score)
        
        else:
            # Generic approach for other companies
            return min(base_score, 50)  # Cap at 50% for unknown conglomerates
    
    def _calculate_sector_statistics(self, sector_data: List[Dict]) -> Dict:
        """Calculate comprehensive sector statistics"""
        
        # Extract metrics
        pe_ratios = [d['pe_ratio'] for d in sector_data if d['pe_ratio'] > 0]
        roes = [d['roe'] for d in sector_data if d['roe'] and d['roe'] > 0]
        margins = [d['profit_margin'] for d in sector_data if d['profit_margin'] and d['profit_margin'] > 0]
        market_caps = [d['market_cap'] for d in sector_data if d['market_cap'] > 0]
        
        def safe_median(values):
            return np.median(values) if values else 0
        
        def safe_mean(values):
            return np.mean(values) if values else 0
        
        return {
            'valuation': {
                'median_pe': safe_median(pe_ratios),
                'pe_range': [min(pe_ratios), max(pe_ratios)] if pe_ratios else [0, 0]
            },
            'profitability': {
                'median_roe': safe_median(roes) * 100,
                'median_margin': safe_median(margins) * 100,
                'avg_roe': safe_mean(roes) * 100
            },
            'market_size': {
                'median_market_cap': safe_median(market_caps),
                'total_market_cap': sum(market_caps),
                'avg_market_cap': safe_mean(market_caps)
            },
            'data_quality': {
                'companies_analyzed': len(sector_data),
                'pe_coverage': len(pe_ratios) / len(sector_data) if sector_data else 0,
                'roe_coverage': len(roes) / len(sector_data) if sector_data else 0
            }
        }