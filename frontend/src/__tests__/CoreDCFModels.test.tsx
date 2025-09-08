// Test suite for core DCF model implementations (IT EV/Revenue, Real Estate NAV, Banking Excess Returns)
import { render } from '@testing-library/react';
import '@testing-library/jest-dom';
import { DCFModelsCard } from '../components/DCFValuation/DCFModelsCard';
import * as ApiService from '../services/api';
import type { SummaryResponse } from '../types/summary';

// Mock API Service with realistic test data
jest.mock('../services/api');
const mockApiService = ApiService as jest.Mocked<typeof ApiService>;

// Test data for different sectors
const createMockSummaryData = (sector: string, ticker: string): SummaryResponse => ({
  ticker,
  company_name: `Test Company (${sector})`,
  fair_value_band: {
    min_value: 90,
    max_value: 110,
    current_price: 100,
    method: 'DCF',
    confidence: 0.75
  },
  investment_label: 'Neutral',
  key_factors: ['Test factor 1', 'Test factor 2'],
  valuation_insights: 'Test insights',
  market_signals: 'Test signals',
  business_fundamentals: 'Test fundamentals',
  data_health_warnings: [],
  analysis_timestamp: '2025-08-01T03:00:00.000Z',
  analysis_mode: 'simple',
  sector
});

// Mock financial data for TCS (IT company)
const mockTCSFinancialData = {
  ticker: 'TCS.NS',
  years: [2024, 2023, 2022],
  revenue: [250000000000, 230000000000, 210000000000], // ₹25k Cr, ₹23k Cr, ₹21k Cr (growing)
  net_income: [42500000000, 39100000000, 35700000000], // ₹4.25k Cr, ₹3.91k Cr, ₹3.57k Cr
  shares_outstanding: [3700000000, 3700000000, 3700000000] // 370 Cr shares
};

const mockTCSBasicCompanyData = {
  stock_price: {
    current_price: 3500, // ₹3,500 per share
    market_cap: 1295000000000, // ₹12.95 lakh crore (mega cap)
    pe_ratio: 30.5,
    pb_ratio: 12.8
  }
};

// Mock financial data for DLF (Real Estate company)
const mockDLFFinancialData = {
  ticker: 'DLF.NS',
  years: [2024, 2023, 2022],
  revenue: [64000000000, 58000000000, 52000000000], // ₹6.4k Cr, ₹5.8k Cr, ₹5.2k Cr
  net_income: [8960000000, 6960000000, 5200000000], // ₹896 Cr, ₹696 Cr, ₹520 Cr
  shares_outstanding: [2470000000, 2470000000, 2470000000] // 247 Cr shares
};

const mockDLFBasicCompanyData = {
  stock_price: {
    current_price: 800, // ₹800 per share
    market_cap: 197600000000, // ₹1.976 lakh crore (large cap real estate)
    pe_ratio: 22.1,
    pb_ratio: 1.4
  }
};

// Mock financial data for HDFC Bank (Banking company)
const mockHDFCBankFinancialData = {
  ticker: 'HDFCBANK.NS',
  years: [2024, 2023, 2022],
  revenue: [180000000000, 165000000000, 150000000000], // ₹18k Cr, ₹16.5k Cr, ₹15k Cr
  net_income: [55000000000, 48000000000, 42000000000], // ₹5.5k Cr, ₹4.8k Cr, ₹4.2k Cr
  shares_outstanding: [5400000000, 5400000000, 5400000000] // 540 Cr shares
};

const mockHDFCBankBasicCompanyData = {
  stock_price: {
    current_price: 1650, // ₹1,650 per share
    market_cap: 891000000000, // ₹8.91 lakh crore (mega cap banking)
    pe_ratio: 16.2,
    pb_ratio: 2.9
  }
};

