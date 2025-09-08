import React from 'react';
import { motion } from 'framer-motion';
import { Brain, Calculator } from 'lucide-react';
import type { AnalysisMode } from '../../types/summary';

interface AnalysisModeToggleProps {
  currentMode: AnalysisMode;
  onModeChange: (mode: AnalysisMode) => void;
  disabled?: boolean;
}

export const AnalysisModeToggle: React.FC<AnalysisModeToggleProps> = ({
  currentMode,
  onModeChange,
  disabled = false
}) => {
  const modes = [
    {
      id: 'simple' as const,
      label: 'Rule-Based Analysis',
      description: 'Quantitative rules and heuristics',
      icon: Calculator,
      color: 'blue'
    },
    {
      id: 'agentic' as const,
      label: 'AI Analyst Insights',
      description: 'LLM-powered investment thesis',
      icon: Brain,
      color: 'purple'
    }
  ];

  return (
    <div className="bg-slate-800 border border-slate-700 rounded-lg p-4">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-slate-200 mb-1">Analysis Mode</h3>
        <p className="text-xs text-slate-400">
          Choose between rule-based analysis or AI-powered insights
        </p>
      </div>

      <div className="flex space-x-2">
        {modes.map((mode) => {
          const isActive = currentMode === mode.id;
          const Icon = mode.icon;

          return (
            <motion.button
              key={mode.id}
              onClick={() => onModeChange(mode.id)}
              disabled={disabled}
              className={`flex-1 flex items-center space-x-3 p-3 rounded-lg border transition-all duration-200 ${
                isActive
                  ? mode.color === 'blue'
                    ? 'bg-blue-600 text-white border-blue-500'
                    : 'bg-purple-600 text-white border-purple-500'
                  : mode.color === 'blue'
                    ? 'bg-blue-900/20 text-blue-300 border-blue-600/30 hover:bg-blue-800/30'
                    : 'bg-purple-900/20 text-purple-300 border-purple-600/30 hover:bg-purple-800/30'
              } ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
              whileHover={disabled ? {} : { scale: 1.02 }}
              whileTap={disabled ? {} : { scale: 0.98 }}
            >
              <Icon className="h-5 w-5 flex-shrink-0" />
              <div className="text-left flex-1">
                <div className="text-sm font-medium">{mode.label}</div>
                <div className={`text-xs ${isActive ? 'opacity-90' : 'opacity-75'}`}>
                  {mode.description}
                </div>
              </div>
              
              {/* Active indicator */}
              {isActive && (
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  className="w-2 h-2 bg-white rounded-full"
                />
              )}
            </motion.button>
          );
        })}
      </div>

      {/* Mode-specific info */}
      <div className="mt-3 p-2 bg-slate-700/30 rounded text-xs text-slate-400">
        {currentMode === 'simple' ? (
          '⚡ Fast analysis using pre-defined rules and financial metrics'
        ) : (
          '🧠 Deep analysis with AI-powered reasoning and sector-specific insights'
        )}
      </div>
    </div>
  );
};