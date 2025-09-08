// Company Analysis Types
export interface CompanyInfo {
  ticker: string;
  name: string;
  sector: string;
  industry: string;
  market_cap?: number;
  current_price?: number;
  currency: string;
  exchange: string;
}

export interface StockPrice {
  current_price: number;
  change: number;
  change_percent: number;
  volume: number;
  market_cap: number;
  pe_ratio?: number;
  pb_ratio?: number;
}

export interface SWOTAnalysis {
  strengths: string[];
  weaknesses: string[];
  opportunities: string[];
  threats: string[];
}

export interface NewsSentiment {
  headlines: string[];
  sentiment_score: number;
  sentiment_label: string;
  news_count: number;
  last_updated: string;
}

export interface CompetitiveComparison {
  financial: {
    score: 'stronger' | 'similar' | 'weaker';
    details: string;
    sources: string[];
  };
  technological: {
    score: 'stronger' | 'similar' | 'weaker';
    details: string;
    sources: string[];
  };
  operational: {
    score: 'stronger' | 'similar' | 'weaker';
    details: string;
    sources: string[];
  };
  governance: {
    score: 'stronger' | 'similar' | 'weaker';
    details: string;
    sources: string[];
  };
}

export interface CompetitivePeer {
  name: string;
  ticker: string;
  comparison: CompetitiveComparison;
}

export interface CompetitiveAnalysis {
  peers: CompetitivePeer[];
  competitive_positioning: string;
  key_competitive_advantages: string[];
  competitive_threats: string[];
}

export interface MarketLandscape {
  competitors: Array<{
    name: string;
    market_cap: number;
    market_share: number;
    growth_rate: number;
  }>;
  market_share?: number;
  industry_trends: string[];
  market_position: string;
}

export interface EmployeeSentiment {
  rating: number;
  review_count: number;
  pros: string[];
  cons: string[];
  sentiment_summary: string;
}

export interface CompanyAnalysis {
  company_info: CompanyInfo;
  stock_price: StockPrice;
  swot: SWOTAnalysis;
  news_sentiment: NewsSentiment;
  market_landscape: MarketLandscape;
  employee_sentiment: EmployeeSentiment;
}

// DCF Valuation Types
export interface FinancialData {
  ticker: string;
  years: number[];
  revenue: number[];
  ebitda: number[];
  net_income: number[];
  free_cash_flow: number[];
  total_debt: number[];
  cash: number[];
  shares_outstanding: number[];
  // Capital intensity metrics for dynamic calculations
  capex: number[];
  working_capital_change: number[];
  depreciation_amortization: number[];
}

export interface DCFAssumptions {
  revenue_growth_rate: number;
  ebitda_margin: number;
  tax_rate: number;
  wacc: number;
  terminal_growth_rate: number;
  projection_years?: number;
}

export interface DCFProjection {
  year: number;
  revenue: number;
  ebitda: number;
  ebit: number;
  tax: number;
  nopat: number;
  capex: number;
  working_capital_change: number;
  free_cash_flow: number;
  present_value: number;
}

export interface DCFValuation {
  intrinsic_value_per_share: number;
  terminal_value: number;
  enterprise_value: number;
  equity_value: number;
  current_stock_price: number;
  upside_downside: number;
  projections: DCFProjection[];
  assumptions: DCFAssumptions;
}

export interface SensitivityAnalysis {
  wacc_range: number[];
  terminal_growth_range: number[];
  sensitivity_matrix: number[][];
}

export interface DCFDefaults {
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
  current_price: number;
  rationale: Record<string, string>;
  // Normalization System flags
  normalized_capex_rate?: number;
  requires_normalization?: boolean;
}

export interface DCFResponse {
  valuation: DCFValuation;
  sensitivity: SensitivityAnalysis;
  financial_data: FinancialData;
  last_updated: string;
}

// UI State Types
export interface LoadingState {
  isLoading: boolean;
  error?: string;
}

export interface DashboardState {
  ticker?: string;
  companyAnalysis?: CompanyAnalysis | import('../types/summary').SummaryResponse;
  dcfResponse?: DCFResponse;
  dcfDefaults?: DCFDefaults;
  loadingStates: {
    company: LoadingState;
    dcf: LoadingState;
  };
}

// Form Types
export interface DCFFormData {
  revenue_growth_rate: string;
  ebitda_margin: string;
  tax_rate: string;
  wacc: string;
  terminal_growth_rate: string;
}

// Chart Data Types
export interface ChartDataPoint {
  name: string;
  value: number;
  year?: number;
}

export interface ProjectionChartData {
  year: number;
  revenue: number;
  ebitda: number;
  free_cash_flow: number;
  present_value: number;
}

