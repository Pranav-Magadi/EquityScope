// EquityScope v3 Summary Engine API Service
import type { SummaryResponse, AnalysisMode } from '../types/summary';

class V3ApiService {
  private baseUrl = 'http://localhost:8000/api/v3';

  async getSummary(ticker: string, mode: AnalysisMode = 'simple'): Promise<SummaryResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/summary/${ticker}/${mode}`);
      
      if (!response.ok) {
        throw new Error(`API Error: ${response.status} ${response.statusText}`);
      }
      
      const data = await response.json();
      return data;
    } catch (error) {
      console.error(`Error fetching ${mode} summary for ${ticker}:`, error);
      throw error;
    }
  }

  async getSimpleSummary(ticker: string): Promise<SummaryResponse> {
    return this.getSummary(ticker, 'simple');
  }

  async getAgenticSummary(ticker: string): Promise<SummaryResponse> {
    return this.getSummary(ticker, 'agentic');
  }

  async getPeerAnalysis(ticker: string, targetCount: number = 5): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/peers/${ticker}?target_count=${targetCount}`);
      
      if (!response.ok) {
        throw new Error(`API Error: ${response.status} ${response.statusText}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error(`Error fetching peer analysis for ${ticker}:`, error);
      throw error;
    }
  }

  async getBatchSummaries(tickers: string[], mode: AnalysisMode = 'simple'): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/summary/batch?mode=${mode}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ tickers }),
      });
      
      if (!response.ok) {
        throw new Error(`API Error: ${response.status} ${response.statusText}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error(`Error fetching batch summaries:`, error);
      throw error;
    }
  }

  async healthCheck(): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/health`);
      
      if (!response.ok) {
        throw new Error(`API Error: ${response.status} ${response.statusText}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error checking v3 API health:', error);
      throw error;
    }
  }

  // Mock data for development/demo purposes
  getMockSummary(ticker: string, mode: AnalysisMode = 'simple'): SummaryResponse {
    return {
      ticker: ticker,
      company_name: `${ticker.replace('.NS', '')} Limited`,
      fair_value_band: {
        min_value: 200,
        max_value: 250,
        current_price: 220,
        method: mode === 'simple' ? 'PE_Multiple' : 'DCF',
        confidence: mode === 'simple' ? 0.7 : 0.8
      },
      investment_label: 'Cautiously Bullish',
      key_factors: [
        'Moderately undervalued vs fair value',
        'Strong fundamentals with consistent growth',
        'Favorable sector tailwinds'
      ],
      valuation_insights: mode === 'simple' 
        ? 'PE ratio of 18.5x is attractive vs sector average of 22x. Current price offers 15% upside to fair value.'
        : 'DCF analysis indicates intrinsic value of ₹235 per share. Company trades at discount due to temporary margin pressures, which are expected to normalize.',
      market_signals: 'RSI at 45 indicates neutral momentum. Volume trends suggest accumulation by institutional investors.',
      business_fundamentals: 'Revenue growth of 12% CAGR over 3 years. Strong return ratios with ROE of 18%. Management guidance indicates continued expansion.',
      data_health_warnings: mode === 'simple' 
        ? []
        : ['Using cached peer data (2 hours old)', 'Technical indicators partially unavailable'],
      analysis_timestamp: new Date().toISOString(),
      analysis_mode: mode,
      sector: 'Technology'
    };
  }
}

export const v3ApiService = new V3ApiService();