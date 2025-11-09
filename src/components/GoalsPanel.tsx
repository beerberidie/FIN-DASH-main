import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Target, Home, Plane, PiggyBank, Circle, Trash2 } from "lucide-react";
import api from "@/services/api";
import { formatCurrency } from "@/lib/formatters";
import { useToast } from "@/hooks/use-toast";
import { GoalCreateDialog } from "./GoalCreateDialog";
import { GoalContributeDialog } from "./GoalContributeDialog";

// Icon mapping for goals
const iconMap: Record<string, React.ReactNode> = {
  Target: <Target className="h-5 w-5" />,
  Home: <Home className="h-5 w-5" />,
  Plane: <Plane className="h-5 w-5" />,
  PiggyBank: <PiggyBank className="h-5 w-5" />,
  Circle: <Circle className="h-5 w-5" />,
};

interface GoalWithProgress {
  id: string;
  name: string;
  current_amount: number;
  target_amount: number;
  progress_percent: number;
  remaining: number;
  icon: React.ReactNode;
  color: string;
}

interface GoalItemProps {
  goal: GoalWithProgress;
  onDelete: (goal: GoalWithProgress) => void;
}

const GoalItem = ({ goal, onDelete }: GoalItemProps) => {
  const percentage = goal.progress_percent;
  const remaining = goal.remaining;

  return (
    <div className="space-y-3 p-4 rounded-lg bg-muted/30 hover:bg-muted/50 transition-colors">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className={`p-2 rounded-lg ${goal.color} text-white`}>
            {goal.icon}
          </div>
          <div>
            <p className="font-semibold text-foreground">{goal.name}</p>
            <p className="text-xs text-muted-foreground">
              {formatCurrency(remaining)} remaining
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-lg font-bold text-foreground">{percentage.toFixed(0)}%</span>
          <GoalContributeDialog
            goalId={goal.id}
            goalName={goal.name}
            currentAmount={goal.current_amount}
            targetAmount={goal.target_amount}
          />
          <Button
            variant="outline"
            size="icon"
            onClick={() => onDelete(goal)}
          >
            <Trash2 className="h-4 w-4 text-destructive" />
          </Button>
        </div>
      </div>
      <div className="space-y-2">
        <Progress value={percentage} className="h-2 bg-muted" />
        <div className="flex items-center justify-between text-xs text-muted-foreground">
          <span>{formatCurrency(goal.current_amount)}</span>
          <span>{formatCurrency(goal.target_amount)}</span>
        </div>
      </div>
    </div>
  );
};

const GoalSkeleton = () => (
  <div className="space-y-3 p-4 rounded-lg bg-muted/30">
    <div className="flex items-center justify-between">
      <div className="flex items-center gap-3">
        <Skeleton className="h-10 w-10 rounded-lg" />
        <div className="space-y-2">
          <Skeleton className="h-4 w-24" />
          <Skeleton className="h-3 w-20" />
        </div>
      </div>
      <Skeleton className="h-6 w-12" />
    </div>
    <Skeleton className="h-2 w-full" />
  </div>
);

export const GoalsPanel = () => {
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [goalToDelete, setGoalToDelete] = useState<GoalWithProgress | null>(null);

  const { data: summary, isLoading } = useQuery({
    queryKey: ['summary'],
    queryFn: api.getSummary,
    onError: (err: Error) => {
      toast({
        title: "Error loading goals",
        description: err.message,
        variant: "destructive",
      });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: api.deleteGoal,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['summary'] });
      queryClient.invalidateQueries({ queryKey: ['goals'] });
      toast({
        title: "Goal Deleted",
        description: "The goal has been successfully deleted.",
      });
      setDeleteDialogOpen(false);
      setGoalToDelete(null);
    },
    onError: (err: Error) => {
      toast({
        title: "Error deleting goal",
        description: err.message || "Failed to delete goal",
        variant: "destructive",
      });
    },
  });

  const handleDelete = (goal: GoalWithProgress) => {
    setGoalToDelete(goal);
    setDeleteDialogOpen(true);
  };

  const confirmDelete = () => {
    if (goalToDelete) {
      deleteMutation.mutate(goalToDelete.id);
    }
  };

  // Map summary goals to GoalWithProgress format
  const goals: GoalWithProgress[] = (summary?.goals || []).map((goal: any) => ({
    ...goal,
    icon: iconMap[goal.icon] || iconMap.Circle,
    color: "bg-primary", // Use a default color for now
  }));

  return (
    <Card className="p-6 bg-gradient-card shadow-md border-border">
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-xl font-bold text-foreground">Savings Goals</h3>
            <p className="text-sm text-muted-foreground mt-1">
              {isLoading ? 'Loading...' : `Track your ${goals.length} financial targets`}
            </p>
          </div>
          <GoalCreateDialog />
        </div>
        <div className="space-y-4">
          {isLoading ? (
            <>
              <GoalSkeleton />
              <GoalSkeleton />
              <GoalSkeleton />
            </>
          ) : goals.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              <p>No goals yet</p>
              <p className="text-sm mt-1">Create your first savings goal</p>
            </div>
          ) : (
            goals.map((goal) => (
              <GoalItem key={goal.id} goal={goal} onDelete={handleDelete} />
            ))
          )}
        </div>
      </div>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Goal?</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete "{goalToDelete?.name}"?
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
    </Card>
  );
};
