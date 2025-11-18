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
    categorizer_success_rate: number;
    categorizer_error_rate: number;
    system_health: 'healthy' | 'degraded';
  };
}

export interface TimeSeriesDataPoint {
  hour: string;
  transactions: number;
  categorizer_requests: number;
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
   * Generate mock time series data for charts
   * In a real implementation, this would fetch historical data
   */
  static generateTimeSeriesData(metrics: MetricsData): TimeSeriesDataPoint[] {
    const currentHour = new Date().getHours();
    
    return Array.from({ length: 24 }, (_, i) => {
      const hourIndex = (currentHour - 23 + i) % 24;
      const hour = hourIndex < 0 ? hourIndex + 24 : hourIndex;
      
      // Generate realistic data based on current metrics (with safe defaults)
      const baseTransactions = Math.floor((metrics?.summary?.total_transactions || 0) / 24);
      const baseCategorizer = Math.floor((metrics?.categorizer?.categorization_requests_total || 0) / 24);
      const baseErrors = Math.floor((metrics?.categorizer?.categorization_errors_total || 0) / 24);
      
      return {
        hour: `${hour.toString().padStart(2, '0')}:00`,
        transactions: Math.max(0, baseTransactions + Math.floor(Math.random() * 20 - 10)),
        categorizer_requests: Math.max(0, baseCategorizer + Math.floor(Math.random() * 15 - 7)),
        errors: Math.max(0, baseErrors + Math.floor(Math.random() * 3)),
        response_time: Math.random() * 200 + 50, // 50-250ms
      };
    });
  }

  /**
   * Get category breakdown data
   * In a real implementation, this would be fetched from the backend
   */
  static getCategoryBreakdown(): CategoryBreakdown[] {
    return [
      { name: 'Food & Drink', value: 25, color: '#ff6b6b' },
      { name: 'Transport', value: 18, color: '#4ecdc4' },
      { name: 'Shopping', value: 20, color: '#45b7d1' },
      { name: 'Groceries', value: 15, color: '#96ceb4' },
      { name: 'Entertainment', value: 8, color: '#ffeaa7' },
      { name: 'Bills & Utilities', value: 12, color: '#dda0dd' },
      { name: 'Housing', value: 6, color: '#fab1a0' },
      { name: 'Income', value: 3, color: '#00b894' },
      { name: 'ATM', value: 2, color: '#a29bfe' },
      { name: 'Other', value: 5, color: '#6c5ce7' },
    ];
  }

  /**
   * Calculate average response time from time series data
   */
  static calculateAverageResponseTime(timeSeriesData: TimeSeriesDataPoint[]): number {
    if (timeSeriesData.length === 0) return 0;
    
    const total = timeSeriesData.reduce((sum, point) => sum + point.response_time, 0);
    return total / timeSeriesData.length;
  }

  /**
   * Get system health status based on metrics
   */
  static getSystemHealth(metrics: MetricsData): {
    status: 'healthy' | 'degraded';
    issues: string[];
  } {
    const issues: string[] = [];
    
    if (metrics.summary.categorizer_success_rate < 95) {
      issues.push('Categorizer success rate below 95%');
    }
    
    if (metrics.categorizer.categorization_errors_total > 10) {
      issues.push('High error count in categorizer service');
    }
    
    return {
      status: issues.length === 0 ? 'healthy' : 'degraded',
      issues,
    };
  }
}

export default MetricsApiService;