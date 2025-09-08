import axios from 'axios';
import type {
  CompanyAnalysis,
  DCFResponse,
  DCFDefaults,
  FinancialData,
  DCFAssumptions,
  SensitivityAnalysis
} from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`Enhanced API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('Enhanced API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('Enhanced API Response Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// Additional types for enhanced features
export interface IntradayDataPoint {
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface IntradayResponse {
  ticker: string;
  interval: string;
  data: IntradayDataPoint[];
  count: number;
  source: string;
}

export interface MarketDepthData {
  symbol: string;
  timestamp: string;
  depth: {
    buy: Array<{ price: number; quantity: number; orders: number }>;
    sell: Array<{ price: number; quantity: number; orders: number }>;
  };
  circuit_limits: {
    upper: number | null;
    lower: number | null;
  };
}

export interface SearchResult {
  symbol: string;
  name: string;
  exchange: string;
  instrument_type: string;
  last_price: number;
}

export interface SearchResponse {
  query: string;
  results: SearchResult[];
  count: number;
  total_found: number;
  source: string;
}

export interface DataSourceStatus {
  kite_available: boolean;
  yfinance_available: boolean;
  enhanced_mode: boolean;
}

export interface RealTimeMetrics {
  ticker: string;
  timestamp: string;
  current_price: number;
  change: number;
  change_percent: number;
  volume: number;
  day_open?: number;
  day_high?: number;
  day_low?: number;
  price_to_sales?: number;
  market_cap?: number;
  intraday_data_points?: number;
  source: DataSourceStatus;
}

export class EnhancedApiService {
  // Data Source Status
  static async getDataSourceStatus(): Promise<DataSourceStatus> {
    const response = await api.get<DataSourceStatus>('/api/v2/company/status');
    return response.data;
  }

  // Enhanced Company Analysis Endpoints
  static async getEnhancedCompanyAnalysis(ticker: string): Promise<CompanyAnalysis> {
    const response = await api.get<CompanyAnalysis>(`/api/v2/company/${ticker}`);
    return response.data;
  }

  static async getEnhancedCompanyInfo(ticker: string) {
    const response = await api.get(`/api/v2/company/${ticker}/info`);
    return response.data;
  }

  static async getEnhancedStockPrice(ticker: string) {
    const response = await api.get(`/api/v2/company/${ticker}/price`);
    return response.data;
  }

  // Real-time Market Data (Kite-specific features)
  static async getIntradayData(
    ticker: string, 
    interval: '1minute' | '3minute' | '5minute' | '15minute' | '30minute' | '60minute' = '5minute'
  ): Promise<IntradayResponse> {
    const response = await api.get<IntradayResponse>(
      `/api/v2/company/${ticker}/intraday`,
      { params: { interval } }
    );
    return response.data;
  }

  static async getMarketDepth(ticker: string): Promise<MarketDepthData | null> {
    const response = await api.get<MarketDepthData>(`/api/v2/company/${ticker}/market-depth`);
    return response.data;
  }

  static async getMultipleQuotes(tickers: string[]) {
    const response = await api.post('/api/v2/company/quotes', tickers);
    return response.data;
  }

  static async searchSymbols(query: string, limit: number = 20): Promise<SearchResponse> {
    const response = await api.get<SearchResponse>(
      `/api/v2/company/search/${encodeURIComponent(query)}`,
      { params: { limit } }
    );
    return response.data;
  }

  static async getMarketStatus() {
    const response = await api.get('/api/v2/company/market/status');
    return response.data;
  }

  static async getPortfolioHoldings() {
    const response = await api.get('/api/v2/company/portfolio/holdings');
    return response.data;
  }

  // Enhanced DCF Valuation Endpoints
  static async getEnhancedFinancialData(ticker: string, years: number = 5): Promise<FinancialData> {
    const response = await api.get<FinancialData>(`/api/v2/valuation/${ticker}/financials`, {
      params: { years }
    });
    return response.data;
  }

  static async getEnhancedDCFDefaults(ticker: string): Promise<DCFDefaults> {
    const response = await api.get<DCFDefaults>(`/api/v2/valuation/${ticker}/defaults`);
    return response.data;
  }

  static async calculateEnhancedDCF(ticker: string, assumptions: DCFAssumptions): Promise<DCFResponse> {
    const response = await api.post<DCFResponse>('/api/v2/valuation/dcf', assumptions, {
      params: { ticker }
    });
    return response.data;
  }

  static async quickEnhancedDCFCalculation(
    ticker: string,
    overrides: Partial<DCFAssumptions> = {}
  ) {
    const params = new URLSearchParams();
    Object.entries(overrides).forEach(([key, value]) => {
      if (value !== undefined) {
        params.append(key, value.toString());
      }
    });

    const response = await api.post(`/api/v2/valuation/${ticker}/quick-dcf?${params.toString()}`);
    return response.data;
  }

  static async getEnhancedSensitivityAnalysis(ticker: string): Promise<SensitivityAnalysis> {
    const response = await api.get<SensitivityAnalysis>(`/api/v2/valuation/${ticker}/sensitivity`);
    return response.data;
  }

  static async getRealTimeValuationMetrics(ticker: string): Promise<RealTimeMetrics> {
    const response = await api.get<RealTimeMetrics>(`/api/v2/valuation/${ticker}/real-time-metrics`);
    return response.data;
  }

  static async getPeerComparison(ticker: string, peers?: string[]) {
    const params = peers ? { peers: peers.join(',') } : {};
    const response = await api.get(`/api/v2/valuation/${ticker}/comparison`, { params });
    return response.data;
  }

  // Kite Authentication Helpers
  static async getKiteLoginUrl() {
    const response = await api.get('/api/v2/company/kite/login-url');
    return response.data;
  }

  static async setKiteTokens(requestToken?: string, accessToken?: string) {
    const response = await api.post('/api/v2/company/kite/set-tokens', {
      request_token: requestToken,
      access_token: accessToken
    });
    return response.data;
  }

  // Utility Methods
  static async testConnection(): Promise<boolean> {
    try {
      await api.get('/health');
      return true;
    } catch (error) {
      console.error('API connection test failed:', error);
      return false;
    }
  }

  static async getApiInfo() {
    const response = await api.get('/');
    return response.data;
  }

  static async getDataSourcesInfo() {
    const response = await api.get('/api/data-sources');
    return response.data;
  }

  // Batch operations for performance
  static async batchQuoteRequest(tickers: string[], batchSize: number = 10) {
    const results: Record<string, any> = {};
    
    for (let i = 0; i < tickers.length; i += batchSize) {
      const batch = tickers.slice(i, i + batchSize);
      try {
        const batchResults = await this.getMultipleQuotes(batch);
        Object.assign(results, batchResults.quotes);
        
        // Small delay between batches to respect rate limits
        if (i + batchSize < tickers.length) {
          await new Promise(resolve => setTimeout(resolve, 100));
        }
      } catch (error) {
        console.error(`Error fetching batch ${i}-${i + batchSize}:`, error);
        // Mark failed tickers as null
        batch.forEach(ticker => {
          results[ticker] = null;
        });
      }
    }
    
    return results;
  }

  // WebSocket connection for real-time updates (future implementation)
  static createWebSocketConnection(tickers: string[], onUpdate: (data: any) => void) {
    // This would be implemented when WebSocket support is added
    console.log('WebSocket connection not yet implemented');
    return null;
  }
}

export default EnhancedApiService;