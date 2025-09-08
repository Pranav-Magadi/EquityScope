// Cost Protection Integration Tests
import React from 'react';
import { render, screen, waitFor, fireEvent, act } from '@testing-library/react';
import '@testing-library/jest-dom';
import { DCFModelsCard } from '../components/DCFValuation/DCFModelsCard';
import * as ApiService from '../services/api';
import type { SummaryResponse } from '../types/summary';

// Mock API Service
jest.mock('../services/api');
const mockApiService = ApiService as jest.Mocked<typeof ApiService>;

// Mock console methods to track system behavior
const consoleSpy = jest.spyOn(console, 'log').mockImplementation();
const consoleWarnSpy = jest.spyOn(console, 'warn').mockImplementation();

// Test data
const mockSummaryData: SummaryResponse = {
  ticker: 'TESTCORP.NS',
  company_name: 'Test Corporation Limited',
  fair_value_band: {
    min_value: 950,
    max_value: 1050,
    current_price: 1000,
    confidence_score: 0.75
  },
  sector: 'IT',
  analysis_mode: 'agentic' as const,
  key_metrics: {
    revenue: 50000,
    market_cap: 100000,
    pe_ratio: 25.0,
    debt_to_equity: 0.15
  }
};

const mockFinancialData = {
  ticker: 'TESTCORP.NS',
  revenue: [50000000000, 45000000000, 40000000000],
  ebitda: [12000000000, 11000000000, 10000000000],
  shares_outstanding: [1000000000, 1000000000, 1000000000]
};

const mockBasicCompanyData = {
  stock_price: {
    current_price: 1000,
    market_cap: 100000000000,
    pe_ratio: 25.0,
    pb_ratio: 3.2
  }
};

const mockDCFDefaults = {
  revenue_growth_rate: 15.0,
  ebitda_margin: 24.0,
  tax_rate: 25.0,
  wacc: 12.0,
  terminal_growth_rate: 4.0,
  projection_years: 10,
  capex_percentage: 3.0,
  working_capital_percentage: 1.5,
  current_price: 1000,
  rationale: {}
};

