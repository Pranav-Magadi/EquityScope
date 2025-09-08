import type { ExperienceLevel, ContentType } from '../components/common/ProgressiveDisclosure';

interface EducationalContentItem {
  id: string;
  type: ContentType;
  title: string;
  content: string;
  levels: ExperienceLevel[];
  priority: 'high' | 'medium' | 'low';
  relatedConcepts?: string[];
}

export const DCF_10_YEAR_EDUCATIONAL_CONTENT: Record<string, EducationalContentItem[]> = {
  'dcf_basics': [
    {
      id: 'dcf_intro',
      type: 'concept',
      title: 'What is DCF (Discounted Cash Flow)?',
      content: 'DCF is a valuation method that estimates a company\'s value by predicting its future cash flows and converting them to present value. Think of it like asking: "If I buy this company today, what will all the cash it generates in the future be worth in today\'s money?" The 10-year model gives us a longer view than traditional 5-year models.',
      levels: ['beginner', 'intermediate', 'advanced'],
      priority: 'high',
      relatedConcepts: ['Present Value', 'Time Value of Money', 'Intrinsic Value']
    },
    {
      id: 'intrinsic_value',
      type: 'concept',
      title: 'Understanding Intrinsic Value',
      content: 'Intrinsic value is what a company is "really worth" based on its fundamentals, not what the market currently prices it at. Our DCF calculation shows this fair value per share. If intrinsic value > current price, the stock might be undervalued. If intrinsic value < current price, it might be overvalued.',
      levels: ['beginner', 'intermediate', 'advanced'],
      priority: 'high',
      relatedConcepts: ['Market Price', 'Undervalued', 'Overvalued']
    },
    {
      id: 'time_value_money',
      type: 'concept',
      title: 'Time Value of Money',
      content: 'Money today is worth more than the same amount in the future because you can invest it and earn returns. This is why we "discount" future cash flows. A dollar received 10 years from now is worth less than a dollar today. The discount rate (WACC) tells us how much less.',
      levels: ['beginner', 'intermediate'],
      priority: 'high',
      relatedConcepts: ['WACC', 'Discount Rate', 'Present Value']
    }
  ],

  'multi_stage_growth': [
    {
      id: 'why_10_years',
      type: 'concept',
      title: 'Why 10 Years Instead of 5?',
      content: 'Traditional DCF models use 5 years, but we extend to 10 years to better capture long-term business cycles and competitive dynamics. Many companies need more than 5 years to fully realize their growth potential or reach competitive equilibrium. The 10-year view helps us model the transition from high growth to mature, steady-state growth more accurately.',
      levels: ['beginner', 'intermediate', 'advanced'],
      priority: 'high',
      relatedConcepts: ['Business Cycles', 'Competitive Dynamics', 'Terminal Value']
    },
    {
      id: 'growth_stages',
      type: 'methodology',
      title: 'Multi-Stage Growth Model',
      content: 'Our model divides the 10-year projection into stages: Years 1-2 (near-term momentum), Years 3-5 (competitive positioning), Years 6-8 (market maturation), Years 9-10 + Terminal (GDP convergence). Each stage has different growth assumptions based on competitive realities and market dynamics.',
      levels: ['intermediate', 'advanced'],
      priority: 'high',
      relatedConcepts: ['Competitive Fade', 'Market Maturity', 'GDP Growth']
    },
    {
      id: 'gdp_blending',
      type: 'methodology',
      title: 'GDP Blending Logic',
      content: 'Over time, companies cannot grow faster than the overall economy indefinitely. Our model gradually blends company-specific growth with India\'s GDP growth (3%). Early years use mostly historical data, but later years increasingly weight GDP growth as the company matures and competitive advantages fade.',
      levels: ['intermediate', 'advanced'],
      priority: 'high',
      relatedConcepts: ['Economic Constraints', 'Competitive Fade', 'Long-term Growth']
    },
    {
      id: 'competitive_fade',
      type: 'concept',
      title: 'Understanding Competitive Fade',
      content: 'No company can maintain high growth rates forever. Competition intensifies, markets mature, and extraordinary returns attract new entrants. Our multi-stage model captures this reality by gradually reducing growth rates over time, reflecting the natural business lifecycle.',
      levels: ['intermediate', 'advanced'],
      priority: 'medium',
      relatedConcepts: ['Market Competition', 'Business Lifecycle', 'Mean Reversion']
    }
  ],

  'mode_selection': [
    {
      id: 'simple_vs_agentic',
      type: 'concept',
      title: 'Simple Mode vs Agentic Mode',
      content: 'Simple Mode uses historical data and rule-based logic - perfect for learning DCF fundamentals and getting conservative estimates. Agentic Mode adds AI analysis of management guidance, news sentiment, and forward-looking insights - better for comprehensive analysis but more complex to interpret.',
      levels: ['beginner', 'intermediate', 'advanced'],
      priority: 'high',
      relatedConcepts: ['Historical Analysis', 'AI Enhancement', 'Management Guidance']
    },
    {
      id: 'when_use_simple',
      type: 'tip',
      title: 'When to Use Simple Mode',
      content: 'Choose Simple Mode when: (1) Learning DCF basics, (2) You want conservative, historically-grounded estimates, (3) Analyzing mature, stable companies, (4) You prefer transparent, rule-based calculations. Simple Mode is ideal for building DCF intuition and understanding core concepts.',
      levels: ['beginner', 'intermediate'],
      priority: 'medium',
      relatedConcepts: ['Conservative Analysis', 'Historical Data', 'Learning']
    },
    {
      id: 'when_use_agentic',
      type: 'tip',
      title: 'When to Use Agentic Mode',
      content: 'Choose Agentic Mode when: (1) You have DCF experience, (2) Analyzing growth companies with changing dynamics, (3) You want forward-looking insights, (4) Management guidance and market sentiment matter. Agentic Mode is best for comprehensive, nuanced analysis.',
      levels: ['intermediate', 'advanced'],
      priority: 'medium',
      relatedConcepts: ['Growth Companies', 'Forward-looking', 'AI Analysis']
    },
    {
      id: 'mode_recommendation',
      type: 'methodology',
      title: 'How Mode Recommendation Works',
      content: 'Our AI considers your experience level, company characteristics (size, sector, volatility), and analysis complexity to recommend the best mode. Large, stable companies often suit Simple Mode, while growth companies with dynamic markets benefit from Agentic Mode. The system explains its reasoning.',
      levels: ['intermediate', 'advanced'],
      priority: 'low',
      relatedConcepts: ['AI Recommendation', 'Company Characteristics', 'Analysis Complexity']
    }
  ],

  'growth_analysis': [
    {
      id: 'historical_cagr',
      type: 'methodology',
      title: 'Multi-Period CAGR Analysis',
      content: 'We analyze 3-year, 5-year, and 7-year Compound Annual Growth Rates (CAGR) to understand growth trends and consistency. Recent 3-year CAGR shows current momentum, 5-year CAGR captures a full business cycle, and 7-year CAGR reveals long-term trends. Consistency across periods indicates reliability.',
      levels: ['intermediate', 'advanced'],
      priority: 'high',
      relatedConcepts: ['CAGR', 'Growth Consistency', 'Business Cycles']
    },
    {
      id: 'growth_reliability',
      type: 'interpretation',
      title: 'Interpreting Growth Reliability Scores',
      content: 'High reliability (>70%) means consistent growth patterns - the company has delivered steady performance. Medium reliability (40-70%) suggests some volatility but identifiable trends. Low reliability (<40%) indicates erratic growth - use projections cautiously and consider wider sensitivity ranges.',
      levels: ['intermediate', 'advanced'],
      priority: 'medium',
      relatedConcepts: ['Reliability Scoring', 'Growth Volatility', 'Sensitivity Analysis']
    },
    {
      id: 'seasonality_adjustments',
      type: 'methodology',
      title: 'Seasonal and Cyclical Adjustments',
      content: 'Some businesses have seasonal patterns (retail peaks in Q4) or cyclical trends (auto sales with economic cycles). Our model detects these patterns and adjusts projections accordingly. Through-cycle analysis smooths temporary fluctuations to focus on underlying business trends.',
      levels: ['advanced'],
      priority: 'low',
      relatedConcepts: ['Seasonality', 'Business Cycles', 'Through-cycle Analysis']
    }
  ],

  'valuation_interpretation': [
    {
      id: 'upside_downside',
      type: 'interpretation',
      title: 'Understanding Upside/Downside Percentage',
      content: 'This shows the potential return if the stock reaches its intrinsic value. +25% upside means the stock could rise 25% to reach fair value. -15% downside suggests the stock is overvalued by 15%. Remember: this assumes our assumptions are correct and the market will eventually recognize the "true" value.',
      levels: ['beginner', 'intermediate', 'advanced'],
      priority: 'high',
      relatedConcepts: ['Market Efficiency', 'Fair Value', 'Investment Returns']
    },
    {
      id: 'enterprise_value',
      type: 'concept',
      title: 'Enterprise Value vs Equity Value',
      content: 'Enterprise Value (EV) represents the total company value - what you\'d pay to buy the entire business. Equity Value is EV minus debt plus cash - the value belonging to shareholders. Per-share price comes from Equity Value ÷ Shares Outstanding. EV includes the value that debt holders have a claim on.',
      levels: ['intermediate', 'advanced'],
      priority: 'medium',
      relatedConcepts: ['Debt', 'Cash', 'Shares Outstanding']
    },
    {
      id: 'terminal_value',
      type: 'concept',
      title: 'Terminal Value Significance',
      content: 'Terminal Value represents cash flows beyond year 10, assuming steady growth forever. It typically comprises 60-80% of total enterprise value, making terminal growth rate assumptions crucial. Small changes in terminal growth rate (e.g., 2.5% vs 3.5%) can dramatically impact the valuation.',
      levels: ['intermediate', 'advanced'],
      priority: 'high',
      relatedConcepts: ['Terminal Growth Rate', 'Perpetual Growth', 'Valuation Sensitivity']
    },
    {
      id: 'confidence_levels',
      type: 'interpretation',
      title: 'Interpreting Confidence Levels',
      content: 'High confidence means assumptions are well-supported by historical data and analysis. Medium confidence suggests reasonable assumptions with some uncertainty. Low confidence indicates limited data or high uncertainty - use results cautiously and consider wide sensitivity ranges.',
      levels: ['beginner', 'intermediate', 'advanced'],
      priority: 'medium',
      relatedConcepts: ['Data Quality', 'Uncertainty', 'Risk Assessment']
    }
  ],

  'common_pitfalls': [
    {
      id: 'growth_optimism',
      type: 'warning',
      title: 'Avoiding Growth Rate Optimism',
      content: 'The biggest DCF mistake is assuming high growth rates will continue indefinitely. Companies face increasing competition, market saturation, and size constraints. Our multi-stage model prevents this by gradually reducing growth rates and blending with GDP growth over time.',
      levels: ['beginner', 'intermediate', 'advanced'],
      priority: 'high',
      relatedConcepts: ['Growth Sustainability', 'Market Saturation', 'Reality Check']
    },
    {
      id: 'terminal_sensitivity',
      type: 'warning',
      title: 'Terminal Value Sensitivity Risk',
      content: 'Small changes in terminal growth assumptions create large valuation changes. A 0.5% difference in terminal growth rate can change valuation by 15-20%. Always test different terminal growth scenarios and understand this sensitivity when making investment decisions.',
      levels: ['intermediate', 'advanced'],
      priority: 'high',
      relatedConcepts: ['Sensitivity Analysis', 'Terminal Growth', 'Valuation Risk']
    },
    {
      id: 'false_precision',
      type: 'warning',
      title: 'False Precision Trap',
      content: 'DCF results seem precise (₹2,547.23 per share), but they\'re only as good as your assumptions. Think in ranges, not exact numbers. A valuation of ₹2,200-2,800 with clear assumptions is more honest than ₹2,547.23 with hidden uncertainty.',
      levels: ['intermediate', 'advanced'],
      priority: 'medium',
      relatedConcepts: ['Uncertainty', 'Valuation Ranges', 'Assumption Risk']
    },
    {
      id: 'market_timing',
      type: 'warning',
      title: 'DCF Doesn\'t Predict Market Timing',
      content: 'DCF tells you what a company might be worth, not when the market will recognize that value. Markets can stay "irrational" longer than you expect. Use DCF for long-term value assessment, not short-term trading decisions.',
      levels: ['beginner', 'intermediate', 'advanced'],
      priority: 'medium',
      relatedConcepts: ['Market Efficiency', 'Long-term Investing', 'Market Psychology']
    }
  ],

  'advanced_concepts': [
    {
      id: 'wacc_components',
      type: 'methodology',
      title: 'WACC (Weighted Average Cost of Capital)',
      content: 'WACC is the blended cost of equity and debt financing. Cost of equity reflects the return shareholders require (higher for riskier companies). Cost of debt is the interest rate on borrowings (tax-deductible, so we use after-tax cost). The weights reflect the company\'s capital structure (debt vs equity ratio).',
      levels: ['advanced'],
      priority: 'high',
      relatedConcepts: ['Cost of Equity', 'Cost of Debt', 'Capital Structure']
    },
    {
      id: 'free_cash_flow',
      type: 'concept',
      title: 'Free Cash Flow Calculation',
      content: 'Free Cash Flow = EBIT × (1 - Tax Rate) + Depreciation - Capital Expenditure - Change in Working Capital. This represents the cash available to all investors (debt and equity holders) after the company pays for operations and necessary investments to maintain/grow the business.',
      levels: ['intermediate', 'advanced'],
      priority: 'high',
      relatedConcepts: ['EBIT', 'CapEx', 'Working Capital']
    },
    {
      id: 'margin_analysis',
      type: 'methodology',
      title: 'Margin Expansion Analysis',
      content: 'Our model analyzes historical EBITDA margins to project future profitability. Improving margins suggest operational efficiency gains or pricing power. Declining margins indicate competitive pressure or cost inflation. We model margin trends and assess expansion potential based on industry dynamics.',
      levels: ['advanced'],
      priority: 'medium',
      relatedConcepts: ['EBITDA Margins', 'Operating Leverage', 'Competitive Dynamics']
    },
    {
      id: 'working_capital',
      type: 'concept',
      title: 'Working Capital Impact',
      content: 'Working Capital = Current Assets - Current Liabilities (excluding cash and debt). Growing companies typically need more working capital (inventory, receivables) which reduces free cash flow. Mature companies may optimize working capital, creating additional cash flow.',
      levels: ['advanced'],
      priority: 'low',
      relatedConcepts: ['Current Assets', 'Current Liabilities', 'Cash Conversion']
    }
  ]
};

