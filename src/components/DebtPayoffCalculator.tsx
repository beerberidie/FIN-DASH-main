import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api, PayoffComparison } from '@/services/api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { TrendingDown, Calendar, DollarSign, Award, AlertCircle } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';

export function DebtPayoffCalculator() {
  const [extraPayment, setExtraPayment] = useState(0);

  const { data: comparison, isLoading, error } = useQuery<PayoffComparison>({
    queryKey: ['payoff-plan', extraPayment],
    queryFn: () => api.getPayoffPlan(extraPayment, 'both') as Promise<PayoffComparison>,
    enabled: true,
  });

  const { data: debts } = useQuery({
    queryKey: ['debts'],
    queryFn: api.getDebts,
  });

  const activeDebts = debts?.filter(d => d.current_balance > 0) || [];

  if (isLoading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-64 w-full" />
      </div>
    );
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>
          Failed to calculate payoff plan. Please try again.
        </AlertDescription>
      </Alert>
    );
  }

  if (!comparison || activeDebts.length === 0) {
    return (
      <Card>
        <CardContent className="flex flex-col items-center justify-center py-12">
          <TrendingDown className="h-12 w-12 text-muted-foreground mb-4" />
          <h3 className="text-lg font-semibold mb-2">No Active Debts</h3>
          <p className="text-muted-foreground text-center">
            Add debts to see payoff strategies and comparisons
          </p>
        </CardContent>
      </Card>
    );
  }

  const { avalanche, snowball, comparison: comp } = comparison;
  const recommended = comp.recommended;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Debt Payoff Calculator</h2>
        <p className="text-muted-foreground">
          Compare Avalanche vs Snowball strategies to find the best payoff plan
        </p>
      </div>

      {/* Extra Payment Input */}
      <Card>
        <CardHeader>
          <CardTitle>Extra Monthly Payment</CardTitle>
          <CardDescription>
            How much extra can you pay towards your debts each month?
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-end gap-4">
            <div className="flex-1 space-y-2">
              <Label htmlFor="extra_payment">Extra Payment (R)</Label>
              <Input
                id="extra_payment"
                type="number"
                step="100"
                min="0"
                placeholder="0.00"
                value={extraPayment || ''}
                onChange={(e) => setExtraPayment(parseFloat(e.target.value) || 0)}
              />
            </div>
            <div className="space-x-2">
              <Button
                variant="outline"
                onClick={() => setExtraPayment(500)}
              >
                R500
              </Button>
              <Button
                variant="outline"
                onClick={() => setExtraPayment(1000)}
              >
                R1,000
              </Button>
              <Button
                variant="outline"
                onClick={() => setExtraPayment(2000)}
              >
                R2,000
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Comparison Summary */}
      {comp.interest_savings !== 0 && (
        <Alert>
          <Award className="h-4 w-4" />
          <AlertDescription>
            <strong>Recommendation:</strong> The {recommended === 'avalanche' ? 'Avalanche' : 'Snowball'} method
            {comp.interest_savings > 0 && ` saves you R${Math.abs(comp.interest_savings).toLocaleString('en-ZA', { minimumFractionDigits: 2 })} in interest`}
            {comp.time_savings_months !== 0 && ` and ${Math.abs(comp.time_savings_months)} month${Math.abs(comp.time_savings_months) !== 1 ? 's' : ''} of payments`}.
          </AlertDescription>
        </Alert>
      )}

      {/* Strategy Comparison */}
      <div className="grid gap-6 md:grid-cols-2">
        {/* Avalanche Strategy */}
        <Card className={recommended === 'avalanche' ? 'border-green-500 border-2' : ''}>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2">
                Avalanche Method
                {recommended === 'avalanche' && (
                  <Badge className="bg-green-500">Recommended</Badge>
                )}
              </CardTitle>
            </div>
            <CardDescription>
              Pay highest interest rate first (saves most money)
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Key Metrics */}
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1">
                <div className="flex items-center text-sm text-muted-foreground">
                  <Calendar className="mr-1 h-3 w-3" />
                  Payoff Time
                </div>
                <div className="text-2xl font-bold">{avalanche.total_months} months</div>
                <div className="text-xs text-muted-foreground">
                  {(avalanche.total_months / 12).toFixed(1)} years
                </div>
              </div>

              <div className="space-y-1">
                <div className="flex items-center text-sm text-muted-foreground">
                  <DollarSign className="mr-1 h-3 w-3" />
                  Total Interest
                </div>
                <div className="text-2xl font-bold">
                  R{avalanche.total_interest.toLocaleString('en-ZA')}
                </div>
              </div>
            </div>

            {/* Payoff Date */}
            <div className="rounded-lg bg-muted p-3">
              <div className="text-sm text-muted-foreground">Debt-Free Date</div>
              <div className="text-lg font-semibold">
                {new Date(avalanche.payoff_date).toLocaleDateString('en-ZA', {
                  year: 'numeric',
                  month: 'long',
                })}
              </div>
            </div>

            {/* Debt Order */}
            <div className="space-y-2">
              <div className="text-sm font-medium">Payoff Order (by interest rate):</div>
              <div className="space-y-1">
                {avalanche.debts.map((debt, index) => (
                  <div key={debt.id} className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">
                      {index + 1}. {debt.name}
                    </span>
                    <span className="font-medium">{debt.interest_rate}%</span>
                  </div>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Snowball Strategy */}
        <Card className={recommended === 'snowball' ? 'border-green-500 border-2' : ''}>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2">
                Snowball Method
                {recommended === 'snowball' && (
                  <Badge className="bg-green-500">Recommended</Badge>
                )}
              </CardTitle>
            </div>
            <CardDescription>
              Pay smallest balance first (quick wins for motivation)
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Key Metrics */}
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1">
                <div className="flex items-center text-sm text-muted-foreground">
                  <Calendar className="mr-1 h-3 w-3" />
                  Payoff Time
                </div>
                <div className="text-2xl font-bold">{snowball.total_months} months</div>
                <div className="text-xs text-muted-foreground">
                  {(snowball.total_months / 12).toFixed(1)} years
                </div>
              </div>

              <div className="space-y-1">
                <div className="flex items-center text-sm text-muted-foreground">
                  <DollarSign className="mr-1 h-3 w-3" />
                  Total Interest
                </div>
                <div className="text-2xl font-bold">
                  R{snowball.total_interest.toLocaleString('en-ZA')}
                </div>
              </div>
            </div>

            {/* Payoff Date */}
            <div className="rounded-lg bg-muted p-3">
              <div className="text-sm text-muted-foreground">Debt-Free Date</div>
              <div className="text-lg font-semibold">
                {new Date(snowball.payoff_date).toLocaleDateString('en-ZA', {
                  year: 'numeric',
                  month: 'long',
                })}
              </div>
            </div>

            {/* Debt Order */}
            <div className="space-y-2">
              <div className="text-sm font-medium">Payoff Order (by balance):</div>
              <div className="space-y-1">
                {snowball.debts.map((debt, index) => (
                  <div key={debt.id} className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">
                      {index + 1}. {debt.name}
                    </span>
                    <span className="font-medium">
                      R{debt.original_balance.toLocaleString('en-ZA')}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

