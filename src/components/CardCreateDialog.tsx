import { useState } from 'react';
import { useMutation, useQueryClient, useQuery } from '@tanstack/react-query';
import { createCard, CardCreate, getAccounts } from '@/services/api';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { useToast } from '@/hooks/use-toast';
import { Loader2 } from 'lucide-react';

interface CardCreateDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

const CARD_COLORS = [
  { value: '#dc2626', label: 'Red' },
  { value: '#2563eb', label: 'Blue' },
  { value: '#16a34a', label: 'Green' },
  { value: '#9333ea', label: 'Purple' },
  { value: '#ea580c', label: 'Orange' },
  { value: '#0891b2', label: 'Cyan' },
  { value: '#4f46e5', label: 'Indigo' },
  { value: '#64748b', label: 'Gray' },
];

export function CardCreateDialog({ open, onOpenChange }: CardCreateDialogProps) {
  const { toast } = useToast();
  const queryClient = useQueryClient();

  const [formData, setFormData] = useState<CardCreate>({
    name: '',
    card_type: 'credit',
    last_four_digits: '',
    account_id: '',
    issuer: '',
    available_balance: 0,
    current_balance: 0,
    credit_limit: null,
    expiry_month: null,
    expiry_year: null,
    is_active: true,
    color: '#dc2626',
    icon: 'CreditCard',
  });

  const { data: accounts = [] } = useQuery({
    queryKey: ['accounts'],
    queryFn: getAccounts,
  });

  const createMutation = useMutation({
    mutationFn: createCard,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cards'] });
      toast({
        title: 'Success',
        description: 'Card created successfully',
      });
      onOpenChange(false);
      resetForm();
    },
    onError: (error: Error) => {
      toast({
        title: 'Error',
        description: error.message,
        variant: 'destructive',
      });
    },
  });

  const resetForm = () => {
    setFormData({
      name: '',
      card_type: 'credit',
      last_four_digits: '',
      account_id: '',
      issuer: '',
      available_balance: 0,
      current_balance: 0,
      credit_limit: null,
      expiry_month: null,
      expiry_year: null,
      is_active: true,
      color: '#dc2626',
      icon: 'CreditCard',
    });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validation
    if (!formData.name || !formData.last_four_digits || !formData.account_id || !formData.issuer) {
      toast({
        title: 'Validation Error',
        description: 'Please fill in all required fields',
        variant: 'destructive',
      });
      return;
    }

    if (formData.last_four_digits.length !== 4) {
      toast({
        title: 'Validation Error',
        description: 'Last four digits must be exactly 4 digits',
        variant: 'destructive',
      });
      return;
    }

    createMutation.mutate(formData);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Add New Card</DialogTitle>
          <DialogDescription>
            Add a new payment card to track transactions and balances.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit}>
          <div className="grid gap-4 py-4">
            {/* Card Name */}
            <div className="grid gap-2">
              <Label htmlFor="name">Card Name *</Label>
              <Input
                id="name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="e.g., Standard Bank Credit Card"
              />
            </div>

            {/* Card Type */}
            <div className="grid gap-2">
              <Label htmlFor="card_type">Card Type *</Label>
              <Select
                value={formData.card_type}
                onValueChange={(value: 'credit' | 'debit' | 'prepaid' | 'virtual') =>
                  setFormData({ ...formData, card_type: value })
                }
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="credit">Credit Card</SelectItem>
                  <SelectItem value="debit">Debit Card</SelectItem>
                  <SelectItem value="prepaid">Prepaid Card</SelectItem>
                  <SelectItem value="virtual">Virtual Card</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Issuer */}
            <div className="grid gap-2">
              <Label htmlFor="issuer">Issuer *</Label>
              <Input
                id="issuer"
                value={formData.issuer}
                onChange={(e) => setFormData({ ...formData, issuer: e.target.value })}
                placeholder="e.g., Standard Bank, FNB, Capitec"
              />
            </div>

            {/* Last Four Digits */}
            <div className="grid gap-2">
              <Label htmlFor="last_four_digits">Last Four Digits *</Label>
              <Input
                id="last_four_digits"
                value={formData.last_four_digits}
                onChange={(e) => {
                  const value = e.target.value.replace(/\D/g, '').slice(0, 4);
                  setFormData({ ...formData, last_four_digits: value });
                }}
                placeholder="1234"
                maxLength={4}
              />
            </div>

            {/* Account */}
            <div className="grid gap-2">
              <Label htmlFor="account_id">Linked Account *</Label>
              <Select
                value={formData.account_id}
                onValueChange={(value) => setFormData({ ...formData, account_id: value })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select account" />
                </SelectTrigger>
                <SelectContent>
                  {accounts.map((account) => (
                    <SelectItem key={account.id} value={account.id}>
                      {account.name} ({account.type})
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Expiry Date */}
            <div className="grid grid-cols-2 gap-4">
              <div className="grid gap-2">
                <Label htmlFor="expiry_month">Expiry Month</Label>
                <Input
                  id="expiry_month"
                  type="number"
                  min="1"
                  max="12"
                  value={formData.expiry_month || ''}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      expiry_month: e.target.value ? parseInt(e.target.value) : null,
                    })
                  }
                  placeholder="MM"
                />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="expiry_year">Expiry Year</Label>
                <Input
                  id="expiry_year"
                  type="number"
                  min={new Date().getFullYear()}
                  max={new Date().getFullYear() + 20}
                  value={formData.expiry_year || ''}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      expiry_year: e.target.value ? parseInt(e.target.value) : null,
                    })
                  }
                  placeholder="YYYY"
                />
              </div>
            </div>

            {/* Credit Limit (for credit cards) */}
            {formData.card_type === 'credit' && (
              <div className="grid gap-2">
                <Label htmlFor="credit_limit">Credit Limit</Label>
                <Input
                  id="credit_limit"
                  type="number"
                  step="0.01"
                  value={formData.credit_limit || ''}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      credit_limit: e.target.value ? parseFloat(e.target.value) : null,
                    })
                  }
                  placeholder="0.00"
                />
              </div>
            )}

            {/* Color */}
            <div className="grid gap-2">
              <Label htmlFor="color">Card Color</Label>
              <Select
                value={formData.color}
                onValueChange={(value) => setFormData({ ...formData, color: value })}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {CARD_COLORS.map((color) => (
                    <SelectItem key={color.value} value={color.value}>
                      <div className="flex items-center gap-2">
                        <div
                          className="w-4 h-4 rounded"
                          style={{ backgroundColor: color.value }}
                        />
                        {color.label}
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
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
              {createMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Create Card
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}

