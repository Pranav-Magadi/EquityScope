import React from 'react';
import { motion } from 'framer-motion';
import { Grid3x3, Info } from 'lucide-react';
import type { SensitivityAnalysis, DCFValuation } from '../../types';
import { DCFUtils } from '../../utils/dcf';

interface SensitivityAnalysisProps {
  sensitivity: SensitivityAnalysis;
  baseValuation: DCFValuation;
}

export const SensitivityAnalysisComponent: React.FC<SensitivityAnalysisProps> = ({
  sensitivity,
  baseValuation
}) => {
  const baseValue = baseValuation.intrinsic_value_per_share;

  const getCellColor = (value: number): string => {
    return DCFUtils.getSensitivityColor(value, baseValue);
  };

  const getPercentDifference = (value: number): string => {
    const diff = ((value - baseValue) / baseValue) * 100;
    return `${diff > 0 ? '+' : ''}${diff.toFixed(1)}%`;
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.6 }}
      className="bg-slate-800/50 rounded-lg p-4"
    >
      <div className="flex items-center space-x-2 mb-4">
        <Grid3x3 className="h-5 w-5 text-slate-400" />
        <h4 className="text-md font-medium text-slate-300">Sensitivity Analysis</h4>
        <div className="relative group">
          <Info className="h-4 w-4 text-slate-400 cursor-help" />
          <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 w-72 bg-slate-900 text-slate-200 text-xs rounded-lg p-3 border border-slate-700 opacity-0 group-hover:opacity-100 transition-opacity z-50 pointer-events-none">
            Shows how intrinsic value changes with variations in WACC (discount rate) and terminal growth rate.
            Green indicates higher valuations, red indicates lower valuations relative to base case.
          </div>
        </div>
      </div>

      <div className="space-y-4">
        {/* Base Case Highlight */}
        <div className="bg-primary-900/20 border border-primary-500/30 rounded-lg p-3">
          <div className="text-sm text-slate-400 mb-1">Base Case Valuation</div>
          <div className="text-lg font-bold text-primary-400">
            ₹{baseValue.toFixed(2)}
          </div>
          <div className="text-xs text-slate-400">
            WACC: {baseValuation.assumptions.wacc.toFixed(1)}%, 
            Terminal Growth: {baseValuation.assumptions.terminal_growth_rate.toFixed(1)}%
          </div>
        </div>

        {/* Sensitivity Grid */}
        <div className="overflow-x-auto">
          <div className="min-w-max">
            {/* Headers */}
            <div className="grid grid-cols-6 gap-1 mb-2">
              <div className="text-xs text-slate-400 p-2 text-center font-medium">
                WACC \ Term. Growth
              </div>
              {sensitivity.terminal_growth_range.map((rate) => (
                <div key={rate} className="text-xs text-slate-400 p-2 text-center font-medium">
                  {rate.toFixed(1)}%
                </div>
              ))}
            </div>

            {/* Grid Rows */}
            {sensitivity.wacc_range.map((wacc, rowIndex) => (
              <motion.div
                key={wacc}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3, delay: 0.1 + rowIndex * 0.05 }}
                className="grid grid-cols-6 gap-1 mb-1"
              >
                {/* WACC Label */}
                <div className="text-xs text-slate-400 p-2 text-center font-medium bg-slate-700/30 rounded">
                  {wacc.toFixed(1)}%
                </div>
                
                {/* Sensitivity Values */}
                {sensitivity.sensitivity_matrix[rowIndex]?.map((value, colIndex) => {
                  const isBaseCase = 
                    wacc === baseValuation.assumptions.wacc && 
                    sensitivity.terminal_growth_range[colIndex] === baseValuation.assumptions.terminal_growth_rate;
                  
                  return (
                    <div
                      key={colIndex}
                      className={`
                        sensitivity-cell text-center p-2 rounded transition-all duration-200 hover:scale-105 cursor-pointer
                        ${isBaseCase ? 'ring-2 ring-primary-400' : ''}
                        ${getCellColor(value)}
                      `}
                      title={`WACC: ${wacc.toFixed(1)}%, Terminal Growth: ${sensitivity.terminal_growth_range[colIndex]?.toFixed(1)}%`}
                    >
                      <div className="font-mono text-xs">
                        ₹{value.toFixed(0)}
                      </div>
                      <div className="text-xs opacity-75">
                        {getPercentDifference(value)}
                      </div>
                    </div>
                  );
                })}
              </motion.div>
            ))}
          </div>
        </div>

        {/* Legend */}
        <div className="flex items-center justify-center space-x-6 text-xs">
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-green-900/30 border border-green-500/30 rounded"></div>
            <span className="text-slate-400">Higher Valuation</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-slate-800 border border-slate-600 rounded"></div>
            <span className="text-slate-400">Similar to Base</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-red-900/30 border border-red-500/30 rounded"></div>
            <span className="text-slate-400">Lower Valuation</span>
          </div>
        </div>

        {/* Key Insights */}
        <div className="bg-slate-700/30 rounded-lg p-3">
          <div className="text-sm font-medium text-slate-300 mb-2">Key Insights</div>
          <div className="space-y-2 text-xs text-slate-400">
            <div className="flex items-start space-x-2">
              <div className="w-1 h-1 bg-slate-400 rounded-full mt-1.5 flex-shrink-0" />
              <span>
                Higher WACC (discount rate) reduces valuation as future cash flows are discounted more heavily
              </span>
            </div>
            <div className="flex items-start space-x-2">
              <div className="w-1 h-1 bg-slate-400 rounded-full mt-1.5 flex-shrink-0" />
              <span>
                Higher terminal growth rate increases valuation through higher terminal value
              </span>
            </div>
            <div className="flex items-start space-x-2">
              <div className="w-1 h-1 bg-slate-400 rounded-full mt-1.5 flex-shrink-0" />
              <span>
                The model is most sensitive to changes in discount rate assumptions
              </span>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
};