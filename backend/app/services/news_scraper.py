import asyncio
import aiohttp
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import re
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import time
from dataclasses import dataclass
from collections import defaultdict

logger = logging.getLogger(__name__)

@dataclass
class RateLimitConfig:
    requests_per_minute: int = 30
    requests_per_hour: int = 500
    delay_between_requests: float = 2.0
    max_retries: int = 3

class NewsScrapingService:
    """Service for scraping financial news with rate limiting and ethical practices."""
    
    def __init__(self):
        self.rate_limit = RateLimitConfig()
        self.request_timestamps = defaultdict(list)
        self.session = None
        
        # Top financial news sources with their domains
        self.news_sources = {
            # Global Financial News
            'reuters_finance': 'https://www.reuters.com/finance/',
            'bloomberg': 'https://www.bloomberg.com/search?query=',
            'financial_times': 'https://www.ft.com/search?q=',
            'cnbc': 'https://www.cnbc.com/search/?query=',
            'marketwatch': 'https://www.marketwatch.com/tools/quotes/lookup.asp?siteID=mktw&Lookup=',
            
            # Indian Financial Sources
            'economic_times': 'https://economictimes.indiatimes.com/topic/',
            'business_standard': 'https://www.business-standard.com/search?q=',
            'moneycontrol': 'https://www.moneycontrol.com/news/tags/',
            'livemint': 'https://www.livemint.com/Search/',
            'business_today': 'https://www.businesstoday.in/search?q=',
            
            # Alternative sources
            'yahoo_finance': 'https://finance.yahoo.com/quote/',
            'investing_com': 'https://www.investing.com/search/?q=',
        }
        
        # Top 20 Global Companies reference for context
        self.top_global_companies = [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'BRK-A', 'JPM', 'JNJ',
            'V', 'PG', 'UNH', 'HD', 'MA', 'PYPL', 'DIS', 'ADBE', 'NFLX', 'CRM'
        ]
        
        # Top 20 Indian Companies reference
        self.top_indian_companies = [
            'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'ICICIBANK.NS', 'HINDUNILVR.NS',
            'INFY.NS', 'ITC.NS', 'SBIN.NS', 'BHARTIARTL.NS', 'KOTAKBANK.NS',
            'LT.NS', 'ASIANPAINT.NS', 'AXISBANK.NS', 'MARUTI.NS', 'SUNPHARMA.NS',
            'TITAN.NS', 'ULTRACEMCO.NS', 'NESTLEIND.NS', 'WIPRO.NS', 'HCLTECH.NS'
        ]
    
    async def __aenter__(self):
        """Async context manager entry."""
        import ssl
        import aiohttp
        
        # Create SSL context that doesn't verify certificates (for development)
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=aiohttp.ClientTimeout(total=30),
            headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    def _check_rate_limit(self, source: str) -> bool:
        """Check if we can make a request without violating rate limits."""
        now = time.time()
        timestamps = self.request_timestamps[source]
        
        # Remove timestamps older than 1 hour
        timestamps[:] = [t for t in timestamps if now - t < 3600]
        
        # Check hourly limit
        if len(timestamps) >= self.rate_limit.requests_per_hour:
            return False
        
        # Check per-minute limit
        recent_timestamps = [t for t in timestamps if now - t < 60]
        if len(recent_timestamps) >= self.rate_limit.requests_per_minute:
            return False
        
        return True
    
    def _record_request(self, source: str):
        """Record a request timestamp for rate limiting."""
        self.request_timestamps[source].append(time.time())
    
    async def _make_request(self, url: str, source: str) -> Optional[str]:
        """Make a rate-limited HTTP request."""
        if not self._check_rate_limit(source):
            logger.warning(f"Rate limit exceeded for {source}, skipping request")
            return None
        
        try:
            # Add delay between requests
            await asyncio.sleep(self.rate_limit.delay_between_requests)
            
            async with self.session.get(url) as response:
                self._record_request(source)
                
                if response.status == 200:
                    return await response.text()
                elif response.status == 429:  # Too Many Requests
                    logger.warning(f"Rate limited by {source}, waiting...")
                    await asyncio.sleep(60)  # Wait 1 minute
                    return None
                else:
                    logger.warning(f"HTTP {response.status} from {source}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error requesting {url}: {e}")
            return None
    
    def _extract_article_content(self, html: str, url: str) -> Optional[Dict[str, Any]]:
        """Extract article content from HTML."""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Remove unwanted elements
            for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'advertisement']):
                element.decompose()
            
            # Try to find title
            title = None
            for selector in ['h1', 'title', '.headline', '.article-title', '.story-title']:
                title_elem = soup.select_one(selector)
                if title_elem:
                    title = title_elem.get_text().strip()
                    break
            
            # Try to find article content
            content = ""
            for selector in ['.article-content', '.story-content', '.post-content', 'article', '.content']:
                content_elem = soup.select_one(selector)
                if content_elem:
                    content = content_elem.get_text().strip()
                    break
            
            if not content:
                # Fallback: get all paragraph text
                paragraphs = soup.find_all('p')
                content = ' '.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
            
            # Clean up content
            content = re.sub(r'\s+', ' ', content)
            content = content[:2000]  # Limit content length
            
            if len(content) < 100:  # Skip if too short
                return None
            
            return {
                'url': url,
                'title': title or 'No title found',
                'content': content,
                'scraped_at': datetime.now().isoformat(),
                'source_domain': urlparse(url).netloc
            }
            
        except Exception as e:
            logger.error(f"Error extracting content from {url}: {e}")
            return None
    
    async def search_company_news(
        self,
        company_name: str,
        ticker: str,
        max_articles: int = 10,
        days_back: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Search for recent news articles about a company.
        
        Args:
            company_name: Full company name
            ticker: Stock ticker symbol
            max_articles: Maximum number of articles to return
            days_back: How many days back to search
            
        Returns:
            List of article dictionaries with url, title, content, and metadata
        """
        articles = []
        search_terms = [company_name, ticker.replace('.NS', ''), ticker]
        
        # Add company context for better search
        is_indian_company = ticker.endswith('.NS')
        if is_indian_company:
            search_terms.append(f"{company_name} India")
        
        logger.info(f"Starting news search for {company_name} ({ticker})")
        
        try:
            # Search Yahoo Finance first (most reliable)
            yahoo_articles = await self._search_yahoo_finance(ticker)
            articles.extend(yahoo_articles[:max_articles//2])
            
            # Search Economic Times for Indian companies
            if is_indian_company:
                et_articles = await self._search_economic_times(company_name)
                articles.extend(et_articles[:max_articles//4])
            
            # Search Google News (if we need more articles)
            if len(articles) < max_articles:
                google_articles = await self._search_google_news(search_terms[0])
                articles.extend(google_articles[:max_articles - len(articles)])
            
            # Remove duplicates and sort by relevance
            unique_articles = self._deduplicate_articles(articles)
            
            logger.info(f"Found {len(unique_articles)} unique articles for {ticker}")
            return unique_articles[:max_articles]
            
        except Exception as e:
            logger.error(f"Error searching news for {ticker}: {e}")
            return []
    
    async def _search_yahoo_finance(self, ticker: str) -> List[Dict[str, Any]]:
        """Search Yahoo Finance for company news."""
        articles = []
        
        try:
            # Yahoo Finance news URL
            base_ticker = ticker.replace('.NS', '')
            url = f"https://finance.yahoo.com/quote/{base_ticker}/news"
            
            html = await self._make_request(url, 'yahoo_finance')
            if not html:
                return articles
            
            soup = BeautifulSoup(html, 'html.parser')
            
            # Find news links
            news_links = soup.find_all('a', href=True)
            for link in news_links[:5]:  # Limit to first 5 links
                href = link.get('href')
                if href and '/news/' in href:
                    full_url = urljoin('https://finance.yahoo.com', href)
                    title = link.get_text().strip()
                    
                    if title and len(title) > 20:
                        # Try to fetch and extract actual content
                        article_html = await self._make_request(full_url, 'yahoo_finance_article')
                        content = f"Yahoo Finance article: {title}"
                        
                        if article_html:
                            extracted = self._extract_article_content(article_html, full_url)
                            if extracted:
                                content = extracted['content']
                        
                        articles.append({
                            'url': full_url,
                            'title': title,
                            'content': content,
                            'scraped_at': datetime.now().isoformat(),
                            'source_domain': 'finance.yahoo.com',
                            'article_type': 'financial_news'
                        })
            
        except Exception as e:
            logger.error(f"Error searching Yahoo Finance: {e}")
        
        return articles
    
    async def _search_economic_times(self, company_name: str) -> List[Dict[str, Any]]:
        """Search Economic Times for Indian company news."""
        articles = []
        
        try:
            # Economic Times search URL
            search_term = company_name.replace(' ', '-').lower()
            url = f"https://economictimes.indiatimes.com/topic/{search_term}"
            
            html = await self._make_request(url, 'economic_times')
            if not html:
                return articles
            
            soup = BeautifulSoup(html, 'html.parser')
            
            # Find article links
            article_links = soup.find_all('a', href=True)
            for link in article_links[:3]:
                href = link.get('href')
                if href and '/articleshow/' in href:
                    full_url = urljoin('https://economictimes.indiatimes.com', href)
                    title = link.get_text().strip()
                    
                    if title and len(title) > 20:
                        # Try to fetch and extract actual content
                        article_html = await self._make_request(full_url, 'economic_times_article')
                        content = f"Economic Times article: {title}"
                        
                        if article_html:
                            extracted = self._extract_article_content(article_html, full_url)
                            if extracted:
                                content = extracted['content']
                        
                        articles.append({
                            'url': full_url,
                            'title': title,
                            'content': content,
                            'scraped_at': datetime.now().isoformat(),
                            'source_domain': 'economictimes.indiatimes.com',
                            'article_type': 'financial_news'
                        })
            
        except Exception as e:
            logger.error(f"Error searching Economic Times: {e}")
        
        return articles
    
    async def _search_google_news(self, search_term: str) -> List[Dict[str, Any]]:
        """Search Google News for general company news."""
        articles = []
        
        try:
            # Google News search URL (simplified)
            url = f"https://news.google.com/search?q={search_term.replace(' ', '%20')}&hl=en-US&gl=US&ceid=US:en"
            
            html = await self._make_request(url, 'google_news')
            if not html:
                return articles
            
            soup = BeautifulSoup(html, 'html.parser')
            
            # Find news articles (Google News has dynamic structure)
            article_elements = soup.find_all('article')[:3]
            for article in article_elements:
                title_elem = article.find('h3') or article.find('h4')
                link_elem = article.find('a', href=True)
                
                if title_elem and link_elem:
                    title = title_elem.get_text().strip()
                    href = link_elem.get('href')
                    
                    if title and href:
                        articles.append({
                            'url': f"https://news.google.com{href}",
                            'title': title,
                            'content': f"Google News article: {title}",
                            'scraped_at': datetime.now().isoformat(),
                            'source_domain': 'news.google.com'
                        })
            
        except Exception as e:
            logger.error(f"Error searching Google News: {e}")
        
        return articles
    
    def _deduplicate_articles(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate articles based on title similarity."""
        unique_articles = []
        seen_titles = set()
        
        for article in articles:
            title = article.get('title', '').lower()
            # Simple deduplication based on first 50 characters of title
            title_key = title[:50]
            
            if title_key not in seen_titles:
                seen_titles.add(title_key)
                unique_articles.append(article)
        
        return unique_articles
    
    def get_progress_callback(self):
        """Get a callback function for progress tracking."""
        total_requests = 0
        completed_requests = 0
        
        def progress_callback(increment: int = 1):
            nonlocal completed_requests
            completed_requests += increment
            
            if total_requests > 0:
                progress = (completed_requests / total_requests) * 100
                
                if progress >= 50 and progress < 60:
                    logger.info("🔄 News scraping: 50% complete (halfway point)")
                elif progress >= 80 and progress < 90:
                    logger.info("🔄 News scraping: 80% complete (near completion)")
        
        def set_total(total: int):
            nonlocal total_requests
            total_requests = total
        
        progress_callback.set_total = set_total
        return progress_callback

class NewsScraperService:
    """Service for fetching and analyzing recent news articles."""
    
    def __init__(self):
        self.scraper = NewsScrapingService()
        
    async def get_recent_news(
        self, 
        ticker: str, 
        limit: int = 10, 
        days: int = 7,
        force_refresh: bool = False
    ) -> List[Dict[str, Any]]:
        """Get recent news articles for a ticker with sentiment analysis."""
        try:
            # Extract company name from ticker
            company_name = self._get_company_name(ticker)
            
            logger.info(f"📰 Fetching {limit} recent articles for {ticker} ({company_name})")
            
            # Use the existing scraper to search for news
            async with self.scraper:
                raw_articles = await self.scraper.search_company_news(
                    company_name=company_name,
                    ticker=ticker,
                    max_articles=limit,
                    days_back=days
                )
            
            # Transform to our API format with sentiment analysis
            processed_articles = []
            for i, article in enumerate(raw_articles[:limit]):
                processed_article = {
                    "id": f"{ticker}-article-{i+1}",
                    "title": article.get('title', 'No title'),
                    "summary": self._extract_summary(article.get('content', '')),
                    "url": article.get('url', '#'),
                    "published_date": article.get('scraped_at', datetime.utcnow().isoformat()),
                    "source": {
                        "name": self._get_source_name(article.get('source_domain', 'Unknown')),
                        "domain": article.get('source_domain', 'unknown.com')
                    },
                    "sentiment": self._analyze_basic_sentiment(article.get('title', '') + ' ' + article.get('content', '')),
                    "sentiment_score": self._calculate_sentiment_score(article.get('title', '') + ' ' + article.get('content', '')),
                    "relevance_score": 0.8,  # Could be enhanced with ML
                    "tags": self._extract_tags(article.get('content', '')),
                    "language": "en"
                }
                processed_articles.append(processed_article)
            
            logger.info(f"✅ Successfully processed {len(processed_articles)} articles for {ticker}")
            return processed_articles
            
        except Exception as e:
            logger.error(f"❌ Error fetching news for {ticker}: {str(e)}")
            # Return empty list instead of failing
            return []
    
    def _get_company_name(self, ticker: str) -> str:
        """Extract company name from ticker."""
        # Simple mapping for common Indian stocks
        ticker_to_name = {
            'RELIANCE.NS': 'Reliance Industries',
            'TCS.NS': 'Tata Consultancy Services', 
            'HDFCBANK.NS': 'HDFC Bank',
            'INFY.NS': 'Infosys',
            'ICICIBANK.NS': 'ICICI Bank',
            'HINDUNILVR.NS': 'Hindustan Unilever',
            'ITC.NS': 'ITC Limited',
            'SBIN.NS': 'State Bank of India',
            'BHARTIARTL.NS': 'Bharti Airtel',
            'KOTAKBANK.NS': 'Kotak Mahindra Bank'
        }
        
        return ticker_to_name.get(ticker, ticker.replace('.NS', '').replace('_', ' '))
    
    def _extract_summary(self, content: str) -> str:
        """Extract a summary from article content."""
        if not content:
            return "Article summary not available."
        
        # Take first 200 characters as summary
        sentences = content.split('. ')
        summary = sentences[0] if sentences else content[:200]
        
        if len(summary) > 200:
            summary = summary[:200] + "..."
        
        return summary
    
    def _get_source_name(self, domain: str) -> str:
        """Get friendly source name from domain."""
        domain_to_name = {
            'finance.yahoo.com': 'Yahoo Finance',
            'economictimes.indiatimes.com': 'Economic Times',
            'moneycontrol.com': 'MoneyControl',
            'business-standard.com': 'Business Standard',
            'livemint.com': 'LiveMint',
            'reuters.com': 'Reuters',
            'bloomberg.com': 'Bloomberg',
            'cnbc.com': 'CNBC',
            'news.google.com': 'Google News'
        }
        
        return domain_to_name.get(domain, domain.replace('www.', '').title())
    
    def _analyze_basic_sentiment(self, text: str) -> str:
        """Basic sentiment analysis using keywords."""
        if not text:
            return 'neutral'
        
        text_lower = text.lower()
        
        positive_keywords = [
            'growth', 'profit', 'gain', 'rise', 'increase', 'strong', 'positive', 
            'success', 'beat', 'exceed', 'upgrade', 'bullish', 'expansion', 
            'partnership', 'acquisition', 'revenue', 'earnings beat'
        ]
        
        negative_keywords = [
            'loss', 'decline', 'fall', 'drop', 'weak', 'negative', 'concern', 
            'worry', 'risk', 'bearish', 'downgrade', 'miss', 'below', 'challenge',
            'regulatory', 'investigation', 'lawsuit', 'penalty'
        ]
        
        positive_count = sum(1 for word in positive_keywords if word in text_lower)
        negative_count = sum(1 for word in negative_keywords if word in text_lower)
        
        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        else:
            return 'neutral'
    
    def _calculate_sentiment_score(self, text: str) -> float:
        """Calculate sentiment score between -1.0 and 1.0."""
        if not text:
            return 0.0
        
        sentiment = self._analyze_basic_sentiment(text)
        
        if sentiment == 'positive':
            return 0.3 + (len([w for w in ['strong', 'excellent', 'outstanding'] if w in text.lower()]) * 0.2)
        elif sentiment == 'negative':
            return -0.3 - (len([w for w in ['severe', 'major', 'significant'] if w in text.lower()]) * 0.2)
        else:
            return 0.0
    
    def _extract_tags(self, content: str) -> List[str]:
        """Extract relevant tags from content."""
        if not content:
            return ['general']
        
        content_lower = content.lower()
        possible_tags = [
            'earnings', 'growth', 'merger', 'acquisition', 'partnership', 
            'regulatory', 'expansion', 'digital', 'technology', 'finance',
            'market', 'sector', 'quarterly', 'annual', 'investment'
        ]
        
        found_tags = [tag for tag in possible_tags if tag in content_lower]
        return found_tags[:3] if found_tags else ['market', 'analysis']

# Global service instance
news_scraper = NewsScrapingService()
news_scraper_service = NewsScraperService()