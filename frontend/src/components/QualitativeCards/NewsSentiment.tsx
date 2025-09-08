import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Newspaper, TrendingUp, TrendingDown, Minus, Clock, ExternalLink, ChevronDown, ChevronRight, FileText, BarChart3, Building2 } from 'lucide-react';
import type { NewsSentiment, CompanyAnalysis } from '../../types';
import type { SummaryResponse } from '../../types/summary';
import NewsService, { type NewsAnalysis, type NewsArticle, type CompanyReport, type IndustryReport } from '../../services/newsService';

interface NewsSentimentProps {
  ticker: string;
  companyAnalysis: CompanyAnalysis | SummaryResponse;
  onSentimentInsightsUpdate?: (insights: any) => void;
}

type TabType = 'news' | 'company_reports' | 'industry_view';

interface NewsTheme {
  theme: string;
  description: string;
  sentiment: 'positive' | 'neutral' | 'negative';
  sources: Array<{
    title: string;
    url: string;
    type: 'news' | 'report' | 'filing' | 'analysis';
  }>;
  impact: 'high' | 'medium' | 'low';
}

interface NewsThemeCardProps {
  theme: NewsTheme;
  index: number;
}

const NewsThemeCard: React.FC<NewsThemeCardProps> = ({ theme, index }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const getSentimentColor = (sentiment: string) => {
    switch (sentiment) {
      case 'positive': return 'text-green-400 bg-green-900/20';
      case 'negative': return 'text-red-400 bg-red-900/20';
      default: return 'text-slate-400 bg-slate-700/20';
    }
  };

  const getImpactColor = (impact: string) => {
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

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.3, delay: 0.1 + index * 0.05 }}
      className="bg-slate-700/30 rounded-lg border border-slate-600/30 overflow-hidden"
    >
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full p-3 text-left hover:bg-slate-600/20 transition-colors"
      >
        <div className="flex items-start justify-between">
          <div className="flex items-start space-x-3 flex-1">
            <div className="w-1 h-1 bg-primary-400 rounded-full mt-2 flex-shrink-0" />
            <div className="flex-1">
              <p className="text-sm text-slate-300 leading-relaxed">{theme.description}</p>
              <div className="flex items-center space-x-2 mt-2">
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${getSentimentColor(theme.sentiment)}`}>
                  {theme.sentiment}
                </span>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${getImpactColor(theme.impact)}`}>
                  {theme.impact} impact
                </span>
                <span className="text-xs text-slate-400">
                  {theme.sources.length} source{theme.sources.length !== 1 ? 's' : ''}
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

      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="border-t border-slate-600/30"
          >
            <div className="p-3 space-y-3">
              <div>
                <h5 className="text-sm font-medium text-slate-200 mb-2">Sources & References</h5>
                <div className="space-y-2">
                  {theme.sources.map((source, sourceIndex) => (
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
    </motion.div>
  );
};

// Recent News Tab Component
const RecentNewsTab: React.FC<{
  articles: NewsArticle[];
  keyTopics: NewsAnalysis['key_topics'];
  fallbackHeadlines: string[];
  aiInsights: NewsAnalysis['ai_insights'] | null;
  loading: boolean;
}> = ({ articles, keyTopics, fallbackHeadlines, aiInsights, loading }) => {
  if (loading) {
    return (
      <div className="space-y-4">
        {[...Array(3)].map((_, i) => (
          <div key={i} className="animate-pulse">
            <div className="h-4 bg-slate-700 rounded w-3/4 mb-2"></div>
            <div className="h-3 bg-slate-800 rounded w-1/2"></div>
          </div>
        ))}
      </div>
    );
  }

  if (articles.length > 0) {
    return (
      <div>
        {/* AI Summary Section */}
        {aiInsights && (
          <div className="mb-6 p-4 bg-gradient-to-r from-blue-900/30 to-purple-900/30 border border-blue-500/30 rounded-lg">
            <div className="flex items-center space-x-2 mb-3">
              <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse"></div>
              <h4 className="text-sm font-semibold text-blue-300">📊 AI Market Sentiment Analysis</h4>
            </div>
            <p className="text-sm text-slate-200 mb-3 leading-relaxed">{aiInsights.summary}</p>
            <div className="space-y-2">
              <div>
                <span className="text-xs font-medium text-green-300">💡 Investment Implications:</span>
                <p className="text-xs text-slate-300 mt-1">{aiInsights.investment_implications}</p>
              </div>
              {aiInsights.key_themes.length > 0 && (
                <div className="flex items-center space-x-2">
                  <span className="text-xs font-medium text-amber-300">🎯 Key Themes:</span>
                  <div className="flex flex-wrap gap-1">
                    {aiInsights.key_themes.map((theme, idx) => (
                      <span key={idx} className="px-2 py-1 bg-amber-900/20 border border-amber-700/30 rounded-full text-xs text-amber-200">
                        {theme}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-medium text-slate-300">Recent Articles (Last 30 Days)</h3>
          <span className="text-xs text-slate-400">{articles.length} articles found</span>
        </div>
        
        <div className="space-y-3">
          {articles.slice(0, 10).map((article, index) => (
            <motion.a
              key={article.id}
              href={article.url}
              target="_blank"
              rel="noopener noreferrer"
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.2, delay: index * 0.05 }}
              className="block bg-slate-700/30 rounded-lg border border-slate-600/30 p-4 hover:bg-slate-600/40 hover:border-slate-500/50 transition-all duration-200 cursor-pointer group"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  {/* Headline/Title */}
                  <h5 className="text-sm font-semibold text-slate-200 group-hover:text-white line-clamp-2 mb-2">
                    {article.title}
                  </h5>
                  
                  {/* Summary/Subject */}
                  <p className="text-xs text-slate-400 mb-3 line-clamp-3">{article.summary}</p>
                  
                  {/* Source, Date, and Sentiment */}
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <span className="text-xs text-slate-500 font-medium">
                        📰 {article.source.name}
                      </span>
                      
                      <span className="text-xs text-slate-500">
                        📅 {new Date(article.published_date).toLocaleDateString('en-US', {
                          month: 'short',
                          day: 'numeric',
                          year: 'numeric'
                        })}
                      </span>
                      
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        article.sentiment === 'positive' ? 'text-green-400 bg-green-900/20 border border-green-700/30' :
                        article.sentiment === 'negative' ? 'text-red-400 bg-red-900/20 border border-red-700/30' :
                        'text-slate-400 bg-slate-700/20 border border-slate-600/30'
                      }`}>
                        {article.sentiment} ({(article.sentiment_score * 100).toFixed(0)}%)
                      </span>
                    </div>
                    
                    <div className="flex items-center space-x-2">
                      <ExternalLink className="h-4 w-4 text-slate-400 group-hover:text-slate-200 transition-colors" />
                    </div>
                  </div>
                </div>
              </div>
            </motion.a>
          ))}
        </div>
        
        {/* Key Topics Summary */}
        {keyTopics.length > 0 && (
          <div className="mt-6">
            <h4 className="text-sm font-medium text-slate-300 mb-3">Key Topics</h4>
            <div className="flex flex-wrap gap-2">
              {keyTopics.slice(0, 6).map((topic, index) => (
                <span
                  key={index}
                  className={`px-3 py-1 rounded-full text-xs font-medium border ${
                    topic.sentiment > 0.1 ? 'text-green-400 border-green-500/30 bg-green-900/20' :
                    topic.sentiment < -0.1 ? 'text-red-400 border-red-500/30 bg-red-900/20' :
                    'text-slate-400 border-slate-600/30 bg-slate-700/20'
                  }`}
                >
                  {topic.topic} ({topic.frequency})
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  }

  // Fallback to existing theme cards
  return (
    <div>
      <h3 className="text-sm font-medium text-slate-300 mb-3">Key Analysis Points</h3>
      <div className="space-y-2">
        {fallbackHeadlines.map((headline, index) => (
          <NewsThemeCard
            key={index}
            theme={{
              theme: `Analysis Point ${index + 1}`,
              description: headline,
              sentiment: 'neutral',
              sources: [
                { title: `Analysis Report`, url: `#`, type: 'analysis' }
              ],
              impact: index === 0 ? 'high' : index === 1 ? 'medium' : 'low'
            }}
            index={index}
          />
        ))}
      </div>
      
      <div className="mt-4 p-3 bg-yellow-900/20 border border-yellow-700/30 rounded-lg">
        <p className="text-xs text-yellow-200">
          ⚠️ <strong>Limited Data:</strong> Using fallback analysis. Enhanced news data loading failed.
        </p>
      </div>
    </div>
  );
};

// Company Reports Tab Component
const CompanyReportsTab: React.FC<{
  ticker: string;
  reports: CompanyReport[];
  loading: boolean;
}> = ({ ticker, reports, loading }) => {
  if (loading) {
    return (
      <div className="space-y-4">
        {[...Array(3)].map((_, i) => (
          <div key={i} className="animate-pulse">
            <div className="h-4 bg-slate-700 rounded w-3/4 mb-2"></div>
            <div className="h-3 bg-slate-800 rounded w-1/2"></div>
          </div>
        ))}
      </div>
    );
  }

  if (reports.length === 0) {
    return (
      <div className="text-center py-8">
        <FileText className="h-12 w-12 text-slate-500 mx-auto mb-4" />
        <h3 className="text-sm font-medium text-slate-300 mb-2">No Company Reports Found</h3>
        <p className="text-xs text-slate-400 mb-4">
          We're working to gather annual reports and earnings transcripts for {ticker}.
        </p>
        
        {/* Placeholder links */}
        <div className="space-y-2">
          <a
            href={`https://www.sec.gov/edgar/search/#/q=${ticker.replace('.NS', '')}`}
            target="_blank"
            rel="noopener noreferrer"
            className="block text-xs text-blue-400 hover:text-blue-300"
          >
            → Search SEC EDGAR Database
          </a>
          <a
            href={`https://www.bseindia.com/corporates/Comp_Resultsnew.aspx`}
            target="_blank"
            rel="noopener noreferrer"
            className="block text-xs text-blue-400 hover:text-blue-300"
          >
            → Browse BSE Company Results
          </a>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-medium text-slate-300">Company Reports & Filings</h3>
        <span className="text-xs text-slate-400">{reports.length} documents</span>
      </div>
      
      <div className="space-y-3">
        {reports.map((report, index) => (
          <motion.div
            key={report.id}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.2, delay: index * 0.05 }}
            className="bg-slate-700/30 rounded-lg border border-slate-600/30 p-4"
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <a
                  href={report.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm font-medium text-slate-200 hover:text-white mb-2 block"
                >
                  {report.title}
                </a>
                <p className="text-xs text-slate-400 mb-3">{report.summary}</p>
                
                <div className="flex items-center space-x-3 mb-2">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                    report.type === 'annual_report' ? 'text-blue-400 bg-blue-900/20' :
                    report.type === 'earnings_transcript' ? 'text-green-400 bg-green-900/20' :
                    'text-slate-400 bg-slate-700/20'
                  }`}>
                    {report.type.replace('_', ' ')}
                  </span>
                  
                  <span className="text-xs text-slate-500">
                    {new Date(report.published_date).toLocaleDateString()}
                  </span>
                  
                  {report.fiscal_year && (
                    <span className="text-xs text-slate-500">
                      FY {report.fiscal_year}
                    </span>
                  )}
                </div>
                
                {report.key_highlights.length > 0 && (
                  <div className="mt-3">
                    <h5 className="text-xs font-medium text-slate-300 mb-1">Key Highlights:</h5>
                    <ul className="text-xs text-slate-400 space-y-1">
                      {report.key_highlights.slice(0, 3).map((highlight, idx) => (
                        <li key={idx} className="flex items-start">
                          <span className="text-primary-400 mr-2">•</span>
                          {highlight}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
              
              <ExternalLink className="h-4 w-4 text-slate-400 hover:text-slate-200 ml-3 flex-shrink-0" />
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
};

// Industry View Tab Component
const IndustryViewTab: React.FC<{
  sector: string;
  reports: IndustryReport[];
  loading: boolean;
}> = ({ sector, reports, loading }) => {
  if (loading) {
    return (
      <div className="space-y-4">
        {[...Array(3)].map((_, i) => (
          <div key={i} className="animate-pulse">
            <div className="h-4 bg-slate-700 rounded w-3/4 mb-2"></div>
            <div className="h-3 bg-slate-800 rounded w-1/2"></div>
          </div>
        ))}
      </div>
    );
  }

  if (reports.length === 0) {
    return (
      <div className="text-center py-8">
        <BarChart3 className="h-12 w-12 text-slate-500 mx-auto mb-4" />
        <h3 className="text-sm font-medium text-slate-300 mb-2">No Industry Reports Found</h3>
        <p className="text-xs text-slate-400 mb-4">
          We're gathering industry analysis and market intelligence for the {sector} sector.
        </p>
        
        {/* Placeholder links based on sector */}
        <div className="space-y-2">
          <a
            href="https://www.mckinsey.com/industries"
            target="_blank"
            rel="noopener noreferrer"
            className="block text-xs text-blue-400 hover:text-blue-300"
          >
            → McKinsey Industry Insights
          </a>
          <a
            href="https://www.pwc.com/gx/en/industries.html"
            target="_blank"
            rel="noopener noreferrer"
            className="block text-xs text-blue-400 hover:text-blue-300"
          >
            → PwC Industry Reports
          </a>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-medium text-slate-300">{sector} Industry Intelligence</h3>
        <span className="text-xs text-slate-400">{reports.length} reports</span>
      </div>
      
      <div className="space-y-3">
        {reports.map((report, index) => (
          <motion.div
            key={report.id}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.2, delay: index * 0.05 }}
            className="bg-slate-700/30 rounded-lg border border-slate-600/30 p-4"
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <a
                  href={report.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm font-medium text-slate-200 hover:text-white mb-2 block"
                >
                  {report.title}
                </a>
                <p className="text-xs text-slate-400 mb-3">{report.summary}</p>
                
                <div className="flex items-center space-x-3 mb-2">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                    report.type === 'industry_analysis' ? 'text-purple-400 bg-purple-900/20' :
                    report.type === 'market_intelligence' ? 'text-orange-400 bg-orange-900/20' :
                    'text-slate-400 bg-slate-700/20'
                  }`}>
                    {report.type.replace('_', ' ')}
                  </span>
                  
                  <span className="text-xs text-slate-500">
                    {report.source.name}
                  </span>
                  
                  <span className="text-xs text-slate-500">
                    {new Date(report.published_date).toLocaleDateString()}
                  </span>
                </div>
                
                {report.key_insights.length > 0 && (
                  <div className="mt-3">
                    <h5 className="text-xs font-medium text-slate-300 mb-1">Key Insights:</h5>
                    <ul className="text-xs text-slate-400 space-y-1">
                      {report.key_insights.slice(0, 3).map((insight, idx) => (
                        <li key={idx} className="flex items-start">
                          <span className="text-primary-400 mr-2">•</span>
                          {insight}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
              
              <ExternalLink className="h-4 w-4 text-slate-400 hover:text-slate-200 ml-3 flex-shrink-0" />
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
};

export const NewsSentimentCard: React.FC<NewsSentimentProps> = ({ ticker, companyAnalysis, onSentimentInsightsUpdate }) => {
  const [activeTab, setActiveTab] = useState<TabType>('news');
  const [newsAnalysis, setNewsAnalysis] = useState<NewsAnalysis | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Type guard to check if we have V3 Summary data
  const isV3Summary = (data: any): data is SummaryResponse => {
    return data && 'analysis_mode' in data && 'fair_value_band' in data;
  };
  
  // Extract fallback sentiment data from existing analysis
  const fallbackSentiment: NewsSentiment = isV3Summary(companyAnalysis) ? {
    headlines: companyAnalysis.key_factors.slice(0, 3),
    sentiment_score: companyAnalysis.investment_label === 'Strongly Bullish' ? 0.8 :
                    companyAnalysis.investment_label === 'Cautiously Bullish' ? 0.4 :
                    companyAnalysis.investment_label === 'Cautiously Bearish' ? -0.4 :
                    companyAnalysis.investment_label === 'Strongly Bearish' ? -0.8 : 0,
    sentiment_label: companyAnalysis.investment_label,
    news_count: companyAnalysis.key_factors.length,
    last_updated: companyAnalysis.analysis_timestamp
  } : (companyAnalysis as CompanyAnalysis).news_sentiment;

  // Get company sector for industry analysis
  const companySector = isV3Summary(companyAnalysis) ? companyAnalysis.sector : companyAnalysis.company_info?.sector || 'Unknown';

  // Load enhanced news analysis
  useEffect(() => {
    const loadNewsAnalysis = async () => {
      if (!ticker) return;
      
      setLoading(true);
      setError(null);
      
      try {
        console.log(`📰 Loading enhanced news analysis for ${ticker}`);
        const analysis = await NewsService.getNewsAnalysis(ticker, 30);
        setNewsAnalysis(analysis);
        console.log(`✅ Loaded ${analysis.recent_articles.length} recent articles with overall sentiment: ${analysis.overall_sentiment.score}`);
        
        // Emit sentiment insights to parent component
        if (onSentimentInsightsUpdate && analysis.overall_sentiment) {
          onSentimentInsightsUpdate({
            summary: `Market sentiment: ${analysis.overall_sentiment.label} (${analysis.overall_sentiment.score}/5) based on ${analysis.recent_articles.length} recent articles`
          });
        }
      } catch (err: any) {
        console.error(`❌ Error loading news analysis for ${ticker}:`, err);
        setError(err.message || 'Failed to load news analysis');
        // Keep fallback data available
      } finally {
        setLoading(false);
      }
    };

    loadNewsAnalysis();
  }, [ticker]);

  // Use enhanced sentiment if available, otherwise fallback
  const sentiment = newsAnalysis?.overall_sentiment ? {
    headlines: newsAnalysis.recent_articles.slice(0, 3).map(article => article.title),
    sentiment_score: newsAnalysis.overall_sentiment.score,
    sentiment_label: newsAnalysis.overall_sentiment.label.replace('_', ' '),
    news_count: newsAnalysis.total_articles_analyzed,
    last_updated: newsAnalysis.analysis_date
  } : fallbackSentiment;
  const getSentimentColor = (score: number) => {
    if (score > 0.1) return 'text-green-400';
    if (score < -0.1) return 'text-red-400';
    return 'text-slate-400';
  };

  const getSentimentIcon = (score: number) => {
    if (score > 0.1) return TrendingUp;
    if (score < -0.1) return TrendingDown;
    return Minus;
  };

  const getSentimentBg = (score: number) => {
    if (score > 0.1) return 'bg-green-900/20 border-green-500/30';
    if (score < -0.1) return 'bg-red-900/20 border-red-500/30';
    return 'bg-slate-700/30 border-slate-600/30';
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const sentimentScore = sentiment.sentiment_score || 0;
  const SentimentIcon = getSentimentIcon(sentimentScore);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.2 }}
      className="card"
    >
      <div className="card-header">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Newspaper className="h-5 w-5 text-primary-400" />
            <h2 className="text-xl font-semibold text-slate-100">News & Sentiment Analysis</h2>
            {loading && (
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary-400"></div>
            )}
          </div>
          <div className={`flex items-center space-x-2 ${getSentimentColor(sentimentScore)}`}>
            <SentimentIcon className="h-4 w-4" />
            <span className="font-medium">{sentiment.sentiment_label || 'Neutral'}</span>
          </div>
        </div>
        <div className="flex items-center justify-between mt-2">
          <p className="text-sm text-slate-400">
            {newsAnalysis ? 
              `Analysis of ${newsAnalysis.total_articles_analyzed} articles from ${newsAnalysis.sources.length} sources` :
              `Fallback analysis based on ${sentiment.news_count || 0} key factors`
            }
          </p>
          {error && (
            <p className="text-xs text-red-400">⚠️ Using fallback data</p>
          )}
        </div>
        
        {/* Enhanced News Analysis Status */}
        <div className="mt-3 p-3 bg-gradient-to-r from-green-900/30 to-blue-900/30 border border-green-500/30 rounded-lg">
          <div className="flex items-center space-x-2">
            <div className="flex items-center space-x-1">
              <div className="w-2 h-2 bg-green-400 rounded-full"></div>
              <div className="w-2 h-2 bg-green-400 rounded-full"></div>
              <div className="w-2 h-2 bg-green-400 rounded-full"></div>
            </div>
            <span className="text-sm font-medium text-green-300">✅ Enhanced News Analysis - Active</span>
          </div>
          <div className="mt-2 text-xs text-green-200/80">
            <span className="text-green-400">✓ Live:</span> Real-time sentiment analysis • Market data integration • AI-powered insights •{' '}
            <span className="text-blue-400">📊 Features:</span> Multi-source news aggregation • Contextual analysis
          </div>
        </div>
        
        {/* Tab Navigation */}
        <div className="flex space-x-1 mt-4 bg-slate-800/50 rounded-lg p-1">
          <button
            onClick={() => setActiveTab('news')}
            className={`flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium transition-all ${
              activeTab === 'news'
                ? 'bg-primary-600 text-white shadow-lg'
                : 'text-slate-300 hover:text-white hover:bg-slate-700/50'
            }`}
          >
            <Newspaper className="h-4 w-4" />
            <span>Recent News</span>
            {newsAnalysis && (
              <span className="bg-slate-700 text-slate-300 px-1.5 py-0.5 rounded-full text-xs">
                {newsAnalysis.recent_articles.length}
              </span>
            )}
          </button>
          <button
            onClick={() => setActiveTab('company_reports')}
            className={`flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium transition-all ${
              activeTab === 'company_reports'
                ? 'bg-primary-600 text-white shadow-lg'
                : 'text-slate-300 hover:text-white hover:bg-slate-700/50'
            }`}
          >
            <FileText className="h-4 w-4" />
            <span>Company Reports</span>
            {newsAnalysis && (
              <span className="bg-slate-700 text-slate-300 px-1.5 py-0.5 rounded-full text-xs">
                {newsAnalysis.company_reports.length}
              </span>
            )}
          </button>
          <button
            onClick={() => setActiveTab('industry_view')}
            className={`flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium transition-all ${
              activeTab === 'industry_view'
                ? 'bg-primary-600 text-white shadow-lg'
                : 'text-slate-300 hover:text-white hover:bg-slate-700/50'
            }`}
          >
            <Building2 className="h-4 w-4" />
            <span>Industry View</span>
            {newsAnalysis && (
              <span className="bg-slate-700 text-slate-300 px-1.5 py-0.5 rounded-full text-xs">
                {newsAnalysis.industry_reports.length}
              </span>
            )}
          </button>
        </div>
      </div>
      <div className="card-body">

        {/* Tabbed Content */}
        <div className="mt-4">
          {/* Recent News Tab */}
          {activeTab === 'news' && (
            <RecentNewsTab
              articles={newsAnalysis?.recent_articles || []}
              keyTopics={newsAnalysis?.key_topics || []}
              fallbackHeadlines={sentiment.headlines || []}
              aiInsights={newsAnalysis?.ai_insights || null}
              loading={loading}
            />
          )}
          
          {/* Company Reports Tab */}
          {activeTab === 'company_reports' && (
            <CompanyReportsTab
              ticker={ticker}
              reports={newsAnalysis?.company_reports || []}
              loading={loading}
            />
          )}
          
          {/* Industry View Tab */}
          {activeTab === 'industry_view' && (
            <IndustryViewTab
              sector={companySector}
              reports={newsAnalysis?.industry_reports || []}
              loading={loading}
            />
          )}
        </div>
        
        {/* Data Attribution Footer */}
        <div className="mt-6 p-3 bg-blue-900/20 border border-blue-700/30 rounded-lg">
          <p className="text-xs text-blue-200">
            📊 <strong>Data Sources:</strong> {newsAnalysis ? 
              `Real-time analysis from ${newsAnalysis.sources.length} news sources and company filings` :
              'Analysis based on available company data and market indicators'
            }
          </p>
        </div>
      </div>
    </motion.div>
  );
};