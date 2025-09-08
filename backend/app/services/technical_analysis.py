import pandas as pd
import numpy as np
import yfinance as yf
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from .price_service import price_service
import logging

logger = logging.getLogger(__name__)

class TechnicalAnalysisService:
    """
    Service for calculating technical indicators and preparing data for the Technical Analysis Summary card.
    """
    
    @staticmethod
    def calculate_sma(data: pd.Series, window: int) -> pd.Series:
        """Calculate Simple Moving Average"""
        return data.rolling(window=window, min_periods=1).mean()
    
    @staticmethod
    def calculate_rsi(data: pd.Series, window: int = 14) -> pd.Series:
        """Calculate Relative Strength Index"""
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window, min_periods=1).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window, min_periods=1).mean()
        
        # Avoid division by zero
        rs = gain / loss.replace(0, np.inf)
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    @staticmethod
    def calculate_bollinger_bands(data: pd.Series, window: int = 20, num_std: float = 2) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Calculate Bollinger Bands"""
        sma = data.rolling(window=window, min_periods=1).mean()
        std = data.rolling(window=window, min_periods=1).std()
        
        upper_band = sma + (std * num_std)
        lower_band = sma - (std * num_std)
        
        return upper_band, sma, lower_band
    
    @staticmethod
    def find_support_resistance(data: pd.Series, window: int = 20) -> Tuple[float, float]:
        """Find basic support and resistance levels"""
        # Get recent highs and lows
        recent_data = data.tail(window * 2)  # Look at last 40 periods for more data
        
        # Calculate local maxima and minima
        highs = []
        lows = []
        
        for i in range(window, len(recent_data) - window):
            if all(recent_data.iloc[i] >= recent_data.iloc[i-j] for j in range(1, window+1)) and \
               all(recent_data.iloc[i] >= recent_data.iloc[i+j] for j in range(1, window+1)):
                highs.append(recent_data.iloc[i])
            
            if all(recent_data.iloc[i] <= recent_data.iloc[i-j] for j in range(1, window+1)) and \
               all(recent_data.iloc[i] <= recent_data.iloc[i+j] for j in range(1, window+1)):
                lows.append(recent_data.iloc[i])
        
        # If no clear levels found, use percentiles
        if not highs:
            highs = [recent_data.quantile(0.9)]
        if not lows:
            lows = [recent_data.quantile(0.1)]
        
        resistance = np.mean(highs)
        support = np.mean(lows)
        
        return support, resistance
    
    @staticmethod
    def calculate_macd(data: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Calculate MACD (Moving Average Convergence Divergence)"""
        # Calculate the MACD line (12-day EMA - 26-day EMA)
        ema_fast = data.ewm(span=fast).mean()
        ema_slow = data.ewm(span=slow).mean()
        macd_line = ema_fast - ema_slow
        
        # Signal line (9-day EMA of MACD line)
        macd_signal = macd_line.ewm(span=signal).mean()
        
        # MACD histogram (MACD - Signal)
        macd_histogram = macd_line - macd_signal
        
        return macd_line, macd_signal, macd_histogram
    
    @staticmethod
    def calculate_stochastic(high: pd.Series, low: pd.Series, close: pd.Series, k: int = 14, d: int = 3) -> Tuple[pd.Series, pd.Series]:
        """Calculate Stochastic Oscillator"""
        # Calculate %K (Fast Stochastic)
        lowest_low = low.rolling(window=k, min_periods=1).min()
        highest_high = high.rolling(window=k, min_periods=1).max()
        
        stoch_k = 100 * (close - lowest_low) / (highest_high - lowest_low)
        
        # Calculate %D (Slow Stochastic) - SMA of %K
        stoch_d = stoch_k.rolling(window=d, min_periods=1).mean()
        
        return stoch_k, stoch_d
    
    @staticmethod
    def calculate_volume_indicators(close: pd.Series, volume: pd.Series, window: int = 20) -> Tuple[pd.Series, pd.Series]:
        """Calculate volume indicators"""
        # On-Balance Volume (OBV)
        obv = pd.Series(index=close.index, dtype=float)
        obv.iloc[0] = volume.iloc[0]
        
        for i in range(1, len(close)):
            if close.iloc[i] > close.iloc[i-1]:
                obv.iloc[i] = obv.iloc[i-1] + volume.iloc[i]
            elif close.iloc[i] < close.iloc[i-1]:
                obv.iloc[i] = obv.iloc[i-1] - volume.iloc[i]
            else:
                obv.iloc[i] = obv.iloc[i-1]
        
        # Volume Simple Moving Average
        volume_sma = volume.rolling(window=window, min_periods=1).mean()
        
        return obv, volume_sma
    
    @staticmethod
    def analyze_volume_trend(volume: pd.Series, window: int = 10) -> str:
        """Analyze volume trend over recent periods"""
        if len(volume) < window * 2:
            return 'neutral'
        
        recent_avg = volume.tail(window).mean()
        previous_avg = volume.tail(window * 2).head(window).mean()
        
        if recent_avg > previous_avg * 1.1:  # 10% increase
            return 'increasing'
        elif recent_avg < previous_avg * 0.9:  # 10% decrease
            return 'decreasing'
        else:
            return 'neutral'
    
    @staticmethod
    def detect_signals(data: Dict[str, Any]) -> List[str]:
        """Detect technical signals from the calculated indicators"""
        signals = []
        
        current_price = data.get('current_price', 0)
        sma_50 = data.get('sma_50_current', 0)
        sma_200 = data.get('sma_200_current', 0)
        rsi = data.get('rsi', 50)
        bb_upper = data.get('bb_upper_current', 0)
        bb_lower = data.get('bb_lower_current', 0)
        
        # MACD signals
        macd_current = data.get('macd_current', 0)
        macd_signal_current = data.get('macd_signal_current', 0)
        
        # Stochastic signals
        stoch_k = data.get('stoch_k_current', 50)
        stoch_d = data.get('stoch_d_current', 50)
        
        # Volume trend
        volume_trend = data.get('volume_trend', 'neutral')
        
        # Golden Cross / Death Cross
        if sma_50 > sma_200 and data.get('sma_50_prev', 0) <= data.get('sma_200_prev', 0):
            signals.append("Golden Cross detected")
        elif sma_50 < sma_200 and data.get('sma_50_prev', 0) >= data.get('sma_200_prev', 0):
            signals.append("Death Cross detected")
        
        # MACD signals
        if macd_current > macd_signal_current:
            if abs(macd_current - macd_signal_current) > 0.5:
                signals.append("MACD bullish divergence - strong momentum")
            else:
                signals.append("MACD bullish signal")
        elif macd_current < macd_signal_current:
            if abs(macd_current - macd_signal_current) > 0.5:
                signals.append("MACD bearish divergence - weak momentum")
            else:
                signals.append("MACD bearish signal")
        
        # RSI signals
        if rsi >= 70:
            signals.append("RSI indicates overbought condition")
        elif rsi <= 30:
            signals.append("RSI indicates oversold condition")
        
        # Stochastic signals
        if stoch_k >= 80 and stoch_d >= 80:
            signals.append("Stochastic indicates overbought condition")
        elif stoch_k <= 20 and stoch_d <= 20:
            signals.append("Stochastic indicates oversold condition")
        elif stoch_k > stoch_d and stoch_k > 50:
            signals.append("Stochastic bullish crossover")
        elif stoch_k < stoch_d and stoch_k < 50:
            signals.append("Stochastic bearish crossover")
        
        # Bollinger Band signals
        if current_price >= bb_upper:
            signals.append("Price touching upper Bollinger Band")
        elif current_price <= bb_lower:
            signals.append("Price touching lower Bollinger Band")
        
        # Volume signals
        if volume_trend == 'increasing':
            signals.append("Volume accumulation detected")
        elif volume_trend == 'decreasing':
            signals.append("Volume distribution detected")
        
        # Support/Resistance
        support = data.get('support_level', 0)
        resistance = data.get('resistance_level', 0)
        
        if resistance > 0 and abs(current_price - resistance) / resistance < 0.02:  # Within 2%
            signals.append("Price near resistance level")
        elif support > 0 and abs(current_price - support) / support < 0.02:  # Within 2%
            signals.append("Price near support level")
        
        return signals
    
    def get_technical_analysis(self, ticker: str, period: str = "1y") -> Optional[Dict[str, Any]]:
        """
        Get comprehensive technical analysis for a ticker
        
        Args:
            ticker: Stock ticker symbol
            period: Time period ("3mo", "6mo", "1y", "3y")
            
        Returns:
            Dictionary containing all technical analysis data
        """
        try:
            logger.info(f"Fetching technical analysis for {ticker} with period {period}")
            
            # Fetch historical data
            stock = yf.Ticker(ticker)
            
            # Map period to yfinance format and determine data points needed
            period_map = {
                "3mo": ("3mo", 90),
                "6mo": ("6mo", 180), 
                "1y": ("1y", 365),
                "3y": ("3y", 1095)
            }
            
            yf_period, days_needed = period_map.get(period, ("1y", 365))
            
            # Fetch extra data to ensure we have enough for 200-day SMA calculation
            extended_period = "2y" if period in ["3mo", "6mo", "1y"] else "5y"
            hist = stock.history(period=extended_period)
            
            if hist.empty:
                logger.error(f"No historical data found for {ticker}")
                return None
            
            # Take only the requested period for display, but use extended data for calculations
            display_data = hist.tail(days_needed).copy()
            
            # Calculate indicators using full dataset
            close_prices = hist['Close']
            high_prices = hist['High']
            low_prices = hist['Low']
            volume_data = hist['Volume']
            
            # Simple Moving Averages
            sma_50 = self.calculate_sma(close_prices, 50)
            sma_200 = self.calculate_sma(close_prices, 200)
            
            # RSI
            rsi = self.calculate_rsi(close_prices, 14)
            
            # Bollinger Bands
            bb_upper, bb_middle, bb_lower = self.calculate_bollinger_bands(close_prices, 20)
            
            # MACD
            macd_line, macd_signal, macd_histogram = self.calculate_macd(close_prices)
            
            # Stochastic
            stoch_k, stoch_d = self.calculate_stochastic(high_prices, low_prices, close_prices)
            
            # Volume indicators
            obv, volume_sma = self.calculate_volume_indicators(close_prices, volume_data)
            volume_trend = self.analyze_volume_trend(volume_data)
            
            # Support and Resistance
            support, resistance = self.find_support_resistance(close_prices)
            
            # Get current price from unified service for consistency
            unified_current_price = price_service.get_price_for_dcf(ticker)
            current_price = unified_current_price if unified_current_price else close_prices.iloc[-1]
            logger.info(f"Using unified current price for {ticker}: ₹{current_price:.2f}")
            current_rsi = rsi.iloc[-1]
            current_sma_50 = sma_50.iloc[-1]
            current_sma_200 = sma_200.iloc[-1]
            current_bb_upper = bb_upper.iloc[-1]
            current_bb_lower = bb_lower.iloc[-1]
            current_bb_middle = bb_middle.iloc[-1]
            
            # New indicators current values
            current_macd = macd_line.iloc[-1] if len(macd_line) > 0 and not pd.isna(macd_line.iloc[-1]) else 0
            current_macd_signal = macd_signal.iloc[-1] if len(macd_signal) > 0 and not pd.isna(macd_signal.iloc[-1]) else 0
            current_macd_histogram = macd_histogram.iloc[-1] if len(macd_histogram) > 0 and not pd.isna(macd_histogram.iloc[-1]) else 0
            current_stoch_k = stoch_k.iloc[-1] if len(stoch_k) > 0 and not pd.isna(stoch_k.iloc[-1]) else 50
            current_stoch_d = stoch_d.iloc[-1] if len(stoch_d) > 0 and not pd.isna(stoch_d.iloc[-1]) else 50
            current_obv = obv.iloc[-1] if len(obv) > 0 and not pd.isna(obv.iloc[-1]) else 0
            
            # Get previous values for signal detection
            prev_sma_50 = sma_50.iloc[-2] if len(sma_50) > 1 else current_sma_50
            prev_sma_200 = sma_200.iloc[-2] if len(sma_200) > 1 else current_sma_200
            
            # Prepare indicator values for AI agent
            indicator_values = {
                'current_price': float(current_price),
                'rsi': float(current_rsi),
                'price_vs_50d_sma': float(current_price / current_sma_50),
                'price_vs_200d_sma': float(current_price / current_sma_200),
                'support_level': float(support),
                'resistance_level': float(resistance),
                'sma_50_current': float(current_sma_50),
                'sma_200_current': float(current_sma_200),
                'sma_50_prev': float(prev_sma_50),
                'sma_200_prev': float(prev_sma_200),
                'bb_upper_current': float(current_bb_upper),
                'bb_lower_current': float(current_bb_lower),
                'bb_middle_current': float(current_bb_middle),
                # New indicators
                'macd_current': float(current_macd),
                'macd_signal_current': float(current_macd_signal),
                'macd_histogram_current': float(current_macd_histogram),
                'stoch_k_current': float(current_stoch_k),
                'stoch_d_current': float(current_stoch_d),
                'volume_trend': volume_trend,
                'obv_current': float(current_obv)
            }
            
            # Detect signals
            signals = self.detect_signals(indicator_values)
            if signals:
                indicator_values['signals'] = signals
            
            # Prepare chart data (only for the requested display period)
            chart_data = []
            display_sma_50 = sma_50.tail(len(display_data))
            display_sma_200 = sma_200.tail(len(display_data))
            display_bb_upper = bb_upper.tail(len(display_data))
            display_bb_lower = bb_lower.tail(len(display_data))
            display_bb_middle = bb_middle.tail(len(display_data))
            display_rsi = rsi.tail(len(display_data))
            
            # New indicators for display
            display_macd_line = macd_line.tail(len(display_data))
            display_macd_signal = macd_signal.tail(len(display_data))
            display_macd_histogram = macd_histogram.tail(len(display_data))
            display_stoch_k = stoch_k.tail(len(display_data))
            display_stoch_d = stoch_d.tail(len(display_data))
            display_obv = obv.tail(len(display_data))
            display_volume_sma = volume_sma.tail(len(display_data))
            
            for i, (date, row) in enumerate(display_data.iterrows()):
                chart_data.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'timestamp': int(date.timestamp()),
                    'open': float(row['Open']),
                    'high': float(row['High']),
                    'low': float(row['Low']),
                    'close': float(row['Close']),
                    'volume': int(row['Volume']),
                    'sma_50': float(display_sma_50.iloc[i]) if not pd.isna(display_sma_50.iloc[i]) else None,
                    'sma_200': float(display_sma_200.iloc[i]) if not pd.isna(display_sma_200.iloc[i]) else None,
                    'bb_upper': float(display_bb_upper.iloc[i]) if not pd.isna(display_bb_upper.iloc[i]) else None,
                    'bb_lower': float(display_bb_lower.iloc[i]) if not pd.isna(display_bb_lower.iloc[i]) else None,
                    'bb_middle': float(display_bb_middle.iloc[i]) if not pd.isna(display_bb_middle.iloc[i]) else None,
                    'rsi': float(display_rsi.iloc[i]) if not pd.isna(display_rsi.iloc[i]) else None,
                    # New indicators
                    'macd_line': float(display_macd_line.iloc[i]) if i < len(display_macd_line) and not pd.isna(display_macd_line.iloc[i]) else None,
                    'macd_signal': float(display_macd_signal.iloc[i]) if i < len(display_macd_signal) and not pd.isna(display_macd_signal.iloc[i]) else None,
                    'macd_histogram': float(display_macd_histogram.iloc[i]) if i < len(display_macd_histogram) and not pd.isna(display_macd_histogram.iloc[i]) else None,
                    'stoch_k': float(display_stoch_k.iloc[i]) if i < len(display_stoch_k) and not pd.isna(display_stoch_k.iloc[i]) else None,
                    'stoch_d': float(display_stoch_d.iloc[i]) if i < len(display_stoch_d) and not pd.isna(display_stoch_d.iloc[i]) else None,
                    'volume_sma': float(display_volume_sma.iloc[i]) if i < len(display_volume_sma) and not pd.isna(display_volume_sma.iloc[i]) else None,
                    'obv': float(display_obv.iloc[i]) if i < len(display_obv) and not pd.isna(display_obv.iloc[i]) else None
                })
            
            result = {
                'ticker': ticker,
                'period': period,
                'chart_data': chart_data,
                'indicator_values': indicator_values,
                'analysis_timestamp': datetime.now().isoformat(),
                'data_points': len(chart_data)
            }
            
            logger.info(f"Technical analysis completed for {ticker}: {len(chart_data)} data points")
            return result
            
        except Exception as e:
            logger.error(f"Error in technical analysis for {ticker}: {e}")
            return None

# Global service instance
technical_analysis_service = TechnicalAnalysisService()