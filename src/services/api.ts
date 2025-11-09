/**
 * API client for FIN-DASH backend
 */

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8777/api';

interface ApiError {
  detail: string;
}

/**
 * Check if demo mode is enabled
 */
function isDemoMode(): boolean {
  return localStorage.getItem('demoMode') === 'true';
}

/**
 * Get headers with demo mode flag
 */
function getHeaders(additionalHeaders: Record<string, string> = {}): Record<string, string> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...additionalHeaders,
  };

  if (isDemoMode()) {
    headers['X-Demo-Mode'] = 'true';
  }

  return headers;
}

/**
 * Build fetch URL with demo mode prefix if enabled
 */
function buildUrl(endpoint: string): string {
  if (isDemoMode()) {
    // Use demo endpoints
    if (endpoint.includes('/transactions')) {
      return endpoint.replace('/transactions', '/demo/transactions');
    } else if (endpoint.includes('/accounts')) {
      return endpoint.replace('/accounts', '/demo/accounts');
    } else if (endpoint.includes('/categories')) {
      return endpoint.replace('/categories', '/demo/categories');
    } else if (endpoint.includes('/budgets')) {
      return endpoint.replace('/budgets', '/demo/budgets');
    } else if (endpoint.includes('/investments')) {
      return endpoint.replace('/investments', '/demo/investments');
    } else if (endpoint.includes('/recurring')) {
      return endpoint.replace('/recurring', '/demo/recurring');
    }
  }

  return endpoint;
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error: ApiError = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `HTTP ${response.status}: ${response.statusText}`);
  }

  // Handle 204 No Content
  if (response.status === 204) {
    return null as T;
  }

  return response.json();
}

// Summary / Dashboard
export const getSummary = async () => {
  const response = await fetch(`${API_BASE}/summary`);
  return handleResponse(response);
};

// Transactions
export interface Transaction {
  id: string;
  date: string;
  description: string;
  amount: number;
  category_id: string | null;
  account_id: string;
  type: 'income' | 'expense';
  source: string;
  external_id: string | null;
  tags: string;
  created_at: string;
  updated_at: string;
}

export interface TransactionCreate {
  date: string;
  description: string;
  amount: number;
  category_id?: string | null;
  account_id: string;
  type: 'income' | 'expense';
  source?: string;
  external_id?: string | null;
  tags?: string;
}

export interface TransactionFilters {
  from?: string;
  to?: string;
  category_id?: string;
  account_id?: string;
}

export const getTransactions = async (filters?: TransactionFilters): Promise<Transaction[]> => {
  const params = new URLSearchParams();
  if (filters?.from) params.append('from', filters.from);
  if (filters?.to) params.append('to', filters.to);
  if (filters?.category_id) params.append('category_id', filters.category_id);
  if (filters?.account_id) params.append('account_id', filters.account_id);

  const endpoint = isDemoMode() ? `${API_BASE}/demo/transactions` : `${API_BASE}/transactions`;
  const url = `${endpoint}${params.toString() ? '?' + params.toString() : ''}`;
  const response = await fetch(url);
  return handleResponse(response);
};

export const getTransaction = async (id: string): Promise<Transaction> => {
  const response = await fetch(`${API_BASE}/transactions/${id}`);
  return handleResponse(response);
};

export const createTransaction = async (transaction: TransactionCreate): Promise<Transaction> => {
  const response = await fetch(`${API_BASE}/transactions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(transaction),
  });
  return handleResponse(response);
};

export const updateTransaction = async (id: string, transaction: Partial<TransactionCreate>): Promise<Transaction> => {
  const response = await fetch(`${API_BASE}/transactions/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(transaction),
  });
  return handleResponse(response);
};

export const deleteTransaction = async (id: string): Promise<void> => {
  const response = await fetch(`${API_BASE}/transactions/${id}`, {
    method: 'DELETE',
  });
  return handleResponse(response);
};

// Categories
export interface Category {
  id: string;
  name: string;
  group: 'needs' | 'wants' | 'savings' | 'debt' | 'income';
  color: string;
  icon: string;
  is_system: boolean;
  created_at: string;
}

export const getCategories = async (): Promise<Category[]> => {
  const endpoint = isDemoMode() ? `${API_BASE}/demo/categories` : `${API_BASE}/categories`;
  const response = await fetch(endpoint);
  return handleResponse(response);
};

export const getCategory = async (id: string): Promise<Category> => {
  const response = await fetch(`${API_BASE}/categories/${id}`);
  return handleResponse(response);
};

export const deleteCategory = async (id: string): Promise<void> => {
  const response = await fetch(`${API_BASE}/categories/${id}`, {
    method: 'DELETE',
  });
  return handleResponse(response);
};

// Accounts
export interface Account {
  id: string;
  name: string;
  type: 'bank' | 'cash' | 'investment' | 'virtual';
  opening_balance: number;
  is_active: boolean;
  created_at: string;
}

export const getAccounts = async (): Promise<Account[]> => {
  const endpoint = isDemoMode() ? `${API_BASE}/demo/accounts` : `${API_BASE}/accounts`;
  const response = await fetch(endpoint);
  return handleResponse(response);
};

export const getAccount = async (id: string): Promise<Account> => {
  const response = await fetch(`${API_BASE}/accounts/${id}`);
  return handleResponse(response);
};

export const getAccountBalance = async (id: string) => {
  const response = await fetch(`${API_BASE}/accounts/${id}/balance`);
  return handleResponse(response);
};

export const deleteAccount = async (id: string): Promise<void> => {
  const response = await fetch(`${API_BASE}/accounts/${id}`, {
    method: 'DELETE',
  });
  return handleResponse(response);
};

// Goals
export interface Goal {
  id: string;
  name: string;
  target_amount: number;
  current_amount: number;
  target_date: string | null;
  linked_account_id: string | null;
  color: string;
  icon: string;
  created_at: string;
  updated_at: string;
}

