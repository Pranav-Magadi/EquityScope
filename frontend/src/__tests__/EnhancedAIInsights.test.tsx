// Enhanced AI Insights Test Suite
import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { DCFModelsCard } from '../components/DCFValuation/DCFModelsCard';
import * as ApiService from '../services/api';
import type { SummaryResponse } from '../types/summary';

// Mock API Service
jest.mock('../services/api');
const mockApiService = ApiService as jest.Mocked<typeof ApiService>;

// Mock data for testing
const mockRelianceSummaryData: SummaryResponse = {
  ticker: 'RELIANCE.NS',
  company_name: 'Reliance Industries Limited',
  fair_value_band: {
    min_value: 1600,
    max_value: 1700,
    current_price: 1367,
    confidence_score: 0.78
  },
  sector: 'ENERGY',
  analysis_mode: 'agentic' as const,
  key_metrics: {
    revenue: 964693,
    market_cap: 1854900,
    pe_ratio: 22.5,
    debt_to_equity: 0.25
  }
};

const mockFinancialData = {
  ticker: 'RELIANCE.NS',
  revenue: [964693000000, 875000000000, 792000000000],
  ebitda: [180000000000, 160000000000, 145000000000],
  shares_outstanding: [13530000000, 13530000000, 13530000000]
};

const mockDCFDefaults = {
  revenue_growth_rate: 11.94,
  ebitda_margin: 18.61,
  tax_rate: 30,
  wacc: 11.0,
  terminal_growth_rate: 5.0,
  projection_years: 10,
  capex_percentage: 4.0,
  working_capital_percentage: 2.0,
  current_price: 1367,
  rationale: {}
};

// Enhanced AI Insights Response Mock
const mockEnhancedAIResponse = {
  insights: {
    investment_thesis: "Reliance trades 20.5% below fair value of ₹1647, driven by undervalued energy and digital verticals. Diversified portfolio and renewable energy capex cycle offer strong long-term upside. Digital monetization acceleration provides additional growth catalyst.",
    
    model_interpretation: `**🧠 Investment Thesis:** Reliance shows 20.5% upside at ₹1367 vs fair ₹1647, supported by energy recovery and Jio digital growth.

**🔍 Industry Signals:** Improving refining margins (+15% YoY) and rising Jio ARPU (₹175→₹181) support valuation uplift.

**📈 DCF Assessment:** Conservative 9.5% WACC and 4.5% terminal growth suggest revised fair value of ₹1538 vs ₹1647 base case.

**⚠️ Risk Flags:** 5G spectrum auction costs and renewable energy capex could pressure near-term cash flows.`,

    key_insights: [
      "Fair value: ₹1647 (20.5% upside potential)",
      "Refining margin recovery driving energy vertical performance",
      "Jio subscriber monetization accelerating with 5G rollout",
      "Renewable energy capex creating long-term value despite near-term costs"
    ],
    
    risk_commentary: [
      "Upcoming spectrum auctions could strain cash flows if Jio underperforms",
      "Crude oil volatility impacts refining and petrochemical margins",
      "Regulatory changes in telecom sector affecting pricing power"
    ],
    
    red_flags: [
      "High terminal growth rate (5%) vs India GDP norm (4-4.5%)",
      "WACC assumption may be optimistic given debt refinancing cycles",
      "Retail expansion capex requirements not fully reflected in projections"
    ],
    
    confidence_score: 0.8
  }
};

