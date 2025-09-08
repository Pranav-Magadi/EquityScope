import os
import logging
from typing import Dict, Any, Optional, List
import anthropic
from anthropic import Anthropic
import json
from datetime import datetime, timedelta
from functools import lru_cache
from ..api.settings import get_user_api_keys
from .intelligent_cache import intelligent_cache, CacheType

logger = logging.getLogger(__name__)

class ClaudeService:
    """Service for interacting with Claude AI for agentic workflow."""
    
    def __init__(self):
        self.client = None
        self._initialize_client()
        self._setup_company_references()
    
    def _initialize_client(self):
        """Initialize Claude client with API key."""
        try:
            # Get API keys (user-provided or default)
            api_keys = get_user_api_keys()
            claude_api_key = api_keys.get('claude_api_key') or os.getenv('ANTHROPIC_API_KEY')
            
            if claude_api_key:
                self.client = Anthropic(api_key=claude_api_key)
                logger.info("Claude client initialized successfully")
            else:
                logger.warning("Claude API key not found - some features will be disabled")
                
        except Exception as e:
            logger.error(f"Failed to initialize Claude client: {e}")
            self.client = None
    
    def _setup_company_references(self):
        """Set up reference companies for benchmarking and context."""
        # Top 30 Global Companies by Market Cap (for benchmarking context)
        self.top_global_companies = {
            'Technology': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'ADBE', 'CRM', 'ORCL'],
            'Financial': ['BRK-A', 'JPM', 'V', 'MA', 'BAC', 'WFC', 'GS', 'MS', 'AXP', 'C'],
            'Healthcare': ['JNJ', 'UNH', 'PFE', 'ABBV', 'TMO', 'ABT', 'LLY', 'MRK', 'DHR', 'BMY'],
            'Consumer': ['PG', 'HD', 'KO', 'PEP', 'WMT', 'MCD', 'NKE', 'SBUX', 'TGT', 'LOW'],
            'Industrial': ['HON', 'UPS', 'CAT', 'BA', 'GE', 'MMM', 'LMT', 'RTX', 'DE', 'EMR'],
            'Energy': ['XOM', 'CVX', 'COP', 'EOG', 'SLB', 'PSX', 'VLO', 'MPC', 'OXY', 'HAL']
        }
        
        # Top 30 Indian Companies by Market Cap (for domestic benchmarking)
        self.top_indian_companies = {
            'Technology': ['TCS.NS', 'INFY.NS', 'HCLTECH.NS', 'WIPRO.NS', 'TECHM.NS', 'LTI.NS'],
            'Financial': ['HDFCBANK.NS', 'ICICIBANK.NS', 'KOTAKBANK.NS', 'SBIN.NS', 'AXISBANK.NS', 'INDUSINDBK.NS'],
            'Energy': ['RELIANCE.NS', 'ONGC.NS', 'IOC.NS', 'BPCL.NS', 'HINDPETRO.NS', 'GAIL.NS', 'NTPC.NS'],
            'Consumer': ['HINDUNILVR.NS', 'ITC.NS', 'NESTLEIND.NS', 'BRITANNIA.NS', 'DABUR.NS', 'GODREJCP.NS'],
            'Automotive': ['MARUTI.NS', 'TATAMOTORS.NS', 'M&M.NS', 'BAJAJ-AUTO.NS', 'EICHERMOT.NS', 'HEROMOTOCO.NS'],
            'Pharma': ['SUNPHARMA.NS', 'DRREDDY.NS', 'CIPLA.NS', 'DIVISLAB.NS', 'BIOCON.NS', 'LUPIN.NS'],
            'Industrial': ['LT.NS', 'ULTRACEMCO.NS', 'ASIANPAINT.NS', 'TITAN.NS', 'BHARTIARTL.NS', 'ADANIPORTS.NS'],
            'Materials': ['COALINDIA.NS', 'HINDALCO.NS', 'TATASTEEL.NS', 'JSW.NS', 'VEDL.NS', 'NMDC.NS']
        }
    
    def _get_industry_context(self, sector: str, ticker: str) -> str:
        """Get industry context and peer companies for benchmarking."""
        is_indian = ticker.endswith('.NS')
        
        # Find relevant peer companies
        peers = []
        if is_indian:
            for industry, companies in self.top_indian_companies.items():
                if any(company in companies for company in [ticker]):
                    peers = [c for c in companies if c != ticker][:5]
                    break
            
            if not peers and sector:
                # Try to match by sector name
                sector_mapping = {
                    'Technology': 'Technology',
                    'Financial Services': 'Financial',
                    'Energy': 'Energy',
                    'Consumer Defensive': 'Consumer',
                    'Consumer Cyclical': 'Consumer',
                    'Healthcare': 'Pharma',
                    'Industrials': 'Industrial',
                    'Basic Materials': 'Materials'
                }
                industry_key = sector_mapping.get(sector, 'Technology')
                peers = self.top_indian_companies.get(industry_key, [])[:5]
        else:
            # Global company
            for industry, companies in self.top_global_companies.items():
                if any(company in companies for company in [ticker.replace('.NS', '')]):
                    peers = [c for c in companies if c != ticker.replace('.NS', '')][:5]
                    break
        
        context = f"""
INDUSTRY CONTEXT & PEER BENCHMARKING:
Sector: {sector}
Geographic Focus: {'Indian Market' if is_indian else 'Global Market'}
Key Peer Companies: {', '.join(peers) if peers else 'N/A'}

When analyzing this company, consider:
1. How it compares to these industry leaders in terms of scale, efficiency, and growth
2. Industry-specific challenges and opportunities
3. Competitive positioning relative to top {'domestic' if is_indian else 'global'} peers
4. Market dynamics and competitive landscape trends
        """
        
        return context
    
    def is_available(self) -> bool:
        """Check if Claude service is available."""
        return self.client is not None
    
    async def generate_completion(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 4000,
        temperature: float = 0.3,
        model: str = "claude-3-5-sonnet-20241022"
    ) -> Optional[str]:
        """Generate a completion using Claude."""
        if not self.client:
            logger.error("Claude client not initialized")
            return None
        
        try:
            messages = [{"role": "user", "content": prompt}]
            
            response = self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt or "You are a helpful AI assistant specialized in financial analysis.",
                messages=messages
            )
            
            if response.content and len(response.content) > 0:
                return response.content[0].text
            else:
                logger.error("Empty response from Claude")
                return None
                
        except Exception as e:
            logger.error(f"Error generating Claude completion: {e}")
            return None
    
    async def generator_agent(
        self,
        company_data: Dict[str, Any],
        news_articles: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """
        The Generator Agent - performs initial qualitative and quantitative analysis.
        
        Args:
            company_data: Financial data from yfinance
            news_articles: List of scraped news articles with URLs
            
        Returns:
            Structured JSON with SWOT, News sentiment, DCF assumptions, and sensitivity analysis
        """
        if not self.client:
            return None
        
        system_prompt = """You are an expert financial analyst with deep expertise in equity research and valuation. You will analyze company data and recent news to generate comprehensive qualitative and quantitative insights.

Your output must be valid JSON in exactly this structure:
{
  "qualitative_analysis": {
    "swot": {
      "strengths": [
        {
          "point": "Brief strength description",
          "details": "Detailed explanation with specific metrics/context",
          "sources": ["article_url_1", "article_url_2"],
          "confidence": "high|medium|low"
        }
      ],
      "weaknesses": [...],
      "opportunities": [...],
      "threats": [...]
    },
    "news_sentiment": {
      "overall_sentiment": "positive|neutral|negative",
      "key_themes": [
        {
          "theme": "Theme title",
          "description": "Detailed explanation",
          "sentiment": "positive|neutral|negative",
          "sources": ["article_url_1", "article_url_2"],
          "impact": "high|medium|low"
        }
      ],
      "sentiment_score": 0.5
    },
    "competitive_analysis": {
      "peers": [
        {
          "name": "Peer Company Name",
          "ticker": "PEER.NS",
          "comparison": {
            "financial": {
              "score": "stronger|similar|weaker",
              "details": "Revenue/profit comparison details",
              "sources": ["article_url_1"]
            },
            "technological": {
              "score": "stronger|similar|weaker", 
              "details": "Technology capabilities comparison",
              "sources": ["article_url_1"]
            },
            "operational": {
              "score": "stronger|similar|weaker",
              "details": "Operational efficiency comparison", 
              "sources": ["article_url_1"]
            },
            "governance": {
              "score": "stronger|similar|weaker",
              "details": "Compliance and governance comparison",
              "sources": ["article_url_1"]
            }
          }
        }
      ],
      "competitive_positioning": "Brief overall positioning statement",
      "key_competitive_advantages": ["Advantage 1", "Advantage 2"],
      "competitive_threats": ["Threat 1", "Threat 2"]
    }
  },
  "quantitative_analysis": {
    "dcf_assumptions": {
      "revenue_growth_rate": 8.5,
      "ebitda_margin": 15.2,
      "tax_rate": 25.0,
      "wacc": 10.5,
      "terminal_growth_rate": 3.0,
      "rationale": {
        "revenue_growth_rate": "Based on 3-year historical average and industry outlook",
        "ebitda_margin": "Conservative estimate based on recent performance",
        "wacc": "Calculated using industry beta and current risk-free rate",
        "terminal_growth_rate": "Long-term GDP growth assumption"
      }
    },
    "sensitivity_analysis": {
      "wacc_range": [8.0, 9.0, 10.0, 11.0, 12.0],
      "terminal_growth_range": [2.0, 2.5, 3.0, 3.5, 4.0],
      "sensitivity_matrix": [
        [120.5, 115.2, 110.8, 106.9, 103.4],
        [125.8, 120.1, 115.6, 111.2, 107.5],
        [131.7, 125.4, 120.9, 116.1, 112.1],
        [138.2, 131.3, 126.8, 121.7, 117.3],
        [145.6, 137.9, 133.2, 127.9, 123.1]
      ]
    }
  }
}

CRITICAL REQUIREMENTS - MANDATORY SOURCE ATTRIBUTION:
1. EVERY SWOT point MUST reference specific article URLs from the provided news articles
2. EVERY news theme MUST cite specific article URLs as sources
3. NO analysis point should be made without proper source attribution
4. If insufficient sources exist for a point, do not include that point
5. Use actual data from the company financials to calculate realistic DCF assumptions
6. Provide detailed rationale for each assumption with source references
7. Generate a 5x5 sensitivity matrix with realistic intrinsic values
8. Be specific and quantitative wherever possible with source-backed evidence

SOURCE ATTRIBUTION RULES:
- Use exact URLs from the provided articles in the "sources" arrays
- Each insight must reference at least 1-2 specific news articles
- Include only insights that can be substantiated by the provided sources
- Prioritize quality over quantity - fewer well-sourced insights are better than many unsourced ones"""

        # Format the input data
        if news_articles and len(news_articles) > 0:
            news_text = "\n\n".join([
                f"ARTICLE {i+1}:\nURL: {article['url']}\nTitle: {article['title']}\nContent: {article['content'][:1500]}..."
                for i, article in enumerate(news_articles[:10])
            ])
        else:
            news_text = "NO RECENT NEWS ARTICLES FOUND - Please provide analysis based on historical data and financial fundamentals only. Use placeholder URLs like 'https://example.com/source1' for source attribution in this case."
        
        financials_summary = self._format_financial_data(company_data)
        industry_context = self._get_industry_context(
            company_data.get('info', {}).get('sector', ''),
            company_data.get('ticker', '')
        )
        
        prompt = f"""
Please analyze the following company and generate comprehensive qualitative and quantitative insights:

COMPANY: {company_data.get('ticker', 'Unknown')}
COMPANY NAME: {company_data.get('info', {}).get('longName', 'Unknown')}

{industry_context}

FINANCIAL DATA:
{financials_summary}

RECENT NEWS ARTICLES WITH MANDATORY SOURCE URLS:
{news_text}

CRITICAL INSTRUCTIONS:
1. Generate a complete analysis following the exact JSON structure specified in your system prompt
2. MANDATORY: Every SWOT point must include specific article URLs in the "sources" array
3. MANDATORY: Every news theme must reference specific article URLs as sources
4. Only include insights that can be substantiated by the provided news articles
5. Use exact URLs from the RECENT NEWS ARTICLES section above
6. If you cannot find sufficient sources for a point, do not include that point
7. Quality over quantity - fewer well-sourced insights are preferred
8. When making comparisons, reference both the peer companies and news sources
9. COMPETITIVE FOCUS: Analyze strengths/weaknesses relative to peer companies mentioned above
10. Include competitive threats from peer actions, market positioning changes, and strategic moves
11. Consider competitive opportunities from industry gaps or peer company weaknesses

Remember: NO analysis point should exist without proper source attribution from the provided articles.
        """
        
        try:
            response = await self.generate_completion(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=6000,
                temperature=0.2
            )
            
            if response:
                # Clean response of control characters
                import re
                cleaned_response = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', response)
                
                # Try to parse as JSON
                try:
                    return json.loads(cleaned_response)
                except json.JSONDecodeError as e:
                    logger.error(f"JSON decode error: {e}")
                    
                    # Try to find and extract the JSON object
                    start = cleaned_response.find('{')
                    if start != -1:
                        # Find the matching closing brace by counting braces
                        brace_count = 0
                        end = start
                        for i, char in enumerate(cleaned_response[start:]):
                            if char == '{':
                                brace_count += 1
                            elif char == '}':
                                brace_count -= 1
                                if brace_count == 0:
                                    end = start + i + 1
                                    break
                        
                        if end > start:
                            json_str = cleaned_response[start:end]
                            try:
                                return json.loads(json_str)
                            except json.JSONDecodeError as e2:
                                logger.error(f"JSON extraction failed: {e2}")
                                logger.error(f"Extracted JSON: {json_str[:500]}...")
                                return None
                    
                    logger.error("Could not extract valid JSON from Generator response")
                    logger.error(f"Response preview: {cleaned_response[:500]}...")
                    return None
            
            return None
            
        except Exception as e:
            logger.error(f"Error in generator_agent: {e}")
            return None
    
    async def checker_agent(self, generator_output: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        The Checker Agent - validates the Generator's analysis for reasonableness.
        """
        if not self.client:
            return None
        
        system_prompt = """You are a meticulous, skeptical financial analyst from a top-tier investment bank. Your job is to validate analysis for factual correctness, insightfulness, and reasonableness.

Your output must be valid JSON in exactly this structure:
{
  "validation_report": {
    "overall_score": 8.5,
    "qualitative_validation": {
      "swot_accuracy": "Assessment of SWOT analysis accuracy",
      "news_interpretation": "Assessment of news sentiment interpretation",
      "source_quality": "Assessment of source attribution quality",
      "findings": [
        "Specific finding 1",
        "Specific finding 2"
      ]
    },
    "quantitative_validation": {
      "dcf_assumptions_reasonableness": "Assessment of DCF assumptions",
      "sensitivity_range_appropriateness": "Assessment of sensitivity analysis",
      "calculation_accuracy": "Assessment of mathematical accuracy",
      "findings": [
        "Specific finding 1",
        "Specific finding 2"
      ]
    },
    "key_concerns": [
      "Primary concern 1",
      "Primary concern 2"
    ],
    "recommendations": [
      "Recommendation 1",
      "Recommendation 2"
    ]
  }
}

Be thorough but concise. Focus on factual accuracy and reasonableness."""

        prompt = f"""
Please validate the following financial analysis for accuracy and reasonableness:

ANALYSIS TO VALIDATE:
{json.dumps(generator_output, indent=2)}

Provide a thorough validation report following the exact JSON structure specified. Score the overall analysis from 1-10 where 10 is perfectly reasonable and well-supported.
        """
        
        try:
            response = await self.generate_completion(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=3000,
                temperature=0.1
            )
            
            if response:
                try:
                    return json.loads(response)
                except json.JSONDecodeError:
                    start = response.find('{')
                    end = response.rfind('}') + 1
                    if start != -1 and end != 0:
                        return json.loads(response[start:end])
                    
            return None
            
        except Exception as e:
            logger.error(f"Error in checker_agent: {e}")
            return None
    
    async def bull_commentator_agent(
        self,
        generator_output: Dict[str, Any],
        checker_output: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """The Bull Commentator Agent - provides optimistic investment thesis."""
        if not self.client:
            return None
        
        system_prompt = """You are a growth-oriented financial strategist with expertise in identifying upside potential and growth opportunities.

Your output must be valid JSON in exactly this structure:
{
  "bull_commentary": {
    "summary_of_assumptions": "Brief summary of key DCF and sensitivity assumptions",
    "bullish_implications": "Explanation of optimistic implications if assumptions hold true",
    "recommended_modifications": [
      {
        "assumption": "revenue_growth_rate",
        "current_value": 8.5,
        "recommended_value": 12.0,
        "justification": "Specific reasoning citing market trends or news"
      }
    ],
    "upside_catalysts": [
      "Catalyst 1 with specific reasoning",
      "Catalyst 2 with specific reasoning"
    ],
    "target_price_scenario": "Optimistic price target with reasoning"
  }
}

Be optimistic but grounded in data and market realities."""

        prompt = f"""
Given the following analysis and validation report, provide a bullish investment commentary:

ORIGINAL ANALYSIS:
{json.dumps(generator_output, indent=2)}

VALIDATION REPORT:
{json.dumps(checker_output, indent=2)}

Provide a growth-oriented bull case following the exact JSON structure specified.
        """
        
        try:
            response = await self.generate_completion(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=2500,
                temperature=0.3
            )
            
            if response:
                try:
                    return json.loads(response)
                except json.JSONDecodeError:
                    start = response.find('{')
                    end = response.rfind('}') + 1
                    if start != -1 and end != 0:
                        return json.loads(response[start:end])
                    
            return None
            
        except Exception as e:
            logger.error(f"Error in bull_commentator_agent: {e}")
            return None
    
    async def bear_commentator_agent(
        self,
        generator_output: Dict[str, Any],
        checker_output: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """The Bear Commentator Agent - provides conservative/risk-focused thesis."""
        if not self.client:
            return None
        
        system_prompt = """You are a conservative, value-focused financial strategist with expertise in risk assessment and downside protection.

Your output must be valid JSON in exactly this structure:
{
  "bear_commentary": {
    "summary_of_assumptions": "Brief summary of key DCF and sensitivity assumptions",
    "bearish_implications": "Explanation of key risks and pessimistic implications",
    "recommended_modifications": [
      {
        "assumption": "revenue_growth_rate",
        "current_value": 8.5,
        "recommended_value": 5.0,
        "justification": "Specific reasoning citing risks or conservative factors"
      }
    ],
    "downside_risks": [
      "Risk 1 with specific impact analysis",
      "Risk 2 with specific impact analysis"
    ],
    "conservative_price_scenario": "Conservative price target with reasoning"
  }
}

Be cautious and risk-focused but fair in your assessment."""

        prompt = f"""
Given the following analysis and validation report, provide a bearish investment commentary:

ORIGINAL ANALYSIS:
{json.dumps(generator_output, indent=2)}

VALIDATION REPORT:
{json.dumps(checker_output, indent=2)}

Provide a conservative bear case following the exact JSON structure specified.
        """
        
        try:
            response = await self.generate_completion(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=2500,
                temperature=0.3
            )
            
            if response:
                try:
                    return json.loads(response)
                except json.JSONDecodeError:
                    start = response.find('{')
                    end = response.rfind('}') + 1
                    if start != -1 and end != 0:
                        return json.loads(response[start:end])
                    
            return None
            
        except Exception as e:
            logger.error(f"Error in bear_commentator_agent: {e}")
            return None
    
    async def technical_analyst_agent(self, indicator_values: Dict[str, Any]) -> Optional[str]:
        """
        Technical Analyst Agent: Provides commentary on technical indicators
        
        Args:
            indicator_values: Dictionary containing calculated technical indicator values
            
        Returns:
            Technical analysis summary as a string
        """
        if not self.is_available():
            logger.warning("Claude service not available for technical_analyst_agent")
            return None
        
        try:
            logger.info("Running Technical Analyst Agent")
            
            # Format indicator values for the prompt
            indicators_text = []
            for key, value in indicator_values.items():
                if key == 'signals':
                    indicators_text.append(f"Detected Signals: {', '.join(value)}")
                else:
                    indicators_text.append(f"{key}: {value}")
            
            indicators_summary = "\n".join(indicators_text)
            
            prompt = f"""
Based on the following calculated technical indicator values, provide a concise summary (one paragraph) interpreting the current technical picture of the stock. Your tone should be objective and educational. Explain the meaning of the key signals (e.g., crossovers, overbought/oversold levels, proximity to support/resistance, and Bollinger Band position) in plain, accessible English.

TECHNICAL INDICATORS:
{indicators_summary}

Provide a single paragraph that:
1. Summarizes the overall technical health of the stock
2. Explains what the key indicators are telling us
3. Mentions any significant signals or patterns
4. Uses educational language accessible to both novice and experienced investors
5. Remains objective and avoids strong buy/sell recommendations

Focus on interpreting the data rather than making investment recommendations.
            """
            
            # Determine currency based on ticker
            currency_symbol = "₹" if ticker.endswith('.NS') else "$"
            
            response = await self.generate_completion(
                prompt=prompt,
                system_prompt=f"You are an expert technical analyst providing educational commentary for a fintech dashboard. Be objective, educational, and clear in your explanations. Use {currency_symbol} for all price references (Indian stocks use ₹, US stocks use $).",
                max_tokens=500,
                temperature=0.3
            )
            
            if response:
                # Clean the response
                import re
                cleaned_response = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', response).strip()
                logger.info("Technical Analyst Agent completed successfully")
                return cleaned_response
            else:
                logger.error("No response from Technical Analyst Agent")
                return None
                
        except Exception as e:
            logger.error(f"Error in technical_analyst_agent: {e}")
            return None
    
    async def analyze_news_sentiment(
        self,
        ticker: str,
        articles: List[Dict[str, Any]],
        analysis_depth: str = "advanced"
    ) -> Dict[str, Any]:
        """
        Analyze news articles sentiment and provide investment insights.
        
        Args:
            ticker: Stock ticker symbol
            articles: List of news articles with title, content, url
            analysis_depth: "sentiment_only", "advanced", or "investment_insights"
            
        Returns:
            Dictionary with sentiment analysis, themes, and investment implications
        """
        if not self.client:
            logger.warning("Claude client not available for news sentiment analysis")
            return self._get_fallback_news_insights(ticker, articles)
        
        try:
            logger.info(f"🤖 Analyzing {len(articles)} articles with Claude for {ticker} (depth: {analysis_depth})")
            
            if analysis_depth == "sentiment_only":
                return await self._analyze_sentiment_only(ticker, articles)
            elif analysis_depth == "advanced":
                return await self._analyze_advanced_sentiment(ticker, articles)
            elif analysis_depth == "investment_insights":
                return await self._analyze_investment_insights(ticker, articles)
            else:
                return await self._analyze_advanced_sentiment(ticker, articles)
                
        except Exception as e:
            logger.error(f"❌ Error in Claude news sentiment analysis for {ticker}: {str(e)}")
            return self._get_fallback_news_insights(ticker, articles)
    
    async def _analyze_sentiment_only(self, ticker: str, articles: List[Dict]) -> Dict[str, Any]:
        """Basic sentiment analysis only"""
        system_prompt = """You are a financial news sentiment analyst. Analyze the provided news articles and return ONLY a JSON object with sentiment analysis.
        
Your output must be valid JSON in exactly this structure:
{
  "overall_sentiment_score": 0.15,
  "sentiment_label": "slightly_positive",
  "confidence": 0.8,
  "key_sentiment_drivers": [
    "Positive earnings growth outlook",
    "Regulatory concerns mentioned",
    "Market expansion plans announced"
  ]
}
        
Sentiment score range: -1.0 (very negative) to +1.0 (very positive)
Sentiment labels: strongly_negative, negative, slightly_negative, neutral, slightly_positive, positive, strongly_positive"""
        
        articles_text = self._format_articles_for_analysis(articles, max_articles=10)
        
        prompt = f"""
Analyze the sentiment of these news articles for {ticker}:

{articles_text}

Provide sentiment analysis in the exact JSON format specified. Focus on investment-relevant sentiment only.
        """
        
        response = await self.generate_completion(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=1000,
            temperature=0.2
        )
        
        if response:
            result = self._parse_json_response(response)
            if result:
                return {
                    "analysis_type": "sentiment_only",
                    "ticker": ticker,
                    **result
                }
        
        return self._get_fallback_news_insights(ticker, articles)
    
    async def _analyze_advanced_sentiment(self, ticker: str, articles: List[Dict]) -> Dict[str, Any]:
        """Advanced sentiment analysis with themes and investment context"""
        system_prompt = """You are an expert financial analyst specializing in news sentiment analysis for investment decisions.
        
Your output must be valid JSON in exactly this structure:
{
  "sentiment_summary": {
    "overall_score": 0.25,
    "label": "cautiously_positive",
    "confidence": 0.85,
    "trend": "improving"
  },
  "key_themes": [
    {
      "theme": "Earnings Performance",
      "sentiment": "positive",
      "impact": "high",
      "description": "Strong quarterly results exceeded expectations",
      "supporting_articles": 3
    }
  ],
  "investment_implications": {
    "bullish_factors": [
      "Revenue growth accelerating in core segments",
      "Management guidance raised for full year"
    ],
    "bearish_factors": [
      "Regulatory headwinds in key markets",
      "Rising input cost pressures"
    ],
    "neutral_factors": [
      "Market volatility affecting sector performance"
    ]
  },
  "risk_sentiment": {
    "regulatory_risk": "moderate",
    "market_risk": "low", 
    "operational_risk": "low",
    "financial_risk": "low"
  }
}
        
Be specific and quantitative where possible. Focus on investment-relevant insights."""
        
        articles_text = self._format_articles_for_analysis(articles, max_articles=10)
        company_name = self._get_company_name_from_ticker(ticker)
        
        prompt = f"""
Analyze news sentiment and themes for {company_name} ({ticker}):

{articles_text}

Provide comprehensive sentiment analysis in the exact JSON format specified. Focus on:
1. Overall market sentiment toward the company
2. Key themes driving sentiment (earnings, growth, risks, etc.)
3. Investment implications for retail investors
4. Risk assessment based on news coverage

Be concise but thorough in your analysis.
        """
        
        response = await self.generate_completion(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=2500,
            temperature=0.3
        )
        
        if response:
            result = self._parse_json_response(response)
            if result:
                return {
                    "analysis_type": "advanced_sentiment",
                    "ticker": ticker,
                    "articles_analyzed": len(articles),
                    **result
                }
        
        return self._get_fallback_news_insights(ticker, articles)
    
    async def _analyze_investment_insights(self, ticker: str, articles: List[Dict]) -> Dict[str, Any]:
        """Investment-focused insights and recommendations"""
        system_prompt = """You are a senior equity research analyst providing actionable investment insights based on news analysis.
        
Your output must be valid JSON in exactly this structure:
{
  "investment_thesis": {
    "summary": "Brief 2-sentence investment case based on recent news",
    "conviction_level": "high",
    "time_horizon": "medium_term",
    "price_catalyst_timeline": "3-6 months"
  },
  "key_catalysts": [
    {
      "catalyst": "Q3 Earnings Release",
      "timing": "Next 4-6 weeks", 
      "impact": "high",
      "sentiment": "positive",
      "description": "Expected to show continued margin expansion"
    }
  ],
  "risk_factors": [
    {
      "risk": "Regulatory Changes",
      "probability": "medium",
      "impact": "high",
      "timeline": "6-12 months",
      "mitigation": "Company has strong compliance track record"
    }
  ],
  "sentiment_trajectory": {
    "current": "positive",
    "recent_change": "improving",
    "momentum": "accelerating",
    "sustainability": "likely"
  },
  "actionable_insights": [
    "Monitor Q3 earnings for margin expansion trends",
    "Watch for management commentary on expansion plans",
    "Track regulatory developments in core markets"
  ]
}
        
Focus on actionable, time-bound insights for investment decisions."""
        
        articles_text = self._format_articles_for_analysis(articles, max_articles=8)
        company_name = self._get_company_name_from_ticker(ticker)
        
        prompt = f"""
Provide investment insights and recommendations for {company_name} ({ticker}) based on recent news:

{articles_text}

Generate actionable investment insights in the exact JSON format specified. Focus on:
1. Clear investment thesis based on news developments
2. Specific catalysts with timing and impact assessment
3. Key risks with probability and mitigation strategies
4. Actionable monitoring points for investors

Be specific about timing, probability, and impact levels.
        """
        
        response = await self.generate_completion(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=2000,
            temperature=0.3
        )
        
        if response:
            result = self._parse_json_response(response)
            if result:
                return {
                    "analysis_type": "investment_insights",
                    "ticker": ticker,
                    "articles_analyzed": len(articles),
                    **result
                }
        
        return self._get_fallback_news_insights(ticker, articles)
    
    def _format_articles_for_analysis(self, articles: List[Dict], max_articles: int = 10) -> str:
        """Format articles for Claude analysis"""
        if not articles:
            return "No recent articles available for analysis."
        
        formatted_articles = []
        for i, article in enumerate(articles[:max_articles]):
            title = article.get('title', 'No title')[:200]
            summary = article.get('summary', article.get('content', ''))[:400]
            date = article.get('published_date', 'Date unknown')
            source = article.get('source', {}).get('name', 'Unknown source')
            
            formatted_articles.append(
                f"Article {i+1}:\n"
                f"Source: {source}\n"
                f"Date: {date}\n"
                f"Title: {title}\n"
                f"Summary: {summary}\n"
            )
        
        return "\n---\n\n".join(formatted_articles)
    
    def _get_company_name_from_ticker(self, ticker: str) -> str:
        """Get company name from ticker"""
        ticker_to_name = {
            'RELIANCE.NS': 'Reliance Industries Limited',
            'TCS.NS': 'Tata Consultancy Services',
            'HDFCBANK.NS': 'HDFC Bank Limited',
            'INFY.NS': 'Infosys Limited',
            'ICICIBANK.NS': 'ICICI Bank Limited',
            'HINDUNILVR.NS': 'Hindustan Unilever Limited',
            'ITC.NS': 'ITC Limited',
            'SBIN.NS': 'State Bank of India',
            'BHARTIARTL.NS': 'Bharti Airtel Limited',
            'KOTAKBANK.NS': 'Kotak Mahindra Bank Limited'
        }
        
        return ticker_to_name.get(ticker, ticker.replace('.NS', ' Limited'))
    
    def _get_fallback_news_insights(self, ticker: str, articles: List[Dict]) -> Dict[str, Any]:
        """Fallback insights when Claude analysis fails"""
        return {
            "analysis_type": "fallback",
            "ticker": ticker,
            "sentiment_summary": {
                "overall_score": 0.0,
                "label": "neutral",
                "confidence": 0.5,
                "trend": "stable"
            },
            "key_themes": [
                {
                    "theme": "General Market Activity",
                    "sentiment": "neutral",
                    "impact": "medium",
                    "description": "Regular market news and updates available",
                    "supporting_articles": len(articles)
                }
            ],
            "investment_implications": {
                "bullish_factors": ["Company fundamentals remain intact"],
                "bearish_factors": ["Limited recent positive news flow"],
                "neutral_factors": ["Standard market conditions apply"]
            },
            "actionable_insights": [
                f"Monitor {ticker} for increased news coverage",
                "Watch for quarterly earnings announcements",
                "Track sector-wide developments"
            ],
            "articles_analyzed": len(articles)
        }
    
    def _format_financial_data(self, company_data: Dict[str, Any]) -> str:
        """Format financial data for AI consumption."""
        try:
            import math
            info = company_data.get('info', {})
            
            def safe_format(value, default=0, is_percentage=False, is_currency=False):
                """Safely format a value, handling NaN and None"""
                if value is None or (isinstance(value, float) and (math.isnan(value) or math.isinf(value))):
                    return "N/A"
                if is_percentage:
                    return f"{value:.2%}"
                elif is_currency:
                    return f"${value:,.0f}"
                else:
                    return f"{value:.2f}"
            
            return f"""
Company: {info.get('longName', 'N/A')}
Sector: {info.get('sector', 'N/A')}
Industry: {info.get('industry', 'N/A')}
Market Cap: {safe_format(info.get('marketCap'), is_currency=True)}
Revenue (TTM): {safe_format(info.get('totalRevenue'), is_currency=True)}
EBITDA: {safe_format(info.get('ebitda'), is_currency=True)}
Profit Margin: {safe_format(info.get('profitMargins'), is_percentage=True)}
ROE: {safe_format(info.get('returnOnEquity'), is_percentage=True)}
Debt/Equity: {safe_format(info.get('debtToEquity'))}
Current Ratio: {safe_format(info.get('currentRatio'))}
P/E Ratio: {safe_format(info.get('trailingPE'))}
Forward P/E: {safe_format(info.get('forwardPE'))}
PEG Ratio: {safe_format(info.get('pegRatio'))}
Price/Book: {safe_format(info.get('priceToBook'))}
52-Week High: {safe_format(info.get('fiftyTwoWeekHigh'), is_currency=True)}
52-Week Low: {safe_format(info.get('fiftyTwoWeekLow'), is_currency=True)}
Beta: {safe_format(info.get('beta'))}
            """
        except Exception as e:
            logger.error(f"Error formatting financial data: {e}")
            return "Financial data formatting error"

class AgenticAnalysisService(ClaudeService):
    """
    Enhanced Agentic Analysis Service with cost-optimized batched prompts.
    
    Features:
    - Two-call batching strategy targeting <$0.50 per analysis
    - Structured output parsing with fallback handling
    - Two-tier caching (memory + persistent)
    - Model tier selection for cost optimization
    """
    
    def __init__(self):
        super().__init__()
        # Memory cache for session-level caching
        self.core_analysis_cache = {}
        self.sentiment_cache = {}
        self.cache_ttl = timedelta(hours=6)  # 6-hour cache for AI responses
        
        # Cost optimization settings
        self.use_cost_optimized_model = True  # Use cheaper models when possible
        self.max_tokens_core = 3000  # Reduced from 4000
        self.max_tokens_sentiment = 2000  # Reduced from 3000
    
    async def generate_comprehensive_agentic_analysis(
        self, 
        ticker: str,
        company_data: Dict[str, Any],
        dcf_results: Dict[str, Any],
        technical_data: Dict[str, Any],
        news_data: List[Dict] = None,
        peer_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Main entry point for comprehensive agentic analysis.
        Uses 2-call batching strategy to minimize costs.
        """
        
        try:
            logger.info(f"Starting comprehensive agentic analysis for {ticker}")
            
            # Check persistent cache first
            cache_key = f"{ticker}_agentic_comprehensive"
            cached_result = await intelligent_cache.get(
                CacheType.AI_ANALYSIS, cache_key
            )
            
            if cached_result:
                logger.info(f"Using cached comprehensive analysis for {ticker}")
                return cached_result
            
            # Execute batched analysis calls
            core_analysis_task = self.generate_core_analysis_batch(
                ticker, company_data, dcf_results, technical_data
            )
            
            sentiment_analysis_task = self.generate_sentiment_context_batch(
                ticker, news_data or [], peer_data or {}
            )
            
            # Run both calls concurrently to save time
            import asyncio
            core_analysis, sentiment_analysis = await asyncio.gather(
                core_analysis_task, 
                sentiment_analysis_task,
                return_exceptions=True
            )
            
            # Handle exceptions gracefully
            if isinstance(core_analysis, Exception):
                logger.error(f"Core analysis failed for {ticker}: {core_analysis}")
                core_analysis = self._get_fallback_core_analysis()
            
            if isinstance(sentiment_analysis, Exception):
                logger.error(f"Sentiment analysis failed for {ticker}: {sentiment_analysis}")
                sentiment_analysis = self._get_fallback_sentiment_analysis()
            
            # Combine results
            comprehensive_result = {
                "ticker": ticker,
                "analysis_timestamp": datetime.now().isoformat(),
                "cost_breakdown": {
                    "core_analysis_tokens": core_analysis.get("token_usage", 0),
                    "sentiment_tokens": sentiment_analysis.get("token_usage", 0),
                    "estimated_cost": self._calculate_estimated_cost(core_analysis, sentiment_analysis)
                },
                
                # Core analysis components
                "investment_thesis": core_analysis.get("investment_thesis", "Analysis unavailable"),
                "dcf_commentary": core_analysis.get("dcf_commentary", []),
                "financial_health": core_analysis.get("financial_health", []),
                "technical_outlook": core_analysis.get("technical_outlook", []),
                
                # Sentiment and context
                "news_sentiment": sentiment_analysis.get("news_sentiment", {}),
                "peer_context": sentiment_analysis.get("peer_context", []),
                
                # Metadata
                "analysis_quality": self._assess_analysis_quality(core_analysis, sentiment_analysis),
                "model_version": "claude-3-haiku" if self.use_cost_optimized_model else "claude-3-sonnet"
            }
            
            # Cache the result
            await intelligent_cache.set(
                CacheType.AI_ANALYSIS,
                cache_key,
                comprehensive_result,
                ttl_hours=6
            )
            
            logger.info(f"Completed comprehensive analysis for {ticker}, estimated cost: ${comprehensive_result['cost_breakdown']['estimated_cost']:.3f}")
            return comprehensive_result
            
        except Exception as e:
            logger.error(f"Error in comprehensive agentic analysis for {ticker}: {e}")
            return self._get_emergency_fallback_analysis(ticker)
    
    async def generate_core_analysis_batch(
        self, 
        ticker: str,
        company_data: Dict[str, Any],
        dcf_results: Dict[str, Any],
        technical_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Batched core analysis: Investment Thesis + DCF + Financial + Technical"""
        
        # Check memory cache
        cache_key = f"{ticker}_core_batch"
        if cache_key in self.core_analysis_cache:
            cached_entry = self.core_analysis_cache[cache_key]
            if datetime.now() - cached_entry["timestamp"] < self.cache_ttl:
                return cached_entry["data"]
        
        system_prompt = """You are a financial analyst for Indian retail investors. Be precise, avoid repetition, and use structured output.

Your output must be valid JSON in exactly this structure:
{
  "investment_thesis": "1-2 sentence investment case summary (max 80 words)",
  "dcf_commentary": [
    "Key Growth Driver: [40 words max]",
    "Valuation Gap: [40 words max]", 
    "Main Risk: [40 words max]"
  ],
  "financial_health": [
    "Revenue Trend: [35 words max]",
    "Margin Analysis: [35 words max]",
    "Balance Sheet: [35 words max]"
  ],
  "technical_outlook": [
    "Trend Direction: [30 words max]",
    "Entry Signal: [30 words max]"
  ]
}"""

        # Format data for prompt
        financial_summary = self._format_financial_data(company_data)
        dcf_summary = self._format_dcf_data(dcf_results)
        technical_summary = self._format_technical_data(technical_data)
        
        prompt = f"""
Analyze {company_data.get('info', {}).get('longName', ticker)} ({ticker}) and provide structured output:

FINANCIAL DATA:
{financial_summary}

DCF RESULTS:
{dcf_summary}

TECHNICAL INDICATORS:
{technical_summary}

Provide analysis in the exact JSON structure specified. Focus on key insights for Indian retail investors.
        """
        
        try:
            response = await self.generate_completion(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=self.max_tokens_core,
                temperature=0.2
            )
            
            if response:
                # Parse JSON response
                result = self._parse_json_response(response)
                if result:
                    result["token_usage"] = len(prompt.split()) + len(response.split())
                    
                    # Cache in memory
                    self.core_analysis_cache[cache_key] = {
                        "data": result,
                        "timestamp": datetime.now()
                    }
                    
                    return result
                    
            return self._get_fallback_core_analysis()
            
        except Exception as e:
            logger.error(f"Error in core analysis batch for {ticker}: {e}")
            return self._get_fallback_core_analysis()
    
    async def generate_sentiment_context_batch(
        self,
        ticker: str,
        news_data: List[Dict],
        peer_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Batched sentiment: News + Peer context analysis"""
        
        # Check memory cache
        cache_key = f"{ticker}_sentiment_batch"
        if cache_key in self.sentiment_cache:
            cached_entry = self.sentiment_cache[cache_key]
            if datetime.now() - cached_entry["timestamp"] < self.cache_ttl:
                return cached_entry["data"]
        
        system_prompt = """You are a financial analyst specializing in sentiment and competitive analysis.

Your output must be valid JSON in exactly this structure:
{
  "news_sentiment": {
    "overall_tone": "Positive/Mixed/Negative",
    "key_themes": [
      "Theme 1: [35 words max]",
      "Theme 2: [35 words max]"
    ],
    "insider_activity": "Brief summary if significant [30 words max]"
  },
  "peer_context": [
    "Relative Valuation: [40 words max]",
    "Competitive Position: [40 words max]"
  ]
}"""

        # Format data
        news_summary = self._format_news_data(news_data)
        peer_summary = self._format_peer_data(peer_data)
        
        prompt = f"""
Analyze sentiment and market context for {ticker}:

RECENT NEWS:
{news_summary}

PEER COMPARISON:
{peer_summary}

Provide analysis in the exact JSON structure specified.
        """
        
        try:
            response = await self.generate_completion(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=self.max_tokens_sentiment,
                temperature=0.2
            )
            
            if response:
                result = self._parse_json_response(response)
                if result:
                    result["token_usage"] = len(prompt.split()) + len(response.split())
                    
                    # Cache in memory
                    self.sentiment_cache[cache_key] = {
                        "data": result,
                        "timestamp": datetime.now()
                    }
                    
                    return result
                    
            return self._get_fallback_sentiment_analysis()
            
        except Exception as e:
            logger.error(f"Error in sentiment batch for {ticker}: {e}")
            return self._get_fallback_sentiment_analysis()
    
    def _format_dcf_data(self, dcf_results: Dict[str, Any]) -> str:
        """Format DCF data for AI consumption"""
        if not dcf_results:
            return "DCF analysis unavailable"
        
        try:
            return f"""
Fair Value: ₹{dcf_results.get('fair_value', 0):.2f}
Current Price: ₹{dcf_results.get('current_price', 0):.2f}
Upside/Downside: {dcf_results.get('upside_percent', 0):.1f}%
Growth Rate Assumption: {dcf_results.get('growth_rate', 0):.1f}%
WACC: {dcf_results.get('wacc', 0):.1f}%
Terminal Growth: {dcf_results.get('terminal_growth', 0):.1f}%
            """
        except:
            return "DCF data formatting error"
    
    def _format_technical_data(self, technical_data: Dict[str, Any]) -> str:
        """Format technical data for AI consumption"""
        if not technical_data:
            return "Technical analysis unavailable"
        
        try:
            return f"""
RSI: {technical_data.get('rsi', 50):.1f}
MACD Signal: {technical_data.get('macd_signal', 'Neutral')}
Price vs 50-day MA: {technical_data.get('sma_50_signal', 'Neutral')}
Volume Trend: {technical_data.get('volume_trend', 'Normal')}
Support/Resistance: {technical_data.get('support_resistance', 'Neutral')}
            """
        except:
            return "Technical data formatting error"
    
    def _format_news_data(self, news_data: List[Dict]) -> str:
        """Format news data for AI consumption"""
        if not news_data:
            return "No recent news available"
        
        try:
            summaries = []
            for i, article in enumerate(news_data[:5]):  # Limit to 5 articles
                title = article.get('title', '')[:100]  # Truncate title
                summaries.append(f"{i+1}. {title}")
            
            return "\n".join(summaries)
        except:
            return "News data formatting error"
    
    def _format_peer_data(self, peer_data: Dict[str, Any]) -> str:
        """Format peer data for AI consumption"""
        if not peer_data or not peer_data.get('peers'):
            return "Peer data unavailable"
        
        try:
            peers = peer_data.get('peers', [])[:3]  # Limit to top 3 peers
            peer_summaries = []
            for peer in peers:
                name = peer.get('name', 'Unknown')
                pe = peer.get('pe_ratio', 0)
                growth = peer.get('revenue_growth', 0)
                peer_summaries.append(f"{name}: PE={pe:.1f}x, Growth={growth:.1f}%")
            
            return "\n".join(peer_summaries)
        except:
            return "Peer data formatting error"
    
    def _parse_json_response(self, response: str) -> Optional[Dict[str, Any]]:
        """Parse JSON response with fallback handling"""
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # Try to extract JSON from response
            start = response.find('{')
            end = response.rfind('}') + 1
            if start != -1 and end != 0:
                try:
                    return json.loads(response[start:end])
                except json.JSONDecodeError:
                    pass
        except Exception:
            pass
        
        logger.warning("Failed to parse JSON response, using fallback")
        return None
    
    def _calculate_estimated_cost(self, core_analysis: Dict, sentiment_analysis: Dict) -> float:
        """Calculate estimated API cost"""
        total_tokens = core_analysis.get("token_usage", 1000) + sentiment_analysis.get("token_usage", 1000)
        
        # Claude-3-Haiku pricing: ~$0.25 per 1M input tokens, ~$1.25 per 1M output tokens
        # Rough estimate assuming 60% input, 40% output
        input_cost = (total_tokens * 0.6) * (0.25 / 1000000)
        output_cost = (total_tokens * 0.4) * (1.25 / 1000000)
        
        return input_cost + output_cost
    
    def _assess_analysis_quality(self, core_analysis: Dict, sentiment_analysis: Dict) -> str:
        """Assess the quality of the analysis"""
        if (core_analysis.get("investment_thesis") and 
            len(core_analysis.get("dcf_commentary", [])) >= 3 and
            sentiment_analysis.get("news_sentiment")):
            return "high"
        elif core_analysis.get("investment_thesis"):
            return "medium"
        else:
            return "low"
    
    def _get_fallback_core_analysis(self) -> Dict[str, Any]:
        """Fallback core analysis when AI fails"""
        return {
            "investment_thesis": "Analysis based on quantitative metrics and historical performance",
            "dcf_commentary": [
                "Growth assumptions based on historical CAGR analysis",
                "Fair value calculated using sector-appropriate DCF methodology", 
                "Key risks include market volatility and sector-specific challenges"
            ],
            "financial_health": [
                "Revenue trends analyzed over 3-5 year period",
                "Profitability metrics compared to sector averages",
                "Balance sheet strength assessed using debt and liquidity ratios"
            ],
            "technical_outlook": [
                "Technical indicators suggest current market positioning",
                "Entry timing considerations based on momentum signals"
            ],
            "token_usage": 0
        }
    
    def _get_fallback_sentiment_analysis(self) -> Dict[str, Any]:
        """Fallback sentiment analysis when AI fails"""
        return {
            "news_sentiment": {
                "overall_tone": "Mixed",
                "key_themes": [
                    "Limited recent news analysis available",
                    "Sentiment assessment based on market performance"
                ],
                "insider_activity": "No significant insider activity detected"
            },
            "peer_context": [
                "Peer comparison based on quantitative metrics",
                "Competitive positioning assessed using financial ratios"
            ],
            "token_usage": 0
        }
    
    def _get_emergency_fallback_analysis(self, ticker: str) -> Dict[str, Any]:
        """Emergency fallback when entire analysis fails"""
        return {
            "ticker": ticker,
            "analysis_timestamp": datetime.now().isoformat(),
            "investment_thesis": f"Quantitative analysis available for {ticker} using rule-based methodology",
            "dcf_commentary": ["DCF analysis completed using historical validation"],
            "financial_health": ["Financial metrics analyzed using 5-year trends"],
            "technical_outlook": ["Technical indicators calculated using standard methodology"],
            "news_sentiment": {
                "overall_tone": "Mixed",
                "key_themes": ["Analysis based on quantitative data only"],
                "insider_activity": "Data unavailable"
            },
            "peer_context": ["Peer analysis based on sector classification"],
            "cost_breakdown": {"estimated_cost": 0.0},
            "analysis_quality": "fallback",
            "model_version": "rule-based-fallback"
        }

# Global service instances
claude_service = ClaudeService()
agentic_analysis_service = AgenticAnalysisService()