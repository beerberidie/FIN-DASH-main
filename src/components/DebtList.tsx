import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api, Debt } from '@/services/api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
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
import { Plus, CreditCard, DollarSign, Calendar, TrendingDown, Trash2 } from 'lucide-react';
import { DebtCreateDialog } from './DebtCreateDialog';
import { DebtPaymentDialog } from './DebtPaymentDialog';
import { useToast } from '@/hooks/use-toast';
import { useState } from 'react';

export function DebtList() {
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [paymentDialogOpen, setPaymentDialogOpen] = useState(false);
  const [selectedDebt, setSelectedDebt] = useState<Debt | null>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [debtToDelete, setDebtToDelete] = useState<Debt | null>(null);

  const { data: debts, isLoading } = useQuery({
    queryKey: ['debts'],
    queryFn: api.getDebts,
  });

  const { data: summary } = useQuery({
    queryKey: ['debt-summary'],
    queryFn: api.getDebtSummary,
  });

  const deleteMutation = useMutation({
    mutationFn: api.deleteDebt,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['debts'] });
      queryClient.invalidateQueries({ queryKey: ['debt-summary'] });
      toast({
        title: "Debt Deleted",
        description: "The debt has been successfully deleted.",
      });
      setDeleteDialogOpen(false);
      setDebtToDelete(null);
    },
    onError: (err: Error) => {
      toast({
        title: "Error deleting debt",
        description: err.message || "Failed to delete debt",
        variant: "destructive",
      });
    },
  });

  const handlePayment = (debt: Debt) => {
    setSelectedDebt(debt);
    setPaymentDialogOpen(true);
  };

  const handleDelete = (debt: Debt) => {
    setDebtToDelete(debt);
    setDeleteDialogOpen(true);
  };

  const confirmDelete = () => {
    if (debtToDelete) {
      deleteMutation.mutate(debtToDelete.id);
    }
  };

  const getDebtTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      credit_card: 'Credit Card',
      personal_loan: 'Personal Loan',
      student_loan: 'Student Loan',
      mortgage: 'Mortgage',
      car_loan: 'Car Loan',
      other: 'Other',
    };
    return labels[type] || type;
  };

  const getDebtTypeColor = (type: string) => {
    const colors: Record<string, string> = {
      credit_card: 'bg-red-100 text-red-800',
      personal_loan: 'bg-blue-100 text-blue-800',
      student_loan: 'bg-purple-100 text-purple-800',
      mortgage: 'bg-green-100 text-green-800',
      car_loan: 'bg-yellow-100 text-yellow-800',
      other: 'bg-gray-100 text-gray-800',
    };
    return colors[type] || colors.other;
  };

  const calculateProgress = (debt: Debt) => {
    const paid = debt.original_balance - debt.current_balance;
    return (paid / debt.original_balance) * 100;
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

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      {summary && (
        <div className="grid gap-4 md:grid-cols-3">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Debt</CardTitle>
              <TrendingDown className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">R{summary.total_debt.toLocaleString('en-ZA', { minimumFractionDigits: 2 })}</div>
              <p className="text-xs text-muted-foreground">
                {summary.active_debt_count} active {summary.active_debt_count === 1 ? 'debt' : 'debts'}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Minimum Payment</CardTitle>
              <DollarSign className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">R{summary.minimum_payment.toLocaleString('en-ZA', { minimumFractionDigits: 2 })}</div>
              <p className="text-xs text-muted-foreground">Per month</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Debts</CardTitle>
              <CreditCard className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{summary.debt_count}</div>
              <p className="text-xs text-muted-foreground">All accounts</p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Debts</h2>
          <p className="text-muted-foreground">Manage your debts and track payoff progress</p>
        </div>
        <Button onClick={() => setCreateDialogOpen(true)}>
          <Plus className="mr-2 h-4 w-4" />
          Add Debt
        </Button>
      </div>

      {/* Debt List */}
      {debts && debts.length > 0 ? (
        <div className="grid gap-4 md:grid-cols-2">
          {debts.map((debt) => {
            const progress = calculateProgress(debt);
            const paidAmount = debt.original_balance - debt.current_balance;

            return (
              <Card key={debt.id}>
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="space-y-1">
                      <CardTitle className="text-lg">{debt.name}</CardTitle>
                      <Badge className={getDebtTypeColor(debt.debt_type)}>
                        {getDebtTypeLabel(debt.debt_type)}
                      </Badge>
                    </div>
                    <div className="text-right">
                      <div className="text-2xl font-bold">
                        R{debt.current_balance.toLocaleString('en-ZA', { minimumFractionDigits: 2 })}
                      </div>
                      <div className="text-xs text-muted-foreground">
                        of R{debt.original_balance.toLocaleString('en-ZA', { minimumFractionDigits: 2 })}
                      </div>
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  {/* Progress Bar */}
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Paid off</span>
                      <span className="font-medium">{progress.toFixed(1)}%</span>
                    </div>
                    <Progress value={progress} className="h-2" />
                    <div className="text-xs text-muted-foreground">
                      R{paidAmount.toLocaleString('en-ZA', { minimumFractionDigits: 2 })} paid
                    </div>
                  </div>

                  {/* Details */}
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <div className="text-muted-foreground">Interest Rate</div>
                      <div className="font-medium">{debt.interest_rate}%</div>
                    </div>
                    <div>
                      <div className="text-muted-foreground">Min. Payment</div>
                      <div className="font-medium">R{debt.minimum_payment.toLocaleString('en-ZA')}</div>
                    </div>
                    <div>
                      <div className="text-muted-foreground">Due Day</div>
                      <div className="font-medium flex items-center">
                        <Calendar className="mr-1 h-3 w-3" />
                        {debt.due_day}th
                      </div>
                    </div>
                    <div>
                      <div className="text-muted-foreground">Status</div>
                      <div className="font-medium">
                        {debt.current_balance > 0 ? (
                          <Badge variant="outline" className="text-orange-600">Active</Badge>
                        ) : (
                          <Badge variant="outline" className="text-green-600">Paid Off</Badge>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Notes */}
                  {debt.notes && (
                    <div className="text-sm">
                      <div className="text-muted-foreground">Notes</div>
                      <div className="mt-1">{debt.notes}</div>
                    </div>
                  )}

                  {/* Actions */}
                  <div className="flex gap-2 pt-2">
                    <Button
                      variant="outline"
                      size="sm"
                      className="flex-1"
                      onClick={() => handlePayment(debt)}
                      disabled={debt.current_balance <= 0}
                    >
                      Record Payment
                    </Button>
                    <Button
                      variant="outline"
                      size="icon"
                      onClick={() => handleDelete(debt)}
                    >
                      <Trash2 className="h-4 w-4 text-destructive" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      ) : (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <CreditCard className="h-12 w-12 text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold mb-2">No debts yet</h3>
            <p className="text-muted-foreground text-center mb-4">
              Start tracking your debts to see payoff progress and strategies
            </p>
            <Button onClick={() => setCreateDialogOpen(true)}>
              <Plus className="mr-2 h-4 w-4" />
              Add Your First Debt
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Dialogs */}
      <DebtCreateDialog open={createDialogOpen} onOpenChange={setCreateDialogOpen} />
      {selectedDebt && (
        <DebtPaymentDialog
          open={paymentDialogOpen}
          onOpenChange={setPaymentDialogOpen}
          debt={selectedDebt}
        />
      )}

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Debt?</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete "{debtToDelete?.name}"?
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

