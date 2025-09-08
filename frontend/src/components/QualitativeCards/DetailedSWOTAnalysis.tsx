import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { TrendingUp, TrendingDown, Target, Shield, AlertTriangle, ExternalLink, Info, ChevronDown, ChevronRight } from 'lucide-react';
import type { SWOTAnalysis } from '../../types';

interface DetailedSWOTPoint {
  point: string;
  details: string;
  impact: 'high' | 'medium' | 'low';
  sources: Array<{
    title: string;
    url: string;
    type: 'news' | 'report' | 'filing' | 'analysis';
  }>;
  metrics?: Array<{
    label: string;
    value: string;
    trend?: 'up' | 'down' | 'stable';
  }>;
}

interface DetailedSWOTAnalysisProps {
  swot: SWOTAnalysis;
  companyName: string;
  ticker: string;
}

// Enhanced SWOT data with details and sources
const getDetailedSWOTData = (swot: SWOTAnalysis, ticker: string): {
  strengths: DetailedSWOTPoint[];
  weaknesses: DetailedSWOTPoint[];
  opportunities: DetailedSWOTPoint[];
  threats: DetailedSWOTPoint[];
} => {
  // This would typically come from a backend API with real data
  // For demo purposes, we're creating realistic examples
  
  const isReliance = ticker.includes('RELIANCE');
  
  return {
    strengths: swot.strengths.map((strength, index) => ({
      point: typeof strength === 'string' ? strength : (strength as any)?.point || strength,
      details: isReliance ? [
        "Reliance operates Asia's largest oil refining complex with a capacity of 1.24 million barrels per day, providing significant scale advantages and cost efficiencies.",
        "The company has successfully diversified from oil & gas into retail and telecommunications, with Jio becoming India's largest telecom operator with 450M+ subscribers.",
        "Strong cash generation capabilities with consistent EBITDA margins above 15% and robust free cash flow generation supporting dividend payments and growth investments."
      ][index] || "Detailed analysis of this strength factor shows positive indicators for long-term competitive positioning and market leadership." : 
      `This strength represents a key competitive advantage for ${ticker.replace('.NS', '')}, providing sustainable differentiation in the market with measurable business impact.`,
      
      impact: index === 0 ? 'high' : index === 1 ? 'medium' : 'low',
      
      sources: isReliance ? [
        [
          { title: "Reliance Annual Report 2023-24", url: "https://www.ril.com/InvestorRelations/FinancialReporting.aspx", type: "filing" as const },
          { title: "Oil Refining Industry Analysis", url: "https://economictimes.indiatimes.com/industry/energy/oil-gas", type: "report" as const }
        ],
        [
          { title: "Jio Subscriber Growth Report", url: "https://www.moneycontrol.com/news/business/companies/reliance-jio", type: "news" as const },
          { title: "Indian Telecom Market Analysis", url: "https://www.business-standard.com/topic/telecom", type: "analysis" as const }
        ],
        [
          { title: "Reliance Financial Performance", url: "https://economictimes.indiatimes.com/reliance-industries-ltd/stocks/companyid-13556.cms", type: "analysis" as const },
          { title: "Q4 FY24 Results Analysis", url: "https://www.livemint.com/companies/news/reliance-industries", type: "filing" as const }
        ]
      ][index] || [
        { title: "Company Financial Analysis", url: "https://economictimes.indiatimes.com/markets/stocks", type: "analysis" as const }
      ] : [
        { title: `${ticker.replace('.NS', '')} Analysis`, url: `https://economictimes.indiatimes.com/markets/stocks/info?companyid=${ticker.replace('.NS', '')}`, type: "analysis" as const },
        { title: "Industry Report", url: "https://www.moneycontrol.com/news/business/companies", type: "report" as const }
      ],
      
      metrics: isReliance ? [
        [
          { label: "Refining Capacity", value: "1.24M bpd", trend: "stable" as const },
          { label: "Capacity Utilization", value: "95%", trend: "up" as const }
        ],
        [
          { label: "Jio Subscribers", value: "450M+", trend: "up" as const },
          { label: "Market Share", value: "35%", trend: "up" as const }
        ],
        [
          { label: "EBITDA Margin", value: "15.2%", trend: "stable" as const },
          { label: "Free Cash Flow", value: "₹85K Cr", trend: "up" as const }
        ]
      ][index] : [
        { label: "Market Position", value: "Strong", trend: "up" as const },
        { label: "Performance", value: "Above Avg", trend: "stable" as const }
      ]
    })),

    weaknesses: swot.weaknesses.map((weakness, index) => ({
      point: typeof weakness === 'string' ? weakness : (weakness as any)?.point || weakness,
      details: isReliance ? [
        "High dependency on volatile oil prices affects refining margins, with every $1/barrel change impacting EBITDA by approximately ₹1,500 crores annually.",
        "Limited innovation pipeline in traditional business segments compared to global peers, with R&D spending at 0.3% of revenue vs industry average of 1.2%."
      ][index] || "This weakness area requires management attention to prevent potential competitive disadvantages and operational challenges." :
      `This represents a challenge area for ${ticker.replace('.NS', '')} that could impact operational efficiency and competitive positioning if not addressed strategically.`,
      
      impact: index === 0 ? 'high' : 'medium',
      
      sources: [
        { title: "Oil Price Impact Analysis", url: "https://economictimes.indiatimes.com/markets/commodities/news", type: "analysis" },
        { title: "Quarterly Results Discussion", url: "https://www.moneycontrol.com/news/earnings", type: "report" }
      ],
      
      metrics: isReliance ? [
        [
          { label: "Oil Price Sensitivity", value: "₹1.5K Cr/$1", trend: "stable" as const },
          { label: "Refining Margin", value: "$8.2/bbl", trend: "down" as const }
        ],
        [
          { label: "R&D Spending", value: "0.3% of Rev", trend: "stable" as const },
          { label: "Innovation Index", value: "Below Avg", trend: "stable" as const }
        ]
      ][index] : [
        { label: "Risk Level", value: "Medium", trend: "stable" as const }
      ]
    })),

    opportunities: swot.opportunities.map((opportunity, index) => ({
      point: typeof opportunity === 'string' ? opportunity : (opportunity as any)?.point || opportunity,
      details: isReliance ? [
        "Green energy transition presents a $20B+ investment opportunity with plans for 100GW renewable capacity and green hydrogen production by 2030.",
        "Digital services expansion through AI, cloud, and fintech could add $10B+ in revenue with higher margin profile than traditional businesses.",
        "Strategic partnerships with global tech giants provide access to cutting-edge technologies and new market segments."
      ][index] || "This opportunity represents significant growth potential with measurable value creation possibilities." :
      `This opportunity could provide substantial growth potential for ${ticker.replace('.NS', '')}, with estimated value creation of multiple basis points in market positioning.`,
      
      impact: 'high',
      
      sources: isReliance ? [
        [
          { title: "Green Energy Investment Strategy", url: "https://www.livemint.com/industry/energy/renewable-energy-investments-india", type: "analysis" as const },
          { title: "India Renewable Energy Policy", url: "https://economictimes.indiatimes.com/industry/renewables", type: "report" as const }
        ],
        [
          { title: "Digital Services Market Growth", url: "https://www.business-standard.com/topic/digital-services", type: "report" as const },
          { title: "Fintech Industry Expansion", url: "https://economictimes.indiatimes.com/tech/startups/fintech", type: "news" as const }
        ],
        [
          { title: "Strategic Partnership News", url: "https://www.moneycontrol.com/news/business/companies/partnerships", type: "news" as const },
          { title: "Corporate Alliance Analysis", url: "https://www.business-standard.com/topic/strategic-partnerships", type: "analysis" as const }
        ]
      ][index] || [
        { title: "Market Opportunity Report", url: "https://economictimes.indiatimes.com/markets", type: "analysis" as const }
      ] : [
        { title: "Growth Opportunity Analysis", url: `https://www.moneycontrol.com/india/stockpricequote/${ticker.replace('.NS', '')}`, type: "analysis" as const }
      ],
      
      metrics: isReliance ? [
        [
          { label: "Investment Target", value: "$20B", trend: "up" as const },
          { label: "Renewable Capacity", value: "100GW by 2030", trend: "up" as const }
        ],
        [
          { label: "Digital Revenue", value: "$3B current", trend: "up" as const },
          { label: "Margin Potential", value: "25%+", trend: "up" as const }
        ],
        [
          { label: "Partnership Value", value: "$5B+", trend: "up" as const },
          { label: "Tech Access", value: "High", trend: "up" as const }
        ]
      ][index] : [
        { label: "Growth Potential", value: "High", trend: "up" as const }
      ]
    })),

    threats: swot.threats.map((threat, index) => ({
      point: typeof threat === 'string' ? threat : (threat as any)?.point || threat,
      details: isReliance ? [
        "Increasing regulatory pressure on traditional energy sectors with carbon pricing and emission norms potentially adding ₹5,000+ crores in compliance costs.",
        "Intense competition in telecom sector with price wars reducing ARPU and margin pressure across the industry.",
        "Economic downturns significantly impact consumer discretionary spending, affecting retail and telecom businesses."
      ][index] || "This threat requires proactive risk management and strategic planning to mitigate potential negative impacts." :
      `This represents a potential risk factor for ${ticker.replace('.NS', '')} that could impact business performance and requires ongoing monitoring and mitigation strategies.`,
      
      impact: index === 0 ? 'high' : 'medium',
      
      sources: isReliance ? [
        [
          { title: "Regulatory Impact on Energy Sector", url: "https://economictimes.indiatimes.com/industry/energy/oil-gas/regulatory-policy", type: "analysis" as const },
          { title: "Environmental Compliance Guidelines", url: "https://www.business-standard.com/topic/environmental-regulations", type: "report" as const }
        ],
        [
          { title: "Telecom Industry Competition Analysis", url: "https://www.livemint.com/industry/telecom", type: "report" as const },
          { title: "ARPU Trends in Indian Telecom", url: "https://economictimes.indiatimes.com/industry/telecom/telecom-news", type: "analysis" as const }
        ],
        [
          { title: "Economic Outlook and Consumer Impact", url: "https://www.moneycontrol.com/news/india/economy", type: "analysis" as const },
          { title: "Consumer Spending Pattern Analysis", url: "https://economictimes.indiatimes.com/news/economy/indicators", type: "report" as const }
        ]
      ][index] || [
        { title: "Industry Risk Analysis", url: "https://economictimes.indiatimes.com/markets/stocks/earnings", type: "analysis" as const }
      ] : [
        { title: "Market Risk Assessment", url: `https://www.moneycontrol.com/india/stockpricequote/${ticker.replace('.NS', '')}`, type: "analysis" as const }
      ],
      
      metrics: isReliance ? [
        [
          { label: "Compliance Cost", value: "₹5K+ Cr", trend: "up" as const },
          { label: "Carbon Price Risk", value: "High", trend: "up" as const }
        ],
        [
          { label: "ARPU Trend", value: "₹175", trend: "down" as const },
          { label: "Market Pressure", value: "High", trend: "stable" as const }
        ],
        [
          { label: "Economic Sensitivity", value: "Medium", trend: "stable" as const },
          { label: "Consumer Impact", value: "Moderate", trend: "stable" as const }
        ]
      ][index] : [
        { label: "Risk Level", value: "Medium", trend: "stable" as const }
      ]
    }))
  };
};

