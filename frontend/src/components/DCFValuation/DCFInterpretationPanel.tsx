import React from 'react';
import { motion } from 'framer-motion';
import { 
  Lightbulb, 
  AlertTriangle, 
  TrendingUp, 
  TrendingDown, 
  Shield, 
  Target,
  DollarSign,
  Clock,
  BarChart3,
  Info
} from 'lucide-react';
import type { MultiStageDCFResponse } from '../../types';

interface DCFInterpretationPanelProps {
  dcfResponse: MultiStageDCFResponse;
  userLevel?: 'beginner' | 'intermediate' | 'advanced';
}

interface InterpretationInsight {
  type: 'bullish' | 'bearish' | 'neutral' | 'warning';
  title: string;
  description: string;
  confidence: 'high' | 'medium' | 'low';
  reasoning: string;
}

const getInsightIcon = (type: string) => {
  switch (type) {
    case 'bullish': return TrendingUp;
    case 'bearish': return TrendingDown;
    case 'neutral': return BarChart3;
    case 'warning': return AlertTriangle;
    default: return Info;
  }
};

const getInsightColor = (type: string) => {
  switch (type) {
    case 'bullish': return 'text-green-400 bg-green-500/10 border-green-500/20';
    case 'bearish': return 'text-red-400 bg-red-500/10 border-red-500/20';
    case 'neutral': return 'text-blue-400 bg-blue-500/10 border-blue-500/20';
    case 'warning': return 'text-yellow-400 bg-yellow-500/10 border-yellow-500/20';
    default: return 'text-slate-400 bg-slate-500/10 border-slate-500/20';
  }
};

const generateInterpretations = (dcfResponse: MultiStageDCFResponse, userLevel: string): InterpretationInsight[] => {
  const { valuation, mode } = dcfResponse;
  const upside = valuation.upside_downside;
  const insights: InterpretationInsight[] = [];

  // Valuation Assessment
  if (upside > 15) {
    insights.push({
      type: 'bullish',
      title: 'Significant Upside Potential',
      description: `Our DCF analysis suggests the stock is trading ${upside.toFixed(1)}% below its intrinsic value of ₹${valuation.intrinsic_value_per_share.toFixed(0)}.`,
      confidence: 'high',
      reasoning: 'Large price gaps in DCF models often indicate market inefficiencies or overlooked value creation potential.'
    });
  } else if (upside > 5) {
    insights.push({
      type: 'bullish',
      title: 'Moderate Upside Opportunity',
      description: `The stock appears modestly undervalued with ${upside.toFixed(1)}% upside to fair value.`,
      confidence: 'medium',
      reasoning: 'Modest undervaluation suggests reasonable entry opportunity with limited downside risk.'
    });
  } else if (upside < -15) {
    insights.push({
      type: 'bearish',
      title: 'Significant Overvaluation Risk',
      description: `The current price appears ${Math.abs(upside).toFixed(1)}% above our calculated intrinsic value.`,
      confidence: 'high',
      reasoning: 'Large overvaluation suggests market expectations may be too optimistic relative to fundamental value.'
    });
  } else if (upside < -5) {
    insights.push({
      type: 'bearish',
      title: 'Moderate Overvaluation',
      description: `The stock is trading ${Math.abs(upside).toFixed(1)}% above our fair value estimate.`,
      confidence: 'medium',
      reasoning: 'Moderate overvaluation indicates caution warranted, though not necessarily a strong sell signal.'
    });
  } else {
    insights.push({
      type: 'neutral',
      title: 'Fair Value Trading Range',
      description: `The current price is within ${Math.abs(upside).toFixed(1)}% of our intrinsic value estimate.`,
      confidence: 'high',
      reasoning: 'Stock appears fairly valued by the market, suggesting efficient pricing relative to fundamentals.'
    });
  }

  // Growth Pattern Analysis
  const earlyGrowth = Object.values(valuation.growth_waterfall)[0];
  const lateGrowth = Object.values(valuation.growth_waterfall)[Object.values(valuation.growth_waterfall).length - 2];
  
  if (earlyGrowth > 15) {
    insights.push({
      type: 'bullish',
      title: 'Strong Near-Term Growth Trajectory',
      description: `Early-stage growth of ${earlyGrowth.toFixed(1)}% suggests strong fundamental momentum.`,
      confidence: mode === 'simple' ? 'high' : 'medium',
      reasoning: mode === 'simple' 
        ? 'Historical data supports this growth rate with high confidence'
        : 'AI analysis incorporates forward-looking factors but carries model uncertainty'
    });
  }

  if (earlyGrowth - lateGrowth > 10) {
    insights.push({
      type: 'neutral',
      title: 'Realistic Growth Fade Modeled',
      description: `Growth declines from ${earlyGrowth.toFixed(1)}% to ${lateGrowth.toFixed(1)}% over the projection period.`,
      confidence: 'high',
      reasoning: 'Multi-stage modeling captures realistic competitive dynamics and market maturation effects.'
    });
  }

  // Mode-Specific Insights
  if (mode === 'simple') {
    insights.push({
      type: 'neutral',
      title: 'Conservative Historical Approach',
      description: 'Analysis based on verified historical performance with GDP-blended long-term assumptions.',
      confidence: 'high',
      reasoning: 'Simple mode provides reliable baseline using established track record and conservative projections.'
    });
  } else {
    insights.push({
      type: 'neutral',
      title: 'AI-Enhanced Forward Analysis',
      description: 'Incorporates management guidance, market sentiment, and strategic developments beyond historical data.',
      confidence: 'medium',
      reasoning: 'Agentic mode captures additional value drivers but introduces model complexity and uncertainty.'
    });
  }

  // Terminal Value Assessment
  const terminalPortion = (valuation.terminal_value / valuation.enterprise_value) * 100;
  if (terminalPortion > 70) {
    insights.push({
      type: 'warning',
      title: 'High Terminal Value Dependency',
      description: `${terminalPortion.toFixed(0)}% of value comes from terminal value beyond 10 years.`,
      confidence: 'high',
      reasoning: 'High terminal value dependency increases sensitivity to long-term assumptions and discount rate changes.'
    });
  } else if (terminalPortion < 50) {
    insights.push({
      type: 'bullish',
      title: 'Strong Near-Term Value Creation',
      description: `${(100 - terminalPortion).toFixed(0)}% of value comes from 10-year explicit projections.`,
      confidence: 'high',
      reasoning: 'Lower terminal value dependency provides more reliable valuation based on explicit cash flow projections.'
    });
  }

  return insights;
};