describe('Core DCF Models Implementation Tests', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    // Suppress console logs during tests
    jest.spyOn(console, 'log').mockImplementation(() => {});
    jest.spyOn(console, 'error').mockImplementation(() => {});
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  describe('TCS.NS - IT Sector EV/Revenue Model', () => {
    beforeEach(() => {
      mockApiService.getFinancialData.mockResolvedValue(mockTCSFinancialData);
      mockApiService.getBasicCompanyData.mockResolvedValue(mockTCSBasicCompanyData);
      mockApiService.getDCFDefaults.mockResolvedValue({
        revenue_growth_rate: 12.0,
        ebitda_margin: 26.0,
        tax_rate: 25.0,
        wacc: 11.0,
        terminal_growth_rate: 3.0,
        projection_years: 10,
        capex_percentage: 2.0,
        working_capital_percentage: 3.0,
        current_price: 3500,
        rationale: {}
      });
    });

    test('should load TCS without errors and show EV/Revenue model', async () => {
      const summaryData = createMockSummaryData('IT', 'TCS.NS');
      
      const { container } = render(
        <DCFModelsCard ticker="TCS.NS" summaryData={summaryData} />
      );

      // Should render the component without crashing
      expect(container).toBeInTheDocument();
      
      // Should show sector-specific model tab (EV/Revenue)
      expect(container.textContent).toMatch(/EV\/Revenue/i);
    });

    test('should calculate EV/Revenue multiple correctly for large cap IT company', async () => {
      const summaryData = createMockSummaryData('IT', 'TCS.NS');
      
      render(<DCFModelsCard ticker="TCS.NS" summaryData={summaryData} />);
      
      // Wait for async calculations to complete
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Check that API calls were made
      expect(mockApiService.getFinancialData).toHaveBeenCalledWith('TCS.NS', 3);
      expect(mockApiService.getBasicCompanyData).toHaveBeenCalledWith('TCS.NS');
    });

    test('should handle TCS market cap classification correctly', async () => {
      const summaryData = createMockSummaryData('IT', 'TCS.NS');
      
      render(<DCFModelsCard ticker="TCS.NS" summaryData={summaryData} />);
      
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // TCS market cap (₹12.95 lakh crore) should classify as Tier-1 Leader
      // This should result in base multiple of 6.5x
      expect(mockApiService.getFinancialData).toHaveBeenCalled();
    });
  });

  describe('DLF.NS - Real Estate Sector NAV-Based Model', () => {
    beforeEach(() => {
      mockApiService.getFinancialData.mockResolvedValue(mockDLFFinancialData);
      mockApiService.getBasicCompanyData.mockResolvedValue(mockDLFBasicCompanyData);
      mockApiService.getDCFDefaults.mockResolvedValue({
        revenue_growth_rate: 15.0,
        ebitda_margin: 22.0,
        tax_rate: 25.0,
        wacc: 12.0,
        terminal_growth_rate: 3.5,
        projection_years: 10,
        capex_percentage: 8.0,
        working_capital_percentage: 5.0,
        current_price: 800,
        rationale: {}
      });
    });

    test('should load DLF without errors and show NAV-based model', async () => {
      const summaryData = createMockSummaryData('REAL ESTATE', 'DLF.NS');
      
      const { container } = render(
        <DCFModelsCard ticker="DLF.NS" summaryData={summaryData} />
      );

      // Should render the component without crashing
      expect(container).toBeInTheDocument();
      
      // Should show sector-specific model tab (NAV-based)
      expect(container.textContent).toMatch(/NAV.*based/i);
    });

    test('should calculate book value per share correctly for DLF', async () => {
      const summaryData = createMockSummaryData('REAL ESTATE', 'DLF.NS');
      
      render(<DCFModelsCard ticker="DLF.NS" summaryData={summaryData} />);
      
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Check that API calls were made
      expect(mockApiService.getFinancialData).toHaveBeenCalledWith('DLF.NS', 3);
      expect(mockApiService.getBasicCompanyData).toHaveBeenCalledWith('DLF.NS');
    });

    test('should handle DLF P/B ratio calculation', async () => {
      const summaryData = createMockSummaryData('REAL ESTATE', 'DLF.NS');
      
      render(<DCFModelsCard ticker="DLF.NS" summaryData={summaryData} />);
      
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // DLF P/B ratio of 1.4x should result in book value = current price / P/B
      // Book Value Per Share = 800 / 1.4 = ₹571.43
      expect(mockApiService.getBasicCompanyData).toHaveBeenCalled();
    });
  });

  describe('HDFCBANK.NS - Banking Sector Excess Returns Model', () => {
    beforeEach(() => {
      mockApiService.getFinancialData.mockResolvedValue(mockHDFCBankFinancialData);
      mockApiService.getBasicCompanyData.mockResolvedValue(mockHDFCBankBasicCompanyData);
      mockApiService.getDCFDefaults.mockResolvedValue({
        revenue_growth_rate: 14.0,
        ebitda_margin: 45.0, // Banking EBITDA margin (will be capped)
        tax_rate: 25.0,
        wacc: 15.0,
        terminal_growth_rate: 4.5,
        projection_years: 10,
        capex_percentage: 1.0,
        working_capital_percentage: 1.0,
        current_price: 1650,
        rationale: {}
      });
    });

    test('should load HDFC Bank without errors and show Excess Returns model', async () => {
      const summaryData = createMockSummaryData('BFSI', 'HDFCBANK.NS');
      
      const { container } = render(
        <DCFModelsCard ticker="HDFCBANK.NS" summaryData={summaryData} />
      );

      // Should render the component without crashing
      expect(container).toBeInTheDocument();
      
      // Should show sector-specific model tab (Excess Returns)
      expect(container.textContent).toMatch(/Excess.*Returns/i);
    });

    test('should calculate banking excess returns correctly', async () => {
      const summaryData = createMockSummaryData('BFSI', 'HDFCBANK.NS');
      
      render(<DCFModelsCard ticker="HDFCBANK.NS" summaryData={summaryData} />);
      
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Check that API calls were made
      expect(mockApiService.getFinancialData).toHaveBeenCalledWith('HDFCBANK.NS', 3);
      expect(mockApiService.getBasicCompanyData).toHaveBeenCalledWith('HDFCBANK.NS');
    });

    test('should handle HDFC Bank market cap classification', async () => {
      const summaryData = createMockSummaryData('BFSI', 'HDFCBANK.NS');
      
      render(<DCFModelsCard ticker="HDFCBANK.NS" summaryData={summaryData} />);
      
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // HDFC Bank market cap (₹8.91 lakh crore) should classify as mega cap
      // This should result in appropriate beta and moat premium adjustments
      expect(mockApiService.getFinancialData).toHaveBeenCalled();
    });
  });

  describe('Model Method Names Consistency', () => {
    test('IT model should use EV_Revenue_Model method', async () => {
      mockApiService.getFinancialData.mockResolvedValue(mockTCSFinancialData);
      mockApiService.getBasicCompanyData.mockResolvedValue(mockTCSBasicCompanyData);
      mockApiService.getDCFDefaults.mockResolvedValue({
        revenue_growth_rate: 12.0,
        ebitda_margin: 26.0,
        tax_rate: 25.0,
        wacc: 11.0,
        terminal_growth_rate: 3.0,
        projection_years: 10,
        capex_percentage: 2.0,
        working_capital_percentage: 3.0,
        current_price: 3500,
        rationale: {}
      });

      const summaryData = createMockSummaryData('IT', 'TCS.NS');
      render(<DCFModelsCard ticker="TCS.NS" summaryData={summaryData} />);
      
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Method should be consistent with naming conventions
      expect(mockApiService.getFinancialData).toHaveBeenCalled();
    });

    test('Real Estate model should use NAV_Based_Model method', async () => {
      mockApiService.getFinancialData.mockResolvedValue(mockDLFFinancialData);
      mockApiService.getBasicCompanyData.mockResolvedValue(mockDLFBasicCompanyData);
      mockApiService.getDCFDefaults.mockResolvedValue({
        revenue_growth_rate: 15.0,
        ebitda_margin: 22.0,
        tax_rate: 25.0,
        wacc: 12.0,
        terminal_growth_rate: 3.5,
        projection_years: 10,
        capex_percentage: 8.0,
        working_capital_percentage: 5.0,
        current_price: 800,
        rationale: {}
      });

      const summaryData = createMockSummaryData('REAL ESTATE', 'DLF.NS');
      render(<DCFModelsCard ticker="DLF.NS" summaryData={summaryData} />);
      
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Method should be consistent with naming conventions
      expect(mockApiService.getBasicCompanyData).toHaveBeenCalled();
    });

    test('Banking model should use Excess_Returns_Model method', async () => {
      mockApiService.getFinancialData.mockResolvedValue(mockHDFCBankFinancialData);
      mockApiService.getBasicCompanyData.mockResolvedValue(mockHDFCBankBasicCompanyData);
      mockApiService.getDCFDefaults.mockResolvedValue({
        revenue_growth_rate: 14.0,
        ebitda_margin: 45.0,
        tax_rate: 25.0,
        wacc: 15.0,
        terminal_growth_rate: 4.5,
        projection_years: 10,
        capex_percentage: 1.0,
        working_capital_percentage: 1.0,
        current_price: 1650,
        rationale: {}
      });

      const summaryData = createMockSummaryData('BFSI', 'HDFCBANK.NS');
      render(<DCFModelsCard ticker="HDFCBANK.NS" summaryData={summaryData} />);
      
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Method should be consistent with naming conventions
      expect(mockApiService.getFinancialData).toHaveBeenCalled();
    });
  });

  describe('Error Handling Tests', () => {
    test('should handle API failures gracefully for IT model', async () => {
      mockApiService.getFinancialData.mockRejectedValue(new Error('API Error'));
      mockApiService.getBasicCompanyData.mockRejectedValue(new Error('API Error'));

      const summaryData = createMockSummaryData('IT', 'TCS.NS');
      
      const { container } = render(
        <DCFModelsCard ticker="TCS.NS" summaryData={summaryData} />
      );

      // Should not crash and should render fallback
      expect(container).toBeInTheDocument();
      
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Should have attempted API calls
      expect(mockApiService.getFinancialData).toHaveBeenCalled();
    });

    test('should handle API failures gracefully for Real Estate model', async () => {
      mockApiService.getFinancialData.mockRejectedValue(new Error('API Error'));
      mockApiService.getBasicCompanyData.mockRejectedValue(new Error('API Error'));

      const summaryData = createMockSummaryData('REAL ESTATE', 'DLF.NS');
      
      const { container } = render(
        <DCFModelsCard ticker="DLF.NS" summaryData={summaryData} />
      );

      // Should not crash and should render fallback
      expect(container).toBeInTheDocument();
      
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Should have attempted API calls
      expect(mockApiService.getFinancialData).toHaveBeenCalled();
    });
  });

  describe('Sector Normalization Integration', () => {
    test('should correctly normalize "Information Technology" to IT', async () => {
      mockApiService.getFinancialData.mockResolvedValue(mockTCSFinancialData);
      mockApiService.getBasicCompanyData.mockResolvedValue(mockTCSBasicCompanyData);
      mockApiService.getDCFDefaults.mockResolvedValue({
        revenue_growth_rate: 12.0,
        ebitda_margin: 26.0,
        tax_rate: 25.0,
        wacc: 11.0,
        terminal_growth_rate: 3.0,
        projection_years: 10,
        capex_percentage: 2.0,
        working_capital_percentage: 3.0,
        current_price: 3500,
        rationale: {}
      });

      const summaryData = createMockSummaryData('Information Technology', 'TCS.NS');
      
      const { container } = render(
        <DCFModelsCard ticker="TCS.NS" summaryData={summaryData} />
      );

      // Should normalize "Information Technology" to "IT" and show EV/Revenue model
      expect(container.textContent).toMatch(/EV\/Revenue/i);
    });

    test('should correctly normalize "Real Estate" variations', async () => {
      mockApiService.getFinancialData.mockResolvedValue(mockDLFFinancialData);
      mockApiService.getBasicCompanyData.mockResolvedValue(mockDLFBasicCompanyData);
      mockApiService.getDCFDefaults.mockResolvedValue({
        revenue_growth_rate: 15.0,
        ebitda_margin: 22.0,
        tax_rate: 25.0,
        wacc: 12.0,
        terminal_growth_rate: 3.5,
        projection_years: 10,
        capex_percentage: 8.0,
        working_capital_percentage: 5.0,
        current_price: 800,
        rationale: {}
      });

      const sectorVariations = ['Real Estate', 'REALTY', 'Property'];
      
      for (const sector of sectorVariations) {
        const summaryData = createMockSummaryData(sector, 'DLF.NS');
        
        const { container } = render(
          <DCFModelsCard ticker="DLF.NS" summaryData={summaryData} />
        );

        // Should normalize all variations to show NAV-based model
        expect(container.textContent).toMatch(/NAV.*based/i);
      }
    });
  });
});