// EquityScope v3 Summary Engine Types
// Based on Architecture Migration Strategy

export type InvestmentLabel = 
  | "Strongly Bullish" 
  | "Cautiously Bullish" 
  | "Neutral" 
  | "Cautiously Bearish" 
  | "Strongly Bearish";

export interface FairValueBand {
  min_value: number;
  max_value: number;
  current_price: number;
  method: "DCF" | "PE_Multiple" | "Sector_Average";
  confidence: number; // 0.0 to 1.0
}

export interface SummaryResponse {
  ticker: string;
  company_name: string;
  fair_value_band: FairValueBand;
  investment_label: InvestmentLabel;
  key_factors: string[];
  
  // Three lens analysis
  valuation_insights: string;
  market_signals: string;
  business_fundamentals: string;
  
  // Metadata
  data_health_warnings: string[];
  analysis_timestamp: string;
  analysis_mode: "simple" | "agentic";
  sector: string;
  
  // v3 Weighted scoring (optional, for simple mode)
  weighted_score?: number;
  component_scores?: {
    dcf_score: number;
    financial_score: number;
    technical_score: number;
    peer_score: number;
  };
}

export type AnalysisMode = "simple" | "agentic";

// Simplified v3 App State (replacing complex v2 state)
export interface AppState {
  // Core summary state
  currentTicker: string;
  summaryData: SummaryResponse | null;
  analysisMode: AnalysisMode;
  isLoading: boolean;
  error: string | null;
}

// Extended response types for specific modes
export interface SimpleSummaryResponse extends SummaryResponse {
  rules_applied: string[];
  fallback_triggers: string[];
  weighted_score?: number;
  component_scores?: {
    dcf_score: number;
    financial_score: number;
    technical_score: number;
    peer_score: number;
  };
}

export interface AgenticSummaryResponse extends SummaryResponse {
  agent_reasoning?: string;
  cost_breakdown?: any;
  model_version?: string;
}