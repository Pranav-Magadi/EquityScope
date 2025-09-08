// Model-Specific DCF Assumption Interfaces
// Date: July 31, 2025
// Purpose: Define specific assumption interfaces for different DCF model types

// Base interface for all DCF models
export interface BaseDCFAssumptions {
  model_type: DCFModelType;
  sector?: string;
  projection_years: number;
}

// DCF Model Types Enum
export enum DCFModelType {
  MULTI_STAGE_SIMPLE = 'multi_stage_simple',
  MULTI_STAGE_AGENTIC = 'multi_stage_agentic',
  BANKING_DCF = 'banking_dcf',
  PHARMA_DCF = 'pharma_dcf',
  REAL_ESTATE_DCF = 'real_estate_dcf',
  IT_SERVICES_DCF = 'it_services_dcf',
  GENERIC_DCF = 'generic_dcf',
  PE_VALUATION = 'pe_valuation',
  EV_EBITDA = 'ev_ebitda'
}

// =============================================================================
// 10-YEAR MULTI-STAGE DCF MODELS
// =============================================================================

export interface MultiStageSimpleDCFAssumptions extends BaseDCFAssumptions {
  model_type: DCFModelType.MULTI_STAGE_SIMPLE;
  
  // Multi-stage growth parameters
  stage_1_2_growth: number;         // Years 1-2: Historical (80%) + GDP (20%)
  stage_3_5_growth: number;         // Years 3-5: Historical (50%) + GDP (50%)
  stage_6_8_growth: number;         // Years 6-8: Historical (25%) + GDP (75%)
  stage_9_10_growth: number;        // Years 9-10: GDP (100%)
  
  // Traditional DCF parameters
  ebitda_margin: number;
  tax_rate: number;
  wacc: number;
  terminal_growth_rate: number;
  capex_percentage: number;
  working_capital_percentage: number;
  
  // Simple mode specific
  historical_confidence: number;     // 0.0 to 1.0
  gdp_blend_methodology: 'conservative' | 'balanced' | 'aggressive';
  validation_period_years: number;   // 3, 5, or 7 years of historical data
}

export interface MultiStageAgenticDCFAssumptions extends BaseDCFAssumptions {
  model_type: DCFModelType.MULTI_STAGE_AGENTIC;
  
  // AI-enhanced multi-stage parameters
  management_guidance_years_1_2: number;   // Years 1-2: Management guidance (90%) + GDP (10%)
  capacity_expansion_years_3_5: number;    // Years 3-5: AI analysis (70%) + GDP (30%)
  market_dynamics_years_6_8: number;       // Years 6-8: Market analysis (40%) + GDP (60%)
  gdp_convergence_years_9_10: number;      // Years 9-10: GDP (100%)
  
  // AI risk adjustments
  news_sentiment_adjustment: number;       // -2% to +2% adjustment
  management_credibility_score: number;    // 0.0 to 1.0
  competitive_moat_strength: number;       // 0.0 to 1.0
  
  // Enhanced DCF parameters
  risk_adjusted_wacc: number;
  scenario_weighted_terminal: number;
  ebitda_margin: number;
  tax_rate: number;
  capex_percentage: number;
  working_capital_percentage: number;
  
  // Agentic mode specific
  ai_confidence_score: number;            // 0.0 to 1.0
  forward_looking_weight: number;         // Weight given to forward-looking vs historical
}

// =============================================================================
// SECTOR-SPECIFIC DCF MODELS
// =============================================================================

export interface BankingDCFAssumptions extends BaseDCFAssumptions {
  model_type: DCFModelType.BANKING_DCF;
  
  // Banking-specific metrics (NOT standard DCF)
  credit_growth_rate: number;             // Instead of revenue growth (8-20%)
  net_interest_margin: number;            // Instead of EBITDA margin (2.5-4.0%)
  cost_income_ratio: number;              // Banking efficiency metric (35-55%)
  
  // Banking regulatory parameters
  tier_1_capital_ratio: number;           // Regulatory requirement (>11%)
  provision_coverage_ratio: number;       // Risk management (70-90%)
  roe_target: number;                     // Return on equity target (12-18%)
  
