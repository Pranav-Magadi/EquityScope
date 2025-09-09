"""
DCF AI Insights Service
Provides AI-powered analysis and insights for DCF valuation results
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from .claude_service import ClaudeService
from .intelligent_cache import intelligent_cache, CacheType

logger = logging.getLogger(__name__)


class DCFAIInsightsService:
    """Service for generating AI insights about DCF valuations"""
    
    def __init__(self):
        self.claude_service = None
    
    async def generate_dcf_insights(
        self,
        ticker: str,
        dcf_result: Dict[str, Any],
        assumptions: Dict[str, Any],
        company_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate comprehensive AI insights for DCF valuation results
        
        Args:
            ticker: Stock ticker symbol
            dcf_result: DCF calculation results (fair value, upside, etc.)
            assumptions: DCF assumptions used (WACC, growth rates, etc.)
            company_data: Company financial and sector data
            
        Returns:
            Dictionary containing AI insights with 6 hour caching
        """
        
        try:
            # Debug logging
            logger.info(f"🔍 DCF AI Insights Debug - Ticker: {ticker}")
            logger.info(f"🔍 DCF AI Insights Debug - DCF Result: {dcf_result}")
            logger.info(f"🔍 DCF AI Insights Debug - Assumptions: {assumptions}")
            logger.info(f"🔍 DCF AI Insights Debug - Company Data: {company_data}")
            
            # Check cache first (6 hour TTL from intelligent_cache.py)
            cache_key = f"dcf_insights_{ticker}_{hash(str(dcf_result))}"
            cached_insights = await intelligent_cache.get(
                cache_type=CacheType.AI_INSIGHTS,
                identifier=ticker,
                dcf_hash=cache_key,
                fair_value=dcf_result.get('fairValue', 0)
            )
            
            if cached_insights:
                logger.info(f"Using cached DCF insights for {ticker}")
                return cached_insights
            
            # Generate fresh AI insights
            logger.info(f"Generating fresh DCF AI insights for {ticker}")
            
            # Prepare structured prompt for Claude
            prompt = self._create_dcf_analysis_prompt(
                ticker=ticker,
                dcf_result=dcf_result,
                assumptions=assumptions,
                company_data=company_data
            )
            
            # Initialize or reinitialize Claude service to get latest API keys
            self.claude_service = ClaudeService()
            
            # Check if Claude service is available first
            if not self.claude_service.is_available():
                logger.warning(f"Claude service not available for {ticker} - no API key configured")
                return self._get_api_error_response(ticker, "no_api_key")
            
            # Call Claude for analysis using existing generate_completion method with timeout
            logger.info(f"🔍 Calling Claude API for {ticker}...")
            
            # Add timeout wrapper to prevent hanging
            import asyncio
            try:
                ai_response = await asyncio.wait_for(
                    self.claude_service.generate_completion(
                        prompt=prompt,
                        max_tokens=1200,  # Reduced for faster response
                        model="claude-3-haiku-20240307"  # Cost-effective for insights
                    ),
                    timeout=20.0  # 20 second timeout
                )
            except asyncio.TimeoutError:
                logger.warning(f"Claude API timeout for {ticker} - using fallback")
                return self._get_api_error_response(ticker, "api_timeout")
            
            logger.info(f"🔍 Claude Response for {ticker}: {ai_response[:200] if ai_response else 'None'}...")
            
            # If Claude didn't return a response, likely an API issue
            if not ai_response:
                logger.warning(f"Empty Claude response for {ticker} - API credits/key issue")
                return self._get_api_error_response(ticker, "api_error")
            
            # Parse and structure the response
            insights = self._parse_dcf_insights(ai_response, dcf_result, assumptions)
            logger.info(f"🔍 Parsed Insights for {ticker}: {insights}")
            
            # Cache the results for 6 hours
            await intelligent_cache.set(
                cache_type=CacheType.AI_INSIGHTS,
                identifier=ticker,
                data=insights,
                dcf_hash=cache_key,
                fair_value=dcf_result.get('fairValue', 0)
            )
            
            logger.info(f"Successfully generated and cached DCF insights for {ticker}")
            return insights
            
        except Exception as e:
            logger.error(f"Error generating DCF insights for {ticker}: {e}")
            return self._get_api_error_response(ticker, "service_error")
    
    def _create_dcf_analysis_prompt(
        self,
        ticker: str,
        dcf_result: Dict[str, Any],
        assumptions: Dict[str, Any],
        company_data: Dict[str, Any]
    ) -> str:
        """Create structured prompt for DCF analysis using specified format"""
        
        fair_value = dcf_result.get('fairValue', 0)
        current_price = dcf_result.get('currentPrice', 0)
        upside = dcf_result.get('upside', 0)
        wacc = assumptions.get('wacc', 'N/A')
        growth_rate = assumptions.get('revenue_growth_rate', 'N/A')
        terminal_growth = assumptions.get('terminal_growth_rate', 'N/A')
        
        company_name = company_data.get('name', ticker)
        sector = company_data.get('sector', 'Unknown')
        market_cap = company_data.get('market_cap', 'Unknown')
        
        # Calculate additional metrics for comprehensive analysis
        roce = assumptions.get('roce', 'N/A')
        cagr = assumptions.get('cagr', growth_rate)
        
        return f"""
You are an expert equity analyst. Provide concise DCF analysis for {company_name} ({ticker}):

**DATA:** {company_name} | Sector: {sector} | Price: ₹{current_price:.0f} | Fair Value: ₹{fair_value:.0f} | Upside: {upside:.1f}%
**ASSUMPTIONS:** WACC {wacc}%, Growth {growth_rate}%, Terminal {terminal_growth}%

**Return JSON only:**
{{
  "investment_thesis_summary": "2-sentence summary of valuation view and key growth drivers",
  "industry_macro_signals": "Brief sector/macro insights affecting valuation",
  "ai_diagnostic_commentary": "Quick assessment of assumptions with revised fair value if needed",
  "smart_risk_flags": ["Key risk 1", "Key risk 2"],
  "revised_fair_value": "₹XXXX (conservative scenario)",
  "key_catalysts": ["Catalyst 1", "Catalyst 2"]
}}

Be concise, specific to {sector}, use ₹ for Indian stocks.
"""
    
    def _parse_dcf_insights(self, ai_response: str, dcf_result: Dict[str, Any], assumptions: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Claude's response into structured insights"""
        
        try:
            # Parse JSON response from Claude
            import json
            
            if not ai_response:
                logger.warning("Empty AI response received")
                return self._get_fallback_insights(dcf_result, assumptions)
            
            # Try to extract JSON from response
            response_text = ai_response.strip()
            
            # Look for JSON block in response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_text = response_text[json_start:json_end]
                analysis = json.loads(json_text)
            else:
                # Fallback: try to parse the whole response as JSON
                analysis = json.loads(response_text)
            
            return {
                'investment_thesis_summary': analysis.get('investment_thesis_summary', 'Trading at current levels with mixed valuation signals. Sector positioning and growth assumptions require monitoring. Fair value assessment pending detailed analysis.'),
                'industry_macro_signals': analysis.get('industry_macro_signals', 'Industry trends and macro conditions present balanced outlook with sector-specific considerations.'),
                'ai_diagnostic_commentary': analysis.get('ai_diagnostic_commentary', 'DCF assumptions appear within reasonable ranges. Conservative scenario analysis recommended for enhanced accuracy.'),
                'smart_risk_flags': analysis.get('smart_risk_flags', [
                    'Market volatility may impact model assumptions',
                    'Regulatory changes could affect projected cash flows'
                ]),
                'revised_fair_value': analysis.get('revised_fair_value', 'Conservative scenario analysis pending'),
                'key_catalysts': analysis.get('key_catalysts', [
                    'Sector performance improvements',
                    'Execution of strategic initiatives'
                ]),
                'confidence_score': analysis.get('confidence_score', 0.7),
                'generated_at': datetime.now().isoformat(),
                'model_used': 'claude-3-haiku-20240307',
                'token_usage': {'tokens': len(response_text.split()) if response_text else 0, 'cost': 0.0}
            }
            
        except Exception as e:
            logger.error(f"Error parsing DCF insights: {e}")
            logger.error(f"AI response content: {ai_response[:200] if ai_response else 'None'}...")
            return self._get_fallback_insights(dcf_result, assumptions)
    
    def _get_fallback_insights(
        self, 
        dcf_result: Dict[str, Any], 
        assumptions: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Provide fallback insights when AI analysis fails"""
        
        fair_value = dcf_result.get('fairValue', 0)
        current_price = dcf_result.get('currentPrice', 0)
        upside = dcf_result.get('upside', 0)
        method = dcf_result.get('method', 'DCF')
        confidence = dcf_result.get('confidence', 0.5)
        wacc = assumptions.get('wacc', 'N/A')
        growth_rate = assumptions.get('revenue_growth_rate', 'N/A')
        
        return {
            'investment_thesis_summary': f'Trading {"above" if upside < 0 else "below"} fair value of ₹{fair_value:.0f} with {abs(upside):.1f}% {"downside" if upside < 0 else "upside"} potential. DCF methodology using {wacc}% WACC and {growth_rate}% growth suggests {"cautious" if upside < 5 else "moderate" if upside < 15 else "attractive"} risk-reward profile.',
            'industry_macro_signals': f'Current valuation reflects sector-appropriate assumptions with {method} methodology. Market conditions and {"discount rate of " + str(wacc) + "%" if wacc != "N/A" else "standard assumptions"} factor in prevailing macro environment.',
            'ai_diagnostic_commentary': f'DCF assumptions appear reasonable with WACC of {wacc}% and growth rate of {growth_rate}%. {"Conservative approach recommended" if confidence < 0.6 else "Moderate confidence in projections"}. Consider sensitivity analysis for key variables.',
            'smart_risk_flags': [
                f'WACC sensitivity: ±100bps could impact fair value by 8-12%',
                f'Growth assumptions may face headwinds from sector cyclicality'
            ],
            'revised_fair_value': f'Base case ₹{fair_value:.0f} (conservative scenario analysis pending)',
            'key_catalysts': [
                'Execution of strategic initiatives',
                'Sector performance improvements'
            ],
            'confidence_score': confidence,
            'generated_at': datetime.now().isoformat(),
            'model_used': 'fallback_sophisticated',
            'token_usage': {'tokens': 0, 'cost': 0.0}
        }
    
    def _get_api_error_response(self, ticker: str, error_type: str) -> Dict[str, Any]:
        """Provide error response when API keys are missing/invalid"""
        
        error_messages = {
            "no_api_key": "API key required for AI insights. Please configure Claude or Perplexity API key in Settings.",
            "api_error": "API credits exhausted or invalid key. Please check your API key settings.",
            "service_error": "AI service temporarily unavailable. Please try again later.",
            "api_timeout": "AI analysis timed out. Please try again or check API service status."
        }
        
        return {
            'error': True,
            'error_type': error_type,
            'error_message': error_messages.get(error_type, "Unknown API error occurred"),
            'ticker': ticker,
            'investment_thesis_summary': f'AI insights unavailable - {error_messages.get(error_type, "API error")}',
            'industry_macro_signals': 'Configure API key in Settings to enable AI-powered analysis',
            'ai_diagnostic_commentary': 'Real-time AI insights require valid API key configuration',
            'smart_risk_flags': [
                'API configuration required for enhanced insights',
                'Using quantitative analysis only until AI service is configured'
            ],
            'revised_fair_value': 'API key required for revised analysis',
            'key_catalysts': [
                'Configure AI API key to unlock detailed catalysts',
                'Enable enhanced analysis in Settings'
            ],
            'confidence_score': 0.0,
            'generated_at': datetime.now().isoformat(),
            'model_used': f'error_{error_type}',
            'token_usage': {'tokens': 0, 'cost': 0.0},
            'requires_api_key': True
        }


# Global service instance
dcf_ai_insights_service = DCFAIInsightsService()