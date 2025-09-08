import React from 'react';
import { motion } from 'framer-motion';
import { Calculator, Brain, Clock, Zap, TrendingUp, BarChart3, Users, BookOpen, Key } from 'lucide-react';
import type { AnalysisMode } from '../../types/summary';

interface ModeSelectionCardsProps {
  selectedMode: AnalysisMode;
  onModeSelect: (mode: AnalysisMode) => void;
  disabled?: boolean;
}

export const ModeSelectionCards: React.FC<ModeSelectionCardsProps> = ({
  selectedMode,
  onModeSelect,
  disabled = false
}) => {
  const modeData = {
    simple: {
      title: "Rule-Based Analysis",
      subtitle: "Fast & Systematic",
      icon: Calculator,
      color: "blue",
      analysisTime: "~15 seconds",
      requiresApiKey: false,
      features: [
        { icon: TrendingUp, text: "DCF valuation with auto-selected sector models" },
        { icon: BarChart3, text: "Technical indicators (RSI, volume, momentum)" },
        { icon: Users, text: "Peer comparison with sector-matched companies" },
        { icon: Clock, text: "Rule-based insights with conglomerate handling" }
      ],
      benefits: [
        "Consistent, deterministic results",
        "Special handling for complex companies",
        "Pure quantitative methodology", 
        "No API costs or dependencies"
      ],
      bestFor: "Quick investment decisions, portfolio screening, systematic analysis approach",
      methodology: "Sector-specific DCF models + technical analysis + peer benchmarking with quantitative rules",
      apiRequirement: "No API keys required - works with financial data only",
      tokenUsage: undefined
    },
    agentic: {
      title: "AI Analyst Insights",
      subtitle: "Deep & Contextual",
      icon: Brain,
      color: "purple",
      analysisTime: "<30 seconds",
      requiresApiKey: true,
      features: [
        { icon: BookOpen, text: "AI-generated structured investment summaries" },
        { icon: TrendingUp, text: "News analysis from multiple sources" },
        { icon: BarChart3, text: "AI-enhanced DCF commentary & reasoning" },
        { icon: Users, text: "Contextual market insights & sentiment" }
      ],
      benefits: [
        "Context-aware qualitative insights",
        "Current market news integration",
        "Natural language explanations",
        "Enhanced decision-making depth"
      ],
      bestFor: "Comprehensive research, complex investment decisions, understanding market context",
      methodology: "AI-enhanced analysis combining quantitative data with news sentiment and contextual reasoning",
      apiRequirement: "Requires Claude API key - Estimated 2,500-4,000 tokens per query (~$0.02-$0.06)",
      tokenUsage: "2,500-4,000 tokens per query"
    }
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-6xl mx-auto">
      {Object.entries(modeData).map(([mode, data]) => {
        const isSelected = selectedMode === mode;
        const IconComponent = data.icon;
        const colorClasses = {
          blue: {
            border: isSelected ? 'border-blue-500 ring-2 ring-blue-500/20' : 'border-slate-600 hover:border-blue-400',
            bg: isSelected ? 'bg-blue-900/30' : 'bg-slate-800 hover:bg-slate-750',
            icon: isSelected ? 'bg-blue-600' : 'bg-slate-600',
            text: 'text-blue-400',
            badge: 'bg-blue-900/50 text-blue-300 border-blue-500/30'
          },
          purple: {
            border: isSelected ? 'border-purple-500 ring-2 ring-purple-500/20' : 'border-slate-600 hover:border-purple-400',
            bg: isSelected ? 'bg-purple-900/30' : 'bg-slate-800 hover:bg-slate-750',
            icon: isSelected ? 'bg-purple-600' : 'bg-slate-600',
            text: 'text-purple-400',
            badge: 'bg-purple-900/50 text-purple-300 border-purple-500/30'
          }
        };
        
        const colors = colorClasses[data.color as keyof typeof colorClasses];

        return (
          <motion.div
            key={mode}
            onClick={() => !disabled && onModeSelect(mode as AnalysisMode)}
            className={`
              relative p-8 rounded-xl border-2 cursor-pointer transition-all duration-300
              ${colors.border} ${colors.bg}
              ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
            `}
            whileHover={!disabled ? { scale: 1.02 } : {}}
            whileTap={!disabled ? { scale: 0.98 } : {}}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
          >
            {/* Selection Indicator */}
            {isSelected && (
              <motion.div
                className="absolute top-4 right-4 w-4 h-4 bg-current rounded-full"
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ type: "spring", stiffness: 300, damping: 20 }}
                style={{ color: data.color === 'blue' ? '#60a5fa' : '#a78bfa' }}
              />
            )}

            {/* Header */}
            <div className="flex items-start justify-between mb-6">
              <div className="flex items-center space-x-4">
                <div className={`p-3 rounded-lg ${colors.icon}`}>
                  <IconComponent className="h-8 w-8 text-white" />
                </div>
                <div>
                  <h3 className="text-2xl font-bold text-slate-100 mb-1">
                    {data.title}
                  </h3>
                  <p className="text-slate-400 font-medium">
                    {data.subtitle}
                  </p>
                </div>
              </div>
            </div>

            {/* Analysis Time Badge */}
            <div className={`inline-flex items-center space-x-2 px-3 py-1 rounded-full border mb-6 ${colors.badge}`}>
              <Clock className="h-4 w-4" />
              <span className="text-sm font-medium">{data.analysisTime}</span>
            </div>

            {/* Features */}
            <div className="space-y-3 mb-6">
              <h4 className="text-slate-200 font-semibold text-sm uppercase tracking-wider">
                What You Get
              </h4>
              {data.features.map((feature, index) => (
                <div key={index} className="flex items-center space-x-3">
                  <feature.icon className={`h-4 w-4 ${colors.text} flex-shrink-0`} />
                  <span className="text-slate-300 text-sm">{feature.text}</span>
                </div>
              ))}
            </div>

            {/* Benefits */}
            <div className="space-y-2 mb-6">
              <h4 className="text-slate-200 font-semibold text-sm uppercase tracking-wider">
                Key Benefits
              </h4>
              <ul className="space-y-1">
                {data.benefits.map((benefit, index) => (
                  <li key={index} className="text-slate-400 text-sm flex items-start">
                    <Zap className={`h-3 w-3 ${colors.text} mt-0.5 mr-2 flex-shrink-0`} />
                    {benefit}
                  </li>
                ))}
              </ul>
            </div>

            {/* Best For */}
            <div className="border-t border-slate-700 pt-4 mb-4">
              <h4 className={`font-semibold text-sm mb-2 ${colors.text}`}>
                💡 Best For:
              </h4>
              <p className="text-slate-300 text-sm leading-relaxed">
                {data.bestFor}
              </p>
            </div>

            {/* API Requirement Info */}
            <div className={`rounded-lg p-3 mb-4 ${
              data.requiresApiKey 
                ? 'bg-yellow-900/20 border border-yellow-700/30'
                : 'bg-green-900/20 border border-green-700/30'
            }`}>
              <div className="flex items-start space-x-2">
                <Key className={`h-4 w-4 mt-0.5 flex-shrink-0 ${
                  data.requiresApiKey ? 'text-yellow-400' : 'text-green-400'
                }`} />
                <div>
                  <h4 className={`font-medium text-xs uppercase tracking-wider mb-1 ${
                    data.requiresApiKey ? 'text-yellow-300' : 'text-green-300'
                  }`}>
                    {data.requiresApiKey ? 'API Key Required' : 'No API Keys Needed'}
                  </h4>
                  <p className={`text-xs leading-relaxed ${
                    data.requiresApiKey ? 'text-yellow-200' : 'text-green-200'
                  }`}>
                    {data.apiRequirement}
                  </p>
                </div>
              </div>
            </div>

            {/* Token Usage (AI Mode Only) */}
            {data.requiresApiKey && data.tokenUsage && (
              <div className="bg-blue-900/20 border border-blue-700/30 rounded-lg p-3 mb-4">
                <div className="flex items-start space-x-2">
                  <BarChart3 className="h-4 w-4 mt-0.5 flex-shrink-0 text-blue-400" />
                  <div>
                    <h4 className="font-medium text-xs uppercase tracking-wider mb-1 text-blue-300">
                      Token Usage Per Query
                    </h4>
                    <p className="text-xs leading-relaxed text-blue-200">
                      {data.tokenUsage}
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* Methodology */}
            <div className="bg-slate-900/50 rounded-lg p-4">
              <h4 className="text-slate-300 font-medium text-xs uppercase tracking-wider mb-2">
                Methodology
              </h4>
              <p className="text-slate-400 text-xs leading-relaxed">
                {data.methodology}
              </p>
            </div>

            {/* Selection Overlay */}
            {isSelected && (
              <motion.div
                className="absolute inset-0 bg-gradient-to-br from-transparent via-transparent to-current opacity-5 rounded-xl pointer-events-none"
                initial={{ opacity: 0 }}
                animate={{ opacity: 0.05 }}
                style={{ 
                  background: `linear-gradient(135deg, transparent 0%, transparent 70%, ${data.color === 'blue' ? '#3b82f6' : '#8b5cf6'} 100%)`
                }}
              />
            )}
          </motion.div>
        );
      })}
    </div>
  );
};