export interface GoalCreate {
  name: string;
  target_amount: number;
  current_amount?: number;
  target_date?: string | null;
  linked_account_id?: string | null;
  color?: string;
  icon?: string;
}

export interface GoalContribution {
  amount: number;
  note?: string;
}

// Import interfaces
export interface ImportSummary {
  success: boolean;
  imported: number;
  skipped: number;
  total: number;
  errors: string[];
  error?: string;
}

export interface CategorizationPreview {
  description: string;
  amount: number;
  suggested_category: string;
  confidence: float;
  confidence_label: string;
}

export interface BankFormat {
  formats: string[];
  details: Record<string, string>;
}

export const getGoals = async (activeOnly: boolean = false): Promise<Goal[]> => {
  const params = new URLSearchParams();
  if (activeOnly) params.append('active_only', 'true');

  const url = `${API_BASE}/goals${params.toString() ? '?' + params.toString() : ''}`;
  const response = await fetch(url);
  return handleResponse(response);
};

export const getGoal = async (id: string): Promise<Goal> => {
  const response = await fetch(`${API_BASE}/goals/${id}`);
  return handleResponse(response);
};

export const createGoal = async (goal: GoalCreate): Promise<Goal> => {
  const response = await fetch(`${API_BASE}/goals`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(goal),
  });
  return handleResponse(response);
};

export const updateGoal = async (id: string, goal: Partial<GoalCreate>): Promise<Goal> => {
  const response = await fetch(`${API_BASE}/goals/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(goal),
  });
  return handleResponse(response);
};

export const contributeToGoal = async (id: string, contribution: GoalContribution): Promise<Goal> => {
  const response = await fetch(`${API_BASE}/goals/${id}/contribute`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(contribution),
  });
  return handleResponse(response);
};

export const deleteGoal = async (id: string): Promise<void> => {
  const response = await fetch(`${API_BASE}/goals/${id}`, {
    method: 'DELETE',
  });
  return handleResponse(response);
};

// Budgets
export interface Budget {
  id: string;
  year: number;
  month: number;
  needs_planned: number;
  wants_planned: number;
  savings_planned: number;
  notes: string;
  created_at: string;
  updated_at: string;
}

export interface BudgetStatus {
  id?: string;
  year: number;
  month: number;
  needs_planned: number;
  needs_actual: number;
  wants_planned: number;
  wants_actual: number;
  savings_planned: number;
  savings_actual: number;
  total_planned: number;
  total_actual: number;
  needs_utilization: number;
  wants_utilization: number;
  savings_utilization: number;
  total_utilization: number;
  over_budget: {
    needs: boolean;
    wants: boolean;
    savings: boolean;
  };
  exists: boolean;
}

export interface BudgetCreate {
  year: number;
  month: number;
  needs_planned: number;
  wants_planned: number;
  savings_planned: number;
  notes?: string;
}

export const getBudgets = async (year?: number, month?: number): Promise<Budget[]> => {
  const params = new URLSearchParams();
  if (year) params.append('year', year.toString());
  if (month) params.append('month', month.toString());

  const url = `${API_BASE}/budgets${params.toString() ? '?' + params.toString() : ''}`;
  const response = await fetch(url);
  return handleResponse(response);
};

export const getCurrentBudget = async (): Promise<BudgetStatus> => {
  const response = await fetch(`${API_BASE}/budgets/current`);
  return handleResponse(response);
};

export const getBudget = async (id: string): Promise<BudgetStatus> => {
  const response = await fetch(`${API_BASE}/budgets/${id}`);
  return handleResponse(response);
};

export const createBudget = async (budget: BudgetCreate): Promise<Budget> => {
  const response = await fetch(`${API_BASE}/budgets`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(budget),
  });
  return handleResponse(response);
};

export const updateBudget = async (id: string, budget: Partial<BudgetCreate>): Promise<Budget> => {
  const response = await fetch(`${API_BASE}/budgets/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(budget),
  });
  return handleResponse(response);
};

export const deleteBudget = async (id: string): Promise<void> => {
  const response = await fetch(`${API_BASE}/budgets/${id}`, {
    method: 'DELETE',
  });
  return handleResponse(response);
};

// Import
export const importCSV = async (file: File, accountId: string, bankFormat?: string, autoCategorize: boolean = true): Promise<ImportSummary> => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('account_id', accountId);
  if (bankFormat) formData.append('bank_format', bankFormat);
  formData.append('auto_categorize', autoCategorize.toString());

  const response = await fetch(`${API_BASE}/import/csv`, {
    method: 'POST',
    body: formData,
  });
  return handleResponse(response);
};

export const previewImport = async (file: File, bankFormat?: string): Promise<CategorizationPreview[]> => {
  const formData = new FormData();
  formData.append('file', file);
  if (bankFormat) formData.append('bank_format', bankFormat);

  const response = await fetch(`${API_BASE}/import/preview`, {
    method: 'POST',
    body: formData,
  });
  return handleResponse(response);
};

export const getSupportedFormats = async (): Promise<BankFormat> => {
  const response = await fetch(`${API_BASE}/import/formats`);
  return handleResponse(response);
};

// Debts
export interface Debt {
  id: string;
  name: string;
  debt_type: 'credit_card' | 'personal_loan' | 'student_loan' | 'mortgage' | 'car_loan' | 'other';
  original_balance: number;
  current_balance: number;
  interest_rate: number;
  minimum_payment: number;
  due_day: number;
  linked_account_id?: string | null;
  notes?: string | null;
  created_at: string;
  updated_at: string;
}

export interface DebtCreate {
  name: string;
  debt_type: 'credit_card' | 'personal_loan' | 'student_loan' | 'mortgage' | 'car_loan' | 'other';
  original_balance: number;
  current_balance: number;
  interest_rate: number;
  minimum_payment: number;
  due_day: number;
  linked_account_id?: string | null;
  notes?: string | null;
}

export interface DebtPayment {
  amount: number;
  payment_date?: string;
  notes?: string;
}

