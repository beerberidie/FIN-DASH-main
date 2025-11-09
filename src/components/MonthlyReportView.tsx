import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api, MonthlyReport } from '@/services/api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  TrendingUp,
  TrendingDown,
  DollarSign,
  PiggyBank,
  Receipt,
  AlertCircle,
  Lightbulb,
  ArrowUp,
  ArrowDown,
} from 'lucide-react';
import { ReportSelector } from './ReportSelector';

export function MonthlyReportView() {
  const now = new Date();
  const [selectedYear, setSelectedYear] = useState(now.getFullYear());
  const [selectedMonth, setSelectedMonth] = useState(now.getMonth() + 1);

  const { data: report, isLoading, error } = useQuery<MonthlyReport>({
    queryKey: ['monthly-report', selectedYear, selectedMonth],
    queryFn: () => api.getMonthlyReport(selectedYear, selectedMonth),
  });

  if (isLoading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-32 w-full" />
        <Skeleton className="h-64 w-full" />
        <Skeleton className="h-48 w-full" />
      </div>
    );
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>
          Failed to load monthly report. Please try again.
        </AlertDescription>
      </Alert>
    );
  }

  if (!report) {
    return null;
  }

  const { summary, top_categories, budget_performance, month_over_month, insights } = report;

  return (
    <div className="space-y-6">
      {/* Header with Selector */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Monthly Report</h2>
          <p className="text-muted-foreground">
            Financial overview for {new Date(selectedYear, selectedMonth - 1).toLocaleDateString('en-ZA', {
              month: 'long',
              year: 'numeric',
            })}
          </p>
        </div>
        <ReportSelector
          selectedYear={selectedYear}
          selectedMonth={selectedMonth}
          onYearChange={setSelectedYear}
          onMonthChange={setSelectedMonth}
        />
      </div>

      {/* Summary Cards */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Income</CardTitle>
            <TrendingUp className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              R{summary.income.toLocaleString('en-ZA', { minimumFractionDigits: 2 })}
            </div>
            {month_over_month.income_change !== 0 && (
              <p className="text-xs text-muted-foreground flex items-center mt-1">
                {month_over_month.income_change > 0 ? (
                  <ArrowUp className="h-3 w-3 text-green-600 mr-1" />
                ) : (
                  <ArrowDown className="h-3 w-3 text-red-600 mr-1" />
                )}
                {Math.abs(month_over_month.income_change).toFixed(1)}% from last month
              </p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Expenses</CardTitle>
            <TrendingDown className="h-4 w-4 text-red-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">
              R{summary.expenses.toLocaleString('en-ZA', { minimumFractionDigits: 2 })}
            </div>
            {month_over_month.expense_change !== 0 && (
              <p className="text-xs text-muted-foreground flex items-center mt-1">
                {month_over_month.expense_change > 0 ? (
                  <ArrowUp className="h-3 w-3 text-red-600 mr-1" />
                ) : (
                  <ArrowDown className="h-3 w-3 text-green-600 mr-1" />
                )}
                {Math.abs(month_over_month.expense_change).toFixed(1)}% from last month
              </p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Net Income</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className={`text-2xl font-bold ${summary.net_income >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              R{summary.net_income.toLocaleString('en-ZA', { minimumFractionDigits: 2 })}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              {summary.transaction_count} transactions
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Savings Rate</CardTitle>
            <PiggyBank className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {summary.savings_rate.toFixed(1)}%
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              {summary.savings_rate >= 20 ? 'Excellent!' : summary.savings_rate >= 10 ? 'Good' : 'Needs improvement'}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Top Spending Categories */}
      <Card>
        <CardHeader>
          <CardTitle>Top Spending Categories</CardTitle>
          <CardDescription>Your highest expense categories this month</CardDescription>
        </CardHeader>
        <CardContent>
          {top_categories.length > 0 ? (
            <div className="space-y-4">
              {top_categories.map((category, index) => (
                <div key={category.category_id} className="space-y-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Badge variant="outline">{index + 1}</Badge>
                      <span className="font-medium">{category.category_name}</span>
                      <span className="text-sm text-muted-foreground">
                        ({category.transaction_count} transaction{category.transaction_count !== 1 ? 's' : ''})
                      </span>
                    </div>
                    <div className="text-right">
                      <div className="font-bold">
                        R{category.amount.toLocaleString('en-ZA', { minimumFractionDigits: 2 })}
                      </div>
                      <div className="text-sm text-muted-foreground">
                        {category.percentage.toFixed(1)}%
                      </div>
                    </div>
                  </div>
                  <div className="h-2 bg-muted rounded-full overflow-hidden">
                    <div
                      className="h-full bg-primary"
                      style={{ width: `${category.percentage}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-muted-foreground text-center py-4">
              No expense data for this month
            </p>
          )}
        </CardContent>
      </Card>

      {/* Budget Performance */}
      {budget_performance.has_budget && (
        <Card>
          <CardHeader>
            <CardTitle>Budget Performance</CardTitle>
            <CardDescription>How you're tracking against your budget</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-3">
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Needs (50%)</span>
                  <span className="text-sm text-muted-foreground">
                    {budget_performance.needs.utilization.toFixed(0)}%
                  </span>
                </div>
                <div className="h-2 bg-muted rounded-full overflow-hidden">
                  <div
                    className={`h-full ${
                      budget_performance.needs.utilization > 100
                        ? 'bg-red-500'
                        : budget_performance.needs.utilization > 90
                        ? 'bg-yellow-500'
                        : 'bg-green-500'
                    }`}
                    style={{ width: `${Math.min(budget_performance.needs.utilization, 100)}%` }}
                  />
                </div>
                <div className="text-xs text-muted-foreground">
                  R{budget_performance.needs.actual.toLocaleString('en-ZA')} of R
                  {budget_performance.needs.planned.toLocaleString('en-ZA')}
                </div>
              </div>

              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Wants (30%)</span>
                  <span className="text-sm text-muted-foreground">
                    {budget_performance.wants.utilization.toFixed(0)}%
                  </span>
                </div>
                <div className="h-2 bg-muted rounded-full overflow-hidden">
                  <div
                    className={`h-full ${
                      budget_performance.wants.utilization > 100
                        ? 'bg-red-500'
                        : budget_performance.wants.utilization > 90
                        ? 'bg-yellow-500'
                        : 'bg-green-500'
                    }`}
                    style={{ width: `${Math.min(budget_performance.wants.utilization, 100)}%` }}
                  />
                </div>
                <div className="text-xs text-muted-foreground">
                  R{budget_performance.wants.actual.toLocaleString('en-ZA')} of R
                  {budget_performance.wants.planned.toLocaleString('en-ZA')}
                </div>
              </div>

              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Savings (20%)</span>
                  <span className="text-sm text-muted-foreground">
                    {budget_performance.savings.utilization.toFixed(0)}%
                  </span>
                </div>
                <div className="h-2 bg-muted rounded-full overflow-hidden">
                  <div
                    className={`h-full ${
                      budget_performance.savings.utilization >= 100
                        ? 'bg-green-500'
                        : budget_performance.savings.utilization >= 50
                        ? 'bg-yellow-500'
                        : 'bg-red-500'
                    }`}
                    style={{ width: `${Math.min(budget_performance.savings.utilization, 100)}%` }}
                  />
                </div>
                <div className="text-xs text-muted-foreground">
                  R{budget_performance.savings.actual.toLocaleString('en-ZA')} of R
                  {budget_performance.savings.planned.toLocaleString('en-ZA')}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Insights */}
      {insights.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Lightbulb className="h-5 w-5" />
              Insights & Recommendations
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              {insights.map((insight, index) => (
                <li key={index} className="flex items-start gap-2">
                  <Receipt className="h-4 w-4 text-muted-foreground mt-0.5" />
                  <span className="text-sm">{insight}</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

