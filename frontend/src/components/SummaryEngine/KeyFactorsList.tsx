import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, ChevronUp, Key, TrendingUp, TrendingDown, AlertCircle } from 'lucide-react';

interface KeyFactorsListProps {
  factors: string[];
}

export const KeyFactorsList: React.FC<KeyFactorsListProps> = ({ factors }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  
  // Show first 3 factors by default, rest on expansion
  const visibleFactors = isExpanded ? factors : factors.slice(0, 3);
  const hasMoreFactors = factors.length > 3;

  const getFactorIcon = (factor: string) => {
    const lowerFactor = factor.toLowerCase();
    if (lowerFactor.includes('undervalued') || lowerFactor.includes('growth') || lowerFactor.includes('strong')) {
      return <TrendingUp className="h-4 w-4 text-green-400" />;
    } else if (lowerFactor.includes('overvalued') || lowerFactor.includes('decline') || lowerFactor.includes('weak')) {
      return <TrendingDown className="h-4 w-4 text-red-400" />;
    } else if (lowerFactor.includes('risk') || lowerFactor.includes('caution') || lowerFactor.includes('concern')) {
      return <AlertCircle className="h-4 w-4 text-yellow-400" />;
    }
    return <Key className="h-4 w-4 text-blue-400" />;
  };

  const getFactorStyle = (factor: string) => {
    const lowerFactor = factor.toLowerCase();
    if (lowerFactor.includes('undervalued') || lowerFactor.includes('growth') || lowerFactor.includes('strong')) {
      return 'border-green-500/30 bg-green-900/10';
    } else if (lowerFactor.includes('overvalued') || lowerFactor.includes('decline') || lowerFactor.includes('weak')) {
      return 'border-red-500/30 bg-red-900/10';
    } else if (lowerFactor.includes('risk') || lowerFactor.includes('caution') || lowerFactor.includes('concern')) {
      return 'border-yellow-500/30 bg-yellow-900/10';
    }
    return 'border-slate-600/50 bg-slate-800/50';
  };

  return (
    <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-slate-100">Key Factors</h3>
        <div className="text-sm text-slate-400">
          {factors.length} factor{factors.length !== 1 ? 's' : ''} identified
        </div>
      </div>

      <div className="space-y-3">
        <AnimatePresence>
          {visibleFactors.map((factor, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.3, delay: index * 0.1 }}
              className={`flex items-start space-x-3 p-3 rounded-lg border ${getFactorStyle(factor)}`}
            >
              <div className="flex-shrink-0 mt-0.5">
                {getFactorIcon(factor)}
              </div>
              <div className="flex-1 text-slate-200 text-sm leading-relaxed">
                {factor}
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>

      {hasMoreFactors && (
        <motion.button
          onClick={() => setIsExpanded(!isExpanded)}
          className="w-full mt-4 flex items-center justify-center space-x-2 py-2 px-4 bg-slate-700/50 hover:bg-slate-700 text-slate-300 rounded-lg transition-colors"
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          <span className="text-sm">
            {isExpanded ? 'Show Less' : `Show ${factors.length - 3} More`}
          </span>
          {isExpanded ? (
            <ChevronUp className="h-4 w-4" />
          ) : (
            <ChevronDown className="h-4 w-4" />
          )}
        </motion.button>
      )}

      {factors.length === 0 && (
        <div className="text-center py-8">
          <Key className="h-12 w-12 text-slate-600 mx-auto mb-3" />
          <div className="text-slate-400 text-sm">
            No key factors identified yet
          </div>
        </div>
      )}
    </div>
  );
};