export interface PayoffPlan {
  method: 'avalanche' | 'snowball';
  total_months: number;
  total_interest: number;
  total_paid: number;
  payoff_date: string;
  debts: Array<{
    id: string;
    name: string;
    original_balance: number;
    interest_rate: number;
    payoff_month: number;
    payoff_date: string;
  }>;
  monthly_schedule: Array<{
    month: number;
    payment: number;
    interest: number;
    remaining_balance: number;
  }>;
}

export interface PayoffComparison {
  avalanche: PayoffPlan;
  snowball: PayoffPlan;
  comparison: {
    interest_savings: number;
    time_savings_months: number;
    recommended: 'avalanche' | 'snowball';
  };
}

export const getDebts = async (): Promise<Debt[]> => {
  const response = await fetch(`${API_BASE}/debts`);
  return handleResponse(response);
};

export const getDebt = async (id: string): Promise<Debt> => {
  const response = await fetch(`${API_BASE}/debts/${id}`);
  return handleResponse(response);
};

export const createDebt = async (debt: DebtCreate): Promise<Debt> => {
  const response = await fetch(`${API_BASE}/debts`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(debt),
  });
  return handleResponse(response);
};

export const updateDebt = async (id: string, debt: Partial<DebtCreate>): Promise<Debt> => {
  const response = await fetch(`${API_BASE}/debts/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(debt),
  });
  return handleResponse(response);
};

export const deleteDebt = async (id: string): Promise<void> => {
  const response = await fetch(`${API_BASE}/debts/${id}`, {
    method: 'DELETE',
  });
  return handleResponse(response);
};

export const recordDebtPayment = async (id: string, payment: DebtPayment): Promise<Debt> => {
  const response = await fetch(`${API_BASE}/debts/${id}/payment`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payment),
  });
  return handleResponse(response);
};

export const getPayoffPlan = async (extraPayment: number = 0, strategy: 'avalanche' | 'snowball' | 'both' = 'both'): Promise<PayoffPlan | PayoffComparison> => {
  const response = await fetch(`${API_BASE}/debts/payoff-plan`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ extra_payment: extraPayment, strategy }),
  });
  return handleResponse(response);
};

export const getDebtSummary = async (): Promise<{
  total_debt: number;
  minimum_payment: number;
  debt_count: number;
  active_debt_count: number;
}> => {
  const response = await fetch(`${API_BASE}/debts/summary/total`);
  return handleResponse(response);
};

// Reports
export interface MonthlyReport {
  year: number;
  month: number;
  period: string;
  summary: {
    income: number;
    expenses: number;
    net_income: number;
    savings_rate: number;
    transaction_count: number;
    income_count: number;
    expense_count: number;
    avg_expense: number;
  };
  category_breakdown: Record<string, {
    amount: number;
    count: number;
    name: string;
    percentage: number;
  }>;
  top_categories: Array<{
    category_id: string;
    category_name: string;
    amount: number;
    percentage: number;
    transaction_count: number;
  }>;
  budget_performance: any;
  month_over_month: {
    income_change: number;
    expense_change: number;
    previous_month: string;
  };
  insights: string[];
}

export interface YTDSummary {
  year: number;
  summary: {
    total_income: number;
    total_expenses: number;
    net_income: number;
    avg_monthly_income: number;
    avg_monthly_expenses: number;
  };
  monthly_breakdown: Array<{
    month: number;
    income: number;
    expenses: number;
    net: number;
  }>;
}

export interface AvailableMonth {
  year: number;
  month: number;
  period: string;
  label: string;
}

export const getMonthlyReport = async (year: number, month: number): Promise<MonthlyReport> => {
  const response = await fetch(`${API_BASE}/reports/monthly/${year}/${month}`);
  return handleResponse(response);
};

export const getYTDSummary = async (year?: number): Promise<YTDSummary> => {
  const url = year ? `${API_BASE}/reports/summary?year=${year}` : `${API_BASE}/reports/summary`;
  const response = await fetch(url);
  return handleResponse(response);
};

export const getAvailableMonths = async (): Promise<AvailableMonth[]> => {
  const response = await fetch(`${API_BASE}/reports/available-months`);
  return handleResponse(response);
};

export const api = {
  // Summary
  getSummary,

  // Transactions
  getTransactions,
  getTransaction,
  createTransaction,
  updateTransaction,
  deleteTransaction,

  // Categories
  getCategories,
  getCategory,
  deleteCategory,

  // Accounts
  getAccounts,
  getAccount,
  getAccountBalance,
  deleteAccount,

  // Goals
  getGoals,
  getGoal,
  createGoal,
  updateGoal,
  contributeToGoal,
  deleteGoal,

  // Budgets
  getBudgets,
  getCurrentBudget,
  getBudget,
  createBudget,
  updateBudget,
  deleteBudget,

  // Import
  importCSV,
  previewImport,
  getSupportedFormats,

  // Debts
  getDebts,
  getDebt,
  createDebt,
  updateDebt,
  deleteDebt,
  recordDebtPayment,
  getPayoffPlan,
  getDebtSummary,

  // Reports
  getMonthlyReport,
  getYTDSummary,
  getAvailableMonths,
};

export default api;

// Recurring Transactions
export interface RecurringTransaction {
  id: string;
  name: string;
  amount: number;
  category_id: string;
  account_id: string;
  type: 'income' | 'expense';
  frequency: 'daily' | 'weekly' | 'biweekly' | 'monthly' | 'quarterly' | 'yearly';
  start_date: string;
  end_date: string | null;
  day_of_month: number | null;
  day_of_week: number | null;
  is_active: boolean;
  last_generated: string | null;
  next_due: string | null;
  tags: string;
  notes: string;
  created_at: string;
  updated_at: string;
}

export interface RecurringTransactionCreate {
  name: string;
  amount: number;
  category_id: string;
  account_id: string;
  type: 'income' | 'expense';
  frequency: 'daily' | 'weekly' | 'biweekly' | 'monthly' | 'quarterly' | 'yearly';
  start_date: string;
  end_date?: string | null;
  day_of_month?: number | null;
  day_of_week?: number | null;
  is_active?: boolean;
  tags?: string;
  notes?: string;
}

export const getRecurringTransactions = async (activeOnly: boolean = false): Promise<RecurringTransaction[]> => {
  const url = `${API_BASE}/recurring${activeOnly ? '?active_only=true' : ''}`;
  const response = await fetch(url);
  return handleResponse(response);
};

export const getRecurringTransaction = async (id: string): Promise<RecurringTransaction> => {
  const response = await fetch(`${API_BASE}/recurring/${id}`);
  return handleResponse(response);
};

export const createRecurringTransaction = async (data: RecurringTransactionCreate): Promise<RecurringTransaction> => {
  const response = await fetch(`${API_BASE}/recurring`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  return handleResponse(response);
};

export const updateRecurringTransaction = async (id: string, data: Partial<RecurringTransactionCreate>): Promise<RecurringTransaction> => {
  const response = await fetch(`${API_BASE}/recurring/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  return handleResponse(response);
};

export const deleteRecurringTransaction = async (id: string): Promise<void> => {
  const response = await fetch(`${API_BASE}/recurring/${id}`, {
    method: 'DELETE',
  });
  return handleResponse(response);
};

// ============================================================================
// ANALYTICS & REPORTING (Phase 3 Week 5)
// ============================================================================

// Trend Analysis Types
export interface TrendDataPoint {
  period: string;
  value: number;
  count: number;
}

export interface TrendAnalysis {
  metric: string;
  period_type: string;
  data_points: TrendDataPoint[];
  average: number;
  total: number;
  trend_direction: string;
  trend_percentage: number;
}

// Year-over-Year Types
export interface YoYComparison {
  metric: string;
  current_year: number;
  current_value: number;
  previous_year: number;
  previous_value: number;
  change_amount: number;
  change_percentage: number;
  is_improvement: boolean;
}

export interface YoYReport {
  current_year: number;
  previous_year: number;
  income_comparison: YoYComparison;
  expense_comparison: YoYComparison;
  net_comparison: YoYComparison;
  savings_rate_current: number;
  savings_rate_previous: number;
  category_comparisons: any[];
}

// Spending Pattern Types
export interface SpendingPattern {
  category: string;
  pattern_type: string;
  average_amount: number;
  frequency: string;
  confidence: number;
  description: string;
}

// Category Insight Types
export interface CategoryInsight {
  category_id: string;
  category_name: string;
  total_spent: number;
  transaction_count: number;
  average_transaction: number;
  percentage_of_total: number;
  trend: string;
  top_merchants: string[];
  monthly_breakdown: TrendDataPoint[];
}

// Prediction Types
export interface Prediction {
  period: string;
  predicted_value: number;
  confidence_interval_low: number;
  confidence_interval_high: number;
  confidence_level: number;
}

export interface PredictionReport {
  metric: string;
  method: string;
  predictions: Prediction[];
  historical_accuracy?: number;
}

// Financial Health Types
export interface HealthMetric {
  name: string;
  score: number;
  status: string;
  description: string;
  recommendation?: string;
}

export interface FinancialHealthScore {
  overall_score: number;
  overall_status: string;
  metrics: HealthMetric[];
  strengths: string[];
  weaknesses: string[];
  recommendations: string[];
  calculated_at: string;
}

export interface HealthMetricBreakdown {
  savings_rate: number;
  debt_to_income: number;
  emergency_fund_months: number;
  budget_adherence: number;
  investment_diversification: number;
  net_worth_trend: string;
}

// Analytics API Functions

export const getTrendAnalysis = async (
  metric: string,
  periodType: string = 'monthly',
  startDate?: string,
  endDate?: string,
  categoryId?: string
): Promise<TrendAnalysis> => {
  const params = new URLSearchParams();
  params.append('period_type', periodType);
  if (startDate) params.append('start_date', startDate);
  if (endDate) params.append('end_date', endDate);
  if (categoryId) params.append('category_id', categoryId);

  const response = await fetch(`${API_BASE}/analytics/trends/${metric}?${params.toString()}`);
  return handleResponse(response);
};

export const getYoYComparison = async (
  currentYear?: number,
  previousYear?: number
): Promise<YoYReport> => {
  const params = new URLSearchParams();
  if (currentYear) params.append('current_year', currentYear.toString());
  if (previousYear) params.append('previous_year', previousYear.toString());

  const url = `${API_BASE}/analytics/yoy-comparison${params.toString() ? '?' + params.toString() : ''}`;
  const response = await fetch(url);
  return handleResponse(response);
};

export const getSpendingPatterns = async (
  startDate?: string,
  endDate?: string
): Promise<SpendingPattern[]> => {
  const params = new URLSearchParams();
  if (startDate) params.append('start_date', startDate);
  if (endDate) params.append('end_date', endDate);

  const url = `${API_BASE}/analytics/spending-patterns${params.toString() ? '?' + params.toString() : ''}`;
  const response = await fetch(url);
  return handleResponse(response);
};

export const getCategoryInsights = async (
  categoryId: string,
  startDate?: string,
  endDate?: string
): Promise<CategoryInsight> => {
  const params = new URLSearchParams();
  if (startDate) params.append('start_date', startDate);
  if (endDate) params.append('end_date', endDate);

  const response = await fetch(`${API_BASE}/analytics/category-insights/${categoryId}?${params.toString()}`);
  return handleResponse(response);
};

export const getPredictions = async (
  metric: string,
  periodsAhead: number = 3,
  method: string = 'moving_average'
): Promise<PredictionReport> => {
  const params = new URLSearchParams();
  params.append('periods_ahead', periodsAhead.toString());
  params.append('method', method);

  const response = await fetch(`${API_BASE}/analytics/predictions/${metric}?${params.toString()}`);
  return handleResponse(response);
};

export const getFinancialHealthScore = async (
  includeInvestments: boolean = true,
  includeDebts: boolean = true,
  referenceDate?: string
): Promise<FinancialHealthScore> => {
  const params = new URLSearchParams();
  params.append('include_investments', includeInvestments.toString());
  params.append('include_debts', includeDebts.toString());
  if (referenceDate) params.append('reference_date', referenceDate);

  const response = await fetch(`${API_BASE}/analytics/health-score?${params.toString()}`);
  return handleResponse(response);
};

export const getHealthBreakdown = async (
  referenceDate?: string
): Promise<HealthMetricBreakdown> => {
  const params = new URLSearchParams();
  if (referenceDate) params.append('reference_date', referenceDate);

  const url = `${API_BASE}/analytics/health-breakdown${params.toString() ? '?' + params.toString() : ''}`;
  const response = await fetch(url);
  return handleResponse(response);
};

export const getIncomeAnalysis = async (
  startDate?: string,
  endDate?: string
): Promise<any> => {
  const params = new URLSearchParams();
  if (startDate) params.append('start_date', startDate);
  if (endDate) params.append('end_date', endDate);

  const url = `${API_BASE}/analytics/income-analysis${params.toString() ? '?' + params.toString() : ''}`;
  const response = await fetch(url);
  return handleResponse(response);
};

export const getExpenseAnalysis = async (
  startDate?: string,
  endDate?: string
): Promise<any> => {
  const params = new URLSearchParams();
  if (startDate) params.append('start_date', startDate);
  if (endDate) params.append('end_date', endDate);

  const url = `${API_BASE}/analytics/expense-analysis${params.toString() ? '?' + params.toString() : ''}`;
  const response = await fetch(url);
  return handleResponse(response);
};

// ============================================================================
// INVESTMENTS & PORTFOLIO (Phase 3 Week 3)
// ============================================================================

// Investment Types
export type InvestmentType = 'stock' | 'etf' | 'crypto' | 'bond' | 'mutual_fund' | 'other';
export type InvestmentTransactionType = 'buy' | 'sell';

export interface Investment {
  id: string;
  symbol: string;
  name: string;
  type: InvestmentType;
  currency: string;
  quantity: number;
  average_cost: number;
  current_price: number;
  last_updated: string;
  notes: string;
  created_at: string;
  updated_at: string;
}

export interface InvestmentCreate {
  symbol: string;
  name: string;
  type: InvestmentType;
  currency?: string;
  quantity?: number;
  average_cost?: number;
  current_price?: number;
  last_updated: string;
  notes?: string;
}

export interface InvestmentUpdate {
  name?: string;
  type?: InvestmentType;
  currency?: string;
  quantity?: number;
  average_cost?: number;
  current_price?: number;
  last_updated?: string;
  notes?: string;
}

export interface InvestmentTransaction {
  id: string;
  investment_id: string;
  date: string;
  type: InvestmentTransactionType;
  quantity: number;
  price: number;
  fees: number;
  total_amount: number;
  notes: string;
  created_at: string;
  updated_at: string;
}

export interface InvestmentTransactionCreate {
  investment_id: string;
  date: string;
  type: InvestmentTransactionType;
  quantity: number;
  price: number;
  fees?: number;
  total_amount: number;
  notes?: string;
}

export interface InvestmentPerformance {
  investment_id: string;
  symbol: string;
  name: string;
  type: string;
  quantity: number;
  average_cost: number;
  current_price: number;
  total_cost: number;
  current_value: number;
  profit_loss: number;
  profit_loss_percentage: number;
  currency: string;
}

export interface PortfolioSummary {
  total_investments: number;
  total_value: number;
  total_cost: number;
  total_profit_loss: number;
  total_profit_loss_percentage: number;
  currency: string;
  by_type: Record<string, any>;
  top_performers: any[];
  worst_performers: any[];
}

export interface PriceUpdate {
  current_price: number;
  last_updated?: string;
}

// Investment API Functions

export const getInvestments = async (
  type?: string,
  symbol?: string
): Promise<Investment[]> => {
  const params = new URLSearchParams();
  if (type) params.append('type', type);
  if (symbol) params.append('symbol', symbol);

  const url = `${API_BASE}/investments${params.toString() ? '?' + params.toString() : ''}`;
  const response = await fetch(url);
  return handleResponse(response);
};

export const getInvestment = async (id: string): Promise<Investment> => {
  const response = await fetch(`${API_BASE}/investments/${id}`);
  return handleResponse(response);
};

export const createInvestment = async (investment: InvestmentCreate): Promise<Investment> => {
  const response = await fetch(`${API_BASE}/investments`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(investment),
  });
  return handleResponse(response);
};

