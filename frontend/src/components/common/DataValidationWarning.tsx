import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { AlertTriangle, Info, TrendingDown, TrendingUp, AlertCircle } from 'lucide-react';

interface ValidationRule {
  field: string;
  value: number;
  min?: number;
  max?: number;
  warning?: string;
  severity: 'info' | 'warning' | 'error';
  recommendation?: string;
}

interface DataValidationWarningProps {
  validationRules: ValidationRule[];
  className?: string;
  showDetails?: boolean;
}

interface SpecificWarningProps {
  type: 'growth_rate' | 'margin' | 'discount_rate' | 'terminal_growth' | 'debt_ratio';
  value: number;
  className?: string;
  onAdjust?: (suggestedValue: number) => void;
}

// Main validation warning component
export const DataValidationWarning: React.FC<DataValidationWarningProps> = ({
  validationRules,
  className = '',
  showDetails = true
}) => {
  const errors = validationRules.filter(rule => rule.severity === 'error');
  const warnings = validationRules.filter(rule => rule.severity === 'warning');
  const infos = validationRules.filter(rule => rule.severity === 'info');

  if (validationRules.length === 0) return null;

  const getIcon = (severity: string) => {
    switch (severity) {
      case 'error':
        return <AlertTriangle className="h-4 w-4 text-red-400" />;
      case 'warning':
        return <AlertCircle className="h-4 w-4 text-yellow-400" />;
      case 'info':
        return <Info className="h-4 w-4 text-blue-400" />;
      default:
        return <Info className="h-4 w-4 text-slate-400" />;
    }
  };

  const getStyles = (severity: string) => {
    switch (severity) {
      case 'error':
        return 'bg-red-900/20 border-red-500/30 text-red-300';
      case 'warning':
        return 'bg-yellow-900/20 border-yellow-500/30 text-yellow-300';
      case 'info':
        return 'bg-blue-900/20 border-blue-500/30 text-blue-300';
      default:
        return 'bg-slate-800/50 border-slate-600 text-slate-300';
    }
  };

  return (
    <div className={`space-y-3 ${className}`}>
      {errors.length > 0 && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          className={`rounded-lg border p-3 ${getStyles('error')}`}
        >
          <div className="flex items-start space-x-2">
            {getIcon('error')}
            <div className="flex-1">
              <div className="font-medium text-sm mb-1">Validation Errors</div>
              {showDetails && (
                <ul className="text-xs space-y-1">
                  {errors.map((error, index) => (
                    <li key={index} className="flex items-start space-x-1">
                      <span className="w-1 h-1 bg-red-400 rounded-full mt-1.5 flex-shrink-0" />
                      <span>{error.warning}</span>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>
        </motion.div>
      )}

      {warnings.length > 0 && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          className={`rounded-lg border p-3 ${getStyles('warning')}`}
        >
          <div className="flex items-start space-x-2">
            {getIcon('warning')}
            <div className="flex-1">
              <div className="font-medium text-sm mb-1">
                Assumptions May Be Optimistic ({warnings.length})
              </div>
              {showDetails && (
                <ul className="text-xs space-y-1">
                  {warnings.map((warning, index) => (
                    <li key={index} className="flex items-start space-x-1">
                      <span className="w-1 h-1 bg-yellow-400 rounded-full mt-1.5 flex-shrink-0" />
                      <span>{warning.warning}</span>
                      {warning.recommendation && (
                        <span className="text-yellow-200 ml-2">
                          → {warning.recommendation}
                        </span>
                      )}
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>
        </motion.div>
      )}

      {infos.length > 0 && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          className={`rounded-lg border p-3 ${getStyles('info')}`}
        >
          <div className="flex items-start space-x-2">
            {getIcon('info')}
            <div className="flex-1">
              <div className="font-medium text-sm mb-1">Additional Insights</div>
              {showDetails && (
                <ul className="text-xs space-y-1">
                  {infos.map((info, index) => (
                    <li key={index} className="flex items-start space-x-1">
                      <span className="w-1 h-1 bg-blue-400 rounded-full mt-1.5 flex-shrink-0" />
                      <span>{info.warning}</span>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>
        </motion.div>
      )}
    </div>
  );
};

// Specific warning components for different metrics
export const GrowthRateWarning: React.FC<SpecificWarningProps> = ({
  value,
  className = '',
  onAdjust
}) => {
  const getWarning = () => {
    if (value > 25) {
      return {
        severity: 'error' as const,
        message: `${value.toFixed(1)}% growth rate is extremely optimistic`,
        suggestion: 20,
        explanation: 'Very few large companies sustain >25% growth long-term'
      };
    } else if (value > 20) {
      return {
        severity: 'warning' as const,
        message: `${value.toFixed(1)}% growth rate is quite aggressive`,
        suggestion: 15,
        explanation: 'Consider if the company can maintain this growth rate'
      };
    } else if (value > 15) {
      return {
        severity: 'info' as const,
        message: `${value.toFixed(1)}% growth rate is above average`,
        suggestion: null,
        explanation: 'Ensure this is supported by company fundamentals'
      };
    } else if (value < 0) {
      return {
        severity: 'warning' as const,
        message: `Negative growth rate of ${value.toFixed(1)}% assumed`,
        suggestion: 5,
        explanation: 'Consider cyclical recovery or turnaround potential'
      };
    }
    return null;
  };

  const warning = getWarning();
  if (!warning) return null;

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className={`p-3 rounded-lg border ${
        warning.severity === 'error'
          ? 'bg-red-900/20 border-red-500/30'
          : warning.severity === 'warning'
          ? 'bg-yellow-900/20 border-yellow-500/30'
          : 'bg-blue-900/20 border-blue-500/30'
      } ${className}`}
    >
      <div className="flex items-start space-x-2">
        <div className="flex-shrink-0 mt-0.5">
          {warning.severity === 'error' ? (
            <AlertTriangle className="h-4 w-4 text-red-400" />
          ) : warning.severity === 'warning' ? (
            <AlertCircle className="h-4 w-4 text-yellow-400" />
          ) : (
            <Info className="h-4 w-4 text-blue-400" />
          )}
        </div>
        <div className="flex-1 min-w-0">
          <div className={`text-sm font-medium mb-1 ${
            warning.severity === 'error'
              ? 'text-red-300'
              : warning.severity === 'warning'
              ? 'text-yellow-300'
              : 'text-blue-300'
          }`}>
            {warning.message}
          </div>
          <div className={`text-xs ${
            warning.severity === 'error'
              ? 'text-red-200'
              : warning.severity === 'warning'
              ? 'text-yellow-200'
              : 'text-blue-200'
          }`}>
            {warning.explanation}
          </div>
          {warning.suggestion && onAdjust && (
            <button
              onClick={() => onAdjust(warning.suggestion!)}
              className={`mt-2 text-xs px-2 py-1 rounded transition-colors ${
                warning.severity === 'error'
                  ? 'bg-red-600 hover:bg-red-700 text-white'
                  : 'bg-yellow-600 hover:bg-yellow-700 text-white'
              }`}
            >
              Use {warning.suggestion}% instead
            </button>
          )}
        </div>
      </div>
    </motion.div>
  );
};

export const MarginWarning: React.FC<SpecificWarningProps> = ({
  value,
  className = '',
  onAdjust
}) => {
  const getWarning = () => {
    if (value > 40) {
      return {
        severity: 'error' as const,
        message: `${value.toFixed(1)}% margin is exceptionally high`,
        suggestion: 35,
        explanation: 'Few companies sustain >40% EBITDA margins'
      };
    } else if (value > 30) {
      return {
        severity: 'warning' as const,
        message: `${value.toFixed(1)}% margin is quite optimistic`,
        suggestion: 25,
        explanation: 'High margins may attract competition'
      };
    } else if (value < 5) {
      return {
        severity: 'warning' as const,
        message: `${value.toFixed(1)}% margin is very low`,
        suggestion: 10,
        explanation: 'Low margins may indicate operational challenges'
      };
    } else if (value < 0) {
      return {
        severity: 'error' as const,
        message: `Negative margin of ${value.toFixed(1)}% assumed`,
        suggestion: 5,
        explanation: 'Negative margins are unsustainable long-term'
      };
    }
    return null;
  };

  const warning = getWarning();
  if (!warning) return null;

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className={`p-3 rounded-lg border ${
        warning.severity === 'error'
          ? 'bg-red-900/20 border-red-500/30'
          : 'bg-yellow-900/20 border-yellow-500/30'
      } ${className}`}
    >
      <div className="flex items-start space-x-2">
        <div className="flex-shrink-0 mt-0.5">
          {warning.severity === 'error' ? (
            <AlertTriangle className="h-4 w-4 text-red-400" />
          ) : (
            <AlertCircle className="h-4 w-4 text-yellow-400" />
          )}
        </div>
        <div className="flex-1 min-w-0">
          <div className={`text-sm font-medium mb-1 ${
            warning.severity === 'error' ? 'text-red-300' : 'text-yellow-300'
          }`}>
            {warning.message}
          </div>
          <div className={`text-xs ${
            warning.severity === 'error' ? 'text-red-200' : 'text-yellow-200'
          }`}>
            {warning.explanation}
          </div>
          {onAdjust && (
            <button
              onClick={() => onAdjust(warning.suggestion)}
              className={`mt-2 text-xs px-2 py-1 rounded transition-colors ${
                warning.severity === 'error'
                  ? 'bg-red-600 hover:bg-red-700 text-white'
                  : 'bg-yellow-600 hover:bg-yellow-700 text-white'
              }`}
            >
              Use {warning.suggestion}% instead
            </button>
          )}
        </div>
      </div>
    </motion.div>
  );
};

export const DiscountRateWarning: React.FC<SpecificWarningProps> = ({
  value,
  className = '',
  onAdjust
}) => {
  const getWarning = () => {
    if (value < 6) {
      return {
        severity: 'warning' as const,
        message: `${value.toFixed(1)}% discount rate seems too low`,
        suggestion: 10,
        explanation: 'Very low discount rates may overvalue the company'
      };
    } else if (value > 20) {
      return {
        severity: 'warning' as const,
        message: `${value.toFixed(1)}% discount rate is quite high`,
        suggestion: 15,
        explanation: 'High discount rates may undervalue quality companies'
      };
    } else if (value > 25) {
      return {
        severity: 'error' as const,
        message: `${value.toFixed(1)}% discount rate is exceptionally high`,
        suggestion: 18,
        explanation: 'Extreme discount rates may indicate data issues'
      };
    }
    return null;
  };

  const warning = getWarning();
  if (!warning) return null;

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className={`p-3 rounded-lg border ${
        warning.severity === 'error'
          ? 'bg-red-900/20 border-red-500/30'
          : 'bg-yellow-900/20 border-yellow-500/30'
      } ${className}`}
    >
      <div className="flex items-start space-x-2">
        <div className="flex-shrink-0 mt-0.5">
          {warning.severity === 'error' ? (
            <AlertTriangle className="h-4 w-4 text-red-400" />
          ) : (
            <AlertCircle className="h-4 w-4 text-yellow-400" />
          )}
        </div>
        <div className="flex-1 min-w-0">
          <div className={`text-sm font-medium mb-1 ${
            warning.severity === 'error' ? 'text-red-300' : 'text-yellow-300'
          }`}>
            {warning.message}
          </div>
          <div className={`text-xs ${
            warning.severity === 'error' ? 'text-red-200' : 'text-yellow-200'
          }`}>
            {warning.explanation}
          </div>
          {onAdjust && (
            <button
              onClick={() => onAdjust(warning.suggestion)}
              className={`mt-2 text-xs px-2 py-1 rounded transition-colors ${
                warning.severity === 'error'
                  ? 'bg-red-600 hover:bg-red-700 text-white'
                  : 'bg-yellow-600 hover:bg-yellow-700 text-white'
              }`}
            >
              Use {warning.suggestion}% instead
            </button>
          )}
        </div>
      </div>
    </motion.div>
  );
};

export const TerminalGrowthWarning: React.FC<SpecificWarningProps> = ({
  value,
  className = '',
  onAdjust
}) => {
  const getWarning = () => {
    if (value > 5) {
      return {
        severity: 'error' as const,
        message: `${value.toFixed(1)}% terminal growth is too high`,
        suggestion: 3,
        explanation: 'Terminal growth should not exceed long-term GDP growth (~3-4%)'
      };
    } else if (value > 4) {
      return {
        severity: 'warning' as const,
        message: `${value.toFixed(1)}% terminal growth is optimistic`,
        suggestion: 3,
        explanation: 'Consider long-term economic growth constraints'
      };
    } else if (value < 0) {
      return {
        severity: 'warning' as const,
        message: `Negative terminal growth of ${value.toFixed(1)}%`,
        suggestion: 2,
        explanation: 'Negative perpetual growth is highly unusual'
      };
    }
    return null;
  };

  const warning = getWarning();
  if (!warning) return null;

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className={`p-3 rounded-lg border ${
        warning.severity === 'error'
          ? 'bg-red-900/20 border-red-500/30'
          : 'bg-yellow-900/20 border-yellow-500/30'
      } ${className}`}
    >
      <div className="flex items-start space-x-2">
        <div className="flex-shrink-0 mt-0.5">
          {warning.severity === 'error' ? (
            <AlertTriangle className="h-4 w-4 text-red-400" />
          ) : (
            <AlertCircle className="h-4 w-4 text-yellow-400" />
          )}
        </div>
        <div className="flex-1 min-w-0">
          <div className={`text-sm font-medium mb-1 ${
            warning.severity === 'error' ? 'text-red-300' : 'text-yellow-300'
          }`}>
            {warning.message}
          </div>
          <div className={`text-xs ${
            warning.severity === 'error' ? 'text-red-200' : 'text-yellow-200'
          }`}>
            {warning.explanation}
          </div>
          {onAdjust && (
            <button
              onClick={() => onAdjust(warning.suggestion)}
              className={`mt-2 text-xs px-2 py-1 rounded transition-colors ${
                warning.severity === 'error'
                  ? 'bg-red-600 hover:bg-red-700 text-white'
                  : 'bg-yellow-600 hover:bg-yellow-700 text-white'
              }`}
            >
              Use {warning.suggestion}% instead
            </button>
          )}
        </div>
      </div>
    </motion.div>
  );
};

// Utility function to validate DCF assumptions
export const validateDCFAssumptions = (assumptions: {
  revenue_growth_rate?: number;
  ebitda_margin?: number;
  wacc?: number;
  terminal_growth_rate?: number;
  tax_rate?: number;
}): ValidationRule[] => {
  const rules: ValidationRule[] = [];

  if (assumptions.revenue_growth_rate !== undefined) {
    const growth = assumptions.revenue_growth_rate;
    if (growth > 25) {
      rules.push({
        field: 'revenue_growth_rate',
        value: growth,
        severity: 'error',
        warning: `Revenue growth of ${growth.toFixed(1)}% is extremely optimistic`,
        recommendation: 'Consider 15-20% for high-growth companies'
      });
    } else if (growth > 20) {
      rules.push({
        field: 'revenue_growth_rate',
        value: growth,
        severity: 'warning',
        warning: `Revenue growth of ${growth.toFixed(1)}% is quite aggressive`,
        recommendation: 'Ensure fundamentals support this growth'
      });
    } else if (growth < -5) {
      rules.push({
        field: 'revenue_growth_rate',
        value: growth,
        severity: 'warning',
        warning: `Revenue decline of ${Math.abs(growth).toFixed(1)}% may be temporary`,
        recommendation: 'Consider recovery scenarios'
      });
    }
  }

  if (assumptions.ebitda_margin !== undefined) {
    const margin = assumptions.ebitda_margin;
    if (margin > 40) {
      rules.push({
        field: 'ebitda_margin',
        value: margin,
        severity: 'error',
        warning: `EBITDA margin of ${margin.toFixed(1)}% is exceptionally high`,
        recommendation: 'Few companies sustain >40% margins'
      });
    } else if (margin < 0) {
      rules.push({
        field: 'ebitda_margin',
        value: margin,
        severity: 'error',
        warning: `Negative EBITDA margin of ${margin.toFixed(1)}%`,
        recommendation: 'Consider turnaround timeline'
      });
    }
  }

  if (assumptions.wacc !== undefined) {
    const wacc = assumptions.wacc;
    if (wacc < 6) {
      rules.push({
        field: 'wacc',
        value: wacc,
        severity: 'warning',
        warning: `WACC of ${wacc.toFixed(1)}% seems low for equity investments`,
        recommendation: 'Consider risk premiums and market conditions'
      });
    } else if (wacc > 20) {
      rules.push({
        field: 'wacc',
        value: wacc,
        severity: 'warning',
        warning: `WACC of ${wacc.toFixed(1)}% is quite high`,
        recommendation: 'Review cost of capital assumptions'
      });
    }
  }

  if (assumptions.terminal_growth_rate !== undefined) {
    const terminal = assumptions.terminal_growth_rate;
    if (terminal > 5) {
      rules.push({
        field: 'terminal_growth_rate',
        value: terminal,
        severity: 'error',
        warning: `Terminal growth of ${terminal.toFixed(1)}% exceeds economic growth`,
        recommendation: 'Use 2-4% based on long-term GDP growth'
      });
    } else if (terminal < 0) {
      rules.push({
        field: 'terminal_growth_rate',
        value: terminal,
        severity: 'warning',
        warning: `Negative terminal growth of ${terminal.toFixed(1)}% is unusual`,
        recommendation: 'Consider 2-3% default terminal growth'
      });
    }
  }

  return rules;
};