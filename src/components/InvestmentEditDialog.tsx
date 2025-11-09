import { useState, useEffect } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import * as api from "@/services/api";
import { useToast } from "@/hooks/use-toast";

interface InvestmentEditDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  investment: api.Investment;
}

export const InvestmentEditDialog = ({ open, onOpenChange, investment }: InvestmentEditDialogProps) => {
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const [formData, setFormData] = useState<api.InvestmentUpdate>({});
  const [priceUpdate, setPriceUpdate] = useState<api.PriceUpdate>({
    current_price: investment.current_price,
    last_updated: new Date().toISOString().split('T')[0],
  });

  useEffect(() => {
    setFormData({
      name: investment.name,
      type: investment.type,
      currency: investment.currency,
      quantity: investment.quantity,
      average_cost: investment.average_cost,
      current_price: investment.current_price,
      last_updated: investment.last_updated,
      notes: investment.notes,
    });
    setPriceUpdate({
      current_price: investment.current_price,
      last_updated: new Date().toISOString().split('T')[0],
    });
  }, [investment]);

  const updateMutation = useMutation({
    mutationFn: (data: api.InvestmentUpdate) => api.updateInvestment(investment.id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['investments'] });
      queryClient.invalidateQueries({ queryKey: ['portfolio-summary'] });
      toast({
        title: "Investment updated",
        description: `${investment.symbol} has been updated.`,
      });
      onOpenChange(false);
    },
    onError: (err: Error) => {
      toast({
        title: "Error updating investment",
        description: err.message || "Failed to update investment",
        variant: "destructive",
      });
    },
  });

  const updatePriceMutation = useMutation({
    mutationFn: (data: api.PriceUpdate) => api.updateInvestmentPrice(investment.id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['investments'] });
      queryClient.invalidateQueries({ queryKey: ['portfolio-summary'] });
      toast({
        title: "Price updated",
        description: `${investment.symbol} price has been updated.`,
      });
      onOpenChange(false);
    },
    onError: (err: Error) => {
      toast({
        title: "Error updating price",
        description: err.message || "Failed to update price",
        variant: "destructive",
      });
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    updateMutation.mutate(formData);
  };

  const handlePriceUpdate = (e: React.FormEvent) => {
    e.preventDefault();
    updatePriceMutation.mutate(priceUpdate);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Edit Investment: {investment.symbol}</DialogTitle>
          <DialogDescription>
            Update investment details or current price
          </DialogDescription>
        </DialogHeader>

        <Tabs defaultValue="details" className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="details">Details</TabsTrigger>
            <TabsTrigger value="price">Update Price</TabsTrigger>
          </TabsList>

          {/* Details Tab */}
          <TabsContent value="details">
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Type */}
                <div className="space-y-2">
                  <Label htmlFor="type">Type</Label>
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
              </div>

              {/* Name */}
              <div className="space-y-2">
                <Label htmlFor="name">Name</Label>
                <Input
                  id="name"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Quantity */}
                <div className="space-y-2">
                  <Label htmlFor="quantity">Quantity</Label>
                  <Input
                    id="quantity"
                    type="number"
                    step="0.0001"
                    min="0"
                    value={formData.quantity}
                    onChange={(e) => setFormData({ ...formData, quantity: parseFloat(e.target.value) || 0 })}
                  />
                </div>

                {/* Average Cost */}
                <div className="space-y-2">
                  <Label htmlFor="average_cost">Average Cost per Unit</Label>
                  <Input
                    id="average_cost"
                    type="number"
                    step="0.01"
                    min="0"
                    value={formData.average_cost}
                    onChange={(e) => setFormData({ ...formData, average_cost: parseFloat(e.target.value) || 0 })}
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Current Price */}
                <div className="space-y-2">
                  <Label htmlFor="current_price">Current Price</Label>
                  <Input
                    id="current_price"
                    type="number"
                    step="0.01"
                    min="0"
                    value={formData.current_price}
                    onChange={(e) => setFormData({ ...formData, current_price: parseFloat(e.target.value) || 0 })}
                  />
                </div>

                {/* Last Updated */}
                <div className="space-y-2">
                  <Label htmlFor="last_updated">Last Price Update</Label>
                  <Input
                    id="last_updated"
                    type="date"
                    value={formData.last_updated}
                    onChange={(e) => setFormData({ ...formData, last_updated: e.target.value })}
                  />
                </div>
              </div>

              {/* Notes */}
              <div className="space-y-2">
                <Label htmlFor="notes">Notes</Label>
                <Textarea
                  id="notes"
                  value={formData.notes}
                  onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                  rows={3}
                />
              </div>

              <DialogFooter>
                <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
                  Cancel
                </Button>
                <Button type="submit" disabled={updateMutation.isPending}>
                  {updateMutation.isPending ? "Updating..." : "Update Investment"}
                </Button>
              </DialogFooter>
            </form>
          </TabsContent>

          {/* Price Update Tab */}
          <TabsContent value="price">
            <form onSubmit={handlePriceUpdate} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="new_price">New Price</Label>
                <Input
                  id="new_price"
                  type="number"
                  step="0.01"
                  min="0"
                  placeholder="0.00"
                  value={priceUpdate.current_price}
                  onChange={(e) => setPriceUpdate({ ...priceUpdate, current_price: parseFloat(e.target.value) || 0 })}
                  required
                />
                <p className="text-sm text-muted-foreground">
                  Current price: {investment.currency} {investment.current_price.toFixed(2)}
                </p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="price_date">Update Date</Label>
                <Input
                  id="price_date"
                  type="date"
                  value={priceUpdate.last_updated}
                  onChange={(e) => setPriceUpdate({ ...priceUpdate, last_updated: e.target.value })}
                />
              </div>

              <DialogFooter>
                <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
                  Cancel
                </Button>
                <Button type="submit" disabled={updatePriceMutation.isPending}>
                  {updatePriceMutation.isPending ? "Updating..." : "Update Price"}
                </Button>
              </DialogFooter>
            </form>
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  );
};

