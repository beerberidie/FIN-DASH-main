import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { createBudget, BudgetCreate } from '@/services/api';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { useToast } from '@/hooks/use-toast';
import { Loader2 } from 'lucide-react';

interface BudgetCreateDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function BudgetCreateDialog({ open, onOpenChange }: BudgetCreateDialogProps) {
  const { toast } = useToast();
  const queryClient = useQueryClient();

  const currentDate = new Date();
  const [year, setYear] = useState(currentDate.getFullYear());
  const [month, setMonth] = useState(currentDate.getMonth() + 1);
  const [totalIncome, setTotalIncome] = useState('');

  const createMutation = useMutation({
    mutationFn: (budget: BudgetCreate) => createBudget(budget),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['currentBudget'] });
      queryClient.invalidateQueries({ queryKey: ['budgets'] });
      toast({
        title: 'Budget Created',
        description: 'Your budget has been successfully created.',
      });
      onOpenChange(false);
      resetForm();
    },
    onError: (error: Error) => {
      toast({
        title: 'Error Creating Budget',
        description: error.message || 'Failed to create budget',
        variant: 'destructive',
      });
    },
  });

  const resetForm = () => {
    const currentDate = new Date();
    setYear(currentDate.getFullYear());
    setMonth(currentDate.getMonth() + 1);
    setTotalIncome('');
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    const income = parseFloat(totalIncome);
    if (isNaN(income) || income <= 0) {
      toast({
        title: 'Validation Error',
        description: 'Please enter a valid total income amount',
        variant: 'destructive',
      });
      return;
    }

    // Calculate 50/30/20 rule
    const needs = income * 0.5;
    const wants = income * 0.3;
    const savings = income * 0.2;

    const budget: BudgetCreate = {
      year,
      month,
      total_income: income,
      needs_budget: needs,
      wants_budget: wants,
      savings_budget: savings,
    };

    createMutation.mutate(budget);
  };

  const monthNames = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ];

  const years = Array.from({ length: 5 }, (_, i) => currentDate.getFullYear() - 1 + i);

  // Calculate preview amounts
  const income = parseFloat(totalIncome) || 0;
  const needs = income * 0.5;
  const wants = income * 0.3;
  const savings = income * 0.2;

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-ZA', {
      style: 'currency',
      currency: 'ZAR',
    }).format(amount);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>Create New Budget</DialogTitle>
          <DialogDescription>
            Create a budget using the 50/30/20 rule: 50% Needs, 30% Wants, 20% Savings
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit}>
          <div className="grid gap-4 py-4">
            {/* Year Selection */}
            <div className="grid gap-2">
              <Label htmlFor="year">Year</Label>
              <Select
                value={year.toString()}
                onValueChange={(value) => setYear(parseInt(value))}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select year" />
                </SelectTrigger>
                <SelectContent>
                  {years.map((y) => (
                    <SelectItem key={y} value={y.toString()}>
                      {y}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Month Selection */}
            <div className="grid gap-2">
              <Label htmlFor="month">Month</Label>
              <Select
                value={month.toString()}
                onValueChange={(value) => setMonth(parseInt(value))}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select month" />
                </SelectTrigger>
                <SelectContent>
                  {monthNames.map((name, index) => (
                    <SelectItem key={index + 1} value={(index + 1).toString()}>
                      {name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Total Income */}
            <div className="grid gap-2">
              <Label htmlFor="totalIncome">Total Monthly Income *</Label>
              <Input
                id="totalIncome"
                type="number"
                step="0.01"
                min="0"
                placeholder="Enter your total monthly income"
                value={totalIncome}
                onChange={(e) => setTotalIncome(e.target.value)}
                required
              />
            </div>

            {/* Budget Preview */}
            {income > 0 && (
              <div className="rounded-lg border p-4 space-y-3 bg-muted/50">
                <h4 className="font-semibold text-sm">Budget Breakdown</h4>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Needs (50%):</span>
                    <span className="font-medium">{formatCurrency(needs)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Wants (30%):</span>
                    <span className="font-medium">{formatCurrency(wants)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Savings (20%):</span>
                    <span className="font-medium">{formatCurrency(savings)}</span>
                  </div>
                  <div className="flex justify-between pt-2 border-t">
                    <span className="font-semibold">Total:</span>
                    <span className="font-semibold">{formatCurrency(income)}</span>
                  </div>
                </div>
              </div>
            )}
          </div>

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => {
                onOpenChange(false);
                resetForm();
              }}
              disabled={createMutation.isPending}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={createMutation.isPending || !totalIncome}>
              {createMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Create Budget
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}

