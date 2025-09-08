// Comprehensive test suite for DCFModelsCard dynamic implementation
import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { DCFModelsCard } from '../components/DCFValuation/DCFModelsCard';
import * as ApiService from '../services/api';
import type { SummaryResponse } from '../types/summary';

// Mock API Service
jest.mock('../services/api');
const mockApiService = ApiService as jest.Mocked<typeof ApiService>;

// Mock financial and company data
const mockFinancialData = {
  ticker: 'TEST.NS',
  years: [2024, 2023, 2022],
  revenue: [100000000000, 90000000000, 80000000000], // ₹1000Cr, ₹900Cr, ₹800Cr
  net_income: [15000000000, 13500000000, 12000000000], // ₹150Cr, ₹135Cr, ₹120Cr
  shares_outstanding: [1000000000, 1000000000, 1000000000] // 100Cr shares
};

const mockBasicCompanyData = {
  stock_price: {
    current_price: 100,
    market_cap: 100000000000, // ₹1000Cr market cap
    pe_ratio: 20,
    pb_ratio: 2.5
  }
};

const mockDCFDefaults = {
  revenue_growth_rate: 12.0,
  ebitda_margin: 25.0,
  tax_rate: 25.0,
  wacc: 11.0,
  terminal_growth_rate: 3.0,
  projection_years: 10,
  capex_percentage: 4.0,
  working_capital_percentage: 2.0,
  current_price: 100,
  rationale: {}
};

// Test data for different sectors
const createMockSummaryData = (sector: string, ticker: string = 'TEST.NS'): SummaryResponse => ({
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
  analysis_timestamp: '2025-07-31T14:00:00.000Z',
  analysis_mode: 'simple',
  sector
});

