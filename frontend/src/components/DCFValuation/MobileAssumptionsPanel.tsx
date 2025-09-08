import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Info, RotateCcw, Plus, Minus, ChevronDown, ChevronUp } from 'lucide-react';
import type { DCFAssumptions, DCFDefaults } from '../../types';
import { DCFUtils } from '../../utils/dcf';

interface MobileAssumptionsPanelProps {
  assumptions: DCFAssumptions;
  defaults: DCFDefaults;
  onUpdateAssumption: (key: keyof DCFAssumptions, value: number) => void;
  onResetToDefaults: () => void;
}

interface MobileAssumptionControlProps {
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

const MobileAssumptionControl: React.FC<MobileAssumptionControlProps> = ({
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
  const [showTooltip, setShowTooltip] = useState(false);
  const isModified = defaultValue !== undefined && Math.abs(value - defaultValue) > 0.01;

  const handleIncrement = () => {
    const newValue = Math.min(max, value + step);
    onChange(parseFloat(newValue.toFixed(1)));
  };

  const handleDecrement = () => {
    const newValue = Math.max(min, value - step);
    onChange(parseFloat(newValue.toFixed(1)));
  };

  const handleDirectInput = (inputValue: string) => {
    const numValue = parseFloat(inputValue);
    if (!isNaN(numValue) && numValue >= min && numValue <= max) {
      onChange(numValue);
    }
  };

  return (
    <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
      {/* Header with label and info */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-2">
          <label className="text-sm font-medium text-slate-300">{label}</label>
          <div className="relative">
            <Info
              className="h-4 w-4 text-slate-400 cursor-help"
              onTouchStart={() => setShowTooltip(true)}
              onTouchEnd={() => setTimeout(() => setShowTooltip(false), 3000)}
              onClick={() => setShowTooltip(!showTooltip)}
            />
            <AnimatePresence>
              {showTooltip && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.95, y: -10 }}
                  animate={{ opacity: 1, scale: 1, y: 0 }}
                  exit={{ opacity: 0, scale: 0.95, y: -10 }}
                  className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 w-64 bg-slate-900 text-slate-200 text-xs rounded-lg p-3 border border-slate-700 z-50 shadow-lg"
                >
                  {tooltip}
                  <div className="absolute top-full left-1/2 transform -translate-x-1/2 w-2 h-2 bg-slate-900 border-r border-b border-slate-700 rotate-45 -mt-1" />
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
        {isModified && (
          <div className="w-2 h-2 bg-primary-400 rounded-full" title="Modified from default" />
        )}
      </div>

      {/* Mobile Control Interface */}
      <div className="flex items-center space-x-3">
        {/* Decrease Button */}
        <motion.button
          whileTap={{ scale: 0.95 }}
          onClick={handleDecrement}
          disabled={value <= min}
          className="flex-shrink-0 w-10 h-10 bg-slate-700 hover:bg-slate-600 disabled:bg-slate-800 disabled:opacity-50 rounded-lg flex items-center justify-center text-slate-300 transition-colors touch-manipulation"
        >
          <Minus className="h-5 w-5" />
        </motion.button>

        {/* Value Display and Input */}
        <div className="flex-1 flex flex-col items-center space-y-1">
          <input
            type="number"
            value={value.toFixed(1)}
            onChange={(e) => handleDirectInput(e.target.value)}
            min={min}
            max={max}
            step={step}
            className="w-full text-center text-lg font-mono bg-slate-900 border border-slate-600 rounded-lg px-3 py-2 text-slate-200 focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
          />
          <span className="text-xs text-slate-400">{suffix}</span>
        </div>

        {/* Increase Button */}
        <motion.button
          whileTap={{ scale: 0.95 }}
          onClick={handleIncrement}
          disabled={value >= max}
          className="flex-shrink-0 w-10 h-10 bg-slate-700 hover:bg-slate-600 disabled:bg-slate-800 disabled:opacity-50 rounded-lg flex items-center justify-center text-slate-300 transition-colors touch-manipulation"
        >
          <Plus className="h-5 w-5" />
        </motion.button>
      </div>

      {/* Range Indicator */}
      <div className="mt-3">
        <div className="relative h-2 bg-slate-700 rounded-full overflow-hidden">
          <div
            className="absolute left-0 top-0 h-full bg-gradient-to-r from-primary-500 to-primary-400 rounded-full transition-all duration-300"
            style={{ width: `${((value - min) / (max - min)) * 100}%` }}
          />
          {defaultValue !== undefined && (
            <div
              className="absolute top-0 w-1 h-2 bg-slate-300 rounded-full transform -translate-x-1/2"
              style={{ left: `${((defaultValue - min) / (max - min)) * 100}%` }}
              title={`Default: ${defaultValue.toFixed(1)}${suffix}`}
            />
          )}
        </div>
        <div className="flex justify-between text-xs text-slate-500 mt-1">
          <span>{min}{suffix}</span>
          <span>{max}{suffix}</span>
        </div>
      </div>

      {/* Quick Presets for Common Values */}
      {label === 'Revenue Growth Rate' && (
        <div className="flex flex-wrap gap-2 mt-3">
          {[5, 10, 15, 20].map((preset) => (
            <motion.button
              key={preset}
              whileTap={{ scale: 0.95 }}
              onClick={() => onChange(preset)}
              className={`px-3 py-1 text-xs rounded-full transition-colors ${
                Math.abs(value - preset) < 0.1
                  ? 'bg-primary-500 text-white'
                  : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
              }`}
            >
              {preset}%
            </motion.button>
          ))}
        </div>
      )}

      {label === 'WACC (Discount Rate)' && (
        <div className="flex flex-wrap gap-2 mt-3">
          {[8, 10, 12, 15].map((preset) => (
            <motion.button
              key={preset}
              whileTap={{ scale: 0.95 }}
              onClick={() => onChange(preset)}
              className={`px-3 py-1 text-xs rounded-full transition-colors ${
                Math.abs(value - preset) < 0.1
                  ? 'bg-primary-500 text-white'
                  : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
              }`}
            >
              {preset}%
            </motion.button>
          ))}
        </div>
      )}
    </div>
  );
};

export const MobileAssumptionsPanel: React.FC<MobileAssumptionsPanelProps> = ({
  assumptions,
  defaults,
  onUpdateAssumption,
  onResetToDefaults
}) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const validation = DCFUtils.validateAssumptions(assumptions);

  const assumptionConfigs = [
    {
      key: 'revenue_growth_rate' as keyof DCFAssumptions,
      label: 'Revenue Growth Rate',
      min: -10,
      max: 30,
      step: 0.5,
      suffix: '%',
      tooltip: DCFUtils.getAssumptionTooltip('revenue_growth_rate'),
      defaultValue: defaults.revenue_growth_rate
    },
    {
      key: 'ebitda_margin' as keyof DCFAssumptions,
      label: 'EBITDA Margin',
      min: -5,
      max: 40,
      step: 0.5,
      suffix: '%',
      tooltip: DCFUtils.getAssumptionTooltip('ebitda_margin'),
      defaultValue: defaults.ebitda_margin
    },
    {
      key: 'tax_rate' as keyof DCFAssumptions,
      label: 'Effective Tax Rate',
      min: 0,
      max: 50,
      step: 0.5,
      suffix: '%',
      tooltip: DCFUtils.getAssumptionTooltip('tax_rate'),
      defaultValue: defaults.tax_rate
    },
    {
      key: 'wacc' as keyof DCFAssumptions,
      label: 'WACC (Discount Rate)',
      min: 5,
      max: 25,
      step: 0.5,
      suffix: '%',
      tooltip: DCFUtils.getAssumptionTooltip('wacc'),
      defaultValue: defaults.wacc
    },
    {
      key: 'terminal_growth_rate' as keyof DCFAssumptions,
      label: 'Terminal Growth Rate',
      min: 0,
      max: 8,
      step: 0.25,
      suffix: '%',
      tooltip: DCFUtils.getAssumptionTooltip('terminal_growth_rate'),
      defaultValue: defaults.terminal_growth_rate
    }
  ];

  const modifiedCount = assumptionConfigs.filter(config => 
    Math.abs((assumptions[config.key] ?? config.defaultValue) - config.defaultValue) > 0.01
  ).length;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="bg-slate-900/50 backdrop-blur-sm rounded-xl border border-slate-700"
    >
      {/* Collapsible Header */}
      <div className="p-4 border-b border-slate-700">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <h3 className="text-lg font-semibold text-slate-100">Key Assumptions</h3>
            {modifiedCount > 0 && (
              <span className="bg-primary-500 text-white text-xs px-2 py-1 rounded-full">
                {modifiedCount} modified
              </span>
            )}
          </div>
          <div className="flex items-center space-x-2">
            <motion.button
              whileTap={{ scale: 0.95 }}
              onClick={onResetToDefaults}
              className="flex items-center space-x-1 text-sm text-slate-400 hover:text-primary-400 transition-colors px-3 py-1 rounded-lg hover:bg-slate-800"
            >
              <RotateCcw className="h-4 w-4" />
              <span>Reset</span>
            </motion.button>
            <motion.button
              whileTap={{ scale: 0.95 }}
              onClick={() => setIsExpanded(!isExpanded)}
              className="flex items-center justify-center w-8 h-8 text-slate-400 hover:text-slate-200 transition-colors rounded-lg hover:bg-slate-800"
            >
              {isExpanded ? <ChevronUp className="h-5 w-5" /> : <ChevronDown className="h-5 w-5" />}
            </motion.button>
          </div>
        </div>

        {/* Quick Summary when collapsed */}
        {!isExpanded && (
          <div className="mt-3 grid grid-cols-2 gap-2 text-xs">
            <div className="flex justify-between">
              <span className="text-slate-400">Growth:</span>
              <span className="text-slate-200 font-mono">
                {(assumptions.revenue_growth_rate ?? defaults.revenue_growth_rate).toFixed(1)}%
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">WACC:</span>
              <span className="text-slate-200 font-mono">
                {(assumptions.wacc ?? defaults.wacc).toFixed(1)}%
              </span>
            </div>
          </div>
        )}
      </div>

      {/* Expandable Content */}
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="overflow-hidden"
          >
            <div className="p-4 space-y-4">
              {/* Validation Errors */}
              {!validation.isValid && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="bg-red-900/20 border border-red-500/30 rounded-lg p-3"
                >
                  <div className="text-sm text-red-400 font-medium mb-2">⚠ Validation Errors:</div>
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

              {/* Mobile Assumption Controls */}
              <div className="space-y-4">
                {assumptionConfigs.map((config, index) => (
                  <motion.div
                    key={config.key}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.3, delay: index * 0.1 }}
                  >
                    <MobileAssumptionControl
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

              {/* Tips for Mobile Users */}
              <div className="bg-slate-800/30 rounded-lg p-3 border border-slate-700/50">
                <h4 className="text-sm font-medium text-slate-300 mb-2">📱 Mobile Tips</h4>
                <ul className="text-xs text-slate-400 space-y-1">
                  <li>• Tap +/- buttons for precise adjustments</li>
                  <li>• Tap the value to type directly</li>
                  <li>• Use preset buttons for common values</li>
                  <li>• Touch and hold ℹ️ for detailed explanations</li>
                </ul>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};