  // Banking risk parameters
  credit_cost_ratio: number;              // Expected credit losses (0.3-1.5%)
  casa_ratio: number;                     // Current/Savings account ratio (35-50%)
  
  // DCF conversion parameters
  tax_rate: number;                       // Corporate tax rate
  terminal_growth_rate: number;           // Long-term growth
  discount_rate: number;                  // Cost of equity for banks
}

export interface PharmaDCFAssumptions extends BaseDCFAssumptions {
  model_type: DCFModelType.PHARMA_DCF;
  
  // Pharma-specific parameters
  rd_investment_rate: number;             // R&D as % of revenue (8-12%)
  us_market_growth: number;               // US pharmaceutical market (5-8%)
  india_market_growth: number;            // Domestic market growth (10-15%)
  
  // Pipeline and IP parameters
  pipeline_value_multiple: number;        // Patent pipeline valuation (2-5x sales)
  patent_cliff_adjustment: number;        // Patent expiry impact (-5% to 0%)
  generic_competition_factor: number;     // Generic drug pressure (0.8-1.0)
  
  // Regulatory parameters
  fda_approval_success_rate: number;      // Clinical trial success (10-30%)
  regulatory_compliance_cost: number;     // Compliance overhead (3-8%)
  
  // Traditional DCF parameters
  ebitda_margin: number;                  // Adjusted for R&D (15-30%)
  tax_rate: number;
  wacc: number;
  terminal_growth_rate: number;
  capex_percentage: number;
  working_capital_percentage: number;
}

export interface RealEstateDCFAssumptions extends BaseDCFAssumptions {
  model_type: DCFModelType.REAL_ESTATE_DCF;
  
  // Real estate specific metrics
  project_monetization_timeline: number;  // Years to complete projects (2-5 years)
  land_appreciation_rate: number;         // Land value growth (5-12%)
  construction_cost_inflation: number;    // Input cost pressure (3-8%)
  
  // Market parameters
  housing_demand_growth: number;          // Market demand (8-15%)
  price_realization_rate: number;        // Pricing power (90-110%)
  inventory_turnover_ratio: number;       // Asset efficiency (0.3-0.8)
  
  // NAV-based parameters
  nav_discount_rate: number;              // NAV discount to market (10-25%)
  project_execution_risk: number;        // Delivery risk premium (2-5%)
  
  // DCF parameters adapted for real estate
  revenue_growth_rate: number;            // Project revenue growth
  operating_margin: number;               // After construction costs
  tax_rate: number;
  wacc: number;
  terminal_growth_rate: number;
}

export interface ITServicesDCFAssumptions extends BaseDCFAssumptions {
  model_type: DCFModelType.IT_SERVICES_DCF;
  
  // IT Services specific parameters
  revenue_growth_rate: number;            // Client acquisition + pricing (5-30%)
  ebitda_margin: number;                  // Service margin optimization (15-35%)
  
  // IT-specific operational metrics
  employee_utilization_rate: number;      // Billable hours efficiency (75-85%)
  wage_inflation_rate: number;            // Annual salary increases (6-12%)
  attrition_rate: number;                 // Employee turnover (10-25%)
  
  // Client and market parameters
  client_concentration_risk: number;      // Top client dependency (20-40%)
  offshore_onshore_mix: number;          // Cost arbitrage (60-80% offshore)
  digital_transformation_premium: number; // Premium for digital services (10-25%)
  
  // Traditional DCF parameters
  tax_rate: number;
  wacc: number;
  terminal_growth_rate: number;
  capex_percentage: number;               // Lower for services (1-3%)
  working_capital_percentage: number;
}

// =============================================================================
// TRADITIONAL VALUATION MODELS
// =============================================================================

export interface GenericDCFAssumptions extends BaseDCFAssumptions {
  model_type: DCFModelType.GENERIC_DCF;
  
  // Standard 5-year DCF parameters
  revenue_growth_rate: number;            // (0-30%)
  ebitda_margin: number;                  // (5-40%)
  tax_rate: number;                       // (15-35%)
  wacc: number;                           // (8-18%)
  terminal_growth_rate: number;           // (1-6%)
  projection_years: 5;                    // Fixed at 5 years
  
