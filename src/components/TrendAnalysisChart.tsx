import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { 
  LineChart, 
  Line, 
  BarChart,
  Bar,
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer 
} from "recharts";
import { TrendingUp, TrendingDown, Minus, AlertCircle } from "lucide-react";
import * as api from "@/services/api";
import { formatCurrency } from "@/lib/formatters";
import { useToast } from "@/hooks/use-toast";

interface TrendAnalysisChartProps {
  defaultMetric?: string;
  defaultPeriodType?: string;
  showControls?: boolean;
}

const getTrendIcon = (direction: string) => {
  switch (direction.toLowerCase()) {
    case 'increasing':
      return <TrendingUp className="h-4 w-4 text-green-600" />;
    case 'decreasing':
      return <TrendingDown className="h-4 w-4 text-red-600" />;
    default:
      return <Minus className="h-4 w-4 text-gray-600" />;
  }
};

const getTrendColor = (direction: string) => {
  switch (direction.toLowerCase()) {
    case 'increasing':
      return 'text-green-600 bg-green-50 border-green-200';
    case 'decreasing':
      return 'text-red-600 bg-red-50 border-red-200';
    default:
      return 'text-gray-600 bg-gray-50 border-gray-200';
  }
};

export const TrendAnalysisChart = ({ 
  defaultMetric = 'income',
  defaultPeriodType = 'monthly',
  showControls = true 
}: TrendAnalysisChartProps) => {
  const { toast } = useToast();
  const [metric, setMetric] = useState(defaultMetric);
  const [periodType, setPeriodType] = useState(defaultPeriodType);
  const [chartType, setChartType] = useState<'line' | 'bar'>('line');

  const { data: trendData, isLoading, error } = useQuery({
    queryKey: ['trend-analysis', metric, periodType],
    queryFn: () => api.getTrendAnalysis(metric, periodType),
    onError: (err: Error) => {
      toast({
        title: "Error loading trend data",
        description: err.message || "Failed to load trend analysis",
        variant: "destructive",
      });
    },
  });

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <Skeleton className="h-6 w-48" />
          <Skeleton className="h-4 w-64 mt-2" />
        </CardHeader>
        <CardContent>
          <Skeleton className="h-80 w-full" />
        </CardContent>
      </Card>
    );
  }

  if (error || !trendData) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <AlertCircle className="h-5 w-5 text-destructive" />
            Trend Analysis
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              {error?.message || "Failed to load trend analysis"}
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>
    );
  }

  const chartData = trendData.data_points.map(point => ({
    period: point.period,
    value: point.value,
    count: point.count,
  }));

  return (
    <Card>
      <CardHeader>
        <div className="flex items-start justify-between">
          <div>
            <CardTitle className="capitalize">
              {metric} Trend Analysis
            </CardTitle>
            <CardDescription>
              {periodType.charAt(0).toUpperCase() + periodType.slice(1)} trends over time
            </CardDescription>
          </div>
          <div className="flex items-center gap-2">
            <Badge className={getTrendColor(trendData.trend_direction)}>
              {getTrendIcon(trendData.trend_direction)}
              <span className="ml-1">{trendData.trend_direction}</span>
            </Badge>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Controls */}
        {showControls && (
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Metric</label>
              <Select value={metric} onValueChange={setMetric}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="income">Income</SelectItem>
                  <SelectItem value="expenses">Expenses</SelectItem>
                  <SelectItem value="net">Net Income</SelectItem>
                  <SelectItem value="savings">Savings</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Period</label>
              <Select value={periodType} onValueChange={setPeriodType}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="monthly">Monthly</SelectItem>
                  <SelectItem value="quarterly">Quarterly</SelectItem>
                  <SelectItem value="yearly">Yearly</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Chart Type</label>
              <Select value={chartType} onValueChange={(v) => setChartType(v as 'line' | 'bar')}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="line">Line Chart</SelectItem>
                  <SelectItem value="bar">Bar Chart</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        )}

        {/* Statistics */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="space-y-1">
            <p className="text-sm text-muted-foreground">Total</p>
            <p className="text-2xl font-bold">{formatCurrency(trendData.total)}</p>
          </div>
          <div className="space-y-1">
            <p className="text-sm text-muted-foreground">Average</p>
            <p className="text-2xl font-bold">{formatCurrency(trendData.average)}</p>
          </div>
          <div className="space-y-1">
            <p className="text-sm text-muted-foreground">Trend</p>
            <p className={`text-2xl font-bold ${trendData.trend_percentage >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {trendData.trend_percentage >= 0 ? '+' : ''}{trendData.trend_percentage.toFixed(1)}%
            </p>
          </div>
          <div className="space-y-1">
            <p className="text-sm text-muted-foreground">Data Points</p>
            <p className="text-2xl font-bold">{trendData.data_points.length}</p>
          </div>
        </div>

        {/* Chart */}
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            {chartType === 'line' ? (
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="period" 
                  tick={{ fontSize: 12 }}
                  angle={-45}
                  textAnchor="end"
                  height={80}
                />
                <YAxis 
                  tick={{ fontSize: 12 }}
                  tickFormatter={(value) => `R${(value / 1000).toFixed(0)}k`}
                />
                <Tooltip 
                  formatter={(value: number) => [formatCurrency(value), metric.charAt(0).toUpperCase() + metric.slice(1)]}
                  labelStyle={{ color: '#000' }}
                />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="value" 
                  stroke="#8884d8" 
                  strokeWidth={2}
                  name={metric.charAt(0).toUpperCase() + metric.slice(1)}
                  dot={{ r: 4 }}
                  activeDot={{ r: 6 }}
                />
              </LineChart>
            ) : (
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="period" 
                  tick={{ fontSize: 12 }}
                  angle={-45}
                  textAnchor="end"
                  height={80}
                />
                <YAxis 
                  tick={{ fontSize: 12 }}
                  tickFormatter={(value) => `R${(value / 1000).toFixed(0)}k`}
                />
                <Tooltip 
                  formatter={(value: number) => [formatCurrency(value), metric.charAt(0).toUpperCase() + metric.slice(1)]}
                  labelStyle={{ color: '#000' }}
                />
                <Legend />
                <Bar 
                  dataKey="value" 
                  fill="#8884d8"
                  name={metric.charAt(0).toUpperCase() + metric.slice(1)}
                />
              </BarChart>
            )}
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
};

