import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
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
import {
  ArrowUpRight,
  ArrowDownRight,
  ShoppingCart,
  Home,
  Utensils,
  Car,
  DollarSign,
  Zap,
  Smartphone,
  Film,
  Tv,
  PiggyBank,
  Target,
  CreditCard,
  Landmark,
  Briefcase,
  Circle,
  Upload,
  Trash2
} from "lucide-react";
import api, { Transaction as ApiTransaction, Category } from "@/services/api";
import { formatCurrency, formatDate } from "@/lib/formatters";
import { useToast } from "@/hooks/use-toast";
import { CSVImportDialog } from "./CSVImportDialog";
import { StatementImportDialog } from "./StatementImportDialog";
import { useState } from "react";

// Icon mapping for categories
const iconMap: Record<string, React.ReactNode> = {
  Home: <Home className="h-4 w-4" />,
  ShoppingCart: <ShoppingCart className="h-4 w-4" />,
  Car: <Car className="h-4 w-4" />,
  Utensils: <Utensils className="h-4 w-4" />,
  Zap: <Zap className="h-4 w-4" />,
  Smartphone: <Smartphone className="h-4 w-4" />,
  Film: <Film className="h-4 w-4" />,
  Tv: <Tv className="h-4 w-4" />,
  PiggyBank: <PiggyBank className="h-4 w-4" />,
  Target: <Target className="h-4 w-4" />,
  CreditCard: <CreditCard className="h-4 w-4" />,
  Landmark: <Landmark className="h-4 w-4" />,
  DollarSign: <DollarSign className="h-4 w-4" />,
  Briefcase: <Briefcase className="h-4 w-4" />,
  Circle: <Circle className="h-4 w-4" />,
};

interface TransactionWithCategory extends ApiTransaction {
  categoryName: string;
  categoryIcon: React.ReactNode;
}

interface TransactionRowProps {
  transaction: TransactionWithCategory;
  onDelete: (transaction: TransactionWithCategory) => void;
}

const TransactionRow = ({ transaction, onDelete }: TransactionRowProps) => (
  <div className="flex items-center justify-between py-4 border-b border-border last:border-0 hover:bg-muted/50 transition-colors px-2 rounded-md">
    <div className="flex items-center gap-4">
      <div className={`p-2 rounded-lg ${
        transaction.type === "income" ? "bg-success/10 text-success" : "bg-muted text-foreground"
      }`}>
        {transaction.type === "income" ? (
          <ArrowUpRight className="h-4 w-4" />
        ) : (
          <ArrowDownRight className="h-4 w-4" />
        )}
      </div>
      <div>
        <p className="font-medium text-foreground">{transaction.description}</p>
        <p className="text-sm text-muted-foreground">{formatDate(transaction.date)}</p>
      </div>
    </div>
    <div className="flex items-center gap-4">
      <Badge variant="secondary" className="hidden sm:inline-flex">
        <span className="mr-1">{transaction.categoryIcon}</span>
        {transaction.categoryName}
      </Badge>
      <span className={`font-bold ${
        transaction.type === "income" ? "text-success" : "text-foreground"
      }`}>
        {formatCurrency(transaction.amount)}
      </span>
      <Button
        variant="ghost"
        size="icon"
        onClick={() => onDelete(transaction)}
        className="h-8 w-8"
      >
        <Trash2 className="h-4 w-4 text-destructive" />
      </Button>
    </div>
  </div>
);

const TransactionSkeleton = () => (
  <div className="flex items-center justify-between py-4 border-b border-border">
    <div className="flex items-center gap-4">
      <Skeleton className="h-10 w-10 rounded-lg" />
      <div className="space-y-2">
        <Skeleton className="h-4 w-32" />
        <Skeleton className="h-3 w-24" />
      </div>
    </div>
    <div className="flex items-center gap-4">
      <Skeleton className="h-6 w-20 hidden sm:block" />
      <Skeleton className="h-6 w-24" />
    </div>
  </div>
);

export const TransactionsTable = () => {
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const [importDialogOpen, setImportDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [transactionToDelete, setTransactionToDelete] = useState<TransactionWithCategory | null>(null);

  // Fetch transactions
  const { data: transactions, isLoading: transactionsLoading } = useQuery({
    queryKey: ['transactions'],
    queryFn: () => api.getTransactions(),
    onError: (err: Error) => {
      toast({
        title: "Error loading transactions",
        description: err.message,
        variant: "destructive",
      });
    },
  });

  // Fetch categories
  const { data: categories, isLoading: categoriesLoading } = useQuery({
    queryKey: ['categories'],
    queryFn: api.getCategories,
  });

  const deleteMutation = useMutation({
    mutationFn: api.deleteTransaction,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['transactions'] });
      queryClient.invalidateQueries({ queryKey: ['summary'] });
      toast({
        title: "Transaction Deleted",
        description: "The transaction has been successfully deleted.",
      });
      setDeleteDialogOpen(false);
      setTransactionToDelete(null);
    },
    onError: (err: Error) => {
      toast({
        title: "Error deleting transaction",
        description: err.message || "Failed to delete transaction",
        variant: "destructive",
      });
    },
  });

  const handleDelete = (transaction: TransactionWithCategory) => {
    setTransactionToDelete(transaction);
    setDeleteDialogOpen(true);
  };

  const confirmDelete = () => {
    if (transactionToDelete) {
      deleteMutation.mutate(transactionToDelete.id);
    }
  };

  const isLoading = transactionsLoading || categoriesLoading;

  // Create category lookup map
  const categoryMap = new Map<string, Category>();
  categories?.forEach(cat => categoryMap.set(cat.id, cat));

  // Enrich transactions with category data
  const enrichedTransactions: TransactionWithCategory[] = (transactions || [])
    .slice(0, 5) // Show only last 5
    .map(tx => {
      const category = tx.category_id ? categoryMap.get(tx.category_id) : null;
      return {
        ...tx,
        categoryName: category?.name || 'Uncategorized',
        categoryIcon: category ? (iconMap[category.icon] || iconMap.Circle) : iconMap.Circle,
      };
    });

  return (
    <Card className="p-6 bg-gradient-card shadow-md border-border">
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-xl font-bold text-foreground">Recent Transactions</h3>
            <p className="text-sm text-muted-foreground mt-1">
              {isLoading ? 'Loading...' : `Last ${enrichedTransactions.length} transactions`}
            </p>
          </div>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setImportDialogOpen(true)}
            >
              <Upload className="h-4 w-4 mr-2" />
              Import Statement
            </Button>
            <CSVImportDialog />
            <Badge variant="outline" className="text-primary border-primary">
              View All
            </Badge>
          </div>
        </div>
        <div className="space-y-1">
          {isLoading ? (
            <>
              <TransactionSkeleton />
              <TransactionSkeleton />
              <TransactionSkeleton />
              <TransactionSkeleton />
              <TransactionSkeleton />
            </>
          ) : enrichedTransactions.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              <p>No transactions yet</p>
              <p className="text-sm mt-1">Start by adding your first transaction</p>
            </div>
          ) : (
            enrichedTransactions.map((transaction) => (
              <TransactionRow key={transaction.id} transaction={transaction} onDelete={handleDelete} />
            ))
          )}
        </div>
      </div>

      {/* Statement Import Dialog */}
      <StatementImportDialog open={importDialogOpen} onOpenChange={setImportDialogOpen} />

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Transaction?</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete the transaction "{transactionToDelete?.description}"
              for {transactionToDelete ? formatCurrency(transactionToDelete.amount) : ''}?
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
