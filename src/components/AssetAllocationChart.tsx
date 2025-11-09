import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from "recharts";
import { PieChart as PieChartIcon, AlertCircle } from "lucide-react";
import * as api from "@/services/api";
import { formatCurrency, formatPercentage } from "@/lib/formatters";
import { useToast } from "@/hooks/use-toast";

const COLORS = [
  '#3b82f6', // blue
  '#10b981', // green
  '#8b5cf6', // purple
  '#f59e0b', // yellow
  '#6366f1', // indigo
  '#ec4899', // pink
  '#14b8a6', // teal
  '#f97316', // orange
];

const getTypeLabel = (type: string) => {
  const labels: Record<string, string> = {
    stock: 'Stocks',
    etf: 'ETFs',
    crypto: 'Crypto',
    bond: 'Bonds',
    mutual_fund: 'Mutual Funds',
    other: 'Other',
  };
  return labels[type] || type;
};

export const AssetAllocationChart = () => {
  const { toast } = useToast();

  const { data: portfolio, isLoading, error } = useQuery({
    queryKey: ['portfolio-summary'],
    queryFn: () => api.getPortfolioSummary('USD'),
    onError: (err: Error) => {
      toast({
        title: "Error loading allocation",
        description: err.message || "Failed to load asset allocation",
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

  if (error || !portfolio) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <AlertCircle className="h-5 w-5 text-destructive" />
            Asset Allocation
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              {error?.message || "Failed to load asset allocation"}
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>
    );
  }

  if (portfolio.total_investments === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <PieChartIcon className="h-6 w-6 text-primary" />
            Asset Allocation
          </CardTitle>
          <CardDescription>
            Portfolio distribution by asset type
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Alert>
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              No investments yet. Add investments to see your asset allocation.
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>
    );
  }

  // Prepare chart data
  const chartData = Object.entries(portfolio.by_type).map(([type, data]: [string, any]) => ({
    name: getTypeLabel(type),
    value: data.total_value,
    count: data.count,
    percentage: (data.total_value / portfolio.total_value) * 100,
  }));

  // Custom label for pie chart
  const renderCustomLabel = (entry: any) => {
    return `${entry.percentage.toFixed(1)}%`;
  };

  // Custom tooltip
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-white p-3 border rounded-lg shadow-lg">
          <p className="font-semibold">{data.name}</p>
          <p className="text-sm text-muted-foreground">
            {data.count} {data.count === 1 ? 'investment' : 'investments'}
          </p>
          <p className="text-sm font-semibold text-primary">
            {formatCurrency(data.value)}
          </p>
          <p className="text-xs text-muted-foreground">
            {formatPercentage(data.percentage / 100)} of portfolio
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <PieChartIcon className="h-6 w-6 text-primary" />
          Asset Allocation
        </CardTitle>
        <CardDescription>
          Portfolio distribution by asset type
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Pie Chart */}
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={chartData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={renderCustomLabel}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip content={<CustomTooltip />} />
              <Legend 
                verticalAlign="bottom" 
                height={36}
                formatter={(value, entry: any) => {
                  const data = chartData.find(d => d.name === value);
                  return `${value} (${data?.count || 0})`;
                }}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Allocation Breakdown */}
        <div className="space-y-3">
          <h4 className="font-semibold text-sm">Allocation Breakdown</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {chartData.map((item, index) => (
              <div key={item.name} className="flex items-center justify-between p-3 border rounded-lg">
                <div className="flex items-center gap-3">
                  <div
                    className="w-4 h-4 rounded-full"
                    style={{ backgroundColor: COLORS[index % COLORS.length] }}
                  />
                  <div>
                    <p className="font-medium text-sm">{item.name}</p>
                    <p className="text-xs text-muted-foreground">
                      {item.count} {item.count === 1 ? 'asset' : 'assets'}
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="font-semibold text-sm">{formatCurrency(item.value)}</p>
                  <Badge variant="outline" className="text-xs">
                    {item.percentage.toFixed(1)}%
                  </Badge>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Diversification Score */}
        <div className="p-4 bg-muted rounded-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium">Diversification Score</p>
              <p className="text-xs text-muted-foreground">
                Based on number of asset types
              </p>
            </div>
            <div className="text-right">
              <p className="text-2xl font-bold text-primary">
                {Object.keys(portfolio.by_type).length}/6
              </p>
              <p className="text-xs text-muted-foreground">
                {Object.keys(portfolio.by_type).length === 1 && 'Low diversification'}
                {Object.keys(portfolio.by_type).length === 2 && 'Moderate diversification'}
                {Object.keys(portfolio.by_type).length >= 3 && Object.keys(portfolio.by_type).length < 5 && 'Good diversification'}
                {Object.keys(portfolio.by_type).length >= 5 && 'Excellent diversification'}
              </p>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

