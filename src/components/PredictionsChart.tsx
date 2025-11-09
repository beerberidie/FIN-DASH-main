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
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer,
  Area,
  AreaChart
} from "recharts";
import { AlertCircle, TrendingUp, Brain } from "lucide-react";
import * as api from "@/services/api";
import { formatCurrency } from "@/lib/formatters";
import { useToast } from "@/hooks/use-toast";

const getMethodBadge = (method: string) => {
  const colors: Record<string, string> = {
    moving_average: 'bg-blue-100 text-blue-800',
    linear_regression: 'bg-purple-100 text-purple-800',
    seasonal: 'bg-green-100 text-green-800',
  };
  
  const labels: Record<string, string> = {
    moving_average: 'Moving Average',
    linear_regression: 'Linear Regression',
    seasonal: 'Seasonal',
  };
  
  return {
    color: colors[method] || 'bg-gray-100 text-gray-800',
    label: labels[method] || method,
  };
};

export const PredictionsChart = () => {
  const { toast } = useToast();
  const [metric, setMetric] = useState('income');
  const [method, setMethod] = useState('moving_average');
  const [periodsAhead, setPeriodsAhead] = useState(3);

  const { data: predictions, isLoading, error } = useQuery({
    queryKey: ['predictions', metric, method, periodsAhead],
    queryFn: () => api.getPredictions(metric, periodsAhead, method),
    onError: (err: Error) => {
      toast({
        title: "Error loading predictions",
        description: err.message || "Failed to load prediction data",
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

  if (error || !predictions) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <AlertCircle className="h-5 w-5 text-destructive" />
            Financial Predictions
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              {error?.message || "Failed to load predictions"}
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>
    );
  }

  const methodInfo = getMethodBadge(predictions.method);

  // Prepare chart data with confidence intervals
  const chartData = predictions.predictions.map(pred => ({
    period: pred.period,
    predicted: pred.predicted_value,
    lower: pred.confidence_interval_low,
    upper: pred.confidence_interval_high,
  }));

  return (
    <Card>
      <CardHeader>
        <div className="flex items-start justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <Brain className="h-6 w-6 text-primary" />
              Financial Predictions
            </CardTitle>
            <CardDescription>
              AI-powered forecasts for your finances
            </CardDescription>
          </div>
          <Badge className={methodInfo.color}>
            {methodInfo.label}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Controls */}
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
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium">Method</label>
            <Select value={method} onValueChange={setMethod}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="moving_average">Moving Average</SelectItem>
                <SelectItem value="linear_regression">Linear Regression</SelectItem>
                <SelectItem value="seasonal">Seasonal</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium">Periods Ahead</label>
            <Select value={periodsAhead.toString()} onValueChange={(v) => setPeriodsAhead(parseInt(v))}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="3">3 months</SelectItem>
                <SelectItem value="6">6 months</SelectItem>
                <SelectItem value="12">12 months</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        {/* Accuracy Badge */}
        {predictions.historical_accuracy !== undefined && predictions.historical_accuracy !== null && (
          <Alert>
            <TrendingUp className="h-4 w-4" />
            <AlertDescription>
              <span className="font-semibold">Historical Accuracy: </span>
              <span className="text-primary font-bold">
                {(predictions.historical_accuracy * 100).toFixed(1)}%
              </span>
              <span className="text-muted-foreground ml-2">
                (based on past predictions)
              </span>
            </AlertDescription>
          </Alert>
        )}

        {/* Predictions Chart */}
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={chartData}>
              <defs>
                <linearGradient id="colorPredicted" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8}/>
                  <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.1}/>
                </linearGradient>
                <linearGradient id="colorConfidence" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#94a3b8" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#94a3b8" stopOpacity={0.05}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="period" 
                tick={{ fontSize: 12 }}
              />
              <YAxis 
                tick={{ fontSize: 12 }}
                tickFormatter={(value) => `R${(value / 1000).toFixed(0)}k`}
              />
              <Tooltip 
                formatter={(value: number, name: string) => {
                  const labels: Record<string, string> = {
                    predicted: 'Predicted',
                    lower: 'Lower Bound',
                    upper: 'Upper Bound',
                  };
                  return [formatCurrency(value), labels[name] || name];
                }}
                labelStyle={{ color: '#000' }}
              />
              <Legend />
              
              {/* Confidence Interval Area */}
              <Area
                type="monotone"
                dataKey="upper"
                stroke="none"
                fill="url(#colorConfidence)"
                name="Confidence Range"
              />
              <Area
                type="monotone"
                dataKey="lower"
                stroke="none"
                fill="#fff"
                name=""
              />
              
              {/* Predicted Line */}
              <Line 
                type="monotone" 
                dataKey="predicted" 
                stroke="#3b82f6" 
                strokeWidth={3}
                name="Predicted Value"
                dot={{ r: 5, fill: '#3b82f6' }}
                activeDot={{ r: 7 }}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Predictions Table */}
        <div className="space-y-2">
          <h4 className="font-semibold text-sm">Detailed Predictions</h4>
          <div className="border rounded-lg overflow-hidden">
            <table className="w-full">
              <thead className="bg-muted">
                <tr>
                  <th className="text-left p-3 text-sm font-medium">Period</th>
                  <th className="text-right p-3 text-sm font-medium">Predicted</th>
                  <th className="text-right p-3 text-sm font-medium">Range</th>
                  <th className="text-right p-3 text-sm font-medium">Confidence</th>
                </tr>
              </thead>
              <tbody>
                {predictions.predictions.map((pred, idx) => (
                  <tr key={idx} className="border-t">
                    <td className="p-3 text-sm font-medium">{pred.period}</td>
                    <td className="p-3 text-sm text-right font-bold">
                      {formatCurrency(pred.predicted_value)}
                    </td>
                    <td className="p-3 text-sm text-right text-muted-foreground">
                      {formatCurrency(pred.confidence_interval_low)} - {formatCurrency(pred.confidence_interval_high)}
                    </td>
                    <td className="p-3 text-sm text-right">
                      <Badge variant="outline">
                        {(pred.confidence_level * 100).toFixed(0)}%
                      </Badge>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Disclaimer */}
        <Alert>
          <AlertCircle className="h-4 w-4" />
          <AlertDescription className="text-xs">
            <strong>Note:</strong> Predictions are based on historical data and statistical models. 
            Actual results may vary due to unforeseen circumstances. Use these forecasts as guidance, 
            not guarantees.
          </AlertDescription>
        </Alert>
      </CardContent>
    </Card>
  );
};

