import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Info, RotateCcw, TrendingUp, Percent, Building2, DollarSign, BarChart3 } from 'lucide-react';

export interface DCFAssumptions {
  revenue_growth_rate: number;
  ebitda_margin: number;
  tax_rate: number;
  wacc: number;
  terminal_growth_rate: number;
  projection_years: number;
  capex_percentage: number;
  working_capital_percentage: number;
  depreciation_percentage: number;
  net_debt_percentage: number;
  // Normalization System flags
  normalized_capex_rate?: number;
  requires_normalization?: boolean;
}

export interface DCFDefaults extends DCFAssumptions {
  current_price: number;
  rationale: Record<string, string>;
}

interface InteractiveDCFAssumptionsProps {
  assumptions: DCFAssumptions;
  defaults: DCFDefaults;
  onUpdateAssumption: (key: keyof DCFAssumptions, value: number) => void;
  onResetToDefaults: () => void;
  sector: string;
  modelType?: string;
  ticker: string;
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
  icon: React.ComponentType<{ className?: string }>;
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
  defaultValue,
  icon: Icon = Percent
}) => {
  const [showTooltip, setShowTooltip] = useState(false);
  const isModified = defaultValue !== undefined && Math.abs(value - defaultValue) > 0.01;

  const percentage = ((value - min) / (max - min)) * 100;

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Icon className="h-4 w-4 text-primary-400" />
          <label className="text-sm font-medium text-slate-200">{label}</label>
          <div className="relative">
            <Info
              className="h-3 w-3 text-slate-400 cursor-help hover:text-slate-300 transition-colors"
              onMouseEnter={() => setShowTooltip(true)}
              onMouseLeave={() => setShowTooltip(false)}
            />
            {showTooltip && (
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                className="absolute z-10 w-64 p-2 mt-1 text-xs text-slate-200 bg-slate-800 border border-slate-600 rounded-lg shadow-lg -left-32"
              >
                {tooltip}
              </motion.div>
            )}
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <span className={`text-sm font-mono ${isModified ? 'text-primary-300' : 'text-slate-300'}`}>
            {value.toFixed(step < 1 ? 1 : 0)}{suffix}
          </span>
          {isModified && (
            <div className="w-2 h-2 rounded-full bg-primary-400"></div>
          )}
        </div>
      </div>

      <div className="relative">
        <div className="w-full h-2 bg-slate-700 rounded-full">
          <div 
            className="h-2 bg-gradient-to-r from-primary-500 to-primary-400 rounded-full transition-all duration-200"
            style={{ width: `${percentage}%` }}
          />
        </div>
        
        <input
          type="range"
          min={min}
          max={max}
          step={step}
          value={value}
          onChange={(e) => onChange(parseFloat(e.target.value))}
          className="absolute inset-0 w-full h-2 opacity-0 cursor-pointer"
        />
      </div>

      <div className="flex justify-between text-xs text-slate-500">
        <span>{min}{suffix}</span>
        <span>{max}{suffix}</span>
      </div>
    </div>
  );
};

