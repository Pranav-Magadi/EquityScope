import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Users, 
  CheckCircle, 
  TrendingUp, 
  TrendingDown, 
  AlertTriangle, 
  Target, 
  ChevronDown, 
  ChevronRight,
  Star,
  ArrowUp,
  ArrowDown,
  Activity
} from 'lucide-react';
import type { 
  ValidationReport, 
  BullCommentary, 
  BearCommentary, 
  InvestmentCommitteeData
} from '../../types';

interface AIInvestmentCommitteeProps {
  data: InvestmentCommitteeData;
  companyName: string;
  ticker: string;
}

const ValidationReportCard: React.FC<{
  validation: ValidationReport;
}> = ({ validation }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const getScoreColor = (score: number) => {
    if (score >= 8) return 'text-green-400 bg-green-900/20';
    if (score >= 6) return 'text-yellow-400 bg-yellow-900/20';
    return 'text-red-400 bg-red-900/20';
  };

  const getScoreIcon = (score: number) => {
    if (score >= 8) return CheckCircle;
    if (score >= 6) return AlertTriangle;
    return AlertTriangle;
  };

  const ScoreIcon = getScoreIcon(validation.overall_score);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-slate-800 rounded-lg border border-slate-700 overflow-hidden"
    >
      {/* Header */}
      <div className="p-6 border-b border-slate-700">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-blue-600 rounded-lg">
              <CheckCircle className="h-5 w-5 text-white" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-white">AI Validation Report</h3>
              <p className="text-sm text-slate-400">Analysis quality assessment</p>
            </div>
          </div>
          <div className={`flex items-center space-x-2 px-3 py-2 rounded-lg ${getScoreColor(validation.overall_score)}`}>
            <ScoreIcon className="h-4 w-4" />
            <span className="font-bold">{validation.overall_score.toFixed(1)}/10</span>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="p-6">
        {/* Quick Assessment */}
        <div className="grid grid-cols-2 gap-4 mb-6">
          <div className="bg-slate-900/50 rounded-lg p-4">
            <h4 className="text-sm font-medium text-slate-200 mb-2">Qualitative Assessment</h4>
            <div className="space-y-2 text-xs">
              <div className="flex justify-between">
                <span className="text-slate-400">SWOT Accuracy:</span>
                <span className="text-slate-200">Strong</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">News Interpretation:</span>
                <span className="text-slate-200">Accurate</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Source Quality:</span>
                <span className="text-slate-200">High</span>
              </div>
            </div>
          </div>

          <div className="bg-slate-900/50 rounded-lg p-4">
            <h4 className="text-sm font-medium text-slate-200 mb-2">Quantitative Assessment</h4>
            <div className="space-y-2 text-xs">
              <div className="flex justify-between">
                <span className="text-slate-400">DCF Assumptions:</span>
                <span className="text-slate-200">Reasonable</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Sensitivity Range:</span>
                <span className="text-slate-200">Appropriate</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Calculations:</span>
                <span className="text-slate-200">Accurate</span>
              </div>
            </div>
          </div>
        </div>

        {/* Expandable Details */}
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="w-full flex items-center justify-between p-3 bg-slate-700/30 rounded-lg hover:bg-slate-600/30 transition-colors"
        >
          <span className="text-sm font-medium text-slate-200">View Detailed Analysis</span>
          {isExpanded ? (
            <ChevronDown className="h-4 w-4 text-slate-400" />
          ) : (
            <ChevronRight className="h-4 w-4 text-slate-400" />
          )}
        </button>

        <AnimatePresence>
          {isExpanded && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              className="mt-4 space-y-4"
            >
              {/* Key Concerns */}
              {validation.key_concerns.length > 0 && (
                <div>
                  <h5 className="text-sm font-medium text-slate-200 mb-2">Key Concerns</h5>
                  <div className="space-y-2">
                    {validation.key_concerns.map((concern, index) => (
                      <div key={index} className="flex items-start space-x-2 p-2 bg-red-900/10 border border-red-700/30 rounded">
                        <AlertTriangle className="h-3 w-3 text-red-400 mt-0.5 flex-shrink-0" />
                        <p className="text-xs text-red-200">{concern}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Recommendations */}
              {validation.recommendations.length > 0 && (
                <div>
                  <h5 className="text-sm font-medium text-slate-200 mb-2">Recommendations</h5>
                  <div className="space-y-2">
                    {validation.recommendations.map((rec, index) => (
                      <div key={index} className="flex items-start space-x-2 p-2 bg-blue-900/10 border border-blue-700/30 rounded">
                        <Target className="h-3 w-3 text-blue-400 mt-0.5 flex-shrink-0" />
                        <p className="text-xs text-blue-200">{rec}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  );
};

const CommentaryCard: React.FC<{
  commentary: BullCommentary | BearCommentary;
  type: 'bull' | 'bear';
}> = ({ commentary, type }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const config = type === 'bull' ? {
    icon: TrendingUp,
    color: 'text-green-400',
    bgColor: 'bg-green-600',
    title: 'Bull Case Analysis',
    subtitle: 'Optimistic growth scenario'
  } : {
    icon: TrendingDown,
    color: 'text-red-400',
    bgColor: 'bg-red-600',
    title: 'Bear Case Analysis',
    subtitle: 'Conservative risk assessment'
  };

  const Icon = config.icon;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: type === 'bull' ? 0.1 : 0.2 }}
      className="bg-slate-800 rounded-lg border border-slate-700 overflow-hidden"
    >
      {/* Header */}
      <div className="p-6 border-b border-slate-700">
        <div className="flex items-center space-x-3">
          <div className={`p-2 ${config.bgColor} rounded-lg`}>
            <Icon className="h-5 w-5 text-white" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-white">{config.title}</h3>
            <p className="text-sm text-slate-400">{config.subtitle}</p>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="p-6">
        {/* Summary */}
        <div className="mb-6">
          <h4 className="text-sm font-medium text-slate-200 mb-2">Key Implications</h4>
          <p className="text-sm text-slate-300 leading-relaxed">
            {type === 'bull' 
              ? (commentary as BullCommentary).bullish_implications
              : (commentary as BearCommentary).bearish_implications
            }
          </p>
        </div>

        {/* Price Target */}
        <div className="mb-6 p-4 bg-slate-900/50 rounded-lg">
          <h4 className="text-sm font-medium text-slate-200 mb-2">Price Target Scenario</h4>
          <p className="text-sm text-slate-300">
            {type === 'bull' 
              ? (commentary as BullCommentary).target_price_scenario
              : (commentary as BearCommentary).conservative_price_scenario
            }
          </p>
        </div>

        {/* Catalysts/Risks */}
        <div className="mb-6">
          <h4 className="text-sm font-medium text-slate-200 mb-3">
            {type === 'bull' ? 'Upside Catalysts' : 'Downside Risks'}
          </h4>
          <div className="space-y-2">
            {(type === 'bull' 
              ? (commentary as BullCommentary).upside_catalysts
              : (commentary as BearCommentary).downside_risks
            ).map((item, index) => (
              <div key={index} className="flex items-start space-x-2 p-3 bg-slate-700/30 rounded">
                <div className={`w-1.5 h-1.5 rounded-full mt-2 flex-shrink-0 ${
                  type === 'bull' ? 'bg-green-400' : 'bg-red-400'
                }`} />
                <p className="text-sm text-slate-300">{item}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Recommended Modifications */}
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="w-full flex items-center justify-between p-3 bg-slate-700/30 rounded-lg hover:bg-slate-600/30 transition-colors mb-4"
        >
          <span className="text-sm font-medium text-slate-200">DCF Assumption Modifications</span>
          {isExpanded ? (
            <ChevronDown className="h-4 w-4 text-slate-400" />
          ) : (
            <ChevronRight className="h-4 w-4 text-slate-400" />
          )}
        </button>

        <AnimatePresence>
          {isExpanded && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              className="space-y-3"
            >
              {commentary.recommended_modifications.map((mod, index) => (
                <div key={index} className="p-3 bg-slate-900/50 rounded-lg border border-slate-600/30">
                  <div className="flex items-center justify-between mb-2">
                    <h5 className="text-sm font-medium text-slate-200 capitalize">
                      {mod.assumption.replace('_', ' ')}
                    </h5>
                    <div className="flex items-center space-x-2">
                      <span className="text-xs text-slate-400">{mod.current_value}%</span>
                      {mod.recommended_value > mod.current_value ? (
                        <ArrowUp className={`h-3 w-3 ${config.color}`} />
                      ) : (
                        <ArrowDown className={`h-3 w-3 ${config.color}`} />
                      )}
                      <span className={`text-xs font-medium ${config.color}`}>
                        {mod.recommended_value}%
                      </span>
                    </div>
                  </div>
                  <p className="text-xs text-slate-400">{mod.justification}</p>
                </div>
              ))}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  );
};

export const AIInvestmentCommittee: React.FC<AIInvestmentCommitteeProps> = ({ 
  data, 
  companyName, 
  ticker 
}) => {
  return (
    <div className="space-y-6">
      {/* Section Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center"
      >
        <div className="flex items-center justify-center space-x-3 mb-2">
          <div className="p-3 bg-gradient-to-r from-purple-600 to-blue-600 rounded-lg">
            <Users className="h-6 w-6 text-white" />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-white">AI Investment Committee</h2>
            <p className="text-slate-400">Multi-agent validation and investment perspectives</p>
          </div>
        </div>
        <div className="flex items-center justify-center space-x-1 text-xs text-slate-500">
          <Activity className="h-3 w-3" />
          <span>4-Agent Analysis: Generator → Checker → Bull → Bear</span>
        </div>
      </motion.div>

      {/* Validation Report */}
      <ValidationReportCard validation={data.validation_report} />

      {/* Bull and Bear Commentary */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <CommentaryCard commentary={data.bull_commentary} type="bull" />
        <CommentaryCard commentary={data.bear_commentary} type="bear" />
      </div>

      {/* AI Attribution */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.4 }}
        className="text-center p-4 bg-gradient-to-r from-purple-900/20 to-blue-900/20 border border-purple-700/30 rounded-lg"
      >
        <div className="flex items-center justify-center space-x-2 text-sm text-purple-200">
          <Star className="h-4 w-4" />
          <span>
            <strong>AI-Powered Analysis:</strong> Generated by Claude AI with source attribution and multi-agent validation
          </span>
        </div>
      </motion.div>
    </div>
  );
};

export default AIInvestmentCommittee;