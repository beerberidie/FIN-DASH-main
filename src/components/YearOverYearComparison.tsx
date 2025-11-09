import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { 
  BarChart,
  Bar,
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer,
  Cell
} from "recharts";
import { TrendingUp, TrendingDown, AlertCircle, ArrowUpRight, ArrowDownRight } from "lucide-react";
import * as api from "@/services/api";
import { formatCurrency, formatPercentage } from "@/lib/formatters";
import { useToast } from "@/hooks/use-toast";

const ComparisonCard = ({ 
  comparison, 
  icon 
}: { 
  comparison: api.YoYComparison; 
  icon: React.ReactNode;
}) => {
  const isPositive = comparison.change_percentage >= 0;
  const isImprovement = comparison.is_improvement;

  return (
    <Card>
      <CardContent className="pt-6">
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="p-2 rounded-lg bg-primary/10">
                {icon}
              </div>
              <h3 className="font-semibold capitalize">{comparison.metric}</h3>
            </div>
            <Badge variant={isImprovement ? "default" : "destructive"}>
              {isImprovement ? (
                <ArrowUpRight className="h-3 w-3 mr-1" />
              ) : (
                <ArrowDownRight className="h-3 w-3 mr-1" />
              )}
              {isPositive ? '+' : ''}{formatPercentage(comparison.change_percentage / 100)}
            </Badge>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-xs text-muted-foreground">{comparison.previous_year}</p>
              <p className="text-xl font-bold">{formatCurrency(comparison.previous_value)}</p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground">{comparison.current_year}</p>
              <p className="text-xl font-bold">{formatCurrency(comparison.current_value)}</p>
            </div>
          </div>

          <div className="space-y-1">
            <div className="flex items-center justify-between text-sm">
              <span className="text-muted-foreground">Change</span>
              <span className={`font-semibold ${isPositive ? 'text-green-600' : 'text-red-600'}`}>
                {isPositive ? '+' : ''}{formatCurrency(comparison.change_amount)}
              </span>
            </div>
            <Progress 
              value={Math.abs(comparison.change_percentage)} 
              className="h-2"
              // @ts-ignore
              indicatorClassName={isImprovement ? 'bg-green-500' : 'bg-red-500'}
            />
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export const YearOverYearComparison = () => {
  const { toast } = useToast();

  const { data: yoyData, isLoading, error } = useQuery({
    queryKey: ['yoy-comparison'],
    queryFn: () => api.getYoYComparison(),
    onError: (err: Error) => {
      toast({
        title: "Error loading YoY comparison",
        description: err.message || "Failed to load year-over-year data",
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
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Skeleton className="h-48" />
            <Skeleton className="h-48" />
            <Skeleton className="h-48" />
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error || !yoyData) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <AlertCircle className="h-5 w-5 text-destructive" />
            Year-over-Year Comparison
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              {error?.message || "Failed to load year-over-year comparison"}
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>
    );
  }

  const chartData = [
    {
      category: 'Income',
      [yoyData.previous_year]: yoyData.income_comparison.previous_value,
      [yoyData.current_year]: yoyData.income_comparison.current_value,
    },
    {
      category: 'Expenses',
      [yoyData.previous_year]: yoyData.expense_comparison.previous_value,
      [yoyData.current_year]: yoyData.expense_comparison.current_value,
    },
    {
      category: 'Net Income',
      [yoyData.previous_year]: yoyData.net_comparison.previous_value,
      [yoyData.current_year]: yoyData.net_comparison.current_value,
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header Card */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-6 w-6 text-primary" />
            Year-over-Year Comparison
          </CardTitle>
          <CardDescription>
            Comparing {yoyData.current_year} vs {yoyData.previous_year}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {/* Comparison Chart */}
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="category" />
                <YAxis tickFormatter={(value) => `R${(value / 1000).toFixed(0)}k`} />
                <Tooltip 
                  formatter={(value: number) => formatCurrency(value)}
                  labelStyle={{ color: '#000' }}
                />
                <Legend />
                <Bar dataKey={yoyData.previous_year} fill="#94a3b8" name={`${yoyData.previous_year}`} />
                <Bar dataKey={yoyData.current_year} fill="#3b82f6" name={`${yoyData.current_year}`} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      {/* Detailed Comparisons */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <ComparisonCard 
          comparison={yoyData.income_comparison}
          icon={<TrendingUp className="h-5 w-5 text-green-600" />}
        />
        <ComparisonCard 
          comparison={yoyData.expense_comparison}
          icon={<TrendingDown className="h-5 w-5 text-red-600" />}
        />
        <ComparisonCard 
          comparison={yoyData.net_comparison}
          icon={<TrendingUp className="h-5 w-5 text-blue-600" />}
        />
      </div>

      {/* Savings Rate Comparison */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Savings Rate Comparison</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-6">
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">{yoyData.previous_year}</span>
                <span className="text-2xl font-bold">{formatPercentage(yoyData.savings_rate_previous / 100)}</span>
              </div>
              <Progress value={yoyData.savings_rate_previous} className="h-2" />
            </div>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">{yoyData.current_year}</span>
                <span className="text-2xl font-bold">{formatPercentage(yoyData.savings_rate_current / 100)}</span>
              </div>
              <Progress value={yoyData.savings_rate_current} className="h-2" />
            </div>
          </div>
          <div className="mt-4 text-center">
            <Badge variant={yoyData.savings_rate_current > yoyData.savings_rate_previous ? "default" : "destructive"}>
              {yoyData.savings_rate_current > yoyData.savings_rate_previous ? (
                <TrendingUp className="h-3 w-3 mr-1" />
              ) : (
                <TrendingDown className="h-3 w-3 mr-1" />
              )}
              {Math.abs(yoyData.savings_rate_current - yoyData.savings_rate_previous).toFixed(1)}% 
              {yoyData.savings_rate_current > yoyData.savings_rate_previous ? ' increase' : ' decrease'}
            </Badge>
          </div>
        </CardContent>
      </Card>

      {/* Category Comparisons */}
      {yoyData.category_comparisons && yoyData.category_comparisons.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Category Breakdown</CardTitle>
            <CardDescription>
              Spending changes by category
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {yoyData.category_comparisons.slice(0, 10).map((cat: any, idx: number) => (
                <div key={idx} className="flex items-center justify-between">
                  <span className="text-sm font-medium">{cat.category || 'Uncategorized'}</span>
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-muted-foreground">
                      {formatCurrency(cat.previous_value)} → {formatCurrency(cat.current_value)}
                    </span>
                    <Badge 
                      variant={cat.change_percentage >= 0 ? "destructive" : "default"}
                      className="min-w-[60px] justify-center"
                    >
                      {cat.change_percentage >= 0 ? '+' : ''}{cat.change_percentage.toFixed(0)}%
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