const InvestmentDecisionGuidance: React.FC<{ 
  upside: number; 
  userLevel: string;
  mode: string;
}> = ({ upside, userLevel, mode }) => {
  const getDecisionFramework = () => {
    if (upside > 20) {
      return {
        decision: 'Strong Buy Consideration',
        rationale: 'Significant undervaluation suggests attractive risk-adjusted returns',
        actions: [
          'Consider position sizing based on conviction level',
          'Review catalysts that could close the value gap',
          'Monitor key assumptions for changes',
          'Set target price near intrinsic value'
        ],
        risks: [
          'Market may be pricing in risks not captured in DCF',
          'Value gap may take longer than expected to close',
          'Assumptions may prove too optimistic'
        ]
      };
    } else if (upside > 10) {
      return {
        decision: 'Buy Consideration',
        rationale: 'Moderate undervaluation with reasonable upside potential',
        actions: [
          'Suitable for value-oriented portfolios',
          'Consider dollar-cost averaging approach',
          'Wait for better entry if risk-averse',
          'Compare to sector alternatives'
        ],
        risks: [
          'Limited margin of safety',
          'Growth assumptions may not materialize',
          'Market sentiment could remain negative'
        ]
      };
    } else if (upside > -10) {
      return {
        decision: 'Hold/Neutral',
        rationale: 'Fair value trading suggests efficient market pricing',
        actions: [
          'Maintain existing positions if held',
          'Monitor for better entry opportunities',
          'Focus on dividend yield if applicable',
          'Consider other opportunities with better risk-reward'
        ],
        risks: [
          'Limited upside potential at current levels',
          'Vulnerable to market downturns',
          'Opportunity cost versus alternatives'
        ]
      };
    } else {
      return {
        decision: 'Avoid/Sell Consideration',
        rationale: 'Overvaluation suggests limited upside with downside risk',
        actions: [
          'Avoid new positions at current levels',
          'Consider reducing existing positions',
          'Wait for significant pullback',
          'Look for better value elsewhere'
        ],
        risks: [
          'Potential for continued overvaluation',
          'Market momentum may persist',
          'Missing out if assumptions prove conservative'
        ]
      };
    }
  };

  const framework = getDecisionFramework();

  return (
    <div className="bg-slate-800/30 rounded-lg p-4 border border-slate-700/50">
      <div className="flex items-center space-x-2 mb-3">
        <Target className="h-5 w-5 text-primary-400" />
        <h4 className="font-semibold text-slate-200">{framework.decision}</h4>
      </div>
      
      <p className="text-sm text-slate-300 mb-4">{framework.rationale}</p>
      
      {userLevel !== 'beginner' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <h5 className="text-xs font-medium text-green-400 mb-2">Potential Actions</h5>
            <ul className="text-xs text-slate-400 space-y-1">
              {framework.actions.map((action, index) => (
                <li key={index} className="flex items-start space-x-1">
                  <span className="text-green-400 mt-0.5">•</span>
                  <span>{action}</span>
                </li>
              ))}
            </ul>
          </div>
          
          <div>
            <h5 className="text-xs font-medium text-yellow-400 mb-2">Key Risks</h5>
            <ul className="text-xs text-slate-400 space-y-1">
              {framework.risks.map((risk, index) => (
                <li key={index} className="flex items-start space-x-1">
                  <span className="text-yellow-400 mt-0.5">•</span>
                  <span>{risk}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
};

export const DCFInterpretationPanel: React.FC<DCFInterpretationPanelProps> = ({
  dcfResponse,
  userLevel = 'intermediate'
}) => {
  const insights = generateInterpretations(dcfResponse, userLevel);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="space-y-6"
    >
      {/* Header */}
      <div className="flex items-center space-x-3">
        <div className="p-2 bg-primary-500/20 rounded-lg">
          <Lightbulb className="h-6 w-6 text-primary-400" />
        </div>
        <div>
          <h3 className="text-lg font-semibold text-slate-100">What This Means</h3>
          <p className="text-sm text-slate-400">Plain-English interpretation of your DCF analysis</p>
        </div>
      </div>

      {/* Key Insights */}
      <div className="space-y-4">
        {insights.map((insight, index) => {
          const IconComponent = getInsightIcon(insight.type);
          const colorClasses = getInsightColor(insight.type);
          
          return (
            <motion.div
              key={index}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.3, delay: index * 0.1 }}
              className={`border rounded-lg p-4 ${colorClasses}`}
            >
              <div className="flex items-start space-x-3">
                <div className="p-1 rounded">
                  <IconComponent className="h-5 w-5" />
                </div>
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-1">
                    <h4 className="font-medium text-slate-100">{insight.title}</h4>
                    <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                      insight.confidence === 'high' 
                        ? 'bg-green-500/20 text-green-300'
                        : insight.confidence === 'medium'
                        ? 'bg-yellow-500/20 text-yellow-300'
                        : 'bg-red-500/20 text-red-300'
                    }`}>
                      {insight.confidence.toUpperCase()}
                    </span>
                  </div>
                  <p className="text-sm text-slate-300 mb-2">{insight.description}</p>
                  {userLevel !== 'beginner' && (
                    <p className="text-xs text-slate-400 italic">{insight.reasoning}</p>
                  )}
                </div>
              </div>
            </motion.div>
          );
        })}
      </div>

      {/* Investment Decision Framework */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.3 }}
      >
        <div className="flex items-center space-x-2 mb-4">
          <DollarSign className="h-5 w-5 text-slate-400" />
          <h4 className="font-medium text-slate-300">Investment Decision Framework</h4>
        </div>
        
        <InvestmentDecisionGuidance 
          upside={dcfResponse.valuation.upside_downside}
          userLevel={userLevel}
          mode={dcfResponse.mode}
        />
      </motion.div>

      {/* Assumptions Sensitivity */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.4 }}
        className="bg-gradient-to-r from-purple-900/10 to-blue-900/10 border border-purple-500/20 rounded-lg p-4"
      >
        <div className="flex items-center space-x-2 mb-3">
          <Shield className="h-5 w-5 text-purple-400" />
          <h4 className="font-medium text-slate-300">Key Assumption Sensitivity</h4>
        </div>
        
        <div className="text-sm text-slate-400 space-y-2">
          <p>
            <strong className="text-slate-300">Most Critical:</strong> Terminal growth rate and discount rate assumptions 
            heavily influence valuation due to compound effects over 10 years.
          </p>
          <p>
            <strong className="text-slate-300">Moderate Impact:</strong> Near-term growth rates (years 1-3) affect 
            overall value but with lower sensitivity than terminal assumptions.
          </p>
          <p>
            <strong className="text-slate-300">Monitor Closely:</strong> Changes in competitive position, regulatory environment, 
            or industry dynamics could invalidate growth stage assumptions.
          </p>
        </div>
      </motion.div>

      {/* Disclaimer */}
      {userLevel === 'beginner' && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.5 }}
          className="bg-yellow-900/10 border border-yellow-500/20 rounded-lg p-3"
        >
          <div className="flex items-start space-x-2">
            <AlertTriangle className="h-4 w-4 text-yellow-400 mt-0.5 flex-shrink-0" />
            <div className="text-xs text-yellow-200">
              <strong>Investment Disclaimer:</strong> This analysis is for educational purposes only. 
              DCF models are estimates based on assumptions that may not materialize. Always consult 
              with financial advisors and conduct additional research before making investment decisions.
            </div>
          </div>
        </motion.div>
      )}
    </motion.div>
  );
};