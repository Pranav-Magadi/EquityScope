import axios from 'axios';
import type {
  CompanyAnalysis,
  DCFResponse,
  DCFDefaults,
  FinancialData,
  DCFAssumptions,
  SensitivityAnalysis,
  MultiStageDCFResponse,
  ModeSelectionRequest,
  ModeRecommendationResponse,
  DCFMode
} from '../types';
import type {
  SummaryResponse,
  SimpleSummaryResponse,
  AgenticSummaryResponse,
  AnalysisMode
} from '../types/summary';
import type {
  ValuationModelResponse,
  ValuationComparison
  // GenericDCFResult, MultiplesResult, ValuationRequest - used by API methods
} from '../types/valuation';

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
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Response Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export class ApiService {
  // Company Analysis Endpoints
  static async getCompanyAnalysis(ticker: string): Promise<CompanyAnalysis> {
    const response = await api.get<CompanyAnalysis>(`/api/company/${ticker}`);
    return response.data;
  }

  static async getBasicCompanyData(ticker: string) {
    const response = await api.get(`/api/company/${ticker}/basic`);
    return response.data;
  }

  static async getCompanyInfo(ticker: string) {
    const response = await api.get(`/api/company/${ticker}/info`);
    return response.data;
  }

  static async getStockPrice(ticker: string) {
    const response = await api.get(`/api/company/${ticker}/price`);
    return response.data;
  }

  static async getSWOTAnalysis(ticker: string) {
    const response = await api.get(`/api/company/${ticker}/swot`);
    return response.data;
  }

  static async getNewsSentiment(ticker: string) {
    const response = await api.get(`/api/company/${ticker}/sentiment`);
    return response.data;
  }

  static async getMarketLandscape(ticker: string) {
    const response = await api.get(`/api/company/${ticker}/market`);
    return response.data;
  }

  static async getEmployeeSentiment(ticker: string) {
    const response = await api.get(`/api/company/${ticker}/employee`);
    return response.data;
  }

  // DCF Valuation Endpoints
  static async getFinancialData(ticker: string, years: number = 5): Promise<FinancialData> {
    const response = await api.get<FinancialData>(`/api/valuation/${ticker}/financials`, {
      params: { years }
    });
    return response.data;
  }

  static async getDCFDefaults(ticker: string, sector?: string): Promise<DCFDefaults> {
    const params = sector ? { sector } : {};
    const response = await api.get<DCFDefaults>(`/api/valuation/${ticker}/defaults`, { params });
    return response.data;
  }

  static async calculateDCF(ticker: string, assumptions: DCFAssumptions): Promise<DCFResponse> {
    const response = await api.post<DCFResponse>('/api/valuation/dcf', assumptions, {
      params: { ticker }
    });
    return response.data;
  }

  static async quickDCFCalculation(
    ticker: string,
    overrides: Partial<DCFAssumptions> = {}
  ) {
    const params = new URLSearchParams();
    Object.entries(overrides).forEach(([key, value]) => {
      if (value !== undefined) {
        params.append(key, value.toString());
      }
    });

    const response = await api.post(`/api/valuation/${ticker}/quick-dcf?${params.toString()}`);
    return response.data;
  }

  static async getSensitivityAnalysis(ticker: string): Promise<SensitivityAnalysis> {
    const response = await api.get<SensitivityAnalysis>(`/api/valuation/${ticker}/sensitivity`);
    return response.data;
  }

  // 10-Year Multi-Stage DCF Endpoints
  static async getModeRecommendation(request: ModeSelectionRequest): Promise<ModeRecommendationResponse> {
    const response = await api.post<ModeRecommendationResponse>('/api/v2/mode-recommendation', request);
    return response.data;
  }

  static async calculateMultiStageDCF(
    ticker: string, 
    mode: DCFMode, 
    projection_years: number = 10
  ): Promise<MultiStageDCFResponse> {
    const response = await api.post<MultiStageDCFResponse>('/api/v2/multi-stage-dcf', {
      ticker,
      mode,
      projection_years
    });
    return response.data;
  }

  // V3 Mode-Based Analysis Endpoints
  static async getV3SimpleSummary(ticker: string, forceRefresh: boolean = false): Promise<SimpleSummaryResponse> {
    const response = await api.get<SimpleSummaryResponse>(`/api/v3/summary/${ticker}/simple`, {
      params: { force_refresh: forceRefresh }
    });
    return response.data;
  }

  static async getV3AgenticSummary(ticker: string, forceRefresh: boolean = false): Promise<AgenticSummaryResponse> {
    const response = await api.get<AgenticSummaryResponse>(`/api/v3/summary/${ticker}/agentic`, {
      params: { force_refresh: forceRefresh }
    });
    return response.data;
  }

  static async getV3Summary(
    ticker: string, 
    mode: AnalysisMode = 'simple', 
    forceRefresh: boolean = false
  ): Promise<SummaryResponse> {
    const response = await api.get<SummaryResponse>(`/api/v3/summary/${ticker}`, {
      params: { mode, force_refresh: forceRefresh }
    });
    return response.data;
  }

  static async getV3PeerComparison(ticker: string) {
    const response = await api.get(`/api/v3/peers/${ticker}`);
    return response.data;
  }

  static async batchV3Analysis(tickers: string[], mode: AnalysisMode = 'simple') {
    const response = await api.post('/api/v3/summary/batch', {
      tickers,
      mode
    });
    return response.data;
  }

  static async getV3SupportedSectors() {
    const response = await api.get('/api/v3/sectors');
    return response.data;
  }

  // Health Check
  static async healthCheck() {
    const response = await api.get('/health');
    return response.data;
  }

  // ===== VALUATION MODELS API =====

  // Get available valuation models for a ticker
  static async getAvailableModels(ticker: string): Promise<string[]> {
    const response = await api.get(`/api/valuation/${ticker}/models`);
    return response.data;
  }

  // Calculate sector-specific DCF
  static async calculateSectorDCF(
    ticker: string, 
    mode: AnalysisMode = 'simple', 
    forceRefresh: boolean = false
  ): Promise<ValuationModelResponse> {
    const response = await api.get(`/api/valuation/${ticker}/sector-dcf`, {
      params: { mode, force_refresh: forceRefresh }
    });
    return response.data;
  }

  // Calculate generic DCF
  static async calculateGenericDCF(
    ticker: string,
    forecastYears: number = 10,
    forceRefresh: boolean = false
  ): Promise<ValuationModelResponse> {
    const response = await api.get(`/api/valuation/${ticker}/generic-dcf`, {
      params: { forecast_years: forecastYears, force_refresh: forceRefresh }
    });
    return response.data;
  }

  // Calculate P/E based valuation
  static async calculatePEValuation(
    ticker: string,
    forceRefresh: boolean = false
  ): Promise<ValuationModelResponse> {
    const response = await api.get(`/api/valuation/${ticker}/pe-valuation`, {
      params: { force_refresh: forceRefresh }
    });
    return response.data;
  }

  // Calculate EV/EBITDA based valuation
  static async calculateEVEBITDAValuation(
    ticker: string,
    forceRefresh: boolean = false
  ): Promise<ValuationModelResponse> {
    const response = await api.get(`/api/valuation/${ticker}/ev-ebitda`, {
      params: { force_refresh: forceRefresh }
    });
    return response.data;
  }

  // Compare multiple valuation models
  static async compareValuationModels(
    ticker: string,
    models?: string[],
    forceRefresh: boolean = false
  ): Promise<ValuationComparison> {
    const params: any = { force_refresh: forceRefresh };
    if (models && models.length > 0) {
      params.models = models;
    }
    
    const response = await api.get(`/api/valuation/${ticker}/comparison`, { params });
    return response.data;
  }

  // Calculate specific valuation model by ID
  static async calculateValuationModel(
    ticker: string,
    modelId: string,
    options: { forceRefresh?: boolean; parameters?: Record<string, any> } = {}
  ): Promise<ValuationModelResponse> {
    const { forceRefresh = false } = options;
    
    switch (modelId) {
      case 'sector_dcf':
        return this.calculateSectorDCF(ticker, 'simple', forceRefresh);
      case 'generic_dcf':
        return this.calculateGenericDCF(ticker, 10, forceRefresh);
      case 'pe_valuation':
        return this.calculatePEValuation(ticker, forceRefresh);
      case 'ev_ebitda':
        return this.calculateEVEBITDAValuation(ticker, forceRefresh);
      default:
        throw new Error(`Unknown valuation model: ${modelId}`);
    }
  }

  // DCF AI Insights Service
  static async getDCFInsights(
    ticker: string,
    dcfResult: any,
    assumptions: any,
    companyData: any,
    forceRefresh: boolean = false
  ): Promise<any> {
    const response = await api.post(`/api/dcf/insights/${ticker}?force_refresh=${forceRefresh}`, {
      dcf_result: dcfResult,
      assumptions: assumptions,
      company_data: companyData
    });
    return response.data;
  }

  // API Key Management
  static async updateApiKeys(config: any): Promise<any> {
    const response = await api.post('/api/settings/api-keys', config);
    return response.data;
  }

  static async getApiKeyStatus(): Promise<any> {
    const response = await api.get('/api/settings/api-keys/status');
    return response.data;
  }

  // Enhanced News Service Endpoints
  static async getEnhancedNewsAnalysis(
    ticker: string, 
    days: number = 30,
    forceRefresh: boolean = false
  ) {
    const response = await api.get(`/api/news/analysis/${ticker}`, {
      params: { days, force_refresh: forceRefresh }
    });
    return response.data;
  }

  static async getRecentNewsArticles(
    ticker: string, 
    limit: number = 10,
    days: number = 7
  ) {
    const response = await api.get(`/api/news/articles/${ticker}`, {
      params: { limit, days }
    });
    return response.data;
  }

  static async getCompanyReports(
    ticker: string,
    limit: number = 5,
    types?: string[]
  ) {
    const params: any = { limit };
    if (types && types.length > 0) {
      params.types = types.join(',');
    }
    
    const response = await api.get(`/api/news/company-reports/${ticker}`, { params });
    return response.data;
  }

  static async getIndustryReports(
    ticker: string,
    limit: number = 5,
    sector?: string
  ) {
    const params: any = { limit };
    if (sector) {
      params.sector = sector;
    }
    
    const response = await api.get(`/api/news/industry-reports/${ticker}`, { params });
    return response.data;
  }
}

export default ApiService;

// Export the NewsService for direct use in components
export { NewsService } from './newsService';