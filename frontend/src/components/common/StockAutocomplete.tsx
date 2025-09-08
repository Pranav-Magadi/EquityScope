import React, { useState, useEffect, useRef } from 'react';
import { Search, Building2, ChevronDown, TrendingUp, Star, Clock } from 'lucide-react';
import { searchStocks, type StockSymbol } from '../../data/stockSymbols';

interface StockAutocompleteProps {
  value: string;
  onChange: (value: string) => void;
  onSelect: (stock: StockSymbol) => void;
  placeholder?: string;
  disabled?: boolean;
  className?: string;
  showRecentSearches?: boolean;
  showPopularStocks?: boolean;
}

export const StockAutocomplete: React.FC<StockAutocompleteProps> = ({
  value,
  onChange,
  onSelect,
  placeholder = "Search by company name or ticker symbol...",
  disabled = false,
  className = "",
  showRecentSearches = true,
  showPopularStocks = true
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [suggestions, setSuggestions] = useState<StockSymbol[]>([]);
  const [highlightedIndex, setHighlightedIndex] = useState(-1);
  const [recentSearches, setRecentSearches] = useState<StockSymbol[]>([]);
  const [showEmpty, setShowEmpty] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // Popular stocks for empty state
  const popularStocks: StockSymbol[] = [
    { ticker: 'TCS.NS', name: 'Tata Consultancy Services Limited', sector: 'IT Services', aliases: ['TCS', 'TATA CONSULTANCY'], marketCap: 'Large', description: 'Leading IT services company' },
    { ticker: 'RELIANCE.NS', name: 'Reliance Industries Limited', sector: 'Oil & Gas', aliases: ['RELIANCE', 'RIL'], marketCap: 'Large', description: 'Diversified conglomerate' },
    { ticker: 'HDFCBANK.NS', name: 'HDFC Bank Limited', sector: 'Banking', aliases: ['HDFC', 'HDFC BANK'], marketCap: 'Large', description: 'Private sector bank' },
    { ticker: 'INFY.NS', name: 'Infosys Limited', sector: 'IT Services', aliases: ['INFY', 'INFOSYS'], marketCap: 'Large', description: 'IT services and consulting' },
    { ticker: 'ICICIBANK.NS', name: 'ICICI Bank Limited', sector: 'Banking', aliases: ['ICICI', 'ICICI BANK'], marketCap: 'Large', description: 'Private sector bank' },
    { ticker: 'HINDUNILVR.NS', name: 'Hindustan Unilever Limited', sector: 'FMCG', aliases: ['HUL', 'HINDUSTAN UNILEVER'], marketCap: 'Large', description: 'Consumer goods company' }
  ];

  // Load recent searches from localStorage
  useEffect(() => {
    if (showRecentSearches) {
      const saved = localStorage.getItem('equityscope_recent_searches');
      if (saved) {
        try {
          setRecentSearches(JSON.parse(saved).slice(0, 5));
        } catch (e) {
          setRecentSearches([]);
        }
      }
    }
  }, [showRecentSearches]);

  // Save to recent searches
  const saveToRecentSearches = (stock: StockSymbol) => {
    if (!showRecentSearches) return;
    
    const updated = [
      stock,
      ...recentSearches.filter(s => s.ticker !== stock.ticker)
    ].slice(0, 5);
    
    setRecentSearches(updated);
    localStorage.setItem('equityscope_recent_searches', JSON.stringify(updated));
  };

  useEffect(() => {
    if (value.trim().length > 0) {
      const results = searchStocks(value, 8);
      setSuggestions(results);
      setIsOpen(true);
      setShowEmpty(results.length === 0);
      setHighlightedIndex(-1);
    } else {
      setSuggestions([]);
      setShowEmpty(false);
      setIsOpen(false);
    }
  }, [value]);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onChange(e.target.value);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!isOpen) return;

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setHighlightedIndex(prev => 
          prev < suggestions.length - 1 ? prev + 1 : 0
        );
        break;
      case 'ArrowUp':
        e.preventDefault();
        setHighlightedIndex(prev => 
          prev > 0 ? prev - 1 : suggestions.length - 1
        );
        break;
      case 'Enter':
        e.preventDefault();
        if (highlightedIndex >= 0 && suggestions[highlightedIndex]) {
          handleStockSelect(suggestions[highlightedIndex]);
        }
        break;
      case 'Escape':
        setIsOpen(false);
        setHighlightedIndex(-1);
        break;
    }
  };

  const handleStockSelect = (stock: StockSymbol) => {
    onChange(stock.ticker.replace('.NS', ''));
    onSelect(stock);
    saveToRecentSearches(stock);
    setIsOpen(false);
    setShowEmpty(false);
    setHighlightedIndex(-1);
    inputRef.current?.blur();
  };

  const getSectorColor = (sector: string) => {
    const colors: { [key: string]: string } = {
      'Banking': 'bg-blue-900/30 text-blue-300',
      'IT Services': 'bg-purple-900/30 text-purple-300',
      'Oil & Gas': 'bg-orange-900/30 text-orange-300',
      'FMCG': 'bg-green-900/30 text-green-300',
      'Pharma': 'bg-red-900/30 text-red-300',
      'Auto': 'bg-yellow-900/30 text-yellow-300',
      'Metals': 'bg-gray-900/30 text-gray-300',
      'Telecom': 'bg-indigo-900/30 text-indigo-300',
      'Cement': 'bg-stone-900/30 text-stone-300',
      'Power': 'bg-amber-900/30 text-amber-300',
      'Healthcare': 'bg-pink-900/30 text-pink-300',
    };
    return colors[sector] || 'bg-slate-900/30 text-slate-300';
  };

  return (
    <div ref={containerRef} className={`relative ${className}`}>
      <div className="relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-slate-400" />
        <input
          ref={inputRef}
          type="text"
          value={value}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          onFocus={() => {
            if (value.trim().length === 0 && (recentSearches.length > 0 || showPopularStocks)) {
              setIsOpen(true);
            } else if (suggestions.length > 0) {
              setIsOpen(true);
            }
          }}
          placeholder={placeholder}
          disabled={disabled}
          className="w-full pl-10 pr-10 py-3 bg-slate-800 border border-slate-700 rounded-lg text-slate-100 placeholder-slate-400 focus:ring-2 focus:ring-primary-500 focus:border-primary-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
        />
        <ChevronDown 
          className={`absolute right-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-slate-400 transition-transform ${isOpen ? 'rotate-180' : ''}`} 
        />
      </div>

      {isOpen && (
        <div className="absolute z-50 w-full mt-1 bg-slate-800 border border-slate-700 rounded-lg shadow-2xl max-h-80 overflow-y-auto">
          {/* Search Results */}
          {suggestions.length > 0 && (
            <>
              <div className="px-3 py-2 border-b border-slate-700/50 bg-slate-800/50">
                <div className="flex items-center space-x-2">
                  <Search className="h-4 w-4 text-slate-400" />
                  <span className="text-xs font-medium text-slate-400 uppercase tracking-wide">
                    Search Results ({suggestions.length})
                  </span>
                </div>
              </div>
              {suggestions.map((stock, index) => (
                <div
                  key={stock.ticker}
                  onClick={() => handleStockSelect(stock)}
                  className={`px-4 py-3 cursor-pointer border-b border-slate-700/50 last:border-b-0 transition-colors ${
                    index === highlightedIndex 
                      ? 'bg-primary-600/20 border-primary-500/50' 
                      : 'hover:bg-slate-700/50'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3 flex-1 min-w-0">
                      <div className="p-1.5 bg-slate-700 rounded flex-shrink-0">
                        <Building2 className="h-3 w-3 text-slate-400" />
                      </div>
                      <div className="min-w-0 flex-1">
                        <div className="font-medium text-slate-100">
                          {stock.ticker.replace('.NS', '')}
                        </div>
                        <div className="text-sm text-slate-400 truncate">
                          {stock.name}
                        </div>
                        {stock.description && (
                          <div className="text-xs text-slate-500 truncate mt-0.5">
                            {stock.description}
                          </div>
                        )}
                      </div>
                    </div>
                    <div className={`px-2 py-1 rounded-full text-xs font-medium flex-shrink-0 ${getSectorColor(stock.sector)}`}>
                      {stock.sector}
                    </div>
                  </div>
                </div>
              ))}
            </>
          )}

          {/* No Results */}
          {showEmpty && value.trim().length > 0 && (
            <div className="px-4 py-6 text-center">
              <div className="text-slate-400 mb-2">
                <Search className="h-8 w-8 mx-auto mb-2 opacity-50" />
                <div className="font-medium">No companies found</div>
                <div className="text-sm mt-1">
                  Try searching with a different company name or ticker symbol
                </div>
              </div>
              <div className="text-xs text-slate-500 mt-3">
                Popular searches: TCS, Reliance, HDFC Bank, Infosys
              </div>
            </div>
          )}

          {/* Empty State - Recent Searches */}
          {value.trim().length === 0 && recentSearches.length > 0 && showRecentSearches && (
            <>
              <div className="px-3 py-2 border-b border-slate-700/50 bg-slate-800/50">
                <div className="flex items-center space-x-2">
                  <Clock className="h-4 w-4 text-slate-400" />
                  <span className="text-xs font-medium text-slate-400 uppercase tracking-wide">
                    Recent Searches
                  </span>
                </div>
              </div>
              {recentSearches.map((stock, index) => (
                <div
                  key={`recent-${stock.ticker}`}
                  onClick={() => handleStockSelect(stock)}
                  className="px-4 py-3 cursor-pointer border-b border-slate-700/50 last:border-b-0 hover:bg-slate-700/50 transition-colors"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3 flex-1 min-w-0">
                      <div className="p-1.5 bg-slate-700 rounded flex-shrink-0">
                        <Clock className="h-3 w-3 text-slate-400" />
                      </div>
                      <div className="min-w-0 flex-1">
                        <div className="font-medium text-slate-100">
                          {stock.ticker.replace('.NS', '')}
                        </div>
                        <div className="text-sm text-slate-400 truncate">
                          {stock.name}
                        </div>
                      </div>
                    </div>
                    <div className={`px-2 py-1 rounded-full text-xs font-medium flex-shrink-0 ${getSectorColor(stock.sector)}`}>
                      {stock.sector}
                    </div>
                  </div>
                </div>
              ))}
            </>
          )}

          {/* Empty State - Popular Stocks */}
          {value.trim().length === 0 && showPopularStocks && (
            <>
              {recentSearches.length > 0 && showRecentSearches && (
                <div className="border-t border-slate-700/50" />
              )}
              <div className="px-3 py-2 border-b border-slate-700/50 bg-slate-800/50">
                <div className="flex items-center space-x-2">
                  <TrendingUp className="h-4 w-4 text-slate-400" />
                  <span className="text-xs font-medium text-slate-400 uppercase tracking-wide">
                    Popular Companies
                  </span>
                </div>
              </div>
              {popularStocks.map((stock, index) => (
                <div
                  key={`popular-${stock.ticker}`}
                  onClick={() => handleStockSelect(stock)}
                  className="px-4 py-3 cursor-pointer border-b border-slate-700/50 last:border-b-0 hover:bg-slate-700/50 transition-colors"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3 flex-1 min-w-0">
                      <div className="p-1.5 bg-slate-700 rounded flex-shrink-0">
                        <Star className="h-3 w-3 text-slate-400" />
                      </div>
                      <div className="min-w-0 flex-1">
                        <div className="font-medium text-slate-100">
                          {stock.ticker.replace('.NS', '')}
                        </div>
                        <div className="text-sm text-slate-400 truncate">
                          {stock.name}
                        </div>
                        {stock.description && (
                          <div className="text-xs text-slate-500 truncate mt-0.5">
                            {stock.description}
                          </div>
                        )}
                      </div>
                    </div>
                    <div className={`px-2 py-1 rounded-full text-xs font-medium flex-shrink-0 ${getSectorColor(stock.sector)}`}>
                      {stock.sector}
                    </div>
                  </div>
                </div>
              ))}
            </>
          )}
        </div>
      )}
    </div>
  );
};