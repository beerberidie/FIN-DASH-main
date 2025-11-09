import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Area,
  AreaChart
} from "recharts";
import { TrendingUp, AlertCircle } from "lucide-react";
import * as api from "@/services/api";
import { formatCurrency } from "@/lib/formatters";
import { useToast } from "@/hooks/use-toast";

export const PerformanceChart = () => {
  const { toast } = useToast();

  // Get portfolio performance data
  const { data: performanceData, isLoading, error } = useQuery({
    queryKey: ['portfolio-performance'],
    queryFn: () => api.getPortfolioPerformance('USD'),
    onError: (err: Error) => {
      toast({
        title: "Error loading performance",
        description: err.message || "Failed to load performance data",
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

  if (error || !performanceData) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <AlertCircle className="h-5 w-5 text-destructive" />
            Portfolio Performance
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              {error?.message || "Failed to load performance data"}
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>
    );
  }

  if (!performanceData || performanceData.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-6 w-6 text-primary" />
            Portfolio Performance
          </CardTitle>
          <CardDescription>
            Track your portfolio value over time
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Alert>
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              No performance data available yet. Add investments to track performance.
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>
    );
  }

  // Calculate overall performance metrics
  const totalCurrentValue = performanceData.reduce((sum: number, item: any) => sum + item.current_value, 0);
  const totalCost = performanceData.reduce((sum: number, item: any) => sum + item.total_cost, 0);
  const totalProfitLoss = totalCurrentValue - totalCost;
  const totalProfitLossPercentage = totalCost > 0 ? (totalProfitLoss / totalCost) * 100 : 0;

  // Prepare chart data - showing top 5 investments
  const chartData = performanceData
    .sort((a: any, b: any) => b.current_value - a.current_value)
    .slice(0, 5)
    .map((item: any) => ({
      name: item.symbol,
      value: item.current_value,
      cost: item.total_cost,
      profitLoss: item.profit_loss,
    }));

  return (
    <Card>
      <CardHeader>
        <div className="flex items-start justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-6 w-6 text-primary" />
              Portfolio Performance
            </CardTitle>
            <CardDescription>
              Top 5 investments by value
            </CardDescription>
          </div>
          <Badge variant={totalProfitLoss >= 0 ? "default" : "destructive"}>
            {totalProfitLoss >= 0 ? '+' : ''}{formatCurrency(totalProfitLoss)}
            ({totalProfitLoss >= 0 ? '+' : ''}{totalProfitLossPercentage.toFixed(2)}%)
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Summary Stats */}
        <div className="grid grid-cols-3 gap-4">
          <div className="space-y-1">
            <p className="text-sm text-muted-foreground">Total Value</p>
            <p className="text-2xl font-bold">{formatCurrency(totalCurrentValue)}</p>
          </div>
          <div className="space-y-1">
            <p className="text-sm text-muted-foreground">Total Cost</p>
            <p className="text-2xl font-bold">{formatCurrency(totalCost)}</p>
          </div>
          <div className="space-y-1">
            <p className="text-sm text-muted-foreground">Profit/Loss</p>
            <p className={`text-2xl font-bold ${totalProfitLoss >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {totalProfitLoss >= 0 ? '+' : ''}{formatCurrency(totalProfitLoss)}
            </p>
          </div>
        </div>

        {/* Chart */}
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={chartData}>
              <defs>
                <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8}/>
                  <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.1}/>
                </linearGradient>
                <linearGradient id="colorCost" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#94a3b8" stopOpacity={0.8}/>
                  <stop offset="95%" stopColor="#94a3b8" stopOpacity={0.1}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="name" 
                tick={{ fontSize: 12 }}
              />
              <YAxis 
                tick={{ fontSize: 12 }}
                tickFormatter={(value) => `$${(value / 1000).toFixed(0)}k`}
              />
              <Tooltip 
                formatter={(value: number, name: string) => {
                  const labels: Record<string, string> = {
                    value: 'Current Value',
                    cost: 'Total Cost',
                    profitLoss: 'Profit/Loss',
                  };
                  return [formatCurrency(value), labels[name] || name];
                }}
                labelStyle={{ color: '#000' }}
              />
              <Legend />
              <Area
                type="monotone"
                dataKey="cost"
                stroke="#94a3b8"
                fill="url(#colorCost)"
                name="Total Cost"
              />
              <Area
                type="monotone"
                dataKey="value"
                stroke="#3b82f6"
                fill="url(#colorValue)"
                name="Current Value"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Performance Table */}
        <div className="space-y-2">
          <h4 className="font-semibold text-sm">Top Investments</h4>
          <div className="border rounded-lg overflow-hidden">
            <table className="w-full">
              <thead className="bg-muted">
                <tr>
                  <th className="text-left p-3 text-sm font-medium">Symbol</th>
                  <th className="text-right p-3 text-sm font-medium">Value</th>
                  <th className="text-right p-3 text-sm font-medium">Cost</th>
                  <th className="text-right p-3 text-sm font-medium">P/L</th>
                </tr>
              </thead>
              <tbody>
                {performanceData.slice(0, 5).map((item: any, idx: number) => {
                  const isProfit = item.profit_loss >= 0;
                  return (
                    <tr key={idx} className="border-t">
                      <td className="p-3 text-sm font-medium">{item.symbol}</td>
                      <td className="p-3 text-sm text-right font-semibold">
                        {formatCurrency(item.current_value)}
                      </td>
                      <td className="p-3 text-sm text-right text-muted-foreground">
                        {formatCurrency(item.total_cost)}
                      </td>
                      <td className="p-3 text-sm text-right">
                        <span className={`font-semibold ${isProfit ? 'text-green-600' : 'text-red-600'}`}>
                          {isProfit ? '+' : ''}{formatCurrency(item.profit_loss)}
                        </span>
                        <span className="text-xs text-muted-foreground ml-1">
                          ({isProfit ? '+' : ''}{item.profit_loss_percentage.toFixed(2)}%)
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

