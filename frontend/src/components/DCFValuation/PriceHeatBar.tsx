import React from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, Target, AlertCircle } from 'lucide-react';

interface PriceHeatBarProps {
  currentPrice: number;
  intrinsicValue: number;
  bullTarget?: number;
  bearTarget?: number;
  companyName: string;
}

export const PriceHeatBar: React.FC<PriceHeatBarProps> = ({
  currentPrice,
  intrinsicValue,
  bullTarget,
  bearTarget,
  companyName
}) => {
  // Calculate price range for visualization
  const prices = [currentPrice, intrinsicValue, bullTarget, bearTarget].filter((p): p is number => p !== undefined && p > 0);
  const minPrice = prices.length > 0 ? Math.min(...prices) * 0.9 : 0; // Add 10% buffer
  const maxPrice = prices.length > 0 ? Math.max(...prices) * 1.1 : 100; // Add 10% buffer
  const priceRange = maxPrice - minPrice;

  // If no valid prices, return early with fallback display
  if (prices.length === 0 || priceRange === 0) {
    return (
      <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-600/30">
        <div className="flex items-center justify-center h-32">
          <div className="text-slate-400 text-center">
            <p>Price data not available</p>
            <p className="text-sm">Unable to display price visualization</p>
          </div>
        </div>
      </div>
    );
  }

  // Calculate positions on the bar (0-100%)
  const getPosition = (price: number) => {
    return ((price - minPrice) / priceRange) * 100;
  };

  const currentPos = getPosition(currentPrice);
  const intrinsicPos = getPosition(intrinsicValue);
  const bullPos = bullTarget ? getPosition(bullTarget) : null;
  const bearPos = bearTarget ? getPosition(bearTarget) : null;

  // Determine valuation status
  const upside = ((intrinsicValue - currentPrice) / currentPrice) * 100;
  const isUndervalued = upside > 5;
  const isOvervalued = upside < -5;
  
  const getValuationColor = () => {
    if (isUndervalued) return 'text-green-400';
    if (isOvervalued) return 'text-red-400';
    return 'text-yellow-400';
  };

  const getValuationIcon = () => {
    if (isUndervalued) return TrendingUp;
    if (isOvervalued) return TrendingDown;
    return Target;
  };

  const ValuationIcon = getValuationIcon();

  return (
    <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-600/30">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-slate-100 flex items-center space-x-2">
          <Target className="h-5 w-5 text-primary-400" />
          <span>Price Valuation Analysis</span>
        </h3>
        <div className={`flex items-center space-x-2 ${getValuationColor()}`}>
          <ValuationIcon className="h-4 w-4" />
          <span className="font-medium">
            {upside > 0 ? '+' : ''}{upside.toFixed(1)}% {isUndervalued ? 'Undervalued' : isOvervalued ? 'Overvalued' : 'Fair Value'}
          </span>
        </div>
      </div>

      {/* Price Heat Bar */}
      <div className="relative">
        {/* Background bar */}
        <div className="w-full h-8 bg-slate-700 rounded-lg relative overflow-hidden">
          {/* Gradient background showing value zones */}
          <div className="absolute inset-0 bg-gradient-to-r from-red-500/20 via-yellow-500/20 to-green-500/20" />
          
          {/* Current Price Marker */}
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ duration: 0.5 }}
            className="absolute top-0 h-full w-1 bg-blue-400 shadow-lg z-10"
            style={{ left: `${currentPos}%` }}
          >
            <div className="absolute -top-8 left-1/2 transform -translate-x-1/2">
              <div className="bg-blue-500 text-white text-xs px-2 py-1 rounded whitespace-nowrap">
                Current: ₹{currentPrice.toFixed(0)}
              </div>
            </div>
          </motion.div>

          {/* Intrinsic Value Marker */}
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="absolute top-0 h-full w-1 bg-purple-400 shadow-lg z-10"
            style={{ left: `${intrinsicPos}%` }}
          >
            <div className="absolute -bottom-8 left-1/2 transform -translate-x-1/2">
              <div className="bg-purple-500 text-white text-xs px-2 py-1 rounded whitespace-nowrap">
                DCF: ₹{intrinsicValue.toFixed(0)}
              </div>
            </div>
          </motion.div>

          {/* Bear Target Marker */}
          {bearTarget && bearPos !== null && (
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              className="absolute top-0 h-full w-1 bg-red-400 shadow-lg z-10"
              style={{ left: `${bearPos}%` }}
            >
              <div className="absolute -top-8 left-1/2 transform -translate-x-1/2">
                <div className="bg-red-500 text-white text-xs px-2 py-1 rounded whitespace-nowrap">
                  Bear: ₹{bearTarget.toFixed(0)}
                </div>
              </div>
            </motion.div>
          )}

          {/* Bull Target Marker */}
          {bullTarget && bullPos !== null && (
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ duration: 0.5, delay: 0.3 }}
              className="absolute top-0 h-full w-1 bg-green-400 shadow-lg z-10"
              style={{ left: `${bullPos}%` }}
            >
              <div className="absolute -bottom-8 left-1/2 transform -translate-x-1/2">
                <div className="bg-green-500 text-white text-xs px-2 py-1 rounded whitespace-nowrap">
                  Bull: ₹{bullTarget.toFixed(0)}
                </div>
              </div>
            </motion.div>
          )}
        </div>

        {/* Price scale */}
        <div className="flex justify-between mt-12 text-xs text-slate-400">
          <span>₹{minPrice.toFixed(0)}</span>
          <span>₹{maxPrice.toFixed(0)}</span>
        </div>
      </div>

      {/* Legend */}
      <div className="grid grid-cols-2 gap-4 mt-6">
        <div className="space-y-2">
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-blue-400 rounded"></div>
            <span className="text-sm text-slate-300">Current Market Price</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-purple-400 rounded"></div>
            <span className="text-sm text-slate-300">DCF Intrinsic Value</span>
          </div>
        </div>
        <div className="space-y-2">
          {bearTarget && (
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-red-400 rounded"></div>
              <span className="text-sm text-slate-300">Bear Case Target</span>
            </div>
          )}
          {bullTarget && (
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-green-400 rounded"></div>
              <span className="text-sm text-slate-300">Bull Case Target</span>
            </div>
          )}
        </div>
      </div>

      {/* Valuation Insight */}
      <div className="mt-4 p-3 bg-slate-700/30 rounded-lg">
        <div className="flex items-start space-x-2">
          <AlertCircle className="h-4 w-4 text-blue-400 mt-0.5 flex-shrink-0" />
          <div className="text-sm text-slate-300">
            <strong>Valuation Insight:</strong> {' '}
            {isUndervalued && (
              <>The market price is <strong className="text-green-400">{Math.abs(upside).toFixed(1)}% below</strong> our DCF intrinsic value, suggesting potential upside opportunity.</>
            )}
            {isOvervalued && (
              <>The market price is <strong className="text-red-400">{Math.abs(upside).toFixed(1)}% above</strong> our DCF intrinsic value, suggesting the stock may be overvalued.</>
            )}
            {!isUndervalued && !isOvervalued && (
              <>The market price is close to our DCF intrinsic value, suggesting <strong className="text-yellow-400">fair valuation</strong>.</>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default PriceHeatBar;