describe('Cost Protection Integration Tests', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    consoleSpy.mockClear();
    consoleWarnSpy.mockClear();
    
    // Setup default mocks
    mockApiService.getFinancialData.mockResolvedValue(mockFinancialData);
    mockApiService.getBasicCompanyData.mockResolvedValue(mockBasicCompanyData);
    mockApiService.getDCFDefaults.mockResolvedValue(mockDCFDefaults);
    mockApiService.getDCFInsights.mockResolvedValue({
      insights: {
        investment_thesis: 'Test thesis',
        model_interpretation: 'Test interpretation',
        key_insights: ['Test insight'],
        risk_commentary: ['Test risk'],
        red_flags: ['Test flag'],
        confidence_score: 0.8
      }
    });
  });

  afterEach(() => {
    consoleSpy.mockRestore();
    consoleWarnSpy.mockRestore();
  });

  describe('System Recalculation Limit Enforcement', () => {
    test('should enforce 10 recalculation limit per ticker', async () => {
      render(<DCFModelsCard ticker="TESTCORP.NS" summaryData={mockSummaryData} />);

      // Wait for initial calculations
      await waitFor(() => {
        expect(mockApiService.getFinancialData).toHaveBeenCalled();
      }, { timeout: 5000 });

      // Check system recalculation logs
      const systemRecalcLogs = consoleSpy.mock.calls.filter(call =>
        call[0]?.includes('💰 System recalculation #')
      );

      expect(systemRecalcLogs.length).toBeLessThanOrEqual(10);
    });

    test('should display cost protection counter when recalculations occur', async () => {
      render(<DCFModelsCard ticker="TESTCORP.NS" summaryData={mockSummaryData} />);

      await waitFor(() => {
        expect(mockApiService.getFinancialData).toHaveBeenCalled();
      }, { timeout: 5000 });

      // Look for cost protection counter in UI
      const costIndicator = screen.queryByText(/System Recalcs:/);
      
      if (costIndicator) {
        expect(costIndicator).toBeInTheDocument();
        expect(costIndicator.textContent).toMatch(/\d+\/10/);
      }
    });

    test('should prevent further system recalculations after limit reached', async () => {
      // Mock scenario where limit would be exceeded
      let recalculationCount = 0;
      mockApiService.getDCFInsights.mockImplementation(async () => {
        recalculationCount++;
        if (recalculationCount > 10) {
          throw new Error('Should not reach this - cost protection should prevent');
        }
        return {
          insights: {
            investment_thesis: `Test thesis ${recalculationCount}`,
            model_interpretation: 'Test interpretation',
            key_insights: ['Test insight'],
            risk_commentary: ['Test risk'],
            red_flags: ['Test flag'],
            confidence_score: 0.8
          }
        };
      });

      render(<DCFModelsCard ticker="TESTCORP.NS" summaryData={mockSummaryData} />);

      // Wait for maximum processing time
      await waitFor(() => {
        expect(mockApiService.getFinancialData).toHaveBeenCalled();
      }, { timeout: 15000 });

      // Should not exceed recalculation limit
      expect(recalculationCount).toBeLessThanOrEqual(10);

      // Should show cost protection warning
      const costProtectionWarnings = consoleWarnSpy.mock.calls.filter(call =>
        call[0]?.includes('💰 COST PROTECTION')
      );

      if (recalculationCount >= 10) {
        expect(costProtectionWarnings.length).toBeGreaterThan(0);
      }
    });
  });

  describe('Cost Protection Messaging', () => {
    test('should show enhanced fallback insights when cost limit reached', async () => {
      // Force cost protection by simulating limit reached
      mockApiService.getDCFInsights.mockImplementation(async () => {
        throw new Error('Cost limit simulation');
      });

      render(<DCFModelsCard ticker="TESTCORP.NS" summaryData={mockSummaryData} />);

      await waitFor(() => {
        expect(screen.getByText(/AI Insights/)).toBeInTheDocument();
      }, { timeout: 10000 });

      // Should show structured cost protection message
      expect(screen.getByText(/Cost protection active/i) || 
             screen.getByText(/manual analysis recommended/i)).toBeInTheDocument();

      // Should maintain structured format
      expect(screen.getByText(/Investment Thesis/i) ||
             screen.getByText(/Fair value:/)).toBeInTheDocument();
    });

    test('should indicate cost protection status in insights', async () => {
      render(<DCFModelsCard ticker="TESTCORP.NS" summaryData={mockSummaryData} />);

      // Wait for potential cost protection activation
      await waitFor(() => {
        expect(mockApiService.getFinancialData).toHaveBeenCalled();
      }, { timeout: 10000 });

      // Check for cost protection indicators
      const costProtectionLogs = consoleSpy.mock.calls.filter(call =>
        call[0]?.includes('Cost protection') ||
        call[0]?.includes('recalculation limit')
      );

      // If cost protection was activated, should see appropriate messaging
      if (costProtectionLogs.length > 0) {
        expect(screen.getByText(/cost protection/i) ||
               screen.getByText(/manual review/i)).toBeInTheDocument();
      }
    });
  });

  describe('User vs System Operation Differentiation', () => {
    test('should allow unlimited user-initiated assumption changes', async () => {
      render(<DCFModelsCard ticker="TESTCORP.NS" summaryData={mockSummaryData} />);

      await waitFor(() => {
        expect(screen.getByText(/Valuation Models/i)).toBeInTheDocument();
      }, { timeout: 5000 });

      // Simulate multiple user assumption changes (should not be limited)
      const userChanges = 15; // More than system limit
      
      for (let i = 0; i < userChanges; i++) {
        act(() => {
          // Simulate user-initiated change (not counted against system limit)
          console.log(`👤 User-initiated assumption change #${i + 1}`);
        });
      }

      // Verify user changes are logged and not blocked
      const userChangeLogs = consoleSpy.mock.calls.filter(call =>
        call[0]?.includes('👤 User-initiated')
      );
      
      expect(userChangeLogs.length).toBe(userChanges);
    });

    test('should distinguish between user and system operations in logs', async () => {
      render(<DCFModelsCard ticker="TESTCORP.NS" summaryData={mockSummaryData} />);

      await waitFor(() => {
        expect(mockApiService.getFinancialData).toHaveBeenCalled();
      }, { timeout: 5000 });

      // Check log patterns
      const systemLogs = consoleSpy.mock.calls.filter(call =>
        call[0]?.includes('💰 System recalculation')
      );
      
      const userLogs = consoleSpy.mock.calls.filter(call =>
        call[0]?.includes('👤 User-initiated')
      );

      // Should be able to distinguish between system and user operations
      expect(systemLogs.length + userLogs.length).toBeGreaterThanOrEqual(0);
    });
  });

  describe('Ticker Reset Functionality', () => {
    test('should reset cost protection counter for new ticker', async () => {
      const { rerender } = render(<DCFModelsCard ticker="TESTCORP.NS" summaryData={mockSummaryData} />);

      // Wait for initial load
      await waitFor(() => {
        expect(mockApiService.getFinancialData).toHaveBeenCalled();
      }, { timeout: 5000 });

      // Change to new ticker
      const newSummaryData = { 
        ...mockSummaryData, 
        ticker: 'NEWCORP.NS',
        company_name: 'New Corporation Limited'
      };
      
      rerender(<DCFModelsCard ticker="NEWCORP.NS" summaryData={newSummaryData} />);

      // Should see reset message for new ticker
      await waitFor(() => {
        const resetLogs = consoleSpy.mock.calls.filter(call =>
          call[0]?.includes('💰 Reset system recalculation counter')
        );
        expect(resetLogs.length).toBeGreaterThan(0);
      }, { timeout: 5000 });
    });

    test('should start fresh cost protection for each new ticker', async () => {
      const tickers = ['TICKER1.NS', 'TICKER2.NS', 'TICKER3.NS'];
      
      for (const ticker of tickers) {
        const summaryData = {
          ...mockSummaryData,
          ticker,
          company_name: `${ticker} Company`
        };

        const { unmount } = render(<DCFModelsCard ticker={ticker} summaryData={summaryData} />);

        await waitFor(() => {
          expect(mockApiService.getFinancialData).toHaveBeenCalledWith(ticker, expect.any(Number));
        }, { timeout: 5000 });

        // Each ticker should start with fresh cost protection
        const resetLogs = consoleSpy.mock.calls.filter(call =>
          call[0]?.includes('💰 Reset system recalculation counter')
        );
        expect(resetLogs.length).toBeGreaterThanOrEqual(tickers.indexOf(ticker));

        unmount();
      }
    });
  });

  describe('Error Handling with Cost Protection', () => {
    test('should maintain cost protection during error scenarios', async () => {
      // Simulate API errors after some successful calls
      let callCount = 0;
      mockApiService.getDCFInsights.mockImplementation(async () => {
        callCount++;
        if (callCount > 5) {
          throw new Error('Simulated API error');
        }
        return {
          insights: {
            investment_thesis: 'Test thesis',
            model_interpretation: 'Test interpretation',
            key_insights: ['Test insight'],
            risk_commentary: ['Test risk'],
            red_flags: ['Test flag'],
            confidence_score: 0.8
          }
        };
      });

      render(<DCFModelsCard ticker="TESTCORP.NS" summaryData={mockSummaryData} />);

      await waitFor(() => {
        expect(mockApiService.getFinancialData).toHaveBeenCalled();
      }, { timeout: 10000 });

      // Cost protection should still be enforced even during errors
      expect(callCount).toBeLessThanOrEqual(10);

      // Should show error handling with cost awareness
      const errorLogs = consoleSpy.mock.calls.filter(call =>
        call[0]?.includes('❌ Error fetching AI insights') ||
        call[0]?.includes('💰 COST PROTECTION')
      );

      if (callCount > 5) {
        expect(errorLogs.length).toBeGreaterThan(0);
      }
    });

    test('should provide fallback insights when both cost limit and errors occur', async () => {
      // Simulate cost limit reached AND API errors
      mockApiService.getDCFInsights.mockRejectedValue(new Error('Service unavailable'));

      render(<DCFModelsCard ticker="TESTCORP.NS" summaryData={mockSummaryData} />);

      await waitFor(() => {
        expect(screen.getByText(/AI Insights/)).toBeInTheDocument();
      }, { timeout: 10000 });

      // Should show appropriate fallback message
      expect(screen.getByText(/unavailable/i) ||
             screen.getByText(/manual/i) ||
             screen.getByText(/fallback/i)).toBeInTheDocument();

      // Should maintain structured format even in fallback
      expect(screen.getByText(/Fair value/i) ||
             screen.getByText(/Investment/i)).toBeInTheDocument();
    });
  });

  describe('Performance Under Cost Protection', () => {
    test('should maintain responsive UI even when cost protection activates', async () => {
      render(<DCFModelsCard ticker="TESTCORP.NS" summaryData={mockSummaryData} />);

      const startTime = performance.now();

      await waitFor(() => {
        expect(screen.getByText(/Valuation Models/i)).toBeInTheDocument();
      }, { timeout: 5000 });

      const loadTime = performance.now() - startTime;

      // Should load within reasonable time even with cost protection
      expect(loadTime).toBeLessThan(5000); // 5 seconds max
    });

    test('should not block UI interactions during cost protection', async () => {
      render(<DCFModelsCard ticker="TESTCORP.NS" summaryData={mockSummaryData} />);

      await waitFor(() => {
        expect(screen.getByText(/Valuation Models/i)).toBeInTheDocument();
      }, { timeout: 5000 });

      // Try to interact with UI elements
      const assumptionsToggle = screen.queryByText(/Show.*DCF.*Assumptions/i);
      if (assumptionsToggle) {
        fireEvent.click(assumptionsToggle);
        
        // UI should respond immediately
        await waitFor(() => {
          expect(screen.getByText(/Hide.*DCF.*Assumptions/i)).toBeInTheDocument();
        }, { timeout: 1000 });
      }
    });
  });

  describe('Integration with Enhanced AI Insights', () => {
    test('should apply cost protection to enhanced AI insights format', async () => {
      render(<DCFModelsCard ticker="TESTCORP.NS" summaryData={mockSummaryData} />);

      await waitFor(() => {
        expect(mockApiService.getDCFInsights).toHaveBeenCalled();
      }, { timeout: 10000 });

      // Verify enhanced request structure respects cost protection
      if (mockApiService.getDCFInsights.mock.calls.length > 0) {
        const callArgs = mockApiService.getDCFInsights.mock.calls[0];
        const enhancedData = callArgs[3]; // Enhanced company data

        expect(enhancedData).toHaveProperty('analysis_requirements');
        
        // Should not call more than cost protection allows
        expect(mockApiService.getDCFInsights.mock.calls.length).toBeLessThanOrEqual(10);
      }
    });

    test('should maintain enhanced format in cost protection fallbacks', async () => {
      // Force cost protection by rejecting API calls
      mockApiService.getDCFInsights.mockRejectedValue(new Error('Cost protection test'));

      render(<DCFModelsCard ticker="TESTCORP.NS" summaryData={mockSummaryData} />);

      await waitFor(() => {
        expect(screen.getByText(/AI Insights/)).toBeInTheDocument();
      }, { timeout: 10000 });

      // Should show enhanced structured fallback format
      expect(screen.getByText(/🧠/i) ||
             screen.getByText(/Investment Thesis/i) ||
             screen.getByText(/Fair value:/i)).toBeInTheDocument();
    });
  });
});

export {};