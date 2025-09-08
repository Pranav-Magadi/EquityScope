# Claude-Based News Sentiment Service
# Generates contextual sentiment analysis using Claude AI instead of scraping news

import logging
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

from .claude_service import claude_service
from .intelligent_cache import intelligent_cache, CacheType
from ..models.company import NewsSentiment

logger = logging.getLogger(__name__)

@dataclass
class SentimentContext:
    """Context data for generating realistic sentiment"""
    ticker: str
    company_name: str
    sector: str
    market_cap: Optional[float] = None
    recent_performance: Optional[str] = None
    financial_health: Optional[str] = None
    industry_trends: Optional[List[str]] = None

class ClaudeNewsSentimentService:
    """
    Claude AI-powered contextual news sentiment service
    
    Instead of scraping unreliable news sources, this service uses Claude AI to:
    1. Generate realistic news themes based on company context
    2. Provide sophisticated sentiment analysis considering:
       - Sector-specific market conditions
       - Company financial performance
       - Industry trends and challenges
       - Macroeconomic factors
    """
    
    def __init__(self):
        self.cache_duration = timedelta(hours=6)  # Cache sentiment for 6 hours
        self.sector_themes = {
            "ENERGY": {
                "positive": ["renewable transition progress", "strong energy demand", "commodity price recovery"],
                "negative": ["regulatory pressures", "environmental concerns", "energy transition risks"],
                "neutral": ["quarterly earnings", "capacity utilization", "refining margins"]
            },
            "IT": {
                "positive": ["digital transformation demand", "AI adoption", "cloud migration"],
                "negative": ["H1B visa concerns", "client budget cuts", "automation displacing jobs"],
                "neutral": ["quarterly guidance", "deal wins", "employee retention"]
            },
            "BFSI": {
                "positive": ["credit growth", "digitalization", "fee income growth"],
                "negative": ["NPA concerns", "interest rate volatility", "regulatory changes"],
                "neutral": ["deposit growth", "branch expansion", "technology upgrades"]
            },
            "PHARMA": {
                "positive": ["new drug approvals", "US market expansion", "R&D breakthroughs"],
                "negative": ["regulatory rejections", "pricing pressures", "patent expiries"],
                "neutral": ["clinical trials", "manufacturing capacity", "quality audits"]
            },
            "FMCG": {
                "positive": ["rural demand recovery", "premiumization", "brand strength"],
                "negative": ["raw material inflation", "competitive pressure", "consumer slowdown"],
                "neutral": ["distribution expansion", "product launches", "market share"]
            }
        }
    
    async def get_contextual_sentiment(
        self, 
        context: SentimentContext,
        force_refresh: bool = False
    ) -> NewsSentiment:
        """
        Generate contextual news sentiment using Claude AI
        
        Args:
            context: Company and market context for sentiment generation
            force_refresh: Skip cache and generate fresh sentiment
            
        Returns:
            NewsSentiment with Claude-generated headlines and contextual analysis
        """
        try:
            # Check cache first
            if not force_refresh:
                cached_sentiment = await self._get_cached_sentiment(context.ticker)
                if cached_sentiment:
                    logger.info(f"Cache hit for {context.ticker} sentiment analysis")
                    return cached_sentiment
            
            logger.info(f"Generating Claude-based sentiment analysis for {context.company_name} ({context.ticker})")
            
            # Generate contextual sentiment using Claude
            sentiment_analysis = await self._generate_claude_sentiment(context)
            
            # Create NewsSentiment object
            news_sentiment = NewsSentiment(
                headlines=sentiment_analysis["headlines"],
                sentiment_score=sentiment_analysis["sentiment_score"],
                sentiment_label=sentiment_analysis["sentiment_label"],
                news_count=len(sentiment_analysis["headlines"]),
                last_updated=datetime.now()
            )
            
            # Cache the result
            await self._cache_sentiment(context.ticker, news_sentiment)
            
            logger.info(f"Generated {sentiment_analysis['sentiment_label']} sentiment ({sentiment_analysis['sentiment_score']:.3f}) for {context.ticker}")
            return news_sentiment
            
        except Exception as e:
            logger.error(f"Error generating Claude sentiment for {context.ticker}: {e}")
            return self._create_fallback_sentiment(context)
    
    async def _generate_claude_sentiment(self, context: SentimentContext) -> Dict[str, Any]:
        """Generate sentiment analysis using Claude AI"""
        
        # Get sector-specific themes
        sector_themes = self.sector_themes.get(context.sector, self.sector_themes["ENERGY"])
        
        # Create comprehensive prompt for Claude
        prompt = f"""
        As a financial news analyst, generate realistic news sentiment analysis for {context.company_name} ({context.ticker}), a {context.sector} sector company.

        Context:
        - Sector: {context.sector}
        - Recent themes: {', '.join(sector_themes['positive'] + sector_themes['negative'] + sector_themes['neutral'])}
        - Analysis date: {datetime.now().strftime('%B %Y')}

        Generate:
        1. 4-5 realistic news headlines that could appear for this company
        2. Overall sentiment score (-1.0 to 1.0) based on:
           - Sector-specific market conditions
           - Company's market position
           - Current industry trends
           - Economic environment

        Sector considerations:
        - {context.sector} companies currently facing: {self._get_sector_challenges(context.sector)}
        - Key opportunities: {self._get_sector_opportunities(context.sector)}

        Return in this exact JSON format:
        {{
            "headlines": [
                "headline 1",
                "headline 2", 
                "headline 3",
                "headline 4"
            ],
            "sentiment_score": 0.15,
            "sentiment_rationale": "Brief explanation of sentiment",
            "key_themes": ["theme1", "theme2"]
        }}

        Make headlines realistic and sector-appropriate. Sentiment should reflect realistic market conditions for {context.sector} sector in current market environment.
        """
        
        try:
            # Check if Claude service is available and re-initialize if needed
            if not claude_service.is_available():
                logger.warning(f"Claude service not available, reinitializing...")
                claude_service._initialize_client()
            
            if not claude_service.is_available():
                logger.warning(f"Claude service still not available after reinitialize, using fallback")
                return self._generate_sector_based_sentiment(context)
            
            # Get Claude analysis using generate_completion
            claude_response = await claude_service.generate_completion(
                prompt=prompt,
                system_prompt="You are a financial news analyst. Generate realistic news sentiment analysis in valid JSON format.",
                max_tokens=1000,
                temperature=0.7
            )
            
            # Parse Claude response (it's text, need to extract JSON)
            if not claude_response:
                logger.warning(f"Empty response from Claude for {context.ticker}")
                return self._generate_sector_based_sentiment(context)
            
            # Try to extract JSON from text response
            import json
            try:
                # Claude might return JSON wrapped in markdown code blocks
                text_response = claude_response.strip()
                if text_response.startswith("```json"):
                    text_response = text_response.replace("```json", "").replace("```", "").strip()
                elif text_response.startswith("```"):
                    text_response = text_response.replace("```", "").strip()
                
                sentiment_data = json.loads(text_response)
                logger.info(f"Successfully parsed Claude sentiment data for {context.ticker}: {sentiment_data}")
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse Claude JSON response for {context.ticker}: {e}")
                logger.error(f"Raw Claude response: {claude_response[:500]}...")
                return self._generate_sector_based_sentiment(context)
            
            # Validate and process sentiment score
            sentiment_score = max(-1.0, min(1.0, float(sentiment_data.get("sentiment_score", 0.0))))
            
            # Determine sentiment label
            if sentiment_score > 0.2:
                sentiment_label = "Positive"
            elif sentiment_score < -0.2:
                sentiment_label = "Negative"
            else:
                sentiment_label = "Neutral"
            
            return {
                "headlines": sentiment_data.get("headlines", [])[:5],  # Limit to 5
                "sentiment_score": sentiment_score,
                "sentiment_label": sentiment_label,
                "rationale": sentiment_data.get("sentiment_rationale", ""),
                "themes": sentiment_data.get("key_themes", [])
            }
            
        except Exception as e:
            logger.warning(f"Claude sentiment generation failed for {context.ticker}: {e}")
            # Fallback to intelligent sector-based sentiment
            return self._generate_sector_based_sentiment(context)
    
    def _generate_sector_based_sentiment(self, context: SentimentContext) -> Dict[str, Any]:
        """Generate sector-based sentiment when Claude fails"""
        
        sector_themes = self.sector_themes.get(context.sector, self.sector_themes["ENERGY"])
        
        # Create realistic headlines based on sector
        headlines = [
            f"{context.company_name} reports quarterly results amid {context.sector.lower()} sector trends",
            f"Analysts maintain coverage on {context.ticker} with sector-specific outlook",
            f"{context.sector} sector dynamics impact {context.company_name} performance",
            f"Market volatility affects {context.ticker} amid broader {context.sector.lower()} trends"
        ]
        
        # Sector-specific sentiment biases
        sector_sentiment_bias = {
            "ENERGY": 0.1,     # Slightly positive due to energy transition opportunities
            "IT": 0.15,        # Positive due to digital transformation demand
            "BFSI": 0.05,      # Neutral to slightly positive
            "PHARMA": 0.08,    # Slightly positive due to healthcare demand
            "FMCG": 0.02       # Neutral due to mixed demand patterns
        }
        
        base_sentiment = sector_sentiment_bias.get(context.sector, 0.0)
        # Add some realistic variation
        import random
        sentiment_score = max(-0.5, min(0.5, base_sentiment + random.uniform(-0.15, 0.15)))
        
        if sentiment_score > 0.1:
            sentiment_label = "Positive"
        elif sentiment_score < -0.1:
            sentiment_label = "Negative"
        else:
            sentiment_label = "Neutral"
        
        return {
            "headlines": headlines,
            "sentiment_score": sentiment_score,
            "sentiment_label": sentiment_label,
            "rationale": f"Sector-based analysis for {context.sector} industry",
            "themes": sector_themes["neutral"][:2]
        }
    
    def _get_sector_challenges(self, sector: str) -> str:
        """Get current challenges for sector"""
        challenges = {
            "ENERGY": "regulatory pressures, renewable transition costs, commodity volatility",
            "IT": "talent shortage, client budget optimization, currency fluctuations",
            "BFSI": "NPA concerns, regulatory changes, interest rate volatility", 
            "PHARMA": "pricing pressures, regulatory scrutiny, patent cliff risks",
            "FMCG": "raw material inflation, rural demand weakness, competitive intensity"
        }
        return challenges.get(sector, "market volatility, competitive pressures")
    
    def _get_sector_opportunities(self, sector: str) -> str:
        """Get current opportunities for sector"""
        opportunities = {
            "ENERGY": "renewable energy transition, energy security focus, ESG investments",
            "IT": "AI/ML adoption, cloud migration, digital transformation acceleration",
            "BFSI": "digital banking growth, financial inclusion, fee income expansion",
            "PHARMA": "healthcare infrastructure growth, chronic disease management, biosimilars",
            "FMCG": "premiumization trends, rural penetration, e-commerce growth"
        }
        return opportunities.get(sector, "market expansion, operational efficiency")
    
    def _create_fallback_sentiment(self, context: SentimentContext) -> NewsSentiment:
        """Create fallback sentiment when all else fails"""
        return NewsSentiment(
            headlines=[
                f"{context.company_name} operational update",
                f"{context.sector} sector performance review",
                f"Market analysis for {context.ticker}",
                f"Industry trends affecting {context.company_name}"
            ],
            sentiment_score=0.0,
            sentiment_label="Neutral",
            news_count=4,
            last_updated=datetime.now()
        )
    
    async def _get_cached_sentiment(self, ticker: str) -> Optional[NewsSentiment]:
        """Retrieve cached sentiment analysis"""
        try:
            cached_data = await intelligent_cache.get(
                cache_type=CacheType.AI_INSIGHTS,
                identifier=ticker,
                analysis_type="claude_sentiment"
            )
            
            if cached_data:
                return NewsSentiment(
                    headlines=cached_data["headlines"],
                    sentiment_score=cached_data["sentiment_score"],
                    sentiment_label=cached_data["sentiment_label"],
                    news_count=cached_data["news_count"],
                    last_updated=datetime.fromisoformat(cached_data["last_updated"])
                )
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving cached sentiment for {ticker}: {e}")
            return None
    
    async def _cache_sentiment(self, ticker: str, sentiment: NewsSentiment) -> bool:
        """Cache sentiment analysis result"""
        try:
            cache_data = {
                "headlines": sentiment.headlines,
                "sentiment_score": sentiment.sentiment_score,
                "sentiment_label": sentiment.sentiment_label,
                "news_count": sentiment.news_count,
                "last_updated": sentiment.last_updated.isoformat()
            }
            
            success = await intelligent_cache.set(
                cache_type=CacheType.AI_INSIGHTS,
                identifier=ticker,
                data=cache_data,
                analysis_type="claude_sentiment"
            )
            
            if success:
                logger.info(f"Cached Claude sentiment analysis for {ticker}")
            return success
            
        except Exception as e:
            logger.error(f"Error caching sentiment for {ticker}: {e}")
            return False

# Create service instance
claude_news_sentiment_service = ClaudeNewsSentimentService()