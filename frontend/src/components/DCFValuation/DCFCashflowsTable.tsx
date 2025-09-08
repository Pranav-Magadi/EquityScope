import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { ChevronDown, ChevronUp, Table, Info } from 'lucide-react';

interface DCFCashflowsTableProps {
  valuation: any;
  assumptions: any;
}

interface ProjectionRow {
  label: string;
  values: number[];
  isPercentage?: boolean;
  isHighlighted?: boolean;
  tooltip?: string;
}

export const DCFCashflowsTable: React.FC<DCFCashflowsTableProps> = ({
  valuation,
  assumptions
}) => {
  const [isExpanded, setIsExpanded] = useState(false);

  // Calculate 10-year projections with correct financial methodology
  const calculateProjections = (): ProjectionRow[] => {
    const projectionYears = 10;
    const years = Array.from({ length: projectionYears }, (_, i) => new Date().getFullYear() + i + 1);
    
    // Starting values (assuming we have base revenue from valuation)
    const baseRevenue = valuation?.summary?.revenue || valuation?.revenue || 100000; // Fallback if not available
    
    // Get assumptions (with fallbacks if not present)
    const capexPercent = assumptions.capex_percentage || 5.0;
    const wcChangePercent = assumptions.working_capital_percentage || 2.0;
    const depreciationPercent = assumptions.depreciation_percentage || 3.5;
    
    // Initialize arrays for calculations
    const revenues: number[] = [];
    const revenueGrowthRates: number[] = [];
    const ebitdas: number[] = [];
    const ebitdaMargins: number[] = [];
    const depreciationAmortization: number[] = [];
    const ebits: number[] = [];
    const taxes: number[] = [];
    const nopats: number[] = []; // Net Operating Profit After Tax
    const capexValues: number[] = [];
    const workingCapitalChanges: number[] = [];
    const fcffs: number[] = [];
    const discountFactors: number[] = [];
    const presentValues: number[] = [];

    // Calculate year-by-year projections
    for (let year = 0; year < projectionYears; year++) {
      // Revenue growth rate (declining over time to terminal growth)
      const terminalGrowth = assumptions.terminal_growth_rate;
      const initialGrowth = assumptions.revenue_growth_rate;
      
      // Linear convergence to terminal growth over 10 years
      const convergenceWeight = year / (projectionYears - 1);
      const currentGrowthRate = initialGrowth * (1 - convergenceWeight) + terminalGrowth * convergenceWeight;
      revenueGrowthRates.push(currentGrowthRate);

      // Revenue calculation
      const revenue = year === 0 
        ? baseRevenue * (1 + currentGrowthRate / 100)
        : revenues[year - 1] * (1 + currentGrowthRate / 100);
      revenues.push(revenue);

      // EBITDA calculation
      const ebitda = revenue * (assumptions.ebitda_margin / 100);
      ebitdas.push(ebitda);
      ebitdaMargins.push(assumptions.ebitda_margin);

      // Depreciation & Amortization (as % of revenue)
      const da = revenue * (depreciationPercent / 100);
      depreciationAmortization.push(da);

      // EBIT calculation (CORRECT: EBITDA - D&A)
      const ebit = ebitda - da;
      ebits.push(ebit);

      // Taxes calculation (CORRECT: Tax on EBIT, not EBITDA)
      const tax = Math.max(0, ebit * (assumptions.tax_rate / 100)); // No negative taxes
      taxes.push(tax);

      // NOPAT calculation (Net Operating Profit After Tax)
      const nopat = ebit - tax;
      nopats.push(nopat);

      // CapEx calculation (as % of revenue)
      const capex = revenue * (capexPercent / 100);
      capexValues.push(capex);

      // Working Capital Change (as % of revenue change)
      const wcChange = year === 0 
        ? revenue * (wcChangePercent / 100)
        : (revenue - revenues[year - 1]) * (wcChangePercent / 100);
      workingCapitalChanges.push(wcChange);

      // Free Cash Flow to Firm calculation (CORRECT FORMULA)
      // FCFF = NOPAT + D&A - CapEx - Change in WC
      // This is equivalent to: EBIT * (1 - Tax Rate) + D&A - CapEx - Change in WC
      const fcff = nopat + da - capex - wcChange;
      fcffs.push(fcff);

      // Discount Factor calculation
      const discountFactor = 1 / Math.pow(1 + assumptions.wacc / 100, year + 1);
      discountFactors.push(discountFactor);

      // Present Value calculation
      const presentValue = fcff * discountFactor;
      presentValues.push(presentValue);
    }

    // Return structured data for table
    return [
      {
        label: 'Revenue',
        values: revenues,
        tooltip: 'Projected annual revenue converging from initial to terminal growth rate'
      },
      {
        label: 'Revenue Growth Rate (%)',
        values: revenueGrowthRates,
        isPercentage: true,
        tooltip: 'Year-over-year revenue growth rate (converging to terminal growth)'
      },
      {
        label: 'EBITDA',
        values: ebitdas,
        tooltip: 'Earnings Before Interest, Taxes, Depreciation & Amortization'
      },
      {
        label: 'EBITDA Margin (%)',
        values: ebitdaMargins,
        isPercentage: true,
        tooltip: 'EBITDA as percentage of revenue (held constant)'
      },
      {
        label: 'Depreciation & Amortization',
        values: depreciationAmortization,
        tooltip: `D&A as ${depreciationPercent.toFixed(1)}% of revenue (non-cash charge)`
      },
      {
        label: 'EBIT',
        values: ebits,
        tooltip: 'Earnings Before Interest and Taxes (EBITDA - D&A)'
      },
      {
        label: 'Taxes',
        values: taxes,
        tooltip: `Corporate income taxes on EBIT at ${assumptions.tax_rate.toFixed(1)}% rate`
      },
      {
        label: 'NOPAT',
        values: nopats,
        tooltip: 'Net Operating Profit After Tax (EBIT - Taxes)'
      },
      {
        label: 'Capital Expenditures (CapEx)',
        values: capexValues,
        tooltip: `Investment in fixed assets (${capexPercent.toFixed(1)}% of revenue)`
      },
      {
        label: 'Change in Working Capital',
        values: workingCapitalChanges,
        tooltip: `Working capital change (${wcChangePercent.toFixed(1)}% of revenue growth)`
      },
      {
        label: 'Free Cash Flow to the Firm (FCFF)',
        values: fcffs,
        isHighlighted: true,
        tooltip: 'NOPAT + D&A - CapEx - ΔWC (cash available to all investors)'
      },
      {
        label: 'Discount Factor',
        values: discountFactors,
        tooltip: `Present value factor using ${assumptions.wacc.toFixed(1)}% WACC`
      },
      {
        label: 'Present Value of FCFF',
        values: presentValues,
        isHighlighted: true,
        tooltip: 'FCFF discounted back to present value using WACC'
      }
    ];
  };

  const projectionData = calculateProjections();
  const currentYear = new Date().getFullYear();
  const years = Array.from({ length: 10 }, (_, i) => currentYear + i + 1);

  // Calculate summary values
  const sumOfPV = projectionData[12].values.reduce((sum, val) => sum + val, 0); // Present Values
  const terminalValuePV = valuation?.terminal_value || 0;
  const totalEnterpriseValue = sumOfPV + terminalValuePV;
  const totalEquityValue = (valuation?.intrinsic_value_per_share || valuation?.fairValue || 0) * (valuation?.shares_outstanding || 1);

  const formatValue = (value: number, isPercentage?: boolean): string => {
    if (isPercentage) {
      return `${value.toFixed(1)}%`;
    }
    
    // Format large numbers in Crores
    if (Math.abs(value) >= 10000000) {
      return `₹${(value / 10000000).toFixed(1)}Cr`;
    } else if (Math.abs(value) >= 100000) {
      return `₹${(value / 100000).toFixed(1)}L`;
    } else {
      return `₹${value.toFixed(0)}`;
    }
  };

  if (!isExpanded) {
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="bg-slate-800/50 rounded-lg p-4 cursor-pointer hover:bg-slate-800/70 transition-colors"
        onClick={() => setIsExpanded(true)}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Table className="h-5 w-5 text-slate-400" />
            <h4 className="text-md font-medium text-slate-300">Show Calculation Breakdown</h4>
          </div>
          <ChevronDown className="h-5 w-5 text-slate-400" />
        </div>
        <p className="text-sm text-slate-400 mt-1">
          View detailed 10-year cash flow projections and present value calculations
        </p>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, height: 0 }}
      animate={{ opacity: 1, height: 'auto' }}
      transition={{ duration: 0.3 }}
      className="bg-slate-800/50 rounded-lg p-4 space-y-4"
    >
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Table className="h-5 w-5 text-slate-400" />
          <h4 className="text-md font-medium text-slate-300">DCF Cash Flow Projections</h4>
        </div>
        <button
          onClick={() => setIsExpanded(false)}
          className="p-1 hover:bg-slate-700 rounded transition-colors"
        >
          <ChevronUp className="h-5 w-5 text-slate-400" />
        </button>
      </div>

      {/* Projections Table */}
      <div className="overflow-x-auto">
        <table className="w-full min-w-max">
          {/* Table Header */}
          <thead>
            <tr className="border-b border-slate-700">
              <th className="text-left text-xs font-medium text-slate-400 p-2 sticky left-0 bg-slate-800/90 min-w-48">
                Metric
              </th>
              {years.map((year) => (
                <th key={year} className="text-center text-xs font-medium text-slate-400 p-2 min-w-24">
                  {year}
                </th>
              ))}
            </tr>
          </thead>

          {/* Table Body */}
          <tbody>
            {projectionData.map((row, rowIndex) => (
              <motion.tr
                key={row.label}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.2, delay: rowIndex * 0.05 }}
                className={`
                  border-b border-slate-700/50 hover:bg-slate-700/30 transition-colors
                  ${row.isHighlighted ? 'bg-primary-900/10' : ''}
                `}
              >
                {/* Row Label */}
                <td className="text-left text-xs p-2 sticky left-0 bg-slate-800/90">
                  <div className="flex items-center space-x-1">
                    <span className={`
                      ${row.isHighlighted ? 'text-primary-300 font-medium' : 'text-slate-300'}
                    `}>
                      {row.label}
                    </span>
                    {row.tooltip && (
                      <div className="relative group">
                        <Info className="h-3 w-3 text-slate-500 cursor-help" />
                        <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 w-48 bg-slate-900 text-slate-200 text-xs rounded-lg p-2 border border-slate-700 opacity-0 group-hover:opacity-100 transition-opacity z-50 pointer-events-none">
                          {row.tooltip}
                        </div>
                      </div>
                    )}
                  </div>
                </td>

                {/* Data Cells */}
                {row.values.map((value, colIndex) => (
                  <td key={colIndex} className="text-center text-xs p-2">
                    <span className={`
                      font-mono
                      ${row.isHighlighted ? 'text-primary-300 font-medium' : 'text-slate-300'}
                      ${value < 0 ? 'text-red-400' : ''}
                    `}>
                      {formatValue(value, row.isPercentage)}
                    </span>
                  </td>
                ))}
              </motion.tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Summary Section */}
      <div className="bg-slate-700/30 rounded-lg p-3 space-y-2">
        <h5 className="text-sm font-medium text-slate-300">Valuation Summary</h5>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-xs">
          <div>
            <div className="text-slate-400">Sum of PV (10 years)</div>
            <div className="text-primary-400 font-semibold">
              {formatValue(sumOfPV)}
            </div>
          </div>
          <div>
            <div className="text-slate-400">Terminal Value (PV)</div>
            <div className="text-primary-400 font-semibold">
              {formatValue(terminalValuePV)}
            </div>
          </div>
          <div>
            <div className="text-slate-400">Total Enterprise Value</div>
            <div className="text-primary-400 font-semibold">
              {formatValue(totalEnterpriseValue)}
            </div>
          </div>
          <div>
            <div className="text-slate-400">Total Equity Value</div>
            <div className="text-primary-400 font-semibold font-bold">
              {formatValue(totalEquityValue)}
            </div>
          </div>
        </div>
      </div>

      {/* Methodology Note */}
      <div className="text-xs text-slate-400 bg-slate-700/20 rounded p-2">
        <div className="font-medium mb-1">Methodology:</div>
        <div>
          <strong>Correct FCFF Formula:</strong> NOPAT + D&A - CapEx - ΔWC • 
          Taxes calculated on EBIT (not EBITDA) • D&A = {assumptions.depreciation_percentage || 3.5}% of revenue • 
          CapEx = {assumptions.capex_percentage || 5.0}% of revenue • 
          Working capital change = {assumptions.working_capital_percentage || 2.0}% of revenue growth • 
          WACC = {assumptions.wacc?.toFixed(1) || 'N/A'}% discount rate
        </div>
      </div>
    </motion.div>
  );
};