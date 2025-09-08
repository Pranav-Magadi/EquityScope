import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Settings, ChevronDown, ChevronUp, Info, Calculator } from 'lucide-react';
import type { SummaryResponse } from '../../types/summary';

interface DCFAssumptionsPanelProps {
  summaryData: SummaryResponse;
  ticker: string;
}

interface AssumptionItem {
  label: string;
  value: string;
  description: string;
  category: 'growth' | 'risk' | 'terminal' | 'sector';
}

export const DCFAssumptionsPanel: React.FC<DCFAssumptionsPanelProps> = ({
  summaryData,
  ticker
}) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [activeCategory, setActiveCategory] = useState<string>('all');

  // Generate sector-specific assumptions based on the sector
  const getSectorAssumptions = (sector: string, analysisMode: string): AssumptionItem[] => {
    const baseAssumptions: AssumptionItem[] = [
      {
        label: 'Risk-free Rate',
        value: '6.5%',
        description: '10-year Government Security yield used as risk-free rate',
        category: 'risk'
      },
      {
        label: 'Market Risk Premium',
        value: '8.0%',
        description: 'India equity market risk premium over risk-free rate',
        category: 'risk'
      },
      {
        label: 'Terminal Growth Rate',
        value: '3.0%',
        description: 'Long-term GDP growth assumption for terminal value',
        category: 'terminal'
      },
      {
        label: 'Forecast Period',
        value: '10 years',
        description: 'Explicit forecast period for DCF projections',
        category: 'growth'
      }
    ];

    // Add sector-specific assumptions
    const sectorSpecificAssumptions: Record<string, AssumptionItem[]> = {
      'BFSI': [
        {
          label: 'ROE Sustainability',
          value: '15-18%',
          description: 'Sustainable Return on Equity based on capital adequacy and growth',
          category: 'sector'
        },
        {
          label: 'Credit Growth',
          value: '12-15%',
          description: 'Assumed credit growth rate aligned with economic growth',
          category: 'sector'
        },
        {
          label: 'NIM Assumption',
          value: '3.0-3.5%',
          description: 'Net Interest Margin based on interest rate environment',
          category: 'sector'
        },
        {
          label: 'Cost/Income Ratio',
          value: '<45%',
          description: 'Operational efficiency target for mature banks',
          category: 'sector'
        }
      ],
      'PHARMA': [
        {
          label: 'R&D Investment',
          value: '8-12%',
          description: 'R&D as percentage of revenue for innovation-driven growth',
          category: 'sector'
        },
        {
          label: 'US Market Growth',
          value: '5-8%',
          description: 'US generics market growth assumption',
          category: 'sector'
        },
        {
          label: 'EBITDA Margin',
          value: '20-25%',
          description: 'Target EBITDA margin for pharmaceutical companies',
          category: 'sector'
        },
        {
          label: 'Patent Cliff Impact',
          value: '2-3% annual',
          description: 'Revenue impact from patent expirations',
          category: 'sector'
        }
      ],
      'IT': [
        {
          label: 'Revenue Growth',
          value: '8-12%',
          description: 'Organic revenue growth in IT services',
          category: 'sector'
        },
        {
          label: 'EBIT Margin',
          value: '22-26%',
          description: 'Operating margin target for IT services',
          category: 'sector'
        },
        {
          label: 'Onsite/Offshore Mix',
          value: '30:70',
          description: 'Revenue mix assumption for cost optimization',
          category: 'sector'
        },
        {
          label: 'Wage Inflation',
          value: '6-8%',
          description: 'Annual wage inflation for IT workforce',
          category: 'sector'
        }
      ],
      'REAL_ESTATE': [
        {
          label: 'Pre-sales Growth',
          value: '15-20%',
          description: 'Annual pre-sales value growth assumption',
          category: 'sector'
        },
        {
          label: 'Realization Rate',
          value: '85-90%',
          description: 'Average realization vs launched prices',
          category: 'sector'
        },
        {
          label: 'Debt/Equity Ratio',
          value: '<0.8x',
          description: 'Target leverage for financial stability',
          category: 'sector'
        },
        {
          label: 'Inventory Turnover',
          value: '1.2x',
          description: 'Asset turnover efficiency assumption',
          category: 'sector'
        }
      ]
    };

    const sectorKey = sector.toUpperCase().replace(' ', '_');
    const sectorAssumptions = sectorSpecificAssumptions[sectorKey] || [];
    
    // Add mode-specific assumptions
    if (analysisMode === 'agentic') {
      baseAssumptions.push({
        label: 'AI Enhancement',
        value: 'Management Insights',
        description: 'AI-powered analysis of management guidance and market sentiment',
        category: 'growth'
      });
    }

    return [...baseAssumptions, ...sectorAssumptions];
  };

  const assumptions = getSectorAssumptions(summaryData.sector, summaryData.analysis_mode);
  
  const categoryColors: Record<string, string> = {
    growth: 'text-green-400',
    risk: 'text-orange-400', 
    terminal: 'text-blue-400',
    sector: 'text-purple-400'
  };

  const categoryLabels: Record<string, string> = {
    growth: 'Growth',
    risk: 'Risk',
    terminal: 'Terminal',
    sector: 'Sector-Specific'
  };

  const filteredAssumptions = activeCategory === 'all' 
    ? assumptions 
    : assumptions.filter(a => a.category === activeCategory);

  const categories = Array.from(new Set(assumptions.map(a => a.category)));

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-slate-800/50 rounded-lg border border-slate-700/50 overflow-hidden"
    >
      {/* Header */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full px-4 py-3 flex items-center justify-between hover:bg-slate-700/30 transition-colors"
      >
        <div className="flex items-center space-x-3">
          <Settings className="h-4 w-4 text-slate-400" />
          <span className="font-medium text-slate-200">DCF Key Assumptions</span>
          <span className="text-xs text-slate-500">
            ({summaryData.sector} • {summaryData.analysis_mode} mode)
          </span>
        </div>
        {isExpanded ? (
          <ChevronUp className="h-4 w-4 text-slate-400" />
        ) : (
          <ChevronDown className="h-4 w-4 text-slate-400" />
        )}
      </button>

      {/* Expandable Content */}
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="border-t border-slate-700/50"
          >
            <div className="p-4">
              {/* Category Filter */}
              <div className="flex items-center space-x-2 mb-4">
                <button
                  onClick={() => setActiveCategory('all')}
                  className={`px-3 py-1 rounded-md text-xs font-medium transition-colors ${
                    activeCategory === 'all'
                      ? 'bg-primary-500/20 text-primary-300'
                      : 'bg-slate-700/50 text-slate-400 hover:text-slate-300'
                  }`}
                >
                  All ({assumptions.length})
                </button>
                {categories.map(category => (
                  <button
                    key={category}
                    onClick={() => setActiveCategory(category)}
                    className={`px-3 py-1 rounded-md text-xs font-medium transition-colors ${
                      activeCategory === category
                        ? 'bg-primary-500/20 text-primary-300'
                        : 'bg-slate-700/50 text-slate-400 hover:text-slate-300'
                    }`}
                  >
                    {categoryLabels[category]} ({assumptions.filter(a => a.category === category).length})
                  </button>
                ))}
              </div>

              {/* Assumptions Grid */}
              <div className="space-y-3">
                {filteredAssumptions.map((assumption, index) => (
                  <motion.div
                    key={`${assumption.category}-${index}`}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.05 }}
                    className="bg-slate-900/30 rounded-lg p-3"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2">
                          <span className="font-medium text-slate-200">{assumption.label}</span>
                          <span className={`text-xs px-2 py-0.5 rounded-full ${categoryColors[assumption.category]} bg-current/10`}>
                            {categoryLabels[assumption.category]}
                          </span>
                        </div>
                        <div className="mt-1 text-sm text-slate-400">{assumption.description}</div>
                      </div>
                      <div className="text-right ml-4">
                        <div className="font-mono text-sm font-medium text-slate-100">
                          {assumption.value}
                        </div>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>

              {/* Footer Note */}
              <div className="mt-4 pt-3 border-t border-slate-700/30">
                <div className="flex items-start space-x-2 text-xs text-slate-500">
                  <Info className="h-3 w-3 mt-0.5 flex-shrink-0" />
                  <div>
                    <span className="font-medium">Note:</span> These assumptions are based on {summaryData.sector} sector benchmarks 
                    and current market conditions. {summaryData.analysis_mode === 'agentic' ? 'AI-enhanced analysis incorporates management guidance and sentiment factors.' : 'Rule-based analysis uses standard financial models.'}
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};