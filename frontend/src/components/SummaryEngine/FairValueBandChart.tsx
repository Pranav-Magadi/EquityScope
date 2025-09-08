import React from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import type { FairValueBand } from '../../types/summary';

interface FairValueBandChartProps {
  fairValueBand: FairValueBand;
}

export const FairValueBandChart: React.FC<FairValueBandChartProps> = ({ 
  fairValueBand 
}) => {
  const { min_value, max_value, current_price, method, confidence } = fairValueBand;
  
  // Calculate position of current price within the band
  const bandWidth = max_value - min_value;
  const pricePosition = ((current_price - min_value) / bandWidth) * 100;
  
  // Determine if current price is above, below, or within the band
  const priceStatus = current_price < min_value ? 'below' : 
                     current_price > max_value ? 'above' : 'within';
  
  const upside = ((max_value - current_price) / current_price) * 100;
  const downside = ((current_price - min_value) / current_price) * 100;
  
  const getStatusColor = () => {
    switch (priceStatus) {
      case 'below': return 'text-green-400';
      case 'above': return 'text-red-400';
      case 'within': return 'text-blue-400';
      default: return 'text-slate-400';
    }
  };
  
  const getStatusIcon = () => {
    switch (priceStatus) {
      case 'below': return <TrendingUp className="h-4 w-4" />;
      case 'above': return <TrendingDown className="h-4 w-4" />;
      case 'within': return <Minus className="h-4 w-4" />;
    }
  };

  return (
    <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-slate-100">Fair Value Band</h3>
        <div className="flex items-center space-x-2">
          <span className={`flex items-center space-x-1 ${getStatusColor()}`}>
            {getStatusIcon()}
            <span className="text-sm font-medium">
              {priceStatus === 'below' ? 'Undervalued' : 
               priceStatus === 'above' ? 'Overvalued' : 'Fair Value'}
            </span>
          </span>
        </div>
      </div>

      {/* Fair Value Band Visualization */}
      <div className="mb-6">
        <div className="relative h-8 bg-slate-700 rounded-lg overflow-hidden">
          {/* Fair Value Band */}
          <div className="absolute inset-0 bg-gradient-to-r from-green-500/30 to-green-400/30" />
          
          {/* Current Price Indicator */}
          <motion.div
            initial={{ scaleX: 0 }}
            animate={{ scaleX: 1 }}
            transition={{ duration: 0.8, ease: "easeOut" }}
            className="absolute top-0 h-full w-1 bg-white shadow-lg"
            style={{ 
              left: priceStatus === 'below' ? '0%' : 
                    priceStatus === 'above' ? '100%' : `${Math.max(0, Math.min(100, pricePosition))}%`,
              transform: 'translateX(-50%)'
            }}
          />
          
          {/* Price labels */}
          <div className="absolute -top-6 left-0 text-xs text-slate-400">
            ₹{min_value.toFixed(0)}
          </div>
          <div className="absolute -top-6 right-0 text-xs text-slate-400">
            ₹{max_value.toFixed(0)}
          </div>
          <div 
            className="absolute -top-6 text-xs font-semibold text-white"
            style={{ 
              left: priceStatus === 'below' ? '0%' : 
                    priceStatus === 'above' ? '100%' : `${Math.max(0, Math.min(100, pricePosition))}%`,
              transform: 'translateX(-50%)'
            }}
          >
            ₹{current_price.toFixed(0)}
          </div>
        </div>
      </div>

      {/* Metrics */}
      <div className="grid grid-cols-3 gap-4 text-center">
        <div>
          <div className="text-sm text-slate-400">Upside Potential</div>
          <div className={`text-lg font-semibold ${upside > 0 ? 'text-green-400' : 'text-red-400'}`}>
            {upside > 0 ? '+' : ''}{upside.toFixed(1)}%
          </div>
        </div>
        <div>
          <div className="text-sm text-slate-400">Method</div>
          <div className="text-lg font-semibold text-slate-200">
            {method.replace('_', ' ')}
          </div>
        </div>
        <div>
          <div className="text-sm text-slate-400">Confidence</div>
          <div className="text-lg font-semibold text-blue-400">
            {(confidence * 100).toFixed(0)}%
          </div>
        </div>
      </div>

      {/* Downside Protection */}
      {priceStatus === 'above' && (
        <div className="mt-4 p-3 bg-red-900/20 border border-red-500/30 rounded-lg">
          <div className="text-sm text-red-300">
            <strong>Downside Risk:</strong> -{downside.toFixed(1)}% to fair value
          </div>
        </div>
      )}
    </div>
  );
};