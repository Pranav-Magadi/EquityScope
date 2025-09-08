import React from 'react';
import { motion } from 'framer-motion';
import { Clock, RefreshCw } from 'lucide-react';
import { FairValueBandChart } from './FairValueBandChart';
import { InvestmentLabelBadge } from './InvestmentLabelBadge';
import { KeyFactorsList } from './KeyFactorsList';
import { ThreeLensAnalysis } from './ThreeLensAnalysis';
import { DataHealthWarnings } from './DataHealthWarnings';
import { AnalysisModeToggle } from './AnalysisModeToggle';
import { WeightedScoreDisplay } from './WeightedScoreDisplay';
import type { SummaryResponse, AnalysisMode } from '../../types/summary';

interface SummaryBoxProps {
  ticker: string;
  summary: SummaryResponse;
  onModeToggle: (mode: AnalysisMode) => void;
  isLoading: boolean;
  onRefresh?: () => void;
  hideAnalysisModeToggle?: boolean;
}

export const SummaryBox: React.FC<SummaryBoxProps> = ({
  ticker,
  summary,
  onModeToggle,
  isLoading,
  onRefresh,
  hideAnalysisModeToggle = false
}) => {
  const formatTimestamp = (timestamp: string) => {
    try {
      const date = new Date(timestamp);
      return date.toLocaleString('en-IN', {
        dateStyle: 'medium',
        timeStyle: 'short',
        timeZone: 'Asia/Kolkata'
      });
    } catch {
      return 'Unknown';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header with Company Info and Last Updated */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-slate-800 border border-slate-700 rounded-lg p-6"
      >
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-slate-100 mb-1">
              {summary.company_name}
            </h1>
            <div className="flex items-center space-x-4 text-sm text-slate-400">
              <span className="font-mono">{ticker}</span>
              <span>•</span>
              <span>{summary.sector}</span>
              <span>•</span>
              <span className="capitalize">{summary.analysis_mode} Mode</span>
            </div>
          </div>
          
          <div className="text-right">
            <div className="flex items-center space-x-2 text-sm text-slate-400 mb-2">
              <Clock className="h-4 w-4" />
              <span>Last Updated</span>
            </div>
            <div className="text-slate-300 font-medium">
              {formatTimestamp(summary.analysis_timestamp)}
            </div>
            {onRefresh && (
              <button
                onClick={onRefresh}
                disabled={isLoading}
                className="mt-2 flex items-center space-x-1 text-xs text-blue-400 hover:text-blue-300 transition-colors disabled:opacity-50"
              >
                <RefreshCw className={`h-3 w-3 ${isLoading ? 'animate-spin' : ''}`} />
                <span>Refresh</span>
              </button>
            )}
          </div>
        </div>
      </motion.div>

      {/* Analysis Mode Toggle */}
      {!hideAnalysisModeToggle && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <AnalysisModeToggle
            currentMode={summary.analysis_mode}
            onModeChange={onModeToggle}
            disabled={isLoading}
          />
        </motion.div>
      )}

      {/* Main Summary Grid */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="grid grid-cols-1 lg:grid-cols-2 gap-6"
      >
        {/* Fair Value Band */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.3 }}
        >
          <FairValueBandChart fairValueBand={summary.fair_value_band} />
        </motion.div>

        {/* Investment Label */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.4 }}
        >
          <InvestmentLabelBadge
            label={summary.investment_label}
            confidence={summary.fair_value_band.confidence}
          />
        </motion.div>
      </motion.div>

      {/* Key Factors */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
      >
        <KeyFactorsList factors={summary.key_factors} />
      </motion.div>

      {/* Weighted Score Display (if available) */}
      {summary.analysis_mode === 'simple' && summary.weighted_score !== undefined && summary.component_scores && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
        >
          <WeightedScoreDisplay
            totalScore={summary.weighted_score}
            componentScores={summary.component_scores}
            investmentLabel={summary.investment_label}
            confidence={summary.fair_value_band.confidence}
          />
        </motion.div>
      )}

      {/* Three Lens Analysis */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: summary.analysis_mode === 'simple' && summary.weighted_score !== undefined ? 0.7 : 0.6 }}
      >
        <ThreeLensAnalysis
          valuation={summary.valuation_insights}
          market={summary.market_signals}
          fundamentals={summary.business_fundamentals}
        />
      </motion.div>

      {/* Data Health Warnings */}
      {summary.data_health_warnings && summary.data_health_warnings.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7 }}
        >
          <DataHealthWarnings warnings={summary.data_health_warnings} />
        </motion.div>
      )}
    </div>
  );
};