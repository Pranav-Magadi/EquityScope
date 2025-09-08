"""
Pre-built Demo Analyses for Popular Companies
These are cached analysis results for immediate display in demo mode
"""

from datetime import datetime

DEMO_ANALYSES = {
    "TCS.NS": {
        "companyName": "Tata Consultancy Services Limited",
        "ticker": "TCS.NS", 
        "sector": "IT Services",
        "description": "India's largest IT services company with global presence",
        "analysis": {
            "executive_summary": {
                "investment_thesis": "Strong Buy - TCS is a market leader in IT services with consistent growth, strong margins, and excellent governance. The company benefits from digital transformation trends and has a diversified client base across geographies.",
                "key_highlights": [
                    "Market leader in IT services with 22% revenue growth CAGR over 5 years",
                    "Industry-leading EBITDA margins of 26-28%", 
                    "Strong balance sheet with minimal debt and high cash generation",
                    "Diversified revenue across banking, retail, manufacturing, and healthcare",
                    "Consistent dividend payments with 15-20% annual increases"
                ],
                "main_risks": [
                    "Currency headwinds from USD/INR fluctuations",
                    "Wage inflation in IT sector",
                    "Client concentration in BFSI segment",
                    "Competition from global IT services providers"
                ]
            },
            "financial_analysis": {
                "revenue_trends": {
                    "fy2023": 2348.64,
                    "fy2022": 1917.29,
                    "fy2021": 1562.15,
                    "fy2020": 1563.68,  
                    "fy2019": 1463.23,
                    "five_year_cagr": 12.5,
                    "analysis": "Consistent double-digit revenue growth driven by digital transformation demand"
                },
                "profitability": {
                    "ebitda_margin": 27.2,
                    "net_margin": 19.1,
                    "roe": 38.2,
                    "roic": 35.8,
                    "analysis": "Industry-leading margins with excellent capital efficiency"
                },
                "financial_health": {
                    "debt_to_equity": 0.02,
                    "current_ratio": 2.8,
                    "cash_ratio": 1.9,
                    "interest_coverage": 245.6,
                    "analysis": "Excellent financial health with minimal debt and strong liquidity"
                }
            },
            "dcf_valuation": {
                "assumptions": {
                    "revenue_growth_rate": 15.0,
                    "ebitda_margin": 27.0,  
                    "tax_rate": 25.0,
                    "wacc": 11.5,
                    "terminal_growth_rate": 3.0,
                    "projection_years": 10
                },
                "projections": {
                    "year_1_revenue": 2701.0,
                    "year_5_revenue": 4731.2,
                    "year_10_revenue": 9491.8,
                    "terminal_fcf": 2085.4
                },
                "valuation_results": {
                    "enterprise_value": 18567.8,
                    "equity_value": 19234.6,
                    "shares_outstanding": 37.25,
                    "fair_value_per_share": 4165,
                    "current_price": 3547,
                    "upside": 17.4,
                    "rating": "BUY"
                },
                "scenario_analysis": {
                    "conservative": {"fair_value": 3789, "upside": 6.8},
                    "base_case": {"fair_value": 4165, "upside": 17.4},
                    "optimistic": {"fair_value": 4634, "upside": 30.6}
                }
            },
            "ai_insights": {
                "bull_case": {
                    "agent": "Optimistic Analyst",
                    "thesis": "TCS is perfectly positioned for the next wave of digital transformation. Cloud migration, AI adoption, and automation will drive 20%+ revenue growth for the next 3-5 years.",
                    "key_points": [
                        "Leading position in cloud services and AI/ML capabilities",
                        "Strong client relationships enabling cross-selling opportunities",
                        "Expanding into high-growth areas like cybersecurity and IoT",
                        "Talent acquisition advantage in competitive IT market"
                    ],
                    "price_target": 4800,
                    "probability": 0.25
                },
                "bear_case": {
                    "agent": "Conservative Analyst", 
                    "thesis": "TCS faces headwinds from economic slowdown, wage inflation, and increasing competition. Growth will moderate to single digits with margin pressure.",
                    "key_points": [
                        "Economic uncertainty reducing IT spending budgets",
                        "Wage inflation eroding margin advantages", 
                        "Increased competition from boutique consulting firms",
                        "Client consolidation reducing pricing power"
                    ],
                    "price_target": 3200,
                    "probability": 0.25
                },
                "neutral_case": {
                    "agent": "Balanced Analyst",
                    "thesis": "TCS will continue steady growth at 12-15% with stable margins. A quality compounder for long-term investors seeking consistent returns.",
                    "key_points": [
                        "Balanced exposure across industries and geographies",
                        "Strong execution track record and management quality",
                        "Reasonable valuation at current levels",
                        "Sustainable competitive advantages in talent and process"
                    ],
                    "price_target": 4165,
                    "probability": 0.50
                }
            },
            "what_this_means": {
                "for_beginners": "TCS is India's largest IT company, like the Microsoft or Google of IT services. They help other companies with their technology needs. The company makes steady profits and pays regular dividends, making it a relatively safe investment for long-term wealth creation.",
                "valuation_explanation": "Our analysis suggests TCS is worth about ₹4,165 per share based on its future earnings potential. With the current price around ₹3,547, there's potential upside of 17%. This means for every ₹100 invested today, you might get ₹117 if the stock reaches fair value.",
                "risk_explanation": "The main risks are economic slowdowns (which reduce IT spending), currency changes (since TCS earns in dollars but reports in rupees), and competition. However, TCS has weathered many such cycles successfully.",
                "investment_suitability": "Suitable for conservative to moderate investors seeking steady growth with dividend income. Good for beginners due to transparent business model and consistent performance."
            }
        },
        "metadata": {
            "analysis_date": "2024-01-15T10:30:00Z",
            "model_version": "v2.0",
            "confidence_score": 0.85,
            "data_sources": ["NSE", "BSE", "Company Filings", "Industry Reports"],
            "user_level": "beginner"
        }
    },

    "RELIANCE.NS": {
        "companyName": "Reliance Industries Limited", 
        "ticker": "RELIANCE.NS",
        "sector": "Oil & Gas", 
        "description": "India's largest private sector company with interests in petrochemicals, oil & gas, telecom, and retail",
        "analysis": {
            "executive_summary": {
                "investment_thesis": "Hold - Reliance is undergoing a major transformation from energy to technology and retail. While traditional businesses face challenges, new ventures in telecom (Jio) and retail offer significant growth potential.",
                "key_highlights": [
                    "Successful digital transformation with Jio becoming #1 telecom player",
                    "Retail business scaling rapidly with omnichannel strategy",
                    "Strong cash generation from petrochemicals business",
                    "Strategic partnerships with global technology giants",
                    "Net debt reduction from ₹1.6L cr to nearly debt-free status"
                ],
                "main_risks": [
                    "Cyclical nature of petrochemicals and refining margins",
                    "Intense competition in telecom with price wars",
                    "Execution risk in new retail expansion",
                    "Regulatory changes in telecom and retail sectors"
                ]
            },
            "financial_analysis": {
                "revenue_trends": {
                    "fy2023": 869696,
                    "fy2022": 792756,
                    "fy2021": 540326,
                    "fy2020": 659205,
                    "fy2019": 659641,
                    "five_year_cagr": 7.2,
                    "analysis": "Revenue growth driven by new businesses offsetting mature O&G segment"
                },
                "profitability": {
                    "ebitda_margin": 17.8,
                    "net_margin": 8.9,
                    "roe": 9.2,
                    "roic": 7.8,
                    "analysis": "Margins under pressure due to new business investments and competitive telecom market"
                },
                "financial_health": {
                    "debt_to_equity": 0.23,
                    "current_ratio": 1.1,
                    "cash_ratio": 0.4,
                    "interest_coverage": 5.2,
                    "analysis": "Improved financial health after aggressive deleveraging, but still capital intensive"
                }
            },
            "dcf_valuation": {
                "assumptions": {
                    "revenue_growth_rate": 12.0,
                    "ebitda_margin": 18.5,
                    "tax_rate": 25.0,
                    "wacc": 9.8,
                    "terminal_growth_rate": 3.5,
                    "projection_years": 10
                },
                "projections": {
                    "year_1_revenue": 974459,
                    "year_5_revenue": 1532876,
                    "year_10_revenue": 2705234,
                    "terminal_fcf": 87456
                },
                "valuation_results": {
                    "enterprise_value": 1876543,
                    "equity_value": 1798765,
                    "shares_outstanding": 6.77,
                    "fair_value_per_share": 2657,
                    "current_price": 2489,
                    "upside": 6.7,
                    "rating": "HOLD"
                },
                "scenario_analysis": {
                    "conservative": {"fair_value": 2234, "upside": -10.2},
                    "base_case": {"fair_value": 2657, "upside": 6.7},
                    "optimistic": {"fair_value": 3156, "upside": 26.8}
                }
            },
            "ai_insights": {
                "bull_case": {
                    "agent": "Growth Specialist",
                    "thesis": "Reliance's digital and retail platforms are just hitting their stride. Jio's 5G rollout and retail expansion will drive significant value creation over the next decade.",
                    "key_points": [
                        "Jio Platform valued at $100B+ by global investors",
                        "Retail business achieving Amazon-like scale in India",
                        "Green energy investments positioning for future growth",
                        "Data monetization opportunities through digital ecosystem"
                    ],
                    "price_target": 3200,
                    "probability": 0.30
                },
                "bear_case": {
                    "agent": "Value Skeptic",
                    "thesis": "Reliance's transformation is expensive and uncertain. Traditional businesses are declining and new ventures face intense competition with unclear profitability.",
                    "key_points": [
                        "Telecom price wars destroying industry profitability",
                        "Retail business burning cash with thin margins",
                        "Petrochemicals facing structural headwinds",
                        "High capital intensity limiting free cash flow"
                    ],
                    "price_target": 2000,
                    "probability": 0.25
                },
                "neutral_case": {
                    "agent": "Sector Analyst",
                    "thesis": "Reliance offers diversified exposure to India's growth story. Stable cash flows from energy business fund new growth investments with moderate returns expected.",
                    "key_points": [
                        "Balanced portfolio across old and new economy sectors",
                        "Strong brand and distribution advantages in retail",
                        "Reasonable valuation considering growth options",
                        "Management track record of successful transformations"
                    ],
                    "price_target": 2657,
                    "probability": 0.45
                }
            },
            "what_this_means": {
                "for_beginners": "Reliance is like India's Amazon + Verizon + ExxonMobil combined. They make money from oil/chemicals, run Jio telecom network, and have retail stores. The company is changing from traditional oil business to technology and retail, which is risky but potentially rewarding.",
                "valuation_explanation": "Our analysis shows Reliance is roughly fairly valued at current prices around ₹2,500. There's modest upside potential to ₹2,657 (about 7% gain) if their new businesses succeed as planned.",
                "risk_explanation": "Main risks include the costly transformation from oil to digital/retail, intense competition in telecom and retail sectors, and cyclical oil/chemical markets. Success isn't guaranteed despite past achievements.",
                "investment_suitability": "Best for investors who understand complex business models and can tolerate volatility. Not ideal for beginners due to multiple moving parts and transformation risks."
            }
        },
        "metadata": {
            "analysis_date": "2024-01-15T11:15:00Z",
            "model_version": "v2.0",
            "confidence_score": 0.72,
            "data_sources": ["NSE", "BSE", "Company Filings", "Industry Reports"],
            "user_level": "intermediate"
        }
    },

    "HDFCBANK.NS": {
        "companyName": "HDFC Bank Limited",
        "ticker": "HDFCBANK.NS",
        "sector": "Banking",
        "description": "India's largest private sector bank by assets and market capitalization",
        "analysis": {
            "executive_summary": {
                "investment_thesis": "Buy - HDFC Bank remains India's highest quality private bank with superior asset quality, consistent profitability, and strong competitive moats. Post-merger integration with HDFC Ltd creates the largest mortgage franchise.",
                "key_highlights": [
                    "Best-in-class asset quality with lowest NPAs in banking sector",
                    "Consistent ROA of 1.8-2.1% and ROE of 17-19%",
                    "Successful merger with HDFC Ltd creating mortgage leadership",
                    "Digital transformation driving cost efficiencies",
                    "Strong liability franchise with low-cost CASA deposits"
                ],
                "main_risks": [
                    "Economic slowdown increasing credit costs",
                    "Interest rate volatility affecting NIMs",
                    "Regulatory changes in banking sector",
                    "Integration challenges post-HDFC merger"
                ]
            },
            "financial_analysis": {
                "revenue_trends": {
                    "fy2023": 175044,
                    "fy2022": 147816,
                    "fy2021": 132993,
                    "fy2020": 129804,
                    "fy2019": 121406,
                    "five_year_cagr": 9.6,
                    "analysis": "Steady revenue growth with improved fee income and merger benefits"
                },
                "profitability": {
                    "nim": 4.2,
                    "roa": 1.95,
                    "roe": 18.1,
                    "cost_to_income": 41.2,
                    "analysis": "Industry-leading profitability metrics with operational efficiency"
                },
                "asset_quality": {
                    "gross_npa": 1.26,
                    "net_npa": 0.31,
                    "provision_coverage": 79.1,
                    "credit_cost": 0.41,
                    "analysis": "Excellent asset quality with strong provisioning buffer"  
                }
            },
            "dcf_valuation": {
                "model_type": "DDM",
                "assumptions": {
                    "roe": 18.5,
                    "growth_rate": 14.0,
                    "payout_ratio": 22.0,
                    "cost_of_equity": 12.0,
                    "terminal_growth_rate": 2.5,
                    "projection_years": 10
                },
                "projections": {
                    "year_1_book_value": 523,
                    "year_5_book_value": 1016,
                    "year_10_book_value": 2645,
                    "terminal_dividend": 145
                },
                "valuation_results": {
                    "fair_value_per_share": 1856,
                    "current_price": 1634,
                    "upside": 13.6,
                    "pb_multiple": 3.55,
                    "rating": "BUY"
                },
                "scenario_analysis": {
                    "conservative": {"fair_value": 1654, "upside": 1.2},
                    "base_case": {"fair_value": 1856, "upside": 13.6},
                    "optimistic": {"fair_value": 2134, "upside": 30.6}
                }
            },
            "ai_insights": {
                "bull_case": {
                    "agent": "Banking Specialist",
                    "thesis": "HDFC Bank's merger with HDFC Ltd creates an unassailable competitive position in Indian banking. Digital initiatives and cross-selling will drive superior growth.",
                    "key_points": [
                        "Largest home loan portfolio with deepest customer relationships",
                        "Technology investments creating operational leverage",
                        "Premium valuation justified by consistent outperformance",
                        "Demographic dividend benefiting consumer lending"
                    ],
                    "price_target": 2100,
                    "probability": 0.25
                },
                "bear_case": {
                    "agent": "Credit Analyst",
                    "thesis": "HDFC Bank's growth is slowing and valuation multiples are unsustainable. Credit normalization and competitive pressure will impact returns.",
                    "key_points": [
                        "Credit costs rising as economic cycle turns",
                        "Digital disruption challenging traditional banking",
                        "Merger integration risks and execution challenges",
                        "Premium valuations leave little room for disappointment"
                    ],
                    "price_target": 1450,
                    "probability": 0.20
                },
                "neutral_case": {
                    "agent": "Equity Strategist",
                    "thesis": "HDFC Bank remains a quality franchise but growth is moderating. Fair value reflects steady but not spectacular returns ahead.",
                    "key_points": [
                        "Market leadership position with strong moats",
                        "Consistent dividend growth track record",
                        "Reasonable valuations for quality banking franchise",
                        "Defensive characteristics during economic uncertainty"
                    ],
                    "price_target": 1856,
                    "probability": 0.55
                }
            },
            "what_this_means": {
                "for_beginners": "HDFC Bank is like the Apple of Indian banking - premium quality, trusted brand, and consistent performance. Banks make money by taking deposits and lending at higher rates. HDFC does this better than most others with very few bad loans.",
                "valuation_explanation": "Using a dividend discount model (suitable for banks), HDFC Bank appears worth about ₹1,856 per share vs current price of ₹1,634. This suggests 14% upside potential, making it a reasonable buy for long-term investors.",
                "risk_explanation": "Main risks include economic slowdown (leading to loan defaults), interest rate changes (affecting profitability), and increased competition from fintech companies. However, HDFC has managed these risks well historically.",
                "investment_suitability": "Excellent for conservative investors seeking steady dividend income and capital appreciation. Good entry point for beginners into banking sector due to proven track record and transparent business model."
            }
        },
        "metadata": {
            "analysis_date": "2024-01-15T12:00:00Z",
            "model_version": "v2.0-DDM",
            "confidence_score": 0.88,
            "data_sources": ["NSE", "BSE", "RBI Reports", "Company Filings"],
            "user_level": "advanced"
        }
    }
}