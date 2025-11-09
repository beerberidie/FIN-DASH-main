import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import * as api from "@/services/api";
import { useToast } from "@/hooks/use-toast";

interface ExchangeRateCreateDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export const ExchangeRateCreateDialog = ({ open, onOpenChange }: ExchangeRateCreateDialogProps) => {
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const [formData, setFormData] = useState<api.ExchangeRateCreate>({
    from_currency: 'USD',
    to_currency: 'ZAR',
    rate: 0,
    date: new Date().toISOString().split('T')[0],
    source: 'manual',
  });

  // Fetch currencies for dropdowns
  const { data: currencies } = useQuery({
    queryKey: ['currencies'],
    queryFn: () => api.getCurrencies(true), // Only active currencies
  });

  const createMutation = useMutation({
    mutationFn: api.createExchangeRate,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['exchange-rates'] });
      toast({
        title: "Exchange rate created",
        description: `Rate from ${formData.from_currency} to ${formData.to_currency} has been added.`,
      });
      onOpenChange(false);
      resetForm();
    },
    onError: (err: Error) => {
      toast({
        title: "Error creating exchange rate",
        description: err.message || "Failed to create exchange rate",
        variant: "destructive",
      });
    },
  });

  const resetForm = () => {
    setFormData({
      from_currency: 'USD',
      to_currency: 'ZAR',
      rate: 0,
      date: new Date().toISOString().split('T')[0],
      source: 'manual',
    });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validation
    if (formData.from_currency === formData.to_currency) {
      toast({
        title: "Validation error",
        description: "From and To currencies must be different",
        variant: "destructive",
      });
      return;
    }
    
    if (formData.rate <= 0) {
      toast({
        title: "Validation error",
        description: "Exchange rate must be greater than 0",
        variant: "destructive",
      });
      return;
    }

    createMutation.mutate(formData);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>Add Exchange Rate</DialogTitle>
          <DialogDescription>
            Create a new exchange rate between two currencies
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            {/* From Currency */}
            <div className="space-y-2">
              <Label htmlFor="from_currency">From Currency *</Label>
              <Select
                value={formData.from_currency}
                onValueChange={(value) => setFormData({ ...formData, from_currency: value })}
              >
                <SelectTrigger id="from_currency">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {currencies?.map((currency) => (
                    <SelectItem key={currency.code} value={currency.code}>
                      {currency.code} - {currency.symbol}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* To Currency */}
            <div className="space-y-2">
              <Label htmlFor="to_currency">To Currency *</Label>
              <Select
                value={formData.to_currency}
                onValueChange={(value) => setFormData({ ...formData, to_currency: value })}
              >
                <SelectTrigger id="to_currency">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {currencies?.map((currency) => (
                    <SelectItem key={currency.code} value={currency.code}>
                      {currency.code} - {currency.symbol}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
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
              1 {formData.from_currency} = {formData.rate.toFixed(6)} {formData.to_currency}
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
          {formData.rate > 0 && (
            <div className="p-3 bg-muted rounded-lg">
              <p className="text-sm font-medium mb-1">Example Conversion:</p>
              <p className="text-sm text-muted-foreground">
                100 {formData.from_currency} = {(100 * formData.rate).toFixed(2)} {formData.to_currency}
              </p>
              <p className="text-sm text-muted-foreground">
                100 {formData.to_currency} = {(100 / formData.rate).toFixed(2)} {formData.from_currency}
              </p>
            </div>
          )}

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => {
                onOpenChange(false);
                resetForm();
              }}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={createMutation.isPending}>
              {createMutation.isPending ? "Creating..." : "Create Rate"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
};

