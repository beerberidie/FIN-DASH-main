import { useQuery } from '@tanstack/react-query';
import { getCardAnalytics, Card, getCategories } from '@/services/api';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Card as CardUI, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Loader2, TrendingUp, ShoppingCart, Calendar, Percent } from 'lucide-react';
import { Progress } from '@/components/ui/progress';

interface CardAnalyticsDialogProps {
  card: Card | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function CardAnalyticsDialog({ card, open, onOpenChange }: CardAnalyticsDialogProps) {
  const { data: analytics, isLoading } = useQuery({
    queryKey: ['card-analytics', card?.id],
    queryFn: () => (card ? getCardAnalytics(card.id) : null),
    enabled: !!card && open,
  });

  const { data: categories = [] } = useQuery({
    queryKey: ['categories'],
    queryFn: getCategories,
  });

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-ZA', {
      style: 'currency',
      currency: 'ZAR',
    }).format(amount);
  };

  const getCategoryName = (categoryId: string) => {
    const category = categories.find((c) => c.id === categoryId);
    return category?.name || 'Unknown';
  };

  if (!card) return null;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Card Analytics - {card.name}</DialogTitle>
          <DialogDescription>
            Detailed spending analytics and insights for this card.
          </DialogDescription>
        </DialogHeader>

        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
          </div>
        ) : analytics ? (
          <div className="space-y-6">
            {/* Summary Cards */}
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
              <CardUI>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Total Transactions</CardTitle>
                  <ShoppingCart className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{analytics.total_transactions}</div>
                </CardContent>
              </CardUI>

              <CardUI>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Total Spent</CardTitle>
                  <TrendingUp className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{formatCurrency(analytics.total_spent)}</div>
                </CardContent>
              </CardUI>

              <CardUI>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Average Transaction</CardTitle>
                  <Calendar className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">
                    {formatCurrency(analytics.average_transaction)}
                  </div>
                </CardContent>
              </CardUI>

              {card.card_type === 'credit' && (
                <CardUI>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Credit Utilization</CardTitle>
                    <Percent className="h-4 w-4 text-muted-foreground" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">
                      {analytics.credit_utilization.toFixed(1)}%
                    </div>
                    <Progress
                      value={analytics.credit_utilization}
                      className="mt-2"
                      indicatorClassName={
                        analytics.credit_utilization > 80
                          ? 'bg-red-500'
                          : analytics.credit_utilization > 50
                          ? 'bg-yellow-500'
                          : 'bg-green-500'
                      }
                    />
                  </CardContent>
                </CardUI>
              )}
            </div>

            {/* Spending by Category */}
            <CardUI>
              <CardHeader>
                <CardTitle>Spending by Category</CardTitle>
              </CardHeader>
              <CardContent>
                {Object.keys(analytics.spending_by_category).length > 0 ? (
                  <div className="space-y-4">
                    {Object.entries(analytics.spending_by_category)
                      .sort(([, a], [, b]) => b - a)
                      .map(([categoryId, amount]) => {
                        const percentage =
                          (amount / analytics.total_spent) * 100;
                        return (
                          <div key={categoryId} className="space-y-2">
                            <div className="flex items-center justify-between text-sm">
                              <span className="font-medium">{getCategoryName(categoryId)}</span>
                              <span className="text-muted-foreground">
                                {formatCurrency(amount)} ({percentage.toFixed(1)}%)
                              </span>
                            </div>
                            <Progress value={percentage} />
                          </div>
                        );
                      })}
                  </div>
                ) : (
                  <p className="text-sm text-muted-foreground">No spending data available</p>
                )}
              </CardContent>
            </CardUI>

            {/* Monthly Spending */}
            <CardUI>
              <CardHeader>
                <CardTitle>Monthly Spending</CardTitle>
              </CardHeader>
              <CardContent>
                {Object.keys(analytics.monthly_spending).length > 0 ? (
                  <div className="space-y-4">
                    {Object.entries(analytics.monthly_spending)
                      .sort(([a], [b]) => b.localeCompare(a))
                      .map(([month, amount]) => {
                        const maxAmount = Math.max(...Object.values(analytics.monthly_spending));
                        const percentage = (amount / maxAmount) * 100;
                        return (
                          <div key={month} className="space-y-2">
                            <div className="flex items-center justify-between text-sm">
                              <span className="font-medium">{month}</span>
                              <span className="text-muted-foreground">
                                {formatCurrency(amount)}
                              </span>
                            </div>
                            <Progress value={percentage} />
                          </div>
                        );
                      })}
                  </div>
                ) : (
                  <p className="text-sm text-muted-foreground">No monthly data available</p>
                )}
              </CardContent>
            </CardUI>
          </div>
        ) : (
          <div className="text-center py-12">
            <p className="text-sm text-muted-foreground">No analytics data available</p>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}

