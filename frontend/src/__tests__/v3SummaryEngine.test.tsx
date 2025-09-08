// Test suite for EquityScope v3 Summary Engine
import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { SummaryBox } from '../components/SummaryEngine/SummaryBox';
import { FairValueBandChart } from '../components/SummaryEngine/FairValueBandChart';
import { InvestmentLabelBadge } from '../components/SummaryEngine/InvestmentLabelBadge';
import { KeyFactorsList } from '../components/SummaryEngine/KeyFactorsList';
import { ThreeLensAnalysis } from '../components/SummaryEngine/ThreeLensAnalysis';
import { v3ApiService } from '../services/v3ApiService';
import type { SummaryResponse } from '../types/summary';

// Mock data for testing
const mockSummaryData: SummaryResponse = {
  ticker: 'TCS.NS',
  company_name: 'Tata Consultancy Services Limited',
  fair_value_band: {
    min_value: 3000,
    max_value: 3500,
    current_price: 3200,
    method: 'DCF',
    confidence: 0.8
  },
  investment_label: 'Cautiously Bullish',
  key_factors: [
    'Moderately undervalued based on DCF analysis',
    'Strong technical momentum with RSI oversold',
    'Consistent revenue growth and margin expansion'
  ],
  valuation_insights: 'DCF analysis indicates fair value of ₹3,250. Current price offers limited upside with strong downside protection.',
  market_signals: 'RSI at 28 indicates oversold territory. MACD showing potential bullish crossover. Volume above average.',
  business_fundamentals: 'Revenue growth of 15% CAGR. Strong margins at 25%. ROE consistently above 30%. Management guidance positive.',
  data_health_warnings: ['Technical indicators cached (2 hours old)'],
  analysis_timestamp: '2025-07-29T23:30:00.000Z',
  analysis_mode: 'simple',
  sector: 'IT'
};

describe('V3 Summary Engine Components', () => {
  describe('FairValueBandChart', () => {
    test('renders fair value band with correct price positioning', () => {
      render(<FairValueBandChart fairValueBand={mockSummaryData.fair_value_band} />);
      
      expect(screen.getByText('Fair Value Band')).toBeInTheDocument();
      expect(screen.getByText('₹3000')).toBeInTheDocument();
      expect(screen.getByText('₹3500')).toBeInTheDocument();
      expect(screen.getByText('₹3200')).toBeInTheDocument();
      expect(screen.getByText('DCF')).toBeInTheDocument();
      expect(screen.getByText('80%')).toBeInTheDocument();
    });

    test('shows undervalued status when price below band', () => {
      const undervaluedBand = {
        ...mockSummaryData.fair_value_band,
        current_price: 2800
      };
      
      render(<FairValueBandChart fairValueBand={undervaluedBand} />);
      expect(screen.getByText('Undervalued')).toBeInTheDocument();
    });
  });

  describe('InvestmentLabelBadge', () => {
    test('renders investment label with correct styling', () => {
      render(
        <InvestmentLabelBadge 
          label={mockSummaryData.investment_label}
          confidence={mockSummaryData.fair_value_band.confidence}
        />
      );
      
      expect(screen.getByText('Cautiously Bullish')).toBeInTheDocument();
      expect(screen.getByText('Investment Assessment')).toBeInTheDocument();
      expect(screen.getByText('80% confidence')).toBeInTheDocument();
      expect(screen.getByText('High')).toBeInTheDocument();
    });

    test('shows low confidence warning when confidence < 0.6', () => {
      render(
        <InvestmentLabelBadge 
          label="Neutral"
          confidence={0.5}
        />
      );
      
      expect(screen.getByText('Low confidence analysis due to limited data availability')).toBeInTheDocument();
    });
  });

  describe('KeyFactorsList', () => {
    test('renders key factors with expand/collapse functionality', () => {
      render(<KeyFactorsList factors={mockSummaryData.key_factors} />);
      
      expect(screen.getByText('Key Factors')).toBeInTheDocument();
      expect(screen.getByText('3 factors identified')).toBeInTheDocument();
      expect(screen.getByText(/Moderately undervalued based on DCF analysis/)).toBeInTheDocument();
    });

    test('shows expand button when more than 3 factors', () => {
      const manyFactors = [
        'Factor 1', 'Factor 2', 'Factor 3', 'Factor 4', 'Factor 5'
      ];
      
      render(<KeyFactorsList factors={manyFactors} />);
      expect(screen.getByText('Show 2 More')).toBeInTheDocument();
    });
  });

  describe('ThreeLensAnalysis', () => {
    test('renders three lens tabs and content', () => {
      render(
        <ThreeLensAnalysis
          valuation={mockSummaryData.valuation_insights}
          market={mockSummaryData.market_signals}
          fundamentals={mockSummaryData.business_fundamentals}
        />
      );
      
      expect(screen.getByText('Three Lens Analysis')).toBeInTheDocument();
      expect(screen.getByText('Valuation Insights')).toBeInTheDocument();
      expect(screen.getByText('Market Signals')).toBeInTheDocument();
      expect(screen.getByText('Business & Macro Fundamentals')).toBeInTheDocument();
    });

    test('expands lens content when clicked', async () => {
      render(
        <ThreeLensAnalysis
          valuation={mockSummaryData.valuation_insights}
          market={mockSummaryData.market_signals}
          fundamentals={mockSummaryData.business_fundamentals}
        />
      );
      
      fireEvent.click(screen.getByText('Valuation Insights'));
      
      await waitFor(() => {
        expect(screen.getByText(/DCF analysis indicates fair value/)).toBeInTheDocument();
      });
    });
  });

  describe('SummaryBox Integration', () => {
    test('renders complete summary box with all components', () => {
      const mockOnModeToggle = jest.fn();
      const mockOnRefresh = jest.fn();
      
      render(
        <SummaryBox
          ticker="TCS.NS"
          summary={mockSummaryData}
          onModeToggle={mockOnModeToggle}
          isLoading={false}
          onRefresh={mockOnRefresh}
        />
      );
      
      // Check header
      expect(screen.getByText('Tata Consultancy Services Limited')).toBeInTheDocument();
      expect(screen.getByText('TCS.NS')).toBeInTheDocument();
      expect(screen.getByText('IT')).toBeInTheDocument();
      
      // Check analysis mode toggle
      expect(screen.getByText('Rule-Based Analysis')).toBeInTheDocument();
      expect(screen.getByText('AI Analyst Insights')).toBeInTheDocument();
      
      // Check components are rendered
      expect(screen.getByText('Fair Value Band')).toBeInTheDocument();
      expect(screen.getByText('Investment Assessment')).toBeInTheDocument();
      expect(screen.getByText('Key Factors')).toBeInTheDocument();
      expect(screen.getByText('Three Lens Analysis')).toBeInTheDocument();
    });

    test('calls onModeToggle when analysis mode is changed', () => {
      const mockOnModeToggle = jest.fn();
      
      render(
        <SummaryBox
          ticker="TCS.NS"
          summary={mockSummaryData}
          onModeToggle={mockOnModeToggle}
          isLoading={false}
        />
      );
      
      fireEvent.click(screen.getByText('AI Analyst Insights'));
      expect(mockOnModeToggle).toHaveBeenCalledWith('agentic');
    });
  });
});

