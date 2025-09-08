import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import { InteractiveDCFAssumptions, type DCFAssumptions, type DCFDefaults } from '../components/DCFValuation/InteractiveDCFAssumptions';

describe('InteractiveDCFAssumptions Component', () => {
  const mockDefaults: DCFDefaults = {
    revenue_growth_rate: 10.0,
    ebitda_margin: 25.0,
    tax_rate: 22.0,
    wacc: 12.0,
    terminal_growth_rate: 3.5,
    projection_years: 10,
    capex_percentage: 4.0,
    working_capital_percentage: 2.0,
    current_price: 3000.0,
    rationale: {
      revenue_growth_rate: "Based on 4 years of historical company data",
      ebitda_margin: "Average margin from company's historical financial statements",
      tax_rate: "Sector-specific effective tax rate from Damodaran data (IT)",
      wacc: "Calculated using Damodaran sector data + live risk-free rate (IT)",
      terminal_growth_rate: "Sector-specific long-term growth rate from Damodaran data (IT)"
    }
  };

  const mockAssumptions: DCFAssumptions = {
    revenue_growth_rate: 10.0,
    ebitda_margin: 25.0,
    tax_rate: 22.0,
    wacc: 12.0,
    terminal_growth_rate: 3.5,
    projection_years: 10,
    capex_percentage: 4.0,
    working_capital_percentage: 2.0
  };

  const mockOnUpdateAssumption = jest.fn();
  const mockOnResetToDefaults = jest.fn();

  beforeEach(() => {
    mockOnUpdateAssumption.mockClear();
    mockOnResetToDefaults.mockClear();
  });

  test('renders all DCF assumption sliders', () => {
    render(
      <InteractiveDCFAssumptions
        assumptions={mockAssumptions}
        defaults={mockDefaults}
        onUpdateAssumption={mockOnUpdateAssumption}
        onResetToDefaults={mockOnResetToDefaults}
        sector="IT"
      />
    );

    // Check for all slider labels
    expect(screen.getByText('Revenue Growth Rate')).toBeInTheDocument();
    expect(screen.getByText('EBITDA Margin')).toBeInTheDocument();
    expect(screen.getByText('Tax Rate')).toBeInTheDocument();
    expect(screen.getByText('WACC')).toBeInTheDocument();
    expect(screen.getByText('Terminal Growth Rate')).toBeInTheDocument();
    expect(screen.getByText('Projection Years')).toBeInTheDocument();
    expect(screen.getByText('CapEx % of Revenue')).toBeInTheDocument();
    expect(screen.getByText('Working Capital %')).toBeInTheDocument();
  });

  test('displays current assumption values', () => {
    render(
      <InteractiveDCFAssumptions
        assumptions={mockAssumptions}
        defaults={mockDefaults}
        onUpdateAssumption={mockOnUpdateAssumption}
        onResetToDefaults={mockOnResetToDefaults}
        sector="IT"
      />
    );

    // Check that current values are displayed
    expect(screen.getByText('10.0%')).toBeInTheDocument(); // Revenue growth
    expect(screen.getByText('25.0%')).toBeInTheDocument(); // EBITDA margin
    expect(screen.getByText('22.0%')).toBeInTheDocument(); // Tax rate
    expect(screen.getByText('12.0%')).toBeInTheDocument(); // WACC
    expect(screen.getByText('3.5%')).toBeInTheDocument(); // Terminal growth
    expect(screen.getByText('10')).toBeInTheDocument(); // Projection years
    expect(screen.getByText('4.0%')).toBeInTheDocument(); // CapEx
    expect(screen.getByText('2.0%')).toBeInTheDocument(); // Working capital
  });

  test('calls onUpdateAssumption when slider values change', async () => {
    const user = userEvent.setup();
    render(
      <InteractiveDCFAssumptions
        assumptions={mockAssumptions}
        defaults={mockDefaults}
        onUpdateAssumption={mockOnUpdateAssumption}
        onResetToDefaults={mockOnResetToDefaults}
        sector="IT"
      />
    );

    // Find revenue growth slider and change its value
    const sliders = screen.getAllByRole('slider');
    const revenueGrowthSlider = sliders[0]; // First slider should be revenue growth

    fireEvent.change(revenueGrowthSlider, { target: { value: '15' } });

    expect(mockOnUpdateAssumption).toHaveBeenCalledWith('revenue_growth_rate', 15);
  });

  test('shows reset button and calls onResetToDefaults when clicked', async () => {
    const user = userEvent.setup();
    render(
      <InteractiveDCFAssumptions
        assumptions={mockAssumptions}
        defaults={mockDefaults}
        onUpdateAssumption={mockOnUpdateAssumption}
        onResetToDefaults={mockOnResetToDefaults}
        sector="IT"
      />
    );

    const resetButton = screen.getByText('Reset to Defaults');
    expect(resetButton).toBeInTheDocument();

    await user.click(resetButton);

    expect(mockOnResetToDefaults).toHaveBeenCalled();
  });

  test('shows modification indicators when values differ from defaults', () => {
    const modifiedAssumptions: DCFAssumptions = {
      ...mockAssumptions,
      revenue_growth_rate: 15.0, // Different from default
      wacc: 14.0 // Different from default
    };

    render(
      <InteractiveDCFAssumptions
        assumptions={modifiedAssumptions}
        defaults={mockDefaults}
        onUpdateAssumption={mockOnUpdateAssumption}
        onResetToDefaults={mockOnResetToDefaults}
        sector="IT"
      />
    );

    // Check that modified values are displayed
    expect(screen.getByText('15.0%')).toBeInTheDocument(); // Modified revenue growth
    expect(screen.getByText('14.0%')).toBeInTheDocument(); // Modified WACC
  });

  test('displays tooltips with helpful information', async () => {
    const user = userEvent.setup();
    render(
      <InteractiveDCFAssumptions
        assumptions={mockAssumptions}
        defaults={mockDefaults}
        onUpdateAssumption={mockOnUpdateAssumption}
        onResetToDefaults={mockOnResetToDefaults}
        sector="IT"
      />
    );

    // Find info icons and hover to show tooltips
    const infoIcons = screen.getAllByTestId('info-icon');
    expect(infoIcons.length).toBeGreaterThan(0);
  });

  test('renders sector-specific content', () => {
    render(
      <InteractiveDCFAssumptions
        assumptions={mockAssumptions}
        defaults={mockDefaults}
        onUpdateAssumption={mockOnUpdateAssumption}
        onResetToDefaults={mockOnResetToDefaults}
        sector="IT"
      />
    );

    // Should render IT sector-specific content if available
    expect(screen.getByText(/IT/)).toBeInTheDocument();
  });

  test('handles edge cases for slider values', async () => {
    render(
      <InteractiveDCFAssumptions
        assumptions={mockAssumptions}
        defaults={mockDefaults}
        onUpdateAssumption={mockOnUpdateAssumption}
        onResetToDefaults={mockOnResetToDefaults}
        sector="IT"
      />
    );

    const sliders = screen.getAllByRole('slider');
    const revenueGrowthSlider = sliders[0];

    // Test minimum value
    fireEvent.change(revenueGrowthSlider, { target: { value: '-10' } });
    expect(mockOnUpdateAssumption).toHaveBeenCalledWith('revenue_growth_rate', -10);

    // Test maximum value
    fireEvent.change(revenueGrowthSlider, { target: { value: '50' } });
    expect(mockOnUpdateAssumption).toHaveBeenCalledWith('revenue_growth_rate', 50);
  });

  test('rationale section displays data sources correctly', () => {
    render(
      <InteractiveDCFAssumptions
        assumptions={mockAssumptions}
        defaults={mockDefaults}
        onUpdateAssumption={mockOnUpdateAssumption}
        onResetToDefaults={mockOnResetToDefaults}
        sector="IT"
      />
    );

    // Check that rationale is displayed
    expect(screen.getByText(/Based on 4 years of historical company data/)).toBeInTheDocument();
    expect(screen.getByText(/Damodaran data/)).toBeInTheDocument();
  });
});