from typing import List, Dict, Any
from datetime import datetime, timedelta
import random
import logging
import asyncio
from ..models.company import SWOTAnalysis, NewsSentiment, MarketLandscape, EmployeeSentiment
from .claude_news_sentiment_service import claude_news_sentiment_service, SentimentContext

logger = logging.getLogger(__name__)

class AnalysisService:
    """
    Service for qualitative analysis. Uses placeholder functions for external API calls.
    In production, integrate with news APIs, sentiment analysis services, and Glassdoor API.
    """
    
    @staticmethod
    def get_swot_analysis(ticker: str, company_name: str) -> SWOTAnalysis:
        """
        Generate SWOT analysis using AI/LLM.
        Placeholder implementation - integrate with OpenAI/Claude API in production.
        """
        try:
            # Placeholder: Return realistic-looking SWOT based on company type
            swot_templates = {
                'tech': {
                    'strengths': [
                        {
                            "point": "Strong digital infrastructure and technology capabilities",
                            "sources": [
                                "https://economictimes.indiatimes.com/tech/technology/indian-it-sector-digital-transformation",
                                "https://www.moneycontrol.com/news/business/companies/tech-infrastructure-growth-india"
                            ]
                        },
                        {
                            "point": "Skilled workforce and engineering talent",
                            "sources": [
                                "https://www.business-standard.com/topic/skilled-workforce",
                                "https://www.livemint.com/industry/human-resource/engineering-talent-pool-india"
                            ]
                        },
                        {
                            "point": "Established market presence in digital services",
                            "sources": [
                                "https://www.reuters.com/technology/digital-services-market-growth",
                                "https://economictimes.indiatimes.com/tech/software/digital-services-expansion"
                            ]
                        }
                    ],
                    'weaknesses': [
                        "High dependency on technology investments",
                        "Intense competition in the tech sector",
                        "Rapid technological obsolescence risk"
                    ],
                    'opportunities': [
                        "Growing digital transformation demand",
                        "Expansion into emerging markets",
                        "AI and automation integration potential"
                    ],
                    'threats': [
                        "Cybersecurity risks and data breaches",
                        "Regulatory changes in data privacy",
                        "Economic downturns affecting IT spending"
                    ]
                },
                'financial': {
                    'strengths': [
                        "Strong capital base and liquidity position",
                        "Diversified financial product portfolio",
                        "Established customer relationships"
                    ],
                    'weaknesses': [
                        "Regulatory compliance burden",
                        "Interest rate sensitivity",
                        "Legacy system modernization needs"
                    ],
                    'opportunities': [
                        "Digital banking and fintech expansion",
                        "Growing middle-class financial needs",
                        "Cross-selling opportunities"
                    ],
                    'threats': [
                        "Economic volatility and credit risks",
                        "Increasing competition from fintech",
                        "Regulatory policy changes"
                    ]
                },
                'default': {
                    'strengths': [
                        "Established brand recognition and market position",
                        "Experienced management team",
                        "Diversified revenue streams"
                    ],
                    'weaknesses': [
                        "Market concentration risks",
                        "Operational efficiency challenges",
                        "Capital intensive business model"
                    ],
                    'opportunities': [
                        "Market expansion and growth potential",
                        "Digital transformation initiatives",
                        "Strategic partnerships and alliances"
                    ],
                    'threats': [
                        "Increased competition and market saturation",
                        "Economic downturns and market volatility",
                        "Regulatory and policy changes"
                    ]
                }
            }
            
            # Simple heuristic to determine company type
            company_lower = company_name.lower()
            if any(word in company_lower for word in ['tech', 'info', 'software', 'digital']):
                template = swot_templates['tech']
            elif any(word in company_lower for word in ['bank', 'financial', 'insurance', 'credit']):
                template = swot_templates['financial']
            else:
                template = swot_templates['default']
            
            return SWOTAnalysis(**template)
            
        except Exception as e:
            logger.error(f"Error generating SWOT analysis for {ticker}: {e}")
            return SWOTAnalysis(
                strengths=["Analysis unavailable"],
                weaknesses=["Analysis unavailable"],
                opportunities=["Analysis unavailable"],
                threats=["Analysis unavailable"]
            )

    @staticmethod
    async def get_news_sentiment(
        ticker: str, 
        company_name: str = None, 
        sector: str = None,
        force_refresh: bool = False
    ) -> NewsSentiment:
        """
        Generate contextual news sentiment using Claude AI.
        Provides realistic sentiment analysis based on company sector and market conditions.
        """
        try:
            # Create sentiment context
            context = SentimentContext(
                ticker=ticker,
                company_name=company_name or ticker,
                sector=sector or "GENERAL"
            )
            
            # Get Claude-based contextual sentiment
            return await claude_news_sentiment_service.get_contextual_sentiment(
                context=context,
                force_refresh=force_refresh
            )
            
        except Exception as e:
            logger.error(f"Error generating Claude sentiment for {ticker}: {e}")
            # Fallback to neutral sentiment
            return NewsSentiment(
                headlines=[
                    f"{company_name or ticker} market analysis",
                    f"Industry trends affecting {ticker}",
                    f"Sector performance review for {company_name or ticker}"
                ],
                sentiment_score=0.0,
                sentiment_label="Neutral",
                news_count=3,
                last_updated=datetime.now()
            )
    
    @staticmethod
    def get_news_sentiment_sync(ticker: str) -> NewsSentiment:
        """
        Synchronous wrapper for backwards compatibility.
        This method is deprecated - use get_news_sentiment() instead.
        """
        try:
            # Run async method in sync context
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If we're already in an async context, create a new loop
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(
                        asyncio.run, 
                        AnalysisService.get_news_sentiment(ticker)
                    )
                    return future.result()
            else:
                return loop.run_until_complete(
                    AnalysisService.get_news_sentiment(ticker)
                )
        except Exception as e:
            logger.error(f"Error in sync sentiment wrapper for {ticker}: {e}")
            return NewsSentiment(
                headlines=[f"Sentiment analysis unavailable for {ticker}"],
                sentiment_score=0.0,
                sentiment_label="Neutral", 
                news_count=0,
                last_updated=datetime.now()
            )

    @staticmethod
    def get_market_landscape(ticker: str, company_name: str, sector: str) -> MarketLandscape:
        """
        Analyze market landscape and competitive positioning.
        Placeholder implementation - integrate with market research APIs.
        """
        try:
            # Sample competitors based on sector
            competitor_templates = {
                'Technology': ['Infosys', 'Wipro', 'HCL Technologies', 'Tech Mahindra'],
                'Financial Services': ['HDFC Bank', 'ICICI Bank', 'Axis Bank', 'SBI'],
                'Healthcare': ['Sun Pharma', 'Dr. Reddy\'s', 'Cipla', 'Lupin'],
                'Energy': ['Reliance Industries', 'ONGC', 'IOC', 'BPCL']
            }
            
            competitors = competitor_templates.get(sector, ['Competitor A', 'Competitor B', 'Competitor C'])
            
            # Create competitor data
            competitor_data = []
            for comp in competitors[:3]:  # Top 3 competitors
                competitor_data.append({
                    'name': comp,
                    'market_cap': random.uniform(10000, 100000),  # In crores
                    'market_share': random.uniform(5, 25),
                    'growth_rate': random.uniform(-5, 15)
                })
            
            # Sample industry trends
            trend_templates = [
                "Digital transformation accelerating across the industry",
                "Increasing focus on ESG and sustainability initiatives",
                "Growing demand for data analytics and AI solutions",
                "Regulatory changes driving compliance investments",
                "Market consolidation through mergers and acquisitions"
            ]
            
            return MarketLandscape(
                competitors=competitor_data,
                market_share=random.uniform(8, 20),
                industry_trends=random.sample(trend_templates, 3),
                market_position="Established player with competitive advantages"
            )
            
        except Exception as e:
            logger.error(f"Error analyzing market landscape for {ticker}: {e}")
            return MarketLandscape(
                competitors=[],
                market_share=None,
                industry_trends=["Market analysis unavailable"],
                market_position="Analysis unavailable"
            )

    @staticmethod
    def get_employee_sentiment(company_name: str) -> EmployeeSentiment:
        """
        Analyze employee sentiment from Glassdoor-like data.
        Placeholder implementation - integrate with Glassdoor API or web scraping.
        """
        try:
            # Simulate employee sentiment data
            rating = random.uniform(3.2, 4.5)
            review_count = random.randint(50, 500)
            
            # Sample pros and cons
            pros_templates = [
                "Good work-life balance and flexible working hours",
                "Competitive compensation and benefits package",
                "Strong learning and development opportunities",
                "Collaborative and supportive team environment",
                "Clear career progression paths"
            ]
            
            cons_templates = [
                "Limited remote work options in some roles",
                "Slow decision-making processes",
                "High workload during peak periods",
                "Limited innovation in some departments",
                "Bureaucratic organizational structure"
            ]
            
            pros = random.sample(pros_templates, 3)
            cons = random.sample(cons_templates, 2)
            
            # Generate sentiment summary
            if rating >= 4.0:
                sentiment_summary = "Generally positive employee sentiment with high satisfaction"
            elif rating >= 3.5:
                sentiment_summary = "Mixed but overall positive employee feedback"
            else:
                sentiment_summary = "Employee sentiment shows areas for improvement"
            
            return EmployeeSentiment(
                rating=rating,
                review_count=review_count,
                pros=pros,
                cons=cons,
                sentiment_summary=sentiment_summary
            )
            
        except Exception as e:
            logger.error(f"Error analyzing employee sentiment for {company_name}: {e}")
            return EmployeeSentiment(
                rating=3.5,
                review_count=0,
                pros=["Employee data unavailable"],
                cons=["Employee data unavailable"],
                sentiment_summary="Employee sentiment analysis unavailable"
            )

    @staticmethod
    def generate_mock_news_sentiment(ticker: str):
        """
        Generate mock enhanced news sentiment data for fallback scenarios.
        Used when news scraping fails or returns no data.
        """
        try:
            # Generate mock articles with realistic content
            company_name = ticker.replace('.NS', '').replace('_', ' ')
            base_date = datetime.now()
            
            # Create company-specific realistic articles with real URLs
            if 'RELIANCE' in ticker.upper():
                mock_articles_data = [
                    {
                        "title": f"Reliance Industries Q3 results beat estimates; retail expansion accelerates",
                        "summary": f"Reliance reported strong quarterly earnings with retail revenue up 19% YoY. New store rollouts in tier-2 cities and JioMart growth driving expansion.",
                        "source": "Economic Times",
                        "days_ago": 3,
                        "sentiment": "positive",
                        "score": random.uniform(0.4, 0.7),
                        "url": "https://economictimes.indiatimes.com/markets/stocks/news"
                    },
                    {
                        "title": f"Reliance's green energy pivot gains momentum with solar manufacturing",
                        "summary": f"The conglomerate announced plans to invest ₹75,000 crores in renewable energy manufacturing, targeting 100 GW capacity by 2030.",
                        "source": "Business Standard",
                        "days_ago": 6,
                        "sentiment": "positive", 
                        "score": random.uniform(0.3, 0.6),
                        "url": "https://www.business-standard.com/industry/energy"
                    },
                    {
                        "title": f"Jio 5G rollout accelerates, crosses 100 cities milestone",
                        "summary": f"Reliance Jio expanded its 5G network to over 100 cities, strengthening its position in India's telecom market with advanced infrastructure.",
                        "source": "Mint",
                        "days_ago": 8,
                        "sentiment": "positive",
                        "score": random.uniform(0.2, 0.5),
                        "url": "https://www.livemint.com/technology"
                    },
                    {
                        "title": f"Global oil price volatility affects Reliance's petrochemical margins",
                        "summary": f"Rising crude costs and supply chain disruptions impacted the company's refining and petrochemical segment profitability in recent quarters.",
                        "source": "CNBC-TV18",
                        "days_ago": 2,
                        "sentiment": "negative",
                        "score": random.uniform(-0.3, -0.1),
                        "url": "https://www.cnbctv18.com/market/"
                    },
                    {
                        "title": f"Regulatory scrutiny over data localization norms for Jio platforms",
                        "summary": f"Government committees reviewing compliance requirements for digital platforms may impact Jio's data storage and processing operations.",
                        "source": "Financial Express",
                        "days_ago": 12,
                        "sentiment": "neutral",
                        "score": random.uniform(-0.1, 0.1),
                        "url": "https://www.financialexpress.com/industry/"
                    }
                ]
            elif 'TCS' in ticker.upper() or 'TATA' in ticker.upper():
                mock_articles_data = [
                    {
                        "title": f"TCS reports strong Q3 results with 12.2% YoY growth in net profit",
                        "summary": f"India's largest IT services company posted robust quarterly earnings driven by digital transformation deals and strong client addition in North America.",
                        "source": "Economic Times",
                        "days_ago": 2,
                        "sentiment": "positive",
                        "score": random.uniform(0.4, 0.6),
                        "url": "https://economictimes.indiatimes.com/tech/information-tech"
                    },
                    {
                        "title": f"TCS wins major cloud transformation deal worth $2.25 billion",
                        "summary": f"The multinational secured a multi-year contract with a Fortune 500 client for comprehensive cloud migration and digital transformation services.",
                        "source": "Business Standard",
                        "days_ago": 5,
                        "sentiment": "positive",
                        "score": random.uniform(0.3, 0.5),
                        "url": "https://www.business-standard.com/industry/news"
                    },
                    {
                        "title": f"IT hiring slowdown concerns weigh on TCS workforce expansion plans",
                        "summary": f"Industry-wide cautious hiring approach and client budget constraints are impacting the company's aggressive recruitment targets for FY24.",
                        "source": "Mint",
                        "days_ago": 8,
                        "sentiment": "negative",
                        "score": random.uniform(-0.3, -0.1),
                        "url": "https://www.livemint.com/industry/human-resource"
                    },
                    {
                        "title": f"TCS continues leadership in AI and automation services segment",
                        "summary": f"The company strengthened its position in artificial intelligence and robotic process automation, securing multiple enterprise deals in the segment.",
                        "source": "CNBC-TV18",
                        "days_ago": 6,
                        "sentiment": "positive",
                        "score": random.uniform(0.2, 0.4),
                        "url": "https://www.cnbctv18.com/technology/"
                    },
                    {
                        "title": f"Currency headwinds may impact TCS margin guidance for upcoming quarters",
                        "summary": f"Strengthening rupee and cross-currency fluctuations pose challenges to maintaining healthy operating margins amid competitive pricing pressures.",
                        "source": "Financial Express",
                        "days_ago": 9,
                        "sentiment": "neutral",
                        "score": random.uniform(-0.1, 0.1),
                        "url": "https://www.financialexpress.com/industry/technology/"
                    }
                ]
            elif 'INFY' in ticker.upper():
                mock_articles_data = [
                    {
                        "title": f"Infosys beats revenue estimates with strong performance in financial services",
                        "summary": f"The IT major reported better-than-expected quarterly results with 16% growth in BFSI vertical and improved large deal wins.",
                        "source": "Economic Times", 
                        "days_ago": 3,
                        "sentiment": "positive",
                        "score": random.uniform(0.3, 0.5),
                        "url": "https://economictimes.indiatimes.com/tech/information-tech"
                    },
                    {
                        "title": f"Infosys raises full-year revenue guidance on strong client demand",
                        "summary": f"Management upgraded FY24 guidance citing robust pipeline in digital services and sustained momentum in cloud migration projects.",
                        "source": "Business Standard",
                        "days_ago": 4,
                        "sentiment": "positive", 
                        "score": random.uniform(0.4, 0.6),
                        "url": "https://www.business-standard.com/industry/news"
                    },
                    {
                        "title": f"Infosys expands European operations with new delivery center in Poland",
                        "summary": f"Strategic expansion aims to strengthen nearshore capabilities and serve European clients with enhanced service delivery and cost optimization.",
                        "source": "Mint",
                        "days_ago": 7,
                        "sentiment": "positive",
                        "score": random.uniform(0.2, 0.4),
                        "url": "https://www.livemint.com/industry/"
                    },
                    {
                        "title": f"Visa restrictions and talent shortage pose challenges for Infosys US operations",
                        "summary": f"Tightening immigration policies and skilled workforce availability concerns impact the company's onsite delivery model and growth projections.",
                        "source": "CNBC-TV18",
                        "days_ago": 1,
                        "sentiment": "negative",
                        "score": random.uniform(-0.3, -0.1),
                        "url": "https://www.cnbctv18.com/market/"
                    },
                    {
                        "title": f"Infosys sustainability initiatives align with client ESG requirements",
                        "summary": f"The company announced comprehensive carbon neutrality goals and sustainable business practices to meet evolving client sustainability mandates.",
                        "source": "Financial Express",
                        "days_ago": 10,
                        "sentiment": "neutral",
                        "score": random.uniform(0.0, 0.2),
                        "url": "https://www.financialexpress.com/industry/technology/"
                    }
                ]
            else:
                # Generic articles for other companies
                mock_articles_data = [
                    {
                        "title": f"{company_name} reports strong quarterly performance, beats consensus estimates",
                        "summary": f"{company_name} delivered robust financial results with revenue growth of 15% YoY, driven by operational excellence and market expansion strategies.",
                        "source": "Economic Times",
                        "days_ago": 4,
                        "sentiment": "positive",
                        "score": random.uniform(0.3, 0.6),
                        "url": "https://economictimes.indiatimes.com/markets/stocks/news"
                    },
                    {
                        "title": f"Analysts upgrade {company_name} on improving fundamentals and growth outlook",
                        "summary": f"Leading brokerages revised their price targets upward following strong operational metrics and positive management guidance for upcoming quarters.",
                        "source": "Business Standard",
                        "days_ago": 7,
                        "sentiment": "positive",
                        "score": random.uniform(0.2, 0.5),
                        "url": "https://www.business-standard.com/markets/news"
                    },
                    {
                        "title": f"{company_name} announces strategic expansion into emerging markets",
                        "summary": f"The company unveiled plans for geographic expansion with investments in new manufacturing facilities and distribution networks in Asia-Pacific region.",
                        "source": "Mint",
                        "days_ago": 9,
                        "sentiment": "positive",
                        "score": random.uniform(0.1, 0.4),
                        "url": "https://www.livemint.com/industry/"
                    },
                    {
                        "title": f"Market concerns over sector headwinds impact {company_name} stock",
                        "summary": f"Industry-wide challenges including raw material costs and competitive pressures have created near-term uncertainty for the company's growth trajectory.",
                        "source": "CNBC-TV18",
                        "days_ago": 1,
                        "sentiment": "negative",
                        "score": random.uniform(-0.4, -0.1),
                        "url": "https://www.cnbctv18.com/market/"
                    },
                    {
                        "title": f"ESG initiatives and sustainability focus shape {company_name}'s long-term strategy",
                        "summary": f"The company outlined comprehensive environmental and governance improvements as part of its commitment to sustainable business practices and stakeholder value.",
                        "source": "Financial Express",
                        "days_ago": 11,
                        "sentiment": "neutral",
                        "score": random.uniform(-0.05, 0.15),
                        "url": "https://www.financialexpress.com/industry/"
                    }
                ]
            
            mock_articles = []
            for i, article_data in enumerate(mock_articles_data):
                published_date = base_date - timedelta(days=article_data['days_ago'])
                mock_articles.append({
                    "id": f"mock_{ticker}_{i+1}",
                    "title": article_data['title'],
                    "summary": article_data['summary'],
                    "url": article_data['url'],
                    "source": {"name": article_data['source'], "domain": article_data['url'].split('//')[1].split('/')[0]},
                    "published_date": published_date.strftime("%Y-%m-%d"),
                    "sentiment": article_data['sentiment'],
                    "sentiment_score": article_data['score']
                })
            
            # Generate mock key topics
            mock_topics = [
                {"topic": "earnings", "frequency": 3, "sentiment": 0.4},
                {"topic": "growth", "frequency": 2, "sentiment": 0.3},
                {"topic": "market", "frequency": 2, "sentiment": 0.1}
            ]
            
            # Overall sentiment calculation
            avg_sentiment = sum(article["sentiment_score"] for article in mock_articles) / len(mock_articles)
            
            company_name = ticker.replace('.NS', '').replace('_', ' ')
            sentiment_label = "positive" if avg_sentiment > 0.1 else "neutral" if avg_sentiment > -0.1 else "negative"
            
            return {
                "ticker": ticker,
                "analysis_date": datetime.now().strftime("%Y-%m-%d"),
                "total_articles_analyzed": len(mock_articles),
                "recent_articles": mock_articles,
                "overall_sentiment": {
                    "score": avg_sentiment,
                    "label": sentiment_label,
                    "confidence": 0.75,
                    "trend": "improving" if avg_sentiment > 0.2 else "declining" if avg_sentiment < -0.2 else "stable"
                },
                "key_topics": mock_topics,
                "sentiment_breakdown": {
                    "last_7_days": avg_sentiment * 1.1,
                    "last_30_days": avg_sentiment,
                    "last_90_days": avg_sentiment * 0.9
                },
                "ai_insights": {
                    "summary": AnalysisService._generate_sophisticated_summary(company_name, ticker, mock_articles_data, sentiment_label, avg_sentiment),
                    "investment_implications": AnalysisService._generate_investment_implications(company_name, ticker, sentiment_label, avg_sentiment),
                    "key_themes": AnalysisService._extract_key_themes(company_name, ticker, mock_articles_data),
                    "risk_factors": AnalysisService._extract_risk_factors(company_name, ticker, mock_articles_data)
                },
                "sources": [
                    {"name": "Economic Times", "articles_count": 2},
                    {"name": "Business Standard", "articles_count": 1},
                    {"name": "Mint", "articles_count": 1},
                    {"name": "CNBC-TV18", "articles_count": 1}
                ],
                "company_reports": [],
                "industry_reports": [],
                "data_quality": "enhanced_mock_data"
            }
            
        except Exception as e:
            logger.error(f"Error generating mock news sentiment for {ticker}: {e}")
            return {
                "ticker": ticker,
                "analysis_date": datetime.now().strftime("%Y-%m-%d"),
                "total_articles_analyzed": 0,
                "recent_articles": [],
                "overall_sentiment": {
                    "score": 0.0,
                    "label": "neutral",
                    "confidence": 0.0,
                    "trend": "stable"
                },
                "key_topics": [],
                "sentiment_breakdown": {
                    "last_7_days": 0.0,
                    "last_30_days": 0.0,
                    "last_90_days": 0.0
                },
                "sources": [],
                "company_reports": [],
                "industry_reports": [],
                "data_quality": "error_fallback"
            }
    
    @staticmethod
    def _generate_sophisticated_summary(company_name: str, ticker: str, articles_data: list, sentiment_label: str, avg_sentiment: float) -> str:
        """Generate sophisticated AI summary like the user's example"""
        if 'RELIANCE' in ticker.upper():
            if avg_sentiment > 0.2:
                return f"Reliance has received mostly upbeat coverage over the past 2 weeks, with strong focus on retail expansion, green energy bets, and quarterly earnings beat. The conglomerate's diversification strategy and Jio's 5G rollout continue to drive investor confidence."
            elif avg_sentiment < -0.1:
                return f"Reliance faces mixed sentiment in recent coverage, with concerns around global oil price volatility affecting petrochemical margins and regulatory scrutiny over data localization. However, retail expansion and green energy initiatives provide positive counterbalance."
            else:
                return f"Reliance coverage has been balanced over recent weeks, highlighting both growth drivers like retail expansion and green energy investments, alongside headwinds from oil price volatility and regulatory considerations."
        elif 'TCS' in ticker.upper():
            if avg_sentiment > 0.2:
                return f"TCS has received largely positive coverage over the past 2 weeks, with strong focus on major deal wins, cloud transformation leadership, and robust quarterly performance. The IT giant's AI and automation capabilities continue to attract client confidence."
            elif avg_sentiment < -0.1:
                return f"TCS faces mixed sentiment in recent coverage, with concerns around hiring slowdown and currency headwinds affecting margins. However, strong deal pipeline and digital transformation expertise provide positive offset."
            else:
                return f"TCS coverage has been balanced over recent weeks, with positive developments around large deal wins and technology leadership balanced against industry-wide hiring concerns and margin pressures."
        else:
            positive_themes = [art['title'] for art in articles_data if art['sentiment'] == 'positive']
            negative_themes = [art['title'] for art in articles_data if art['sentiment'] == 'negative']
            
            if avg_sentiment > 0.2:
                return f"{company_name} has received largely positive coverage over the past 2 weeks, with strong focus on earnings performance, strategic expansion, and operational improvements. Analyst upgrades and growth initiatives continue to drive favorable sentiment."
            elif avg_sentiment < -0.1:
                return f"{company_name} faces mixed sentiment in recent coverage, with concerns around market headwinds and competitive pressures. However, strategic initiatives and operational excellence provide some positive offset."
            else:
                return f"{company_name} coverage has been balanced over recent weeks, with positive developments around strategic growth balanced against broader market concerns and sector-specific challenges."
    
    @staticmethod
    def _generate_investment_implications(company_name: str, ticker: str, sentiment_label: str, avg_sentiment: float) -> str:
        """Generate investment implications based on sentiment and company"""
        if avg_sentiment > 0.3:
            return f"Strong positive sentiment suggests {company_name} is well-positioned for near-term outperformance. Key catalysts include earnings momentum and strategic execution. Monitor for profit-taking at resistance levels."
        elif avg_sentiment > 0:
            return f"Moderately positive sentiment indicates selective opportunities for {company_name}. Focus on entry points during market corrections. Key risks include execution delays and market volatility."
        elif avg_sentiment < -0.2:
            return f"Negative sentiment creates headwinds for {company_name} in the near term. Recommend defensive positioning with focus on downside protection. Look for turnaround catalysts before increasing exposure."
        else:
            return f"Mixed sentiment suggests range-bound performance for {company_name}. Selective opportunities exist on weakness. Focus on risk management and position sizing."
    
    @staticmethod 
    def _extract_key_themes(company_name: str, ticker: str, articles_data: list) -> list:
        """Extract key themes from articles"""
        if 'RELIANCE' in ticker.upper():
            return ["retail expansion", "green energy transition", "5G infrastructure", "earnings performance"]
        else:
            themes = []
            for article in articles_data:
                if 'earnings' in article['title'].lower() or 'results' in article['title'].lower():
                    themes.append("earnings performance")
                if 'expansion' in article['title'].lower() or 'growth' in article['title'].lower():
                    themes.append("strategic expansion")
                if 'analyst' in article['title'].lower() or 'upgrade' in article['title'].lower():
                    themes.append("analyst sentiment")
                if 'market' in article['title'].lower() or 'sector' in article['title'].lower():
                    themes.append("market dynamics")
            return list(set(themes[:4]))  # Unique themes, max 4
    
    @staticmethod
    def _extract_risk_factors(company_name: str, ticker: str, articles_data: list) -> list:
        """Extract risk factors from articles"""  
        if 'RELIANCE' in ticker.upper():
            return ["global oil price volatility", "regulatory scrutiny on data localization"]
        else:
            risks = []
            for article in articles_data:
                if article['sentiment'] == 'negative':
                    if 'market' in article['title'].lower():
                        risks.append("market volatility")
                    if 'regulatory' in article['title'].lower() or 'compliance' in article['title'].lower():
                        risks.append("regulatory changes")
                    if 'competition' in article['title'].lower():
                        risks.append("competitive pressures")
                    if 'cost' in article['title'].lower():
                        risks.append("cost inflation")
            
            if not risks:
                risks = ["general market conditions", "execution risks"]
            return list(set(risks[:3]))  # Unique risks, max 3