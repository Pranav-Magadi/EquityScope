import React from 'react';
import { motion } from 'framer-motion';
import { Info, RotateCcw } from 'lucide-react';
import type { DCFAssumptions, DCFDefaults } from '../../types';
import { DCFUtils } from '../../utils/dcf';

interface AssumptionsPanelProps {
  assumptions: DCFAssumptions;
  defaults: DCFDefaults;
  onUpdateAssumption: (key: keyof DCFAssumptions, value: number) => void;
  onResetToDefaults: () => void;
}

interface SliderInputProps {
  label: string;
  value: number;
  min: number;
  max: number;
  step: number;
  suffix: string;
  tooltip: string;
  onChange: (value: number) => void;
  defaultValue?: number;
}

const SliderInput: React.FC<SliderInputProps> = ({
  label,
  value,
  min,
  max,
  step,
  suffix,
  tooltip,
  onChange,
  defaultValue
}) => {
  const [showTooltip, setShowTooltip] = React.useState(false);
  const isModified = defaultValue !== undefined && Math.abs(value - defaultValue) > 0.01;

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <label className="text-sm font-medium text-slate-300">{label}</label>
          <div className="relative">
            <Info
              className="h-3 w-3 text-slate-400 cursor-help"
              onMouseEnter={() => setShowTooltip(true)}
              onMouseLeave={() => setShowTooltip(false)}
            />
            {showTooltip && (
              <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 w-64 bg-slate-900 text-slate-200 text-xs rounded-lg p-2 border border-slate-700 z-50">
                {tooltip}
                <div className="absolute top-full left-1/2 transform -translate-x-1/2 w-2 h-2 bg-slate-900 border-r border-b border-slate-700 rotate-45 -mt-1" />
              </div>
            )}
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <span className={`text-sm font-mono ${isModified ? 'text-primary-400' : 'text-slate-300'}`}>
            {value.toFixed(1)}{suffix}
          </span>
          {isModified && (
            <div className="w-2 h-2 bg-primary-400 rounded-full" title="Modified from default" />
          )}
        </div>
      </div>
      
      <div className="relative">
        <input
          type="range"
          min={min}
          max={max}
          step={step}
          value={value}
          onChange={(e) => onChange(parseFloat(e.target.value))}
          className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer slider"
          style={{
            background: `linear-gradient(to right, #0ea5e9 0%, #0ea5e9 ${((value - min) / (max - min)) * 100}%, #475569 ${((value - min) / (max - min)) * 100}%, #475569 100%)`
          }}
        />
        {defaultValue !== undefined && (
          <div
            className="absolute top-0 w-1 h-2 bg-slate-400 rounded-full transform -translate-x-1/2"
            style={{ left: `${((defaultValue - min) / (max - min)) * 100}%` }}
            title={`Default: ${defaultValue.toFixed(1)}${suffix}`}
          />
        )}
      </div>

      <div className="flex justify-between text-xs text-slate-500">
        <span>{min}{suffix}</span>
        <span>{max}{suffix}</span>
      </div>
    </div>
  );
};

export const AssumptionsPanel: React.FC<AssumptionsPanelProps> = ({
  assumptions,
  defaults,
  onUpdateAssumption,
  onResetToDefaults
}) => {
  const validation = DCFUtils.validateAssumptions(assumptions);

  const assumptionConfigs = [
    {
      key: 'revenue_growth_rate' as keyof DCFAssumptions,
      label: 'Revenue Growth Rate',
      min: -10,
      max: 30,
      step: 0.1,
      suffix: '%',
      tooltip: DCFUtils.getAssumptionTooltip('revenue_growth_rate'),
      defaultValue: defaults.revenue_growth_rate
    },
    {
      key: 'ebitda_margin' as keyof DCFAssumptions,
      label: 'EBITDA Margin',
      min: -5,
      max: 40,
      step: 0.1,
      suffix: '%',
      tooltip: DCFUtils.getAssumptionTooltip('ebitda_margin'),
      defaultValue: defaults.ebitda_margin
    },
    {
      key: 'tax_rate' as keyof DCFAssumptions,
      label: 'Effective Tax Rate',
      min: 0,
      max: 50,
      step: 0.1,
      suffix: '%',
      tooltip: DCFUtils.getAssumptionTooltip('tax_rate'),
      defaultValue: defaults.tax_rate
    },
    {
      key: 'wacc' as keyof DCFAssumptions,
      label: 'WACC (Discount Rate)',
      min: 5,
      max: 25,
      step: 0.1,
      suffix: '%',
      tooltip: DCFUtils.getAssumptionTooltip('wacc'),
      defaultValue: defaults.wacc
    },
    {
      key: 'terminal_growth_rate' as keyof DCFAssumptions,
      label: 'Terminal Growth Rate',
      min: 0,
      max: 8,
      step: 0.1,
      suffix: '%',
      tooltip: DCFUtils.getAssumptionTooltip('terminal_growth_rate'),
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
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-slate-100">Key Assumptions</h3>
        <button
          onClick={onResetToDefaults}
          className="flex items-center space-x-2 text-sm text-slate-400 hover:text-primary-400 transition-colors"
          title="Reset to default values"
        >
          <RotateCcw className="h-4 w-4" />
          <span>Reset</span>
        </button>
      </div>

      {/* Validation Errors */}
      {!validation.isValid && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          className="bg-red-900/20 border border-red-500/30 rounded-lg p-3"
        >
          <div className="text-sm text-red-400 font-medium mb-2">Validation Errors:</div>
          <ul className="text-xs text-red-300 space-y-1">
            {validation.errors.map((error, index) => (
              <li key={index} className="flex items-start space-x-2">
                <span className="w-1 h-1 bg-red-400 rounded-full mt-1.5 flex-shrink-0" />
                <span>{error}</span>
              </li>
            ))}
          </ul>
        </motion.div>
      )}

      {/* Assumption Sliders */}
      <div className="space-y-6">
        {assumptionConfigs.map((config, index) => (
          <motion.div
            key={config.key}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: index * 0.05 }}
          >
            <SliderInput
              label={config.label}
              value={assumptions[config.key] ?? config.defaultValue}
              min={config.min}
              max={config.max}
              step={config.step}
              suffix={config.suffix}
              tooltip={config.tooltip}
              defaultValue={config.defaultValue}
              onChange={(value) => onUpdateAssumption(config.key, value)}
            />
          </motion.div>
        ))}
      </div>

      {/* Rationale */}
      <div className="border-t border-slate-700 pt-4">
        <h4 className="text-sm font-medium text-slate-300 mb-3">Default Rationale</h4>
        <div className="space-y-2">
          {Object.entries(defaults.rationale).map(([key, rationale]) => (
            <div key={key} className="text-xs text-slate-400">
              <span className="font-medium capitalize">{key.replace('_', ' ')}:</span> {rationale}
            </div>
          ))}
        </div>
      </div>
    </motion.div>
  );
};