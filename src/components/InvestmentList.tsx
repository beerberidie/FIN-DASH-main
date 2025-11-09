import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
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
import { 
  Plus, 
  TrendingUp, 
  TrendingDown, 
  Edit, 
  Trash2, 
  AlertCircle,
  Search,
  DollarSign
} from "lucide-react";
import * as api from "@/services/api";
import { formatCurrency } from "@/lib/formatters";
import { useToast } from "@/hooks/use-toast";
import { InvestmentCreateDialog } from "./InvestmentCreateDialog";
import { InvestmentEditDialog } from "./InvestmentEditDialog";

const getTypeColor = (type: string) => {
  const colors: Record<string, string> = {
    stock: 'bg-blue-100 text-blue-800',
    etf: 'bg-green-100 text-green-800',
    crypto: 'bg-purple-100 text-purple-800',
    bond: 'bg-yellow-100 text-yellow-800',
    mutual_fund: 'bg-indigo-100 text-indigo-800',
    other: 'bg-gray-100 text-gray-800',
  };
  return colors[type] || colors.other;
};

const getTypeLabel = (type: string) => {
  const labels: Record<string, string> = {
    stock: 'Stock',
    etf: 'ETF',
    crypto: 'Crypto',
    bond: 'Bond',
    mutual_fund: 'Mutual Fund',
    other: 'Other',
  };
  return labels[type] || type;
};

