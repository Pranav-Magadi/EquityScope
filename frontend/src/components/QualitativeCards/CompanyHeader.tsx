import React from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, Building2, Globe, Target, AlertTriangle, CheckCircle } from 'lucide-react';
import { InfoTooltip } from '../common/InfoTooltip';
import type { CompanyInfo, StockPrice, CompanyAnalysis } from '../../types';
import type { SummaryResponse } from '../../types/summary';
import { DCFUtils } from '../../utils/dcf';

interface CompanyHeaderProps {
  ticker: string;
  companyAnalysis: CompanyAnalysis | SummaryResponse;
}

export const CompanyHeader: React.FC<CompanyHeaderProps> = ({
  ticker,
  companyAnalysis
}) => {
  // Type guard to check if we have V3 Summary data
  const isV3Summary = (data: any): data is SummaryResponse => {
    return data && 'analysis_mode' in data && 'fair_value_band' in data;
  };
  
  // Extract data based on format
  const companyInfo: CompanyInfo = isV3Summary(companyAnalysis) ? {
    ticker: companyAnalysis.ticker,
    name: companyAnalysis.company_name,
    sector: companyAnalysis.sector,
    industry: companyAnalysis.sector, // Using sector as industry for V3
    currency: 'INR',
    exchange: 'NSE',
    current_price: companyAnalysis.fair_value_band.current_price,
    market_cap: undefined // Not available in V3 format
  } : (companyAnalysis as CompanyAnalysis).company_info;
  
  const stockPrice: StockPrice = isV3Summary(companyAnalysis) ? {
    current_price: companyAnalysis.fair_value_band.current_price,
    change: 0, // Not available in V3 format
    change_percent: 0, // Not available in V3 format
    volume: 0, // Not available in V3 format
    market_cap: 0, // Not available in V3 format
    pe_ratio: undefined,
    pb_ratio: undefined
  } : (companyAnalysis as CompanyAnalysis).stock_price;
  const change = stockPrice?.change || 0;
  const changePercent = stockPrice?.change_percent || 0;
  const currentPrice = stockPrice?.current_price || 0;
  const isPositiveChange = change >= 0;
  const changeIcon = isPositiveChange ? TrendingUp : TrendingDown;
  const changeColorClass = isPositiveChange ? 'text-green-400' : 'text-red-400';

  // Get recommendation from V3 data or fallback to basic logic
  const getRecommendation = () => {
    if (isV3Summary(companyAnalysis)) {
      // Use V3 investment label
      const label = companyAnalysis.investment_label;
      const colors = {
        'Strongly Bullish': { color: 'text-green-500', icon: CheckCircle },
        'Cautiously Bullish': { color: 'text-green-400', icon: TrendingUp },
        'Neutral': { color: 'text-yellow-400', icon: Target },
        'Cautiously Bearish': { color: 'text-red-400', icon: TrendingDown },
        'Strongly Bearish': { color: 'text-red-500', icon: AlertTriangle }
      };
      const config = colors[label] || colors['Neutral'];
      return { 
        action: label.replace(' Bullish', ' BUY').replace(' Bearish', ' SELL'), 
        reason: companyAnalysis.key_factors[0] || 'Based on comprehensive analysis', 
        color: config.color, 
        icon: config.icon 
      };
    } else {
      // Fallback to basic logic for old format
      const peRatio = stockPrice?.pe_ratio || 0;
      const pbRatio = stockPrice?.pb_ratio || 0;
      
      if (changePercent > 5 && peRatio > 25) {
        return { action: 'HOLD', reason: 'Strong performance but high valuation', color: 'text-yellow-400', icon: AlertTriangle };
      } else if (changePercent < -10) {
        return { action: 'BUY', reason: 'Potential value opportunity', color: 'text-green-400', icon: CheckCircle };
      } else if (changePercent > 3) {
        return { action: 'HOLD', reason: 'Positive momentum', color: 'text-yellow-400', icon: Target };
      } else if (peRatio > 30 || pbRatio > 5) {
        return { action: 'SELL', reason: 'High valuation metrics', color: 'text-red-400', icon: AlertTriangle };
      } else {
        return { action: 'HOLD', reason: 'Market neutral', color: 'text-slate-400', icon: Target };
      }
    }
  };

  const recommendation = getRecommendation();
  const RecommendationIcon = recommendation.icon;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="card"
    >
      <div className="card-body">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center space-x-3 mb-2">
              <div className="p-2 bg-primary-900/20 rounded-lg">
                <Building2 className="h-6 w-6 text-primary-400" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-slate-100">
                  {companyInfo.name}
                </h1>
                <div className="flex items-center space-x-2 text-sm text-slate-400">
                  <span className="font-mono bg-slate-700 px-2 py-1 rounded">
                    {companyInfo.ticker}
                  </span>
                  <Globe className="h-3 w-3" />
                  <span>{companyInfo.exchange}</span>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
              <div className="bg-slate-700/30 rounded-lg p-3">
                <div className="text-xs text-slate-400 mb-1">Sector</div>
                <div className="text-sm font-medium text-slate-200">
                  {companyInfo.sector}
                </div>
              </div>
              <div className="bg-slate-700/30 rounded-lg p-3">
                <div className="text-xs text-slate-400 mb-1">Industry</div>
                <div className="text-sm font-medium text-slate-200">
                  {companyInfo.industry}
                </div>
              </div>
              <div className="bg-slate-700/30 rounded-lg p-3">
                <div className="flex items-center space-x-1 mb-1">
                  <span className="text-xs text-slate-400">Market Cap</span>
                  <InfoTooltip content="Total market value of all outstanding shares. Calculated as current stock price multiplied by total shares outstanding." />
                </div>
                <div className="text-sm font-medium text-slate-200">
                  {stockPrice?.market_cap ? DCFUtils.formatCurrency(stockPrice.market_cap) : 'N/A'}
                </div>
              </div>
              <div className="bg-slate-700/30 rounded-lg p-3">
                <div className="flex items-center space-x-1 mb-1">
                  <span className="text-xs text-slate-400">Volume</span>
                  <InfoTooltip content="Number of shares traded during the current trading session. Higher volume often indicates increased investor interest or significant news." />
                </div>
                <div className="text-sm font-medium text-slate-200">
                  {stockPrice?.volume ? DCFUtils.formatLargeNumber(stockPrice.volume) : 'N/A'}
                </div>
              </div>
            </div>
          </div>

          <div className="text-right ml-6">
            {/* Investment Recommendation */}
            <div className="mb-3 text-right">
              <div className={`flex items-center justify-end space-x-2 ${recommendation.color} mb-1`}>
                <RecommendationIcon className="h-4 w-4" />
                <span className="font-bold text-sm">{recommendation.action}</span>
              </div>
              <div className="text-xs text-slate-400">{recommendation.reason}</div>
            </div>
            
            <div className="text-3xl font-bold text-slate-100 mb-1">
              ₹{currentPrice.toFixed(2)}
            </div>
            <div className={`flex items-center justify-end space-x-1 ${changeColorClass}`}>
              {React.createElement(changeIcon, { className: 'h-4 w-4' })}
              <span className="font-medium">
                ₹{Math.abs(change).toFixed(2)}
              </span>
              <span className="text-sm">
                ({changePercent > 0 ? '+' : ''}{changePercent.toFixed(2)}%)
              </span>
            </div>
            <div className="text-xs text-slate-400 mt-1">
              Daily Change
            </div>
            
            {(stockPrice?.pe_ratio || stockPrice?.pb_ratio) && (
              <div className="grid grid-cols-2 gap-2 mt-3 text-xs">
                {stockPrice?.pe_ratio && (
                  <div className="bg-slate-700/30 rounded px-2 py-1">
                    <div className="flex items-center space-x-1">
                      <span className="text-slate-400">P/E</span>
                      <InfoTooltip content="Price-to-Earnings ratio. Compares stock price to annual earnings per share. Lower P/E may indicate undervaluation, higher P/E may suggest growth expectations." />
                    </div>
                    <div className="font-medium text-slate-200">
                      {stockPrice.pe_ratio.toFixed(1)}x
                    </div>
                  </div>
                )}
                {stockPrice?.pb_ratio && (
                  <div className="bg-slate-700/30 rounded px-2 py-1">
                    <div className="flex items-center space-x-1">
                      <span className="text-slate-400">P/B</span>
                      <InfoTooltip content="Price-to-Book ratio. Compares stock price to book value per share. Lower P/B may indicate undervaluation relative to assets." />
                    </div>
                    <div className="font-medium text-slate-200">
                      {stockPrice.pb_ratio.toFixed(1)}x
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </motion.div>
  );
};