export const InteractiveDCFAssumptions: React.FC<InteractiveDCFAssumptionsProps> = ({
  assumptions,
  defaults,
  onUpdateAssumption,
  onResetToDefaults,
  sector,
  modelType,
  ticker
}) => {
  // Get sector-specific assumption ranges and tooltips
  const getAssumptionConfig = (sector: string) => {
    const configs: Record<string, any> = {
      'BFSI': {
        revenue_growth_rate: { min: 5, max: 25, tooltip: 'Credit growth rate for banking sector (5-25%)' },
        ebitda_margin: { min: 10, max: 40, tooltip: 'Net Interest Margin for banks (10-40%)' },
        wacc: { min: 8, max: 16, tooltip: 'Cost of equity for banking sector (8-16%)' }
      },
      'IT': {
        revenue_growth_rate: { min: 5, max: 30, tooltip: 'IT services revenue growth (5-30%)' },
        ebitda_margin: { min: 15, max: 35, tooltip: 'EBITDA margin for IT services (15-35%)' },
        wacc: { min: 9, max: 15, tooltip: 'WACC for IT companies (9-15%)' }
      },
      'PHARMA': {
        revenue_growth_rate: { min: 5, max: 25, tooltip: 'Pharma revenue growth including R&D impact (5-25%)' },
        ebitda_margin: { min: 15, max: 30, tooltip: 'EBITDA margin for pharma companies (15-30%)' },
        wacc: { min: 9, max: 14, tooltip: 'WACC for pharmaceutical sector (9-14%)' }
      }
    };

    return configs[sector] || {
      revenue_growth_rate: { min: 0, max: 30, tooltip: 'Annual revenue growth rate' },
      ebitda_margin: { min: 5, max: 40, tooltip: 'EBITDA as percentage of revenue' },
      wacc: { min: 8, max: 18, tooltip: 'Weighted Average Cost of Capital' }
    };
  };

  const sectorConfig = getAssumptionConfig(sector);

  // Model-specific assumptions
  const getModelSpecificAssumptions = (modelType: string, sector: string) => {
    switch (modelType) {
      case 'sector':
        if (sector === 'BFSI') {
          return getBankingExcessReturnsAssumptions();
        } else if (sector === 'REAL ESTATE') {
          return getRealEstateNAVAssumptions();
        } else if (sector === 'IT') {
          return getITServicesAssumptions();
        } else if (sector === 'PHARMA') {
          return getPharmaAssumptions();
        } else {
          return getStandardDCFAssumptions(sector);
        }
      case 'pe_valuation':
        return getPEBasedAssumptions();
      case 'ev_ebitda':
        return getEVEBITDAAssumptions(sector);
      case 'generic_dcf':
      default:
        return getGenericDCFAssumptions(sector);
    }
  };

  // Banking Excess Returns Model assumptions
  const getBankingExcessReturnsAssumptions = () => [
    {
      key: 'revenue_growth_rate' as keyof DCFAssumptions,
      label: 'Starting ROE',
      min: 8,
      max: 25,
      step: 0.5,
      suffix: '%',
      tooltip: `Return on Equity calculated from historical financial data for ${ticker}`,
      icon: Percent
    },
    {
      key: 'wacc' as keyof DCFAssumptions,
      label: 'Cost of Equity',
      min: 8,
      max: 18,
      step: 0.1,
      suffix: '%',
      tooltip: `CAPM-based cost of equity for ${ticker}: Risk-free rate + Beta × Equity risk premium`,
      icon: TrendingUp
    },
    {
      key: 'terminal_growth_rate' as keyof DCFAssumptions,
      label: 'Terminal ROE',
      min: 10,
      max: 20,
      step: 0.5,
      suffix: '%',
      tooltip: 'Long-term sustainable ROE = Cost of Equity + Competitive moat premium',
      icon: TrendingUp
    }
  ];

  // Real Estate NAV Model assumptions
  const getRealEstateNAVAssumptions = () => [
    {
      key: 'revenue_growth_rate' as keyof DCFAssumptions,
      label: 'NAV Premium Multiple',
      min: 0.8,
      max: 2.0,
      step: 0.1,
      suffix: 'x',
      tooltip: 'Premium/discount to book value based on asset quality and market position',
      icon: TrendingUp
    },
    {
      key: 'ebitda_margin' as keyof DCFAssumptions,
      label: 'Asset Quality Premium',
      min: -10,
      max: 20,
      step: 1,
      suffix: '%',
      tooltip: 'ROE-based premium: +15% for >15% ROE, -10% for <5% ROE',
      icon: Percent
    },
    {
      key: 'wacc' as keyof DCFAssumptions,
      label: 'Location Premium',
      min: 0,
      max: 15,
      step: 1,
      suffix: '%',
      tooltip: 'Tier-1 city exposure premium: 8% for large developers, 3% for others',
      icon: Building2
    }
  ];

  // IT Services EV/Revenue Model assumptions
  const getITServicesAssumptions = () => [
    {
      key: 'revenue_growth_rate' as keyof DCFAssumptions,
      label: 'Revenue Growth Rate',
      min: 5,
      max: 30,
      step: 0.5,
      suffix: '%',
      tooltip: '3-year compound annual growth rate of revenue',
      icon: TrendingUp
    },
    {
      key: 'ebitda_margin' as keyof DCFAssumptions,
      label: 'EV/Revenue Multiple',
      min: 4,
      max: 12,
      step: 0.5,
      suffix: 'x',
      tooltip: 'Enterprise value to revenue multiple: 6-8x for IT sector, adjusted for quality',
      icon: BarChart3
    }
  ];

  // PE-Based Valuation assumptions
  const getPEBasedAssumptions = () => [
    {
      key: 'revenue_growth_rate' as keyof DCFAssumptions,
      label: 'Historical EPS Growth',
      min: -10,
      max: 40,
      step: 1,
      suffix: '%',
      tooltip: '3-year compound annual growth rate of earnings',
      icon: TrendingUp
    },
    {
      key: 'ebitda_margin' as keyof DCFAssumptions,
      label: 'Industry P/E Multiple',
      min: 8,
      max: 35,
      step: 0.5,
      suffix: 'x',
      tooltip: 'Sector-specific P/E ratio: BFSI (15x), IT (22x), PHARMA (18x)',
      icon: BarChart3
    }
  ];

  // Pharma R&D Pipeline assumptions
  const getPharmaAssumptions = () => [
    {
      key: 'revenue_growth_rate' as keyof DCFAssumptions,
      label: 'Revenue Growth Rate',
      min: 5,
      max: 25,
      step: 0.5,
      suffix: '%',
      tooltip: 'Pharma revenue growth including R&D pipeline impact',
      icon: TrendingUp
    },
    {
      key: 'ebitda_margin' as keyof DCFAssumptions,
      label: 'R&D Spend',
      min: 5,
      max: 25,
      step: 1,
      suffix: '%',
      tooltip: 'R&D investment as percentage of revenue',
      icon: Percent
    }
  ];

  // Standard FCFF DCF assumptions (ENERGY, FMCG, etc.)
  const getStandardDCFAssumptions = (sector: string) => [
    {
      key: 'revenue_growth_rate' as keyof DCFAssumptions,
      label: 'Revenue Growth Rate',
      min: sectorConfig.revenue_growth_rate?.min || 0,
      max: sectorConfig.revenue_growth_rate?.max || 30,
      step: 0.5,
      suffix: '%',
      tooltip: sectorConfig.revenue_growth_rate?.tooltip || 'Expected annual revenue growth rate',
      icon: TrendingUp
    },
    {
      key: 'ebitda_margin' as keyof DCFAssumptions,
      label: 'EBITDA Margin',
      min: sectorConfig.ebitda_margin?.min || 5,
      max: sectorConfig.ebitda_margin?.max || 40,
      step: 0.5,
      suffix: '%',
      tooltip: sectorConfig.ebitda_margin?.tooltip || 'EBITDA as a percentage of revenue',
      icon: Percent
    },
    {
      key: 'tax_rate' as keyof DCFAssumptions,
      label: 'Tax Rate',
      min: 15,
      max: 35,
      step: 0.5,
      suffix: '%',
      tooltip: 'Corporate tax rate applied to earnings',
      icon: Percent
    },
    {
      key: 'wacc' as keyof DCFAssumptions,
      label: 'WACC (Discount Rate)',
      min: sectorConfig.wacc?.min || 8,
      max: sectorConfig.wacc?.max || 18,
      step: 0.1,
      suffix: '%',
      tooltip: sectorConfig.wacc?.tooltip || 'Weighted Average Cost of Capital',
      icon: Percent
    },
    {
      key: 'terminal_growth_rate' as keyof DCFAssumptions,
      label: 'Terminal Growth Rate',
      min: 1,
      max: 8,
      step: 0.1,
      suffix: '%',
      tooltip: 'Long-term growth rate for terminal value calculation',
      icon: TrendingUp
    },
    {
      key: 'capex_percentage' as keyof DCFAssumptions,
      label: 'CapEx (% of Revenue)',
      min: 1,
      max: 15,
      step: 0.5,
      suffix: '%',
      tooltip: 'Capital expenditure as percentage of revenue (dynamic from historical data)',
      icon: Percent
    },
    {
      key: 'working_capital_percentage' as keyof DCFAssumptions,
      label: 'Working Capital Change',
      min: -5,
      max: 10,
      step: 0.5,
      suffix: '%',
      tooltip: 'Working capital change as percentage of revenue (dynamic from historical data)',
      icon: Percent
    }
  ];

  // EV/EBITDA Model assumptions
  const getEVEBITDAAssumptions = (sector: string) => [
    {
      key: 'revenue_growth_rate' as keyof DCFAssumptions,
      label: 'Revenue Growth Rate',
      min: sectorConfig.revenue_growth_rate?.min || 0,
      max: sectorConfig.revenue_growth_rate?.max || 30,
      step: 0.5,
      suffix: '%',
      tooltip: sectorConfig.revenue_growth_rate?.tooltip || 'Expected annual revenue growth rate',
      icon: TrendingUp
    },
    {
      key: 'ebitda_margin' as keyof DCFAssumptions,
      label: 'EBITDA Margin',
      min: sectorConfig.ebitda_margin?.min || 5,
      max: sectorConfig.ebitda_margin?.max || 40,
      step: 0.5,
      suffix: '%',
      tooltip: sectorConfig.ebitda_margin?.tooltip || 'EBITDA as a percentage of revenue',
      icon: Percent
    },
    {
      key: 'wacc' as keyof DCFAssumptions,
      label: 'EV/EBITDA Multiple',
      min: 8,
      max: 25,
      step: 0.5,
      suffix: 'x',
      tooltip: 'Enterprise Value to EBITDA multiple for valuation',
      icon: BarChart3
    },
    {
      key: 'terminal_growth_rate' as keyof DCFAssumptions,
      label: 'Terminal Growth Rate',
      min: 1,
      max: 8,
      step: 0.1,
      suffix: '%',
      tooltip: 'Long-term growth rate for terminal value calculation',
      icon: TrendingUp
    }
  ];

  // Generic DCF assumptions (fallback)
  const getGenericDCFAssumptions = (sector: string) => [
    {
      key: 'revenue_growth_rate' as keyof DCFAssumptions,
      label: 'Revenue Growth Rate',
      min: sectorConfig.revenue_growth_rate?.min || 0,
      max: sectorConfig.revenue_growth_rate?.max || 30,
      step: 0.5,
      suffix: '%',
      tooltip: sectorConfig.revenue_growth_rate?.tooltip || 'Expected annual revenue growth rate',
      icon: TrendingUp
    },
    {
      key: 'ebitda_margin' as keyof DCFAssumptions,
      label: 'EBITDA Margin',
      min: sectorConfig.ebitda_margin?.min || 5,
      max: sectorConfig.ebitda_margin?.max || 40,
      step: 0.5,
      suffix: '%',
      tooltip: sectorConfig.ebitda_margin?.tooltip || 'EBITDA as a percentage of revenue',
      icon: Percent
    },
    {
      key: 'tax_rate' as keyof DCFAssumptions,
      label: 'Tax Rate',
      min: 15,
      max: 35,
      step: 0.5,
      suffix: '%',
      tooltip: 'Corporate tax rate applied to earnings',
      icon: Percent
    },
    {
      key: 'wacc' as keyof DCFAssumptions,
      label: 'WACC (Discount Rate)',
      min: sectorConfig.wacc?.min || 8,
      max: sectorConfig.wacc?.max || 18,
      step: 0.1,
      suffix: '%',
      tooltip: sectorConfig.wacc?.tooltip || 'Weighted Average Cost of Capital used to discount cash flows',
      icon: Percent
    },
    {
      key: 'terminal_growth_rate' as keyof DCFAssumptions,
      label: 'Terminal Growth Rate',
      min: 1,
      max: 8,
      step: 0.1,
      suffix: '%',
      tooltip: 'Long-term growth rate for terminal value calculation',
      icon: TrendingUp
    },
    {
      key: 'capex_percentage' as keyof DCFAssumptions,
      label: 'CapEx (% of Revenue)',
      min: 1,
      max: 15,
      step: 0.5,
      suffix: '%',
      tooltip: 'Capital expenditure as percentage of revenue',
      icon: Percent
    },
    {
      key: 'working_capital_percentage' as keyof DCFAssumptions,
      label: 'Working Capital Change',
      min: -5,
      max: 10,
      step: 0.5,
      suffix: '%',
      tooltip: 'Working capital change as percentage of revenue change',
      icon: Percent
    },
    {
      key: 'net_debt_percentage' as keyof DCFAssumptions,
      label: 'Net Debt / Enterprise Value',
      min: 0,
      max: 50,
      step: 1,
      suffix: '%',
      tooltip: 'Net debt as percentage of Enterprise Value',
      icon: DollarSign
    }
  ];

  // Helper functions for model-specific UI
  const getModelTitle = (modelType?: string, sector?: string): string => {
    switch (modelType) {
      case 'sector':
        if (sector === 'BFSI') return 'Banking Excess Returns';
        if (sector === 'REAL ESTATE') return 'Real Estate NAV';
        if (sector === 'IT') return 'IT Services EV/Revenue';
        if (sector === 'PHARMA') return 'Pharma R&D Pipeline';
        return 'Sector-Specific DCF';
      case 'pe_valuation':
        return 'P/E Based Valuation';
      case 'ev_ebitda':
        return 'EV/EBITDA Multiple';
      case 'generic_dcf':
        return 'Standard DCF';
      default:
        return 'DCF';
    }
  };

  const getModelDescription = (modelType?: string, sector?: string): string => {
    switch (modelType) {
      case 'sector':
        if (sector === 'BFSI') return 'Adjust ROE convergence and cost of equity assumptions';
        if (sector === 'REAL ESTATE') return 'Adjust NAV premiums and asset quality factors';
        if (sector === 'IT') return 'Adjust revenue growth and EV/Revenue multiples';
        if (sector === 'PHARMA') return 'Adjust R&D pipeline and patent cliff assumptions';
        return 'Adjust sector-specific valuation parameters';
      case 'pe_valuation':
        return 'Adjust earnings growth and P/E multiple assumptions';
      case 'ev_ebitda':
        return 'Adjust EBITDA margins and EV/EBITDA multiple assumptions';
      case 'generic_dcf':
        return 'Adjust cash flow projection assumptions';
      default:
        return 'Adjust assumptions to see real-time impact on valuation';
    }
  };

  // Get the appropriate assumptions based on model type
  const dynamicAssumptions = getModelSpecificAssumptions(modelType || 'generic_dcf', sector);

  // Check for modifications - only consider assumptions displayed in current model
  const hasModifications = dynamicAssumptions.some(input => {
    const assumptionValue = assumptions[input.key];
    const defaultValue = defaults[input.key];
    if (typeof assumptionValue === 'number' && typeof defaultValue === 'number') {
      return Math.abs(assumptionValue - defaultValue) > 0.01;
    }
    return false;
  });

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      className="bg-slate-800/50 rounded-xl p-6 border border-slate-700/50"
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold text-slate-100 mb-1">
            {getModelTitle(modelType, sector)} Assumptions
          </h3>
          <p className="text-sm text-slate-400">
            {getModelDescription(modelType, sector)}
          </p>
        </div>
        
        {hasModifications && (
          <motion.button
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            onClick={onResetToDefaults}
            className="flex items-center space-x-2 px-3 py-1.5 bg-slate-700 hover:bg-slate-600 text-slate-300 rounded-lg text-sm transition-colors"
          >
            <RotateCcw className="h-3 w-3" />
            <span>Reset</span>
          </motion.button>
        )}
      </div>

      {/* Sector Badge */}
      <div className="mb-6">
        <div className="inline-flex items-center space-x-2 px-3 py-1 bg-primary-500/20 text-primary-300 rounded-full text-sm">
          <div className="w-2 h-2 rounded-full bg-primary-400"></div>
          <span>{sector} Sector • {getModelTitle(modelType, sector)}</span>
        </div>
      </div>

      {/* Assumption Sliders */}
      <div className="space-y-6">
        {dynamicAssumptions.map((input) => {
          const value = assumptions[input.key];
          const defaultValue = defaults[input.key];
          // Only render SliderInput for numeric values
          if (typeof value === 'number' && typeof defaultValue === 'number') {
            return (
              <SliderInput
                key={input.key}
                label={input.label}
                value={value}
                min={input.min}
                max={input.max}
                step={input.step}
                suffix={input.suffix}
                tooltip={input.tooltip}
                onChange={(value) => onUpdateAssumption(input.key, value)}
                defaultValue={defaultValue}
                icon={input.icon}
              />
            );
          }
          return null;
        })}
      </div>

      {/* Modifications Summary */}
      {hasModifications && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          className="mt-6 pt-4 border-t border-slate-700"
        >
          <div className="flex items-center justify-between text-sm">
            <span className="text-slate-400">
              {dynamicAssumptions.filter(input => {
                const assumptionValue = assumptions[input.key];
                const defaultValue = defaults[input.key];
                if (typeof assumptionValue === 'number' && typeof defaultValue === 'number') {
                  return Math.abs(assumptionValue - defaultValue) > 0.01;
                }
                return false;
              }).length} assumptions modified
            </span>
            <button
              onClick={onResetToDefaults}
              className="text-primary-400 hover:text-primary-300 transition-colors"
            >
              Reset all
            </button>
          </div>
        </motion.div>
      )}
    </motion.div>
  );
};