export const updateInvestment = async (id: string, investment: InvestmentUpdate): Promise<Investment> => {
  const response = await fetch(`${API_BASE}/investments/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(investment),
  });
  return handleResponse(response);
};

export const updateInvestmentPrice = async (id: string, priceUpdate: PriceUpdate): Promise<Investment> => {
  const response = await fetch(`${API_BASE}/investments/${id}/price`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(priceUpdate),
  });
  return handleResponse(response);
};

export const deleteInvestment = async (id: string): Promise<void> => {
  const response = await fetch(`${API_BASE}/investments/${id}`, {
    method: 'DELETE',
  });
  return handleResponse(response);
};

// Investment Transaction API Functions

export const getInvestmentTransactions = async (
  investmentId?: string
): Promise<InvestmentTransaction[]> => {
  const params = new URLSearchParams();
  if (investmentId) params.append('investment_id', investmentId);

  const url = `${API_BASE}/investments/transactions/list${params.toString() ? '?' + params.toString() : ''}`;
  const response = await fetch(url);
  return handleResponse(response);
};

export const getInvestmentTransaction = async (id: string): Promise<InvestmentTransaction> => {
  const response = await fetch(`${API_BASE}/investments/transactions/${id}`);
  return handleResponse(response);
};

export const createInvestmentTransaction = async (
  transaction: InvestmentTransactionCreate
): Promise<InvestmentTransaction> => {
  const response = await fetch(`${API_BASE}/investments/transactions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(transaction),
  });
  return handleResponse(response);
};

