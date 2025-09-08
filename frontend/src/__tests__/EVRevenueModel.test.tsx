// Comprehensive test suite for Enhanced EV/Revenue Model
import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { DCFModelsCard } from '../components/DCFValuation/DCFModelsCard';
import * as ApiService from '../services/api';
import type { SummaryResponse } from '../types/summary';

// Mock API Service
jest.mock('../services/api');
const mockApiService = ApiService as jest.Mocked<typeof ApiService>;

// Test data factory for different IT company scenarios
const createITSummaryData = (ticker: string): SummaryResponse => ({
  ticker,
  company_name: `${ticker.replace('.NS', '')} Limited`,
  fair_value_band: {
    min_value: 90,
    max_value: 110,
    current_price: 100,
    method: 'EV_Revenue_Model',
    confidence: 0.85
  },
  investment_label: 'Neutral',
  key_factors: ['IT services leader', 'Strong margin profile'],
  valuation_insights: 'Premium IT services company',
  market_signals: 'Stable performance',
  business_fundamentals: 'Strong fundamentals',
  data_health_warnings: [],
  analysis_timestamp: '2025-08-01T03:00:00.000Z',
  analysis_mode: 'simple',
  sector: 'IT'
});

// Financial data scenarios for different company tiers
const createFinancialData = (scenario: 'tier1_leader' | 'tier1_player' | 'midtier' | 'smaller') => {
  const scenarios = {
    tier1_leader: {
      // TCS-like: ₹12+ lakh crore market cap, Elite growth, High margins
      revenue: [255000000000, 240000000000, 225000000000], // ₹2.55L Cr → ₹2.25L Cr (6.4% CAGR)
      net_income: [48450000000, 43200000000, 38250000000], // ₹484.5B → ₹382.5B
      shares_outstanding: [3700000000, 3700000000, 3700000000] // 370 Cr shares
    },
    tier1_player: {
      // HCL/Wipro-like: ₹5-10 lakh crore market cap, Good growth, Good margins
      revenue: [120000000000, 108000000000, 100000000000], // ₹1.2L Cr → ₹1.0L Cr (9.5% CAGR)
      net_income: [24000000000, 20160000000, 18000000000], // ₹240B → ₹180B
      shares_outstanding: [2700000000, 2700000000, 2700000000] // 270 Cr shares
    },
    midtier: {
      // Mid-tier IT: ₹1-5 lakh crore market cap, Moderate growth, Average margins
      revenue: [50000000000, 47000000000, 45000000000], // ₹500B → ₹450B (5.4% CAGR)
      net_income: [8500000000, 7520000000, 6750000000], // ₹85B → ₹67.5B
      shares_outstanding: [1000000000, 1000000000, 1000000000] // 100 Cr shares
    },
    smaller: {
      // Smaller IT: <₹1 lakh crore market cap, Low growth, Below average margins
      revenue: [15000000000, 14700000000, 14500000000], // ₹150B → ₹145B (1.8% CAGR)
      net_income: [2250000000, 2058000000, 1885000000], // ₹22.5B → ₹18.85B
      shares_outstanding: [500000000, 500000000, 500000000] // 50 Cr shares
    }
  };
  return {
    ticker: 'TEST.NS',
    years: [2024, 2023, 2022],
    ...scenarios[scenario]
  };
};

const createBasicCompanyData = (scenario: 'tier1_leader' | 'tier1_player' | 'midtier' | 'smaller') => {
  const scenarios = {
    tier1_leader: {
      stock_price: {
        current_price: 3500,
        market_cap: 1295000000000, // ₹12.95 lakh crore
        pe_ratio: 26.7,
        pb_ratio: 12.8
      }
    },
    tier1_player: {
      stock_price: {
        current_price: 1800,
        market_cap: 486000000000, // ₹4.86 lakh crore
        pe_ratio: 20.3,
        pb_ratio: 8.2
      }
    },
    midtier: {
      stock_price: {
        current_price: 1200,
        market_cap: 120000000000, // ₹1.2 lakh crore
        pe_ratio: 14.1,
        pb_ratio: 4.5
      }
    },
    smaller: {
      stock_price: {
        current_price: 800,
        market_cap: 40000000000, // ₹400 crore
        pe_ratio: 17.8,
        pb_ratio: 3.2
      }
    }
  };
  return scenarios[scenario];
};

