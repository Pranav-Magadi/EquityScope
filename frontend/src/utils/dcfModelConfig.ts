// DCF Model-Specific Configuration
// Date: July 31, 2025
// Purpose: Define model-specific ranges, tooltips, and validation logic

import { DCFModelType } from '../types/dcfModels';

// Model-specific assumption configuration
export interface AssumptionConfig {
  key: string;
  label: string;
  min: number;
  max: number;
  step: number;
  suffix: string;
  tooltip: string;
  icon: string;
  category: 'growth' | 'profitability' | 'risk' | 'operational' | 'regulatory';
}

// =============================================================================
// MULTI-STAGE DCF CONFIGURATIONS
// =============================================================================

export const MultiStageSimpleConfig: AssumptionConfig[] = [
  {
    key: 'stage_1_2_growth',
    label: 'Stage 1-2 Growth (Years 1-2)',
    min: 0,
    max: 30,
    step: 0.5,
    suffix: '%',
    tooltip: 'Near-term growth: 80% historical CAGR + 20% GDP blend. Based on 5-year revenue CAGR validation.',
    icon: 'TrendingUp',
    category: 'growth'
  },
  {
    key: 'stage_3_5_growth',
    label: 'Stage 3-5 Growth (Years 3-5)',
    min: 0,
    max: 25,
    step: 0.5,
    suffix: '%',
    tooltip: 'Mid-term competitive fade: 50% historical + 50% GDP. Industry dynamics impact expected.',
    icon: 'TrendingUp',
    category: 'growth'
  },
  {
    key: 'stage_6_8_growth',
    label: 'Stage 6-8 Growth (Years 6-8)',
    min: 0,
    max: 15,
    step: 0.5,
    suffix: '%',
    tooltip: 'Market maturation: 25% historical + 75% GDP. Competitive convergence phase.',
    icon: 'TrendingUp',
    category: 'growth'
  },
  {
    key: 'stage_9_10_growth',
    label: 'Stage 9-10 Growth (Years 9-10)',
    min: 1,
    max: 8,
    step: 0.1,
    suffix: '%',
    tooltip: 'GDP convergence: 100% India nominal GDP growth (3.0%). Long-term economic constraints.',
    icon: 'TrendingUp',
    category: 'growth'
  },
  {
    key: 'ebitda_margin',
    label: 'EBITDA Margin',
    min: 5,
    max: 40,
    step: 0.5,
    suffix: '%',
    tooltip: 'Average EBITDA margin from 4-year historical analysis. Sector-adjusted for sustainability.',
    icon: 'Percent',
    category: 'profitability'
  },
  {
    key: 'wacc',
    label: 'WACC (Discount Rate)',
    min: 8,
    max: 18,
    step: 0.1,
    suffix: '%',
    tooltip: 'Risk-free rate (7.2%) + Beta × Market premium. Based on Damodaran sector data.',
    icon: 'Percent',
    category: 'risk'
  },
  {
    key: 'terminal_growth_rate',
    label: 'Terminal Growth Rate',
    min: 1,
    max: 6,
    step: 0.1,
    suffix: '%',
    tooltip: 'Long-term growth beyond Year 10. Constrained by India GDP growth expectations.',
    icon: 'TrendingUp',
    category: 'growth'
  }
];

export const MultiStageAgenticConfig: AssumptionConfig[] = [
  {
    key: 'management_guidance_years_1_2',
    label: 'Management Guidance (Years 1-2)',
    min: 0,
    max: 35,
    step: 0.5,
    suffix: '%',
    tooltip: 'AI-extracted from earnings calls: 90% management guidance + 10% GDP. Enhanced with sentiment analysis.',
    icon: 'Brain',
    category: 'growth'
  },
  {
    key: 'capacity_expansion_years_3_5',
    label: 'Capacity Expansion (Years 3-5)',
    min: 0,
    max: 25,
    step: 0.5,
    suffix: '%',
    tooltip: 'AI analysis of capex plans and market expansion: 70% AI insights + 30% GDP blend.',
    icon: 'TrendingUp',
    category: 'growth'
  },
  {
    key: 'market_dynamics_years_6_8',
    label: 'Market Dynamics (Years 6-8)',
    min: 0,
    max: 15,
    step: 0.5,
    suffix: '%',
    tooltip: 'Competitive positioning analysis: 40% market analysis + 60% GDP convergence.',
    icon: 'BarChart3',
    category: 'growth'
  },
  {
    key: 'risk_adjusted_wacc',
    label: 'Risk-Adjusted WACC',
    min: 8,
    max: 20,
    step: 0.1,
    suffix: '%',
    tooltip: 'Base WACC + news sentiment risk + competitive moat adjustments. AI-enhanced risk assessment.',
    icon: 'AlertTriangle',
    category: 'risk'
  },
  {
    key: 'news_sentiment_adjustment',
    label: 'News Sentiment Adjustment',
    min: -2,
    max: 2,
    step: 0.1,
    suffix: '%',
    tooltip: 'AI sentiment analysis impact on growth. Based on 6-month news and social media analysis.',
    icon: 'TrendingUp',
    category: 'risk'
  }
];

// =============================================================================
// BANKING DCF CONFIGURATION
// =============================================================================

