import React from 'react';
import { motion } from 'framer-motion';
import { 
  TrendingUp,
  BarChart3,
  Calculator,
  Brain,
  Search,
  Zap,
  Target,
  PieChart
} from 'lucide-react';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  message?: string;
  submessage?: string;
  progress?: number;
  stage?: 'fetching' | 'analyzing' | 'calculating' | 'validating' | 'finalizing';
  showProgress?: boolean;
  className?: string;
}

const LoadingMessages = {
  fetching: {
    primary: "Gathering Financial Data",
    secondary: "Retrieving latest financial statements and market data...",
    icon: Search
  },
  analyzing: {
    primary: "AI Analysis in Progress",
    secondary: "Our AI agents are analyzing company fundamentals and market position...",
    icon: Brain
  },
  calculating: {
    primary: "Building DCF Model",
    secondary: "Calculating cash flows, discount rates, and terminal value...",
    icon: Calculator
  },
  validating: {
    primary: "Cross-Validating Results",
    secondary: "Ensuring accuracy with multiple valuation approaches...",
    icon: Target
  },
  finalizing: {
    primary: "Preparing Your Analysis",
    secondary: "Generating insights and educational content...",
    icon: TrendingUp
  }
};

const sizeClasses = {
  sm: 'w-4 h-4',
  md: 'w-6 h-6',
  lg: 'w-8 h-8',
  xl: 'w-12 h-12'
};

const containerSizeClasses = {
  sm: 'text-sm',
  md: 'text-base',
  lg: 'text-lg',
  xl: 'text-xl'
};

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  size = 'md',
  message,
  submessage,
  progress,
  stage = 'analyzing',
  showProgress = false,
  className = ''
}) => {
  const loadingInfo = LoadingMessages[stage];
  const IconComponent = loadingInfo.icon;
  
  const displayMessage = message || loadingInfo.primary;
  const displaySubmessage = submessage || loadingInfo.secondary;

  return (
    <div className={`flex flex-col items-center justify-center space-y-4 ${containerSizeClasses[size]} ${className}`}>
      {/* Animated Icon */}
      <motion.div
        className="relative"
        animate={{ rotate: 360 }}
        transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
      >
        <div className={`${sizeClasses[size]} relative`}>
          {/* Outer ring */}
          <motion.div
            className="absolute inset-0 border-2 border-primary-500/30 rounded-full"
            animate={{ rotate: -360 }}
            transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
          />
          {/* Spinning arc */}
          <motion.div
            className="absolute inset-0 border-2 border-transparent border-t-primary-500 rounded-full"
            animate={{ rotate: 360 }}
            transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
          />
          {/* Center icon */}
          <div className="absolute inset-0 flex items-center justify-center">
            <IconComponent className={`${sizeClasses[size === 'xl' ? 'md' : 'sm']} text-primary-400`} />
          </div>
        </div>
      </motion.div>

      {/* Main message */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="text-center space-y-2"
      >
        <div className="font-semibold text-slate-200">
          {displayMessage}
        </div>
        
        {displaySubmessage && (
          <div className="text-sm text-slate-400 max-w-md">
            {displaySubmessage}
          </div>
        )}
      </motion.div>

      {/* Progress bar */}
      {showProgress && typeof progress === 'number' && (
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="w-full max-w-xs"
        >
          <div className="flex items-center justify-between text-xs text-slate-400 mb-2">
            <span>Progress</span>
            <span>{Math.round(progress)}%</span>
          </div>
          <div className="w-full bg-slate-700 rounded-full h-2">
            <motion.div
              className="bg-gradient-to-r from-primary-500 to-primary-400 h-2 rounded-full"
              initial={{ width: 0 }}
              animate={{ width: `${progress}%` }}
              transition={{ duration: 0.5, ease: "easeOut" }}
            />
          </div>
        </motion.div>
      )}

      {/* Floating particles animation */}
      <div className="absolute inset-0 pointer-events-none">
        {[...Array(6)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-1 h-1 bg-primary-400/20 rounded-full"
            animate={{
              x: [0, Math.random() * 40 - 20, 0],
              y: [0, Math.random() * 40 - 20, 0],
              opacity: [0, 1, 0]
            }}
            transition={{
              duration: 3 + Math.random() * 2,
              repeat: Infinity,
              delay: i * 0.5,
              ease: "easeInOut"
            }}
            style={{
              left: `${20 + Math.random() * 60}%`,
              top: `${20 + Math.random() * 60}%`
            }}
          />
        ))}
      </div>
    </div>
  );
};

// Specialized loading component for different analysis stages
export const AnalysisLoadingSpinner: React.FC<{
  stage: 'fetching' | 'analyzing' | 'calculating' | 'validating' | 'finalizing';
  progress?: number;
  className?: string;
}> = ({ stage, progress, className }) => {
  return (
    <LoadingSpinner
      size="lg"
      stage={stage}
      progress={progress}
      showProgress={progress !== undefined}
      className={className}
    />
  );
};

// Compact inline loading spinner
export const InlineLoadingSpinner: React.FC<{
  message?: string;
  className?: string;
}> = ({ message = "Loading...", className }) => {
  return (
    <div className={`flex items-center space-x-2 ${className}`}>
      <motion.div
        className="w-4 h-4 border-2 border-primary-500/30 border-t-primary-500 rounded-full"
        animate={{ rotate: 360 }}
        transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
      />
      <span className="text-sm text-slate-400">{message}</span>
    </div>
  );
};

// Full-page loading overlay
export const LoadingOverlay: React.FC<{
  message?: string;
  submessage?: string;
  stage?: 'fetching' | 'analyzing' | 'calculating' | 'validating' | 'finalizing';
  progress?: number;
  showProgress?: boolean;
}> = ({ message, submessage, stage = 'analyzing', progress, showProgress }) => {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-slate-900/80 backdrop-blur-sm z-50 flex items-center justify-center"
    >
      <div className="bg-slate-800 rounded-xl border border-slate-700 p-8 max-w-md w-full mx-4 shadow-2xl">
        <LoadingSpinner
          size="xl"
          message={message}
          submessage={submessage}
          stage={stage}
          progress={progress}
          showProgress={showProgress}
        />
      </div>
    </motion.div>
  );
};

// Card loading skeleton
export const LoadingSkeleton: React.FC<{
  lines?: number;
  className?: string;
}> = ({ lines = 3, className }) => {
  return (
    <div className={`space-y-3 ${className}`}>
      {[...Array(lines)].map((_, i) => (
        <motion.div
          key={i}
          className="h-4 bg-slate-700/50 rounded"
          style={{ width: `${60 + Math.random() * 40}%` }}
          animate={{ opacity: [0.5, 1, 0.5] }}
          transition={{
            duration: 2,
            repeat: Infinity,
            delay: i * 0.2,
            ease: "easeInOut"
          }}
        />
      ))}
    </div>
  );
};

// Button loading state
export const LoadingButton: React.FC<{
  children: React.ReactNode;
  loading?: boolean;
  loadingText?: string;
  disabled?: boolean;
  onClick?: () => void;
  className?: string;
}> = ({ children, loading = false, loadingText = "Loading...", disabled, onClick, className }) => {
  return (
    <button
      onClick={onClick}
      disabled={disabled || loading}
      className={`relative flex items-center justify-center space-x-2 transition-all ${className} ${
        (disabled || loading) ? 'opacity-50 cursor-not-allowed' : ''
      }`}
    >
      {loading && (
        <motion.div
          className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full"
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
        />
      )}
      <span>{loading ? loadingText : children}</span>
    </button>
  );
};