export const deleteInvestmentTransaction = async (id: string): Promise<void> => {
  const response = await fetch(`${API_BASE}/investments/transactions/${id}`, {
    method: 'DELETE',
  });
  return handleResponse(response);
};

// Portfolio & Performance API Functions

export const getInvestmentPerformance = async (id: string): Promise<InvestmentPerformance> => {
  const response = await fetch(`${API_BASE}/investments/${id}/performance`);
  return handleResponse(response);
};

export const getPortfolioSummary = async (baseCurrency: string = 'USD'): Promise<PortfolioSummary> => {
  const params = new URLSearchParams();
  params.append('base_currency', baseCurrency);

  const response = await fetch(`${API_BASE}/investments/portfolio/summary?${params.toString()}`);
  return handleResponse(response);
};

export const getAssetAllocation = async (): Promise<Record<string, any>> => {
  const response = await fetch(`${API_BASE}/investments/portfolio/allocation`);
  return handleResponse(response);
};

export const getPortfolioPerformance = async (baseCurrency: string = 'USD'): Promise<any[]> => {
  const params = new URLSearchParams();
  params.append('base_currency', baseCurrency);

  const response = await fetch(`${API_BASE}/investments/portfolio/performance?${params.toString()}`);
  return handleResponse(response);
};

export const getPortfolioHistory = async (
  startDate?: string,
  endDate?: string,
  baseCurrency: string = 'USD'
): Promise<any[]> => {
  const params = new URLSearchParams();
  params.append('base_currency', baseCurrency);
  if (startDate) params.append('start_date', startDate);
  if (endDate) params.append('end_date', endDate);

  const response = await fetch(`${API_BASE}/investments/portfolio/history?${params.toString()}`);
  return handleResponse(response);
};

