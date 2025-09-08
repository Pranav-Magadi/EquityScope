import type { MultiStageDCFResponse, CompanyAnalysis } from '../types';

// Pre-built demo analyses for popular Indian stocks
export interface DemoAnalysis {
  ticker: string;
  companyName: string;
  sector: string;
  description: string;
  highlights: string[];
  dcfResponse: MultiStageDCFResponse;
  companyAnalysis: CompanyAnalysis;
  demoNarrative: {
    introduction: string;
    keyInsights: string[];
    learningObjectives: string[];
    modeExplanation: string;
    conclusionPoints: string[];
  };
}

export const DEMO_ANALYSES: Record<string, DemoAnalysis> = {
  'TCS.NS': {
    ticker: 'TCS.NS',
    companyName: 'Tata Consultancy Services',
    sector: 'Information Technology',
    description: 'India\'s largest IT services company with global presence and consistent growth track record.',
    highlights: [
      'Stable 10-15% revenue growth over multiple years',
      'Strong margin expansion from operational efficiency',
      'Diversified global client base reducing concentration risk',
      'Leadership in digital transformation services'
    ],
    dcfResponse: {
      valuation: {
        intrinsic_value_per_share: 3847.50,
        terminal_value: 850000000000,
        enterprise_value: 1200000000000,
        equity_value: 1180000000000,
        current_stock_price: 3245.80,
        upside_downside: 18.5,
        projections: [
          {
            year: 1,
            revenue: 2100000000000,
            ebitda: 546000000000,
            ebit: 525000000000,
            tax: 131250000000,
            nopat: 393750000000,
            capex: 42000000000,
            working_capital_change: 21000000000,
            free_cash_flow: 330750000000,
            present_value: 295312500000,
            revenue_growth_rate: 12.5,
            growth_stage: '1-2',
            growth_method: 'historical_cagr'
          },
          {
            year: 2,
            revenue: 2331000000000,
            ebitda: 606060000000,
            ebit: 582750000000,
            tax: 145687500000,
            nopat: 437062500000,
            capex: 46620000000,
            working_capital_change: 23310000000,
            free_cash_flow: 367132500000,
            present_value: 293098214285,
            revenue_growth_rate: 11.0,
            growth_stage: '1-2',
            growth_method: 'historical_cagr'
          },
          {
            year: 3,
            revenue: 2540340000000,
            ebitda: 660488400000,
            ebit: 635085000000,
            tax: 158771250000,
            nopat: 476313750000,
            capex: 50806800000,
            working_capital_change: 25403400000,
            free_cash_flow: 400103550000,
            present_value: 285377767857,
            revenue_growth_rate: 9.0,
            growth_stage: '3-5',
            growth_method: 'industry_fade'
          },
          {
            year: 4,
            revenue: 2717371000000,
            ebitda: 706516460000,
            ebit: 679391250000,
            tax: 169847812500,
            nopat: 509543437500,
            capex: 54347420000,
            working_capital_change: 27173710000,
            free_cash_flow: 428022307500,
            present_value: 275789006696,
            revenue_growth_rate: 7.0,
            growth_stage: '3-5',
            growth_method: 'industry_fade'
          },
          {
            year: 5,
            revenue: 2853566070000,
            ebitda: 741927178200,
            ebit: 713641568750,
            tax: 178410392187,
            nopat: 535231176563,
            capex: 57071321400,
            working_capital_change: 28535660700,
            free_cash_flow: 449624194463,
            present_value: 264201952901,
            revenue_growth_rate: 5.0,
            growth_stage: '3-5',
            growth_method: 'industry_fade'
          },
          {
            year: 6,
            revenue: 2967945433100,
            ebitda: 771666292610,
            ebit: 742203298438,
            tax: 185550824609,
            nopat: 556652473829,
            capex: 59358908662,
            working_capital_change: 29679454331,
            free_cash_flow: 467614110836,
            present_value: 251203348467,
            revenue_growth_rate: 4.0,
            growth_stage: '6-8',
            growth_method: 'competitive_convergence'
          },
          {
            year: 7,
            revenue: 3066663249984,
            ebitda: 797332444796,
            ebit: 766610430937,
            tax: 191652607734,
            nopat: 574957823203,
            capex: 61333264999,
            working_capital_change: 30666632499,
            free_cash_flow: 482957925705,
            present_value: 237293781718,
            revenue_growth_rate: 3.3,
            growth_stage: '6-8',
            growth_method: 'competitive_convergence'
          },
          {
            year: 8,
            revenue: 3157844567484,
            ebitda: 821038387545,
            ebit: 789528972266,
            tax: 197382243066,
            nopat: 592146729200,
            capex: 63156891349,
            working_capital_change: 31578445674,
            free_cash_flow: 497411392177,
            present_value: 222712615633,
            revenue_growth_rate: 3.0,
            growth_stage: '6-8',
            growth_method: 'competitive_convergence'
          },
          {
            year: 9,
            revenue: 3252580104928,
            ebitda: 845671127281,
            ebit: 813294022734,
            tax: 203323505683,
            nopat: 609970517051,
            capex: 65051602098,
            working_capital_change: 32525801049,
            free_cash_flow: 512393113904,
            present_value: 208013380892,
            revenue_growth_rate: 3.0,
            growth_stage: '9-10',
            growth_method: 'gdp_convergence'
          },
          {
            year: 10,
            revenue: 3350157508076,
            ebitda: 871040935098,
            ebit: 837533242616,
            tax: 209383310654,
            nopat: 628149931962,
            capex: 67003150161,
            working_capital_change: 33501575080,
            free_cash_flow: 527645206721,
            present_value: 194012598084,
            revenue_growth_rate: 3.0,
            growth_stage: '9-10',
            growth_method: 'gdp_convergence'
          }
        ],
        assumptions: {
          revenue_growth_rate: 8.2, // Average across stages
          ebitda_margin: 26.0,
          tax_rate: 25.0,
          wacc: 12.0,
          terminal_growth_rate: 3.0,
          projection_years: 10
        },
        multi_stage_assumptions: {
          mode: 'simple',
          projection_years: 10,
          growth_stages: [
            {
              years: '1-2',
              start_year: 1,
              end_year: 2,
              growth_rate: 11.75,
              method: 'historical_cagr',
              gdp_weight: 0.2,
              confidence: 'high',
              rationale: 'Strong historical performance with 12-15% CAGR over past 5 years, blended with GDP for sustainability'
            },
            {
              years: '3-5', 
              start_year: 3,
              end_year: 5,
              growth_rate: 7.0,
              method: 'industry_fade',
              gdp_weight: 0.5,
              confidence: 'high',
              rationale: 'Industry competition and market maturation leading to growth normalization'
            },
            {
              years: '6-8',
              start_year: 6,
              end_year: 8,
              growth_rate: 3.4,
              method: 'competitive_convergence',
              gdp_weight: 0.75,
              confidence: 'medium',
              rationale: 'Mature market dynamics with increasing GDP weight as competitive advantages fade'
            },
            {
              years: '9-10',
              start_year: 9,
              end_year: 10,
              growth_rate: 3.0,
              method: 'gdp_convergence',
              gdp_weight: 1.0,
              confidence: 'high',
              rationale: 'Long-term convergence to sustainable GDP growth rate'
            }
          ],
          gdp_growth_rate: 3.0,
          wacc: 12.0,
          terminal_growth_rate: 3.0,
          tax_rate: 25.0,
          ebitda_margin: 26.0
        },
        growth_waterfall: {
          '1-2': 11.75,
          '3-5': 7.0,
          '6-8': 3.4,
          '9-10': 3.0,
          'terminal': 3.0
        }
      },
      mode: 'simple',
      growth_stages_summary: [
        {
          years: '1-2',
          growth_rate: '11.75%',
          method: 'Historical CAGR',
          confidence: 'High',
          rationale: 'Strong historical performance with 12-15% CAGR over past 5 years'
        },
        {
          years: '3-5',
          growth_rate: '7.0%', 
          method: 'Industry Fade',
          confidence: 'High',
          rationale: 'Industry competition and market maturation'
        },
        {
          years: '6-8',
          growth_rate: '3.4%',
          method: 'Competitive Convergence',
          confidence: 'Medium',
          rationale: 'Mature market dynamics with GDP blending'
        },
        {
          years: '9-10',
          growth_rate: '3.0%',
          method: 'GDP Convergence',
          confidence: 'High',
          rationale: 'Long-term sustainable growth aligned with economy'
        }
      ],
      education_content: {
        mode_explanation: 'Simple Mode provides historically-grounded analysis using 5-year performance data with conservative GDP blending for long-term sustainability.',
        growth_methodology: 'Multi-stage approach recognizing that high growth cannot continue indefinitely. Early stages rely on historical data, later stages blend with GDP growth.',
        key_benefits: 'Transparent, rule-based calculations that are easy to understand and validate. Ideal for learning DCF fundamentals.',
        best_for: 'Conservative baseline analysis, educational purposes, and understanding core DCF concepts.'
      }
    },
    companyAnalysis: {
      company_info: {
        ticker: 'TCS.NS',
        name: 'Tata Consultancy Services Limited',
        sector: 'Information Technology',
        industry: 'IT Services & Consulting',
        market_cap: 1200000000000,
        current_price: 3245.80,
        currency: 'INR',
        exchange: 'NSE'
      },
      stock_price: {
        current_price: 3245.80,
        change: 45.30,
        change_percent: 1.42,
        volume: 2156789,
        market_cap: 1200000000000,
        pe_ratio: 25.4,
        pb_ratio: 8.9
      },
      swot: {
        strengths: [
          'Market leader in Indian IT services with 22% market share',
          'Strong brand recognition and client relationships across 50+ countries',
          'Consistent revenue growth and margin expansion over past decade',
          'Leadership in digital transformation and cloud services',
          'Strong balance sheet with minimal debt and high cash reserves'
        ],
        weaknesses: [
          'High dependency on US and European markets (70% of revenue)',
          'Exposure to visa and immigration policy changes',
          'Intense competition leading to pricing pressure',
          'Higher employee costs in key markets due to talent shortage'
        ],
        opportunities: [
          'Growing demand for digital transformation services post-COVID',
          'Expansion in emerging markets and new service offerings',
          'Acquisitions to strengthen capabilities in niche areas',
          'Increasing adoption of cloud and AI/ML services by enterprises'
        ],
        threats: [
          'Economic slowdown in key markets affecting IT spending',
          'Rapid technological changes requiring continuous upskilling',
          'Increased competition from global players and new entrants',
          'Potential changes in H-1B visa policies affecting operations'
        ]
      },
      news_sentiment: {
        headlines: [
          'TCS reports strong Q4 results with 12.8% revenue growth',
          'Company announces $1.2B share buyback program',
          'TCS wins major digital transformation deals in BFSI sector',
          'Leadership transition planned with new CEO appointment'
        ],
        sentiment_score: 0.72,
        sentiment_label: 'Positive',
        news_count: 24,
        last_updated: '2025-07-29T10:30:00Z'
      },
      market_landscape: {
        competitors: [
          { name: 'Infosys', market_cap: 680000000000, market_share: 15.2, growth_rate: 11.5 },
          { name: 'Wipro', market_cap: 320000000000, market_share: 8.7, growth_rate: 9.2 },
          { name: 'HCL Technologies', market_cap: 410000000000, market_share: 10.1, growth_rate: 10.8 }
        ],
        market_share: 22.3,
        industry_trends: [
          'Accelerated digital transformation post-pandemic',
          'Growing demand for cloud migration services',
          'Increased focus on cybersecurity solutions',
          'Expansion of AI and machine learning capabilities'
        ],
        market_position: 'Market Leader with strong competitive moat and diversified service portfolio'
      },
      employee_sentiment: {
        rating: 4.1,
        review_count: 45623,
        pros: [
          'Excellent learning and development opportunities',
          'Strong company culture and values alignment',
          'Good work-life balance policies',
          'Competitive compensation and benefits'
        ],
        cons: [
          'Limited growth opportunities in certain roles',
          'Bureaucratic processes in large organization',
          'Variable project allocation affecting career progression',
          'Intense work pressure during project deadlines'
        ],
        sentiment_summary: 'Generally positive employee sentiment with strong appreciation for learning opportunities and company culture, though some concerns about career progression and work pressure.'
      }
    },
    demoNarrative: {
      introduction: 'TCS represents the gold standard for analyzing mature, profitable IT services companies using our 10-year DCF model. This demo showcases how our Simple Mode provides conservative, historically-grounded valuations for established market leaders.',
      keyInsights: [
        'Strong historical growth (12-15% CAGR) justified near-term optimism in years 1-2',
        'Industry maturation captured through declining growth rates in multi-stage model',
        'GDP blending prevents unrealistic long-term growth assumptions',
        '18.5% upside suggests potential undervaluation at current levels'
      ],
      learningObjectives: [
        'Understand how historical performance translates to future projections',
        'See the impact of competitive fade over 10-year horizon',
        'Learn why GDP blending is crucial for realistic terminal values',
        'Appreciate the conservatism built into Simple Mode analysis'
      ],
      modeExplanation: 'Simple Mode is ideal for TCS because it\'s a mature, well-established company with predictable business patterns. The historical data provides a solid foundation for projections, and the conservative approach aligns with the company\'s stable market position.',
      conclusionPoints: [
        'TCS shows solid fundamentals justifying premium valuation',
        'Multi-stage approach reveals realistic growth trajectory over 10 years',
        'Conservative assumptions provide margin of safety for investors',
        'Strong competitive position supports near-term growth assumptions'
      ]
    }
  },

  'RELIANCE.NS': {
    ticker: 'RELIANCE.NS',
    companyName: 'Reliance Industries Limited',
    sector: 'Oil & Gas',
    description: 'India\'s largest private sector company with diversified operations in petrochemicals, oil & gas, telecommunications, and retail.',
    highlights: [
      'Successful transformation from oil refining to digital and retail',
      'Jio disrupted telecom industry with rapid subscriber growth',
      'Strong cash generation from traditional petrochemicals business',
      'Strategic investments from global tech giants validating digital strategy'
    ],
    dcfResponse: {
      valuation: {
        intrinsic_value_per_share: 2834.20,
        terminal_value: 12500000000000,
        enterprise_value: 18500000000000,
        equity_value: 17800000000000,
        current_stock_price: 2456.70,
        upside_downside: 15.4,
        projections: [
          {
            year: 1,
            revenue: 8500000000000,
            ebitda: 1530000000000,
            ebit: 1360000000000,
            tax: 340000000000,
            nopat: 1020000000000,
            capex: 850000000000,
            working_capital_change: 85000000000,
            free_cash_flow: 85000000000,
            present_value: 75892857142,
            revenue_growth_rate: 15.2,
            growth_stage: '1-2',
            growth_method: 'digital_transformation'
          },
          {
            year: 2,
            revenue: 9792000000000,
            ebitda: 1762560000000,
            ebit: 1566720000000,
            tax: 391680000000,
            nopat: 1175040000000,
            capex: 979200000000,
            working_capital_change: 97920000000,
            free_cash_flow: 97920000000,
            present_value: 78652173913,
            revenue_growth_rate: 15.2,
            growth_stage: '1-2',
            growth_method: 'digital_transformation'
          },
          {
            year: 3,
            revenue: 10624320000000,
            ebitda: 1912377600000,
            ebit: 1700211200000,
            tax: 425052800000,
            nopat: 1275158400000,
            capex: 1062432000000,
            working_capital_change: 106243200000,
            free_cash_flow: 106483200000,
            present_value: 76089745762,
            revenue_growth_rate: 8.5,
            growth_stage: '3-5',
            growth_method: 'business_maturation'
          },
          {
            year: 4,
            revenue: 11527387200000,
            ebitda: 2074929296000,
            ebit: 1844140416000,
            tax: 461035104000,
            nopat: 1383105312000,
            capex: 1152738720000,
            working_capital_change: 115273872000,
            free_cash_flow: 115592720000,
            present_value: 73509852145,
            revenue_growth_rate: 8.5,
            growth_stage: '3-5',
            growth_method: 'business_maturation'
          },
          {
            year: 5,
            revenue: 12507215072000,
            ebitda: 2251298729000,
            ebit: 2001154886000,
            tax: 500288721000,
            nopat: 1500866164000,
            capex: 1250721507000,
            working_capital_change: 125072150700,
            free_cash_flow: 125072506300,
            present_value: 70914660131,
            revenue_growth_rate: 8.5,
            growth_stage: '3-5',
            growth_method: 'business_maturation'
          },
          {
            year: 6,
            revenue: 13033030325120,
            ebitda: 2345945458520,
            ebit: 2085401447760,
            tax: 521350361940,
            nopat: 1564051085820,
            capex: 1303303032512,
            working_capital_change: 130330303251,
            free_cash_flow: 130417750057,
            present_value: 66237267568,
            revenue_growth_rate: 4.2,
            growth_stage: '6-8',
            growth_method: 'competitive_convergence'
          },
          {
            year: 7,
            revenue: 13580415619175,
            ebitda: 2444474811652,
            ebit: 2173008109946,
            tax: 543252027486,
            nopat: 1629756082460,
            capex: 1358041561917,
            working_capital_change: 135804156191,
            free_cash_flow: 135950364352,
            present_value: 63943847745,
            revenue_growth_rate: 4.2,
            growth_stage: '6-8',
            growth_method: 'competitive_convergence'
          },
          {
            year: 8,
            revenue: 14148553084776,
            ebitda: 2546739555259,
            ebit: 2260146414629,
            tax: 565036603657,
            nopat: 1695109810972,
            capex: 1414855308477,
            working_capital_change: 141485530847,
            free_cash_flow: 138738971648,
            present_value: 60427816949,
            revenue_growth_rate: 4.2,
            growth_stage: '6-8',
            growth_method: 'competitive_convergence'
          },
          {
            year: 9,
            revenue: 14573009677319,
            ebitda: 2623141742518,
            ebit: 2340581065064,
            tax: 585145266266,
            nopat: 1755435798798,
            capex: 1457300967732,
            working_capital_change: 145730096773,
            free_cash_flow: 152404734293,
            present_value: 56806671402,
            revenue_growth_rate: 3.0,
            growth_stage: '9-10',
            growth_method: 'gdp_convergence'
          },
          {
            year: 10,
            revenue: 15010199967659,
            ebitda: 2701835994579,
            ebit: 2430838395069,
            tax: 607709598767,
            nopat: 1823128796302,
            capex: 1501019996766,
            working_capital_change: 150101999676,
            free_cash_flow: 172006799860,
            present_value: 54757344365,
            revenue_growth_rate: 3.0,
            growth_stage: '9-10',
            growth_method: 'gdp_convergence'
          }
        ],
        assumptions: {
          revenue_growth_rate: 9.5,
          ebitda_margin: 18.0,
          tax_rate: 25.0,
          wacc: 11.5,
          terminal_growth_rate: 3.0,
          projection_years: 10
        },
        multi_stage_assumptions: {
          mode: 'agentic',
          projection_years: 10,
          growth_stages: [
            {
              years: '1-2',
              start_year: 1,
              end_year: 2,
              growth_rate: 15.2,
              method: 'digital_transformation',
              gdp_weight: 0.1,
              confidence: 'medium',
              rationale: 'Digital and retail business scaling rapidly with Jio subscriber monetization'
            }
          ],
          gdp_growth_rate: 3.0,
          wacc: 11.5,
          terminal_growth_rate: 3.0,
          tax_rate: 25.0,
          ebitda_margin: 18.0
        },
        growth_waterfall: {
          '1-2': 15.2,
          '3-5': 8.5,
          '6-8': 4.2,
          '9-10': 3.0,
          'terminal': 3.0
        }
      },
      mode: 'agentic',
      growth_stages_summary: [
        {
          years: '1-2',
          growth_rate: '15.2%',
          method: 'Digital Transformation',
          confidence: 'Medium',
          rationale: 'Jio and retail business scaling with strong subscriber growth'
        },
        {
          years: '3-5',
          growth_rate: '8.5%',
          method: 'Business Maturation',
          confidence: 'Medium',
          rationale: 'Digital businesses mature while traditional segments stabilize'
        },
        {
          years: '6-8',
          growth_rate: '4.2%',
          method: 'Competitive Convergence',
          confidence: 'Medium',
          rationale: 'Market maturation with increased competitive pressure'
        },
        {
          years: '9-10',
          growth_rate: '3.0%',
          method: 'GDP Convergence', 
          confidence: 'High',
          rationale: 'Long-term sustainable growth aligned with economy'
        }
      ],
      education_content: {
        mode_explanation: 'Agentic Mode captures the complexity of Reliance\'s transformation from oil & gas to digital conglomerate, incorporating management guidance and market sentiment.',
        growth_methodology: 'AI-enhanced analysis considers multiple business segments, transformation timeline, and forward-looking management statements about digital monetization.',
        key_benefits: 'Comprehensive analysis incorporating qualitative factors like management vision, strategic partnerships, and market disruption potential.',
        best_for: 'Complex, transforming companies where historical data may not capture future potential and management guidance provides valuable insights.'
      }
    },
    companyAnalysis: {
      // Simplified company analysis structure for demo
      company_info: {
        ticker: 'RELIANCE.NS',
        name: 'Reliance Industries Limited',
        sector: 'Oil & Gas',
        industry: 'Diversified Conglomerate',
        market_cap: 16500000000000,
        current_price: 2456.70,
        currency: 'INR',
        exchange: 'NSE'
      },
      stock_price: {
        current_price: 2456.70,
        change: -23.45,
        change_percent: -0.94,
        volume: 3456789,
        market_cap: 16500000000000,
        pe_ratio: 19.8,
        pb_ratio: 2.1
      },
      swot: {
        strengths: [
          'Largest private company in India with diversified revenue streams',
          'Successful digital transformation with Jio becoming market leader',
          'Strong balance sheet enabling large-scale investments',
          'Integrated business model from crude oil to consumer retail'
        ],
        weaknesses: [
          'High capital intensity requiring continuous large investments',
          'Exposure to oil price volatility affecting petrochemicals margins',
          'Regulatory challenges in telecom and retail sectors',
          'Complex conglomerate structure making valuation challenging'
        ],
        opportunities: [
          'Monetization of Jio\'s large subscriber base through digital services',
          'Expansion of retail footprint and e-commerce capabilities',
          'Green energy transition with renewable investments',
          'Potential IPOs of digital and retail subsidiaries unlocking value'
        ],
        threats: [
          'Global shift away from fossil fuels impacting traditional business',
          'Intense competition in telecom and retail from established players',
          'Economic slowdown affecting consumer spending and industrial demand',
          'Regulatory changes in digital services and data privacy'
        ]
      },
      news_sentiment: {
        headlines: [
          'Reliance announces ₹75,000 crore green energy investment plan',
          'Jio subscriber growth slows but ARPU shows improvement',
          'Retail business reports strong festive season performance',
          'Company explores strategic partnerships for new energy business'
        ],
        sentiment_score: 0.65,
        sentiment_label: 'Moderately Positive',
        news_count: 18,
        last_updated: '2025-07-29T09:15:00Z'
      },
      market_landscape: {
        competitors: [
          { name: 'Bharti Airtel', market_cap: 450000000000, market_share: 32.1, growth_rate: 8.5 },
          { name: 'Vodafone Idea', market_cap: 85000000000, market_share: 21.3, growth_rate: -2.1 },
          { name: 'Asian Paints', market_cap: 280000000000, market_share: 12.4, growth_rate: 15.2 }
        ],
        market_share: 38.7,
        industry_trends: [
          'Digital transformation accelerating across all sectors',
          '5G rollout creating new revenue opportunities',
          'Consolidation in retail sector favoring large players',
          'Sustainability focus driving renewable energy investments'
        ],
        market_position: 'Dominant player across multiple sectors with strong competitive advantages in scale and integration'
      },
      employee_sentiment: {
        rating: 3.9,
        review_count: 28456,
        pros: [
          'Exposure to diverse business verticals and learning opportunities',
          'Strong brand value and market leadership position',
          'Competitive compensation packages',
          'Innovation-focused culture in digital businesses'
        ],
        cons: [
          'Hierarchical structure limiting decision-making autonomy',
          'Work pressure during major project launches and deadlines',
          'Limited work-life balance in certain high-growth divisions',
          'Bureaucratic processes in large organization'
        ],
        sentiment_summary: 'Mixed employee sentiment reflecting the challenges of working in a large, rapidly transforming organization with high growth expectations but traditional corporate culture.'
      }
    },
    demoNarrative: {
      introduction: 'Reliance demonstrates the power of our Agentic Mode for analyzing complex, transforming companies. This analysis shows how AI-enhanced DCF captures the company\'s evolution from traditional oil & gas to digital conglomerate.',
      keyInsights: [
        'Digital transformation justifies higher near-term growth rates despite mature core business',
        'Agentic Mode incorporates management guidance about Jio monetization timeline',
        'Complex multi-business model requires sophisticated analysis beyond historical data',
        'Strategic partnerships and market disruption potential captured in forward-looking projections'
      ],
      learningObjectives: [
        'See how Agentic Mode handles business transformation scenarios',
        'Understand incorporation of management guidance and strategic vision',
        'Learn to analyze multi-segment conglomerates with diverse growth drivers',
        'Appreciate the value of AI-enhanced analysis for complex situations'
      ],
      modeExplanation: 'Agentic Mode is essential for Reliance because historical financial data doesn\'t capture the transformational potential of Jio and retail businesses. Management statements, strategic partnerships, and market disruption patterns provide crucial forward-looking insights.',
      conclusionPoints: [
        'Successful transformation story justifies premium to traditional energy peers',
        'Digital monetization potential provides significant upside optionality',
        'Multi-stage model captures both transformation phase and maturity convergence',
        'AI analysis essential for companies undergoing major strategic shifts'
      ]
    }
  },

  'HDFCBANK.NS': {
    ticker: 'HDFCBANK.NS',
    companyName: 'HDFC Bank Limited',
    sector: 'Banking & Financial Services',
    description: 'India\'s leading private sector bank with strong asset quality, digital leadership, and consistent profitability track record.',
    highlights: [
      'Best-in-class asset quality with lowest NPAs in industry',
      'Strong digital banking platform with 68M+ customers',
      'Consistent ROE of 17-20% over past decade',
      'Leadership in retail and corporate banking segments'
    ],
    dcfResponse: {
      valuation: {
        intrinsic_value_per_share: 1847.30,
        terminal_value: 4200000000000,
        enterprise_value: 5800000000000,
        equity_value: 5800000000000,
        current_stock_price: 1634.50,
        upside_downside: 13.0,
        projections: [
          {
            year: 1,
            revenue: 985000000000,
            ebitda: 0, // Banks don't use EBITDA
            ebit: 0,
            tax: 72000000000,
            nopat: 216000000000,
            capex: 15000000000,
            working_capital_change: 0,
            free_cash_flow: 201000000000,
            present_value: 179464285714,
            revenue_growth_rate: 18.5,
            growth_stage: '1-2',
            growth_method: 'credit_expansion'
          },
          {
            year: 2,
            revenue: 1167250000000,
            ebitda: 0,
            ebit: 0,
            tax: 85267500000,
            nopat: 255802500000,
            capex: 17767500000,
            working_capital_change: 0,
            free_cash_flow: 238035000000,
            present_value: 189673214285,
            revenue_growth_rate: 18.5,
            growth_stage: '1-2',
            growth_method: 'credit_expansion'
          },
          {
            year: 3,
            revenue: 1307320000000,
            ebitda: 0,
            ebit: 0,
            tax: 95531600000,
            nopat: 286594400000,
            capex: 19909800000,
            working_capital_change: 0,
            free_cash_flow: 266684600000,
            present_value: 189878481013,
            revenue_growth_rate: 12.0,
            growth_stage: '3-5',
            growth_method: 'normalized_lending'
          },
          {
            year: 4,
            revenue: 1464198400000,
            ebitda: 0,
            ebit: 0,
            tax: 107035824000,
            nopat: 321107472000,
            capex: 22303476000,
            working_capital_change: 0,
            free_cash_flow: 298803996000,
            present_value: 190034598290,
            revenue_growth_rate: 12.0,
            growth_stage: '3-5',
            growth_method: 'normalized_lending'
          },
          {
            year: 5,
            revenue: 1639902208000,
            ebitda: 0,
            ebit: 0,
            tax: 119920161600,
            nopat: 359680484800,
            capex: 24998533200,
            working_capital_change: 0,
            free_cash_flow: 334681951600,
            present_value: 190155398664,
            revenue_growth_rate: 12.0,
            growth_stage: '3-5',
            growth_method: 'normalized_lending'
          },
          {
            year: 6,
            revenue: 1746495951520,
            ebitda: 0,
            ebit: 0,
            tax: 127774334860,
            nopat: 383223306140,
            capex: 26617439272,
            working_capital_change: 0,
            free_cash_flow: 356605866868,
            present_value: 181121143771,
            revenue_growth_rate: 6.5,
            growth_stage: '6-8',
            growth_method: 'mature_banking'
          },
          {
            year: 7,
            revenue: 1860018238209,
            ebitda: 0,
            ebit: 0,
            tax: 136101329749,
            nopat: 408304978996,
            capex: 28340277821,
            working_capital_change: 0,
            free_cash_flow: 379964701175,
            present_value: 178659086842,
            revenue_growth_rate: 6.5,
            growth_stage: '6-8',
            growth_method: 'mature_banking'
          },
          {
            year: 8,
            revenue: 1980919423693,
            ebitda: 0,
            ebit: 0,
            tax: 144967365670,
            nopat: 434804095579,
            capex: 30193405756,
            working_capital_change: 0,
            free_cash_flow: 404610689823,
            present_value: 176172877134,
            revenue_growth_rate: 6.5,
            growth_stage: '6-8',
            growth_method: 'mature_banking'
          },
          {
            year: 9,
            revenue: 2040547006404,
            ebitda: 0,
            ebit: 0,
            tax: 149440012468,
            nopat: 448320037403,
            capex: 31119205976,
            working_capital_change: 0,
            free_cash_flow: 417200831427,
            present_value: 169327121012,
            revenue_growth_rate: 3.0,
            growth_stage: '9-10',
            growth_method: 'gdp_convergence'
          },
          {
            year: 10,
            revenue: 2101763416596,
            ebitda: 0,
            ebit: 0,
            tax: 153929212838,
            nopat: 461717638515,
            capex: 32034779751,
            working_capital_change: 0,
            free_cash_flow: 429682858764,
            present_value: 162553645887,
            revenue_growth_rate: 3.0,
            growth_stage: '9-10',
            growth_method: 'gdp_convergence'
          }
        ],
        assumptions: {
          revenue_growth_rate: 12.5,
          ebitda_margin: 0, // Not applicable for banks
          tax_rate: 25.0,
          wacc: 12.0,
          terminal_growth_rate: 3.0,
          projection_years: 10
        },
        multi_stage_assumptions: {
          mode: 'simple',
          projection_years: 10,
          growth_stages: [
            {
              years: '1-2',
              start_year: 1,
              end_year: 2,
              growth_rate: 18.5,
              method: 'credit_expansion',
              gdp_weight: 0.2,
              confidence: 'high',
              rationale: 'Strong credit growth driven by economic recovery and market share gains'
            },
            {
              years: '3-5',
              start_year: 3,
              end_year: 5,
              growth_rate: 12.0,
              method: 'normalized_lending',
              gdp_weight: 0.5,
              confidence: 'high',
              rationale: 'Normalized credit growth aligned with economic expansion'
            },
            {
              years: '6-8',
              start_year: 6,
              end_year: 8,
              growth_rate: 6.5,
              method: 'mature_banking',
              gdp_weight: 0.75,
              confidence: 'medium',
              rationale: 'Mature banking market with GDP-aligned growth'
            },
            {
              years: '9-10',
              start_year: 9,
              end_year: 10,
              growth_rate: 3.0,
              method: 'gdp_convergence',
              gdp_weight: 1.0,
              confidence: 'high',
              rationale: 'Long-term convergence to sustainable GDP growth'
            }
          ],
          gdp_growth_rate: 3.0,
          wacc: 12.0,
          terminal_growth_rate: 3.0,
          tax_rate: 25.0,
          ebitda_margin: 0
        },
        growth_waterfall: {
          '1-2': 18.5,
          '3-5': 12.0,
          '6-8': 6.5,
          '9-10': 3.0,
          'terminal': 3.0
        }
      },
      mode: 'simple',
      growth_stages_summary: [
        {
          years: '1-2',
          growth_rate: '18.5%',
          method: 'Credit Expansion',
          confidence: 'High',
          rationale: 'Economic recovery driving strong credit demand'
        },
        {
          years: '3-5',
          growth_rate: '12.0%',
          method: 'Normalized Lending',
          confidence: 'High',
          rationale: 'Sustainable credit growth with economic expansion'
        },
        {
          years: '6-8',
          growth_rate: '6.5%',
          method: 'Mature Banking',
          confidence: 'Medium',
          rationale: 'Market maturation with GDP-aligned growth'
        },
        {
          years: '9-10',
          growth_rate: '3.0%',
          method: 'GDP Convergence',
          confidence: 'High',
          rationale: 'Long-term sustainable growth'
        }
      ],
      education_content: {
        mode_explanation: 'Simple Mode for banking analysis focuses on credit growth cycles, asset quality trends, and regulatory considerations using historical performance data.',
        growth_methodology: 'Banking DCF considers credit expansion phases, regulatory capital requirements, and sectoral lending patterns rather than traditional revenue growth.',
        key_benefits: 'Captures banking-specific metrics like loan growth, NIM expansion, and credit costs while maintaining conservative assumptions.',
        best_for: 'Financial services analysis where regulatory environment and credit cycles are more predictable than market disruption scenarios.'
      }
    },
    companyAnalysis: {
      company_info: {
        ticker: 'HDFCBANK.NS',
        name: 'HDFC Bank Limited',
        sector: 'Banking & Financial Services',
        industry: 'Private Sector Bank',
        market_cap: 8500000000000,
        current_price: 1634.50,
        currency: 'INR',
        exchange: 'NSE'
      },
      stock_price: {
        current_price: 1634.50,
        change: 12.85,
        change_percent: 0.79,
        volume: 1876543,
        market_cap: 8500000000000,
        pe_ratio: 18.7,
        pb_ratio: 2.8
      },
      swot: {
        strengths: [
          'Strongest asset quality among large banks with NPA <1%',
          'Market-leading digital banking platform and customer experience',
          'Consistent profitability with ROE of 17-20% over cycles',
          'Strong retail franchise with extensive branch and ATM network',
          'Excellent management track record and corporate governance'
        ],
        weaknesses: [
          'Premium valuation compared to peers limits upside potential',
          'Lower government securities portfolio reducing treasury income',
          'Exposure to unsecured lending segments with higher credit risk',
          'Intense competition in banking sector affecting margins'
        ],
        opportunities: [
          'Credit growth recovery post-COVID providing expansion opportunities',
          'Digital banking adoption creating cost efficiencies and new revenue',
          'Rural and semi-urban market penetration potential',
          'Cross-selling opportunities in insurance and wealth management'
        ],
        threats: [
          'Economic slowdown leading to higher credit costs and NPAs',
          'Interest rate volatility affecting net interest margins',
          'Regulatory changes impacting profitability and capital requirements',
          'Fintech disruption in payments and lending businesses'
        ]
      },
      news_sentiment: {
        headlines: [
          'HDFC Bank reports strong Q4 results with 23% loan growth',
          'Digital transactions cross 2.8 billion in latest quarter',
          'Bank maintains industry-leading asset quality metrics',
          'Management guides for 18-20% loan growth in FY25'
        ],
        sentiment_score: 0.78,
        sentiment_label: 'Positive',
        news_count: 31,
        last_updated: '2025-07-29T11:45:00Z'
      },
      market_landscape: {
        competitors: [
          { name: 'ICICI Bank', market_cap: 5600000000000, market_share: 12.8, growth_rate: 16.2 },
          { name: 'Axis Bank', market_cap: 2800000000000, market_share: 8.4, growth_rate: 14.5 },
          { name: 'Kotak Mahindra Bank', market_cap: 3200000000000, market_share: 6.2, growth_rate: 19.8 }
        ],
        market_share: 15.7,
        industry_trends: [
          'Digital banking transformation accelerating customer acquisition',
          'Credit growth recovery driven by corporate and retail demand',
          'Focus on asset quality and risk management post-COVID',
          'Regulatory emphasis on capital adequacy and provisioning'
        ],
        market_position: 'Market leader in private banking with premium positioning and superior operational metrics'
      },
      employee_sentiment: {
        rating: 4.3,
        review_count: 18765,
        pros: [
          'Strong brand reputation and market leadership position',
          'Excellent learning and development opportunities',
          'Competitive compensation and performance-based incentives',
          'Professional management and meritocratic culture'
        ],
        cons: [
          'High performance pressure and aggressive targets',
          'Limited work-life balance during busy periods',
          'Hierarchical structure limiting autonomy in junior roles',
          'Intense competition for leadership positions'
        ],
        sentiment_summary: 'Very positive employee sentiment reflecting strong organizational culture, learning opportunities, and market leadership, though work pressure remains a concern in sales roles.'
      }
    },
    demoNarrative: {
      introduction: 'HDFC Bank exemplifies the unique considerations required when analyzing financial services companies using DCF methodology. This demo showcases how banking-specific metrics and regulatory factors influence our 10-year valuation model.',
      keyInsights: [
        'Banking DCF focuses on loan growth and net interest margins rather than traditional revenue',
        'Asset quality and credit costs are critical factors in financial services valuation',
        'Regulatory capital requirements and RBI policies significantly impact growth assumptions',
        '13.0% upside reflects quality premium but also highlights sector-specific risks'
      ],
      learningObjectives: [
        'Understand banking-specific DCF modifications and considerations',
        'Learn how credit cycles influence growth stage assumptions',
        'Appreciate the role of asset quality in valuation sustainability',
        'See how regulatory environment affects long-term projections'
      ],
      modeExplanation: 'Simple Mode works well for HDFC Bank because it\'s a mature, well-regulated institution with predictable business patterns. The bank\'s consistent performance history provides reliable data for projections, while regulatory oversight adds stability to assumptions.',
      conclusionPoints: [
        'HDFC Bank represents quality banking at reasonable valuation',
        'Strong fundamentals support premium to sector average',
        'Asset quality leadership provides defensive characteristics',
        'Digital transformation offers additional growth optionality'
      ]
    }
  }
};

// Additional helper function for demo mode
export const getDemoAnalysis = (ticker: string): DemoAnalysis | null => {
  return DEMO_ANALYSES[ticker] || null;
};