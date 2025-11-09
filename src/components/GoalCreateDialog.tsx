import { useState } from "react";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useToast } from "@/hooks/use-toast";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import api, { GoalCreate } from "@/services/api";
import { Plus } from "lucide-react";

export const GoalCreateDialog = () => {
  const [open, setOpen] = useState(false);
  const [formData, setFormData] = useState<GoalCreate>({
    name: "",
    target_amount: 0,
    current_amount: 0,
    target_date: "",
    color: "blue",
    icon: "Target",
  });

  const { toast } = useToast();
  const queryClient = useQueryClient();

  const createMutation = useMutation({
    mutationFn: api.createGoal,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['summary'] });
      queryClient.invalidateQueries({ queryKey: ['goals'] });
      toast({
        title: "Goal created",
        description: "Your savings goal has been created successfully.",
      });
      setOpen(false);
      // Reset form
      setFormData({
        name: "",
        target_amount: 0,
        current_amount: 0,
        target_date: "",
        color: "blue",
        icon: "Target",
      });
    },
    onError: (error: Error) => {
      toast({
        title: "Error creating goal",
        description: error.message,
        variant: "destructive",
      });
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validation
    if (!formData.name.trim()) {
      toast({
        title: "Validation error",
        description: "Goal name is required",
        variant: "destructive",
      });
      return;
    }

    if (formData.target_amount <= 0) {
      toast({
        title: "Validation error",
        description: "Target amount must be greater than 0",
        variant: "destructive",
      });
      return;
    }

    createMutation.mutate(formData);
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button size="sm" className="gap-2">
          <Plus className="h-4 w-4" />
          New Goal
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[425px]">
        <form onSubmit={handleSubmit}>
          <DialogHeader>
            <DialogTitle>Create Savings Goal</DialogTitle>
            <DialogDescription>
              Set a new financial goal to track your progress.
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <Label htmlFor="name">Goal Name</Label>
              <Input
                id="name"
                placeholder="e.g., Emergency Fund"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                required
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="target_amount">Target Amount (R)</Label>
              <Input
                id="target_amount"
                type="number"
                step="0.01"
                min="0"
                placeholder="15000.00"
                value={formData.target_amount || ""}
                onChange={(e) => setFormData({ ...formData, target_amount: parseFloat(e.target.value) || 0 })}
                required
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="current_amount">Current Amount (R)</Label>
              <Input
                id="current_amount"
                type="number"
                step="0.01"
                min="0"
                placeholder="0.00"
                value={formData.current_amount || ""}
                onChange={(e) => setFormData({ ...formData, current_amount: parseFloat(e.target.value) || 0 })}
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="target_date">Target Date (Optional)</Label>
              <Input
                id="target_date"
                type="date"
                value={formData.target_date || ""}
                onChange={(e) => setFormData({ ...formData, target_date: e.target.value })}
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="icon">Icon</Label>
              <select
                id="icon"
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                value={formData.icon}
                onChange={(e) => setFormData({ ...formData, icon: e.target.value })}
              >
                <option value="Target">Target</option>
                <option value="Home">Home</option>
                <option value="Plane">Plane</option>
                <option value="PiggyBank">Piggy Bank</option>
                <option value="Car">Car</option>
              </select>
            </div>
          </div>
          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => setOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={createMutation.isPending}>
              {createMutation.isPending ? "Creating..." : "Create Goal"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
};

