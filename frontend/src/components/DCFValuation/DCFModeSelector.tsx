import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Brain, Calculator, Clock, Zap, ChevronRight, Info } from 'lucide-react';
import { InfoTooltip } from '../common/InfoTooltip';
import type { DCFMode, ModeRecommendationResponse } from '../../types';

interface DCFModeSelectorProps {
  selectedMode: DCFMode;
  onModeChange: (mode: DCFMode) => void;
  modeRecommendation?: ModeRecommendationResponse;
  isLoading?: boolean;
}

interface ModeOptionProps {
  mode: DCFMode;
  title: string;
  description: string;
  timeRequired: string;
  complexity: string;
  icon: React.ComponentType<{ className?: string }>;
  features: string[];
  isSelected: boolean;
  isRecommended: boolean;
  onClick: () => void;
}

const ModeOption: React.FC<ModeOptionProps> = ({
  mode,
  title,
  description,
  timeRequired,
  complexity,
  icon: Icon,
  features,
  isSelected,
  isRecommended,
  onClick
}) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      onClick={onClick}
      className={`relative p-6 rounded-lg border-2 cursor-pointer transition-all duration-200 ${
        isSelected
          ? 'border-primary-500 bg-primary-900/20'
          : 'border-slate-600 bg-slate-800/30 hover:border-slate-500'
      }`}
    >
      {/* Recommended Badge */}
      {isRecommended && (
        <div className="absolute -top-2 -right-2 bg-gradient-to-r from-primary-500 to-blue-500 text-white text-xs px-2 py-1 rounded-full font-medium">
          Recommended
        </div>
      )}

      {/* Header */}
      <div className="flex items-center space-x-3 mb-3">
        <div className={`p-2 rounded-lg ${isSelected ? 'bg-primary-500/20' : 'bg-slate-700/50'}`}>
          <Icon className={`h-6 w-6 ${isSelected ? 'text-primary-400' : 'text-slate-400'}`} />
        </div>
        <div>
          <h3 className={`text-lg font-semibold ${isSelected ? 'text-slate-100' : 'text-slate-200'}`}>
            {title}
          </h3>
          <p className="text-sm text-slate-400">{description}</p>
        </div>
      </div>

      {/* Metadata */}
      <div className="flex items-center space-x-4 mb-4">
        <div className="flex items-center space-x-1">
          <Clock className="h-4 w-4 text-slate-500" />
          <span className="text-xs text-slate-400">{timeRequired}</span>
        </div>
        <div className="flex items-center space-x-1">
          <Zap className={`h-4 w-4 ${
            complexity === 'Low' ? 'text-green-500' : 
            complexity === 'Medium' ? 'text-yellow-500' : 'text-red-500'
          }`} />
          <span className="text-xs text-slate-400">{complexity} Complexity</span>
        </div>
      </div>

      {/* Features */}
      <div className="space-y-2">
        {features.map((feature, index) => (
          <div key={index} className="flex items-center space-x-2">
            <ChevronRight className="h-3 w-3 text-primary-400 flex-shrink-0" />
            <span className="text-sm text-slate-300">{feature}</span>
          </div>
        ))}
      </div>

      {/* Selection Indicator */}
      {isSelected && (
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          className="absolute bottom-4 right-4 w-6 h-6 bg-primary-500 rounded-full flex items-center justify-center"
        >
          <div className="w-2 h-2 bg-white rounded-full" />
        </motion.div>
      )}
    </motion.div>
  );
};