export const BankingDCFConfig: AssumptionConfig[] = [
  {
    key: 'credit_growth_rate',
    label: 'Credit Growth Rate',
    min: 5,
    max: 25,
    step: 0.5,
    suffix: '%',
    tooltip: 'Loan book CAGR from 4-year analysis: 14.2%. RBI guidelines and economic growth driven.',
    icon: 'TrendingUp',
    category: 'growth'
  },
  {
    key: 'net_interest_margin',
    label: 'Net Interest Margin (NIM)',
    min: 2.5,
    max: 4.5,
    step: 0.1,
    suffix: '%',
    tooltip: 'Current NIM: 3.4% from Q4 FY24. Peer average: 3.1%. Interest rate cycle impact.',
    icon: 'Percent',
    category: 'profitability'
  },
  {
    key: 'cost_income_ratio',
    label: 'Cost-to-Income Ratio',
    min: 35,
    max: 60,
    step: 0.5,
    suffix: '%',
    tooltip: 'Operational efficiency metric. Current: 42%. Best-in-class: <40%. Digital transformation impact.',
    icon: 'Percent',
    category: 'operational'
  },
  {
    key: 'roe_target',
    label: 'ROE Target',
    min: 12,
    max: 20,
    step: 0.5,
    suffix: '%',
    tooltip: 'Return on Equity target. Historical range: 15-18%. Regulatory expectation: >15%.',
    icon: 'Target',
    category: 'profitability'
  },
  {
    key: 'credit_cost_ratio',
    label: 'Credit Cost Ratio',
    min: 0.3,
    max: 2.0,
    step: 0.1,
    suffix: '%',
    tooltip: 'Expected credit losses as % of advances. Current: 0.8%. Cycle-adjusted provisioning.',
    icon: 'AlertTriangle',
    category: 'risk'
  },
  {
    key: 'tier_1_capital_ratio',
    label: 'Tier 1 Capital Ratio',
    min: 11,
    max: 18,
    step: 0.1,
    suffix: '%',
    tooltip: 'Regulatory capital requirement >11%. Current: 13.2%. Basel III compliance buffer.',
    icon: 'Shield',
    category: 'regulatory'
  }
];

// =============================================================================
// PHARMA DCF CONFIGURATION
// =============================================================================

export const PharmaDCFConfig: AssumptionConfig[] = [
  {
    key: 'rd_investment_rate',
    label: 'R&D Investment Rate',
    min: 6,
    max: 15,
    step: 0.5,
    suffix: '%',
    tooltip: 'Current R&D spend: 11.2% of revenue. Industry benchmark: 8-12%. Pipeline development critical.',
    icon: 'Beaker',
    category: 'operational'
  },
  {
    key: 'us_market_growth',
    label: 'US Market Growth',
    min: 3,
    max: 12,
    step: 0.5,
    suffix: '%',
    tooltip: 'US pharmaceutical market growth: 5-8% expected. Generic competition and pricing pressure.',
    icon: 'TrendingUp',
    category: 'growth'
  },
  {
    key: 'india_market_growth',
    label: 'India Market Growth',
    min: 8,
    max: 18,
    step: 0.5,
    suffix: '%',
    tooltip: 'Domestic pharma market growth: 10-15%. Healthcare penetration and income growth driven.',
    icon: 'TrendingUp',
    category: 'growth'
  },
  {
    key: 'pipeline_value_multiple',
    label: 'Pipeline Value Multiple',
    min: 1,
    max: 6,
    step: 0.5,
    suffix: 'x',
    tooltip: 'Patent pipeline valuation: 3x peak sales potential. Phase II/III trials: $2.1B value.',
    icon: 'Layers',
    category: 'operational'
  },
  {
    key: 'patent_cliff_adjustment',
    label: 'Patent Cliff Adjustment',
    min: -10,
    max: 0,
    step: 0.5,
    suffix: '%',
    tooltip: 'Patent expiry impact: Major patent expiry in FY27 affecting 15% of revenue.',
    icon: 'AlertTriangle',
    category: 'risk'
  }
];

// =============================================================================
// MODEL CONFIGURATION MAPPER
// =============================================================================

export const DCFModelConfigurations: Record<DCFModelType, AssumptionConfig[]> = {
  [DCFModelType.MULTI_STAGE_SIMPLE]: MultiStageSimpleConfig,
  [DCFModelType.MULTI_STAGE_AGENTIC]: MultiStageAgenticConfig,
  [DCFModelType.BANKING_DCF]: BankingDCFConfig,
  [DCFModelType.PHARMA_DCF]: PharmaDCFConfig,
  [DCFModelType.REAL_ESTATE_DCF]: [], // TODO: Implement
  [DCFModelType.IT_SERVICES_DCF]: [], // TODO: Implement
  [DCFModelType.GENERIC_DCF]: [], // TODO: Implement
  [DCFModelType.PE_VALUATION]: [], // TODO: Implement
  [DCFModelType.EV_EBITDA]: [] // TODO: Implement
};

// Model-specific validation rules
export const validateAssumption = (
  modelType: DCFModelType,
  key: string,
  value: number
): { isValid: boolean; error?: string } => {
  const configs = DCFModelConfigurations[modelType];
  const config = configs.find(c => c.key === key);
  
  if (!config) {
    return { isValid: false, error: `Unknown assumption: ${key}` };
  }
  
  if (value < config.min || value > config.max) {
    return { 
      isValid: false, 
      error: `${config.label} must be between ${config.min}${config.suffix} and ${config.max}${config.suffix}` 
    };
  }
  
  return { isValid: true };
};

// Get model-specific tooltip with actual data
export const getEnhancedTooltip = (
  modelType: DCFModelType,
  key: string,
  rationale?: Record<string, string>
): string => {
  const configs = DCFModelConfigurations[modelType];
  const config = configs.find(c => c.key === key);
  
  if (!config) return 'No tooltip available';
  
  // Combine base tooltip with actual data rationale
  let tooltip = config.tooltip;
  if (rationale && rationale[key]) {
    tooltip += ` | Current: ${rationale[key]}`;
  }
  
  return tooltip;
};