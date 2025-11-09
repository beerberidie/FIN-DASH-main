import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import * as api from "@/services/api";
import { useToast } from "@/hooks/use-toast";

interface InvestmentCreateDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export const InvestmentCreateDialog = ({ open, onOpenChange }: InvestmentCreateDialogProps) => {
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const [formData, setFormData] = useState<api.InvestmentCreate>({
    symbol: '',
    name: '',
    type: 'stock',
    currency: 'USD',
    quantity: 0,
    average_cost: 0,
    current_price: 0,
    last_updated: new Date().toISOString().split('T')[0],
    notes: '',
  });

  const createMutation = useMutation({
    mutationFn: api.createInvestment,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['investments'] });
      queryClient.invalidateQueries({ queryKey: ['portfolio-summary'] });
      toast({
        title: "Investment created",
        description: `${formData.symbol} has been added to your portfolio.`,
      });
      onOpenChange(false);
      resetForm();
    },
    onError: (err: Error) => {
      toast({
        title: "Error creating investment",
        description: err.message || "Failed to create investment",
        variant: "destructive",
      });
    },
  });

  const resetForm = () => {
    setFormData({
      symbol: '',
      name: '',
      type: 'stock',
      currency: 'USD',
      quantity: 0,
      average_cost: 0,
      current_price: 0,
      last_updated: new Date().toISOString().split('T')[0],
      notes: '',
    });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validation
    if (!formData.symbol.trim()) {
      toast({
        title: "Validation error",
        description: "Symbol is required",
        variant: "destructive",
      });
      return;
    }
    
    if (!formData.name.trim()) {
      toast({
        title: "Validation error",
        description: "Name is required",
        variant: "destructive",
      });
      return;
    }

    createMutation.mutate(formData);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Add New Investment</DialogTitle>
          <DialogDescription>
            Add a new investment to your portfolio
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Symbol */}
            <div className="space-y-2">
              <Label htmlFor="symbol">Symbol *</Label>
              <Input
                id="symbol"
                placeholder="e.g., AAPL, BTC"
                value={formData.symbol}
                onChange={(e) => setFormData({ ...formData, symbol: e.target.value.toUpperCase() })}
                required
              />
            </div>

            {/* Type */}
            <div className="space-y-2">
              <Label htmlFor="type">Type *</Label>
              <Select
                value={formData.type}
                onValueChange={(value: api.InvestmentType) => setFormData({ ...formData, type: value })}
              >
                <SelectTrigger id="type">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="stock">Stock</SelectItem>
                  <SelectItem value="etf">ETF</SelectItem>
                  <SelectItem value="crypto">Crypto</SelectItem>
                  <SelectItem value="bond">Bond</SelectItem>
                  <SelectItem value="mutual_fund">Mutual Fund</SelectItem>
                  <SelectItem value="other">Other</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Name */}
          <div className="space-y-2">
            <Label htmlFor="name">Name *</Label>
            <Input
              id="name"
              placeholder="e.g., Apple Inc., Bitcoin"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              required
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Currency */}
            <div className="space-y-2">
              <Label htmlFor="currency">Currency</Label>
              <Select
                value={formData.currency}
                onValueChange={(value) => setFormData({ ...formData, currency: value })}
              >
                <SelectTrigger id="currency">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="USD">USD</SelectItem>
                  <SelectItem value="EUR">EUR</SelectItem>
                  <SelectItem value="GBP">GBP</SelectItem>
                  <SelectItem value="ZAR">ZAR</SelectItem>
                  <SelectItem value="JPY">JPY</SelectItem>
                  <SelectItem value="AUD">AUD</SelectItem>
                  <SelectItem value="CAD">CAD</SelectItem>
                  <SelectItem value="CHF">CHF</SelectItem>
                  <SelectItem value="CNY">CNY</SelectItem>
                  <SelectItem value="INR">INR</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Quantity */}
            <div className="space-y-2">
              <Label htmlFor="quantity">Quantity</Label>
              <Input
                id="quantity"
                type="number"
                step="0.0001"
                min="0"
                placeholder="0.0000"
                value={formData.quantity}
                onChange={(e) => setFormData({ ...formData, quantity: parseFloat(e.target.value) || 0 })}
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Average Cost */}
            <div className="space-y-2">
              <Label htmlFor="average_cost">Average Cost per Unit</Label>
              <Input
                id="average_cost"
                type="number"
                step="0.01"
                min="0"
                placeholder="0.00"
                value={formData.average_cost}
                onChange={(e) => setFormData({ ...formData, average_cost: parseFloat(e.target.value) || 0 })}
              />
            </div>

            {/* Current Price */}
            <div className="space-y-2">
              <Label htmlFor="current_price">Current Price</Label>
              <Input
                id="current_price"
                type="number"
                step="0.01"
                min="0"
                placeholder="0.00"
                value={formData.current_price}
                onChange={(e) => setFormData({ ...formData, current_price: parseFloat(e.target.value) || 0 })}
              />
            </div>
          </div>

          {/* Last Updated */}
          <div className="space-y-2">
            <Label htmlFor="last_updated">Last Price Update</Label>
            <Input
              id="last_updated"
              type="date"
              value={formData.last_updated}
              onChange={(e) => setFormData({ ...formData, last_updated: e.target.value })}
              required
            />
          </div>

          {/* Notes */}
          <div className="space-y-2">
            <Label htmlFor="notes">Notes</Label>
            <Textarea
              id="notes"
              placeholder="Additional notes about this investment..."
              value={formData.notes}
              onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
              rows={3}
            />
          </div>

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
              {createMutation.isPending ? "Creating..." : "Create Investment"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
};

