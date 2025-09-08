import React from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, Sparkles } from 'lucide-react';
import type { AnalysisMode } from '../../types/summary';

interface ModeSelectionHeaderProps {
  selectedMode?: AnalysisMode | null;
}

export const ModeSelectionHeader: React.FC<ModeSelectionHeaderProps> = ({
  selectedMode
}) => {
  return (
    <div className="text-center mb-12">
      {/* Main Title */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="mb-4"
      >
        <div className="flex items-center justify-center space-x-3 mb-4">
          <div className="p-2 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg">
            <TrendingUp className="h-8 w-8 text-white" />
          </div>
          <h1 className="text-5xl font-bold bg-gradient-to-r from-slate-100 to-slate-300 bg-clip-text text-transparent">
            EquityScope v3
          </h1>
          <motion.div
            animate={{ rotate: [0, 10, -10, 0] }}
            transition={{ duration: 2, repeat: Infinity, repeatType: "reverse" }}
          >
            <Sparkles className="h-6 w-6 text-yellow-400" />
          </motion.div>
        </div>
        
        <h2 className="text-2xl font-semibold text-slate-200 mb-2">
          Investment Summary Engine
        </h2>
        
        <p className="text-slate-400 text-lg max-w-3xl mx-auto leading-relaxed">
          Choose your analysis approach, then enter any stock ticker for comprehensive investment insights
        </p>
      </motion.div>

      {/* Step Indicator */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3, duration: 0.6 }}
        className="flex items-center justify-center space-x-2 mb-8"
      >
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center text-white text-sm font-bold">
              1
            </div>
            <span className="text-slate-300 font-medium">Choose Analysis Mode</span>
          </div>
          
          <div className="w-8 h-px bg-slate-600"></div>
          
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-slate-600 rounded-full flex items-center justify-center text-slate-400 text-sm font-bold">
              2
            </div>
            <span className="text-slate-500 font-medium">Enter Stock Ticker</span>
          </div>
          
          <div className="w-8 h-px bg-slate-600"></div>
          
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-slate-600 rounded-full flex items-center justify-center text-slate-400 text-sm font-bold">
              3
            </div>
            <span className="text-slate-500 font-medium">Get Investment Summary</span>
          </div>
        </div>
      </motion.div>

      {/* Selected Mode Indicator */}
      {selectedMode && (
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.3 }}
          className="mb-6"
        >
          <div className={`inline-flex items-center space-x-3 px-6 py-3 rounded-full border ${
            selectedMode === 'simple' 
              ? 'bg-blue-900/30 text-blue-300 border-blue-500/30' 
              : 'bg-purple-900/30 text-purple-300 border-purple-500/30'
          }`}>
            <div className={`w-3 h-3 rounded-full ${
              selectedMode === 'simple' ? 'bg-blue-400' : 'bg-purple-400'
            }`}></div>
            <span className="font-medium">
              {selectedMode === 'simple' ? 'Rule-Based Analysis' : 'AI Analyst Insights'} Selected
            </span>
            <div className="text-xs opacity-75">
              ✓ Ready for ticker input
            </div>
          </div>
        </motion.div>
      )}

      {/* Feature Highlights */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6, duration: 0.6 }}
        className="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-4xl mx-auto text-center"
      >
        {[
          { label: "Fair Value Band", desc: "DCF-based valuation range" },
          { label: "Investment Label", desc: "Clear bullish/bearish assessment" },
          { label: "Three Lens Analysis", desc: "Valuation, market, fundamentals" },
          { label: "Data Health Warnings", desc: "Transparent data quality alerts" }
        ].map((feature, index) => (
          <div key={index} className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
            <div className="font-medium text-slate-200 text-sm mb-1">
              {feature.label}
            </div>
            <div className="text-xs text-slate-400 leading-relaxed">
              {feature.desc}
            </div>
          </div>
        ))}
      </motion.div>
    </div>
  );
};