// Educational content for specific DCF components
export const DCF_COMPONENT_EXPLANATIONS: Record<string, EducationalContentItem[]> = {
  'growth_waterfall': [
    {
      id: 'waterfall_concept',
      type: 'concept',
      title: 'Growth Waterfall Visualization',
      content: 'The waterfall chart shows how growth rates decline over time as competitive advantages fade and the company matures. Each bar represents a different growth stage, with colors indicating confidence levels. This visual helps you understand the growth trajectory assumptions underlying your valuation.',
      levels: ['beginner', 'intermediate', 'advanced'],
      priority: 'high',
      relatedConcepts: ['Competitive Fade', 'Growth Stages', 'Maturity Curve']
    },
    {
      id: 'stage_methodology',
      type: 'methodology',
      title: 'How Growth Stages Are Determined',
      content: 'Stage 1-2: Current momentum based on recent performance. Stage 3-5: Industry dynamics and competitive positioning. Stage 6-8: Market maturation effects. Stage 9-10: Economic constraints and GDP convergence. Each stage reflects different business and market realities.',
      levels: ['intermediate', 'advanced'],
      priority: 'medium',
      relatedConcepts: ['Business Lifecycle', 'Market Dynamics', 'Economic Constraints']
    }
  ],

  'projection_charts': [
    {
      id: 'cash_flow_chart',
      type: 'interpretation',
      title: 'Reading the Cash Flow Chart',
      content: 'This chart shows projected free cash flows over 10 years. Rising bars indicate growing cash generation, while declining bars suggest maturity. Smooth growth suggests stable business, while erratic patterns indicate cyclical or volatile operations. Focus on the overall trend and sustainability.',
      levels: ['beginner', 'intermediate'],
      priority: 'high',
      relatedConcepts: ['Free Cash Flow', 'Growth Sustainability', 'Business Stability']
    },
    {
      id: 'present_value_chart',
      type: 'interpretation',
      title: 'Understanding Present Value Trends',
      content: 'Present value shows what future cash flows are worth today after discounting. Early years have higher present values (less discounting), while distant years have lower present values. The declining trend is normal and reflects the time value of money principle.',
      levels: ['intermediate', 'advanced'],
      priority: 'medium',
      relatedConcepts: ['Time Value of Money', 'Discounting', 'Present Value']
    }
  ]
};

