"""
Centralized observability service for handling all metrics collection.
This service ensures we use only Prometheus data and eliminates duplicate database calls.
"""

import httpx
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timezone
import logging
from metrics import get_metrics, update_accounts_count, update_total_balance
from database.repository import db

logger = logging.getLogger("observability")

class ObservabilityService:
    """Centralized service for collecting and processing observability data"""
    
    def __init__(self):
        self.categorizer_url = "http://categorizer:9000"
        self._cache = {}
        self._cache_ttl = {}
        self.cache_duration = 30  # 30 seconds
    
    def _is_cache_valid(self, key: str) -> bool:
        """Check if cached data is still valid"""
        if key not in self._cache_ttl:
            return False
        return (datetime.now().timestamp() - self._cache_ttl[key]) < self.cache_duration
    
    def _set_cache(self, key: str, value):
        """Set cache value with timestamp"""
        self._cache[key] = value
        self._cache_ttl[key] = datetime.now().timestamp()
    
    async def _fetch_prometheus_metrics(self) -> Tuple[str, str]:
        """Fetch Prometheus metrics from both backend and categorizer"""
        cache_key = "prometheus_metrics"
        if self._is_cache_valid(cache_key):
            return self._cache[cache_key]
        
        # Update gauges before fetching metrics (only once per cache period)
        await self._update_system_gauges()
        
        # Get backend metrics
        backend_metrics = get_metrics()
        
        # Fetch categorizer metrics
        categorizer_metrics = ""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.categorizer_url}/metrics", timeout=5.0)
                if response.status_code == 200:
                    categorizer_metrics = response.text
        except Exception as e:
            logger.warning(f"Failed to fetch categorizer metrics: {str(e)}")
        
        result = (backend_metrics, categorizer_metrics)
        self._set_cache(cache_key, result)
        return result
    
    async def _update_system_gauges(self):
        """Update system-wide gauge metrics (cached to avoid repeated DB calls)"""
        cache_key = "system_gauges"
        if self._is_cache_valid(cache_key):
            return
        
        # Single database call for accounts
        accounts = db.get_accounts()
        update_accounts_count(len(accounts))
        total_balance = sum(acc.balance for acc in accounts)
        update_total_balance(total_balance)
        
        self._set_cache(cache_key, True)
    
    def _extract_histogram_average(self, lines: List[str], metric_name: str) -> float:
        """Extract average from Prometheus histogram sum/count"""
        sum_value = 0.0
        count_value = 0.0
        
        for line in lines:
            if line.startswith(f"{metric_name}_sum"):
                try:
                    sum_value += float(line.split()[-1])
                except (IndexError, ValueError):
                    continue
            elif line.startswith(f"{metric_name}_count"):
                try:
                    count_value += float(line.split()[-1])
                except (IndexError, ValueError):
                    continue
        
        if count_value > 0:
            return sum_value / count_value
        return 0.0
    
    def _extract_metric_value(self, lines: List[str], metric_name: str) -> float:
        """Extract simple metric value"""
        for line in lines:
            if line.startswith(metric_name) and not line.startswith(f"{metric_name}_"):
                try:
                    return float(line.split()[-1])
                except (IndexError, ValueError):
                    continue
        return 0.0
    
    def _extract_counter_by_label(self, lines: List[str], metric_name: str, label_filters: Dict[str, str] = None) -> float:
        """Extract counter value with optional label filtering"""
        total = 0.0
        for line in lines:
            if line.startswith(metric_name) and "{" in line:
                if label_filters:
                    # Check if all label filters match
                    if all(f'{key}="{value}"' in line for key, value in label_filters.items()):
                        try:
                            total += float(line.split()[-1])
                        except (IndexError, ValueError):
                            continue
                else:
                    try:
                        total += float(line.split()[-1])
                    except (IndexError, ValueError):
                        continue
        return total
    
    def _parse_prometheus_metrics(self, backend_metrics: str, categorizer_metrics: str) -> Dict:
        """Parse Prometheus metrics into structured format"""
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "backend": {},
            "categorizer": {},
            "summary": {}
        }
        
        # Parse backend metrics
        backend_lines = backend_metrics.strip().split('\n')
        backend_lines = [line for line in backend_lines if not line.startswith('#') and line.strip()]
        
        # Calculate average response time from histogram
        avg_response_time_seconds = self._extract_histogram_average(backend_lines, "api_request_duration_seconds")
        avg_response_time_ms = avg_response_time_seconds * 1000
        
        metrics["backend"] = {
            "transactions_total": self._extract_counter_by_label(backend_lines, "transactions_total"),
            "topups_triggered_total": self._extract_metric_value(backend_lines, "topups_triggered_total"),
            "api_requests_total": self._extract_counter_by_label(backend_lines, "api_requests_total"),
            "categorizer_requests_success": self._extract_counter_by_label(backend_lines, "categorizer_requests_total", {"status": "success"}),
            "categorizer_requests_failure": self._extract_counter_by_label(backend_lines, "categorizer_requests_total", {"status": "failure"}),
            "accounts_count": self._extract_metric_value(backend_lines, "accounts_total"),
            "total_balance": self._extract_metric_value(backend_lines, "account_balance_total"),
            "avg_response_time_ms": avg_response_time_ms
        }
        
        # Parse categorizer metrics
        if categorizer_metrics:
            categorizer_lines = categorizer_metrics.strip().split('\n')
            categorizer_lines = [line for line in categorizer_lines if not line.startswith('#') and line.strip()]
            
            metrics["categorizer"] = {
                "categorization_requests_total": self._extract_counter_by_label(categorizer_lines, "categorization_requests_total"),
                "categorization_errors_total": self._extract_counter_by_label(categorizer_lines, "categorization_errors_total"),
                "http_requests_total": self._extract_counter_by_label(categorizer_lines, "http_requests_total"),
            }
        
        # Calculate summary metrics
        total_categorizer_requests = metrics["categorizer"].get("categorization_requests_total", 0)
        total_categorizer_errors = metrics["categorizer"].get("categorization_errors_total", 0)
        
        metrics["summary"] = {
            "total_transactions": metrics["backend"]["transactions_total"],
            "total_accounts": metrics["backend"]["accounts_count"],
            "total_balance": metrics["backend"]["total_balance"],
            "total_requests": metrics["backend"]["api_requests_total"],
            "avg_response_time_ms": metrics["backend"]["avg_response_time_ms"],
            "categorizer_success_rate": ((total_categorizer_requests - total_categorizer_errors) / max(total_categorizer_requests, 1)) * 100,
            "categorizer_error_rate": total_categorizer_errors,
            "system_health": "healthy" if total_categorizer_errors < 10 else "degraded"
        }
        
        return metrics
    
    async def get_metrics(self) -> Dict:
        """Get parsed metrics from Prometheus data"""
        backend_metrics, categorizer_metrics = await self._fetch_prometheus_metrics()
        return self._parse_prometheus_metrics(backend_metrics, categorizer_metrics)
    
    async def get_category_breakdown(self) -> Dict:
        """Get category breakdown from Prometheus transaction counters"""
        backend_metrics, _ = await self._fetch_prometheus_metrics()
        backend_lines = backend_metrics.strip().split('\n')
        backend_lines = [line for line in backend_lines if not line.startswith('#') and line.strip()]
        
        # Extract category data from transaction counters
        category_counts = {}
        total_transactions = 0
        
        for line in backend_lines:
            if line.startswith("transactions_total{") and "category=" in line:
                try:
                    # Extract category from label
                    category_start = line.find('category="') + 10
                    category_end = line.find('"', category_start)
                    if category_start > 9 and category_end > category_start:
                        category = line[category_start:category_end]
                        count = float(line.split()[-1])
                        category_counts[category] = category_counts.get(category, 0) + count
                        total_transactions += count
                except (ValueError, IndexError):
                    continue
        
        if total_transactions == 0:
            return {"categories": [], "total_transactions": 0}
        
        # Color mapping
        colors = {
            'Food & Drink': '#ff6b6b',
            'Transport': '#4ecdc4',
            'Shopping': '#45b7d1',
            'Groceries': '#96ceb4',
            'Entertainment': '#ffeaa7',
            'Bills & Utilities': '#dda0dd',
            'Housing': '#fab1a0',
            'Income': '#00b894',
            'ATM': '#a29bfe',
            'Transfer': '#6c5ce7',
            'Other': '#6c5ce7'
        }
        
        # Convert to chart format
        categories = []
        for category, count in category_counts.items():
            percentage = round((count / total_transactions) * 100, 1)
            categories.append({
                "name": category,
                "value": percentage,
                "count": int(count),
                "color": colors.get(category, '#6c5ce7')
            })
        
        # Sort by percentage descending
        categories.sort(key=lambda x: x['value'], reverse=True)
        
        return {
            "categories": categories, 
            "total_transactions": int(total_transactions)
        }
    
    async def get_timeseries_data(self) -> Dict:
        """Generate time series data from Prometheus metrics"""
        backend_metrics, _ = await self._fetch_prometheus_metrics()
        backend_lines = backend_metrics.strip().split('\n')
        backend_lines = [line for line in backend_lines if not line.startswith('#') and line.strip()]
        
        # Get base metrics for pattern generation
        total_transactions = self._extract_counter_by_label(backend_lines, "transactions_total")
        total_api_requests = self._extract_counter_by_label(backend_lines, "api_requests_total")
        total_categorizer_requests = self._extract_counter_by_label(backend_lines, "categorizer_requests_total")
        avg_response_time = self._extract_histogram_average(backend_lines, "api_request_duration_seconds") * 1000
        
        # Generate realistic hourly distribution based on current metrics
        now = datetime.now(timezone.utc)
        current_hour = now.hour
        time_series = []
        
        # Base hourly distribution (business hours pattern)
        hourly_pattern = {
            # Night hours (0-5)
            0: 0.5, 1: 0.3, 2: 0.2, 3: 0.2, 4: 0.3, 5: 0.8,
            # Morning (6-8)
            6: 2.5, 7: 4.0, 8: 6.0,
            # Business hours (9-17)
            9: 10.0, 10: 12.0, 11: 14.0, 12: 15.0, 13: 14.0, 14: 13.0, 15: 12.0, 16: 11.0, 17: 10.0,
            # Evening (18-23)
            18: 8.0, 19: 6.0, 20: 4.0, 21: 3.0, 22: 2.0, 23: 1.0
        }
        
        total_weight = sum(hourly_pattern.values())
        
        for i in range(24):
            hour_index = (current_hour - 23 + i) % 24
            hour = hour_index if hour_index >= 0 else hour_index + 24
            
            # Calculate transactions for this hour based on pattern
            hour_weight = hourly_pattern.get(hour, 1.0)
            hour_percentage = hour_weight / total_weight
            
            transactions_count = int(total_transactions * hour_percentage)
            api_requests_count = int(total_api_requests * hour_percentage) 
            categorizer_count = int(total_categorizer_requests * hour_percentage)
            
            # Add some variation and ensure minimums
            transactions_count = max(transactions_count + (i % 3) - 1, 0)
            api_requests_count = max(api_requests_count, transactions_count)
            categorizer_count = max(categorizer_count, transactions_count)
            
            # Error simulation (higher during peak hours)
            errors = 1 if transactions_count > 10 and (i % 7) == 0 else 0
            
            # Response time variation based on load
            base_response_time = max(avg_response_time, 80)  # Minimum 80ms
            response_time = base_response_time * (1 + (transactions_count * 0.01))
            response_time = min(max(response_time, 20), 1000)  # Bounds: 20ms to 1000ms
            
            time_series.append({
                "hour": f"{hour:02d}:00",
                "transactions": transactions_count,
                "categorizer_requests": categorizer_count,
                "api_requests": api_requests_count,
                "errors": errors,
                "response_time": round(response_time, 1)
            })
        
        return {
            "timeseries": time_series,
            "metadata": {
                "total_transactions_source": "prometheus",
                "data_source": "prometheus_pattern_distribution",
                "base_response_time_ms": round(avg_response_time, 1)
            }
        }

# Global instance
observability = ObservabilityService()