// ============================================================================
// CURRENCIES & EXCHANGE RATES (Phase 3 Week 2)
// ============================================================================

// Currency Types
export interface Currency {
  code: string;
  name: string;
  symbol: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface CurrencyCreate {
  code: string;
  name: string;
  symbol: string;
  is_active?: boolean;
}

export interface ExchangeRate {
  id: string;
  from_currency: string;
  to_currency: string;
  rate: number;
  date: string;
  source: string;
  created_at: string;
  updated_at: string;
}

export interface ExchangeRateCreate {
  from_currency: string;
  to_currency: string;
  rate: number;
  date: string;
  source?: string;
}

export interface ExchangeRateUpdate {
  rate?: number;
  date?: string;
  source?: string;
}

export interface CurrencyConversion {
  amount: number;
  from_currency: string;
  to_currency: string;
  date?: string;
}

export interface CurrencyConversionResult {
  original_amount: number;
  from_currency: string;
  to_currency: string;
  exchange_rate: number;
  converted_amount: number;
  conversion_date: string;
}

// Currency API Functions

export const getCurrencies = async (activeOnly: boolean = false): Promise<Currency[]> => {
  const params = new URLSearchParams();
  if (activeOnly) params.append('active_only', 'true');

  const url = `${API_BASE}/currencies${params.toString() ? '?' + params.toString() : ''}`;
  const response = await fetch(url);
  return handleResponse(response);
};

export const getCurrency = async (code: string): Promise<Currency> => {
  const response = await fetch(`${API_BASE}/currencies/${code}`);
  return handleResponse(response);
};

export const createCurrency = async (currency: CurrencyCreate): Promise<Currency> => {
  const response = await fetch(`${API_BASE}/currencies`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(currency),
  });
  return handleResponse(response);
};

// Exchange Rate API Functions

export const getExchangeRates = async (
  fromCurrency?: string,
  toCurrency?: string,
  dateFrom?: string,
  dateTo?: string
): Promise<ExchangeRate[]> => {
  const params = new URLSearchParams();
  if (fromCurrency) params.append('from_currency', fromCurrency);
  if (toCurrency) params.append('to_currency', toCurrency);
  if (dateFrom) params.append('date_from', dateFrom);
  if (dateTo) params.append('date_to', dateTo);

  const url = `${API_BASE}/currencies/exchange-rates/list${params.toString() ? '?' + params.toString() : ''}`;
  const response = await fetch(url);
  return handleResponse(response);
};

export const getExchangeRate = async (rateId: string): Promise<ExchangeRate> => {
  const response = await fetch(`${API_BASE}/currencies/exchange-rates/${rateId}`);
  return handleResponse(response);
};

export const getLatestExchangeRate = async (
  fromCurrency: string,
  toCurrency: string
): Promise<ExchangeRate> => {
  const response = await fetch(
    `${API_BASE}/currencies/exchange-rates/latest/${fromCurrency}/${toCurrency}`
  );
  return handleResponse(response);
};

export const createExchangeRate = async (rate: ExchangeRateCreate): Promise<ExchangeRate> => {
  const response = await fetch(`${API_BASE}/currencies/exchange-rates`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(rate),
  });
  return handleResponse(response);
};

