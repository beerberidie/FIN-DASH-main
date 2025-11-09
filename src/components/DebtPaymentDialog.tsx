import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { api, Debt, DebtPayment } from '@/services/api';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { useToast } from '@/hooks/use-toast';
import { Loader2 } from 'lucide-react';

interface DebtPaymentDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  debt: Debt;
}

export function DebtPaymentDialog({ open, onOpenChange, debt }: DebtPaymentDialogProps) {
  const { toast } = useToast();
  const queryClient = useQueryClient();

  const [payment, setPayment] = useState<DebtPayment>({
    amount: debt.minimum_payment,
    payment_date: new Date().toISOString().split('T')[0],
    notes: '',
  });

  const paymentMutation = useMutation({
    mutationFn: (data: DebtPayment) => api.recordDebtPayment(debt.id, data),
    onSuccess: (updatedDebt) => {
      queryClient.invalidateQueries({ queryKey: ['debts'] });
      queryClient.invalidateQueries({ queryKey: ['debt-summary'] });
      queryClient.invalidateQueries({ queryKey: ['summary'] });
      
      const newBalance = updatedDebt.current_balance;
      const paidOff = newBalance <= 0;
      
      toast({
        title: paidOff ? '🎉 Debt Paid Off!' : 'Payment Recorded',
        description: paidOff
          ? `Congratulations! ${debt.name} is now paid off!`
          : `New balance: R${newBalance.toLocaleString('en-ZA', { minimumFractionDigits: 2 })}`,
      });
      
      onOpenChange(false);
      resetForm();
    },
    onError: (error: Error) => {
      toast({
        title: 'Error',
        description: error.message || 'Failed to record payment',
        variant: 'destructive',
      });
    },
  });

  const resetForm = () => {
    setPayment({
      amount: debt.minimum_payment,
      payment_date: new Date().toISOString().split('T')[0],
      notes: '',
    });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    // Validation
    if (payment.amount <= 0) {
      toast({
        title: 'Validation Error',
        description: 'Payment amount must be greater than 0',
        variant: 'destructive',
      });
      return;
    }

    if (payment.amount > debt.current_balance) {
      toast({
        title: 'Validation Error',
        description: 'Payment amount cannot exceed current balance',
        variant: 'destructive',
      });
      return;
    }

    paymentMutation.mutate(payment);
  };

  const handleQuickAmount = (amount: number) => {
    setPayment({ ...payment, amount });
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>Record Payment</DialogTitle>
          <DialogDescription>
            Record a payment for {debt.name}
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Current Balance */}
          <div className="rounded-lg bg-muted p-4">
            <div className="text-sm text-muted-foreground">Current Balance</div>
            <div className="text-2xl font-bold">
              R{debt.current_balance.toLocaleString('en-ZA', { minimumFractionDigits: 2 })}
            </div>
          </div>

          {/* Payment Amount */}
          <div className="space-y-2">
            <Label htmlFor="amount">Payment Amount (R) *</Label>
            <Input
              id="amount"
              type="number"
              step="0.01"
              min="0.01"
              max={debt.current_balance}
              placeholder="0.00"
              value={payment.amount || ''}
              onChange={(e) => setPayment({ ...payment, amount: parseFloat(e.target.value) || 0 })}
              required
            />
          </div>

          {/* Quick Amount Buttons */}
          <div className="space-y-2">
            <Label>Quick Amounts</Label>
            <div className="grid grid-cols-3 gap-2">
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={() => handleQuickAmount(debt.minimum_payment)}
              >
                Minimum
                <br />
                <span className="text-xs">R{debt.minimum_payment.toLocaleString('en-ZA')}</span>
              </Button>
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={() => handleQuickAmount(debt.current_balance / 2)}
              >
                Half
                <br />
                <span className="text-xs">R{(debt.current_balance / 2).toLocaleString('en-ZA')}</span>
              </Button>
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={() => handleQuickAmount(debt.current_balance)}
              >
                Full
                <br />
                <span className="text-xs">R{debt.current_balance.toLocaleString('en-ZA')}</span>
              </Button>
            </div>
          </div>

          {/* Payment Date */}
          <div className="space-y-2">
            <Label htmlFor="payment_date">Payment Date</Label>
            <Input
              id="payment_date"
              type="date"
              value={payment.payment_date || ''}
              onChange={(e) => setPayment({ ...payment, payment_date: e.target.value })}
            />
          </div>

          {/* Notes */}
          <div className="space-y-2">
            <Label htmlFor="notes">Notes (Optional)</Label>
            <Textarea
              id="notes"
              placeholder="Payment details..."
              value={payment.notes || ''}
              onChange={(e) => setPayment({ ...payment, notes: e.target.value })}
              rows={2}
            />
          </div>

          {/* New Balance Preview */}
          <div className="rounded-lg bg-muted p-4">
            <div className="text-sm text-muted-foreground">New Balance After Payment</div>
            <div className="text-2xl font-bold">
              R{Math.max(0, debt.current_balance - (payment.amount || 0)).toLocaleString('en-ZA', { minimumFractionDigits: 2 })}
            </div>
            {debt.current_balance - (payment.amount || 0) <= 0 && (
              <div className="text-sm text-green-600 font-medium mt-1">
                🎉 This will pay off the debt!
              </div>
            )}
          </div>

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
              disabled={paymentMutation.isPending}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={paymentMutation.isPending}>
              {paymentMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Record Payment
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}

