import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Eye, EyeOff, Save, Key, CheckCircle, AlertCircle, Info } from 'lucide-react';

interface ApiKeyConfig {
  kite_api_key: string;
  kite_api_secret: string;
  kite_access_token?: string;
  claude_api_key?: string;
  perplexity_api_key?: string;
  openai_api_key?: string;
}

interface ApiKeySettingsProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (config: ApiKeyConfig) => void;
}

const ApiKeySettings: React.FC<ApiKeySettingsProps> = ({ isOpen, onClose, onSave }) => {
  const [config, setConfig] = useState<ApiKeyConfig>({
    kite_api_key: '',
    kite_api_secret: '',
    kite_access_token: '',
    claude_api_key: '',
    perplexity_api_key: '',
    openai_api_key: ''
  });

  const [showKeys, setShowKeys] = useState({
    kite_api_key: false,
    kite_api_secret: false,
    kite_access_token: false,
    claude_api_key: false,
    perplexity_api_key: false,
    openai_api_key: false
  });

  const [validationStatus, setValidationStatus] = useState<{
    [key: string]: 'idle' | 'validating' | 'valid' | 'invalid'
  }>({});

  const [isSaving, setIsSaving] = useState(false);

  // Load saved configuration from localStorage
  useEffect(() => {
    const savedConfig = localStorage.getItem('qualitative-edge-api-keys');
    if (savedConfig) {
      try {
        const parsedConfig = JSON.parse(savedConfig);
        setConfig(prevConfig => ({ ...prevConfig, ...parsedConfig }));
      } catch (error) {
        console.warn('Failed to load saved API key configuration');
      }
    }
  }, []);

  const handleInputChange = (field: keyof ApiKeyConfig, value: string | boolean) => {
    setConfig(prev => ({ ...prev, [field]: value }));
    
    // Reset validation status when user types
    if (typeof value === 'string' && value !== '') {
      setValidationStatus(prev => ({ ...prev, [field]: 'idle' }));
    }
  };

  const toggleKeyVisibility = (field: keyof typeof showKeys) => {
    setShowKeys(prev => ({ ...prev, [field]: !prev[field] }));
  };

  const validateApiKey = async (field: keyof ApiKeyConfig, value: string) => {
    if (!value.trim()) return;

    setValidationStatus(prev => ({ ...prev, [field]: 'validating' }));

    try {
      // Simulate API key validation
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Basic format validation
      let isValid = false;
      switch (field) {
        case 'kite_api_key':
          isValid = value.length >= 10; // Basic length check
          break;
        case 'kite_api_secret':
          isValid = value.length >= 20; // Basic length check
          break;
        case 'openai_api_key':
          isValid = value.startsWith('sk-'); // OpenAI format
          break;
        default:
          isValid = value.length > 0;
      }

      setValidationStatus(prev => ({ 
        ...prev, 
        [field]: isValid ? 'valid' : 'invalid' 
      }));
    } catch (error) {
      setValidationStatus(prev => ({ ...prev, [field]: 'invalid' }));
    }
  };

  const handleSave = async () => {
    setIsSaving(true);
    
    try {
      // Save to localStorage
      localStorage.setItem('qualitative-edge-api-keys', JSON.stringify(config));
      
      // Call parent save handler
      await onSave(config);
      
      // Show success and close
      setTimeout(() => {
        setIsSaving(false);
        onClose();
      }, 1000);
    } catch (error) {
      console.error('Failed to save API key configuration:', error);
      setIsSaving(false);
    }
  };

  const getValidationIcon = (field: keyof ApiKeyConfig) => {
    const status = validationStatus[field];
    switch (status) {
      case 'validating':
        return <div className="animate-spin h-4 w-4 border-2 border-blue-400 border-t-transparent rounded-full" />;
      case 'valid':
        return <CheckCircle className="h-4 w-4 text-green-400" />;
      case 'invalid':
        return <AlertCircle className="h-4 w-4 text-red-400" />;
      default:
        return null;
    }
  };

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
        onClick={(e) => e.target === e.currentTarget && onClose()}
      >
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 20 }}
          className="bg-slate-800 rounded-xl border border-slate-700 shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto"
        >
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-slate-700">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-primary-600 rounded-lg">
                <Key className="h-5 w-5 text-white" />
              </div>
              <div>
                <h2 className="text-xl font-semibold text-white">API Key Settings</h2>
                <p className="text-sm text-slate-400">Configure your API keys for enhanced features</p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-2 hover:bg-slate-700 rounded-lg transition-colors"
            >
              <svg className="h-5 w-5 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <div className="p-6 space-y-6">
            {/* AI Requirements Explanation */}
            <div className="bg-blue-900/20 border border-blue-700/30 rounded-lg p-4">
              <div className="flex items-start space-x-3">
                <Info className="h-5 w-5 text-blue-400 mt-0.5 flex-shrink-0" />
                <div className="flex-1">
                  <h3 className="text-sm font-medium text-blue-300 mb-2">🤖 AI Features Require API Keys</h3>
                  <p className="text-xs text-blue-200 mb-3">
                    Configure your own API keys to unlock sophisticated AI-powered analysis including:
                  </p>
                  <ul className="text-xs text-blue-200 space-y-1 mb-3 ml-4">
                    <li>• AI Investment Thesis & DCF Commentary</li>
                    <li>• Smart Risk Analysis & Catalysts</li>
                    <li>• Enhanced News Sentiment Analysis</li>
                    <li>• Industry & Macro Signal Detection</li>
                  </ul>
                  <div className="text-xs text-yellow-200 bg-yellow-900/20 border border-yellow-700/30 rounded p-2">
                    <strong>⚠️ Without API keys:</strong> Only quantitative analysis (ratios, multiples, basic DCF) will be available.
                  </div>
                </div>
              </div>
            </div>

            <div className="space-y-6">
              {/* Kite Connect API Keys */}
              <div className="space-y-4">
                <div className="flex items-center space-x-2">
                  <h3 className="text-lg font-medium text-white">Kite Connect API</h3>
                  <span className="px-2 py-1 bg-orange-600 text-white text-xs rounded-full">Real-time Data</span>
                </div>
                
                {/* Kite API Key */}
                <div className="space-y-2">
                  <label className="block text-sm font-medium text-slate-300">API Key</label>
                  <div className="relative">
                    <input
                      type={showKeys.kite_api_key ? 'text' : 'password'}
                      value={config.kite_api_key}
                      onChange={(e) => handleInputChange('kite_api_key', e.target.value)}
                      onBlur={(e) => validateApiKey('kite_api_key', e.target.value)}
                      placeholder="Enter your Kite Connect API Key"
                      className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent pr-20"
                    />
                    <div className="absolute inset-y-0 right-0 flex items-center space-x-1 pr-3">
                      {getValidationIcon('kite_api_key')}
                      <button
                        type="button"
                        onClick={() => toggleKeyVisibility('kite_api_key')}
                        className="p-1 hover:bg-slate-600 rounded transition-colors"
                      >
                        {showKeys.kite_api_key ? (
                          <EyeOff className="h-4 w-4 text-slate-400" />
                        ) : (
                          <Eye className="h-4 w-4 text-slate-400" />
                        )}
                      </button>
                    </div>
                  </div>
                </div>

                {/* Kite API Secret */}
                <div className="space-y-2">
                  <label className="block text-sm font-medium text-slate-300">API Secret</label>
                  <div className="relative">
                    <input
                      type={showKeys.kite_api_secret ? 'text' : 'password'}
                      value={config.kite_api_secret}
                      onChange={(e) => handleInputChange('kite_api_secret', e.target.value)}
                      onBlur={(e) => validateApiKey('kite_api_secret', e.target.value)}
                      placeholder="Enter your Kite Connect API Secret"
                      className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent pr-20"
                    />
                    <div className="absolute inset-y-0 right-0 flex items-center space-x-1 pr-3">
                      {getValidationIcon('kite_api_secret')}
                      <button
                        type="button"
                        onClick={() => toggleKeyVisibility('kite_api_secret')}
                        className="p-1 hover:bg-slate-600 rounded transition-colors"
                      >
                        {showKeys.kite_api_secret ? (
                          <EyeOff className="h-4 w-4 text-slate-400" />
                        ) : (
                          <Eye className="h-4 w-4 text-slate-400" />
                        )}
                      </button>
                    </div>
                  </div>
                </div>

                {/* Kite Access Token (Optional) */}
                <div className="space-y-2">
                  <label className="block text-sm font-medium text-slate-300">
                    Access Token <span className="text-slate-500">(Optional)</span>
                  </label>
                  <div className="relative">
                    <input
                      type={showKeys.kite_access_token ? 'text' : 'password'}
                      value={config.kite_access_token}
                      onChange={(e) => handleInputChange('kite_access_token', e.target.value)}
                      placeholder="Auto-generated after authentication"
                      className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent pr-12"
                    />
                    <div className="absolute inset-y-0 right-0 flex items-center pr-3">
                      <button
                        type="button"
                        onClick={() => toggleKeyVisibility('kite_access_token')}
                        className="p-1 hover:bg-slate-600 rounded transition-colors"
                      >
                        {showKeys.kite_access_token ? (
                          <EyeOff className="h-4 w-4 text-slate-400" />
                        ) : (
                          <Eye className="h-4 w-4 text-slate-400" />
                        )}
                      </button>
                    </div>
                  </div>
                  <p className="text-xs text-slate-500">
                    Will be auto-generated during the authentication flow
                  </p>
                </div>
              </div>

              {/* Claude API Key */}
              <div className="space-y-4">
                <div className="flex items-center space-x-2">
                  <h3 className="text-lg font-medium text-white">Claude API</h3>
                  <span className="px-2 py-1 bg-blue-600 text-white text-xs rounded-full">AI Analysis</span>
                  <span className="px-2 py-1 bg-green-600 text-white text-xs rounded-full">Required</span>
                </div>
                
                <div className="space-y-2">
                  <label className="block text-sm font-medium text-slate-300">API Key</label>
                  <div className="relative">
                    <input
                      type={showKeys.claude_api_key ? 'text' : 'password'}
                      value={config.claude_api_key}
                      onChange={(e) => handleInputChange('claude_api_key', e.target.value)}
                      onBlur={(e) => validateApiKey('claude_api_key', e.target.value)}
                      placeholder="sk-ant-... (for AI agentic workflow)"
                      className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent pr-20"
                    />
                    <div className="absolute inset-y-0 right-0 flex items-center space-x-1 pr-3">
                      {getValidationIcon('claude_api_key')}
                      <button
                        type="button"
                        onClick={() => toggleKeyVisibility('claude_api_key')}
                        className="p-1 hover:bg-slate-600 rounded transition-colors"
                      >
                        {showKeys.claude_api_key ? (
                          <EyeOff className="h-4 w-4 text-slate-400" />
                        ) : (
                          <Eye className="h-4 w-4 text-slate-400" />
                        )}
                      </button>
                    </div>
                  </div>
                  <p className="text-xs text-slate-500">
                    Required for Generator, Checker, and Commentator agents
                  </p>
                </div>
              </div>

              {/* Perplexity API Key */}
              <div className="space-y-4">
                <div className="flex items-center space-x-2">
                  <h3 className="text-lg font-medium text-white">Perplexity API</h3>
                  <span className="px-2 py-1 bg-indigo-600 text-white text-xs rounded-full">AI Research</span>
                  <span className="px-2 py-1 bg-green-600 text-white text-xs rounded-full">Alternative</span>
                </div>
                
                <div className="space-y-2">
                  <label className="block text-sm font-medium text-slate-300">API Key</label>
                  <div className="relative">
                    <input
                      type={showKeys.perplexity_api_key ? 'text' : 'password'}
                      value={config.perplexity_api_key}
                      onChange={(e) => handleInputChange('perplexity_api_key', e.target.value)}
                      onBlur={(e) => validateApiKey('perplexity_api_key', e.target.value)}
                      placeholder="pplx-... (alternative to Claude for AI analysis)"
                      className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent pr-20"
                    />
                    <div className="absolute inset-y-0 right-0 flex items-center space-x-1 pr-3">
                      {getValidationIcon('perplexity_api_key')}
                      <button
                        type="button"
                        onClick={() => toggleKeyVisibility('perplexity_api_key')}
                        className="p-1 hover:bg-slate-600 rounded transition-colors"
                      >
                        {showKeys.perplexity_api_key ? (
                          <EyeOff className="h-4 w-4 text-slate-400" />
                        ) : (
                          <Eye className="h-4 w-4 text-slate-400" />
                        )}
                      </button>
                    </div>
                  </div>
                  <p className="text-xs text-slate-500">
                    Alternative AI provider for enhanced research and analysis capabilities
                  </p>
                </div>
              </div>

              {/* OpenAI API Key (Future Enhancement) */}
              <div className="space-y-4">
                <div className="flex items-center space-x-2">
                  <h3 className="text-lg font-medium text-white">OpenAI API</h3>
                  <span className="px-2 py-1 bg-purple-600 text-white text-xs rounded-full">AI Analysis</span>
                  <span className="px-2 py-1 bg-slate-600 text-slate-300 text-xs rounded-full">Coming Soon</span>
                </div>
                
                <div className="space-y-2">
                  <label className="block text-sm font-medium text-slate-300">API Key</label>
                  <div className="relative">
                    <input
                      type={showKeys.openai_api_key ? 'text' : 'password'}
                      value={config.openai_api_key}
                      onChange={(e) => handleInputChange('openai_api_key', e.target.value)}
                      onBlur={(e) => validateApiKey('openai_api_key', e.target.value)}
                      placeholder="sk-... (for enhanced AI analysis)"
                      disabled={true}
                      className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent pr-20 disabled:opacity-50 disabled:cursor-not-allowed"
                    />
                    <div className="absolute inset-y-0 right-0 flex items-center space-x-1 pr-3">
                      {getValidationIcon('openai_api_key')}
                      <button
                        type="button"
                        onClick={() => toggleKeyVisibility('openai_api_key')}
                        disabled={true}
                        className="p-1 hover:bg-slate-600 rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        {showKeys.openai_api_key ? (
                          <EyeOff className="h-4 w-4 text-slate-400" />
                        ) : (
                          <Eye className="h-4 w-4 text-slate-400" />
                        )}
                      </button>
                    </div>
                  </div>
                  <p className="text-xs text-slate-500">
                    Future enhancement for advanced qualitative analysis
                  </p>
                </div>
              </div>

              {/* Instructions */}
              <div className="bg-blue-900/20 border border-blue-700/30 rounded-lg p-4">
                <h4 className="text-sm font-medium text-blue-300 mb-2">How to get your API keys:</h4>
                <ul className="text-xs text-blue-200 space-y-1">
                  <li>• <strong>Kite Connect:</strong> Visit <a href="https://kite.trade" target="_blank" rel="noopener noreferrer" className="underline hover:text-blue-100">kite.trade</a> → Developer Console → Create App</li>
                  <li>• <strong>Claude:</strong> Visit <a href="https://console.anthropic.com" target="_blank" rel="noopener noreferrer" className="underline hover:text-blue-100">console.anthropic.com</a> → API Keys → Create Key</li>
                  <li>• <strong>Perplexity:</strong> Visit <a href="https://www.perplexity.ai/settings/api" target="_blank" rel="noopener noreferrer" className="underline hover:text-blue-100">perplexity.ai/settings/api</a> → Generate API Key</li>
                  <li>• <strong>OpenAI:</strong> Visit <a href="https://platform.openai.com" target="_blank" rel="noopener noreferrer" className="underline hover:text-blue-100">platform.openai.com</a> → API Keys (Coming Soon)</li>
                </ul>
              </div>
            </div>
          </div>

          {/* Footer */}
          <div className="flex items-center justify-between p-6 border-t border-slate-700 bg-slate-900/50">
            <div className="text-xs text-slate-500">
              Keys are stored locally and never shared with external services
            </div>
            <div className="flex items-center space-x-3">
              <button
                onClick={onClose}
                className="px-4 py-2 text-slate-400 hover:text-white transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleSave}
                disabled={isSaving}
                className="flex items-center space-x-2 px-4 py-2 bg-primary-600 hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-lg transition-colors"
              >
                {isSaving ? (
                  <div className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full" />
                ) : (
                  <Save className="h-4 w-4" />
                )}
                <span>{isSaving ? 'Saving...' : 'Save Settings'}</span>
              </button>
            </div>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default ApiKeySettings;