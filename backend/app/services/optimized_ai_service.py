import os
import logging
from typing import Dict, Any, Optional, List
import anthropic
from anthropic import Anthropic
import json
from datetime import datetime
from ..api.settings import get_user_api_keys

logger = logging.getLogger(__name__)

class OptimizedAIService:
    """
    Cost-optimized AI service implementing 2-agent architecture:
    1. Analysis Engine (8K tokens) - Consolidated financial analysis with AI insights
    2. DCF Validator (2K tokens) - Focused assumption validation and feedback
    
    Target: 50% cost reduction from 24K to 10K tokens per analysis
    """
    
    def __init__(self):
        self.client = None
        self._initialize_client()
        self._setup_industry_models()
        self._setup_templates()
    
    def _initialize_client(self):
        """Initialize Claude client with API key."""
        try:
            api_keys = get_user_api_keys()
            claude_api_key = api_keys.get('claude_api_key') or os.getenv('ANTHROPIC_API_KEY')
            
            if claude_api_key:
                self.client = Anthropic(api_key=claude_api_key)
                logger.info("Optimized Claude client initialized successfully")
            else:
                logger.warning("Claude API key not found - AI features will be disabled")
                
        except Exception as e:
            logger.error(f"Failed to initialize optimized Claude client: {e}")
            self.client = None
    
    def _setup_industry_models(self):
        """Set up industry-specific valuation model mappings."""
        self.industry_model_mapping = {
            'Banking': 'DDM',
            'Financial Services': 'DDM', 
            'Insurance': 'DDM',
            'REIT': 'Asset',
            'Real Estate': 'Asset',
            'Utilities': 'Asset',
            'Infrastructure': 'Asset',
            'Technology': 'DCF',
            'Healthcare': 'DCF',
            'Consumer Discretionary': 'DCF',
            'Consumer Staples': 'DCF',
            'Industrials': 'DCF',
            'Energy': 'DCF',
            'Materials': 'DCF',
            'Communications': 'DCF'
        }
        
        # Peer company references for benchmarking
        self.indian_peer_companies = {
            'Banking': ['HDFCBANK.NS', 'ICICIBANK.NS', 'KOTAKBANK.NS', 'SBIN.NS', 'AXISBANK.NS'],
            'Technology': ['TCS.NS', 'INFY.NS', 'HCLTECH.NS', 'WIPRO.NS', 'TECHM.NS'],
            'Energy': ['RELIANCE.NS', 'ONGC.NS', 'IOC.NS', 'BPCL.NS', 'NTPC.NS'],
            'Consumer': ['HINDUNILVR.NS', 'ITC.NS', 'NESTLEIND.NS', 'BRITANNIA.NS'],
            'Automotive': ['MARUTI.NS', 'TATAMOTORS.NS', 'M&M.NS', 'BAJAJ-AUTO.NS'],
            'Pharma': ['SUNPHARMA.NS', 'DRREDDY.NS', 'CIPLA.NS', 'DIVISLAB.NS']
        }
    
    def _setup_templates(self):
        """Set up templated content to reduce AI token usage."""
        self.dcf_education_template = """
**Understanding DCF Valuation:**
DCF (Discounted Cash Flow) calculates intrinsic value by projecting future cash flows and discounting them to present value.

**Key Assumptions:**
- Revenue Growth: How fast the company will grow sales
- EBITDA Margin: Operating efficiency (earnings before interest, tax, depreciation, amortization)
- Tax Rate: Corporate tax percentage applied to profits
- WACC: Weighted Average Cost of Capital (discount rate)
- Terminal Growth: Long-term growth rate after projection period

**Sensitivity Analysis:** Shows how valuation changes with different assumptions.
"""
        
        self.risk_factors_template = {
            'Technology': ['Rapid technological change', 'Competition from global players', 'Talent retention'],
            'Banking': ['Interest rate changes', 'Credit risk', 'Regulatory changes', 'Economic cycles'],
            'Energy': ['Oil price volatility', 'Environmental regulations', 'Renewable energy shift'],
            'Consumer': ['Changing consumer preferences', 'Input cost inflation', 'Distribution challenges'],
            'Healthcare': ['Regulatory approvals', 'Patent expiry', 'Pricing pressures']
        }
    
    def _get_industry_context(self, sector: str, ticker: str) -> Dict[str, Any]:
        """Get industry-specific context and peer companies."""
        recommended_model = self.industry_model_mapping.get(sector, 'DCF')
        
        # Find peer companies
        peers = []
        for industry, companies in self.indian_peer_companies.items():
            if ticker in companies:
                peers = [c for c in companies if c != ticker][:4]
                break
        
        # Get industry-specific risks
        risk_category = self._map_sector_to_risk_category(sector)
        common_risks = self.risk_factors_template.get(risk_category, ['Market volatility', 'Economic cycles'])
        
        return {
            'recommended_model': recommended_model,
            'model_rationale': self._get_model_rationale(recommended_model, sector),
            'peer_companies': peers,
            'common_industry_risks': common_risks,
            'is_indian_stock': ticker.endswith('.NS')
        }
    
    def _map_sector_to_risk_category(self, sector: str) -> str:
        """Map sector to risk category for templated risks."""
        mapping = {
            'Technology': 'Technology',
            'Financial Services': 'Banking',
            'Banking': 'Banking',
            'Energy': 'Energy',
            'Consumer Discretionary': 'Consumer',
            'Consumer Staples': 'Consumer',
            'Healthcare': 'Healthcare'
        }
        return mapping.get(sector, 'Technology')
    
    def _get_model_rationale(self, model: str, sector: str) -> str:
        """Get rationale for recommended valuation model."""
        rationales = {
            'DCF': f"{sector} companies typically have predictable cash flows suitable for DCF analysis",
            'DDM': f"{sector} companies are dividend-focused with regulated earnings, making DDM more appropriate",
            'Asset': f"{sector} companies have substantial tangible assets, making asset-based valuation relevant"
        }
        return rationales.get(model, "Standard DCF approach for this industry")
    
    def is_available(self) -> bool:
        """Check if optimized AI service is available."""
        return self.client is not None
    
    async def generate_completion(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 4000,
        temperature: float = 0.3,
        model: str = "claude-3-5-sonnet-20241022"
    ) -> Optional[str]:
        """Generate AI completion with error handling."""
        if not self.client:
            logger.error("Claude client not initialized")
            return None
        
        try:
            messages = [{"role": "user", "content": prompt}]
            
            response = self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt or "You are a specialized financial AI assistant.",
                messages=messages
            )
            
            if response.content and len(response.content) > 0:
                return response.content[0].text
            else:
                logger.error("Empty response from Claude")
                return None
                
        except Exception as e:
            logger.error(f"Error generating optimized AI completion: {e}")
            return None
    
    async def analysis_engine_agent(
        self,
        company_data: Dict[str, Any],
        news_articles: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """
        Analysis Engine Agent - Consolidated financial analysis (8K tokens target).
        
        Combines insights from financial data, news sentiment, and peer comparison
        into focused, actionable analysis with templated education content.
        """
        if not self.client:
            return None
        
        info = company_data.get('info', {})
        ticker = company_data.get('ticker', '')
        sector = info.get('sector', 'Technology')
        
        # Get industry context
        industry_context = self._get_industry_context(sector, ticker)
        
        system_prompt = """You are an expert financial analyst focused on generating actionable insights efficiently. 

Your output must be valid JSON in exactly this structure:
{
  "company_overview": {
    "investment_thesis": "2-3 sentence summary of why this is/isn't a good investment",
    "key_strengths": ["Strength 1", "Strength 2", "Strength 3"],
    "key_risks": ["Risk 1", "Risk 2", "Risk 3"],
    "competitive_position": "Brief assessment vs peers"
  },
  "news_insights": {
    "sentiment_score": 0.65,
    "key_developments": [
      {
        "headline": "Brief headline",
        "impact": "positive|negative|neutral",
        "significance": "high|medium|low"
      }
    ],
    "market_sentiment": "Brief sentiment summary"
  },
  "financial_health": {
    "profitability_score": "strong|moderate|weak",
    "liquidity_score": "strong|moderate|weak", 
    "growth_trajectory": "accelerating|stable|declining",
    "key_metrics_analysis": "Brief analysis of important ratios"
  },
  "dcf_assumptions": {
    "revenue_growth_rate": 8.5,
    "ebitda_margin": 15.2,
    "tax_rate": 25.0,
    "wacc": 10.5,
    "terminal_growth_rate": 3.0,
    "rationale": {
      "revenue_growth_rate": "Based on historical performance and industry outlook",
      "ebitda_margin": "Conservative estimate based on operational efficiency",
      "wacc": "Industry average adjusted for company-specific risk",
      "terminal_growth_rate": "Long-term GDP growth assumption"
    }
  },
  "ai_insights": {
    "price_momentum": "Brief technical view",
    "analyst_consensus": "Brief consensus summary if available",
    "unique_value_drivers": ["Driver 1", "Driver 2"],
    "red_flags": ["Warning 1", "Warning 2"] 
  }
}

CRITICAL: Keep insights specific and actionable. Focus on what makes this company unique rather than generic analysis."""
        
        # Format news efficiently
        if news_articles:
            news_summary = "\n".join([
                f"• {article['title'][:100]}..." 
                for article in news_articles[:5]
            ])
        else:
            news_summary = "Limited recent news available"
        
        # Financial data summary
        financial_summary = self._format_financial_summary(company_data)
        
        prompt = f"""
Analyze {info.get('longName', ticker)} ({ticker}) efficiently:

COMPANY: {sector} sector, Market Cap: ${info.get('marketCap', 0):,.0f}

PEER CONTEXT: Compare against {', '.join(industry_context['peer_companies'][:3])}

FINANCIAL SNAPSHOT:
{financial_summary}

RECENT NEWS (Last 30 days):
{news_summary}

FOCUS AREAS:
1. Generate realistic DCF assumptions based on historical data
2. Identify 2-3 key investment drivers unique to this company
3. Assess competitive position vs peers mentioned above
4. Extract actionable insights from recent news
5. Flag any red flags or unusual metrics

EFFICIENCY REQUIREMENTS:
- Focus on company-specific insights, not generic industry analysis
- Prioritize recent developments and unique competitive advantages
- Provide specific, quantified assessments where possible
"""
        
        try:
            response = await self.generate_completion(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=8000,  # Target 8K tokens
                temperature=0.2
            )
            
            if response:
                # Parse JSON response
                import re
                cleaned_response = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', response)
                
                try:
                    parsed_result = json.loads(cleaned_response)
                    
                    # Add templated education content to reduce AI token usage
                    parsed_result['education_content'] = {
                        'dcf_explanation': self.dcf_education_template,
                        'industry_context': {
                            'recommended_model': industry_context['recommended_model'],
                            'model_rationale': industry_context['model_rationale'],
                            'common_risks': industry_context['common_industry_risks']
                        }
                    }
                    
                    return parsed_result
                    
                except json.JSONDecodeError as e:
                    logger.error(f"JSON parsing error in Analysis Engine: {e}")
                    # Try to extract JSON object
                    start = cleaned_response.find('{')
                    if start != -1:
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
                            try:
                                return json.loads(cleaned_response[start:end])
                            except json.JSONDecodeError:
                                pass
                    
                    logger.error("Could not parse Analysis Engine response")
                    return None
            
            return None
            
        except Exception as e:
            logger.error(f"Error in analysis_engine_agent: {e}")
            return None
    
    async def dcf_validator_agent(
        self,
        analysis_output: Dict[str, Any],
        company_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        DCF Validator Agent - Focused assumption validation (2K tokens target).
        
        Validates DCF assumptions against peers and provides specific feedback
        on assumption reasonableness with actionable insights.
        """
        if not self.client:
            return None
        
        system_prompt = """You are a DCF valuation specialist focused on assumption validation.

Your output must be valid JSON in exactly this structure:
{
  "validation_summary": {
    "overall_assessment": "conservative|reasonable|aggressive",
    "confidence_level": "high|medium|low",
    "key_concerns": ["Concern 1", "Concern 2"],
    "strengths": ["Strength 1", "Strength 2"]
  },
  "assumption_feedback": {
    "revenue_growth_rate": {
      "assessment": "reasonable|too_high|too_low",
      "peer_comparison": "vs industry average of X%",
      "suggestion": "Specific actionable feedback",
      "confidence": "high|medium|low"
    },
    "ebitda_margin": {
      "assessment": "reasonable|too_high|too_low", 
      "peer_comparison": "vs industry average of X%",
      "suggestion": "Specific actionable feedback",
      "confidence": "high|medium|low"
    },
    "wacc": {
      "assessment": "reasonable|too_high|too_low",
      "peer_comparison": "vs industry average of X%", 
      "suggestion": "Specific actionable feedback",
      "confidence": "high|medium|low"
    }
  },
  "sensitivity_insights": {
    "most_sensitive_assumption": "revenue_growth_rate|ebitda_margin|wacc|terminal_growth_rate",
    "downside_scenario": "Brief description of key downside risks",
    "upside_scenario": "Brief description of key upside potential",
    "recommended_ranges": {
      "revenue_growth_low": 5.0,
      "revenue_growth_high": 12.0,
      "wacc_low": 9.0,
      "wacc_high": 12.0
    }
  }
}

Be specific and actionable in your feedback."""
        
        # Extract DCF assumptions
        dcf_assumptions = analysis_output.get('dcf_assumptions', {})
        info = company_data.get('info', {})
        
        # Historical context
        historical_growth = self._calculate_historical_growth(company_data)
        industry_multiples = self._get_industry_multiples(info.get('sector', 'Technology'))
        
        prompt = f"""
Validate DCF assumptions for {info.get('longName', 'Unknown')}:

PROPOSED ASSUMPTIONS:
Revenue Growth: {dcf_assumptions.get('revenue_growth_rate', 0)}%
EBITDA Margin: {dcf_assumptions.get('ebitda_margin', 0)}%
WACC: {dcf_assumptions.get('wacc', 0)}%
Terminal Growth: {dcf_assumptions.get('terminal_growth_rate', 0)}%

CONTEXT:
Historical Revenue Growth: {historical_growth}%
Industry: {info.get('sector', 'Technology')}
Current P/E: {info.get('trailingPE', 'N/A')}
Industry Average P/E: {industry_multiples.get('pe_ratio', 'N/A')}

VALIDATION TASKS:
1. Compare assumptions against historical performance
2. Benchmark against industry averages
3. Identify the most sensitive assumption for valuation
4. Suggest realistic ranges for sensitivity analysis
5. Highlight any red flags or aggressive assumptions

Focus on specific, actionable feedback rather than generic validation.
"""
        
        try:
            response = await self.generate_completion(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=2000,  # Target 2K tokens
                temperature=0.1
            )
            
            if response:
                try:
                    return json.loads(response)
                except json.JSONDecodeError:
                    # Try to extract JSON
                    start = response.find('{')
                    end = response.rfind('}') + 1
                    if start != -1 and end != 0:
                        try:
                            return json.loads(response[start:end])
                        except json.JSONDecodeError:
                            pass
                    
                    logger.error("Could not parse DCF Validator response")
                    return None
            
            return None
            
        except Exception as e:
            logger.error(f"Error in dcf_validator_agent: {e}")
            return None
    
    def _format_financial_summary(self, company_data: Dict[str, Any]) -> str:
        """Create concise financial summary for AI consumption."""
        info = company_data.get('info', {})
        
        def safe_format(value, default='N/A', is_percentage=False):
            if value is None or (isinstance(value, float) and (value != value or abs(value) == float('inf'))):
                return default
            if is_percentage:
                return f"{value:.1f}%"
            return f"{value:,.0f}" if isinstance(value, (int, float)) else str(value)
        
        return f"""Revenue: ${safe_format(info.get('totalRevenue'))}, EBITDA: ${safe_format(info.get('ebitda'))}
Profit Margin: {safe_format(info.get('profitMargins'), is_percentage=True)}, ROE: {safe_format(info.get('returnOnEquity'), is_percentage=True)}
P/E: {safe_format(info.get('trailingPE'))}, P/B: {safe_format(info.get('priceToBook'))}
Debt/Equity: {safe_format(info.get('debtToEquity'))}, Current Ratio: {safe_format(info.get('currentRatio'))}"""
    
    def _calculate_historical_growth(self, company_data: Dict[str, Any]) -> float:
        """Calculate historical revenue growth if available."""
        try:
            financials = company_data.get('financials', {})
            if not financials:
                return 0.0
            
            # Simple calculation - would be enhanced with actual historical data
            return 8.0  # Placeholder
        except:
            return 0.0
    
    def _get_industry_multiples(self, sector: str) -> Dict[str, float]:
        """Get industry average multiples."""
        # Simplified industry multiples - would be enhanced with real data
        industry_multiples = {
            'Technology': {'pe_ratio': 25.0, 'pb_ratio': 3.5},
            'Banking': {'pe_ratio': 12.0, 'pb_ratio': 1.2},
            'Energy': {'pe_ratio': 15.0, 'pb_ratio': 1.8},
            'Consumer': {'pe_ratio': 20.0, 'pb_ratio': 2.5}
        }
        
        return industry_multiples.get(sector, {'pe_ratio': 20.0, 'pb_ratio': 2.0})

# Global service instance
optimized_ai_service = OptimizedAIService()