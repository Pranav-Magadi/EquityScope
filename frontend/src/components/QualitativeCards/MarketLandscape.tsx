import React from 'react';
import { motion } from 'framer-motion';
import { BarChart3, Users, TrendingUp, MapPin } from 'lucide-react';
import type { MarketLandscape, CompanyAnalysis } from '../../types';
import type { SummaryResponse } from '../../types/summary';
import { DCFUtils } from '../../utils/dcf';

interface MarketLandscapeProps {
  ticker: string;
  companyAnalysis: CompanyAnalysis | SummaryResponse;
}

export const MarketLandscapeCard: React.FC<MarketLandscapeProps> = ({ ticker, companyAnalysis }) => {
  // Type guard to check if we have V3 Summary data
  const isV3Summary = (data: any): data is SummaryResponse => {
    return data && 'analysis_mode' in data && 'fair_value_band' in data;
  };
  
  // Extract market landscape data based on format
  const landscape: MarketLandscape = isV3Summary(companyAnalysis) ? {
    // For V3 Summary, create a simplified market landscape from available data
    competitors: [], // Not available in V3 format
    market_share: undefined,
    industry_trends: [companyAnalysis.market_signals, companyAnalysis.valuation_insights].filter(Boolean),
    market_position: `${companyAnalysis.sector} sector analysis - ${companyAnalysis.investment_label}`
  } : (companyAnalysis as CompanyAnalysis).market_landscape;
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.3 }}
      className="card"
    >
      <div className="card-header">
        <div className="flex items-center space-x-2">
          <BarChart3 className="h-5 w-5 text-primary-400" />
          <h2 className="text-xl font-semibold text-slate-100">Market & Competitive Landscape</h2>
        </div>
        <p className="text-sm text-slate-400 mt-1">
          {isV3Summary(companyAnalysis)
            ? `${companyAnalysis.sector} sector positioning and market insights`
            : 'Industry positioning and competitive analysis'
          }
        </p>
      </div>
      <div className="card-body">
        {/* Market Position Summary */}
        <div className="bg-primary-900/20 border border-primary-500/30 rounded-lg p-4 mb-4">
          <div className="flex items-center space-x-2 mb-2">
            <MapPin className="h-4 w-4 text-primary-400" />
            <h3 className="font-medium text-slate-100">Market Position</h3>
          </div>
          <p className="text-sm text-slate-300">{landscape.market_position}</p>
          {landscape.market_share && (
            <div className="mt-2">
              <span className="text-xs text-slate-400">Market Share: </span>
              <span className="text-sm font-medium text-primary-400">
                {landscape.market_share.toFixed(1)}%
              </span>
            </div>
          )}
        </div>

        {/* Competitors */}
        <div className="mb-4">
          <div className="flex items-center space-x-2 mb-3">
            <Users className="h-4 w-4 text-slate-400" />
            <h3 className="font-medium text-slate-300">Key Competitors</h3>
          </div>
          <div className="space-y-2">
            {landscape.competitors.map((competitor, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3, delay: 0.1 + index * 0.05 }}
                className="bg-slate-700/30 rounded-lg p-3 border border-slate-600/30"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-medium text-slate-200">{competitor.name}</div>
                    <div className="text-xs text-slate-400 mt-1">
                      Market Cap: {DCFUtils.formatCurrency(competitor.market_cap * 10000000)} {/* Assuming crores */}
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-medium text-slate-300">
                      {competitor.market_share.toFixed(1)}%
                    </div>
                    <div className={`text-xs flex items-center ${
                      competitor.growth_rate >= 0 ? 'text-green-400' : 'text-red-400'
                    }`}>
                      <TrendingUp className="h-3 w-3 mr-1" />
                      {competitor.growth_rate > 0 ? '+' : ''}{competitor.growth_rate.toFixed(1)}%
                    </div>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Industry Trends */}
        <div>
          <h3 className="font-medium text-slate-300 mb-3">Industry Trends</h3>
          <div className="grid grid-cols-1 gap-2">
            {landscape.industry_trends.map((trend, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: 0.2 + index * 0.05 }}
                className="bg-slate-700/30 rounded-lg p-3 border border-slate-600/30"
              >
                <div className="flex items-start space-x-2">
                  <div className="w-1 h-1 bg-primary-400 rounded-full mt-2 flex-shrink-0" />
                  <p className="text-sm text-slate-300">{trend}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </motion.div>
  );
};