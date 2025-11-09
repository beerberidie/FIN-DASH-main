import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { 
  TrendingUp, 
  TrendingDown, 
  DollarSign, 
  PieChart, 
  AlertCircle,
  Target,
  Award
} from "lucide-react";
import * as api from "@/services/api";
import { formatCurrency, formatPercentage } from "@/lib/formatters";
import { useToast } from "@/hooks/use-toast";

const StatCard = ({ 
  title, 
  value, 
  subtitle, 
  icon, 
  trend 
}: { 
  title: string; 
  value: string; 
  subtitle: string; 
  icon: React.ReactNode;
  trend?: 'up' | 'down' | 'neutral';
}) => {
  const getTrendColor = () => {
    if (trend === 'up') return 'text-green-600';
    if (trend === 'down') return 'text-red-600';
    return 'text-gray-600';
  };

  return (
    <Card>
      <CardContent className="pt-6">
        <div className="flex items-start justify-between">
          <div className="space-y-2 flex-1">
            <p className="text-sm font-medium text-muted-foreground">{title}</p>
            <p className="text-3xl font-bold">{value}</p>
            <div className="flex items-center gap-1">
              {trend === 'up' && <TrendingUp className="h-4 w-4 text-green-600" />}
              {trend === 'down' && <TrendingDown className="h-4 w-4 text-red-600" />}
              <span className={`text-sm font-medium ${getTrendColor()}`}>
                {subtitle}
              </span>
            </div>
          </div>
          <div className="p-3 rounded-xl bg-primary/10">
            {icon}
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export const PortfolioDashboard = () => {
  const { toast } = useToast();

  const { data: portfolio, isLoading, error } = useQuery({
    queryKey: ['portfolio-summary'],
    queryFn: () => api.getPortfolioSummary('USD'),
    refetchInterval: 60000, // Refetch every minute
    onError: (err: Error) => {
      toast({
        title: "Error loading portfolio",
        description: err.message || "Failed to load portfolio data",
        variant: "destructive",
      });
    },
  });

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <Skeleton key={i} className="h-32" />
          ))}
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Skeleton className="h-64" />
          <Skeleton className="h-64" />
        </div>
      </div>
    );
  }

  if (error || !portfolio) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <AlertCircle className="h-5 w-5 text-destructive" />
            Portfolio Dashboard
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              {error?.message || "Failed to load portfolio data"}
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>
    );
  }

  const profitLossTrend = portfolio.total_profit_loss >= 0 ? 'up' : 'down';

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Value"
          value={formatCurrency(portfolio.total_value)}
          subtitle={`${portfolio.total_investments} investments`}
          icon={<DollarSign className="h-6 w-6 text-primary" />}
        />
        <StatCard
          title="Total Cost"
          value={formatCurrency(portfolio.total_cost)}
          subtitle="Initial investment"
          icon={<Target className="h-6 w-6 text-blue-600" />}
        />
        <StatCard
          title="Profit/Loss"
          value={formatCurrency(portfolio.total_profit_loss)}
          subtitle={formatPercentage(portfolio.total_profit_loss_percentage / 100)}
          icon={profitLossTrend === 'up' ? 
            <TrendingUp className="h-6 w-6 text-green-600" /> : 
            <TrendingDown className="h-6 w-6 text-red-600" />
          }
          trend={profitLossTrend}
        />
        <StatCard
          title="Asset Types"
          value={Object.keys(portfolio.by_type).length.toString()}
          subtitle="Diversification"
          icon={<PieChart className="h-6 w-6 text-purple-600" />}
        />
      </div>

      {/* Asset Allocation */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <PieChart className="h-5 w-5 text-primary" />
            Asset Allocation
          </CardTitle>
          <CardDescription>
            Portfolio breakdown by investment type
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {Object.entries(portfolio.by_type).map(([type, data]: [string, any]) => {
              const percentage = (data.total_value / portfolio.total_value) * 100;
              
              return (
                <div key={type} className="space-y-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Badge variant="outline" className="capitalize">
                        {type}
                      </Badge>
                      <span className="text-sm text-muted-foreground">
                        {data.count} {data.count === 1 ? 'investment' : 'investments'}
                      </span>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-semibold">{formatCurrency(data.total_value)}</p>
                      <p className="text-xs text-muted-foreground">{percentage.toFixed(1)}%</p>
                    </div>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-primary h-2 rounded-full transition-all"
                      style={{ width: `${percentage}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Top & Worst Performers */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Performers */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Award className="h-5 w-5 text-green-600" />
              Top Performers
            </CardTitle>
            <CardDescription>
              Best performing investments
            </CardDescription>
          </CardHeader>
          <CardContent>
            {portfolio.top_performers.length > 0 ? (
              <div className="space-y-3">
                {portfolio.top_performers.map((investment: any, idx: number) => (
                  <div key={idx} className="flex items-center justify-between p-3 border rounded-lg">
                    <div>
                      <p className="font-semibold">{investment.symbol}</p>
                      <p className="text-sm text-muted-foreground">{investment.name}</p>
                    </div>
                    <div className="text-right">
                      <div className="flex items-center gap-1 text-green-600">
                        <TrendingUp className="h-4 w-4" />
                        <span className="font-semibold">
                          +{formatPercentage(investment.profit_loss_percentage / 100)}
                        </span>
                      </div>
                      <p className="text-sm text-muted-foreground">
                        +{formatCurrency(investment.profit_loss)}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <Alert>
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>
                  No profitable investments yet
                </AlertDescription>
              </Alert>
            )}
          </CardContent>
        </Card>

        {/* Worst Performers */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingDown className="h-5 w-5 text-red-600" />
              Worst Performers
            </CardTitle>
            <CardDescription>
              Underperforming investments
            </CardDescription>
          </CardHeader>
          <CardContent>
            {portfolio.worst_performers.length > 0 ? (
              <div className="space-y-3">
                {portfolio.worst_performers.map((investment: any, idx: number) => (
                  <div key={idx} className="flex items-center justify-between p-3 border rounded-lg">
                    <div>
                      <p className="font-semibold">{investment.symbol}</p>
                      <p className="text-sm text-muted-foreground">{investment.name}</p>
                    </div>
                    <div className="text-right">
                      <div className="flex items-center gap-1 text-red-600">
                        <TrendingDown className="h-4 w-4" />
                        <span className="font-semibold">
                          {formatPercentage(investment.profit_loss_percentage / 100)}
                        </span>
                      </div>
                      <p className="text-sm text-muted-foreground">
                        {formatCurrency(investment.profit_loss)}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <Alert>
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>
                  No underperforming investments
                </AlertDescription>
              </Alert>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

