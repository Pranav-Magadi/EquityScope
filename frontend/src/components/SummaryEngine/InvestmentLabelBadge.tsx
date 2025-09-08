import React from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, Minus, AlertTriangle, Target } from 'lucide-react';
import type { InvestmentLabel } from '../../types/summary';

interface InvestmentLabelBadgeProps {
  label: InvestmentLabel;
  confidence: number;
}

export const InvestmentLabelBadge: React.FC<InvestmentLabelBadgeProps> = ({
  label,
  confidence
}) => {
  const getLabelConfig = (label: InvestmentLabel) => {
    switch (label) {
      case "Strongly Bullish":
        return {
          color: "bg-green-600 text-white border-green-500",
          icon: <TrendingUp className="h-5 w-5" />,
          description: "Strong buy signal with high conviction"
        };
      case "Cautiously Bullish":
        return {
          color: "bg-green-500/20 text-green-300 border-green-400/50",
          icon: <TrendingUp className="h-5 w-5" />,
          description: "Positive outlook with moderate confidence"
        };
      case "Neutral":
        return {
          color: "bg-slate-600/20 text-slate-300 border-slate-500/50",
          icon: <Minus className="h-5 w-5" />,
          description: "Balanced risk-reward, hold position"
        };
      case "Cautiously Bearish":
        return {
          color: "bg-red-500/20 text-red-300 border-red-400/50",
          icon: <TrendingDown className="h-5 w-5" />,
          description: "Negative signals with caution advised"
        };
      case "Strongly Bearish":
        return {
          color: "bg-red-600 text-white border-red-500",
          icon: <TrendingDown className="h-5 w-5" />,
          description: "Strong sell signal with high conviction"
        };
      default:
        return {
          color: "bg-slate-600 text-white border-slate-500",
          icon: <AlertTriangle className="h-5 w-5" />,
          description: "Assessment pending"
        };
    }
  };

  const config = getLabelConfig(label);
  
  return (
    <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-slate-100">Investment Assessment</h3>
        <div className="flex items-center space-x-2">
          <Target className="h-4 w-4 text-slate-400" />
          <span className="text-sm text-slate-400">
            {(confidence * 100).toFixed(0)}% confidence
          </span>
        </div>
      </div>

      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5 }}
        className={`inline-flex items-center space-x-3 px-6 py-4 rounded-lg border-2 ${config.color} w-full justify-center`}
      >
        <motion.div
          initial={{ rotate: -10 }}
          animate={{ rotate: 0 }}
          transition={{ duration: 0.3, delay: 0.2 }}
        >
          {config.icon}
        </motion.div>
        <div className="text-center">
          <div className="text-xl font-bold mb-1">{label}</div>
          <div className="text-sm opacity-90">{config.description}</div>
        </div>
      </motion.div>

      {/* Confidence Meter */}
      <div className="mt-4">
        <div className="flex justify-between items-center mb-2">
          <span className="text-sm text-slate-400">Analysis Confidence</span>
          <span className="text-sm font-medium text-slate-300">
            {confidence >= 0.8 ? 'High' : confidence >= 0.6 ? 'Medium' : 'Low'}
          </span>
        </div>
        <div className="w-full bg-slate-700 rounded-full h-2">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${confidence * 100}%` }}
            transition={{ duration: 1, delay: 0.3 }}
            className={`h-2 rounded-full ${
              confidence >= 0.8 ? 'bg-green-500' : 
              confidence >= 0.6 ? 'bg-yellow-500' : 'bg-red-500'
            }`}
          />
        </div>
      </div>

      {/* Low Confidence Warning */}
      {confidence < 0.6 && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="mt-4 p-3 bg-yellow-900/20 border border-yellow-500/30 rounded-lg"
        >
          <div className="flex items-center space-x-2">
            <AlertTriangle className="h-4 w-4 text-yellow-400" />
            <div className="text-sm text-yellow-300">
              <strong>Note:</strong> Low confidence analysis due to limited data availability
            </div>
          </div>
        </motion.div>
      )}
    </div>
  );
};