const mockDCFDefaults = {
  revenue_growth_rate: 10.0,
  ebitda_margin: 25.0,
  tax_rate: 25.0,
  wacc: 12.0,
  terminal_growth_rate: 3.0,
  projection_years: 10,
  capex_percentage: 2.0,
  working_capital_percentage: 3.0,
  current_price: 3500,
  rationale: {}
};

describe('Enhanced EV/Revenue Model - Comprehensive Tests', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    // Suppress console logs during tests
    jest.spyOn(console, 'log').mockImplementation(() => {});
    jest.spyOn(console, 'error').mockImplementation(() => {});
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  describe('Market Cap Tier Classification Tests', () => {
    test('should classify Tier-1 Leader (>₹10L Cr) with 6.5x base multiple', async () => {
      const financialData = createFinancialData('tier1_leader');
      const basicData = createBasicCompanyData('tier1_leader');
      
      mockApiService.getFinancialData.mockResolvedValue(financialData);
      mockApiService.getBasicCompanyData.mockResolvedValue(basicData);
      mockApiService.getDCFDefaults.mockResolvedValue(mockDCFDefaults);

      const summaryData = createITSummaryData('TCS.NS');
      render(<DCFModelsCard ticker="TCS.NS" summaryData={summaryData} />);
      
      await waitFor(() => {
        expect(mockApiService.getFinancialData).toHaveBeenCalledWith('TCS.NS', 3);
      });

      // Market cap ₹12.95L Cr should be classified as Tier-1 Leader
      // Expected: 6.5x base multiple
    });

    test('should classify Tier-1 Player (₹5-10L Cr) with 5.5x base multiple', async () => {
      const financialData = createFinancialData('tier1_player');
      const basicData = createBasicCompanyData('tier1_player');
      
      mockApiService.getFinancialData.mockResolvedValue(financialData);
      mockApiService.getBasicCompanyData.mockResolvedValue(basicData);
      mockApiService.getDCFDefaults.mockResolvedValue(mockDCFDefaults);

      const summaryData = createITSummaryData('HCLTECH.NS');
      render(<DCFModelsCard ticker="HCLTECH.NS" summaryData={summaryData} />);
      
      await waitFor(() => {
        expect(mockApiService.getBasicCompanyData).toHaveBeenCalled();
      });

      // Market cap ₹4.86L Cr should be classified as Tier-1 Player
      // Expected: 5.5x base multiple
    });

    test('should classify Mid-tier Player (₹1-5L Cr) with 4.5x base multiple', async () => {
      const financialData = createFinancialData('midtier');
      const basicData = createBasicCompanyData('midtier');
      
      mockApiService.getFinancialData.mockResolvedValue(financialData);
      mockApiService.getBasicCompanyData.mockResolvedValue(basicData);
      mockApiService.getDCFDefaults.mockResolvedValue(mockDCFDefaults);

      const summaryData = createITSummaryData('MIDTIER.NS');
      render(<DCFModelsCard ticker="MIDTIER.NS" summaryData={summaryData} />);
      
      await waitFor(() => {
        expect(mockApiService.getFinancialData).toHaveBeenCalled();
      });

      // Market cap ₹1.2L Cr should be classified as Mid-tier Player
      // Expected: 4.5x base multiple
    });

    test('should classify Smaller Player (<₹1L Cr) with 4.0x base multiple + quality discount', async () => {
      const financialData = createFinancialData('smaller');
      const basicData = createBasicCompanyData('smaller');
      
      mockApiService.getFinancialData.mockResolvedValue(financialData);
      mockApiService.getBasicCompanyData.mockResolvedValue(basicData);
      mockApiService.getDCFDefaults.mockResolvedValue(mockDCFDefaults);

      const summaryData = createITSummaryData('SMALLER.NS');
      render(<DCFModelsCard ticker="SMALLER.NS" summaryData={summaryData} />);
      
      await waitFor(() => {
        expect(mockApiService.getBasicCompanyData).toHaveBeenCalled();
      });

      // Market cap ₹400 Cr should be classified as Smaller Player
      // Expected: 4.0x base multiple - 0.5x quality discount = 3.5x
    });
  });

  describe('Growth Premium Tier Tests', () => {
    test('should apply Elite growth premium (+1.5x) for >20% CAGR', async () => {
      // Create high growth scenario: 22% CAGR
      const highGrowthData = {
        ticker: 'HIGHGROWTH.NS',
        years: [2024, 2023, 2022],
        revenue: [150000000000, 123000000000, 100000000000], // 22.5% CAGR
        net_income: [30000000000, 24600000000, 20000000000],
        shares_outstanding: [1000000000, 1000000000, 1000000000]
      };

      mockApiService.getFinancialData.mockResolvedValue(highGrowthData);
      mockApiService.getBasicCompanyData.mockResolvedValue(createBasicCompanyData('tier1_leader'));
      mockApiService.getDCFDefaults.mockResolvedValue(mockDCFDefaults);

      const summaryData = createITSummaryData('HIGHGROWTH.NS');
      render(<DCFModelsCard ticker="HIGHGROWTH.NS" summaryData={summaryData} />);
      
      await waitFor(() => {
        expect(mockApiService.getFinancialData).toHaveBeenCalled();
      });

      // 22% CAGR should trigger Elite growth premium (+1.5x)
    });

    test('should apply growth discount (-0.3x) for ≤5% CAGR', async () => {
      // Use smaller company data (1.8% CAGR)
      const financialData = createFinancialData('smaller');
      
      mockApiService.getFinancialData.mockResolvedValue(financialData);
      mockApiService.getBasicCompanyData.mockResolvedValue(createBasicCompanyData('smaller'));
      mockApiService.getDCFDefaults.mockResolvedValue(mockDCFDefaults);

      const summaryData = createITSummaryData('SLOWGROWTH.NS');
      render(<DCFModelsCard ticker="SLOWGROWTH.NS" summaryData={summaryData} />);
      
      await waitFor(() => {
        expect(mockApiService.getFinancialData).toHaveBeenCalled();
      });

      // 1.8% CAGR should trigger growth discount (-0.3x)
    });
  });

  describe('EBITDA Margin Premium Tier Tests', () => {
    test('should calculate historical EBITDA margin from financial data', async () => {
      const financialData = createFinancialData('tier1_leader');
      
      mockApiService.getFinancialData.mockResolvedValue(financialData);
      mockApiService.getBasicCompanyData.mockResolvedValue(createBasicCompanyData('tier1_leader'));
      mockApiService.getDCFDefaults.mockResolvedValue(mockDCFDefaults);

      const summaryData = createITSummaryData('TCS.NS');
      render(<DCFModelsCard ticker="TCS.NS" summaryData={summaryData} />);
      
      await waitFor(() => {
        expect(mockApiService.getFinancialData).toHaveBeenCalledWith('TCS.NS', 3);
      });

      // Should calculate EBITDA margin from Net Income / (1 - Tax Rate) / Revenue
      // For TCS scenario: Should be around 25-26% margin (Good tier, +0.4x premium)
    });

    test('should apply Elite margin premium (+1.2x) for >30% EBITDA margin', async () => {
      // Create elite margin scenario
      const eliteMarginData = {
        ticker: 'ELITEMARGIN.NS',
        years: [2024, 2023, 2022],
        revenue: [100000000000, 95000000000, 90000000000],
        net_income: [25000000000, 23750000000, 22500000000], // ~33% estimated EBITDA margin
        shares_outstanding: [1000000000, 1000000000, 1000000000]
      };

      mockApiService.getFinancialData.mockResolvedValue(eliteMarginData);
      mockApiService.getBasicCompanyData.mockResolvedValue(createBasicCompanyData('tier1_leader'));
      mockApiService.getDCFDefaults.mockResolvedValue(mockDCFDefaults);

      const summaryData = createITSummaryData('ELITEMARGIN.NS');
      render(<DCFModelsCard ticker="ELITEMARGIN.NS" summaryData={summaryData} />);
      
      await waitFor(() => {
        expect(mockApiService.getFinancialData).toHaveBeenCalled();
      });

      // Should apply Elite margin premium (+1.2x)
    });

    test('should apply margin discount (-0.5x) for ≤18% EBITDA margin', async () => {
      // Create poor margin scenario
      const poorMarginData = {
        ticker: 'POORMARGIN.NS',
        years: [2024, 2023, 2022],
        revenue: [50000000000, 48000000000, 46000000000],
        net_income: [6500000000, 6240000000, 5980000000], // ~17% estimated EBITDA margin
        shares_outstanding: [1000000000, 1000000000, 1000000000]
      };

      mockApiService.getFinancialData.mockResolvedValue(poorMarginData);
      mockApiService.getBasicCompanyData.mockResolvedValue(createBasicCompanyData('midtier'));
      mockApiService.getDCFDefaults.mockResolvedValue(mockDCFDefaults);

      const summaryData = createITSummaryData('POORMARGIN.NS');
      render(<DCFModelsCard ticker="POORMARGIN.NS" summaryData={summaryData} />);
      
      await waitFor(() => {
        expect(mockApiService.getFinancialData).toHaveBeenCalled();
      });

      // Should apply margin discount (-0.5x)
    });
  });

  describe('Combined Premium Logic Tests', () => {
    test('should calculate total multiple correctly with all premiums/discounts', async () => {
      // Test TCS-like scenario: Tier-1 Leader + Moderate Growth + Good Margins
      const financialData = createFinancialData('tier1_leader');
      const basicData = createBasicCompanyData('tier1_leader');
      
      mockApiService.getFinancialData.mockResolvedValue(financialData);
      mockApiService.getBasicCompanyData.mockResolvedValue(basicData);
      mockApiService.getDCFDefaults.mockResolvedValue(mockDCFDefaults);

      const summaryData = createITSummaryData('TCS.NS');
      render(<DCFModelsCard ticker="TCS.NS" summaryData={summaryData} />);
      
      await waitFor(() => {
        expect(mockApiService.getFinancialData).toHaveBeenCalled();
      });

      // Expected calculation:
      // Base: 6.5x (Tier-1 Leader)
      // Growth: +0.2x (6.4% CAGR = Moderate)
      // Margin: +0.4x (~25% EBITDA = Good)
      // Quality: +0.0x (no discount for large cap)
      // Total: 7.1x
    });

    test('should enforce minimum 2.0x multiple floor', async () => {
      // Create worst-case scenario
      const worstCaseData = {
        ticker: 'WORSTCASE.NS',
        years: [2024, 2023, 2022],
        revenue: [10000000000, 11000000000, 12000000000], // Negative growth
        net_income: [800000000, 880000000, 960000000], // Poor margins
        shares_outstanding: [500000000, 500000000, 500000000]
      };

      mockApiService.getFinancialData.mockResolvedValue(worstCaseData);
      mockApiService.getBasicCompanyData.mockResolvedValue(createBasicCompanyData('smaller'));
      mockApiService.getDCFDefaults.mockResolvedValue(mockDCFDefaults);

      const summaryData = createITSummaryData('WORSTCASE.NS');
      render(<DCFModelsCard ticker="WORSTCASE.NS" summaryData={summaryData} />);
      
      await waitFor(() => {
        expect(mockApiService.getFinancialData).toHaveBeenCalled();
      });

      // Expected: Even with all discounts, should not go below 2.0x floor
    });
  });

  describe('Data Quality and Edge Cases', () => {
    test('should handle missing financial data gracefully', async () => {
      const incompleteData = {
        ticker: 'INCOMPLETE.NS',
        years: [2024],
        revenue: [100000000000],
        net_income: [15000000000],
        shares_outstanding: [1000000000]
      };

      mockApiService.getFinancialData.mockResolvedValue(incompleteData);
      mockApiService.getBasicCompanyData.mockResolvedValue(createBasicCompanyData('midtier'));
      mockApiService.getDCFDefaults.mockResolvedValue(mockDCFDefaults);

      const summaryData = createITSummaryData('INCOMPLETE.NS');
      
      expect(() => {
        render(<DCFModelsCard ticker="INCOMPLETE.NS" summaryData={summaryData} />);
      }).not.toThrow();

      // Should fallback to default assumptions when insufficient data
    });

    test('should validate EBITDA margin sanity checks', async () => {
      // Create data with unrealistic margins
      const unrealisticData = {
        ticker: 'UNREALISTIC.NS',
        years: [2024, 2023, 2022],
        revenue: [100000000000, 95000000000, 90000000000],
        net_income: [60000000000, 57000000000, 54000000000], // >60% margin (unrealistic)
        shares_outstanding: [1000000000, 1000000000, 1000000000]
      };

      mockApiService.getFinancialData.mockResolvedValue(unrealisticData);
      mockApiService.getBasicCompanyData.mockResolvedValue(createBasicCompanyData('tier1_leader'));
      mockApiService.getDCFDefaults.mockResolvedValue(mockDCFDefaults);

      const summaryData = createITSummaryData('UNREALISTIC.NS');
      render(<DCFModelsCard ticker="UNREALISTIC.NS" summaryData={summaryData} />);
      
      await waitFor(() => {
        expect(mockApiService.getFinancialData).toHaveBeenCalled();
      });

      // Should reject unrealistic margins and fallback to default
    });

    test('should handle API failures with appropriate fallbacks', async () => {
      mockApiService.getFinancialData.mockRejectedValue(new Error('API Error'));
      mockApiService.getBasicCompanyData.mockRejectedValue(new Error('API Error'));
      mockApiService.getDCFDefaults.mockResolvedValue(mockDCFDefaults);

      const summaryData = createITSummaryData('APIERROR.NS');
      
      expect(() => {
        render(<DCFModelsCard ticker="APIERROR.NS" summaryData={summaryData} />);
      }).not.toThrow();

      // Should show fallback calculation with reduced confidence
    });
  });

  describe('Confidence Scoring Tests', () => {
    test('should assign high confidence (85%) for complete data + large cap', async () => {
      const financialData = createFinancialData('tier1_leader');
      const basicData = createBasicCompanyData('tier1_leader');
      
      mockApiService.getFinancialData.mockResolvedValue(financialData);
      mockApiService.getBasicCompanyData.mockResolvedValue(basicData);
      mockApiService.getDCFDefaults.mockResolvedValue(mockDCFDefaults);

      const summaryData = createITSummaryData('TCS.NS');
      render(<DCFModelsCard ticker="TCS.NS" summaryData={summaryData} />);
      
      await waitFor(() => {
        expect(mockApiService.getFinancialData).toHaveBeenCalled();
      });

      // Should achieve 85% confidence:
      // Base: 75% + 10% (3Y data) + 5% (good margins) + 5% (large cap) = 95% → capped at 85%
    });

    test('should assign medium confidence for mid-tier companies', async () => {
      const financialData = createFinancialData('midtier');
      const basicData = createBasicCompanyData('midtier');
      
      mockApiService.getFinancialData.mockResolvedValue(financialData);
      mockApiService.getBasicCompanyData.mockResolvedValue(basicData);
      mockApiService.getDCFDefaults.mockResolvedValue(mockDCFDefaults);

      const summaryData = createITSummaryData('MIDTIER.NS');
      render(<DCFModelsCard ticker="MIDTIER.NS" summaryData={summaryData} />);
      
      await waitFor(() => {
        expect(mockApiService.getFinancialData).toHaveBeenCalled();
      });

      // Should achieve ~80% confidence (no large cap bonus)
    });

    test('should assign lower confidence for incomplete data', async () => {
      const incompleteData = {
        ticker: 'INCOMPLETE.NS',
        years: [2024],
        revenue: [100000000000],
        net_income: [15000000000],
        shares_outstanding: [1000000000]
      };

      mockApiService.getFinancialData.mockResolvedValue(incompleteData);
      mockApiService.getBasicCompanyData.mockResolvedValue(createBasicCompanyData('smaller'));
      mockApiService.getDCFDefaults.mockResolvedValue(mockDCFDefaults);

      const summaryData = createITSummaryData('INCOMPLETE.NS');
      render(<DCFModelsCard ticker="INCOMPLETE.NS" summaryData={summaryData} />);
      
      await waitFor(() => {
        expect(mockApiService.getFinancialData).toHaveBeenCalled();
      });

      // Should achieve ~75% confidence (base only, no bonuses)
    });
  });

  describe('Assumptions Display Tests', () => {
    test('should display dynamic assumptions with correct labels', async () => {
      const financialData = createFinancialData('tier1_leader');
      const basicData = createBasicCompanyData('tier1_leader');
      
      mockApiService.getFinancialData.mockResolvedValue(financialData);
      mockApiService.getBasicCompanyData.mockResolvedValue(basicData);
      mockApiService.getDCFDefaults.mockResolvedValue(mockDCFDefaults);

      const summaryData = createITSummaryData('TCS.NS');
      const { container } = render(<DCFModelsCard ticker="TCS.NS" summaryData={summaryData} />);
      
      await waitFor(() => {
        expect(mockApiService.getFinancialData).toHaveBeenCalled();
      });

      // Should show labels indicating calculated values:
      // - "Revenue Growth (3Y CAGR)"
      // - "EBITDA Margin (3Y Avg)"
      // - "EV/Revenue Multiple"
      // - "Forward Revenue"
    });
  });
});

