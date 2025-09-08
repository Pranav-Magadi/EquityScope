import pytest
import json
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime

from backend.app.api.optimized_analysis import router
from backend.app.models.dcf import DCFAssumptions
from fastapi import FastAPI

# Create test app
app = FastAPI()
app.include_router(router)
client = TestClient(app)

class TestOptimizedAnalysisAPI:
    """
    Comprehensive TDD tests for Optimized Analysis API endpoints.
    
    Test Coverage:
    - Cost optimization API functionality
    - Performance targets (30s response)
    - Error handling and edge cases
    - Real-time streaming capabilities
    - Assumption validation endpoint
    """
    
    @pytest.fixture
    def sample_analysis_request(self):
        """Sample analysis request for testing."""
        return {
            "ticker": "TCS",
            "user_assumptions": {
                "revenue_growth_rate": 10.0,
                "ebitda_margin": 18.0,
                "tax_rate": 25.0,
                "wacc": 11.5,
                "terminal_growth_rate": 3.5
            },
            "max_news_articles": 5,
            "use_cache": True
        }
    
    @pytest.fixture
    def mock_optimized_analysis_result(self):
        """Mock optimized analysis result."""
        return {
            "metadata": {
                "ticker": "TCS.NS",
                "company_name": "Tata Consultancy Services",
                "analysis_timestamp": datetime.now().isoformat(),
                "analysis_duration_seconds": 28.5,
                "news_articles_analyzed": 5,
                "workflow_version": "2.0-optimized",
                "cost_optimization": {
                    "agent_count": 2,
                    "estimated_tokens": 10000,
                    "estimated_cost_usd": 0.30,
                    "cost_reduction_vs_v1": "50%"
                }
            },
            "raw_data": {
                "financial_data": {"ticker": "TCS.NS"},
                "news_articles": []
            },
            "analysis_engine_output": {
                "company_overview": {
                    "investment_thesis": "TCS is a market leader with strong fundamentals",
                    "key_strengths": ["Market leadership", "Strong margins"],
                    "key_risks": ["Currency risk", "Competition"]
                },
                "dcf_assumptions": {
                    "revenue_growth_rate": 10.0,
                    "ebitda_margin": 18.0,
                    "wacc": 11.5
                }
            },
            "dcf_validation_output": {
                "validation_summary": {
                    "overall_assessment": "reasonable",
                    "confidence_level": "high"
                }
            },
            "enhanced_insights": {
                "investment_summary": {
                    "thesis": "Strong buy candidate",
                    "confidence_level": "high"
                }
            },
            "user_guidance": {
                "what_this_means": {
                    "financial_health": "Company shows strong financial health"
                }
            }
        }
    
    def test_health_check_endpoint(self):
        """Test health check endpoint returns correct status."""
        
        response = client.get("/api/v2/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "healthy"
        assert data["version"] == "2.0-optimized"
        assert "timestamp" in data
        assert "services" in data
        assert "cost_optimization" in data
        
        # Validate cost optimization targets
        cost_opt = data["cost_optimization"]
        assert cost_opt["target_cost_per_analysis"] == 0.30
        assert cost_opt["target_response_time_seconds"] == 30
        assert cost_opt["agent_count"] == 2
        assert cost_opt["estimated_token_usage"] == 10000
    
    def test_cost_metrics_endpoint(self):
        """Test cost metrics endpoint returns optimization data."""
        
        response = client.get("/api/v2/cost-metrics")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "cost_optimization" in data
        assert "performance_optimization" in data
        assert "token_usage" in data
        
        # Validate cost reduction metrics
        cost_opt = data["cost_optimization"]
        assert cost_opt["v2_cost_per_analysis"]["target"] == 0.30
        assert cost_opt["cost_reduction_percentage"] > 50
        
        # Validate performance improvement
        perf_opt = data["performance_optimization"]
        assert perf_opt["v2_response_time"]["target"] == 30
        assert perf_opt["performance_improvement_percentage"] > 0
        
        # Validate token reduction
        token_usage = data["token_usage"]
        assert token_usage["v2_tokens_per_analysis"]["total"] == 10000
        assert token_usage["token_reduction_percentage"] > 40
    
    @patch('backend.app.api.optimized_analysis.optimized_workflow.execute_optimized_analysis')
    def test_analyze_endpoint_success(self, mock_execute, sample_analysis_request, mock_optimized_analysis_result):
        """Test successful analysis endpoint execution."""
        
        # Mock the workflow execution
        mock_execute.return_value = mock_optimized_analysis_result
        
        response = client.post("/api/v2/analyze", json=sample_analysis_request)
        
        assert response.status_code == 200
        data = response.json()
        
        # Validate response structure
        assert "metadata" in data
        assert "raw_data" in data
        assert "analysis_engine_output" in data
        assert "dcf_validation_output" in data
        assert "enhanced_insights" in data
        assert "user_guidance" in data
        
        # Validate cost optimization metadata
        metadata = data["metadata"]
        assert metadata["workflow_version"] == "2.0-optimized"
        
        cost_opt = metadata["cost_optimization"]
        assert cost_opt["agent_count"] == 2
        assert cost_opt["estimated_cost_usd"] == 0.30
        assert cost_opt["cost_reduction_vs_v1"] == "50%"
        
        # Validate API call
        mock_execute.assert_called_once()
        call_args = mock_execute.call_args
        assert call_args[1]['ticker'] == 'TCS.NS'  # Should add .NS suffix
        assert call_args[1]['max_news_articles'] == 5
    
    def test_analyze_endpoint_ticker_normalization(self, sample_analysis_request, mock_optimized_analysis_result):
        """Test that ticker symbols are properly normalized."""
        
        with patch('backend.app.api.optimized_analysis.optimized_workflow.execute_optimized_analysis', return_value=mock_optimized_analysis_result) as mock_execute:
            
            # Test various ticker formats
            test_cases = [
                ("TCS", "TCS.NS"),
                ("tcs", "TCS.NS"),
                ("RELIANCE", "RELIANCE.NS"),
                ("HDFCBANK.NS", "HDFCBANK.NS"),  # Already has suffix
                ("INFY.BO", "INFY.BO")  # BSE format
            ]
            
            for input_ticker, expected_ticker in test_cases:
                request = {**sample_analysis_request, "ticker": input_ticker}
                response = client.post("/api/v2/analyze", json=request)
                
                assert response.status_code == 200
                
                # Check that the workflow was called with normalized ticker
                call_args = mock_execute.call_args
                assert call_args[1]['ticker'] == expected_ticker
    
    def test_analyze_endpoint_validation_errors(self):
        """Test analysis endpoint validation errors."""
        
        # Test empty ticker
        invalid_request = {
            "ticker": "",
            "max_news_articles": 5
        }
        
        response = client.post("/api/v2/analyze", json=invalid_request)
        assert response.status_code == 400
        assert "Ticker symbol is required" in response.json()["detail"]
    
    @patch('backend.app.api.optimized_analysis.optimized_workflow.execute_optimized_analysis')
    def test_analyze_endpoint_workflow_failure(self, mock_execute, sample_analysis_request):
        """Test handling when workflow execution fails."""
        
        # Mock workflow returning None (failure)
        mock_execute.return_value = None
        
        response = client.post("/api/v2/analyze", json=sample_analysis_request)
        
        assert response.status_code == 404
        assert "Could not analyze TCS.NS" in response.json()["detail"]
    
    @patch('backend.app.api.optimized_analysis.optimized_workflow.execute_optimized_analysis')
    def test_analyze_endpoint_exception_handling(self, mock_execute, sample_analysis_request):
        """Test handling of unexpected exceptions."""
        
        # Mock workflow raising exception
        mock_execute.side_effect = Exception("Unexpected error")
        
        response = client.post("/api/v2/analyze", json=sample_analysis_request)
        
        assert response.status_code == 500
        assert "Analysis failed" in response.json()["detail"]
    
    @patch('backend.app.api.optimized_analysis.optimized_ai_service.dcf_validator_agent')
    @patch('yfinance.Ticker')
    def test_validate_assumptions_endpoint(self, mock_ticker, mock_validator):
        """Test DCF assumptions validation endpoint."""
        
        # Mock yfinance data
        mock_stock = MagicMock()
        mock_stock.info = {
            'longName': 'Tata Consultancy Services',
            'sector': 'Technology'
        }
        mock_ticker.return_value = mock_stock
        
        # Mock validation result
        mock_validation_result = {
            'validation_summary': {
                'overall_assessment': 'reasonable',
                'confidence_level': 'high',
                'key_concerns': ['Revenue growth above historical average']
            },
            'assumption_feedback': {
                'revenue_growth_rate': {
                    'assessment': 'reasonable',
                    'peer_comparison': 'vs industry average of 8.5%'
                }
            }
        }
        mock_validator.return_value = mock_validation_result
        
        # Test assumptions
        assumptions = {
            "revenue_growth_rate": 10.0,
            "ebitda_margin": 18.0,
            "tax_rate": 25.0,
            "wacc": 11.5,
            "terminal_growth_rate": 3.5
        }
        
        response = client.post(
            "/api/v2/validate-assumptions",
            params={"ticker": "TCS"},
            json=assumptions
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["ticker"] == "TCS.NS"
        assert "validation_result" in data
        assert "metadata" in data
        
        # Validate cost information
        metadata = data["metadata"]
        assert metadata["estimated_cost"] == 0.06  # DCF Validator only
        
        # Validate that validator was called
        mock_validator.assert_called_once()
    
    @patch('yfinance.Ticker')
    def test_validate_assumptions_invalid_ticker(self, mock_ticker):
        """Test assumption validation with invalid ticker."""
        
        # Mock yfinance returning empty data
        mock_stock = MagicMock()
        mock_stock.info = {}
        mock_ticker.return_value = mock_stock
        
        assumptions = {
            "revenue_growth_rate": 10.0,
            "ebitda_margin": 18.0,
            "tax_rate": 25.0,
            "wacc": 11.5,
            "terminal_growth_rate": 3.5
        }
        
        response = client.post(
            "/api/v2/validate-assumptions",
            params={"ticker": "INVALID"},
            json=assumptions
        )
        
        assert response.status_code == 404
        assert "Company data not found" in response.json()["detail"]
    
    def test_analyze_stream_endpoint_structure(self):
        """Test streaming analysis endpoint structure."""
        
        # Mock the workflow to avoid actual execution
        with patch('backend.app.api.optimized_analysis.optimized_workflow.execute_optimized_analysis') as mock_execute, \
             patch('backend.app.api.optimized_analysis.optimized_workflow.add_progress_callback') as mock_callback:
            
            mock_execute.return_value = {"test": "result"}
            
            request_data = {
                "ticker": "TCS",
                "max_news_articles": 3
            }
            
            response = client.post("/api/v2/analyze/stream", json=request_data)
            
            # Should return streaming response
            assert response.status_code == 200
            assert response.headers["content-type"] == "text/plain; charset=utf-8"
            assert "Cache-Control" in response.headers
            assert response.headers["Cache-Control"] == "no-cache"
    
    def test_request_models_validation(self):
        """Test request model validation."""
        
        # Test OptimizedAnalysisRequest validation
        valid_request = {
            "ticker": "TCS",
            "user_assumptions": {
                "revenue_growth_rate": 10.0,
                "ebitda_margin": 18.0,
                "tax_rate": 25.0,
                "wacc": 11.5,
                "terminal_growth_rate": 3.5
            },
            "max_news_articles": 5,
            "use_cache": True
        }
        
        with patch('backend.app.api.optimized_analysis.optimized_workflow.execute_optimized_analysis', return_value={"metadata": {}, "raw_data": {}, "analysis_engine_output": {}, "dcf_validation_output": {}, "enhanced_insights": {}, "user_guidance": {}}):
            response = client.post("/api/v2/analyze", json=valid_request)
            assert response.status_code == 200
        
        # Test with missing optional fields
        minimal_request = {"ticker": "TCS"}
        
        with patch('backend.app.api.optimized_analysis.optimized_workflow.execute_optimized_analysis', return_value={"metadata": {}, "raw_data": {}, "analysis_engine_output": {}, "dcf_validation_output": {}, "enhanced_insights": {}, "user_guidance": {}}):
            response = client.post("/api/v2/analyze", json=minimal_request)
            assert response.status_code == 200
    
    def test_background_task_metrics_collection(self, sample_analysis_request, mock_optimized_analysis_result):
        """Test that metrics collection background task is triggered."""
        
        with patch('backend.app.api.optimized_analysis.optimized_workflow.execute_optimized_analysis', return_value=mock_optimized_analysis_result) as mock_execute, \
             patch('backend.app.api.optimized_analysis._collect_analysis_metrics') as mock_metrics:
            
            response = client.post("/api/v2/analyze", json=sample_analysis_request)
            
            assert response.status_code == 200
            
            # Background task should be scheduled (can't easily test execution in sync test)
            # But we can verify the response completes successfully
    
    def test_performance_requirements_metadata(self, sample_analysis_request, mock_optimized_analysis_result):
        """Test that performance requirements are reflected in response metadata."""
        
        # Ensure mock result shows good performance
        mock_optimized_analysis_result["metadata"]["analysis_duration_seconds"] = 25.8
        
        with patch('backend.app.api.optimized_analysis.optimized_workflow.execute_optimized_analysis', return_value=mock_optimized_analysis_result):
            
            response = client.post("/api/v2/analyze", json=sample_analysis_request)
            
            assert response.status_code == 200
            data = response.json()
            
            # Should meet performance target
            duration = data["metadata"]["analysis_duration_seconds"]
            assert duration < 30  # Target: <30 seconds
            
            # Should meet cost target
            cost = data["metadata"]["cost_optimization"]["estimated_cost_usd"]
            assert cost <= 0.30  # Target: ≤$0.30
    
    def test_error_response_structure(self):
        """Test that error responses follow consistent structure."""
        
        # Trigger a validation error
        response = client.post("/api/v2/analyze", json={"ticker": ""})
        
        assert response.status_code == 400
        
        # Should have structured error (this would be handled by FastAPI's default error handling)
        error_data = response.json()
        assert "detail" in error_data
    
    @patch('backend.app.api.optimized_analysis.optimized_workflow.execute_optimized_analysis')
    def test_concurrent_requests_handling(self, mock_execute, sample_analysis_request, mock_optimized_analysis_result):
        """Test that API can handle concurrent requests efficiently."""
        
        # Mock workflow with slight delay to simulate real execution
        import asyncio
        
        async def mock_workflow(*args, **kwargs):
            await asyncio.sleep(0.1)  # Simulate processing time
            return mock_optimized_analysis_result
        
        mock_execute.side_effect = mock_workflow
        
        # Send multiple concurrent requests
        import threading
        import queue
        
        results = queue.Queue()
        
        def make_request():
            response = client.post("/api/v2/analyze", json=sample_analysis_request)
            results.put(response.status_code)
        
        # Create multiple threads
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check that all requests succeeded
        status_codes = []
        while not results.empty():
            status_codes.append(results.get())
        
        assert len(status_codes) == 5
        assert all(code == 200 for code in status_codes)
    
    def test_api_versioning(self):
        """Test that API versioning is properly implemented."""
        
        # All endpoints should be under /api/v2
        health_response = client.get("/api/v2/health")
        assert health_response.status_code == 200
        
        cost_metrics_response = client.get("/api/v2/cost-metrics")
        assert cost_metrics_response.status_code == 200
        
        # Validate version in response
        health_data = health_response.json()
        assert health_data["version"] == "2.0-optimized"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])