import React from 'react';
import { motion } from 'framer-motion';
import { Plus, Minus, RotateCcw } from 'lucide-react';
import { InfoTooltip } from '../common/InfoTooltip';
import type { DCFAssumptions, DCFDefaults } from '../../types';

interface SimpleAssumptionsPanelProps {
  assumptions: DCFAssumptions;
  defaults: DCFDefaults;
  onUpdateAssumption: (key: keyof DCFAssumptions, value: number) => void;
  onResetToDefaults: () => void;
}

interface AssumptionRowProps {
  label: string;
  value: number;
  unit: string;
  tooltip: string;
  step: number;
  min: number;
  max: number;
  onChange: (value: number) => void;
  defaultValue?: number;
}

const AssumptionRow: React.FC<AssumptionRowProps> = ({
  label,
  value,
  unit,
  tooltip,
  step,
  min,
  max,
  onChange,
  defaultValue
}) => {
  const isModified = defaultValue !== undefined && Math.abs(value - defaultValue) > 0.01;

  const handleDecrease = () => {
    const newValue = Math.max(min, value - step);
    onChange(newValue);
  };

  const handleIncrease = () => {
    const newValue = Math.min(max, value + step);
    onChange(newValue);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = parseFloat(e.target.value) || 0;
    if (newValue >= min && newValue <= max) {
      onChange(newValue);
    }
  };

  return (
    <div className="bg-slate-700/30 rounded-lg p-4">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-2">
          <span className="text-sm font-medium text-slate-300">{label}</span>
          <InfoTooltip content={tooltip} />
          {isModified && (
            <div className="w-2 h-2 bg-primary-400 rounded-full" title="Modified from default" />
          )}
        </div>
        {defaultValue !== undefined && (
          <div className="text-xs text-slate-500">
            Default: {defaultValue.toFixed(1)}{unit}
          </div>
        )}
      </div>

      <div className="flex items-center space-x-3">
        <button
          onClick={handleDecrease}
          disabled={value <= min}
          className="p-2 bg-slate-600 hover:bg-slate-500 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg transition-colors"
        >
          <Minus className="h-4 w-4 text-slate-200" />
        </button>

        <div className="flex-1 text-center">
          <input
            type="number"
            value={value.toFixed(1)}
            onChange={handleInputChange}
            min={min}
            max={max}
            step={step}
            className="w-20 text-center bg-slate-800 border border-slate-600 rounded px-2 py-1 text-slate-100 text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          />
          <span className="ml-1 text-sm text-slate-400">{unit}</span>
        </div>

        <button
          onClick={handleIncrease}
          disabled={value >= max}
          className="p-2 bg-slate-600 hover:bg-slate-500 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg transition-colors"
        >
          <Plus className="h-4 w-4 text-slate-200" />
        </button>
      </div>

      <div className="mt-2 flex justify-between text-xs text-slate-500">
        <span>Min: {min}{unit}</span>
        <span>Max: {max}{unit}</span>
      </div>
    </div>
  );
};

export const SimpleAssumptionsPanel: React.FC<SimpleAssumptionsPanelProps> = ({
  assumptions,
  defaults,
  onUpdateAssumption,
  onResetToDefaults
}) => {
  const assumptions_config = [
    {
      key: 'revenue_growth_rate' as keyof DCFAssumptions,
      label: 'Revenue Growth Rate',
      unit: '%',
      tooltip: 'Expected annual revenue growth rate over the projection period. Higher growth rates indicate optimistic business expansion expectations.',
      step: 0.5,
      min: -10,
      max: 50,
      defaultValue: defaults.revenue_growth_rate
    },
    {
      key: 'ebitda_margin' as keyof DCFAssumptions,
      label: 'EBITDA Margin',
      unit: '%', 
      tooltip: 'Earnings Before Interest, Taxes, Depreciation, and Amortization as a percentage of revenue. Indicates operational efficiency.',
      step: 0.5,
      min: -50,
      max: 200,
      defaultValue: defaults.ebitda_margin
    },
    {
      key: 'tax_rate' as keyof DCFAssumptions,
      label: 'Tax Rate',
      unit: '%',
      tooltip: 'Effective corporate tax rate applied to earnings. For Indian companies, typically around 25-30%.',
      step: 0.5,
      min: 0,
      max: 50,
      defaultValue: defaults.tax_rate
    },
    {
      key: 'wacc' as keyof DCFAssumptions,
      label: 'WACC (Discount Rate)',
      unit: '%',
      tooltip: 'Weighted Average Cost of Capital - the rate used to discount future cash flows to present value. Higher WACC = lower valuation.',
      step: 0.5,
      min: 5,
      max: 25,
      defaultValue: defaults.wacc
    },
    {
      key: 'terminal_growth_rate' as keyof DCFAssumptions,
      label: 'Terminal Growth Rate',
      unit: '%',
      tooltip: 'Expected perpetual growth rate beyond the projection period. Should typically be close to GDP growth (3-5%).',
      step: 0.1,
      min: 0,
      max: 8,
      defaultValue: defaults.terminal_growth_rate
    }
  ];

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.5 }}
      className="space-y-6"
    >
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-slate-100">DCF Assumptions</h3>
        <button
          onClick={onResetToDefaults}
          className="flex items-center space-x-2 px-3 py-1.5 bg-slate-700 hover:bg-slate-600 text-slate-300 text-sm rounded-lg transition-colors"
        >
          <RotateCcw className="h-3 w-3" />
          <span>Reset to Defaults</span>
        </button>
      </div>

      <div className="space-y-4">
        {assumptions_config.map(config => {
          const currentValue = assumptions[config.key];
          return (
            <AssumptionRow
              key={config.key}
              label={config.label}
              value={typeof currentValue === 'number' ? currentValue : 0}
              unit={config.unit}
              tooltip={config.tooltip}
              step={config.step}
              min={config.min}
              max={config.max}
              onChange={(value) => onUpdateAssumption(config.key, value)}
              defaultValue={config.defaultValue}
            />
          );
        })}
      </div>

      <div className="text-xs text-slate-500 bg-slate-800/50 rounded-lg p-3">
        <p className="mb-1">💡 <strong>Tip:</strong> Adjust assumptions to see how they impact intrinsic value.</p>
        <p>• Higher growth rates increase valuation</p>
        <p>• Higher WACC (discount rate) decreases valuation</p>
        <p>• Changes update automatically after 500ms</p>
      </div>
    </motion.div>
  );
};