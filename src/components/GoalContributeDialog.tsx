import { useState } from "react";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useToast } from "@/hooks/use-toast";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import api, { GoalContribution } from "@/services/api";
import { PlusCircle } from "lucide-react";
import { formatCurrency } from "@/lib/formatters";

interface GoalContributeDialogProps {
  goalId: string;
  goalName: string;
  currentAmount: number;
  targetAmount: number;
}

export const GoalContributeDialog = ({ goalId, goalName, currentAmount, targetAmount }: GoalContributeDialogProps) => {
  const [open, setOpen] = useState(false);
  const [amount, setAmount] = useState<number>(0);

  const { toast } = useToast();
  const queryClient = useQueryClient();

  const contributeMutation = useMutation({
    mutationFn: (contribution: GoalContribution) => api.contributeToGoal(goalId, contribution),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['summary'] });
      queryClient.invalidateQueries({ queryKey: ['goals'] });
      toast({
        title: "Contribution added",
        description: `Successfully added ${formatCurrency(amount)} to ${goalName}`,
      });
      setOpen(false);
      setAmount(0);
    },
    onError: (error: Error) => {
      toast({
        title: "Error adding contribution",
        description: error.message,
        variant: "destructive",
      });
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (amount <= 0) {
      toast({
        title: "Validation error",
        description: "Contribution amount must be greater than 0",
        variant: "destructive",
      });
      return;
    }

    contributeMutation.mutate({ amount });
  };

  const remaining = targetAmount - currentAmount;
  const suggestedAmounts = [
    Math.min(100, remaining),
    Math.min(500, remaining),
    Math.min(1000, remaining),
    remaining,
  ].filter((amt, idx, arr) => amt > 0 && arr.indexOf(amt) === idx);

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button size="sm" variant="outline" className="gap-2">
          <PlusCircle className="h-4 w-4" />
          Contribute
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[425px]">
        <form onSubmit={handleSubmit}>
          <DialogHeader>
            <DialogTitle>Contribute to {goalName}</DialogTitle>
            <DialogDescription>
              Add money to your savings goal. {formatCurrency(remaining)} remaining to reach your target.
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <Label htmlFor="amount">Contribution Amount (R)</Label>
              <Input
                id="amount"
                type="number"
                step="0.01"
                min="0"
                placeholder="100.00"
                value={amount || ""}
                onChange={(e) => setAmount(parseFloat(e.target.value) || 0)}
                required
                autoFocus
              />
            </div>
            <div className="grid gap-2">
              <Label>Quick amounts</Label>
              <div className="flex gap-2 flex-wrap">
                {suggestedAmounts.map((suggestedAmount) => (
                  <Button
                    key={suggestedAmount}
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={() => setAmount(suggestedAmount)}
                  >
                    {formatCurrency(suggestedAmount)}
                  </Button>
                ))}
              </div>
            </div>
            <div className="rounded-lg bg-muted p-3 space-y-1">
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Current:</span>
                <span className="font-medium">{formatCurrency(currentAmount)}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">After contribution:</span>
                <span className="font-medium">{formatCurrency(Math.min(currentAmount + amount, targetAmount))}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Target:</span>
                <span className="font-medium">{formatCurrency(targetAmount)}</span>
              </div>
            </div>
          </div>
          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => setOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={contributeMutation.isPending}>
              {contributeMutation.isPending ? "Adding..." : "Add Contribution"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
};