export const DCFModeSelector: React.FC<DCFModeSelectorProps> = ({
  selectedMode,
  onModeChange,
  modeRecommendation,
  isLoading = false
}) => {
  const [expandedMode, setExpandedMode] = useState<DCFMode | null>(null);

  const simpleModeFeatures = [
    'Historical 5-year CAGR analysis',
    'Conservative GDP blending over 10 years',
    'Rule-based growth projections',
    'Educational DCF fundamentals',
    'Perfect for learning and baseline analysis'
  ];

  const agenticModeFeatures = [
    'AI-enhanced management guidance extraction',
    'News sentiment integration',
    'Multi-scenario Bull/Base/Bear modeling',
    'Forward-looking competitive analysis',
    'Sophisticated risk-adjusted valuations'
  ];

  if (isLoading) {
    return (
      <div className="space-y-4">
        <div className="h-6 bg-slate-700 rounded animate-pulse mb-4" />
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="h-48 bg-slate-700/30 rounded-lg animate-pulse" />
          <div className="h-48 bg-slate-700/30 rounded-lg animate-pulse" />
        </div>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="space-y-6"
    >
      {/* Header */}
      <div className="flex items-center space-x-3 mb-6">
        <Brain className="h-6 w-6 text-primary-400" />
        <h2 className="text-xl font-semibold text-slate-100">Choose Your DCF Analysis Mode</h2>
        <InfoTooltip content="Select between Simple Mode (historically-grounded) for learning and Agentic Mode (AI-enhanced) for comprehensive analysis. The recommendation is based on your experience level and the company characteristics." />
      </div>

      {/* Mode Recommendation */}
      {modeRecommendation && (
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="bg-gradient-to-r from-blue-900/20 to-primary-900/20 border border-blue-500/30 rounded-lg p-4 mb-6"
        >
          <div className="flex items-start space-x-3">
            <Info className="h-5 w-5 text-blue-400 mt-0.5 flex-shrink-0" />
            <div>
              <h4 className="text-sm font-medium text-blue-300 mb-1">AI Recommendation</h4>
              <p className="text-sm text-slate-300 mb-2">
                <span className="font-medium text-primary-400 capitalize">
                  {modeRecommendation.mode_recommendation.recommended_mode} Mode
                </span> is recommended for {modeRecommendation.ticker}
              </p>
              <p className="text-xs text-slate-400">
                {modeRecommendation.mode_recommendation.rationale}
              </p>
            </div>
          </div>
        </motion.div>
      )}

      {/* Mode Options */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ModeOption
          mode="simple"
          title="Simple DCF Mode"
          description="Traditional DCF analysis with proven methodologies - perfect for learning and baseline valuations"
          timeRequired={modeRecommendation?.mode_comparison.simple_mode.time_required || "30-60 seconds"}
          complexity={modeRecommendation?.mode_comparison.simple_mode.complexity || "Beginner Friendly"}
          icon={Calculator}
          features={simpleModeFeatures}
          isSelected={selectedMode === 'simple'}
          isRecommended={modeRecommendation?.mode_recommendation.recommended_mode === 'simple'}
          onClick={() => onModeChange('simple')}
        />

        <ModeOption
          mode="agentic"
          title="AI Multi-Agent Mode"
          description="Advanced AI-powered analysis with Bull/Bear/Neutral perspectives and real-time insights"
          timeRequired={modeRecommendation?.mode_comparison.agentic_mode.time_required || "60-90 seconds"}
          complexity={modeRecommendation?.mode_comparison.agentic_mode.complexity || "Professional"}
          icon={Brain}
          features={agenticModeFeatures}
          isSelected={selectedMode === 'agentic'}
          isRecommended={modeRecommendation?.mode_recommendation.recommended_mode === 'agentic'}
          onClick={() => onModeChange('agentic')}
        />
      </div>

      {/* Mode Comparison */}
      {modeRecommendation && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-slate-800/50 rounded-lg p-4"
        >
          <h4 className="text-sm font-medium text-slate-300 mb-3">Quick Comparison</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
            <div>
              <span className="font-medium text-primary-400">Simple Mode:</span>
              <p className="text-slate-400 mt-1">
                {modeRecommendation.mode_comparison.simple_mode.description}
              </p>
            </div>
            <div>
              <span className="font-medium text-blue-400">Agentic Mode:</span>
              <p className="text-slate-400 mt-1">
                {modeRecommendation.mode_comparison.agentic_mode.description}
              </p>
            </div>
          </div>
        </motion.div>
      )}
    </motion.div>
  );
};