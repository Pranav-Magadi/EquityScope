import React from 'react';
import { motion } from 'framer-motion';
import { Star, ThumbsUp, ThumbsDown, MessageSquare } from 'lucide-react';
import type { EmployeeSentiment, CompanyAnalysis } from '../../types';
import type { SummaryResponse } from '../../types/summary';

interface EmployeeVoiceProps {
  ticker: string;
  companyAnalysis: CompanyAnalysis | SummaryResponse;
}

export const EmployeeVoiceCard: React.FC<EmployeeVoiceProps> = ({ ticker, companyAnalysis }) => {
  // Type guard to check if we have V3 Summary data
  const isV3Summary = (data: any): data is SummaryResponse => {
    return data && 'analysis_mode' in data && 'fair_value_band' in data;
  };
  
  // Extract employee sentiment data based on format
  const sentiment: EmployeeSentiment = isV3Summary(companyAnalysis) ? {
    // For V3 Summary, create a placeholder since employee data is not available
    rating: 3.5, // Default neutral rating
    review_count: 0,
    pros: [companyAnalysis.business_fundamentals],
    cons: companyAnalysis.data_health_warnings,
    sentiment_summary: `Employee insights not available in ${companyAnalysis.analysis_mode} mode analysis`
  } : (companyAnalysis as CompanyAnalysis).employee_sentiment;
  const renderStars = (rating: number) => {
    const stars = [];
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 >= 0.5;

    for (let i = 1; i <= 5; i++) {
      if (i <= fullStars) {
        stars.push(
          <Star key={i} className="h-4 w-4 text-yellow-400 fill-current" />
        );
      } else if (i === fullStars + 1 && hasHalfStar) {
        stars.push(
          <div key={i} className="relative">
            <Star className="h-4 w-4 text-slate-600 fill-current" />
            <div className="absolute inset-0 overflow-hidden w-1/2">
              <Star className="h-4 w-4 text-yellow-400 fill-current" />
            </div>
          </div>
        );
      } else {
        stars.push(
          <Star key={i} className="h-4 w-4 text-slate-600 fill-current" />
        );
      }
    }

    return stars;
  };

  const getRatingColor = (rating: number) => {
    if (rating >= 4.0) return 'text-green-400';
    if (rating >= 3.5) return 'text-yellow-400';
    if (rating >= 3.0) return 'text-orange-400';
    return 'text-red-400';
  };

  const getRatingLabel = (rating: number) => {
    if (rating >= 4.0) return 'Excellent';
    if (rating >= 3.5) return 'Good';
    if (rating >= 3.0) return 'Average';
    return 'Needs Improvement';
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.4 }}
      className="card"
    >
      <div className="card-header">
        <div className="flex items-center space-x-2">
          <MessageSquare className="h-5 w-5 text-primary-400" />
          <h2 className="text-xl font-semibold text-slate-100">Employee Voice</h2>
        </div>
        <p className="text-sm text-slate-400 mt-1">
          Insights from {sentiment.review_count.toLocaleString()} employee reviews
        </p>
      </div>
      <div className="card-body">
        {/* Overall Rating */}
        <div className="bg-slate-700/30 rounded-lg p-4 mb-4 border border-slate-600/30">
          <div className="flex items-center justify-between mb-3">
            <div>
              <div className="text-sm text-slate-400 mb-1">Overall Rating</div>
              <div className={`text-2xl font-bold ${getRatingColor(sentiment.rating)}`}>
                {sentiment.rating.toFixed(1)}/5.0
              </div>
              <div className="text-sm text-slate-400">
                {getRatingLabel(sentiment.rating)}
              </div>
            </div>
            <div className="text-right">
              <div className="flex items-center space-x-1 mb-1">
                {renderStars(sentiment.rating)}
              </div>
              <div className="text-xs text-slate-400">
                {sentiment.review_count.toLocaleString()} reviews
              </div>
            </div>
          </div>
          
          {/* Sentiment Summary */}
          <div className="border-t border-slate-600 pt-3">
            <p className="text-sm text-slate-300">{sentiment.sentiment_summary}</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Pros */}
          <div>
            <div className="flex items-center space-x-2 mb-3">
              <ThumbsUp className="h-4 w-4 text-green-400" />
              <h3 className="font-medium text-slate-300">What Employees Like</h3>
            </div>
            <div className="space-y-2">
              {sentiment.pros.map((pro, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.3, delay: 0.1 + index * 0.05 }}
                  className="bg-green-900/10 border border-green-500/20 rounded-lg p-3"
                >
                  <div className="flex items-start space-x-2">
                    <div className="w-1 h-1 bg-green-400 rounded-full mt-2 flex-shrink-0" />
                    <p className="text-sm text-slate-300">{pro}</p>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>

          {/* Cons */}
          <div>
            <div className="flex items-center space-x-2 mb-3">
              <ThumbsDown className="h-4 w-4 text-red-400" />
              <h3 className="font-medium text-slate-300">Areas for Improvement</h3>
            </div>
            <div className="space-y-2">
              {sentiment.cons.map((con, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.3, delay: 0.2 + index * 0.05 }}
                  className="bg-red-900/10 border border-red-500/20 rounded-lg p-3"
                >
                  <div className="flex items-start space-x-2">
                    <div className="w-1 h-1 bg-red-400 rounded-full mt-2 flex-shrink-0" />
                    <p className="text-sm text-slate-300">{con}</p>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
};