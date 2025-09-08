import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Calculator, TrendingUp, Building, ChevronDown, ChevronUp } from 'lucide-react';

interface ThreeLensAnalysisProps {
  valuation: string;
  market: string;
  fundamentals: string;
}

type ActiveLens = 'valuation' | 'market' | 'fundamentals' | null;

export const ThreeLensAnalysis: React.FC<ThreeLensAnalysisProps> = ({
  valuation,
  market,
  fundamentals
}) => {
  const [activeLens, setActiveLens] = useState<ActiveLens>('valuation');

  const lenses = [
    {
      id: 'valuation' as const,
      title: 'Valuation Insights',
      icon: Calculator,
      content: valuation,
      color: 'blue',
      description: 'DCF analysis and price multiples'
    },
    {
      id: 'market' as const,
      title: 'Market Signals',
      icon: TrendingUp,
      content: market,
      color: 'green',
      description: 'Technical indicators and momentum'
    },
    {
      id: 'fundamentals' as const,
      title: 'Business & Macro Fundamentals',
      icon: Building,
      content: fundamentals,
      color: 'purple',
      description: 'Financial health and sector dynamics'
    }
  ];

  const getColorClasses = (color: string, isActive: boolean) => {
    const baseClasses = {
      blue: {
        button: isActive 
          ? 'bg-blue-600 text-white border-blue-500' 
          : 'bg-blue-900/20 text-blue-300 border-blue-600/30 hover:bg-blue-800/30',
        content: 'border-blue-500/30 bg-blue-900/10'
      },
      green: {
        button: isActive 
          ? 'bg-green-600 text-white border-green-500' 
          : 'bg-green-900/20 text-green-300 border-green-600/30 hover:bg-green-800/30',
        content: 'border-green-500/30 bg-green-900/10'
      },
      purple: {
        button: isActive 
          ? 'bg-purple-600 text-white border-purple-500' 
          : 'bg-purple-900/20 text-purple-300 border-purple-600/30 hover:bg-purple-800/30',
        content: 'border-purple-500/30 bg-purple-900/10'
      }
    };
    return baseClasses[color as keyof typeof baseClasses];
  };

  return (
    <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-slate-100 mb-2">
          Three Lens Analysis
        </h3>
        <p className="text-sm text-slate-400">
          Comprehensive assessment across valuation, market signals, and fundamentals
        </p>
      </div>

      {/* Lens Selection Tabs */}
      <div className="flex flex-wrap gap-3 mb-6">
        {lenses.map((lens) => {
          const isActive = activeLens === lens.id;
          const colorClasses = getColorClasses(lens.color, isActive);
          const Icon = lens.icon;

          return (
            <motion.button
              key={lens.id}
              onClick={() => setActiveLens(activeLens === lens.id ? null : lens.id)}
              className={`flex items-center space-x-2 px-4 py-3 rounded-lg border transition-all duration-200 ${colorClasses.button}`}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <Icon className="h-4 w-4" />
              <div className="text-left">
                <div className="text-sm font-medium">{lens.title}</div>
                <div className="text-xs opacity-75">{lens.description}</div>
              </div>
              {isActive ? (
                <ChevronUp className="h-4 w-4" />
              ) : (
                <ChevronDown className="h-4 w-4" />
              )}
            </motion.button>
          );
        })}
      </div>

      {/* Active Lens Content */}
      <AnimatePresence mode="wait">
        {activeLens && (
          <motion.div
            key={activeLens}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3 }}
            className={`p-4 rounded-lg border ${getColorClasses(
              lenses.find(l => l.id === activeLens)?.color || 'blue', 
              false
            ).content}`}
          >
            <div className="flex items-center space-x-2 mb-3">
              {React.createElement(
                lenses.find(l => l.id === activeLens)?.icon || Calculator,
                { className: "h-5 w-5" }
              )}
              <h4 className="font-semibold text-slate-200">
                {lenses.find(l => l.id === activeLens)?.title}
              </h4>
            </div>
            <div className="text-slate-300 text-sm leading-relaxed whitespace-pre-line">
              {lenses.find(l => l.id === activeLens)?.content || 'Analysis pending...'}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Summary View when no lens is active */}
      {!activeLens && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="grid grid-cols-1 md:grid-cols-3 gap-4"
        >
          {lenses.map((lens) => {
            const Icon = lens.icon;
            const colorClasses = getColorClasses(lens.color, false);
            
            return (
              <div
                key={lens.id}
                className={`p-4 rounded-lg border ${colorClasses.content} cursor-pointer hover:opacity-80 transition-opacity`}
                onClick={() => setActiveLens(lens.id)}
              >
                <div className="flex items-center space-x-2 mb-2">
                  <Icon className="h-4 w-4" />
                  <div className="font-medium text-slate-200 text-sm">
                    {lens.title}
                  </div>
                </div>
                <div className="text-xs text-slate-400 line-clamp-3">
                  {lens.content?.slice(0, 100) || 'Analysis pending...'}
                  {lens.content && lens.content.length > 100 && '...'}
                </div>
              </div>
            );
          })}
        </motion.div>
      )}
    </div>
  );
};