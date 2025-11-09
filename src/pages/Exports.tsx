import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { ExportHistory } from "@/components/ExportHistory";
import { ExportButton } from "@/components/ExportButton";
import { 
  Download, 
  ArrowLeft,
  FileText,
  TrendingUp,
  CreditCard,
  PiggyBank
} from "lucide-react";

const Exports = () => {
  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card shadow-sm">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Link to="/">
                <Button variant="ghost" size="icon">
                  <ArrowLeft className="h-5 w-5" />
                </Button>
              </Link>
              <div className="p-2 rounded-lg bg-gradient-primary">
                <Download className="h-6 w-6 text-primary-foreground" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-foreground">FIN-DASH Exports</h1>
                <p className="text-sm text-muted-foreground">Export and download your financial data</p>
              </div>
            </div>
            <div className="hidden sm:block text-right">
              <p className="text-sm font-medium text-muted-foreground">October 2025</p>
              <p className="text-xs text-muted-foreground">Data Export</p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <div className="space-y-6">
          {/* Quick Export Actions */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="p-4 border rounded-lg bg-card">
              <div className="flex items-center gap-3 mb-3">
                <div className="p-2 rounded-lg bg-blue-100 dark:bg-blue-900">
                  <FileText className="h-5 w-5 text-blue-600 dark:text-blue-300" />
                </div>
                <h3 className="font-semibold">Transactions</h3>
              </div>
              <p className="text-sm text-muted-foreground mb-4">
                Export your transaction history with filters
              </p>
              <ExportButton
                exportType="transactions"
                variant="outline"
                size="sm"
                label="Export"
                className="w-full"
              />
            </div>

            <div className="p-4 border rounded-lg bg-card">
              <div className="flex items-center gap-3 mb-3">
                <div className="p-2 rounded-lg bg-green-100 dark:bg-green-900">
                  <TrendingUp className="h-5 w-5 text-green-600 dark:text-green-300" />
                </div>
                <h3 className="font-semibold">Investments</h3>
              </div>
              <p className="text-sm text-muted-foreground mb-4">
                Export your investment portfolio data
              </p>
              <ExportButton
                exportType="investment_portfolio"
                variant="outline"
                size="sm"
                label="Export"
                className="w-full"
              />
            </div>

            <div className="p-4 border rounded-lg bg-card">
              <div className="flex items-center gap-3 mb-3">
                <div className="p-2 rounded-lg bg-purple-100 dark:bg-purple-900">
                  <CreditCard className="h-5 w-5 text-purple-600 dark:text-purple-300" />
                </div>
                <h3 className="font-semibold">Debts</h3>
              </div>
              <p className="text-sm text-muted-foreground mb-4">
                Export your debt report and payment history
              </p>
              <ExportButton
                exportType="debt_report"
                variant="outline"
                size="sm"
                label="Export"
                className="w-full"
              />
            </div>

            <div className="p-4 border rounded-lg bg-card">
              <div className="flex items-center gap-3 mb-3">
                <div className="p-2 rounded-lg bg-orange-100 dark:bg-orange-900">
                  <PiggyBank className="h-5 w-5 text-orange-600 dark:text-orange-300" />
                </div>
                <h3 className="font-semibold">Summary</h3>
              </div>
              <p className="text-sm text-muted-foreground mb-4">
                Export your complete financial summary
              </p>
              <ExportButton
                exportType="financial_summary"
                variant="outline"
                size="sm"
                label="Export"
                className="w-full"
              />
            </div>
          </div>

          {/* Export History */}
          <ExportHistory />
        </div>
      </main>
    </div>
  );
};

export default Exports;