describe('V3 API Service', () => {
  test('provides mock data with correct structure', () => {
    const mockData = v3ApiService.getMockSummary('TEST.NS', 'simple');
    
    expect(mockData.ticker).toBe('TEST.NS');
    expect(mockData.analysis_mode).toBe('simple');
    expect(mockData.fair_value_band).toHaveProperty('min_value');
    expect(mockData.fair_value_band).toHaveProperty('max_value');
    expect(mockData.fair_value_band).toHaveProperty('current_price');
    expect(mockData.investment_label).toBeDefined();
    expect(Array.isArray(mockData.key_factors)).toBe(true);
  });

  test('generates different data for different modes', () => {
    const simpleData = v3ApiService.getMockSummary('TEST.NS', 'simple');
    const agenticData = v3ApiService.getMockSummary('TEST.NS', 'agentic');
    
    expect(simpleData.analysis_mode).toBe('simple');
    expect(agenticData.analysis_mode).toBe('agentic');
    expect(simpleData.fair_value_band.method).toBe('PE_Multiple');
    expect(agenticData.fair_value_band.method).toBe('DCF');
  });
});

// Integration test for component interaction
describe('V3 Summary Engine Integration', () => {
  test('components work together in summary display', () => {
    const mockOnModeToggle = jest.fn();
    
    render(
      <SummaryBox
        ticker="TCS.NS"
        summary={mockSummaryData}
        onModeToggle={mockOnModeToggle}
        isLoading={false}
      />
    );
    
    // Test Fair Value Band integration
    expect(screen.getByText('Fair Value Band')).toBeInTheDocument();
    expect(screen.getByText('₹3000')).toBeInTheDocument();
    
    // Test Investment Label integration  
    expect(screen.getByText('Investment Assessment')).toBeInTheDocument();
    expect(screen.getByText('Cautiously Bullish')).toBeInTheDocument();
    
    // Test Key Factors integration
    expect(screen.getByText('Key Factors')).toBeInTheDocument();
    expect(screen.getByText(/Moderately undervalued/)).toBeInTheDocument();
    
    // Test Three Lens Analysis integration
    expect(screen.getByText('Three Lens Analysis')).toBeInTheDocument();
    
    // Test data health warnings
    expect(screen.getByText('Data Health Status')).toBeInTheDocument();
    expect(screen.getByText(/Technical indicators cached/)).toBeInTheDocument();
  });
});