import { useState, useEffect } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import * as api from "@/services/api";
import { useToast } from "@/hooks/use-toast";

interface ExchangeRateEditDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  exchangeRate: api.ExchangeRate;
}

export const ExchangeRateEditDialog = ({ open, onOpenChange, exchangeRate }: ExchangeRateEditDialogProps) => {
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const [formData, setFormData] = useState<api.ExchangeRateUpdate>({});

  useEffect(() => {
    setFormData({
      rate: exchangeRate.rate,
      date: exchangeRate.date,
      source: exchangeRate.source,
    });
  }, [exchangeRate]);

  const updateMutation = useMutation({
    mutationFn: (data: api.ExchangeRateUpdate) => api.updateExchangeRate(exchangeRate.id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['exchange-rates'] });
      toast({
        title: "Exchange rate updated",
        description: `Rate from ${exchangeRate.from_currency} to ${exchangeRate.to_currency} has been updated.`,
      });
      onOpenChange(false);
    },
    onError: (err: Error) => {
      toast({
        title: "Error updating exchange rate",
        description: err.message || "Failed to update exchange rate",
        variant: "destructive",
      });
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validation
    if (formData.rate !== undefined && formData.rate <= 0) {
      toast({
        title: "Validation error",
        description: "Exchange rate must be greater than 0",
        variant: "destructive",
      });
      return;
    }

    updateMutation.mutate(formData);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>Edit Exchange Rate</DialogTitle>
          <DialogDescription>
            Update exchange rate from {exchangeRate.from_currency} to {exchangeRate.to_currency}
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Currency Pair (Read-only) */}
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>From Currency</Label>
              <Input value={exchangeRate.from_currency} disabled />
            </div>
            <div className="space-y-2">
              <Label>To Currency</Label>
              <Input value={exchangeRate.to_currency} disabled />
            </div>
          </div>

          {/* Exchange Rate */}
          <div className="space-y-2">
            <Label htmlFor="rate">Exchange Rate *</Label>
            <Input
              id="rate"
              type="number"
              step="0.000001"
              min="0"
              placeholder="0.000000"
              value={formData.rate}
              onChange={(e) => setFormData({ ...formData, rate: parseFloat(e.target.value) || 0 })}
              required
            />
            <p className="text-xs text-muted-foreground">
              1 {exchangeRate.from_currency} = {(formData.rate || 0).toFixed(6)} {exchangeRate.to_currency}
            </p>
          </div>

          {/* Date */}
          <div className="space-y-2">
            <Label htmlFor="date">Date *</Label>
            <Input
              id="date"
              type="date"
              value={formData.date}
              onChange={(e) => setFormData({ ...formData, date: e.target.value })}
              required
            />
          </div>

          {/* Source */}
          <div className="space-y-2">
            <Label htmlFor="source">Source</Label>
            <Select
              value={formData.source}
              onValueChange={(value) => setFormData({ ...formData, source: value })}
            >
              <SelectTrigger id="source">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="manual">Manual</SelectItem>
                <SelectItem value="api">API</SelectItem>
                <SelectItem value="bank">Bank</SelectItem>
                <SelectItem value="market">Market</SelectItem>
                <SelectItem value="other">Other</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Example Calculation */}
          {formData.rate && formData.rate > 0 && (
            <div className="p-3 bg-muted rounded-lg">
              <p className="text-sm font-medium mb-1">Example Conversion:</p>
              <p className="text-sm text-muted-foreground">
                100 {exchangeRate.from_currency} = {(100 * formData.rate).toFixed(2)} {exchangeRate.to_currency}
              </p>
              <p className="text-sm text-muted-foreground">
                100 {exchangeRate.to_currency} = {(100 / formData.rate).toFixed(2)} {exchangeRate.from_currency}
              </p>
            </div>
          )}

          {/* Original Rate Info */}
          <div className="p-3 border rounded-lg">
            <p className="text-sm font-medium mb-1">Original Rate:</p>
            <p className="text-sm text-muted-foreground">
              {exchangeRate.rate.toFixed(6)} (as of {new Date(exchangeRate.date).toLocaleDateString()})
            </p>
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={updateMutation.isPending}>
              {updateMutation.isPending ? "Updating..." : "Update Rate"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
};

