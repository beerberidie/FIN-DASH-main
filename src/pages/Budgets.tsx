import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getBudgets, deleteBudget, Budget } from '@/services/api';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';
import { ArrowLeft, PieChart, Trash2, Plus, Calendar } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { BudgetCreateDialog } from '@/components/BudgetCreateDialog';

export default function Budgets() {
  const { toast } = useToast();
  const queryClient = useQueryClient();

  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [budgetToDelete, setBudgetToDelete] = useState<Budget | null>(null);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);

  const { data: budgets = [], isLoading } = useQuery({
    queryKey: ['budgets'],
    queryFn: () => getBudgets(),
  });

  const deleteMutation = useMutation({
    mutationFn: deleteBudget,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['budgets'] });
      queryClient.invalidateQueries({ queryKey: ['currentBudget'] });
      queryClient.invalidateQueries({ queryKey: ['summary'] });
      toast({
        title: 'Budget Deleted',
        description: 'The budget has been successfully deleted.',
      });
      setDeleteDialogOpen(false);
      setBudgetToDelete(null);
    },
    onError: (error: Error) => {
      toast({
        title: 'Error deleting budget',
        description: error.message || 'Failed to delete budget',
        variant: 'destructive',
      });
    },
  });

  const handleDelete = (budget: Budget) => {
    setBudgetToDelete(budget);
    setDeleteDialogOpen(true);
  };

  const confirmDelete = () => {
    if (budgetToDelete) {
      deleteMutation.mutate(budgetToDelete.id);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-ZA', {
      style: 'currency',
      currency: 'ZAR',
    }).format(amount);
  };

  const getMonthName = (month: number) => {
    const monthNames = [
      'January',
      'February',
      'March',
      'April',
      'May',
      'June',
      'July',
      'August',
      'September',
      'October',
      'November',
      'December',
    ];
    return monthNames[month - 1] || 'Unknown';
  };

  const isCurrentMonth = (budget: Budget) => {
    const now = new Date();
    return budget.year === now.getFullYear() && budget.month === now.getMonth() + 1;
  };

  // Sort budgets by year and month (most recent first)
  const sortedBudgets = [...budgets].sort((a, b) => {
    if (a.year !== b.year) return b.year - a.year;
    return b.month - a.month;
  });

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card shadow-sm">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Link to="/">
                <Button variant="ghost" size="icon">
                  <ArrowLeft className="h-5 w-5" />
                </Button>
              </Link>
              <div className="p-2 rounded-lg bg-gradient-primary">
                <PieChart className="h-6 w-6 text-primary-foreground" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-foreground">Budgets</h1>
                <p className="text-sm text-muted-foreground">Manage your monthly budgets</p>
              </div>
            </div>
            <Button onClick={() => setCreateDialogOpen(true)}>
              <Plus className="h-4 w-4 mr-2" />
              Create Budget
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <div className="space-y-6">
          {/* Summary Card */}
          <Card>
            <CardHeader>
              <CardTitle>Budget Summary</CardTitle>
              <CardDescription>
                {isLoading ? 'Loading...' : `You have ${budgets.length} budget${budgets.length !== 1 ? 's' : ''}`}
              </CardDescription>
            </CardHeader>
          </Card>

          {/* Budgets List */}
          {isLoading ? (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              <Skeleton className="h-64 w-full" />
              <Skeleton className="h-64 w-full" />
              <Skeleton className="h-64 w-full" />
            </div>
          ) : budgets.length === 0 ? (
            <Card>
              <CardContent className="flex flex-col items-center justify-center py-12">
                <PieChart className="h-12 w-12 text-muted-foreground mb-4" />
                <p className="text-lg font-medium text-muted-foreground">No budgets found</p>
                <p className="text-sm text-muted-foreground mt-1">Create your first budget to get started</p>
                <Button onClick={() => setCreateDialogOpen(true)} className="mt-4">
                  <Plus className="h-4 w-4 mr-2" />
                  Create Budget
                </Button>
              </CardContent>
            </Card>
          ) : (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {sortedBudgets.map((budget) => {
                const totalBudget = budget.needs_budget + budget.wants_budget + budget.savings_budget;
                const totalIncome = budget.total_income || totalBudget;

                return (
                  <Card key={budget.id} className="hover:shadow-lg transition-shadow">
                    <CardHeader>
                      <div className="flex items-start justify-between">
                        <div className="space-y-1">
                          <CardTitle className="text-lg flex items-center gap-2">
                            <Calendar className="h-5 w-5" />
                            {getMonthName(budget.month)} {budget.year}
                          </CardTitle>
                          {isCurrentMonth(budget) && (
                            <Badge variant="default" className="bg-green-500">
                              Current Month
                            </Badge>
                          )}
                        </div>
                        <Button variant="ghost" size="icon" onClick={() => handleDelete(budget)}>
                          <Trash2 className="h-4 w-4 text-destructive" />
                        </Button>
                      </div>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div>
                        <div className="text-sm text-muted-foreground">Total Income</div>
                        <div className="text-2xl font-bold">{formatCurrency(totalIncome)}</div>
                      </div>

                      <div className="space-y-3">
                        <div className="flex items-center justify-between text-sm">
                          <span className="text-muted-foreground">Needs (50%)</span>
                          <span className="font-medium">{formatCurrency(budget.needs_budget)}</span>
                        </div>
                        <div className="flex items-center justify-between text-sm">
                          <span className="text-muted-foreground">Wants (30%)</span>
                          <span className="font-medium">{formatCurrency(budget.wants_budget)}</span>
                        </div>
                        <div className="flex items-center justify-between text-sm">
                          <span className="text-muted-foreground">Savings (20%)</span>
                          <span className="font-medium">{formatCurrency(budget.savings_budget)}</span>
                        </div>
                      </div>

                      <div className="pt-3 border-t">
                        <div className="flex items-center justify-between text-sm font-semibold">
                          <span>Total Budget</span>
                          <span>{formatCurrency(totalBudget)}</span>
                        </div>
                      </div>

                      {budget.notes && (
                        <div className="text-xs text-muted-foreground pt-2 border-t">
                          <strong>Notes:</strong> {budget.notes}
                        </div>
                      )}
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          )}
        </div>
      </main>

      {/* Budget Create Dialog */}
      <BudgetCreateDialog open={createDialogOpen} onOpenChange={setCreateDialogOpen} />

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Budget?</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete the budget for{' '}
              {budgetToDelete && `${getMonthName(budgetToDelete.month)} ${budgetToDelete.year}`}?
              <br />
              <br />
              This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={confirmDelete}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}