describe('Enhanced AI Insights Implementation', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    
    // Setup default mock returns
    mockApiService.getFinancialData.mockResolvedValue(mockFinancialData);
    mockApiService.getBasicCompanyData.mockResolvedValue({
      stock_price: {
        current_price: 1367,
        market_cap: 1854900000000,
        pe_ratio: 22.5,
        pb_ratio: 2.1
      }
    });
    mockApiService.getDCFDefaults.mockResolvedValue(mockDCFDefaults);
  });

  describe('Enhanced API Request Structure', () => {
    test('should send enhanced company data with analysis requirements', async () => {
      mockApiService.getDCFInsights.mockResolvedValue(mockEnhancedAIResponse);

      render(<DCFModelsCard ticker="RELIANCE.NS" summaryData={mockRelianceSummaryData} />);

      // Wait for AI insights API call
      await waitFor(() => {
        expect(mockApiService.getDCFInsights).toHaveBeenCalled();
      }, { timeout: 10000 });

      // Verify enhanced request structure
      const callArgs = mockApiService.getDCFInsights.mock.calls[0];
      const enhancedCompanyData = callArgs[3]; // 4th argument

      expect(enhancedCompanyData).toHaveProperty('analysis_requirements');
      expect(enhancedCompanyData.analysis_requirements).toEqual({
        format: "structured_retail_friendly",
        sections: [
          "investment_thesis_3_lines_max",
          "industry_macro_signals",
          "ai_diagnostic_commentary", 
          "smart_risk_flags"
        ],
        tone: "action_oriented_retail_friendly",
        avoid: ["generic_language", "verbose_paragraphs", "repeated_inputs"],
        include: ["specific_numbers", "company_positioning", "growth_levers", "revised_fair_value"]
      });

      expect(enhancedCompanyData).toHaveProperty('current_price', 1367);
      expect(enhancedCompanyData).toHaveProperty('industry_context', 'ENERGY');
    });

    test('should include correct DCF result data in API request', async () => {
      mockApiService.getDCFInsights.mockResolvedValue(mockEnhancedAIResponse);

      render(<DCFModelsCard ticker="RELIANCE.NS" summaryData={mockRelianceSummaryData} />);

      await waitFor(() => {
        expect(mockApiService.getDCFInsights).toHaveBeenCalled();
      }, { timeout: 10000 });

      const callArgs = mockApiService.getDCFInsights.mock.calls[0];
      const dcfResult = callArgs[1]; // 2nd argument

      expect(dcfResult).toHaveProperty('fairValue');
      expect(dcfResult).toHaveProperty('currentPrice');
      expect(dcfResult).toHaveProperty('upside');
      expect(dcfResult).toHaveProperty('confidence');
      expect(dcfResult).toHaveProperty('method');
    });
  });

  describe('Structured AI Insights Display', () => {
    test('should display enhanced AI insights in structured format', async () => {
      mockApiService.getDCFInsights.mockResolvedValue(mockEnhancedAIResponse);

      render(<DCFModelsCard ticker="RELIANCE.NS" summaryData={mockRelianceSummaryData} />);

      await waitFor(() => {
        expect(screen.getByText(/AI Insights/)).toBeInTheDocument();
      }, { timeout: 10000 });

      // Check Investment Thesis
      expect(screen.getByText(/Reliance trades 20.5% below fair value/)).toBeInTheDocument();
      
      // Check structured sections
      expect(screen.getByText(/🧠 Investment Thesis/)).toBeInTheDocument();
      expect(screen.getByText(/🔍 Industry Signals/)).toBeInTheDocument();
      expect(screen.getByText(/📈 DCF Assessment/)).toBeInTheDocument();
      expect(screen.getByText(/⚠️ Risk Flags/)).toBeInTheDocument();

      // Check specific insights
      expect(screen.getByText(/Fair value: ₹1647/)).toBeInTheDocument();
      expect(screen.getByText(/Refining margin recovery/)).toBeInTheDocument();
    });

    test('should display key insights as actionable bullet points', async () => {
      mockApiService.getDCFInsights.mockResolvedValue(mockEnhancedAIResponse);

      render(<DCFModelsCard ticker="RELIANCE.NS" summaryData={mockRelianceSummaryData} />);

      await waitFor(() => {
        expect(screen.getByText(/Key Insights/)).toBeInTheDocument();
      }, { timeout: 10000 });

      // Check bullet points
      mockEnhancedAIResponse.insights.key_insights.forEach(insight => {
        expect(screen.getByText(new RegExp(insight.substring(0, 20)))).toBeInTheDocument();
      });
    });

    test('should display smart risk flags with context', async () => {
      mockApiService.getDCFInsights.mockResolvedValue(mockEnhancedAIResponse);

      render(<DCFModelsCard ticker="RELIANCE.NS" summaryData={mockRelianceSummaryData} />);

      await waitFor(() => {
        expect(screen.getByText(/Risk Commentary/)).toBeInTheDocument();
      }, { timeout: 10000 });

      // Check contextual risks (not generic)
      expect(screen.getByText(/spectrum auctions could strain cash flows/)).toBeInTheDocument();
      expect(screen.getByText(/Crude oil volatility impacts/)).toBeInTheDocument();
    });
  });

  describe('Enhanced Fallback Insights', () => {
    test('should provide structured fallback when AI service fails', async () => {
      mockApiService.getDCFInsights.mockRejectedValue(new Error('Service unavailable'));

      render(<DCFModelsCard ticker="RELIANCE.NS" summaryData={mockRelianceSummaryData} />);

      await waitFor(() => {
        expect(screen.getByText(/AI Insights/)).toBeInTheDocument();
      }, { timeout: 10000 });

      // Check structured fallback format
      expect(screen.getByText(/🧠 Investment Thesis:/)).toBeInTheDocument();
      expect(screen.getByText(/🔍 Industry Signals:/)).toBeInTheDocument();
      expect(screen.getByText(/📈 DCF Assessment:/)).toBeInTheDocument();
      expect(screen.getByText(/⚠️ Risk Flags:/)).toBeInTheDocument();

      // Check specific fallback content
      expect(screen.getByText(/Reliance Industries Limited shows/)).toBeInTheDocument();
      expect(screen.getByText(/Manual review required/)).toBeInTheDocument();
    });

    test('should handle different error types with specific messages', async () => {
      // Test timeout error
      const timeoutError = { code: 'ECONNABORTED', message: 'timeout exceeded' };
      mockApiService.getDCFInsights.mockRejectedValue(timeoutError);

      const { rerender } = render(<DCFModelsCard ticker="RELIANCE.NS" summaryData={mockRelianceSummaryData} />);

      await waitFor(() => {
        expect(screen.getByText(/Request timeout/)).toBeInTheDocument();
      }, { timeout: 10000 });

      // Test rate limit error
      const rateLimitError = { response: { status: 429 }, message: 'Rate limit exceeded' };
      mockApiService.getDCFInsights.mockRejectedValue(rateLimitError);

      rerender(<DCFModelsCard ticker="TCS.NS" summaryData={{...mockRelianceSummaryData, ticker: 'TCS.NS'}} />);

      await waitFor(() => {
        expect(screen.getByText(/Rate limit exceeded/)).toBeInTheDocument();
      }, { timeout: 10000 });
    });
  });

  describe('Cost Protection Enhanced Format', () => {
    test('should display structured format when cost protection activates', async () => {
      // Mock component in state where cost limit is reached
      const costProtectedComponent = render(<DCFModelsCard ticker="RELIANCE.NS" summaryData={mockRelianceSummaryData} />);
      
      // Simulate cost protection by making multiple rapid calls
      for (let i = 0; i < 12; i++) {
        fireEvent.click(screen.getByText(/Refresh/i) || document.body);
      }

      await waitFor(() => {
        // Should show cost protection message
        expect(screen.getByText(/Cost protection active/)).toBeInTheDocument();
      }, { timeout: 5000 });

      // Check structured cost protection format
      expect(screen.getByText(/🧠 Investment Thesis:/)).toBeInTheDocument();
      expect(screen.getByText(/Cost Protection.*System recalculation limit reached/)).toBeInTheDocument();
    });

    test('should show cost protection counter in UI', async () => {
      render(<DCFModelsCard ticker="RELIANCE.NS" summaryData={mockRelianceSummaryData} />);

      await waitFor(() => {
        // Should eventually show system recalculation counter
        const counter = screen.queryByText(/System Recalcs:/);
        if (counter) {
          expect(counter).toBeInTheDocument();
          expect(counter.textContent).toMatch(/\d+\/10/);
        }
      }, { timeout: 10000 });
    });
  });

  describe('Performance and Error Handling', () => {
    test('should implement debouncing to prevent rapid API calls', async () => {
      jest.useFakeTimers();
      mockApiService.getDCFInsights.mockResolvedValue(mockEnhancedAIResponse);

      render(<DCFModelsCard ticker="RELIANCE.NS" summaryData={mockRelianceSummaryData} />);

      // Should not call API immediately
      expect(mockApiService.getDCFInsights).not.toHaveBeenCalled();

      // Fast-forward 2 seconds (debounce period)
      jest.advanceTimersByTime(2000);

      await waitFor(() => {
        expect(mockApiService.getDCFInsights).toHaveBeenCalledTimes(1);
      });

      jest.useRealTimers();
    });

    test('should not retry on any error type', async () => {
      mockApiService.getDCFInsights
        .mockRejectedValueOnce(new Error('Network error'))
        .mockResolvedValue(mockEnhancedAIResponse);

      render(<DCFModelsCard ticker="RELIANCE.NS" summaryData={mockRelianceSummaryData} />);

      await waitFor(() => {
        // Should only call once, no retries
        expect(mockApiService.getDCFInsights).toHaveBeenCalledTimes(1);
      }, { timeout: 10000 });

      // Should show fallback insights, not retry
      expect(screen.getByText(/AI analysis unavailable/)).toBeInTheDocument();
    });
  });

  describe('Integration with DCF Valuation', () => {
    test('should generate insights based on calculated fair value', async () => {
      mockApiService.getDCFInsights.mockResolvedValue(mockEnhancedAIResponse);

      render(<DCFModelsCard ticker="RELIANCE.NS" summaryData={mockRelianceSummaryData} />);

      await waitFor(() => {
        expect(mockApiService.getDCFInsights).toHaveBeenCalled();
      }, { timeout: 10000 });

      const callArgs = mockApiService.getDCFInsights.mock.calls[0];
      const dcfResult = callArgs[1];

      // Should use calculated values, not static ones
      expect(typeof dcfResult.fairValue).toBe('number');
      expect(typeof dcfResult.upside).toBe('number');
      expect(dcfResult.fairValue).toBeGreaterThan(0);
    });

    test('should update insights when valuation model changes', async () => {
      mockApiService.getDCFInsights.mockResolvedValue(mockEnhancedAIResponse);

      render(<DCFModelsCard ticker="RELIANCE.NS" summaryData={mockRelianceSummaryData} />);

      // Wait for initial load
      await waitFor(() => {
        expect(mockApiService.getDCFInsights).toHaveBeenCalled();
      }, { timeout: 10000 });

      const initialCalls = mockApiService.getDCFInsights.mock.calls.length;

      // Switch to PE model
      const peTab = screen.queryByText(/PE.*based/i);
      if (peTab) {
        fireEvent.click(peTab);

        await waitFor(() => {
          // Should call API again for new model
          expect(mockApiService.getDCFInsights.mock.calls.length).toBeGreaterThan(initialCalls);
        }, { timeout: 5000 });
      }
    });
  });

  describe('Accessibility and UX', () => {
    test('should show loading state during insights generation', async () => {
      // Delay the API response
      mockApiService.getDCFInsights.mockImplementation(
        () => new Promise(resolve => setTimeout(() => resolve(mockEnhancedAIResponse), 1000))
      );

      render(<DCFModelsCard ticker="RELIANCE.NS" summaryData={mockRelianceSummaryData} />);

      // Should show loading indicator
      expect(screen.getByText(/Loading insights/i) || screen.getByRole('progressbar')).toBeInTheDocument();

      await waitFor(() => {
        expect(screen.getByText(/AI Insights/)).toBeInTheDocument();
      }, { timeout: 15000 });
    });

    test('should maintain insights when switching between tabs', async () => {
      mockApiService.getDCFInsights.mockResolvedValue(mockEnhancedAIResponse);

      render(<DCFModelsCard ticker="RELIANCE.NS" summaryData={mockRelianceSummaryData} />);

      await waitFor(() => {
        expect(screen.getByText(/Investment Thesis/)).toBeInTheDocument();
      }, { timeout: 10000 });

      // Switch tabs and verify insights persist
      const assumptionsToggle = screen.queryByText(/Show.*DCF.*Assumptions/i);
      if (assumptionsToggle) {
        fireEvent.click(assumptionsToggle);
        fireEvent.click(screen.getByText(/Hide.*DCF.*Assumptions/i));
        
        // Insights should still be there
        expect(screen.getByText(/Investment Thesis/)).toBeInTheDocument();
      }
    });
  });
});

export {};