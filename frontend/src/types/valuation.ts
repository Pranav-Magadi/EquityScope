// Valuation Models Types
// TypeScript interfaces for multiple valuation approaches

export type ValuationMethod = 
  | 'sector_dcf'
  | 'generic_dcf'
  | 'pe_multiple'
  | 'ev_ebitda'
  | 'peg_ratio'
  | 'price_to_book'
  | 'dividend_discount';

export interface ModelAssumptions {
  growth_assumptions: Record<string, string>;
  risk_assumptions: Record<string, string>;
  terminal_assumptions: Record<string, string>;
  sector_specific: Record<string, string>;
}

export interface ValuationModelResponse {
  model_id: string;
  model_name: string;
  ticker: string;
  
  // Valuation Results
  fair_value: number;
  current_price: number;
  upside_downside_pct: number;
  confidence: number;
  
  // Methodology
  method: string;
  assumptions: ModelAssumptions;
  key_factors: string[];
  
  // Metadata
  calculation_timestamp: string;
  data_sources: string[];
  limitations: string[];
}

export interface ValuationSummary {
  ticker: string;
  current_price: number;
  fair_value_range: {
    min: number;
    max: number;
    mean: number;
    median: number;
  };
  upside_range: {
    min: number;
    max: number;
    mean: number;
  };
  consensus_confidence: number;
  model_agreement: number;
  calculation_timestamp: string;
}

export interface ValuationComparison {
  ticker: string;
  models: Record<string, ValuationModelResponse>;
  summary: ValuationSummary;
  warnings: string[];
  recommendation: string;
}

export interface GenericDCFResult {
  ticker: string;
  fair_value: number;
  current_price: number;
  upside_downside_pct: number;
  confidence: number;
  dcf_method: string;
  
  // DCF Components
  terminal_value: number;
  total_pv_fcf: number;
  net_debt: number;
  shares_outstanding: number;
  
  // Key Metrics
  wacc: number;
  terminal_growth_rate: number;
  forecast_years: number;
  
  reasoning: string[];
  assumptions: Record<string, any>;
}

export interface MultiplesResult {
  ticker: string;
  fair_value: number;
  current_price: number;
  upside_downside_pct: number;
  confidence: number;
  method: string;
  
  // Multiple Details
  applied_multiple: number;
  peer_multiples: Record<string, number>;
  industry_median: number;
  
  // Quality Adjustments
  quality_premium_discount: number;
  
  reasoning: string[];
  assumptions: Record<string, any>;
}

export interface ValuationModel {
  id: string;
  name: string;
  description: string;
  icon: string;
  category: 'sector' | 'generic' | 'multiples';
  available: boolean;
}

export interface ValuationRequest {
  ticker: string;
  models?: string[];
  force_refresh?: boolean;
}

export interface ModelParameterOverride {
  model_id: string;
  parameters: Record<string, any>;
}

export interface CustomValuationRequest extends ValuationRequest {
  parameter_overrides?: ModelParameterOverride[];
  include_scenarios?: boolean;
}

// UI State Types
export interface ValuationState {
  activeModel: string;
  models: ValuationModel[];
  results: Record<string, ValuationModelResponse>;
  comparison?: ValuationComparison;
  isLoading: Record<string, boolean>;
  errors: Record<string, string>;
}

export interface ValuationCardProps {
  ticker: string;
  summaryData: any; // SummaryResponse type
}

// Chart Data Types
export interface ValuationChartData {
  model: string;
  fairValue: number;
  currentPrice: number;
  upside: number;
  confidence: number;
}

export interface ModelComparisonData {
  models: string[];
  fairValues: number[];
  confidences: number[];
  upsides: number[];
}

// Error Types
export interface ValuationError {
  model_id: string;
  error_type: 'data_unavailable' | 'calculation_failed' | 'network_error';
  message: string;
  retry_available: boolean;
}