export const updateExchangeRate = async (
  rateId: string,
  rateUpdate: ExchangeRateUpdate
): Promise<ExchangeRate> => {
  const response = await fetch(`${API_BASE}/currencies/exchange-rates/${rateId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(rateUpdate),
  });
  return handleResponse(response);
};

export const deleteExchangeRate = async (rateId: string): Promise<void> => {
  const response = await fetch(`${API_BASE}/currencies/exchange-rates/${rateId}`, {
    method: 'DELETE',
  });
  return handleResponse(response);
};

export const convertCurrency = async (conversion: CurrencyConversion): Promise<CurrencyConversionResult> => {
  const response = await fetch(`${API_BASE}/currencies/convert`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(conversion),
  });
  return handleResponse(response);
};

// ============================================================================
// Export API
// ============================================================================

export type ExportFormat = 'pdf' | 'excel' | 'csv';
export type ExportType =
  | 'transactions'
  | 'budget_report'
  | 'debt_report'
  | 'investment_portfolio'
  | 'financial_summary'
  | 'income_statement'
  | 'balance_sheet';

export interface ExportResponse {
  filename: string;
  file_path: string;
  file_size: number;
  export_type: string;
  format: string;
  created_at: string;
}

export interface ExportFile {
  filename: string;
  file_path: string;
  file_size: number;
  export_type: string;
  format: string;
  created_at: string;
}

export interface TransactionExportParams {
  start_date?: string;
  end_date?: string;
  account_id?: string;
  category_id?: string;
  transaction_type?: 'income' | 'expense';
}

export interface InvestmentExportParams {
  include_transactions?: boolean;
  investment_type?: string;
}

export interface DebtExportParams {
  include_paid_off?: boolean;
}

// Transaction Exports
export const exportTransactionsPDF = async (params: TransactionExportParams = {}): Promise<ExportResponse> => {
  const queryParams = new URLSearchParams();
  if (params.start_date) queryParams.append('start_date', params.start_date);
  if (params.end_date) queryParams.append('end_date', params.end_date);
  if (params.account_id) queryParams.append('account_id', params.account_id);
  if (params.category_id) queryParams.append('category_id', params.category_id);
  if (params.transaction_type) queryParams.append('transaction_type', params.transaction_type);

  const url = `${API_BASE}/export/transactions/pdf${queryParams.toString() ? '?' + queryParams.toString() : ''}`;
  const response = await fetch(url, { method: 'POST' });
  return handleResponse(response);
};

export const exportTransactionsExcel = async (params: TransactionExportParams = {}): Promise<ExportResponse> => {
  const queryParams = new URLSearchParams();
  if (params.start_date) queryParams.append('start_date', params.start_date);
  if (params.end_date) queryParams.append('end_date', params.end_date);
  if (params.account_id) queryParams.append('account_id', params.account_id);
  if (params.category_id) queryParams.append('category_id', params.category_id);
  if (params.transaction_type) queryParams.append('transaction_type', params.transaction_type);

  const url = `${API_BASE}/export/transactions/excel${queryParams.toString() ? '?' + queryParams.toString() : ''}`;
  const response = await fetch(url, { method: 'POST' });
  return handleResponse(response);
};

export const exportTransactionsCSV = async (params: TransactionExportParams = {}): Promise<ExportResponse> => {
  const queryParams = new URLSearchParams();
  if (params.start_date) queryParams.append('start_date', params.start_date);
  if (params.end_date) queryParams.append('end_date', params.end_date);
  if (params.account_id) queryParams.append('account_id', params.account_id);
  if (params.category_id) queryParams.append('category_id', params.category_id);
  if (params.transaction_type) queryParams.append('transaction_type', params.transaction_type);

  const url = `${API_BASE}/export/transactions/csv${queryParams.toString() ? '?' + queryParams.toString() : ''}`;
  const response = await fetch(url, { method: 'POST' });
  return handleResponse(response);
};

// Financial Summary Export
export const exportFinancialSummaryPDF = async (): Promise<ExportResponse> => {
  const response = await fetch(`${API_BASE}/export/financial-summary/pdf`, { method: 'POST' });
  return handleResponse(response);
};

// Investment Portfolio Exports
export const exportInvestmentPortfolioPDF = async (params: InvestmentExportParams = {}): Promise<ExportResponse> => {
  const queryParams = new URLSearchParams();
  if (params.include_transactions !== undefined) {
    queryParams.append('include_transactions', params.include_transactions.toString());
  }
  if (params.investment_type) queryParams.append('investment_type', params.investment_type);

  const url = `${API_BASE}/export/investment-portfolio/pdf${queryParams.toString() ? '?' + queryParams.toString() : ''}`;
  const response = await fetch(url, { method: 'POST' });
  return handleResponse(response);
};

export const exportInvestmentPortfolioExcel = async (params: InvestmentExportParams = {}): Promise<ExportResponse> => {
  const queryParams = new URLSearchParams();
  if (params.include_transactions !== undefined) {
    queryParams.append('include_transactions', params.include_transactions.toString());
  }
  if (params.investment_type) queryParams.append('investment_type', params.investment_type);

  const url = `${API_BASE}/export/investment-portfolio/excel${queryParams.toString() ? '?' + queryParams.toString() : ''}`;
  const response = await fetch(url, { method: 'POST' });
  return handleResponse(response);
};

// Debt Report Export
export const exportDebtReportPDF = async (params: DebtExportParams = {}): Promise<ExportResponse> => {
  const queryParams = new URLSearchParams();
  if (params.include_paid_off !== undefined) {
    queryParams.append('include_paid_off', params.include_paid_off.toString());
  }

  const url = `${API_BASE}/export/debt-report/pdf${queryParams.toString() ? '?' + queryParams.toString() : ''}`;
  const response = await fetch(url, { method: 'POST' });
  return handleResponse(response);
};

// List Exports
export const listExports = async (): Promise<ExportFile[]> => {
  const response = await fetch(`${API_BASE}/export/list`);
  return handleResponse(response);
};

// Download Export
export const downloadExport = async (filename: string): Promise<void> => {
  const response = await fetch(`${API_BASE}/export/download/${filename}`);

  if (!response.ok) {
    throw new Error(`Failed to download file: ${response.statusText}`);
  }

  // Get the blob from the response
  const blob = await response.blob();

  // Create a temporary URL for the blob
  const url = window.URL.createObjectURL(blob);

  // Create a temporary anchor element and trigger download
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();

  // Cleanup
  window.URL.revokeObjectURL(url);
  document.body.removeChild(a);
};

export const toggleRecurringTransaction = async (id: string): Promise<RecurringTransaction> => {
  const response = await fetch(`${API_BASE}/recurring/${id}/toggle`, {
    method: 'POST',
  });
  return handleResponse(response);
};

export const getDueRecurringTransactions = async (): Promise<RecurringTransaction[]> => {
  const response = await fetch(`${API_BASE}/recurring/due/check`);
  return handleResponse(response);
};

export const processRecurringTransactions = async (): Promise<{ success: boolean; count: number; transactions: Transaction[] }> => {
  const response = await fetch(`${API_BASE}/recurring/process/generate`, {
    method: 'POST',
  });
  return handleResponse(response);
};

// Cards
export interface Card {
  id: string;
  name: string;
  card_type: 'credit' | 'debit' | 'prepaid' | 'virtual';
  last_four_digits: string;
  account_id: string;
  issuer: string;
  available_balance: number;
  current_balance: number;
  credit_limit: number | null;
  expiry_month: number | null;
  expiry_year: number | null;
  is_active: boolean;
  color: string;
  icon: string;
  created_at: string;
  updated_at: string;
}

export interface CardCreate {
  name: string;
  card_type: 'credit' | 'debit' | 'prepaid' | 'virtual';
  last_four_digits: string;
  account_id: string;
  issuer: string;
  available_balance?: number;
  current_balance?: number;
  credit_limit?: number | null;
  expiry_month?: number | null;
  expiry_year?: number | null;
  is_active?: boolean;
  color?: string;
  icon?: string;
}

export interface CardUpdate {
  name?: string;
  card_type?: 'credit' | 'debit' | 'prepaid' | 'virtual';
  last_four_digits?: string;
  account_id?: string;
  issuer?: string;
  available_balance?: number;
  current_balance?: number;
  credit_limit?: number | null;
  expiry_month?: number | null;
  expiry_year?: number | null;
  is_active?: boolean;
  color?: string;
  icon?: string;
}

export interface CardBalance {
  card_id: string;
  card_name: string;
  card_type: string;
  available_balance: number;
  current_balance: number;
  credit_limit: number | null;
}

export interface CardAnalytics {
  card_id: string;
  total_transactions: number;
  total_spent: number;
  average_transaction: number;
  spending_by_category: Record<string, number>;
  monthly_spending: Record<string, number>;
  credit_utilization: number;
}

export const getCards = async (): Promise<Card[]> => {
  const response = await fetch(`${API_BASE}/cards`);
  return handleResponse(response);
};

export const getCard = async (id: string): Promise<Card> => {
  const response = await fetch(`${API_BASE}/cards/${id}`);
  return handleResponse(response);
};

export const createCard = async (card: CardCreate): Promise<Card> => {
  const response = await fetch(`${API_BASE}/cards`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(card),
  });
  return handleResponse(response);
};

export const updateCard = async (id: string, card: CardUpdate): Promise<Card> => {
  const response = await fetch(`${API_BASE}/cards/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(card),
  });
  return handleResponse(response);
};

