import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  createRecurringTransaction,
  RecurringTransactionCreate,
  getCategories,
  getAccounts,
} from '@/services/api';
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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { useToast } from '@/hooks/use-toast';
import { Loader2 } from 'lucide-react';

interface RecurringTransactionCreateDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function RecurringTransactionCreateDialog({
  open,
  onOpenChange,
}: RecurringTransactionCreateDialogProps) {
  const { toast } = useToast();
  const queryClient = useQueryClient();

  const [formData, setFormData] = useState<RecurringTransactionCreate>({
    name: '',
    amount: 0,
    category_id: '',
    account_id: '',
    type: 'expense',
    frequency: 'monthly',
    start_date: new Date().toISOString().split('T')[0],
    end_date: null,
    day_of_month: 1,
    day_of_week: null,
    is_active: true,
    tags: '',
    notes: '',
  });

  const { data: categories } = useQuery({
    queryKey: ['categories'],
    queryFn: getCategories,
  });

  const { data: accounts } = useQuery({
    queryKey: ['accounts'],
    queryFn: getAccounts,
  });

  const createMutation = useMutation({
    mutationFn: createRecurringTransaction,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['recurring-transactions'] });
      toast({
        title: 'Recurring transaction created',
        description: 'Your recurring transaction has been set up successfully.',
      });
      onOpenChange(false);
      resetForm();
    },
    onError: (error: Error) => {
      toast({
        title: 'Error',
        description: error.message || 'Failed to create recurring transaction',
        variant: 'destructive',
      });
    },
  });

  const resetForm = () => {
    setFormData({
      name: '',
      amount: 0,
      category_id: '',
      account_id: '',
      type: 'expense',
      frequency: 'monthly',
      start_date: new Date().toISOString().split('T')[0],
      end_date: null,
      day_of_month: 1,
      day_of_week: null,
      is_active: true,
      tags: '',
      notes: '',
    });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    // Validation
    if (!formData.name.trim()) {
      toast({
        title: 'Validation Error',
        description: 'Please enter a name',
        variant: 'destructive',
      });
      return;
    }

    if (formData.amount === 0) {
      toast({
        title: 'Validation Error',
        description: 'Amount cannot be zero',
        variant: 'destructive',
      });
      return;
    }

    if (!formData.category_id) {
      toast({
        title: 'Validation Error',
        description: 'Please select a category',
        variant: 'destructive',
      });
      return;
    }

    if (!formData.account_id) {
      toast({
        title: 'Validation Error',
        description: 'Please select an account',
        variant: 'destructive',
      });
      return;
    }

    // Adjust amount sign based on type
    const adjustedAmount = formData.type === 'expense' && formData.amount > 0
      ? -Math.abs(formData.amount)
      : Math.abs(formData.amount);

    createMutation.mutate({
      ...formData,
      amount: adjustedAmount,
    });
  };

  const needsDayOfMonth = ['monthly', 'quarterly', 'yearly'].includes(formData.frequency);
  const needsDayOfWeek = ['weekly', 'biweekly'].includes(formData.frequency);

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Add Recurring Transaction</DialogTitle>
          <DialogDescription>
            Set up a recurring transaction that will be automatically generated
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Name */}
          <div className="space-y-2">
            <Label htmlFor="name">Name *</Label>
            <Input
              id="name"
              placeholder="e.g., Monthly Salary, Rent Payment"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              required
            />
          </div>

          {/* Type */}
          <div className="space-y-2">
            <Label htmlFor="type">Type *</Label>
            <Select
              value={formData.type}
              onValueChange={(value: 'income' | 'expense') =>
                setFormData({ ...formData, type: value })
              }
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="income">Income</SelectItem>
                <SelectItem value="expense">Expense</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Amount */}
          <div className="space-y-2">
            <Label htmlFor="amount">Amount (R) *</Label>
            <Input
              id="amount"
              type="number"
              step="0.01"
              placeholder="0.00"
              value={formData.amount || ''}
              onChange={(e) =>
                setFormData({ ...formData, amount: parseFloat(e.target.value) || 0 })
              }
              required
            />
          </div>

          {/* Category and Account */}
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="category">Category *</Label>
              <Select
                value={formData.category_id}
                onValueChange={(value) => setFormData({ ...formData, category_id: value })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select category" />
                </SelectTrigger>
                <SelectContent>
                  {categories?.map((cat) => (
                    <SelectItem key={cat.id} value={cat.id}>
                      {cat.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="account">Account *</Label>
              <Select
                value={formData.account_id}
                onValueChange={(value) => setFormData({ ...formData, account_id: value })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select account" />
                </SelectTrigger>
                <SelectContent>
                  {accounts?.map((acc) => (
                    <SelectItem key={acc.id} value={acc.id}>
                      {acc.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Frequency */}
          <div className="space-y-2">
            <Label htmlFor="frequency">Frequency *</Label>
            <Select
              value={formData.frequency}
              onValueChange={(value: any) => setFormData({ ...formData, frequency: value })}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="daily">Daily</SelectItem>
                <SelectItem value="weekly">Weekly</SelectItem>
                <SelectItem value="biweekly">Bi-weekly (Every 2 weeks)</SelectItem>
                <SelectItem value="monthly">Monthly</SelectItem>
                <SelectItem value="quarterly">Quarterly (Every 3 months)</SelectItem>
                <SelectItem value="yearly">Yearly</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Day of Month (for monthly/quarterly/yearly) */}
          {needsDayOfMonth && (
            <div className="space-y-2">
              <Label htmlFor="day_of_month">Day of Month *</Label>
              <Input
                id="day_of_month"
                type="number"
                min="1"
                max="31"
                value={formData.day_of_month || ''}
                onChange={(e) =>
                  setFormData({ ...formData, day_of_month: parseInt(e.target.value) || 1 })
                }
                required
              />
              <p className="text-xs text-muted-foreground">
                Day of the month (1-31). If day doesn't exist in a month, last day will be used.
              </p>
            </div>
          )}

          {/* Day of Week (for weekly/biweekly) */}
          {needsDayOfWeek && (
            <div className="space-y-2">
              <Label htmlFor="day_of_week">Day of Week *</Label>
              <Select
                value={formData.day_of_week?.toString() || '0'}
                onValueChange={(value) =>
                  setFormData({ ...formData, day_of_week: parseInt(value) })
                }
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="0">Monday</SelectItem>
                  <SelectItem value="1">Tuesday</SelectItem>
                  <SelectItem value="2">Wednesday</SelectItem>
                  <SelectItem value="3">Thursday</SelectItem>
                  <SelectItem value="4">Friday</SelectItem>
                  <SelectItem value="5">Saturday</SelectItem>
                  <SelectItem value="6">Sunday</SelectItem>
                </SelectContent>
              </Select>
            </div>
          )}

          {/* Start and End Dates */}
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="start_date">Start Date *</Label>
              <Input
                id="start_date"
                type="date"
                value={formData.start_date}
                onChange={(e) => setFormData({ ...formData, start_date: e.target.value })}
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="end_date">End Date (Optional)</Label>
              <Input
                id="end_date"
                type="date"
                value={formData.end_date || ''}
                onChange={(e) =>
                  setFormData({ ...formData, end_date: e.target.value || null })
                }
              />
            </div>
          </div>

          {/* Notes */}
          <div className="space-y-2">
            <Label htmlFor="notes">Notes (Optional)</Label>
            <Textarea
              id="notes"
              placeholder="Additional information..."
              value={formData.notes || ''}
              onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
              rows={2}
            />
          </div>

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
              disabled={createMutation.isPending}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={createMutation.isPending}>
              {createMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Create Recurring Transaction
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}

