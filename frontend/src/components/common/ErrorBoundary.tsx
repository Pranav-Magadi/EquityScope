import React, { Component, ErrorInfo, ReactNode } from 'react';
import { motion } from 'framer-motion';
import { 
  AlertTriangle, 
  RefreshCw, 
  Home, 
  MessageCircle, 
  ChevronDown,
  ChevronUp,
  Copy,
  CheckCircle
} from 'lucide-react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
  showDetails: boolean;
  copiedToClipboard: boolean;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      showDetails: false,
      copiedToClipboard: false
    };
  }

  static getDerivedStateFromError(error: Error): Partial<State> {
    return {
      hasError: true,
      error
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    this.setState({
      error,
      errorInfo
    });

    // Call custom error handler if provided
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }

    // Log error to console in development
    if (process.env.NODE_ENV === 'development') {
      console.error('ErrorBoundary caught an error:', error, errorInfo);
    }

    // In production, you would send this to an error tracking service
    // Example: Sentry.captureException(error, { contexts: { react: errorInfo } });
  }

  handleRetry = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
      showDetails: false,
      copiedToClipboard: false
    });
  };

  handleGoHome = () => {
    window.location.href = '/';
  };

  handleReportError = () => {
    const { error, errorInfo } = this.state;
    const errorReport = {
      error: error?.toString(),
      stack: error?.stack,
      componentStack: errorInfo?.componentStack,
      timestamp: new Date().toISOString(),
      userAgent: navigator.userAgent,
      url: window.location.href
    };

    // In a real application, this would send to your error reporting service
    console.log('Error Report:', errorReport);
    
    // For now, just show feedback
    alert('Error report prepared. In a production app, this would be sent to our support team.');
  };

  handleCopyError = async () => {
    const { error, errorInfo } = this.state;
    const errorText = `
Error: ${error?.message}
Stack: ${error?.stack}
Component Stack: ${errorInfo?.componentStack}
Timestamp: ${new Date().toISOString()}
URL: ${window.location.href}
    `.trim();

    try {
      await navigator.clipboard.writeText(errorText);
      this.setState({ copiedToClipboard: true });
      setTimeout(() => {
        this.setState({ copiedToClipboard: false });
      }, 2000);
    } catch (err) {
      console.error('Failed to copy error to clipboard:', err);
    }
  };

  render() {
    if (this.state.hasError) {
      // Use custom fallback if provided
      if (this.props.fallback) {
        return this.props.fallback;
      }

      const { error, errorInfo, showDetails, copiedToClipboard } = this.state;

      return (
        <div className="min-h-screen bg-slate-900 flex items-center justify-center p-4">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.3 }}
            className="bg-slate-800 rounded-2xl border border-slate-700 shadow-2xl max-w-2xl w-full"
          >
            {/* Header */}
            <div className="p-8 border-b border-slate-700">
              <div className="flex items-center space-x-4">
                <div className="w-12 h-12 bg-red-500/20 rounded-full flex items-center justify-center">
                  <AlertTriangle className="h-6 w-6 text-red-400" />
                </div>
                <div>
                  <h1 className="text-2xl font-bold text-slate-100">
                    Oops! Something went wrong
                  </h1>
                  <p className="text-slate-400 mt-1">
                    We encountered an unexpected error while processing your request
                  </p>
                </div>
              </div>
            </div>

            {/* Error Summary */}
            <div className="p-6 space-y-4">
              <div className="bg-red-900/20 border border-red-500/30 rounded-lg p-4">
                <div className="flex items-start space-x-3">
                  <AlertTriangle className="h-5 w-5 text-red-400 mt-0.5 flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <div className="font-medium text-red-300 mb-1">
                      {error?.name || 'Error'}
                    </div>
                    <div className="text-sm text-red-200 break-words">
                      {error?.message || 'An unexpected error occurred'}
                    </div>
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex flex-wrap gap-3">
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={this.handleRetry}
                  className="flex items-center space-x-2 bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-lg font-medium transition-colors"
                >
                  <RefreshCw className="h-4 w-4" />
                  <span>Try Again</span>
                </motion.button>

                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={this.handleGoHome}
                  className="flex items-center space-x-2 bg-slate-700 hover:bg-slate-600 text-slate-200 px-4 py-2 rounded-lg font-medium transition-colors"
                >
                  <Home className="h-4 w-4" />
                  <span>Go Home</span>
                </motion.button>

                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={this.handleReportError}
                  className="flex items-center space-x-2 bg-slate-700 hover:bg-slate-600 text-slate-200 px-4 py-2 rounded-lg font-medium transition-colors"
                >
                  <MessageCircle className="h-4 w-4" />
                  <span>Report Issue</span>
                </motion.button>
              </div>

              {/* Error Details Toggle */}
              <div className="border-t border-slate-700 pt-4">
                <button
                  onClick={() => this.setState({ showDetails: !showDetails })}
                  className="flex items-center space-x-2 text-slate-400 hover:text-slate-200 text-sm transition-colors"
                >
                  {showDetails ? (
                    <ChevronUp className="h-4 w-4" />
                  ) : (
                    <ChevronDown className="h-4 w-4" />
                  )}
                  <span>
                    {showDetails ? 'Hide' : 'Show'} Technical Details
                  </span>
                </button>

                {showDetails && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    transition={{ duration: 0.3 }}
                    className="mt-4 space-y-4"
                  >
                    {/* Copy Button */}
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-slate-300">
                        Error Details
                      </span>
                      <motion.button
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={this.handleCopyError}
                        className={`flex items-center space-x-1 text-xs px-3 py-1 rounded transition-colors ${
                          copiedToClipboard
                            ? 'bg-green-600 text-white'
                            : 'bg-slate-700 hover:bg-slate-600 text-slate-300'
                        }`}
                      >
                        {copiedToClipboard ? (
                          <>
                            <CheckCircle className="h-3 w-3" />
                            <span>Copied!</span>
                          </>
                        ) : (
                          <>
                            <Copy className="h-3 w-3" />
                            <span>Copy</span>
                          </>
                        )}
                      </motion.button>
                    </div>

                    {/* Error Stack */}
                    <div className="bg-slate-900 rounded-lg p-4 overflow-x-auto">
                      <pre className="text-xs text-slate-300 whitespace-pre-wrap">
                        <div className="text-red-400 font-medium mb-2">
                          Error Message:
                        </div>
                        <div className="mb-4">
                          {error?.message}
                        </div>

                        {error?.stack && (
                          <>
                            <div className="text-red-400 font-medium mb-2">
                              Stack Trace:
                            </div>
                            <div className="mb-4 text-slate-400">
                              {error.stack}
                            </div>
                          </>
                        )}

                        {errorInfo?.componentStack && (
                          <>
                            <div className="text-red-400 font-medium mb-2">
                              Component Stack:
                            </div>
                            <div className="text-slate-400">
                              {errorInfo.componentStack}
                            </div>
                          </>
                        )}
                      </pre>
                    </div>

                    {/* Additional Info */}
                    <div className="text-xs text-slate-500 space-y-1">
                      <div>Timestamp: {new Date().toISOString()}</div>
                      <div>URL: {window.location.href}</div>
                      <div>User Agent: {navigator.userAgent.substring(0, 100)}...</div>
                    </div>
                  </motion.div>
                )}
              </div>

              {/* Help Text */}
              <div className="bg-slate-700/50 rounded-lg p-4 text-sm text-slate-300">
                <div className="font-medium mb-2">What you can do:</div>
                <ul className="space-y-1 text-slate-400">
                  <li>• Try refreshing the page or clicking "Try Again"</li>
                  <li>• Check your internet connection</li>
                  <li>• Clear your browser cache and cookies</li>
                  <li>• If the problem persists, please report the issue</li>
                </ul>
              </div>
            </div>
          </motion.div>
        </div>
      );
    }

    return this.props.children;
  }
}

