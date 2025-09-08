import React from 'react';
import { AIInvestmentCommittee } from './AIInvestmentCommittee';
import type { InvestmentCommitteeData } from '../../types';

// Sample data for demonstration purposes
const sampleData: InvestmentCommitteeData = {
  validation_report: {
    overall_score: 8.2,
    qualitative_validation: {
      swot_accuracy: "Strong analysis with well-researched strengths and realistic weakness assessment",
      news_interpretation: "Accurate sentiment analysis with appropriate weighting of recent events",
      source_quality: "High-quality sources including annual reports, financial news, and analyst reports",
      findings: [
        "SWOT analysis demonstrates deep understanding of competitive positioning",
        "News sentiment appropriately reflects recent market developments",
        "Source attribution meets institutional investment standards"
      ]
    },
    quantitative_validation: {
      dcf_assumptions_reasonableness: "Conservative yet realistic assumptions aligned with industry benchmarks",
      sensitivity_range_appropriateness: "Comprehensive sensitivity analysis covering realistic scenario ranges",
      calculation_accuracy: "Mathematical accuracy verified, no computational errors detected",
      findings: [
        "Revenue growth assumptions are conservative relative to historical performance",
        "WACC calculation incorporates appropriate risk premium for sector",
        "Terminal growth rate aligns with long-term GDP expectations"
      ]
    },
    key_concerns: [
      "Revenue growth assumptions may be too conservative given strong digital transformation momentum",
      "Tax rate assumptions do not account for potential policy changes in green energy incentives"
    ],
    recommendations: [
      "Consider scenario analysis with higher revenue growth rates (12-15%) for digital services segment",
      "Include sensitivity analysis for tax rate variations (20-30%) due to regulatory uncertainty",
      "Update WACC assumptions quarterly as interest rate environment evolves"
    ]
  },
  bull_commentary: {
    summary_of_assumptions: "Base case assumes 8.5% revenue growth, 15.2% EBITDA margin, and 10.5% WACC with 3% terminal growth",
    bullish_implications: "If the company successfully executes its digital transformation and green energy strategy, revenue growth could accelerate to 12-15% with margin expansion to 18-20%. The digital services business alone could justify a premium valuation multiple, while the renewable energy investments position the company for the energy transition megatrend.",
    recommended_modifications: [
      {
        assumption: "revenue_growth_rate",
        current_value: 8.5,
        recommended_value: 12.0,
        justification: "Digital services expansion and successful 5G monetization could drive accelerated growth, supported by recent partnership announcements"
      },
      {
        assumption: "ebitda_margin",
        current_value: 15.2,
        recommended_value: 18.0,
        justification: "Operational leverage from digital platform scaling and green energy asset optimization should drive margin expansion"
      },
      {
        assumption: "terminal_growth_rate",
        current_value: 3.0,
        recommended_value: 3.5,
        justification: "Leadership position in energy transition and digital infrastructure could sustain above-GDP growth longer term"
      }
    ],
    upside_catalysts: [
      "5G network monetization through enterprise solutions and IoT services driving ARPU expansion",
      "Green hydrogen production becoming commercially viable by 2028, creating new $10B+ revenue stream",
      "Strategic partnerships with global tech giants accelerating digital services revenue to $15B+ by 2030",
      "Carbon credit monetization from renewable energy investments providing additional margin upside",
      "Potential spin-off of digital services business unlocking significant value creation"
    ],
    target_price_scenario: "Bull case target of ₹3,200-3,500 represents 45-60% upside from current levels, driven by re-rating to premium multiples on successful transformation execution"
  },
  bear_commentary: {
    summary_of_assumptions: "Same base assumptions but focusing on execution risks and competitive pressures",
    bearish_implications: "Execution risks in the massive capital-intensive green energy transition, combined with intense competition in telecom and potential oil price volatility, could pressure margins and delay ROI realization. High debt levels limit financial flexibility during economic downturns.",
    recommended_modifications: [
      {
        assumption: "revenue_growth_rate",
        current_value: 8.5,
        recommended_value: 5.5,
        justification: "Competitive pressure in telecom and slower-than-expected digital transformation adoption could constrain growth"
      },
      {
        assumption: "ebitda_margin",
        current_value: 15.2,
        recommended_value: 13.5,
        justification: "Price competition in telecom and higher operational costs for green energy transition could compress margins"
      },
      {
        assumption: "wacc",
        current_value: 10.5,
        recommended_value: 11.5,
        justification: "Higher capital intensity and execution risks warrant higher cost of capital assumption"
      }
    ],
    downside_risks: [
      "Telecom price wars intensifying further, reducing ARPU below ₹150 and pressuring cash generation",
      "Green energy transition facing significant delays or cost overruns, requiring additional ₹50,000+ crores investment",
      "Oil price volatility impacting refining margins, with potential $5-10/barrel sustained downturn affecting cash flows",
      "Regulatory changes in carbon pricing or digital taxation affecting business model economics",
      "Economic recession reducing consumer spending on discretionary services and delaying enterprise digital adoption"
    ],
    conservative_price_scenario: "Bear case target of ₹1,800-2,000 represents 15-25% downside risk if execution challenges materialize and competitive pressures intensify"
  }
};

export const AIInvestmentCommitteeDemo: React.FC = () => {
  return (
    <div className="min-h-screen bg-slate-900 p-6">
      <div className="max-w-7xl mx-auto">
        <AIInvestmentCommittee 
          data={sampleData}
          companyName="Reliance Industries Limited"
          ticker="RELIANCE.NS"
        />
      </div>
    </div>
  );
};

export default AIInvestmentCommitteeDemo;