const DetailedSWOTAnalysisCard: React.FC<DetailedSWOTAnalysisProps> = ({ swot, companyName, ticker }) => {
  const [expandedItems, setExpandedItems] = useState<Set<string>>(new Set());
  const [activeCategory, setActiveCategory] = useState<'strengths' | 'weaknesses' | 'opportunities' | 'threats'>('strengths');

  const detailedData = getDetailedSWOTData(swot, ticker);

  const toggleExpanded = (id: string) => {
    const newExpanded = new Set(expandedItems);
    if (newExpanded.has(id)) {
      newExpanded.delete(id);
    } else {
      newExpanded.add(id);
    }
    setExpandedItems(newExpanded);
  };

  const getImpactColor = (impact: 'high' | 'medium' | 'low') => {
    switch (impact) {
      case 'high': return 'text-red-400 bg-red-900/20';
      case 'medium': return 'text-yellow-400 bg-yellow-900/20';
      case 'low': return 'text-green-400 bg-green-900/20';
    }
  };

  const getSourceIcon = (type: string) => {
    switch (type) {
      case 'news': return '📰';
      case 'report': return '📊';
      case 'filing': return '📋';
      case 'analysis': return '🔍';
      default: return '📄';
    }
  };

  const categories = [
    { key: 'strengths', label: 'Strengths', icon: TrendingUp, color: 'text-green-400', data: detailedData.strengths },
    { key: 'weaknesses', label: 'Weaknesses', icon: TrendingDown, color: 'text-red-400', data: detailedData.weaknesses },
    { key: 'opportunities', label: 'Opportunities', icon: Target, color: 'text-blue-400', data: detailedData.opportunities },
    { key: 'threats', label: 'Threats', icon: AlertTriangle, color: 'text-orange-400', data: detailedData.threats }
  ] as const;

  const activeData = categories.find(cat => cat.key === activeCategory);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-slate-800 rounded-lg border border-slate-700 overflow-hidden"
    >
      {/* Header */}
      <div className="p-6 border-b border-slate-700">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-purple-600 rounded-lg">
              <Shield className="h-5 w-5 text-white" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-white">Strategic SWOT Analysis</h3>
              <p className="text-sm text-slate-400">Double-click insights with detailed analysis & sources</p>
            </div>
          </div>
          <div className="text-xs text-slate-500">
            Interactive Analysis
          </div>
        </div>
      </div>

      {/* Category Tabs */}
      <div className="border-b border-slate-700">
        <div className="flex">
          {categories.map((category) => {
            const Icon = category.icon;
            return (
              <button
                key={category.key}
                onClick={() => setActiveCategory(category.key)}
                className={`flex-1 px-4 py-3 text-sm font-medium transition-colors relative ${
                  activeCategory === category.key
                    ? 'bg-slate-700 text-white'
                    : 'text-slate-400 hover:text-white hover:bg-slate-800/50'
                }`}
              >
                <div className="flex items-center justify-center space-x-2">
                  <Icon className={`h-4 w-4 ${activeCategory === category.key ? category.color : ''}`} />
                  <span>{category.label}</span>
                  <span className="px-1.5 py-0.5 bg-slate-600 rounded-full text-xs">
                    {category.data.length}
                  </span>
                </div>
                {activeCategory === category.key && (
                  <div className={`absolute bottom-0 left-0 right-0 h-0.5 ${category.color.replace('text-', 'bg-')}`} />
                )}
              </button>
            );
          })}
        </div>
      </div>

      {/* Content */}
      <div className="p-6">
        <AnimatePresence mode="wait">
          <motion.div
            key={activeCategory}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="space-y-4"
          >
            {activeData?.data.map((item, index) => {
              const itemId = `${activeCategory}-${index}`;
              const isExpanded = expandedItems.has(itemId);
              const Icon = activeData.icon;

              return (
                <div
                  key={itemId}
                  className="bg-slate-900/50 rounded-lg border border-slate-700 overflow-hidden"
                >
                  {/* Item Header */}
                  <button
                    onClick={() => toggleExpanded(itemId)}
                    className="w-full p-4 text-left hover:bg-slate-800/50 transition-colors"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex items-start space-x-3 flex-1">
                        <Icon className={`h-4 w-4 mt-1 ${activeData.color}`} />
                        <div className="flex-1">
                          <p className="text-sm text-white font-medium">{item.point}</p>
                          <div className="flex items-center space-x-2 mt-1">
                            <span className={`px-2 py-1 rounded-full text-xs font-medium ${getImpactColor(item.impact)}`}>
                              {item.impact} impact
                            </span>
                            <span className="text-xs text-slate-400">
                              {item.sources.length} source{item.sources.length !== 1 ? 's' : ''}
                            </span>
                          </div>
                        </div>
                      </div>
                      {isExpanded ? (
                        <ChevronDown className="h-4 w-4 text-slate-400 flex-shrink-0 mt-1" />
                      ) : (
                        <ChevronRight className="h-4 w-4 text-slate-400 flex-shrink-0 mt-1" />
                      )}
                    </div>
                  </button>

                  {/* Expanded Content */}
                  <AnimatePresence>
                    {isExpanded && (
                      <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: 'auto', opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        className="border-t border-slate-700"
                      >
                        <div className="p-4 space-y-4">
                          {/* Detailed Analysis */}
                          <div>
                            <h5 className="text-sm font-medium text-slate-200 mb-2 flex items-center space-x-2">
                              <Info className="h-3 w-3" />
                              <span>Detailed Analysis</span>
                            </h5>
                            <p className="text-sm text-slate-300 leading-relaxed">{item.details}</p>
                          </div>

                          {/* Key Metrics */}
                          {item.metrics && item.metrics.length > 0 && (
                            <div>
                              <h5 className="text-sm font-medium text-slate-200 mb-2">Key Metrics</h5>
                              <div className="grid grid-cols-2 gap-3">
                                {item.metrics.map((metric, metricIndex) => (
                                  <div key={metricIndex} className="bg-slate-800 rounded p-3">
                                    <div className="flex items-center justify-between">
                                      <span className="text-xs text-slate-400">{metric.label}</span>
                                      {metric.trend && (
                                        <span className={`text-xs ${
                                          metric.trend === 'up' ? 'text-green-400' : 
                                          metric.trend === 'down' ? 'text-red-400' : 'text-slate-400'
                                        }`}>
                                          {metric.trend === 'up' ? '↗' : metric.trend === 'down' ? '↘' : '→'}
                                        </span>
                                      )}
                                    </div>
                                    <div className="text-sm font-medium text-white mt-1">{metric.value}</div>
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}

                          {/* Sources */}
                          <div>
                            <h5 className="text-sm font-medium text-slate-200 mb-2">Sources & References</h5>
                            <div className="space-y-2">
                              {item.sources.map((source, sourceIndex) => (
                                <a
                                  key={sourceIndex}
                                  href={source.url}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="flex items-center space-x-3 p-2 bg-slate-800 rounded hover:bg-slate-700 transition-colors group"
                                >
                                  <span className="text-sm">{getSourceIcon(source.type)}</span>
                                  <div className="flex-1">
                                    <p className="text-sm text-slate-200 group-hover:text-white">{source.title}</p>
                                    <p className="text-xs text-slate-400 capitalize">{source.type}</p>
                                  </div>
                                  <ExternalLink className="h-3 w-3 text-slate-400 group-hover:text-slate-200" />
                                </a>
                              ))}
                            </div>
                          </div>
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              );
            })}
          </motion.div>
        </AnimatePresence>
      </div>
    </motion.div>
  );
};

export { DetailedSWOTAnalysisCard };