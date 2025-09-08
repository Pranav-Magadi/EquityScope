import type { DCFProjection, DCFAssumptions, ProjectionChartData } from '../types';

export class DCFUtils {
  /**
   * Format currency values
   */
  static formatCurrency(value: number, currency: string = 'INR'): string {
    if (isNaN(value) || value === null || value === undefined) {
      return '₹0';
    }

    const formatter = new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: currency === 'INR' ? 'INR' : 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    });

    // Convert to appropriate units
    if (Math.abs(value) >= 10000000) { // 1 crore
      return formatter.format(value / 10000000).replace(/[₹$]/, '') + (currency === 'INR' ? ' Cr' : 'M');
    } else if (Math.abs(value) >= 100000) { // 1 lakh
      return formatter.format(value / 100000).replace(/[₹$]/, '') + (currency === 'INR' ? ' L' : 'K');
    } else {
      return formatter.format(value);
    }
  }

  /**
   * Format percentage values
   */
  static formatPercentage(value: number, decimals: number = 1): string {
    if (isNaN(value) || value === null || value === undefined) {
      return '0.0%';
    }
    return `${value.toFixed(decimals)}%`;
  }

  /**
   * Format large numbers with appropriate suffixes
   */
  static formatLargeNumber(value: number): string {
    if (isNaN(value) || value === null || value === undefined) {
      return '0';
    }

    const absValue = Math.abs(value);
    
    if (absValue >= 1000000000000) { // Trillion
      return (value / 1000000000000).toFixed(1) + 'T';
    } else if (absValue >= 1000000000) { // Billion
      return (value / 1000000000).toFixed(1) + 'B';
    } else if (absValue >= 1000000) { // Million
      return (value / 1000000).toFixed(1) + 'M';
    } else if (absValue >= 1000) { // Thousand
      return (value / 1000).toFixed(1) + 'K';
    } else {
      return value.toFixed(0);
    }
  }

  /**
   * Calculate growth rate between two values
   */
  static calculateGrowthRate(currentValue: number, previousValue: number): number {
    if (!previousValue || previousValue === 0) return 0;
    return ((currentValue - previousValue) / previousValue) * 100;
  }

  /**
   * Validate DCF assumptions
   */
  static validateAssumptions(assumptions: DCFAssumptions): { isValid: boolean; errors: string[] } {
    const errors: string[] = [];

    // Revenue growth rate validation
    if (assumptions.revenue_growth_rate < -50 || assumptions.revenue_growth_rate > 100) {
      errors.push('Revenue growth rate should be between -50% and 100%');
    }

    // EBITDA margin validation - expanded range for banking/financial companies
    if (assumptions.ebitda_margin < -50 || assumptions.ebitda_margin > 200) {
      errors.push('EBITDA margin should be between -50% and 200%');
    }

    // Tax rate validation
    if (assumptions.tax_rate < 0 || assumptions.tax_rate > 60) {
      errors.push('Tax rate should be between 0% and 60%');
    }

    // WACC validation
    if (assumptions.wacc < 1 || assumptions.wacc > 50) {
      errors.push('WACC should be between 1% and 50%');
    }

    // Terminal growth rate validation
    if (assumptions.terminal_growth_rate < -5 || assumptions.terminal_growth_rate > 15) {
      errors.push('Terminal growth rate should be between -5% and 15%');
    }

    // Terminal growth should be less than WACC
    if (assumptions.terminal_growth_rate >= assumptions.wacc) {
      errors.push('Terminal growth rate should be less than WACC');
    }

    return {
      isValid: errors.length === 0,
      errors
    };
  }

  /**
   * Convert DCF projections to chart data
   */
  static convertToChartData(projections: DCFProjection[]): ProjectionChartData[] {
    return projections.map(projection => ({
      year: projection.year,
      revenue: projection.revenue,
      ebitda: projection.ebitda,
      free_cash_flow: projection.free_cash_flow,
      present_value: projection.present_value
    }));
  }

  /**
   * Calculate compound annual growth rate (CAGR)
   */
  static calculateCAGR(startValue: number, endValue: number, years: number): number {
    if (startValue <= 0 || endValue <= 0 || years <= 0) return 0;
    return (Math.pow(endValue / startValue, 1 / years) - 1) * 100;
  }

  /**
   * Get sensitivity color based on value relative to base case
   */
  static getSensitivityColor(value: number, baseValue: number): string {
    const percentDiff = ((value - baseValue) / baseValue) * 100;
    
    if (percentDiff > 10) return 'bg-green-900/30 text-green-300';
    if (percentDiff > 5) return 'bg-green-900/20 text-green-400';
    if (percentDiff < -10) return 'bg-red-900/30 text-red-300';
    if (percentDiff < -5) return 'bg-red-900/20 text-red-400';
    return 'bg-slate-800 text-slate-300';
  }

  /**
   * Generate assumption tooltips
   */
  static getAssumptionTooltip(key: keyof DCFAssumptions): string {
    const tooltips = {
      revenue_growth_rate: 'Expected annual revenue growth rate for the next 5 years. Based on historical performance and industry outlook.',
      ebitda_margin: 'EBITDA as a percentage of revenue. Reflects operational efficiency and profitability.',
      tax_rate: 'Effective corporate tax rate. Use the company\'s historical tax rate or statutory rate.',
      wacc: 'Weighted Average Cost of Capital. The discount rate that reflects the company\'s cost of equity and debt.',
      terminal_growth_rate: 'Long-term growth rate beyond the projection period. Should not exceed long-term GDP growth.',
      projection_years: 'Number of years to project cash flows explicitly before calculating terminal value.'
    };
    
    return tooltips[key] || '';
  }

  /**
   * Calculate present value factor
   */
  static calculatePresentValueFactor(rate: number, periods: number): number {
    return 1 / Math.pow(1 + rate / 100, periods);
  }

  /**
   * Format ratio values
   */
  static formatRatio(value: number): string {
    if (isNaN(value) || value === null || value === undefined) {
      return 'N/A';
    }
    return value.toFixed(1) + 'x';
  }

  /**
   * Determine if a metric represents improvement
   */
  static isPositiveMetric(value: number, previousValue?: number): boolean {
    if (previousValue === undefined) return value > 0;
    return value > previousValue;
  }

  /**
   * Get color class for metric based on value
   */
  static getMetricColorClass(value: number, previousValue?: number): string {
    if (this.isPositiveMetric(value, previousValue)) {
      return 'text-green-400';
    } else if (value < 0 || (previousValue && value < previousValue)) {
      return 'text-red-400';
    }
    return 'text-slate-300';
  }

  /**
   * Calculate implied multiples from DCF valuation
   */
  static calculateImpliedMultiples(
    intrinsicValue: number,
    revenue: number,
    ebitda: number,
    netIncome: number
  ): { peRatio: number; evEbitda: number; priceToSales: number } {
    return {
      peRatio: netIncome > 0 ? intrinsicValue / netIncome : 0,
      evEbitda: ebitda > 0 ? intrinsicValue / ebitda : 0,
      priceToSales: revenue > 0 ? intrinsicValue / revenue : 0
    };
  }
}