import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { useQuery } from "@tanstack/react-query";
import api from "@/services/api";
import { formatCurrency } from "@/lib/formatters";
import { useToast } from "@/hooks/use-toast";
import { BudgetCreateDialog } from "./BudgetCreateDialog";
import { Plus } from "lucide-react";

interface BudgetItem {
  category: string;
  planned: number;
  spent: number;
  color: string;
  utilization: number;
  isOverBudget: boolean;
}

const BudgetBar = ({ category, planned, spent, color, utilization, isOverBudget }: BudgetItem) => {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <div className="space-y-1">
          <p className="text-sm font-semibold text-foreground">{category}</p>
          <p className="text-xs text-muted-foreground">
            {formatCurrency(spent)} of {formatCurrency(planned)}
          </p>
        </div>
        <span className={`text-lg font-bold ${isOverBudget ? "text-destructive" : "text-foreground"}`}>
          {utilization.toFixed(0)}%
        </span>
      </div>
      <div className="relative">
        <Progress
          value={Math.min(utilization, 100)}
          className="h-3 bg-muted"
        />
      </div>
    </div>
  );
};

const BudgetSkeleton = () => (
  <div className="space-y-3">
    <div className="flex items-center justify-between">
      <div className="space-y-1">
        <Skeleton className="h-4 w-32" />
        <Skeleton className="h-3 w-40" />
      </div>
      <Skeleton className="h-6 w-12" />
    </div>
    <Skeleton className="h-3 w-full" />
  </div>
);

export const BudgetBars = () => {
  const { toast } = useToast();
  const [createDialogOpen, setCreateDialogOpen] = useState(false);

  const { data: budgetStatus, isLoading } = useQuery({
    queryKey: ['currentBudget'],
    queryFn: api.getCurrentBudget,
    refetchInterval: 30000, // Refresh every 30 seconds
    onError: (err: Error) => {
      toast({
        title: "Error loading budget",
        description: err.message,
        variant: "destructive",
      });
    },
  });

  // Build budget items from status
  const budgetItems: BudgetItem[] = budgetStatus ? [
    {
      category: "Needs (50%)",
      planned: budgetStatus.needs_planned,
      spent: budgetStatus.needs_actual,
      color: "bg-primary",
      utilization: budgetStatus.needs_utilization,
      isOverBudget: budgetStatus.over_budget.needs,
    },
    {
      category: "Wants (30%)",
      planned: budgetStatus.wants_planned,
      spent: budgetStatus.wants_actual,
      color: "bg-accent",
      utilization: budgetStatus.wants_utilization,
      isOverBudget: budgetStatus.over_budget.wants,
    },
    {
      category: "Savings (20%)",
      planned: budgetStatus.savings_planned,
      spent: budgetStatus.savings_actual,
      color: "bg-success",
      utilization: budgetStatus.savings_utilization,
      isOverBudget: budgetStatus.over_budget.savings,
    },
  ] : [];

  const totalPlanned = budgetStatus?.total_planned || 0;
  const totalActual = budgetStatus?.total_actual || 0;
  const budgetExists = budgetStatus?.exists || false;

  // Get current month name
  const monthNames = ["January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"];
  const currentMonth = budgetStatus ? monthNames[budgetStatus.month - 1] : '';
  const currentYear = budgetStatus?.year || new Date().getFullYear();

  return (
    <Card className="p-6 bg-gradient-card shadow-md border-border">
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-xl font-bold text-foreground">Budget Overview</h3>
            <p className="text-sm text-muted-foreground mt-1">
              {isLoading ? 'Loading...' : budgetExists ? `50/30/20 Rule - ${currentMonth} ${currentYear}` : 'No budget set for current month'}
            </p>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setCreateDialogOpen(true)}
          >
            <Plus className="h-4 w-4 mr-2" />
            Add Budget
          </Button>
        </div>
        <div className="space-y-6">
          {isLoading ? (
            <>
              <BudgetSkeleton />
              <BudgetSkeleton />
              <BudgetSkeleton />
            </>
          ) : !budgetExists ? (
            <div className="text-center py-8 text-muted-foreground">
              <p>No budget configured</p>
              <p className="text-sm mt-1">Create a budget to track your spending</p>
            </div>
          ) : (
            budgetItems.map((budget) => (
              <BudgetBar key={budget.category} {...budget} />
            ))
          )}
        </div>
        {budgetExists && !isLoading && (
          <div className="pt-4 border-t border-border">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-muted-foreground">Total Monthly Budget</span>
              <span className="text-lg font-bold text-foreground">{formatCurrency(totalPlanned)}</span>
            </div>
            <div className="flex items-center justify-between mt-2">
              <span className="text-sm font-medium text-muted-foreground">Total Spent</span>
              <span className="text-lg font-bold text-foreground">{formatCurrency(totalActual)}</span>
            </div>
          </div>
        )}
      </div>

      {/* Budget Create Dialog */}
      <BudgetCreateDialog open={createDialogOpen} onOpenChange={setCreateDialogOpen} />
    </Card>
  );
};
