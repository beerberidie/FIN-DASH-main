import { useState } from "react";
import { Link } from "react-router-dom";
import { OverviewCards } from "@/components/OverviewCards";
import { BudgetBars } from "@/components/BudgetBars";
import { TransactionsTable } from "@/components/TransactionsTable";
import { GoalsPanel } from "@/components/GoalsPanel";
import { DebtList } from "@/components/DebtList";
import { DebtPayoffCalculator } from "@/components/DebtPayoffCalculator";
import { MonthlyReportView } from "@/components/MonthlyReportView";
import { RecurringTransactionsList } from "@/components/RecurringTransactionsList";
import { DemoModeToggle } from "@/components/DemoModeToggle";
import { Wallet, LayoutDashboard, CreditCard, FileText, Calculator, Repeat, BarChart3, TrendingUp, Coins, Download, Building2, Tag, PieChart } from "lucide-react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";

const Index = () => {
  const [activeTab, setActiveTab] = useState("dashboard");

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card shadow-sm">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-gradient-primary">
                <Wallet className="h-6 w-6 text-primary-foreground" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-foreground">FIN-DASH</h1>
                <p className="text-sm text-muted-foreground">Your personal finance dashboard</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <DemoModeToggle />
              <Link to="/accounts">
                <Button variant="outline" size="sm" className="flex items-center gap-2">
                  <Building2 className="h-4 w-4" />
                  <span className="hidden lg:inline">Accounts</span>
                </Button>
              </Link>
              <Link to="/categories">
                <Button variant="outline" size="sm" className="flex items-center gap-2">
                  <Tag className="h-4 w-4" />
                  <span className="hidden lg:inline">Categories</span>
                </Button>
              </Link>
              <Link to="/budgets">
                <Button variant="outline" size="sm" className="flex items-center gap-2">
                  <PieChart className="h-4 w-4" />
                  <span className="hidden lg:inline">Budgets</span>
                </Button>
              </Link>
              <Link to="/cards">
                <Button variant="outline" size="sm" className="flex items-center gap-2">
                  <CreditCard className="h-4 w-4" />
                  <span className="hidden lg:inline">Cards</span>
                </Button>
              </Link>
              <Link to="/currencies">
                <Button variant="outline" size="sm" className="flex items-center gap-2">
                  <Coins className="h-4 w-4" />
                  <span className="hidden lg:inline">Currencies</span>
                </Button>
              </Link>
              <Link to="/investments">
                <Button variant="outline" size="sm" className="flex items-center gap-2">
                  <TrendingUp className="h-4 w-4" />
                  <span className="hidden lg:inline">Investments</span>
                </Button>
              </Link>
              <Link to="/analytics">
                <Button variant="outline" size="sm" className="flex items-center gap-2">
                  <BarChart3 className="h-4 w-4" />
                  <span className="hidden lg:inline">Analytics</span>
                </Button>
              </Link>
              <Link to="/exports">
                <Button variant="outline" size="sm" className="flex items-center gap-2">
                  <Download className="h-4 w-4" />
                  <span className="hidden lg:inline">Exports</span>
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-5 lg:w-auto lg:inline-grid">
            <TabsTrigger value="dashboard" className="flex items-center gap-2">
              <LayoutDashboard className="h-4 w-4" />
              <span className="hidden sm:inline">Dashboard</span>
            </TabsTrigger>
            <TabsTrigger value="recurring" className="flex items-center gap-2">
              <Repeat className="h-4 w-4" />
              <span className="hidden sm:inline">Recurring</span>
            </TabsTrigger>
            <TabsTrigger value="debts" className="flex items-center gap-2">
              <CreditCard className="h-4 w-4" />
              <span className="hidden sm:inline">Debts</span>
            </TabsTrigger>
            <TabsTrigger value="payoff" className="flex items-center gap-2">
              <Calculator className="h-4 w-4" />
              <span className="hidden sm:inline">Payoff</span>
            </TabsTrigger>
            <TabsTrigger value="reports" className="flex items-center gap-2">
              <FileText className="h-4 w-4" />
              <span className="hidden sm:inline">Reports</span>
            </TabsTrigger>
          </TabsList>

          {/* Dashboard Tab */}
          <TabsContent value="dashboard" className="space-y-8">
            {/* Overview Cards */}
            <section>
              <OverviewCards />
            </section>

            {/* Budget & Goals Row */}
            <section className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <BudgetBars />
              <GoalsPanel />
            </section>

            {/* Transactions */}
            <section>
              <TransactionsTable />
            </section>
          </TabsContent>

          {/* Recurring Transactions Tab */}
          <TabsContent value="recurring">
            <RecurringTransactionsList />
          </TabsContent>

          {/* Debts Tab */}
          <TabsContent value="debts">
            <DebtList />
          </TabsContent>

          {/* Payoff Calculator Tab */}
          <TabsContent value="payoff">
            <DebtPayoffCalculator />
          </TabsContent>

          {/* Reports Tab */}
          <TabsContent value="reports">
            <MonthlyReportView />
          </TabsContent>
        </Tabs>
      </main>

      {/* Footer */}
      <footer className="border-t border-border bg-card mt-16">
        <div className="container mx-auto px-4 py-6">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
            <p className="text-sm text-muted-foreground">
              Local-first financial tracking • Secure & Private
            </p>
            <div className="flex items-center gap-2">
              <div className="h-2 w-2 rounded-full bg-success animate-pulse" />
              <span className="text-xs text-muted-foreground">All data synced</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Index;
