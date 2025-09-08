import logging
from typing import Dict, Any, List, Optional
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)

class UserExperienceLevel(Enum):
    """User experience levels for progressive disclosure."""
    BEGINNER = "beginner"       # New to investing, needs basic explanations
    INTERMEDIATE = "intermediate" # Some investing knowledge, wants context
    ADVANCED = "advanced"       # Experienced, wants detailed analysis

class DisclosureSection(Enum):
    """Different sections that can be progressively disclosed."""
    EXECUTIVE_SUMMARY = "executive_summary"
    VALUATION_DETAILS = "valuation_details"
    MODEL_EXPLANATION = "model_explanation"
    ASSUMPTIONS_BREAKDOWN = "assumptions_breakdown"
    RISK_ANALYSIS = "risk_analysis"
    INDUSTRY_CONTEXT = "industry_context"
    TECHNICAL_DETAILS = "technical_details"

class ProgressiveDisclosureService:
    """
    Progressive disclosure service for EquityScope user education.
    
    Breaks down complex financial analysis into digestible layers based on
    user experience level and engagement patterns.
    
    Architecture:
    - Level 1 (Always Visible): Key insights and actionable recommendations
    - Level 2 (Expandable): Context and reasoning behind recommendations  
    - Level 3 (Advanced): Technical details and methodology
    - Level 4 (Expert): Raw data and calculation details
    """
    
    def __init__(self):
        self._setup_disclosure_templates()
    
    def _setup_disclosure_templates(self):
        """Set up templates for different disclosure levels."""
        
        # Templates for different user experience levels
        self.experience_templates = {
            UserExperienceLevel.BEGINNER: {
                'language_style': 'simple',
                'jargon_level': 'minimal',
                'explanation_depth': 'basic',
                'show_formulas': False,
                'default_expanded_sections': [DisclosureSection.EXECUTIVE_SUMMARY]
            },
            UserExperienceLevel.INTERMEDIATE: {
                'language_style': 'conversational',
                'jargon_level': 'moderate',
                'explanation_depth': 'detailed',
                'show_formulas': False,
                'default_expanded_sections': [
                    DisclosureSection.EXECUTIVE_SUMMARY,
                    DisclosureSection.VALUATION_DETAILS
                ]
            },
            UserExperienceLevel.ADVANCED: {
                'language_style': 'professional',
                'jargon_level': 'full',
                'explanation_depth': 'comprehensive',
                'show_formulas': True,
                'default_expanded_sections': [
                    DisclosureSection.EXECUTIVE_SUMMARY,
                    DisclosureSection.VALUATION_DETAILS,
                    DisclosureSection.MODEL_EXPLANATION
                ]
            }
        }
    
    def generate_progressive_disclosure(
        self,
        analysis_result: Dict[str, Any],
        user_level: UserExperienceLevel = UserExperienceLevel.INTERMEDIATE,
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate progressive disclosure structure for financial analysis.
        
        Args:
            analysis_result: Complete analysis result from optimized workflow
            user_level: User's experience level
            user_preferences: User-specific preferences and settings
            
        Returns:
            Structured progressive disclosure with expandable sections
        """
        
        try:
            template = self.experience_templates[user_level]
            
            # Extract key data from analysis result
            ticker = analysis_result.get('metadata', {}).get('ticker', 'UNKNOWN')
            company_name = analysis_result.get('metadata', {}).get('company_name', ticker)
            
            # Build progressive disclosure structure
            disclosure = {
                'user_context': {
                    'experience_level': user_level.value,
                    'company': company_name,
                    'ticker': ticker,
                    'analysis_timestamp': analysis_result.get('metadata', {}).get('analysis_timestamp'),
                    'personalization': self._get_personalization_settings(user_level, user_preferences)
                },
                'disclosure_layers': self._build_disclosure_layers(analysis_result, template),
                'interactive_elements': self._generate_interactive_elements(analysis_result, user_level),
                'learning_opportunities': self._identify_learning_opportunities(analysis_result, user_level)
            }
            
            return disclosure
            
        except Exception as e:
            logger.error(f"Error generating progressive disclosure: {e}")
            return self._generate_fallback_disclosure(analysis_result)
    
    def _build_disclosure_layers(
        self, 
        analysis_result: Dict[str, Any], 
        template: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build the layered disclosure structure."""
        
        layers = {}
        
        # Layer 1: Executive Summary (Always visible)
        layers['level_1_summary'] = self._build_executive_summary(analysis_result, template)
        
        # Layer 2: Valuation Context (Expandable)
        layers['level_2_valuation'] = self._build_valuation_context(analysis_result, template)
        
        # Layer 3: Model Explanation (Advanced expandable)
        layers['level_3_methodology'] = self._build_methodology_explanation(analysis_result, template)
        
        # Layer 4: Technical Details (Expert level)
        layers['level_4_technical'] = self._build_technical_details(analysis_result, template)
        
        return layers
    
    def _build_executive_summary(
        self, 
        analysis_result: Dict[str, Any], 
        template: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build Level 1: Executive Summary - Always visible, actionable insights."""
        
        # Extract key insights
        enhanced_insights = analysis_result.get('enhanced_insights', {})
        user_guidance = analysis_result.get('user_guidance', {})
        multi_model = analysis_result.get('multi_model_analysis', {})
        
        # Get recommendation and confidence
        action_guidance = enhanced_insights.get('action_guidance', {})
        recommended_action = action_guidance.get('recommended_action', 'Additional research recommended')
        confidence = action_guidance.get('confidence_indicator', 'medium')
        
        # Build language appropriate for user level
        language_style = template['language_style']
        
        summary = {
            'section_id': 'executive_summary',
            'title': 'Investment Summary',
            'always_visible': True,
            'content': {
                'headline_recommendation': {
                    'action': recommended_action,
                    'confidence_level': confidence,
                    'color_indicator': action_guidance.get('color_code', 'yellow'),
                    'explanation': self._format_recommendation_explanation(
                        recommended_action, confidence, language_style
                    )
                },
                'key_points': self._extract_key_points(enhanced_insights, language_style),
                'quick_stats': self._generate_quick_stats(analysis_result, template),
                'next_steps': user_guidance.get('next_steps', {}).get('immediate_actions', [])[:2]
            },
            'expand_options': {
                'learn_more_about': [
                    'Why this recommendation?',
                    'What valuation model was used?',
                    'What are the key risks?'
                ]
            }
        }
        
        return summary
    
    def _build_valuation_context(
        self, 
        analysis_result: Dict[str, Any], 
        template: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build Level 2: Valuation Context - Why the recommendation makes sense."""
        
        multi_model = analysis_result.get('multi_model_analysis', {})
        enhanced_insights = analysis_result.get('enhanced_insights', {})
        
        # Get valuation model information
        model_recommendation = multi_model.get('model_recommendation', {})
        recommended_model = model_recommendation.get('recommended_model', {})
        
        context = {
            'section_id': 'valuation_context',
            'title': 'Understanding the Valuation',
            'default_expanded': DisclosureSection.VALUATION_DETAILS in template['default_expanded_sections'],
            'content': {
                'valuation_approach': {
                    'model_used': recommended_model.get('model', 'DCF'),
                    'why_this_model': self._explain_model_choice(recommended_model, template),
                    'confidence_in_model': recommended_model.get('confidence_score', 0.7)
                },
                'valuation_range': self._explain_valuation_range(multi_model, template),
                'peer_comparison': self._generate_peer_context(analysis_result, template),
                'key_assumptions': self._explain_key_assumptions(analysis_result, template)
            },
            'educational_content': {
                'what_is_valuation': self._get_valuation_education(template),
                'model_comparison': self._get_model_comparison_education(multi_model, template)
            }
        }
        
        return context
    
    def _build_methodology_explanation(
        self, 
        analysis_result: Dict[str, Any], 
        template: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build Level 3: Methodology - How the analysis was conducted."""
        
        methodology = {
            'section_id': 'methodology_explanation',
            'title': 'Analysis Methodology',
            'default_expanded': DisclosureSection.MODEL_EXPLANATION in template['default_expanded_sections'],
            'content': {
                'analysis_process': self._explain_analysis_process(analysis_result, template),
                'data_sources': self._explain_data_sources(analysis_result, template),
                'ai_enhancement': self._explain_ai_role(analysis_result, template),
                'quality_checks': self._explain_validation_process(analysis_result, template)
            },
            'formulas_and_calculations': self._get_formulas(analysis_result, template) if template['show_formulas'] else {},
            'limitations_and_assumptions': self._explain_limitations(analysis_result, template)
        }
        
        return methodology
    
    def _build_technical_details(
        self, 
        analysis_result: Dict[str, Any], 
        template: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build Level 4: Technical Details - Raw data and calculations."""
        
        technical = {
            'section_id': 'technical_details',
            'title': 'Technical Analysis Details',
            'default_expanded': False,  # Expert level only
            'expert_only': True,
            'content': {
                'raw_assumptions': analysis_result.get('dcf_validation_output', {}),
                'calculation_breakdown': self._get_calculation_breakdown(analysis_result),
                'sensitivity_analysis': self._get_sensitivity_data(analysis_result),
                'model_parameters': self._get_model_parameters(analysis_result),
                'data_quality_metrics': self._get_data_quality_info(analysis_result)
            },
            'downloadable_data': {
                'excel_model': f"/api/v2/export/{analysis_result.get('metadata', {}).get('ticker')}/excel",
                'raw_json': f"/api/v2/export/{analysis_result.get('metadata', {}).get('ticker')}/json"
            }
        }
        
        return technical
    
    def _generate_interactive_elements(
        self,
        analysis_result: Dict[str, Any],
        user_level: UserExperienceLevel
    ) -> Dict[str, Any]:
        """Generate interactive elements for user engagement."""
        
        interactive = {
            'assumption_sliders': self._generate_assumption_sliders(analysis_result, user_level),
            'scenario_analysis': self._generate_scenario_buttons(analysis_result, user_level),
            'comparison_tools': self._generate_comparison_options(analysis_result, user_level),
            'learning_modules': self._generate_learning_modules(analysis_result, user_level)
        }
        
        return interactive
    
    def _identify_learning_opportunities(
        self,
        analysis_result: Dict[str, Any],
        user_level: UserExperienceLevel
    ) -> List[Dict[str, Any]]:
        """Identify contextual learning opportunities."""
        
        opportunities = []
        
        # Based on the analysis, suggest relevant learning topics
        multi_model = analysis_result.get('multi_model_analysis', {})
        recommended_model = multi_model.get('model_recommendation', {}).get('recommended_model', {})
        
        if recommended_model.get('model') == 'DDM':
            opportunities.append({
                'topic': 'Understanding Banking Valuation',
                'description': 'Learn why banks use different valuation methods',
                'estimated_time': '5 minutes',
                'difficulty': 'beginner' if user_level == UserExperienceLevel.BEGINNER else 'intermediate'
            })
        
        # Add more contextual learning opportunities based on analysis results
        
        return opportunities
    
    def _get_personalization_settings(
        self,
        user_level: UserExperienceLevel,
        user_preferences: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Get personalization settings for the user."""
        
        defaults = {
            'show_tooltips': user_level == UserExperienceLevel.BEGINNER,
            'auto_expand_sections': user_level == UserExperienceLevel.ADVANCED,
            'show_calculations': user_level in [UserExperienceLevel.INTERMEDIATE, UserExperienceLevel.ADVANCED],
            'educational_callouts': user_level in [UserExperienceLevel.BEGINNER, UserExperienceLevel.INTERMEDIATE],
            'quick_mode': False
        }
        
        if user_preferences:
            defaults.update(user_preferences)
        
        return defaults
    
    # Helper methods for content generation
    
    def _format_recommendation_explanation(
        self, 
        action: str, 
        confidence: str, 
        language_style: str
    ) -> str:
        """Format recommendation explanation based on language style."""
        
        if language_style == 'simple':
            if 'buy' in action.lower():
                return "This stock looks like a good investment opportunity based on our analysis."
            elif 'sell' in action.lower():
                return "This stock appears overvalued and might not be a good investment right now."
            else:
                return "This stock needs more research before making an investment decision."
        else:
            return f"Based on our multi-model analysis with {confidence} confidence: {action}"
    
    def _extract_key_points(
        self, 
        enhanced_insights: Dict[str, Any], 
        language_style: str
    ) -> List[str]:
        """Extract and format key points based on language style."""
        
        key_points = []
        
        # Extract from risk_reward_profile
        risk_reward = enhanced_insights.get('risk_reward_profile', {})
        strengths = risk_reward.get('primary_strengths', [])
        risks = risk_reward.get('primary_risks', [])
        
        if strengths:
            key_points.append(f"✅ {strengths[0]}")
        if risks:
            key_points.append(f"⚠️ {risks[0]}")
        
        # Add valuation insight
        valuation_insights = enhanced_insights.get('valuation_insights', {})
        recommendation = valuation_insights.get('consensus_recommendation', 'Hold')
        if recommendation:
            key_points.append(f"📊 Multi-model consensus: {recommendation}")
        
        return key_points[:3]  # Limit to 3 key points for summary
    
    def _generate_quick_stats(
        self, 
        analysis_result: Dict[str, Any], 
        template: Dict[str, Any]
    ) -> Dict[str, str]:
        """Generate quick statistics for executive summary."""
        
        multi_model = analysis_result.get('multi_model_analysis', {})
        valuation_summary = multi_model.get('valuation_summary', {})
        
        stats = {}
        
        # Get primary model result
        primary_result = valuation_summary.get('primary_model_result', {})
        if primary_result:
            upside = primary_result.get('upside_downside', 0)
            stats['potential_upside'] = f"{upside:.1f}%"
        
        # Get model confidence
        model_rec = multi_model.get('model_recommendation', {})
        recommended_model = model_rec.get('recommended_model', {})
        if recommended_model:
            stats['valuation_model'] = recommended_model.get('model', 'DCF')
            stats['model_confidence'] = f"{recommended_model.get('confidence_score', 0.7):.0%}"
        
        return stats
    
    def _explain_model_choice(
        self, 
        recommended_model: Dict[str, Any], 
        template: Dict[str, Any]
    ) -> str:
        """Explain why a particular valuation model was chosen."""
        
        model = recommended_model.get('model', 'DCF')
        rationale = recommended_model.get('rationale', '')
        
        if template['language_style'] == 'simple':
            model_explanations = {
                'DCF': 'We used a cash flow analysis because this company generates steady cash flow.',
                'DDM': 'We used a dividend analysis because this is a bank that focuses on paying dividends.',
                'Asset': 'We used an asset-based analysis because this company owns valuable physical assets.'
            }
            return model_explanations.get(model, 'We used a standard valuation approach.')
        else:
            return rationale
    
    def _explain_valuation_range(
        self, 
        multi_model: Dict[str, Any], 
        template: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Explain the valuation range from multiple models."""
        
        valuation_summary = multi_model.get('valuation_summary', {})
        valuation_range = valuation_summary.get('valuation_range', {})
        
        if not valuation_range:
            return {}
        
        explanation = {
            'range': {
                'low': valuation_range.get('min', 0),
                'high': valuation_range.get('max', 0),
                'average': valuation_range.get('average', 0)
            },
            'interpretation': self._interpret_valuation_range(valuation_range, template)
        }
        
        return explanation
    
    def _interpret_valuation_range(
        self, 
        valuation_range: Dict[str, Any], 
        template: Dict[str, Any]
    ) -> str:
        """Interpret valuation range for user."""
        
        spread = valuation_range.get('spread_percentage', 0)
        
        if template['language_style'] == 'simple':
            if spread < 15:
                return "Our different analysis methods agree closely on the stock's value."
            elif spread < 30:
                return "Our analysis methods show some variation in the stock's estimated value."
            else:
                return "There's significant uncertainty in valuing this stock."
        else:
            return f"Valuation spread of {spread:.1f}% indicates {self._get_confidence_level(spread)} in our analysis."
    
    def _get_confidence_level(self, spread: float) -> str:
        """Get confidence level based on valuation spread."""
        if spread < 15:
            return "high confidence"
        elif spread < 30:
            return "moderate confidence"
        else:
            return "lower confidence"
    
    # Additional helper methods would continue here...
    # For brevity, I'm showing the core structure
    
    def _generate_fallback_disclosure(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate fallback disclosure if main generation fails."""
        
        return {
            'user_context': {
                'experience_level': 'intermediate',
                'error': 'Progressive disclosure generation failed, showing simplified view'
            },
            'disclosure_layers': {
                'level_1_summary': {
                    'section_id': 'fallback_summary',
                    'title': 'Analysis Summary',
                    'content': {
                        'headline_recommendation': {
                            'action': 'Additional research recommended',
                            'explanation': 'Analysis completed, please review detailed results.'
                        }
                    }
                }
            }
        }

# Additional helper methods for content generation
    def _generate_peer_context(self, analysis_result: Dict[str, Any], template: Dict[str, Any]) -> Dict[str, Any]:
        """Generate peer comparison context."""
        return {'comparison': 'Peer analysis not available in this version'}
    
    def _explain_key_assumptions(self, analysis_result: Dict[str, Any], template: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Explain key valuation assumptions."""
        return [{'assumption': 'Revenue growth', 'explanation': 'Company growth expectations'}]
    
    def _get_valuation_education(self, template: Dict[str, Any]) -> Dict[str, str]:
        """Get valuation education content."""
        return {'definition': 'Valuation determines what a company is worth'}
    
    def _get_model_comparison_education(self, multi_model: Dict[str, Any], template: Dict[str, Any]) -> Dict[str, Any]:
        """Get model comparison education."""
        return {'comparison': 'Different models provide different perspectives'}
    
    def _explain_analysis_process(self, analysis_result: Dict[str, Any], template: Dict[str, Any]) -> Dict[str, str]:
        """Explain the analysis process."""
        return {'process': 'Multi-step analysis with AI enhancement'}
    
    def _explain_data_sources(self, analysis_result: Dict[str, Any], template: Dict[str, Any]) -> List[str]:
        """Explain data sources used."""
        return ['Financial statements', 'Market data', 'News analysis']
    
    def _explain_ai_role(self, analysis_result: Dict[str, Any], template: Dict[str, Any]) -> Dict[str, str]:
        """Explain AI's role in analysis."""
        return {'role': 'AI helps validate assumptions and provide insights'}
    
    def _explain_validation_process(self, analysis_result: Dict[str, Any], template: Dict[str, Any]) -> Dict[str, str]:
        """Explain validation process."""
        return {'validation': 'Multi-agent validation ensures quality'}
    
    def _get_formulas(self, analysis_result: Dict[str, Any], template: Dict[str, Any]) -> Dict[str, str]:
        """Get formulas if user level supports it."""
        if template['show_formulas']:
            return {'dcf_formula': 'NPV = Σ(FCF/(1+r)^t) + Terminal Value'}
        return {}
    
    def _explain_limitations(self, analysis_result: Dict[str, Any], template: Dict[str, Any]) -> List[str]:
        """Explain analysis limitations."""
        return ['Assumptions may change', 'Market conditions affect accuracy']
    
    def _get_calculation_breakdown(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Get detailed calculation breakdown."""
        return {'calculations': 'Detailed calculations available in export'}
    
    def _get_sensitivity_data(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Get sensitivity analysis data."""
        return {'sensitivity': 'Sensitivity analysis shows impact of assumption changes'}
    
    def _get_model_parameters(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Get model parameters."""
        return {'parameters': 'Model parameters from analysis'}
    
    def _get_data_quality_info(self, analysis_result: Dict[str, Any]) -> Dict[str, str]:
        """Get data quality information."""
        return {'quality': 'Data quality metrics'}
    
    def _generate_assumption_sliders(self, analysis_result: Dict[str, Any], user_level: UserExperienceLevel) -> List[Dict[str, Any]]:
        """Generate interactive assumption sliders."""
        return [{'name': 'Revenue Growth', 'current': 8.0, 'range': [0, 20]}]
    
    def _generate_scenario_buttons(self, analysis_result: Dict[str, Any], user_level: UserExperienceLevel) -> List[Dict[str, str]]:
        """Generate scenario analysis buttons."""
        return [{'scenario': 'Bull Case', 'description': 'Optimistic outlook'}]
    
    def _generate_comparison_options(self, analysis_result: Dict[str, Any], user_level: UserExperienceLevel) -> List[Dict[str, str]]:
        """Generate comparison options."""
        return [{'comparison': 'Peer Companies', 'description': 'Compare to similar companies'}]
    
    def _generate_learning_modules(self, analysis_result: Dict[str, Any], user_level: UserExperienceLevel) -> List[Dict[str, str]]:
        """Generate contextual learning modules."""
        return [{'module': 'DCF Basics', 'description': 'Learn about cash flow valuation'}]

# Global service instance
progressive_disclosure_service = ProgressiveDisclosureService()