export const InvestmentList = () => {
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const [typeFilter, setTypeFilter] = useState<string>('all');
  const [symbolFilter, setSymbolFilter] = useState<string>('');
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [selectedInvestment, setSelectedInvestment] = useState<api.Investment | null>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [investmentToDelete, setInvestmentToDelete] = useState<api.Investment | null>(null);

  const { data: investments, isLoading, error } = useQuery({
    queryKey: ['investments', typeFilter === 'all' ? undefined : typeFilter, symbolFilter || undefined],
    queryFn: () => api.getInvestments(
      typeFilter === 'all' ? undefined : typeFilter,
      symbolFilter || undefined
    ),
    onError: (err: Error) => {
      toast({
        title: "Error loading investments",
        description: err.message || "Failed to load investments",
        variant: "destructive",
      });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: api.deleteInvestment,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['investments'] });
      queryClient.invalidateQueries({ queryKey: ['portfolio-summary'] });
      toast({
        title: "Investment deleted",
        description: "The investment has been successfully deleted.",
      });
      setDeleteDialogOpen(false);
      setInvestmentToDelete(null);
    },
    onError: (err: Error) => {
      toast({
        title: "Error deleting investment",
        description: err.message || "Failed to delete investment",
        variant: "destructive",
      });
    },
  });

  const handleEdit = (investment: api.Investment) => {
    setSelectedInvestment(investment);
    setEditDialogOpen(true);
  };

  const handleDelete = (investment: api.Investment) => {
    setInvestmentToDelete(investment);
    setDeleteDialogOpen(true);
  };

  const confirmDelete = () => {
    if (investmentToDelete) {
      deleteMutation.mutate(investmentToDelete.id);
    }
  };

  const calculateCurrentValue = (investment: api.Investment) => {
    return investment.quantity * investment.current_price;
  };

  const calculateProfitLoss = (investment: api.Investment) => {
    const currentValue = calculateCurrentValue(investment);
    const totalCost = investment.quantity * investment.average_cost;
    return currentValue - totalCost;
  };

  const calculateProfitLossPercentage = (investment: api.Investment) => {
    const totalCost = investment.quantity * investment.average_cost;
    if (totalCost === 0) return 0;
    const profitLoss = calculateProfitLoss(investment);
    return (profitLoss / totalCost) * 100;
  };

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <Skeleton className="h-6 w-48" />
          <Skeleton className="h-4 w-64 mt-2" />
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <Skeleton key={i} className="h-16 w-full" />
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <AlertCircle className="h-5 w-5 text-destructive" />
            Investments
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              {error.message || "Failed to load investments"}
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>
    );
  }

  return (
    <>
      <Card>
        <CardHeader>
          <div className="flex items-start justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <DollarSign className="h-6 w-6 text-primary" />
                Investments
              </CardTitle>
              <CardDescription>
                Manage your investment portfolio
              </CardDescription>
            </div>
            <Button onClick={() => setCreateDialogOpen(true)}>
              <Plus className="h-4 w-4 mr-2" />
              Add Investment
            </Button>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Filters */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Type</label>
              <Select value={typeFilter} onValueChange={setTypeFilter}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Types</SelectItem>
                  <SelectItem value="stock">Stocks</SelectItem>
                  <SelectItem value="etf">ETFs</SelectItem>
                  <SelectItem value="crypto">Crypto</SelectItem>
                  <SelectItem value="bond">Bonds</SelectItem>
                  <SelectItem value="mutual_fund">Mutual Funds</SelectItem>
                  <SelectItem value="other">Other</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Search Symbol</label>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search by symbol..."
                  value={symbolFilter}
                  onChange={(e) => setSymbolFilter(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
          </div>

          {/* Investments Table */}
          {investments && investments.length > 0 ? (
            <div className="border rounded-lg overflow-hidden">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Symbol</TableHead>
                    <TableHead>Name</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead className="text-right">Quantity</TableHead>
                    <TableHead className="text-right">Avg Cost</TableHead>
                    <TableHead className="text-right">Current Price</TableHead>
                    <TableHead className="text-right">Value</TableHead>
                    <TableHead className="text-right">P/L</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {investments.map((investment) => {
                    const profitLoss = calculateProfitLoss(investment);
                    const profitLossPercentage = calculateProfitLossPercentage(investment);
                    const isProfit = profitLoss >= 0;

                    return (
                      <TableRow key={investment.id}>
                        <TableCell className="font-bold">{investment.symbol}</TableCell>
                        <TableCell>{investment.name}</TableCell>
                        <TableCell>
                          <Badge className={getTypeColor(investment.type)}>
                            {getTypeLabel(investment.type)}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-right">{investment.quantity.toFixed(4)}</TableCell>
                        <TableCell className="text-right">
                          {formatCurrency(investment.average_cost)}
                        </TableCell>
                        <TableCell className="text-right">
                          {formatCurrency(investment.current_price)}
                        </TableCell>
                        <TableCell className="text-right font-semibold">
                          {formatCurrency(calculateCurrentValue(investment))}
                        </TableCell>
                        <TableCell className="text-right">
                          <div className={`flex items-center justify-end gap-1 ${isProfit ? 'text-green-600' : 'text-red-600'}`}>
                            {isProfit ? <TrendingUp className="h-4 w-4" /> : <TrendingDown className="h-4 w-4" />}
                            <span className="font-semibold">
                              {isProfit ? '+' : ''}{formatCurrency(profitLoss)}
                            </span>
                            <span className="text-xs">
                              ({isProfit ? '+' : ''}{profitLossPercentage.toFixed(2)}%)
                            </span>
                          </div>
                        </TableCell>
                        <TableCell className="text-right">
                          <div className="flex items-center justify-end gap-2">
                            <Button
                              variant="ghost"
                              size="icon"
                              onClick={() => handleEdit(investment)}
                            >
                              <Edit className="h-4 w-4" />
                            </Button>
                            <Button
                              variant="ghost"
                              size="icon"
                              onClick={() => handleDelete(investment)}
                            >
                              <Trash2 className="h-4 w-4 text-destructive" />
                            </Button>
                          </div>
                        </TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            </div>
          ) : (
            <Alert>
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>
                No investments found. Click "Add Investment" to get started.
              </AlertDescription>
            </Alert>
          )}
        </CardContent>
      </Card>

      {/* Create Dialog */}
      <InvestmentCreateDialog
        open={createDialogOpen}
        onOpenChange={setCreateDialogOpen}
      />

      {/* Edit Dialog */}
      {selectedInvestment && (
        <InvestmentEditDialog
          open={editDialogOpen}
          onOpenChange={setEditDialogOpen}
          investment={selectedInvestment}
        />
      )}

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Investment?</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete {investmentToDelete?.symbol} ({investmentToDelete?.name})?
              This will also delete all associated transactions. This action cannot be undone.
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
    </>
  );
};