// Higher-order component for functional components
export const withErrorBoundary = <P extends object>(
  Component: React.ComponentType<P>,
  fallback?: ReactNode,
  onError?: (error: Error, errorInfo: ErrorInfo) => void
) => {
  return (props: P) => (
    <ErrorBoundary fallback={fallback} onError={onError}>
      <Component {...props} />
    </ErrorBoundary>
  );
};

// Specific error boundary for API errors
export const APIErrorBoundary: React.FC<{
  children: ReactNode;
  onRetry?: () => void;
}> = ({ children, onRetry }) => {
  return (
    <ErrorBoundary
      fallback={
        <div className="bg-red-900/20 border border-red-500/30 rounded-lg p-6 text-center">
          <AlertTriangle className="h-8 w-8 text-red-400 mx-auto mb-3" />
          <div className="font-medium text-red-300 mb-2">
            API Error
          </div>
          <div className="text-sm text-red-200 mb-4">
            Unable to fetch data from the server. Please check your connection and try again.
          </div>
          {onRetry && (
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={onRetry}
              className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg font-medium transition-colors"
            >
              Retry
            </motion.button>
          )}
        </div>
      }
    >
      {children}
    </ErrorBoundary>
  );
};

// Component error boundary for individual components
export const ComponentErrorBoundary: React.FC<{
  children: ReactNode;
  componentName?: string;
}> = ({ children, componentName = 'Component' }) => {
  return (
    <ErrorBoundary
      fallback={
        <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4 text-center">
          <AlertTriangle className="h-6 w-6 text-orange-400 mx-auto mb-2" />
          <div className="font-medium text-slate-200 mb-1">
            {componentName} Error
          </div>
          <div className="text-sm text-slate-400">
            This component encountered an error and couldn't be displayed.
          </div>
        </div>
      }
    >
      {children}
    </ErrorBoundary>
  );
};