// AI Investment Committee Types
export interface ValidationReport {
  overall_score: number;
  qualitative_validation: {
    swot_accuracy: string;
    news_interpretation: string;
    source_quality: string;
    findings: string[];
  };
  quantitative_validation: {
    dcf_assumptions_reasonableness: string;
    sensitivity_range_appropriateness: string;
    calculation_accuracy: string;
    findings: string[];
  };
  key_concerns: string[];
  recommendations: string[];
}

export interface AssumptionModification {
  assumption: string;
  current_value: number;
  recommended_value: number;
  justification: string;
}

export interface BullCommentary {
  summary_of_assumptions: string;
  bullish_implications: string;
  recommended_modifications: AssumptionModification[];
  upside_catalysts: string[];
  target_price_scenario: string;
}

export interface BearCommentary {
  summary_of_assumptions: string;
  bearish_implications: string;
  recommended_modifications: AssumptionModification[];
  downside_risks: string[];
  conservative_price_scenario: string;
}

export interface InvestmentCommitteeData {
  validation_report: ValidationReport;
  bull_commentary: BullCommentary;
  bear_commentary: BearCommentary;
}

// Technical Analysis Types
export interface TechnicalChartDataPoint {
  date: string;
  timestamp: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  sma_50?: number;
  sma_200?: number;
  bb_upper?: number;
  bb_lower?: number;
  bb_middle?: number;
  rsi?: number;
  // MACD indicators
  macd_line?: number;
  macd_signal?: number;
  macd_histogram?: number;
  // Stochastic indicators
  stoch_k?: number;
  stoch_d?: number;
  // Volume indicators
  volume_sma?: number;
  obv?: number; // On-Balance Volume
}

export interface TechnicalIndicatorValues {
  current_price: number;
  rsi: number;
  price_vs_50d_sma: number;
  price_vs_200d_sma: number;
  support_level: number;
  resistance_level: number;
  sma_50_current: number;
  sma_200_current: number;
  sma_50_prev: number;
  sma_200_prev: number;
  bb_upper_current: number;
  bb_lower_current: number;
  bb_middle_current: number;
  // MACD values
  macd_current: number;
  macd_signal_current: number;
  macd_histogram_current: number;
  // Stochastic values
  stoch_k_current: number;
  stoch_d_current: number;
  // Volume analysis
  volume_trend: 'increasing' | 'decreasing' | 'neutral';
  obv_current: number;
  signals?: string[];
}

export interface TechnicalAnalysisData {
  ticker: string;
  period: string;
  chart_data: TechnicalChartDataPoint[];
  indicator_values: TechnicalIndicatorValues;
  analysis_timestamp: string;
  data_points: number;
  ai_summary?: string;
}

// 10-Year Multi-Stage DCF Types
export type DCFMode = 'simple' | 'agentic';

export interface GrowthStage {
  years: string;           // e.g., "1-2", "3-5", "6-8", "9-10", "terminal"
  start_year: number;
  end_year: number;
  growth_rate: number;     // Percentage
  method: string;          // e.g., "historical_cagr", "management_guidance", "gdp_convergence"
  gdp_weight: number;      // Weight of GDP growth in blending (0.0 to 1.0)
  confidence: 'high' | 'medium' | 'low';
  rationale: string;       // Explanation for this growth rate
}

export interface MultiStageAssumptions {
  mode: DCFMode;
  projection_years: number;
  growth_stages: GrowthStage[];
  gdp_growth_rate: number;
  wacc: number;
  terminal_growth_rate: number;
  tax_rate: number;
  ebitda_margin: number;
}

export interface MultiStageDCFProjection extends DCFProjection {
  revenue_growth_rate: number;
  growth_stage: string;
  growth_method: string;
}

export interface MultiStageDCFValuation extends DCFValuation {
  projections: MultiStageDCFProjection[];
  multi_stage_assumptions: MultiStageAssumptions;
  growth_waterfall: Record<string, number>;
}

export interface MultiStageDCFResponse {
  valuation: MultiStageDCFValuation;
  mode: DCFMode;
  growth_stages_summary: Array<{
    years: string;
    growth_rate: string;
    method: string;
    confidence: string;
    rationale: string;
  }>;
  education_content: {
    mode_explanation: string;
    growth_methodology: string;
    key_benefits: string;
    best_for: string;
  };
}

export interface ModeSelectionRequest {
  ticker: string;
  user_experience_level: 'beginner' | 'intermediate' | 'advanced';
}

export interface ModeRecommendationResponse {
  ticker: string;
  company_context: {
    sector: string;
    market_cap: number;
    market_cap_category: string;
  };
  mode_recommendation: {
    recommended_mode: DCFMode;
    confidence: 'high' | 'medium' | 'low';
    rationale: string;
  };
  mode_comparison: {
    simple_mode: {
      description: string;
      time_required: string;
      complexity: string;
    };
    agentic_mode: {
      description: string;
      time_required: string;
      complexity: string;
    };
  };
}