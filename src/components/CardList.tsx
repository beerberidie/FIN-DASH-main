import { Card } from '@/services/api';
import { CreditCard, Trash2, Edit, TrendingUp, Calendar } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  Card as CardUI,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

interface CardListProps {
  cards: Card[];
  onEdit: (card: Card) => void;
  onDelete: (card: Card) => void;
  onViewAnalytics: (card: Card) => void;
}

export function CardList({ cards, onEdit, onDelete, onViewAnalytics }: CardListProps) {
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-ZA', {
      style: 'currency',
      currency: 'ZAR',
    }).format(amount);
  };

  const getCardTypeColor = (type: string) => {
    switch (type) {
      case 'credit':
        return 'bg-red-500';
      case 'debit':
        return 'bg-blue-500';
      case 'prepaid':
        return 'bg-green-500';
      case 'virtual':
        return 'bg-purple-500';
      default:
        return 'bg-gray-500';
    }
  };

  const getCardTypeBadgeVariant = (type: string): "default" | "secondary" | "destructive" | "outline" => {
    switch (type) {
      case 'credit':
        return 'destructive';
      case 'debit':
        return 'default';
      case 'prepaid':
        return 'secondary';
      case 'virtual':
        return 'outline';
      default:
        return 'default';
    }
  };

  if (cards.length === 0) {
    return (
      <div className="text-center py-12">
        <CreditCard className="mx-auto h-12 w-12 text-gray-400" />
        <h3 className="mt-2 text-sm font-semibold text-gray-900">No cards</h3>
        <p className="mt-1 text-sm text-gray-500">Get started by adding a new card.</p>
      </div>
    );
  }

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      {cards.map((card) => (
        <CardUI key={card.id} className="overflow-hidden">
          <CardHeader className={`${getCardTypeColor(card.card_type)} text-white pb-4`}>
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <CardTitle className="text-lg font-semibold">{card.name}</CardTitle>
                <CardDescription className="text-white/80 text-sm mt-1">
                  {card.issuer}
                </CardDescription>
              </div>
              <Badge variant={getCardTypeBadgeVariant(card.card_type)} className="ml-2">
                {card.card_type}
              </Badge>
            </div>
            <div className="mt-4 flex items-center justify-between">
              <div className="text-2xl font-mono">•••• {card.last_four_digits}</div>
              {card.expiry_month && card.expiry_year && (
                <div className="flex items-center text-sm text-white/80">
                  <Calendar className="h-3 w-3 mr-1" />
                  {String(card.expiry_month).padStart(2, '0')}/{String(card.expiry_year).slice(-2)}
                </div>
              )}
            </div>
          </CardHeader>
          <CardContent className="pt-4">
            <div className="space-y-3">
              {/* Balances */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-xs text-gray-500">Available</p>
                  <p className="text-lg font-semibold text-green-600">
                    {formatCurrency(card.available_balance)}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Current</p>
                  <p className="text-lg font-semibold">
                    {formatCurrency(card.current_balance)}
                  </p>
                </div>
              </div>

              {/* Credit Limit (for credit cards) */}
              {card.card_type === 'credit' && card.credit_limit && (
                <div>
                  <p className="text-xs text-gray-500">Credit Limit</p>
                  <p className="text-sm font-medium">{formatCurrency(card.credit_limit)}</p>
                  {card.credit_limit > 0 && (
                    <div className="mt-1">
                      <div className="flex items-center justify-between text-xs text-gray-500 mb-1">
                        <span>Utilization</span>
                        <span>
                          {((Math.abs(card.current_balance) / card.credit_limit) * 100).toFixed(1)}%
                        </span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className={`h-2 rounded-full ${
                            (Math.abs(card.current_balance) / card.credit_limit) * 100 > 80
                              ? 'bg-red-500'
                              : (Math.abs(card.current_balance) / card.credit_limit) * 100 > 50
                              ? 'bg-yellow-500'
                              : 'bg-green-500'
                          }`}
                          style={{
                            width: `${Math.min(
                              (Math.abs(card.current_balance) / card.credit_limit) * 100,
                              100
                            )}%`,
                          }}
                        />
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Status */}
              <div className="flex items-center justify-between pt-2 border-t">
                <Badge variant={card.is_active ? 'default' : 'secondary'}>
                  {card.is_active ? 'Active' : 'Inactive'}
                </Badge>
              </div>

              {/* Actions */}
              <div className="flex gap-2 pt-2">
                <Button
                  variant="outline"
                  size="sm"
                  className="flex-1"
                  onClick={() => onViewAnalytics(card)}
                >
                  <TrendingUp className="h-4 w-4 mr-1" />
                  Analytics
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => onEdit(card)}
                >
                  <Edit className="h-4 w-4" />
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => onDelete(card)}
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </CardContent>
        </CardUI>
      ))}
    </div>
  );
}

