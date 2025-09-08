# Analysis Logging Service
# Implements comprehensive logging and debugging for v3 Summary Engine

import logging
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path

from ..models.summary import SummaryResponse
from .weighted_scoring_service import WeightedScoringResult

logger = logging.getLogger(__name__)

@dataclass
class AnalysisLogEntry:
    """Individual analysis log entry"""
    timestamp: datetime
    ticker: str
    analysis_mode: str
    execution_time_ms: float
    
    # Core results
    investment_label: str
    total_score: float
    confidence: float
    
    # Component breakdown
    dcf_score: float
    financial_score: float
    technical_score: float
    peer_score: float
    
    # Data quality
    data_warnings: List[str]
    fallback_triggers: List[str]
    
    # Debugging info
    sector: str
    rules_applied: List[str]
    fair_value_method: str
    peer_count: int
    
    # Error tracking
    errors: List[str]
    success: bool

@dataclass
class SessionLog:
    """Complete session logging information"""
    session_id: str
    start_time: datetime
    end_time: Optional[datetime]
    total_analyses: int
    successful_analyses: int
    failed_analyses: int
    average_execution_time: float
    analyses: List[AnalysisLogEntry]

class AnalysisLoggingService:
    """
    Comprehensive logging service for v3 Summary Engine
    
    Features:
    - Detailed analysis logging to files
    - Performance tracking
    - Error analysis and debugging
    - Data quality monitoring
    - Session-based logging
    """
    
    def __init__(self, log_directory: str = "analysis_logs"):
        self.log_directory = Path(log_directory)
        self.log_directory.mkdir(exist_ok=True)
        
        # Current session tracking
        self.current_session = None
        self.session_analyses = []
        
        # Performance tracking
        self.performance_stats = {
            "total_analyses": 0,
            "average_execution_time": 0,
            "success_rate": 0,
            "error_counts": {}
        }
        
        # Create daily log file
        self.daily_log_file = self._get_daily_log_file()
        
        # Set up file logging
        self._setup_file_logging()
    
    def start_session(self) -> str:
        """Start a new analysis session"""
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.current_session = SessionLog(
            session_id=session_id,
            start_time=datetime.now(),
            end_time=None,
            total_analyses=0,
            successful_analyses=0,
            failed_analyses=0,
            average_execution_time=0,
            analyses=[]
        )
        
        logger.info(f"Started analysis session: {session_id}")
        return session_id
    
    def log_analysis(
        self,
        ticker: str,
        analysis_mode: str,
        execution_time_ms: float,
        scoring_result: WeightedScoringResult = None,
        summary_result: SummaryResponse = None,
        errors: List[str] = None,
        data_warnings: List[str] = None,
        fallback_triggers: List[str] = None
    ) -> AnalysisLogEntry:
        """Log a complete analysis with all details"""
        
        errors = errors or []
        data_warnings = data_warnings or []
        fallback_triggers = fallback_triggers or []
        
        # Create log entry
        log_entry = AnalysisLogEntry(
            timestamp=datetime.now(),
            ticker=ticker,
            analysis_mode=analysis_mode,
            execution_time_ms=execution_time_ms,
            
            # Extract from scoring result if available
            investment_label=scoring_result.investment_label if scoring_result else "Unknown",
            total_score=scoring_result.total_score if scoring_result else 0,
            confidence=scoring_result.confidence if scoring_result else 0,
            
            dcf_score=scoring_result.dcf_score if scoring_result else 0,
            financial_score=scoring_result.financial_score if scoring_result else 0,
            technical_score=scoring_result.technical_score if scoring_result else 0,
            peer_score=scoring_result.peer_score if scoring_result else 0,
            
            # Data quality
            data_warnings=data_warnings,
            fallback_triggers=fallback_triggers,
            
            # Debugging info
            sector=scoring_result.sector if scoring_result else "Unknown",
            rules_applied=getattr(summary_result, 'rules_applied', []) if summary_result else [],
            fair_value_method=summary_result.fair_value_band.method if summary_result else "Unknown",
            peer_count=len(scoring_result.component_scores.get("Peer", {}).get("reasoning", [])) if scoring_result else 0,
            
            # Error tracking
            errors=errors,
            success=len(errors) == 0
        )
        
        # Add to current session if exists
        if self.current_session:
            self.current_session.analyses.append(log_entry)
            self.current_session.total_analyses += 1
            if log_entry.success:
                self.current_session.successful_analyses += 1
            else:
                self.current_session.failed_analyses += 1
        
        # Write to daily log file
        self._write_to_daily_log(log_entry)
        
        # Update performance stats
        self._update_performance_stats(log_entry)
        
        logger.info(f"Logged analysis for {ticker}: {log_entry.investment_label} (Score: {log_entry.total_score:.1f})")
        
        return log_entry
    
    def end_session(self) -> Optional[SessionLog]:
        """End the current session and save session log"""
        if not self.current_session:
            return None
        
        self.current_session.end_time = datetime.now()
        
        # Calculate session stats
        if self.current_session.analyses:
            execution_times = [a.execution_time_ms for a in self.current_session.analyses]
            self.current_session.average_execution_time = sum(execution_times) / len(execution_times)
        
        # Save session to file
        self._save_session_log(self.current_session)
        
        session = self.current_session
        self.current_session = None
        
        logger.info(f"Ended session {session.session_id}: {session.successful_analyses}/{session.total_analyses} successful")
        
        return session
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get current performance statistics"""
        return {
            "total_analyses": self.performance_stats["total_analyses"],
            "average_execution_time_ms": self.performance_stats["average_execution_time"],
            "success_rate_pct": self.performance_stats["success_rate"] * 100,
            "top_errors": dict(sorted(
                self.performance_stats["error_counts"].items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]),
            "current_session": {
                "active": self.current_session is not None,
                "session_id": self.current_session.session_id if self.current_session else None,
                "analyses_count": len(self.current_session.analyses) if self.current_session else 0
            }
        }
    
    def get_analysis_history(self, ticker: str, days: int = 7) -> List[AnalysisLogEntry]:
        """Get analysis history for a specific ticker"""
        history = []
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Search through recent daily log files
        for i in range(days + 1):
            date = datetime.now() - timedelta(days=i)
            log_file = self._get_log_file_for_date(date)
            
            if log_file.exists():
                history.extend(self._read_analyses_from_file(log_file, ticker, cutoff_date))
        
        return sorted(history, key=lambda x: x.timestamp, reverse=True)
    
    def generate_debug_report(self, ticker: str) -> Dict[str, Any]:
        """Generate comprehensive debug report for a ticker"""
        recent_analyses = self.get_analysis_history(ticker, days=30)
        
        if not recent_analyses:
            return {"error": f"No recent analyses found for {ticker}"}
        
        # Analyze trends
        scores = [a.total_score for a in recent_analyses]
        labels = [a.investment_label for a in recent_analyses]
        execution_times = [a.execution_time_ms for a in recent_analyses]
        
        # Count label changes
        label_changes = 0
        for i in range(1, len(labels)):
            if labels[i] != labels[i-1]:
                label_changes += 1
        
        # Common issues
        all_warnings = []
        all_errors = []
        for analysis in recent_analyses:
            all_warnings.extend(analysis.data_warnings)
            all_errors.extend(analysis.errors)
        
        warning_counts = {}
        for warning in all_warnings:
            warning_counts[warning] = warning_counts.get(warning, 0) + 1
        
        error_counts = {}
        for error in all_errors:
            error_counts[error] = error_counts.get(error, 0) + 1
        
        return {
            "ticker": ticker,
            "analysis_period_days": 30,
            "total_analyses": len(recent_analyses),
            "score_stats": {
                "latest_score": scores[0] if scores else 0,
                "average_score": sum(scores) / len(scores) if scores else 0,
                "min_score": min(scores) if scores else 0,
                "max_score": max(scores) if scores else 0,
                "score_volatility": self._calculate_volatility(scores)
            },
            "label_stats": {
                "latest_label": labels[0] if labels else "Unknown",
                "label_changes": label_changes,
                "label_distribution": self._count_items(labels)
            },
            "performance_stats": {
                "average_execution_time_ms": sum(execution_times) / len(execution_times) if execution_times else 0,
                "success_rate_pct": (len([a for a in recent_analyses if a.success]) / len(recent_analyses)) * 100
            },
            "data_quality": {
                "common_warnings": dict(sorted(warning_counts.items(), key=lambda x: x[1], reverse=True)[:5]),
                "common_errors": dict(sorted(error_counts.items(), key=lambda x: x[1], reverse=True)[:5])
            },
            "recommendations": self._generate_recommendations(recent_analyses)
        }
    
    def cleanup_old_logs(self, days_to_keep: int = 30):
        """Clean up log files older than specified days"""
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        cleaned_count = 0
        for log_file in self.log_directory.glob("analysis_*.jsonl"):
            try:
                # Extract date from filename
                date_str = log_file.stem.replace("analysis_", "")
                file_date = datetime.strptime(date_str, "%Y_%m_%d")
                
                if file_date < cutoff_date:
                    log_file.unlink()
                    cleaned_count += 1
                    
            except (ValueError, OSError) as e:
                logger.warning(f"Error processing log file {log_file}: {e}")
        
        logger.info(f"Cleaned up {cleaned_count} old log files")
        return cleaned_count
    
    # Private helper methods
    
    def _get_daily_log_file(self) -> Path:
        """Get the daily log file path"""
        date_str = datetime.now().strftime("%Y_%m_%d")
        return self.log_directory / f"analysis_{date_str}.jsonl"
    
    def _get_log_file_for_date(self, date: datetime) -> Path:
        """Get log file path for specific date"""
        date_str = date.strftime("%Y_%m_%d")
        return self.log_directory / f"analysis_{date_str}.jsonl"
    
    def _setup_file_logging(self):
        """Set up file-based logging configuration"""
        # Create a file handler for analysis logs
        log_handler = logging.FileHandler(
            self.log_directory / "analysis_service.log",
            mode='a'
        )
        log_handler.setLevel(logging.INFO)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        log_handler.setFormatter(formatter)
        
        logger.addHandler(log_handler)
    
    def _write_to_daily_log(self, log_entry: AnalysisLogEntry):
        """Write log entry to daily log file"""
        try:
            with open(self.daily_log_file, 'a', encoding='utf-8') as f:
                # Convert to dict and handle datetime serialization
                entry_dict = asdict(log_entry)
                entry_dict['timestamp'] = log_entry.timestamp.isoformat()
                
                f.write(json.dumps(entry_dict) + '\n')
                
        except Exception as e:
            logger.error(f"Failed to write to daily log: {e}")
    
    def _save_session_log(self, session: SessionLog):
        """Save session log to file"""
        try:
            session_file = self.log_directory / f"session_{session.session_id}.json"
            
            session_dict = asdict(session)
            session_dict['start_time'] = session.start_time.isoformat()
            session_dict['end_time'] = session.end_time.isoformat() if session.end_time else None
            
            # Convert analysis entries
            for analysis in session_dict['analyses']:
                analysis['timestamp'] = datetime.fromisoformat(analysis['timestamp']).isoformat()
            
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(session_dict, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save session log: {e}")
    
    def _read_analyses_from_file(self, log_file: Path, ticker: str, cutoff_date: datetime) -> List[AnalysisLogEntry]:
        """Read analyses for a specific ticker from log file"""
        analyses = []
        
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        entry_dict = json.loads(line.strip())
                        
                        if entry_dict.get('ticker') == ticker:
                            timestamp = datetime.fromisoformat(entry_dict['timestamp'])
                            
                            if timestamp >= cutoff_date:
                                # Reconstruct AnalysisLogEntry
                                entry_dict['timestamp'] = timestamp
                                analysis = AnalysisLogEntry(**entry_dict)
                                analyses.append(analysis)
                                
                    except (json.JSONDecodeError, KeyError, TypeError) as e:
                        logger.warning(f"Error parsing log entry: {e}")
                        continue
                        
        except FileNotFoundError:
            pass  # File doesn't exist, return empty list
        except Exception as e:
            logger.error(f"Error reading log file {log_file}: {e}")
        
        return analyses
    
    def _update_performance_stats(self, log_entry: AnalysisLogEntry):
        """Update global performance statistics"""
        self.performance_stats["total_analyses"] += 1
        
        # Update average execution time
        current_avg = self.performance_stats["average_execution_time"]
        total = self.performance_stats["total_analyses"]
        
        new_avg = ((current_avg * (total - 1)) + log_entry.execution_time_ms) / total
        self.performance_stats["average_execution_time"] = new_avg
        
        # Update success rate
        successful = len([a for a in self.session_analyses if a.success]) if self.current_session else 0
        if self.current_session:
            successful += len([a for a in self.current_session.analyses if a.success])
        
        self.performance_stats["success_rate"] = successful / self.performance_stats["total_analyses"]
        
        # Track errors
        for error in log_entry.errors:
            self.performance_stats["error_counts"][error] = self.performance_stats["error_counts"].get(error, 0) + 1
    
    def _calculate_volatility(self, values: List[float]) -> float:
        """Calculate volatility (standard deviation) of values"""
        if len(values) < 2:
            return 0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance ** 0.5
    
    def _count_items(self, items: List[str]) -> Dict[str, int]:
        """Count occurrences of items"""
        counts = {}
        for item in items:
            counts[item] = counts.get(item, 0) + 1
        return counts
    
    def _generate_recommendations(self, analyses: List[AnalysisLogEntry]) -> List[str]:
        """Generate recommendations based on analysis history"""
        recommendations = []
        
        if not analyses:
            return ["No analysis history available"]
        
        # Check for high error rate
        error_rate = len([a for a in analyses if not a.success]) / len(analyses)
        if error_rate > 0.1:  # More than 10% failure rate
            recommendations.append(f"High error rate ({error_rate*100:.1f}%) - review data sources")
        
        # Check for high execution times
        execution_times = [a.execution_time_ms for a in analyses]
        avg_time = sum(execution_times) / len(execution_times)
        if avg_time > 5000:  # More than 5 seconds
            recommendations.append(f"Slow analysis performance ({avg_time:.0f}ms avg) - consider optimization")
        
        # Check for frequent data warnings
        all_warnings = []
        for a in analyses:
            all_warnings.extend(a.data_warnings)
        
        if len(all_warnings) > len(analyses) * 0.5:  # More than 0.5 warnings per analysis
            recommendations.append("Frequent data quality issues - review data sources")
        
        # Check score volatility
        scores = [a.total_score for a in analyses]
        volatility = self._calculate_volatility(scores)
        if volatility > 30:  # High score volatility
            recommendations.append(f"High score volatility ({volatility:.1f}) - review scoring consistency")
        
        if not recommendations:
            recommendations.append("Analysis performance looks good")
        
        return recommendations