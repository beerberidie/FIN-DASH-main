import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
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
import { Plus, Edit, Trash2, AlertCircle, TrendingUp, Calendar } from "lucide-react";
import * as api from "@/services/api";
import { useToast } from "@/hooks/use-toast";
import { ExchangeRateCreateDialog } from "./ExchangeRateCreateDialog";
import { ExchangeRateEditDialog } from "./ExchangeRateEditDialog";

export const ExchangeRateManager = () => {
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [selectedRate, setSelectedRate] = useState<api.ExchangeRate | null>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [rateToDelete, setRateToDelete] = useState<api.ExchangeRate | null>(null);

  const { data: rates, isLoading, error } = useQuery({
    queryKey: ['exchange-rates'],
    queryFn: () => api.getExchangeRates(),
    onError: (err: Error) => {
      toast({
        title: "Error loading exchange rates",
        description: err.message || "Failed to load exchange rates",
        variant: "destructive",
      });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: api.deleteExchangeRate,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['exchange-rates'] });
      toast({
        title: "Exchange rate deleted",
        description: "The exchange rate has been successfully deleted.",
      });
      setDeleteDialogOpen(false);
      setRateToDelete(null);
    },
    onError: (err: Error) => {
      toast({
        title: "Error deleting exchange rate",
        description: err.message || "Failed to delete exchange rate",
        variant: "destructive",
      });
    },
  });

  const handleEdit = (rate: api.ExchangeRate) => {
    setSelectedRate(rate);
    setEditDialogOpen(true);
  };

  const handleDelete = (rate: api.ExchangeRate) => {
    setRateToDelete(rate);
    setDeleteDialogOpen(true);
  };

  const confirmDelete = () => {
    if (rateToDelete) {
      deleteMutation.mutate(rateToDelete.id);
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
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
            Exchange Rates
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              {error.message || "Failed to load exchange rates"}
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>
    );
  }

  // Group rates by currency pair
  const groupedRates = rates?.reduce((acc, rate) => {
    const key = `${rate.from_currency}-${rate.to_currency}`;
    if (!acc[key]) {
      acc[key] = [];
    }
    acc[key].push(rate);
    return acc;
  }, {} as Record<string, api.ExchangeRate[]>);

  // Get latest rate for each pair
  const latestRates = Object.entries(groupedRates || {}).map(([pair, pairRates]) => {
    const sorted = pairRates.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());
    return sorted[0];
  });

  return (
    <>
      <Card>
        <CardHeader>
          <div className="flex items-start justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="h-6 w-6 text-primary" />
                Exchange Rates
              </CardTitle>
              <CardDescription>
                Manage currency exchange rates for multi-currency transactions
              </CardDescription>
            </div>
            <Button onClick={() => setCreateDialogOpen(true)}>
              <Plus className="h-4 w-4 mr-2" />
              Add Rate
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {latestRates && latestRates.length > 0 ? (
            <div className="border rounded-lg overflow-hidden">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>From</TableHead>
                    <TableHead>To</TableHead>
                    <TableHead className="text-right">Rate</TableHead>
                    <TableHead>Date</TableHead>
                    <TableHead>Source</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {latestRates.map((rate) => (
                    <TableRow key={rate.id}>
                      <TableCell className="font-bold">{rate.from_currency}</TableCell>
                      <TableCell className="font-bold">{rate.to_currency}</TableCell>
                      <TableCell className="text-right font-semibold">
                        {rate.rate.toFixed(6)}
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <Calendar className="h-4 w-4 text-muted-foreground" />
                          {formatDate(rate.date)}
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge variant="outline" className="capitalize">
                          {rate.source}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-right">
                        <div className="flex items-center justify-end gap-2">
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => handleEdit(rate)}
                          >
                            <Edit className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => handleDelete(rate)}
                          >
                            <Trash2 className="h-4 w-4 text-destructive" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          ) : (
            <Alert>
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>
                No exchange rates found. Click "Add Rate" to create your first exchange rate.
              </AlertDescription>
            </Alert>
          )}

          {/* Info Box */}
          <div className="mt-6 p-4 bg-muted rounded-lg">
            <h4 className="font-semibold text-sm mb-2">Exchange Rate Information</h4>
            <ul className="text-sm text-muted-foreground space-y-1">
              <li>• Exchange rates are used for multi-currency conversions</li>
              <li>• Format: 1 FROM currency = RATE TO currency</li>
              <li>• Latest rate is used when no specific date is provided</li>
              <li>• Historical rates are maintained for accurate reporting</li>
              <li>• Source can be "manual", "api", or other custom values</li>
            </ul>
          </div>
        </CardContent>
      </Card>

      {/* Create Dialog */}
      <ExchangeRateCreateDialog
        open={createDialogOpen}
        onOpenChange={setCreateDialogOpen}
      />

      {/* Edit Dialog */}
      {selectedRate && (
        <ExchangeRateEditDialog
          open={editDialogOpen}
          onOpenChange={setEditDialogOpen}
          exchangeRate={selectedRate}
        />
      )}

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Exchange Rate?</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete the exchange rate from {rateToDelete?.from_currency} to{' '}
              {rateToDelete?.to_currency} ({formatDate(rateToDelete?.date || '')})?
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
    </>
  );
};