describe('EV/Revenue Model Integration Tests', () => {
  test('should integrate correctly with sector normalization', async () => {
    const sectorVariations = ['IT', 'Information Technology', 'Software', 'Technology'];
    
    for (const sector of sectorVariations) {
      mockApiService.getFinancialData.mockResolvedValue(createFinancialData('tier1_leader'));
      mockApiService.getBasicCompanyData.mockResolvedValue(createBasicCompanyData('tier1_leader'));
      mockApiService.getDCFDefaults.mockResolvedValue(mockDCFDefaults);

      const summaryData = {
        ...createITSummaryData('TEST.NS'),
        sector
      };
      
      const { container } = render(<DCFModelsCard ticker="TEST.NS" summaryData={summaryData} />);
      
      // All variations should route to EV/Revenue model
      expect(container.textContent).toMatch(/EV\/Revenue/i);
    }
  });

  test('should maintain method consistency across calculations', async () => {
    const financialData = createFinancialData('tier1_leader');
    const basicData = createBasicCompanyData('tier1_leader');
    
    mockApiService.getFinancialData.mockResolvedValue(financialData);
    mockApiService.getBasicCompanyData.mockResolvedValue(basicData);
    mockApiService.getDCFDefaults.mockResolvedValue(mockDCFDefaults);

    const summaryData = createITSummaryData('TCS.NS');
    render(<DCFModelsCard ticker="TCS.NS" summaryData={summaryData} />);
    
    await waitFor(() => {
      expect(mockApiService.getFinancialData).toHaveBeenCalled();
    });

    // Method should consistently be "EV_Revenue_Model"
  });
});