// Dynamic content generation based on analysis results
export const generateDynamicEducationalContent = (
  analysisData: any,
  userLevel: ExperienceLevel
): EducationalContentItem[] => {
  const dynamicContent: EducationalContentItem[] = [];

  // Generate content based on upside/downside
  if (analysisData?.upside_downside) {
    const upside = analysisData.upside_downside;
    const isUndervalued = upside > 0;
    
    dynamicContent.push({
      id: 'current_valuation_insight',
      type: 'interpretation',
      title: `This Stock Appears ${isUndervalued ? 'Undervalued' : 'Overvalued'}`,
      content: `Based on our DCF analysis, the stock shows ${Math.abs(upside).toFixed(1)}% ${isUndervalued ? 'upside potential' : 'downside risk'}. ${
        isUndervalued
          ? 'This suggests the market may not fully recognize the company\'s intrinsic value. However, remember that DCF is just one valuation method and markets can take time to reflect fair value.'
          : 'This suggests the current market price may be higher than the fundamental value. Consider whether there are factors not captured in the DCF that justify the premium, or if the market is being overly optimistic.'
      }`,
      levels: ['beginner', 'intermediate', 'advanced'],
      priority: 'high',
      relatedConcepts: ['Market Efficiency', 'Intrinsic Value', 'Investment Decision']
    });
  }

  // Generate content based on growth rates
  if (analysisData?.growth_stages) {
    const stages = analysisData.growth_stages;
    const nearTermGrowth = stages.find((s: any) => s.years === '1-2')?.growth_rate;
    const terminalGrowth = stages.find((s: any) => s.years === '9-10')?.growth_rate;
    
    if (nearTermGrowth && terminalGrowth) {
      dynamicContent.push({
        id: 'growth_trajectory_insight',
        type: 'interpretation',
        title: 'Growth Trajectory Analysis',
        content: `This company's growth trajectory shows ${nearTermGrowth.toFixed(1)}% in early years declining to ${terminalGrowth.toFixed(1)}% in later years. ${
          nearTermGrowth > 15
            ? 'The high initial growth suggests strong momentum but may not be sustainable long-term due to competitive pressures and market maturity.'
            : nearTermGrowth < 5
            ? 'The modest growth rates suggest a mature company with limited expansion opportunities but potentially stable cash flows.'
            : 'The moderate growth rates appear realistic and sustainable, suggesting a balanced growth profile.'
        }`,
        levels: ['intermediate', 'advanced'],
        priority: 'medium',
        relatedConcepts: ['Growth Sustainability', 'Competitive Dynamics', 'Business Maturity']
      });
    }
  }

  return dynamicContent;
};