  // Working capital parameters
  capex_percentage: number;               // (1-15%)
  working_capital_percentage: number;     // (-5% to +10%)
}

export interface PEValuationAssumptions extends BaseDCFAssumptions {
  model_type: DCFModelType.PE_VALUATION;
  
  // Multiple-based parameters
  industry_pe_multiple: number;           // Peer group average (8-35x)
  growth_premium_adjustment: number;      // Premium for growth (0-30%)
  quality_premium_adjustment: number;     // Premium for quality (0-20%)
  
  // Earnings parameters
  earnings_growth_rate: number;           // EPS growth assumption (5-25%)
  payout_ratio: number;                   // Dividend payout (0-60%)
  dividend_yield_expectation: number;     // Expected dividend yield (0-8%)
  
  // Valuation adjustments
  liquidity_discount: number;             // Small cap discount (0-15%)
  governance_premium: number;             // Good governance premium (0-10%)
}

export interface EVEBITDAAssumptions extends BaseDCFAssumptions {
  model_type: DCFModelType.EV_EBITDA;
  
  // EV/EBITDA multiple parameters
  industry_ev_ebitda_multiple: number;    // Peer group average (6-20x)
  ebitda_growth_rate: number;             // EBITDA growth assumption (5-20%)
  ebitda_margin: number;                  // Current EBITDA margin (10-40%)
  
  // Capital structure adjustments
  net_debt_adjustment: number;            // Net debt/cash position
  minority_interest_adjustment: number;   // Minority stakes
  
  // Enterprise value parameters
  revenue_growth_rate: number;            // For EBITDA calculation
  capex_sustainability: number;          // Maintenance capex (2-8%)
  working_capital_efficiency: number;     // Working capital optimization
}

// =============================================================================
// UNION TYPE AND DEFAULTS
// =============================================================================

// Union type for all model assumptions
export type DCFModelAssumptions = 
  | MultiStageSimpleDCFAssumptions
  | MultiStageAgenticDCFAssumptions
  | BankingDCFAssumptions
  | PharmaDCFAssumptions
  | RealEstateDCFAssumptions
  | ITServicesDCFAssumptions
  | GenericDCFAssumptions
  | PEValuationAssumptions
  | EVEBITDAAssumptions;

// Default interface extended for all models
export interface DCFModelDefaults extends BaseDCFAssumptions {
  current_price: number;
  rationale: Record<string, string>;
  data_sources: Record<string, string>;
  confidence_scores: Record<string, number>;
}

// Model identification helper
export const DCFModelLabels: Record<DCFModelType, string> = {
  [DCFModelType.MULTI_STAGE_SIMPLE]: '10-Year DCF (Simple Mode)',
  [DCFModelType.MULTI_STAGE_AGENTIC]: '10-Year DCF (Agentic Mode)',
  [DCFModelType.BANKING_DCF]: 'Banking DCF (Excess Return)',
  [DCFModelType.PHARMA_DCF]: 'Pharma DCF (R&D Pipeline)',
  [DCFModelType.REAL_ESTATE_DCF]: 'Real Estate DCF (NAV-based)',
  [DCFModelType.IT_SERVICES_DCF]: 'IT Services DCF',
  [DCFModelType.GENERIC_DCF]: 'Generic DCF (5-Year)',
  [DCFModelType.PE_VALUATION]: 'P/E Multiple Valuation',
  [DCFModelType.EV_EBITDA]: 'EV/EBITDA Valuation'
};

// Sector to model mapping
export const SectorToDCFModel: Record<string, DCFModelType> = {
  'BFSI': DCFModelType.BANKING_DCF,
  'PHARMA': DCFModelType.PHARMA_DCF,
  'REAL ESTATE': DCFModelType.REAL_ESTATE_DCF,
  'IT': DCFModelType.IT_SERVICES_DCF,
  'INFORMATION TECHNOLOGY': DCFModelType.IT_SERVICES_DCF
};