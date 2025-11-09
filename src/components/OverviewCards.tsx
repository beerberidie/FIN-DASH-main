import { TrendingUp, TrendingDown, DollarSign, PiggyBank, Wallet, Loader2 } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { Card } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import api from "@/services/api";
import { formatCurrency, formatPercentage, getTrend } from "@/lib/formatters";
import { useToast } from "@/hooks/use-toast";

interface StatCardProps {
  title: string;
  value: string;
  change: string;
  trend: "up" | "down";
  icon: React.ReactNode;
  colorClass: string;
  isLoading?: boolean;
}

const StatCard = ({ title, value, change, trend, icon, colorClass, isLoading }: StatCardProps) => {
  if (isLoading) {
    return (
      <Card className="p-6 bg-gradient-card shadow-md border-border">
        <div className="flex items-start justify-between">
          <div className="space-y-2 flex-1">
            <Skeleton className="h-4 w-24" />
            <Skeleton className="h-8 w-32" />
            <Skeleton className="h-4 w-40" />
          </div>
          <Skeleton className="h-12 w-12 rounded-xl" />
        </div>
      </Card>
    );
  }

  return (
    <Card className="p-6 bg-gradient-card shadow-md hover:shadow-lg transition-all duration-300 border-border">
      <div className="flex items-start justify-between">
        <div className="space-y-2">
          <p className="text-sm font-medium text-muted-foreground">{title}</p>
          <p className="text-3xl font-bold text-foreground">{value}</p>
          <div className="flex items-center gap-1">
            {trend === "up" ? (
              <TrendingUp className="h-4 w-4 text-success" />
            ) : (
              <TrendingDown className="h-4 w-4 text-destructive" />
            )}
            <span className={`text-sm font-medium ${trend === "up" ? "text-success" : "text-destructive"}`}>
              {change}
            </span>
            <span className="text-sm text-muted-foreground">vs last month</span>
          </div>
        </div>
        <div className={`p-3 rounded-xl ${colorClass}`}>
          {icon}
        </div>
      </div>
    </Card>
  );
};

export const OverviewCards = () => {
  const { toast } = useToast();

  const { data: summary, isLoading, error } = useQuery({
    queryKey: ['summary'],
    queryFn: api.getSummary,
    refetchInterval: 30000, // Refetch every 30 seconds
    onError: (err: Error) => {
      toast({
        title: "Error loading dashboard",
        description: err.message || "Failed to load summary data",
        variant: "destructive",
      });
    },
  });

  // Show error state
  if (error && !isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="p-6 col-span-full bg-destructive/10 border-destructive">
          <p className="text-destructive font-medium">Failed to load dashboard data. Please check if the backend is running.</p>
        </Card>
      </div>
    );
  }

  // Calculate values from summary data
  const totalBalance = summary?.total_balance || 0;
  const savingsRate = summary?.savings_rate || 0;
  const monthlySurplus = summary?.monthly_surplus || 0;
  const netWorth = summary?.net_worth || 0;

  // Get month-over-month changes
  const balanceChange = summary?.month_over_month?.net_change || 0;
  const savingsChange = 0; // Not directly available, using 0 for now
  const surplusChange = summary?.month_over_month?.net_change || 0;
  const netWorthChange = summary?.month_over_month?.net_change || 0;

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <StatCard
        title="Total Balance"
        value={formatCurrency(totalBalance)}
        change={formatPercentage(balanceChange)}
        trend={getTrend(balanceChange)}
        icon={<Wallet className="h-6 w-6 text-primary-foreground" />}
        colorClass="bg-gradient-primary"
        isLoading={isLoading}
      />
      <StatCard
        title="Savings Rate"
        value={`${savingsRate.toFixed(1)}%`}
        change={formatPercentage(savingsChange)}
        trend={getTrend(savingsChange)}
        icon={<PiggyBank className="h-6 w-6 text-success-foreground" />}
        colorClass="bg-gradient-success"
        isLoading={isLoading}
      />
      <StatCard
        title="Monthly Surplus"
        value={formatCurrency(monthlySurplus)}
        change={formatPercentage(surplusChange)}
        trend={getTrend(surplusChange)}
        icon={<DollarSign className="h-6 w-6 text-primary-foreground" />}
        colorClass="bg-gradient-primary"
        isLoading={isLoading}
      />
      <StatCard
        title="Net Worth"
        value={formatCurrency(netWorth)}
        change={formatPercentage(netWorthChange)}
        trend={getTrend(netWorthChange)}
        icon={<TrendingUp className="h-6 w-6 text-success-foreground" />}
        colorClass="bg-gradient-success"
        isLoading={isLoading}
      />
    </div>
  );
};