export const deleteCard = async (id: string): Promise<void> => {
  const response = await fetch(`${API_BASE}/cards/${id}`, {
    method: 'DELETE',
  });
  return handleResponse(response);
};

export const getCardBalance = async (id: string): Promise<CardBalance> => {
  const response = await fetch(`${API_BASE}/cards/${id}/balance`);
  return handleResponse(response);
};

export const getCardTransactions = async (id: string): Promise<Transaction[]> => {
  const response = await fetch(`${API_BASE}/cards/${id}/transactions`);
  return handleResponse(response);
};

export const getCardAnalytics = async (id: string): Promise<CardAnalytics> => {
  const response = await fetch(`${API_BASE}/cards/${id}/analytics`);
  return handleResponse(response);
};

export const updateCardBalances = async (id: string): Promise<CardBalance> => {
  const response = await fetch(`${API_BASE}/cards/${id}/update-balances`, {
    method: 'POST',
  });
  return handleResponse(response);
};

// Import
export interface ImportPreview {
  import_id: string;
  file_name: string;
  file_type: string;
  account_id: string;
  total_transactions: number;
  new_transactions: number;
  duplicate_transactions: number;
  transactions: any[];
  created_at: string;
  status: string;
}

export interface ImportConfirmRequest {
  skip_duplicates: boolean;
  selected_transaction_indices?: number[];
}

export interface ImportResult {
  import_id: string;
  imported_count: number;
  skipped_count: number;
  errors: any[];
}

export interface ImportHistoryRecord {
  import_id: string;
  file_name: string;
  file_type: string;
  account_id: string;
  total_transactions: number;
  imported_count: number;
  skipped_count: number;
  status: string;
  created_at: string;
  completed_at: string;
}

export const uploadStatement = async (
  file: File,
  accountId: string,
  autoCategorize: boolean = true
): Promise<ImportPreview> => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('account_id', accountId);
  formData.append('auto_categorize', autoCategorize.toString());

  const response = await fetch(`${API_BASE}/import/upload`, {
    method: 'POST',
    body: formData,
  });
  return handleResponse(response);
};

export const getImportPreview = async (importId: string): Promise<ImportPreview> => {
  const response = await fetch(`${API_BASE}/import/preview/${importId}`);
  return handleResponse(response);
};

export const confirmImport = async (
  importId: string,
  request: ImportConfirmRequest
): Promise<ImportResult> => {
  const response = await fetch(`${API_BASE}/import/confirm/${importId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });
  return handleResponse(response);
};

export const getImportHistory = async (limit: number = 50): Promise<ImportHistoryRecord[]> => {
  const response = await fetch(`${API_BASE}/import/history?limit=${limit}`);
  const data = await handleResponse<{ history: ImportHistoryRecord[] }>(response);
  return data.history;
};

export const getImportFormats = async (): Promise<{
  formats: string[];
  file_types: string[];
  details: Record<string, string>;
}> => {
  const response = await fetch(`${API_BASE}/import/formats`);
  return handleResponse(response);
};

