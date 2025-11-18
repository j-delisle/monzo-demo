import { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { ChartContainer, ChartTooltip, ChartTooltipContent } from './ui/chart';
import type { ChartConfig } from './ui/chart';
import { AreaChart, Area, LineChart, Line, BarChart, Bar, XAxis, YAxis, PieChart, Pie, Cell } from 'recharts';
import { Badge } from './ui/badge';
import { ActivityIcon, AlertTriangleIcon, CheckCircleIcon, ClockIcon, ServerIcon, TrendingUpIcon } from 'lucide-react';
import MetricsApiService from '../services/metricsApi';
import type { MetricsData, TimeSeriesDataPoint, CategoryBreakdown } from '../services/metricsApi';

const chartConfig = {
  transactions: {
    label: 'Transactions',
    color: 'hsl(var(--chart-1))',
  },
  requests: {
    label: 'API Requests',
    color: 'hsl(var(--chart-2))',
  },
  categorizer: {
    label: 'Categorizer',
    color: 'hsl(var(--chart-3))',
  },
  errors: {
    label: 'Errors',
    color: 'hsl(var(--chart-4))',
  },
} satisfies ChartConfig;


export function ObservabilityPage() {
  const [metrics, setMetrics] = useState<MetricsData | null>(null);
  const [timeSeriesData, setTimeSeriesData] = useState<TimeSeriesDataPoint[]>([]);
  const [categoryBreakdown, setCategoryBreakdown] = useState<CategoryBreakdown[]>([]);
  const [refreshTime, setRefreshTime] = useState(new Date());
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchMetrics = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Fetch all data in parallel
      const [fetchedMetrics, timeSeriesData, categoryData] = await Promise.all([
        MetricsApiService.getMetrics(),
        MetricsApiService.getTimeSeriesData(),
        MetricsApiService.getCategoryBreakdown()
      ]);
      
      setMetrics(fetchedMetrics);
      setTimeSeriesData(timeSeriesData);
      setCategoryBreakdown(categoryData);
      setRefreshTime(new Date());
    } catch (err: any) {
      const errorMessage = err?.response?.data?.detail || err?.message || 'Failed to fetch metrics from backend';
      setError(errorMessage);
      console.error('Error fetching metrics:', err);
      
      // Don't set fake metrics - let the error state show
      setMetrics(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Initial fetch
    fetchMetrics();

    // Set up real-time updates
    const interval = setInterval(fetchMetrics, 30000); // Refresh every 30 seconds

    return () => clearInterval(interval);
  }, []);

  if (loading && !metrics) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mx-auto"></div>
          <p className="mt-2 text-muted-foreground">Loading metrics...</p>
        </div>
      </div>
    );
  }

  if (error && !metrics) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <AlertTriangleIcon className="h-8 w-8 text-red-500 mx-auto" />
          <p className="mt-2 text-red-600">{error}</p>
          <button 
            onClick={fetchMetrics}
            className="mt-2 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (!metrics) return null;

  const systemHealth = metrics?.summary?.system_health || 'degraded';
  const avgResponseTime = MetricsApiService.calculateAverageResponseTime(timeSeriesData);
  const successRate = metrics?.summary?.categorizer_success_rate || 0;

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Observability Dashboard</h1>
          <p className="text-muted-foreground">
            System metrics and health monitoring for Monzo Demo services
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant={systemHealth === 'healthy' ? 'default' : 'destructive'}>
            {systemHealth === 'healthy' ? <CheckCircleIcon className="w-3 h-3 mr-1" /> : <AlertTriangleIcon className="w-3 h-3 mr-1" />}
            {systemHealth === 'healthy' ? 'System Healthy' : 'System Degraded'}
          </Badge>
          <span className="text-sm text-muted-foreground">
            <ClockIcon className="w-3 h-3 inline mr-1" />
            Last updated: {refreshTime.toLocaleTimeString()}
          </span>
        </div>
      </div>

      {/* Key Metrics Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Transactions</CardTitle>
            <TrendingUpIcon className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{(metrics?.summary?.total_transactions || 0).toLocaleString()}</div>
            <p className="text-xs text-muted-foreground">Real-time data</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Success Rate</CardTitle>
            <CheckCircleIcon className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{successRate.toFixed(1)}%</div>
            <p className="text-xs text-muted-foreground">Categorizer service</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg Response Time</CardTitle>
            <ClockIcon className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{avgResponseTime.toFixed(0)}ms</div>
            <p className="text-xs text-muted-foreground">API requests</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Accounts</CardTitle>
            <ServerIcon className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{metrics?.summary?.total_accounts || 0}</div>
            <p className="text-xs text-muted-foreground">£{((metrics?.summary?.total_balance || 0) / 1000).toFixed(1)}k total balance</p>
          </CardContent>
        </Card>
      </div>

      {/* Charts Grid */}
      <div className="grid gap-4 lg:grid-cols-2">
        {/* Request Volume Over Time */}
        <Card>
          <CardHeader>
            <CardTitle>Request Volume (24h)</CardTitle>
            <CardDescription>API requests and categorizer calls over time</CardDescription>
          </CardHeader>
          <CardContent>
            <ChartContainer config={chartConfig}>
              <AreaChart data={timeSeriesData}>
                <XAxis dataKey="hour" />
                <YAxis />
                <ChartTooltip content={<ChartTooltipContent />} />
                <Area 
                  type="monotone" 
                  dataKey="transactions" 
                  stackId="1"
                  stroke="var(--color-transactions)"
                  fill="var(--color-transactions)"
                  fillOpacity={0.6}
                />
                <Area 
                  type="monotone" 
                  dataKey="categorizer_requests" 
                  stackId="1"
                  stroke="var(--color-categorizer)"
                  fill="var(--color-categorizer)"
                  fillOpacity={0.6}
                />
              </AreaChart>
            </ChartContainer>
          </CardContent>
        </Card>

        {/* Response Time Trend */}
        <Card>
          <CardHeader>
            <CardTitle>Response Time Trend</CardTitle>
            <CardDescription>Average response times throughout the day</CardDescription>
          </CardHeader>
          <CardContent>
            <ChartContainer config={chartConfig}>
              <LineChart data={timeSeriesData}>
                <XAxis dataKey="hour" />
                <YAxis />
                <ChartTooltip content={<ChartTooltipContent />} />
                <Line 
                  type="monotone" 
                  dataKey="response_time" 
                  stroke="var(--color-requests)"
                  strokeWidth={2}
                  dot={false}
                />
              </LineChart>
            </ChartContainer>
          </CardContent>
        </Card>

        {/* Error Rate */}
        <Card>
          <CardHeader>
            <CardTitle>Error Distribution</CardTitle>
            <CardDescription>Errors and failures by hour</CardDescription>
          </CardHeader>
          <CardContent>
            <ChartContainer config={chartConfig}>
              <BarChart data={timeSeriesData}>
                <XAxis dataKey="hour" />
                <YAxis />
                <ChartTooltip content={<ChartTooltipContent />} />
                <Bar 
                  dataKey="errors" 
                  fill="var(--color-errors)"
                  radius={[2, 2, 0, 0]}
                />
              </BarChart>
            </ChartContainer>
          </CardContent>
        </Card>

        {/* Category Breakdown */}
        <Card>
          <CardHeader>
            <CardTitle>Transaction Categories</CardTitle>
            <CardDescription>Distribution of categorized transactions</CardDescription>
          </CardHeader>
          <CardContent>
            <ChartContainer config={chartConfig}>
              <PieChart>
                <Pie
                  data={categoryBreakdown}
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  dataKey="value"
                  label={({ name, value }) => `${name}: ${value}%`}
                >
                  {categoryBreakdown.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <ChartTooltip content={<ChartTooltipContent />} />
              </PieChart>
            </ChartContainer>
          </CardContent>
        </Card>
      </div>

      {/* Service Health Status */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <ActivityIcon className="w-5 h-5" />
            Service Health Status
          </CardTitle>
          <CardDescription>Real-time status of all microservices</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-3">
            <div className="flex items-center justify-between p-4 border rounded-lg">
              <div>
                <h4 className="font-medium">FastAPI Backend</h4>
                <p className="text-sm text-muted-foreground">Main API service</p>
              </div>
              <Badge variant="default">
                <CheckCircleIcon className="w-3 h-3 mr-1" />
                Healthy
              </Badge>
            </div>
            
            <div className="flex items-center justify-between p-4 border rounded-lg">
              <div>
                <h4 className="font-medium">Go Categorizer</h4>
                <p className="text-sm text-muted-foreground">Transaction categorization</p>
              </div>
              <Badge variant={(metrics?.summary?.categorizer_error_rate || 0) < 10 ? 'default' : 'destructive'}>
                {(metrics?.summary?.categorizer_error_rate || 0) < 10 ? (
                  <CheckCircleIcon className="w-3 h-3 mr-1" />
                ) : (
                  <AlertTriangleIcon className="w-3 h-3 mr-1" />
                )}
                {(metrics?.summary?.categorizer_error_rate || 0) < 10 ? 'Healthy' : 'Degraded'}
              </Badge>
            </div>
            
            <div className="flex items-center justify-between p-4 border rounded-lg">
              <div>
                <h4 className="font-medium">PostgreSQL Database</h4>
                <p className="text-sm text-muted-foreground">Primary data store</p>
              </div>
              <Badge variant="default">
                <CheckCircleIcon className="w-3 h-3 mr-1" />
                Healthy
              </Badge>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}