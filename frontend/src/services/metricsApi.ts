import { api } from './api';

export interface MetricsData {
  timestamp: string;
  backend: {
    transactions_total: number;
    topups_triggered_total: number;
    api_requests_total: number;
    categorizer_requests_success: number;
    categorizer_requests_failure: number;
    accounts_count: number;
    total_balance: number;
    avg_response_time_ms: number;
  };
  categorizer: {
    categorization_requests_total: number;
    categorization_errors_total: number;
    http_requests_total: number;
  };
  summary: {
    total_transactions: number;
    total_accounts: number;
    total_balance: number;
    total_requests: number;
    avg_response_time_ms: number;
    categorizer_success_rate: number;
    categorizer_error_rate: number;
    system_health: 'healthy' | 'degraded';
  };
}

export interface TimeSeriesDataPoint {
  hour: string;
  transactions: number;
  categorizer_requests: number;
  api_requests: number;
  errors: number;
  response_time: number;
}

export interface CategoryBreakdown {
  name: string;
  value: number;
  color: string;
}

export class MetricsApiService {
  /**
   * Fetch current system metrics
   */
  static async getMetrics(): Promise<MetricsData> {
    try {
      const response = await api.get('/api/metrics');
      console.log('Metrics API response:', response.data);
      
      // Check if response has error property
      if (response.data?.error) {
        console.error('API returned error:', response.data.error);
        throw new Error(`API Error: ${response.data.error}`);
      }
      
      return response.data;
    } catch (error) {
      console.error('Failed to fetch metrics:', error);
      // Re-throw the error so the component can handle it properly
      throw error;
    }
  }

  /**
   * Get real time series data from backend
   */
  static async getTimeSeriesData(): Promise<TimeSeriesDataPoint[]> {
    try {
      const response = await api.get('/api/metrics/timeseries');
      return response.data.timeseries || [];
    } catch (error) {
      console.error('Failed to fetch time series data:', error);
      // Return empty array on error
      return [];
    }
  }

  /**
   * Get real category breakdown data from backend
   */
  static async getCategoryBreakdown(): Promise<CategoryBreakdown[]> {
    try {
      const response = await api.get('/api/metrics/categories');
      return response.data.categories || [];
    } catch (error) {
      console.error('Failed to fetch category breakdown:', error);
      // Return empty array on error - component will handle gracefully
      return [];
    }
  }

  /**
   * Calculate average response time from time series data
   */
  static calculateAverageResponseTime(timeSeriesData: TimeSeriesDataPoint[]): number {
    if (timeSeriesData.length === 0) return 0;
    
    const total = timeSeriesData.reduce((sum, point) => sum + point.response_time, 0);
    return total / timeSeriesData.length;
  }
}

export default MetricsApiService;