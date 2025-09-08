import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import { ModelSpecificDCFAssumptions } from '../components/DCFValuation/ModelSpecificDCFAssumptions';
import { 
  DCFModelType, 
  MultiStageSimpleDCFAssumptions, 
  MultiStageAgenticDCFAssumptions,
  BankingDCFAssumptions,
  DCFModelDefaults 
} from '../types/dcfModels';

describe('ModelSpecificDCFAssumptions Component', () => {
  const mockOnUpdateAssumption = jest.fn();
  const mockOnResetToDefaults = jest.fn();

  beforeEach(() => {
    mockOnUpdateAssumption.mockClear();
    mockOnResetToDefaults.mockClear();
  });

  describe('Multi-Stage Simple DCF Model', () => {
    const mockSimpleAssumptions: MultiStageSimpleDCFAssumptions = {
      model_type: DCFModelType.MULTI_STAGE_SIMPLE,
      sector: 'IT',
      projection_years: 10,
      stage_1_2_growth: 12.0,
      stage_3_5_growth: 8.0,
      stage_6_8_growth: 5.0,
      stage_9_10_growth: 3.0,
      ebitda_margin: 25.0,
      tax_rate: 22.0,
      wacc: 12.0,
      terminal_growth_rate: 3.5,
      capex_percentage: 4.0,
      working_capital_percentage: 2.0,
      historical_confidence: 0.8,
      gdp_blend_methodology: 'balanced',
      validation_period_years: 5
    };

    const mockSimpleDefaults: DCFModelDefaults = {
      ...mockSimpleAssumptions,
      current_price: 3000.0,
      rationale: {
        stage_1_2_growth: "Based on 5-year historical CAGR analysis",
        ebitda_margin: "Average from 4-year financial statements"
      },
      data_sources: {
        'Historical Data': '5-year revenue and margin analysis',
        'Sector Intelligence': 'Damodaran sector data'
      },
      confidence_scores: {
        stage_1_2_growth: 0.9,
        ebitda_margin: 0.8
      }
    };

    test('renders multi-stage simple DCF assumptions correctly', () => {
      render(
        <ModelSpecificDCFAssumptions
          modelType={DCFModelType.MULTI_STAGE_SIMPLE}
          assumptions={mockSimpleAssumptions}
          defaults={mockSimpleDefaults}
          onUpdateAssumption={mockOnUpdateAssumption}
          onResetToDefaults={mockOnResetToDefaults}
          sector="IT"
          mode="simple"
        />
      );

      // Check for model-specific title
      expect(screen.getByText('10-Year Multi-Stage DCF (Simple Mode)')).toBeInTheDocument();
      
      // Check for stage-specific sliders
      expect(screen.getByText('Stage 1-2 Growth (Years 1-2)')).toBeInTheDocument();
      expect(screen.getByText('Stage 3-5 Growth (Years 3-5)')).toBeInTheDocument();
      expect(screen.getByText('Stage 6-8 Growth (Years 6-8)')).toBeInTheDocument();
      expect(screen.getByText('Stage 9-10 Growth (Years 9-10)')).toBeInTheDocument();

      // Check sector badge
      expect(screen.getByText('IT Sector')).toBeInTheDocument();
      expect(screen.getByText(/simple.*mode/i)).toBeInTheDocument();
    });

    test('displays current assumption values correctly', () => {
      render(
        <ModelSpecificDCFAssumptions
          modelType={DCFModelType.MULTI_STAGE_SIMPLE}
          assumptions={mockSimpleAssumptions}
          defaults={mockSimpleDefaults}
          onUpdateAssumption={mockOnUpdateAssumption}
          onResetToDefaults={mockOnResetToDefaults}
          sector="IT"
          mode="simple"
        />
      );

      // Check that stage values are displayed
      expect(screen.getByText('12.0%')).toBeInTheDocument(); // Stage 1-2 growth
      expect(screen.getByText('8.0%')).toBeInTheDocument();  // Stage 3-5 growth
      expect(screen.getByText('5.0%')).toBeInTheDocument();  // Stage 6-8 growth
      expect(screen.getByText('3.0%')).toBeInTheDocument();  // Stage 9-10 growth
      expect(screen.getByText('25.0%')).toBeInTheDocument(); // EBITDA margin
    });
  });

  describe('Multi-Stage Agentic DCF Model', () => {
    const mockAgenticAssumptions: MultiStageAgenticDCFAssumptions = {
      model_type: DCFModelType.MULTI_STAGE_AGENTIC,
      sector: 'IT',
      projection_years: 10,
      management_guidance_years_1_2: 15.0,
      capacity_expansion_years_3_5: 10.0,
      market_dynamics_years_6_8: 6.0,
      gdp_convergence_years_9_10: 3.0,
      news_sentiment_adjustment: 1.5,
      management_credibility_score: 0.8,
      competitive_moat_strength: 0.7,
      risk_adjusted_wacc: 13.0,
      scenario_weighted_terminal: 3.5,
      ebitda_margin: 25.0,
      tax_rate: 22.0,
      capex_percentage: 4.0,
      working_capital_percentage: 2.0,
      ai_confidence_score: 0.75,
      forward_looking_weight: 0.7
    };

    const mockAgenticDefaults: DCFModelDefaults = {
      ...mockAgenticAssumptions,
      current_price: 3000.0,
      rationale: {
        management_guidance_years_1_2: "AI-extracted from earnings calls",
        news_sentiment_adjustment: "6-month sentiment analysis"
      },
      data_sources: {
        'AI Analysis': 'Management guidance extraction',
        'News Sentiment': '6-month sentiment analysis'
      },
      confidence_scores: {
        management_guidance_years_1_2: 0.85,
        news_sentiment_adjustment: 0.6
      }
    };

    test('renders multi-stage agentic DCF assumptions correctly', () => {
      render(
        <ModelSpecificDCFAssumptions
          modelType={DCFModelType.MULTI_STAGE_AGENTIC}
          assumptions={mockAgenticAssumptions}
          defaults={mockAgenticDefaults}
          onUpdateAssumption={mockOnUpdateAssumption}
          onResetToDefaults={mockOnResetToDefaults}
          sector="IT"
          mode="agentic"
        />
      );

      // Check for model-specific title
      expect(screen.getByText('10-Year Multi-Stage DCF (Agentic Mode)')).toBeInTheDocument();
      
      // Check for AI-specific sliders
      expect(screen.getByText('Management Guidance (Years 1-2)')).toBeInTheDocument();
      expect(screen.getByText('News Sentiment Adjustment')).toBeInTheDocument();
      expect(screen.getByText('Risk-Adjusted WACC')).toBeInTheDocument();

      // Check mode badge
      expect(screen.getByText(/agentic.*mode/i)).toBeInTheDocument();
    });
  });

  describe('Banking DCF Model', () => {
    const mockBankingAssumptions: BankingDCFAssumptions = {
      model_type: DCFModelType.BANKING_DCF,
      sector: 'BFSI',
      projection_years: 5,
      credit_growth_rate: 15.0,
      net_interest_margin: 3.5,
      cost_income_ratio: 45.0,
      tier_1_capital_ratio: 13.0,
      provision_coverage_ratio: 80.0,
      roe_target: 16.0,
      credit_cost_ratio: 0.8,
      casa_ratio: 42.0,
      tax_rate: 25.0,
      terminal_growth_rate: 3.0,
      discount_rate: 14.0
    };

    const mockBankingDefaults: DCFModelDefaults = {
      ...mockBankingAssumptions,
      current_price: 1500.0,
      rationale: {
        credit_growth_rate: "4-year loan book CAGR analysis",
        net_interest_margin: "Current NIM from Q4 financials"
      },
      data_sources: {
        'Historical Banking Data': 'Loan book and NIM analysis',
        'Regulatory Data': 'RBI guidelines and Basel III'
      },
      confidence_scores: {
        credit_growth_rate: 0.9,
        net_interest_margin: 0.8
      }
    };

    test('renders banking DCF assumptions correctly', () => {
      render(
        <ModelSpecificDCFAssumptions
          modelType={DCFModelType.BANKING_DCF}
          assumptions={mockBankingAssumptions}
          defaults={mockBankingDefaults}
          onUpdateAssumption={mockOnUpdateAssumption}
          onResetToDefaults={mockOnResetToDefaults}
          sector="BFSI"
        />
      );

      // Check for banking-specific sliders
      expect(screen.getByText('Credit Growth Rate')).toBeInTheDocument();
      expect(screen.getByText('Net Interest Margin (NIM)')).toBeInTheDocument();
      expect(screen.getByText('Cost-to-Income Ratio')).toBeInTheDocument();
      expect(screen.getByText('ROE Target')).toBeInTheDocument();
      expect(screen.getByText('Tier 1 Capital Ratio')).toBeInTheDocument();

      // Check banking-specific values
      expect(screen.getByText('15.0%')).toBeInTheDocument(); // Credit growth
      expect(screen.getByText('3.5%')).toBeInTheDocument();  // NIM
      expect(screen.getByText('16.0%')).toBeInTheDocument(); // ROE target
    });
  });

  describe('Interactive Functionality', () => {
    const mockSimpleAssumptions: MultiStageSimpleDCFAssumptions = {
      model_type: DCFModelType.MULTI_STAGE_SIMPLE,
      sector: 'IT',
      projection_years: 10,
      stage_1_2_growth: 10.0,
      stage_3_5_growth: 7.0,
      stage_6_8_growth: 4.0,
      stage_9_10_growth: 3.0,
      ebitda_margin: 20.0,
      tax_rate: 25.0,
      wacc: 12.0,
      terminal_growth_rate: 3.0,
      capex_percentage: 4.0,
      working_capital_percentage: 2.0,
      historical_confidence: 0.8,
      gdp_blend_methodology: 'balanced',
      validation_period_years: 5
    };

    const mockSimpleDefaults: DCFModelDefaults = {
      ...mockSimpleAssumptions,
      current_price: 2500.0,
      rationale: {},
      data_sources: {},
      confidence_scores: {}
    };

    test('calls onUpdateAssumption when slider values change', async () => {
      render(
        <ModelSpecificDCFAssumptions
          modelType={DCFModelType.MULTI_STAGE_SIMPLE}
          assumptions={mockSimpleAssumptions}
          defaults={mockSimpleDefaults}
          onUpdateAssumption={mockOnUpdateAssumption}
          onResetToDefaults={mockOnResetToDefaults}
          sector="IT"
          mode="simple"
        />
      );

      // Find sliders and change their values
      const sliders = screen.getAllByRole('slider');
      const firstSlider = sliders[0]; // Should be stage_1_2_growth

      fireEvent.change(firstSlider, { target: { value: '15' } });

      expect(mockOnUpdateAssumption).toHaveBeenCalledWith('stage_1_2_growth', 15);
    });

    test('shows reset button and calls onResetToDefaults when clicked', async () => {
      const user = userEvent.setup();
      
      // Create modified assumptions to trigger reset button
      const modifiedAssumptions = {
        ...mockSimpleAssumptions,
        stage_1_2_growth: 15.0 // Different from default
      };

      render(
        <ModelSpecificDCFAssumptions
          modelType={DCFModelType.MULTI_STAGE_SIMPLE}
          assumptions={modifiedAssumptions}
          defaults={mockSimpleDefaults}
          onUpdateAssumption={mockOnUpdateAssumption}
          onResetToDefaults={mockOnResetToDefaults}
          sector="IT"
          mode="simple"
        />
      );

      const resetButton = screen.getByText('Reset to Defaults');
      expect(resetButton).toBeInTheDocument();

      await user.click(resetButton);

      expect(mockOnResetToDefaults).toHaveBeenCalled();
    });

    test('displays enhanced tooltips with data sources', async () => {
      const user = userEvent.setup();
      render(
        <ModelSpecificDCFAssumptions
          modelType={DCFModelType.MULTI_STAGE_SIMPLE}
          assumptions={mockSimpleAssumptions}
          defaults={mockSimpleDefaults}
          onUpdateAssumption={mockOnUpdateAssumption}
          onResetToDefaults={mockOnResetToDefaults}
          sector="IT"
          mode="simple"
        />
      );

      // Find info icons and check tooltips
      const infoIcons = screen.getAllByTestId('info-icon');
      expect(infoIcons.length).toBeGreaterThan(0);

      // Hover over first info icon
      await user.hover(infoIcons[0]);
      
      // Should show enhanced tooltip
      await waitFor(() => {
        expect(screen.getByText(/Near-term growth/)).toBeInTheDocument();
      });
    });
  });

  describe('Error Handling', () => {
    test('shows fallback message for unimplemented model types', () => {
      render(
        <ModelSpecificDCFAssumptions
          modelType={DCFModelType.REAL_ESTATE_DCF}
          assumptions={{} as any}
          defaults={{} as any}
          onUpdateAssumption={mockOnUpdateAssumption}
          onResetToDefaults={mockOnResetToDefaults}
          sector="REAL ESTATE"
        />
      );

      expect(screen.getByText(/Configuration not yet implemented/)).toBeInTheDocument();
    });
  });
});