describe('DCFModelsCard Dynamic Implementation', () => {
  beforeEach(() => {
    // Reset mocks
    jest.clearAllMocks();
    
    // Setup default mock returns
    mockApiService.getFinancialData.mockResolvedValue(mockFinancialData);
    mockApiService.getBasicCompanyData.mockResolvedValue(mockBasicCompanyData);
    mockApiService.getDCFDefaults.mockResolvedValue(mockDCFDefaults);
  });

  describe('Sector Normalization Tests', () => {
    test('handles BFSI sector variations correctly', async () => {
      const sectorVariations = ['BFSI', 'Financial Services', 'Banking', 'Banks'];
      
      for (const sector of sectorVariations) {
        const summaryData = createMockSummaryData(sector, 'TESTBANK.NS');
        render(<DCFModelsCard ticker="TESTBANK.NS" summaryData={summaryData} />);
        
        // Should load Banking Excess Returns model for all variations
        await waitFor(() => {
          expect(screen.getByText(/Banking.*Excess.*Returns/i)).toBeInTheDocument();
        });
      }
    });

    test('handles IT sector variations correctly', async () => {
      const sectorVariations = ['IT', 'Information Technology', 'Software', 'Technology'];
      
      for (const sector of sectorVariations) {
        const summaryData = createMockSummaryData(sector, 'TESTIT.NS');
        render(<DCFModelsCard ticker="TESTIT.NS" summaryData={summaryData} />);
        
        // Should load IT Services model for all variations
        await waitFor(() => {
          expect(screen.getByText(/IT.*Services/i)).toBeInTheDocument();
        });
      }
    });

    test('handles Pharma sector variations correctly', async () => {
      const sectorVariations = ['PHARMA', 'Pharmaceuticals', 'Healthcare', 'Pharma & Healthcare'];
      
      for (const sector of sectorVariations) {
        const summaryData = createMockSummaryData(sector, 'TESTPHARMA.NS');
        render(<DCFModelsCard ticker="TESTPHARMA.NS" summaryData={summaryData} />);
        
        // Should load Pharma R&D model for all variations
        await waitFor(() => {
          expect(screen.getByText(/R.*D.*Pipeline/i)).toBeInTheDocument();
        });
      }
    });

    test('handles Real Estate sector variations correctly', async () => {
      const sectorVariations = ['REAL ESTATE', 'Real Estate', 'Realty', 'Property'];
      
      for (const sector of sectorVariations) {
        const summaryData = createMockSummaryData(sector, 'TESTREALTY.NS');
        render(<DCFModelsCard ticker="TESTREALTY.NS" summaryData={summaryData} />);
        
        // Should load NAV-based model for all variations
        await waitFor(() => {
          expect(screen.getByText(/NAV.*based/i)).toBeInTheDocument();
        });
      }
    });

    test('handles "Other" category for unknown sectors', async () => {
      const unknownSectors = ['Mining', 'Agriculture', 'Unknown Sector', 'New Industry'];
      
      for (const sector of unknownSectors) {
        const summaryData = createMockSummaryData(sector, 'TESTOTHER.NS');
        render(<DCFModelsCard ticker="TESTOTHER.NS" summaryData={summaryData} />);
        
        // Should use OTHER category fallback
        await waitFor(() => {
          // Check that it doesn't crash and shows some DCF model
          expect(screen.getByText(/Intrinsic Value/i)).toBeInTheDocument();
        });
      }
    });
  });

  describe('Dynamic P/E Multiple Tests', () => {
    test('applies market leader premium for large cap companies', async () => {
      // Large cap company (>₹5 lakh crore)
      const largCapCompanyData = {
        ...mockBasicCompanyData,
        stock_price: {
          ...mockBasicCompanyData.stock_price,
          market_cap: 600000000000 // ₹6 lakh crore
        }
      };
      
      mockApiService.getBasicCompanyData.mockResolvedValue(largCapCompanyData);
      
      const summaryData = createMockSummaryData('IT', 'LARGEIT.NS');
      render(<DCFModelsCard ticker="LARGEIT.NS" summaryData={summaryData} />);
      
      // Switch to PE-based model to test P/E calculation
      const peTab = await screen.findByText(/PE.*based/i);
      fireEvent.click(peTab);
      
      await waitFor(() => {
        // Should show market leader premium in methodology
        expect(screen.getByText(/Market.*position.*premium/i)).toBeInTheDocument();
      });
    });

    test('handles mid-cap companies with appropriate P/E multiples', async () => {
      // Mid cap company
      const midCapCompanyData = {
        ...mockBasicCompanyData,
        stock_price: {
          ...mockBasicCompanyData.stock_price,
          market_cap: 150000000000 // ₹1.5 lakh crore
        }
      };
      
      mockApiService.getBasicCompanyData.mockResolvedValue(midCapCompanyData);
      
      const summaryData = createMockSummaryData('FMCG', 'MIDFMCG.NS');
      render(<DCFModelsCard ticker="MIDFMCG.NS" summaryData={summaryData} />);
      
      await waitFor(() => {
        expect(screen.getByText(/Intrinsic Value/i)).toBeInTheDocument();
      });
    });
  });

  describe('EPS Growth Anomaly Detection Tests', () => {
    test('detects anomaly for stable sector with negative growth', async () => {
      // Mock financial data with negative EPS growth for a banking stock
      const anomalyFinancialData = {
        ...mockFinancialData,
        net_income: [10000000000, 15000000000, 20000000000] // Declining earnings
      };
      
      const largeBankData = {
        ...mockBasicCompanyData,
        stock_price: {
          ...mockBasicCompanyData.stock_price,
          market_cap: 800000000000 // Large bank
        }
      };
      
      mockApiService.getFinancialData.mockResolvedValue(anomalyFinancialData);
      mockApiService.getBasicCompanyData.mockResolvedValue(largeBankData);
      
      const summaryData = createMockSummaryData('BFSI', 'ANOMALYBANK.NS');
      render(<DCFModelsCard ticker="ANOMALYBANK.NS" summaryData={summaryData} />);
      
      // Switch to PE model to trigger anomaly detection
      const peTab = await screen.findByText(/PE.*based/i);
      fireEvent.click(peTab);
      
      await waitFor(() => {
        // Should show GDP-based fallback message
        expect(screen.getByText(/GDP.*based.*forecast/i)).toBeInTheDocument();
      });
    });

    test('handles normal growth for stable sectors', async () => {
      const summaryData = createMockSummaryData('IT', 'NORMALIT.NS');
      render(<DCFModelsCard ticker="NORMALIT.NS" summaryData={summaryData} />);
      
      await waitFor(() => {
        expect(screen.getByText(/Intrinsic Value/i)).toBeInTheDocument();
      });
    });
  });

  describe('Comprehensive Sector Coverage Tests', () => {
    const allSectors = [
      'BFSI', 'IT', 'PHARMA', 'REAL ESTATE', 'FMCG', 
      'ENERGY', 'TELECOM', 'AUTO', 'METALS', 'CHEMICALS',
      'TEXTILES', 'CEMENT', 'DIVERSIFIED', 'OTHER'
    ];

    test.each(allSectors)('handles %s sector without errors', async (sector) => {
      const summaryData = createMockSummaryData(sector, `TEST${sector.replace(' ', '')}.NS`);
      
      render(<DCFModelsCard ticker={`TEST${sector.replace(' ', '')}.NS`} summaryData={summaryData} />);
      
      await waitFor(() => {
        // Should render without errors and show basic DCF structure
        expect(screen.getByText(/Intrinsic Value/i)).toBeInTheDocument();
        expect(screen.getByText(/Upside.*Downside/i)).toBeInTheDocument();
        expect(screen.getByText(/Confidence/i)).toBeInTheDocument();
      });
    });
  });

  describe('Methodology Transparency Tests', () => {
    test('shows methodology transparency panel for all sectors', async () => {
      const summaryData = createMockSummaryData('OTHER', 'UNKNOWN.NS');
      render(<DCFModelsCard ticker="UNKNOWN.NS" summaryData={summaryData} />);
      
      await waitFor(() => {
        expect(screen.getByText(/Methodology Transparency/i)).toBeInTheDocument();
        expect(screen.getByText(/Data Sources/i)).toBeInTheDocument();
        expect(screen.getByText(/Reliability/i)).toBeInTheDocument();
      });
    });

    test('shows low confidence warning when appropriate', async () => {
      // Mock low confidence scenario
      const lowConfidenceSummaryData = {
        ...createMockSummaryData('OTHER', 'LOWCONF.NS'),
        fair_value_band: {
          ...createMockSummaryData('OTHER', 'LOWCONF.NS').fair_value_band,
          confidence: 0.4 // Low confidence
        }
      };
      
      render(<DCFModelsCard ticker="LOWCONF.NS" summaryData={lowConfidenceSummaryData} />);
      
      await waitFor(() => {
        expect(screen.getByText(/Model Limitations/i)).toBeInTheDocument();
        expect(screen.getByText(/preliminary estimate/i)).toBeInTheDocument();
      });
    });
  });

  describe('No Hardcoded Values Tests', () => {
    test('does not contain any hardcoded ticker references', async () => {
      const summaryData = createMockSummaryData('BFSI', 'RANDOMBANK.NS');
      render(<DCFModelsCard ticker="RANDOMBANK.NS" summaryData={summaryData} />);
      
      await waitFor(() => {
        // Should work for any ticker, not just HDFCBANK
        expect(screen.getByText(/Banking.*Excess.*Returns/i)).toBeInTheDocument();
      });
    });

    test('uses dynamic market cap based calculations', async () => {
      // Test with different market caps
      const marketCaps = [50000000000, 200000000000, 700000000000]; // Small, Mid, Large
      
      for (const marketCap of marketCaps) {
        const companyData = {
          ...mockBasicCompanyData,
          stock_price: {
            ...mockBasicCompanyData.stock_price,
            market_cap: marketCap
          }
        };
        
        mockApiService.getBasicCompanyData.mockResolvedValue(companyData);
        
        const summaryData = createMockSummaryData('IT', `TEST${marketCap}.NS`);
        render(<DCFModelsCard ticker={`TEST${marketCap}.NS`} summaryData={summaryData} />);
        
        await waitFor(() => {
          expect(screen.getByText(/Intrinsic Value/i)).toBeInTheDocument();
        });
      }
    });
  });

  describe('Error Handling Tests', () => {
    test('handles API failures gracefully', async () => {
      mockApiService.getFinancialData.mockRejectedValue(new Error('API Error'));
      
      const summaryData = createMockSummaryData('BFSI', 'ERRORBANK.NS');
      render(<DCFModelsCard ticker="ERRORBANK.NS" summaryData={summaryData} />);
      
      await waitFor(() => {
        // Should show error state, not crash
        expect(screen.getByText(/error/i) || screen.getByText(/failed/i)).toBeInTheDocument();
      });
    });

    test('handles missing sector data gracefully', async () => {
      const summaryData = createMockSummaryData('', 'NOSECTOR.NS'); // Empty sector
      render(<DCFModelsCard ticker="NOSECTOR.NS" summaryData={summaryData} />);
      
      await waitFor(() => {
        // Should fallback to OTHER category
        expect(screen.getByText(/Intrinsic Value/i)).toBeInTheDocument();
      });
    });
  });

  describe('Interactive Features Tests', () => {
    test('assumptions panel toggles correctly', async () => {
      const summaryData = createMockSummaryData('IT', 'INTERACTIVE.NS');
      render(<DCFModelsCard ticker="INTERACTIVE.NS" summaryData={summaryData} />);
      
      // Find and click assumptions toggle
      const assumptionsToggle = await screen.findByText(/Show.*DCF.*Assumptions/i);
      fireEvent.click(assumptionsToggle);
      
      await waitFor(() => {
        expect(screen.getByText(/Hide.*DCF.*Assumptions/i)).toBeInTheDocument();
      });
    });

    test('model tabs switch correctly', async () => {
      const summaryData = createMockSummaryData('BFSI', 'TABTEST.NS');
      render(<DCFModelsCard ticker="TABTEST.NS" summaryData={summaryData} />);
      
      // Should start with sector model (Banking Excess Returns)
      await waitFor(() => {
        expect(screen.getByText(/Banking.*Excess.*Returns/i)).toBeInTheDocument();
      });
      
      // Switch to PE model
      const peTab = await screen.findByText(/PE.*based/i);
      fireEvent.click(peTab);
      
      await waitFor(() => {
        expect(screen.getByText(/PE.*Multiple.*Valuation/i)).toBeInTheDocument();
      });
    });
  });
});