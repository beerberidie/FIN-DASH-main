import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { api, DebtCreate } from '@/services/api';
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

interface DebtCreateDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function DebtCreateDialog({ open, onOpenChange }: DebtCreateDialogProps) {
  const { toast } = useToast();
  const queryClient = useQueryClient();

  const [formData, setFormData] = useState<DebtCreate>({
    name: '',
    debt_type: 'credit_card',
    original_balance: 0,
    current_balance: 0,
    interest_rate: 0,
    minimum_payment: 0,
    due_day: 1,
    notes: '',
  });

  const createMutation = useMutation({
    mutationFn: api.createDebt,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['debts'] });
      queryClient.invalidateQueries({ queryKey: ['debt-summary'] });
      queryClient.invalidateQueries({ queryKey: ['summary'] });
      toast({
        title: 'Debt created',
        description: 'Your debt has been added successfully.',
      });
      onOpenChange(false);
      resetForm();
    },
    onError: (error: Error) => {
      toast({
        title: 'Error',
        description: error.message || 'Failed to create debt',
        variant: 'destructive',
      });
    },
  });

  const resetForm = () => {
    setFormData({
      name: '',
      debt_type: 'credit_card',
      original_balance: 0,
      current_balance: 0,
      interest_rate: 0,
      minimum_payment: 0,
      due_day: 1,
      notes: '',
    });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    // Validation
    if (!formData.name.trim()) {
      toast({
        title: 'Validation Error',
        description: 'Please enter a debt name',
        variant: 'destructive',
      });
      return;
    }

    if (formData.original_balance <= 0) {
      toast({
        title: 'Validation Error',
        description: 'Original balance must be greater than 0',
        variant: 'destructive',
      });
      return;
    }

    if (formData.current_balance < 0) {
      toast({
        title: 'Validation Error',
        description: 'Current balance cannot be negative',
        variant: 'destructive',
      });
      return;
    }

    if (formData.current_balance > formData.original_balance) {
      toast({
        title: 'Validation Error',
        description: 'Current balance cannot exceed original balance',
        variant: 'destructive',
      });
      return;
    }

    if (formData.interest_rate < 0 || formData.interest_rate > 100) {
      toast({
        title: 'Validation Error',
        description: 'Interest rate must be between 0 and 100',
        variant: 'destructive',
      });
      return;
    }

    if (formData.minimum_payment < 0) {
      toast({
        title: 'Validation Error',
        description: 'Minimum payment cannot be negative',
        variant: 'destructive',
      });
      return;
    }

    if (formData.due_day < 1 || formData.due_day > 31) {
      toast({
        title: 'Validation Error',
        description: 'Due day must be between 1 and 31',
        variant: 'destructive',
      });
      return;
    }

    createMutation.mutate(formData);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Add New Debt</DialogTitle>
          <DialogDescription>
            Track a new debt to monitor payoff progress and calculate strategies
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Name */}
          <div className="space-y-2">
            <Label htmlFor="name">Debt Name *</Label>
            <Input
              id="name"
              placeholder="e.g., Visa Credit Card"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              required
            />
          </div>

          {/* Debt Type */}
          <div className="space-y-2">
            <Label htmlFor="debt_type">Debt Type *</Label>
            <Select
              value={formData.debt_type}
              onValueChange={(value: any) => setFormData({ ...formData, debt_type: value })}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="credit_card">Credit Card</SelectItem>
                <SelectItem value="personal_loan">Personal Loan</SelectItem>
                <SelectItem value="student_loan">Student Loan</SelectItem>
                <SelectItem value="mortgage">Mortgage</SelectItem>
                <SelectItem value="car_loan">Car Loan</SelectItem>
                <SelectItem value="other">Other</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Balances */}
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="original_balance">Original Balance (R) *</Label>
              <Input
                id="original_balance"
                type="number"
                step="0.01"
                min="0"
                placeholder="0.00"
                value={formData.original_balance || ''}
                onChange={(e) => setFormData({ ...formData, original_balance: parseFloat(e.target.value) || 0 })}
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="current_balance">Current Balance (R) *</Label>
              <Input
                id="current_balance"
                type="number"
                step="0.01"
                min="0"
                placeholder="0.00"
                value={formData.current_balance || ''}
                onChange={(e) => setFormData({ ...formData, current_balance: parseFloat(e.target.value) || 0 })}
                required
              />
            </div>
          </div>

          {/* Interest Rate and Minimum Payment */}
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="interest_rate">Interest Rate (%) *</Label>
              <Input
                id="interest_rate"
                type="number"
                step="0.01"
                min="0"
                max="100"
                placeholder="0.00"
                value={formData.interest_rate || ''}
                onChange={(e) => setFormData({ ...formData, interest_rate: parseFloat(e.target.value) || 0 })}
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="minimum_payment">Minimum Payment (R) *</Label>
              <Input
                id="minimum_payment"
                type="number"
                step="0.01"
                min="0"
                placeholder="0.00"
                value={formData.minimum_payment || ''}
                onChange={(e) => setFormData({ ...formData, minimum_payment: parseFloat(e.target.value) || 0 })}
                required
              />
            </div>
          </div>

          {/* Due Day */}
          <div className="space-y-2">
            <Label htmlFor="due_day">Payment Due Day *</Label>
            <Input
              id="due_day"
              type="number"
              min="1"
              max="31"
              placeholder="1"
              value={formData.due_day || ''}
              onChange={(e) => setFormData({ ...formData, due_day: parseInt(e.target.value) || 1 })}
              required
            />
            <p className="text-xs text-muted-foreground">Day of the month (1-31)</p>
          </div>

          {/* Notes */}
          <div className="space-y-2">
            <Label htmlFor="notes">Notes (Optional)</Label>
            <Textarea
              id="notes"
              placeholder="Additional information about this debt..."
              value={formData.notes || ''}
              onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
              rows={3}
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
              Add Debt
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}

