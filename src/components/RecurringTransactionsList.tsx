import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  getRecurringTransactions,
  toggleRecurringTransaction,
  deleteRecurringTransaction,
  RecurringTransaction,
} from '@/services/api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  Repeat,
  Plus,
  Edit,
  Trash2,
  Power,
  PowerOff,
  AlertCircle,
  Calendar,
  DollarSign,
  TrendingUp,
  TrendingDown,
} from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { RecurringTransactionCreateDialog } from './RecurringTransactionCreateDialog';

export function RecurringTransactionsList() {
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [showInactive, setShowInactive] = useState(false);

  const { data: recurring, isLoading, error } = useQuery({
    queryKey: ['recurring-transactions', showInactive],
    queryFn: () => getRecurringTransactions(!showInactive),
  });

  const toggleMutation = useMutation({
    mutationFn: toggleRecurringTransaction,
    onSuccess: (updated) => {
      queryClient.invalidateQueries({ queryKey: ['recurring-transactions'] });
      toast({
        title: updated.is_active ? 'Activated' : 'Deactivated',
        description: `${updated.name} has been ${updated.is_active ? 'activated' : 'deactivated'}`,
      });
    },
    onError: (error: Error) => {
      toast({
        title: 'Error',
        description: error.message,
        variant: 'destructive',
      });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: deleteRecurringTransaction,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['recurring-transactions'] });
      toast({
        title: 'Deleted',
        description: 'Recurring transaction has been deleted',
      });
    },
    onError: (error: Error) => {
      toast({
        title: 'Error',
        description: error.message,
        variant: 'destructive',
      });
    },
  });

  const getFrequencyLabel = (frequency: string) => {
    const labels: Record<string, string> = {
      daily: 'Daily',
      weekly: 'Weekly',
      biweekly: 'Bi-weekly',
      monthly: 'Monthly',
      quarterly: 'Quarterly',
      yearly: 'Yearly',
    };
    return labels[frequency] || frequency;
  };

  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return 'N/A';
    return new Date(dateStr).toLocaleDateString('en-ZA', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  if (isLoading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-32 w-full" />
        <Skeleton className="h-32 w-full" />
        <Skeleton className="h-32 w-full" />
      </div>
    );
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>
          Failed to load recurring transactions. Please try again.
        </AlertDescription>
      </Alert>
    );
  }

  const activeRecurring = recurring?.filter(r => r.is_active) || [];
  const inactiveRecurring = recurring?.filter(r => !r.is_active) || [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Recurring Transactions</h2>
          <p className="text-muted-foreground">
            Automate your regular income and expenses
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowInactive(!showInactive)}
          >
            {showInactive ? 'Hide Inactive' : 'Show Inactive'}
          </Button>
          <Button onClick={() => setCreateDialogOpen(true)}>
            <Plus className="mr-2 h-4 w-4" />
            Add Recurring Transaction
          </Button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Rules</CardTitle>
            <Repeat className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{activeRecurring.length}</div>
            <p className="text-xs text-muted-foreground">
              {inactiveRecurring.length} inactive
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Monthly Income</CardTitle>
            <TrendingUp className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              R{activeRecurring
                .filter(r => r.type === 'income' && r.frequency === 'monthly')
                .reduce((sum, r) => sum + r.amount, 0)
                .toLocaleString('en-ZA', { minimumFractionDigits: 2 })}
            </div>
            <p className="text-xs text-muted-foreground">
              From recurring income
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Monthly Expenses</CardTitle>
            <TrendingDown className="h-4 w-4 text-red-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">
              R{Math.abs(activeRecurring
                .filter(r => r.type === 'expense' && r.frequency === 'monthly')
                .reduce((sum, r) => sum + r.amount, 0))
                .toLocaleString('en-ZA', { minimumFractionDigits: 2 })}
            </div>
            <p className="text-xs text-muted-foreground">
              From recurring expenses
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Recurring Transactions List */}
      {recurring && recurring.length > 0 ? (
        <div className="space-y-4">
          {recurring.map((rec) => (
            <Card key={rec.id} className={!rec.is_active ? 'opacity-60' : ''}>
              <CardContent className="pt-6">
                <div className="flex items-start justify-between">
                  <div className="flex-1 space-y-2">
                    <div className="flex items-center gap-2">
                      <h3 className="text-lg font-semibold">{rec.name}</h3>
                      <Badge variant={rec.is_active ? 'default' : 'secondary'}>
                        {rec.is_active ? 'Active' : 'Inactive'}
                      </Badge>
                      <Badge variant="outline">{getFrequencyLabel(rec.frequency)}</Badge>
                      <Badge variant={rec.type === 'income' ? 'default' : 'destructive'}>
                        {rec.type === 'income' ? 'Income' : 'Expense'}
                      </Badge>
                    </div>

                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                      <div>
                        <div className="text-muted-foreground">Amount</div>
                        <div className={`font-semibold ${rec.type === 'income' ? 'text-green-600' : 'text-red-600'}`}>
                          R{Math.abs(rec.amount).toLocaleString('en-ZA', { minimumFractionDigits: 2 })}
                        </div>
                      </div>

                      <div>
                        <div className="text-muted-foreground">Next Due</div>
                        <div className="font-medium flex items-center gap-1">
                          <Calendar className="h-3 w-3" />
                          {formatDate(rec.next_due)}
                        </div>
                      </div>

                      <div>
                        <div className="text-muted-foreground">Last Generated</div>
                        <div className="font-medium">
                          {formatDate(rec.last_generated)}
                        </div>
                      </div>

                      <div>
                        <div className="text-muted-foreground">Start Date</div>
                        <div className="font-medium">{formatDate(rec.start_date)}</div>
                      </div>
                    </div>

                    {rec.notes && (
                      <p className="text-sm text-muted-foreground">{rec.notes}</p>
                    )}
                  </div>

                  <div className="flex items-center gap-2 ml-4">
                    <Button
                      variant="outline"
                      size="icon"
                      onClick={() => toggleMutation.mutate(rec.id)}
                      disabled={toggleMutation.isPending}
                    >
                      {rec.is_active ? (
                        <PowerOff className="h-4 w-4" />
                      ) : (
                        <Power className="h-4 w-4" />
                      )}
                    </Button>
                    <Button
                      variant="outline"
                      size="icon"
                      onClick={() => {
                        if (confirm('Are you sure you want to delete this recurring transaction?')) {
                          deleteMutation.mutate(rec.id);
                        }
                      }}
                      disabled={deleteMutation.isPending}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <Repeat className="h-12 w-12 text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold mb-2">No Recurring Transactions</h3>
            <p className="text-muted-foreground text-center mb-4">
              Set up recurring transactions to automate your regular income and expenses
            </p>
            <Button onClick={() => setCreateDialogOpen(true)}>
              <Plus className="mr-2 h-4 w-4" />
              Add Your First Recurring Transaction
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Create Dialog */}
      <RecurringTransactionCreateDialog
        open={createDialogOpen}
        onOpenChange={setCreateDialogOpen}
      />
    </div>
  );
}

