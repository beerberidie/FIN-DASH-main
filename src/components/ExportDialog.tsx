import { useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Checkbox } from "@/components/ui/checkbox";
import { Download, FileText, AlertCircle, CheckCircle } from "lucide-react";
import * as api from "@/services/api";
import { useToast } from "@/hooks/use-toast";

interface ExportDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  exportType: api.ExportType;
  defaultFilters?: {
    start_date?: string;
    end_date?: string;
    account_id?: string;
    category_id?: string;
    transaction_type?: 'income' | 'expense';
  };
}

export const ExportDialog = ({ open, onOpenChange, exportType, defaultFilters = {} }: ExportDialogProps) => {
  const { toast } = useToast();
  const [format, setFormat] = useState<api.ExportFormat>('pdf');
  const [startDate, setStartDate] = useState(defaultFilters.start_date || '');
  const [endDate, setEndDate] = useState(defaultFilters.end_date || '');
  const [accountId, setAccountId] = useState(defaultFilters.account_id || '');
  const [categoryId, setCategoryId] = useState(defaultFilters.category_id || '');
  const [transactionType, setTransactionType] = useState<'income' | 'expense' | ''>(defaultFilters.transaction_type || '');
  const [includeTransactions, setIncludeTransactions] = useState(true);
  const [includePaidOff, setIncludePaidOff] = useState(false);
  const [investmentType, setInvestmentType] = useState('');

  // Fetch accounts and categories for filters
  const { data: accounts } = useQuery({
    queryKey: ['accounts'],
    queryFn: api.getAccounts,
    enabled: exportType === 'transactions',
  });

  const { data: categories } = useQuery({
    queryKey: ['categories'],
    queryFn: api.getCategories,
    enabled: exportType === 'transactions',
  });

  const exportMutation = useMutation({
    mutationFn: async () => {
      let response: api.ExportResponse;

      if (exportType === 'transactions') {
        const params: api.TransactionExportParams = {
          start_date: startDate || undefined,
          end_date: endDate || undefined,
          account_id: accountId || undefined,
          category_id: categoryId || undefined,
          transaction_type: transactionType || undefined,
        };

        if (format === 'pdf') {
          response = await api.exportTransactionsPDF(params);
        } else if (format === 'excel') {
          response = await api.exportTransactionsExcel(params);
        } else {
          response = await api.exportTransactionsCSV(params);
        }
      } else if (exportType === 'financial_summary') {
        response = await api.exportFinancialSummaryPDF();
      } else if (exportType === 'investment_portfolio') {
        const params: api.InvestmentExportParams = {
          include_transactions: includeTransactions,
          investment_type: investmentType || undefined,
        };

        if (format === 'pdf') {
          response = await api.exportInvestmentPortfolioPDF(params);
        } else {
          response = await api.exportInvestmentPortfolioExcel(params);
        }
      } else if (exportType === 'debt_report') {
        const params: api.DebtExportParams = {
          include_paid_off: includePaidOff,
        };
        response = await api.exportDebtReportPDF(params);
      } else {
        throw new Error('Unsupported export type');
      }

      return response;
    },
    onSuccess: async (data) => {
      toast({
        title: "Export created successfully",
        description: `${data.filename} is ready for download.`,
      });

      // Automatically download the file
      try {
        await api.downloadExport(data.filename);
        toast({
          title: "Download started",
          description: `Downloading ${data.filename}...`,
        });
      } catch (err) {
        toast({
          title: "Download failed",
          description: "Export created but download failed. Check export history.",
          variant: "destructive",
        });
      }

      onOpenChange(false);
    },
    onError: (err: Error) => {
      toast({
        title: "Export failed",
        description: err.message || "Failed to create export",
        variant: "destructive",
      });
    },
  });

  const handleExport = () => {
    exportMutation.mutate();
  };

  const getExportTypeLabel = () => {
    switch (exportType) {
      case 'transactions': return 'Transactions';
      case 'financial_summary': return 'Financial Summary';
      case 'investment_portfolio': return 'Investment Portfolio';
      case 'debt_report': return 'Debt Report';
      case 'budget_report': return 'Budget Report';
      case 'income_statement': return 'Income Statement';
      case 'balance_sheet': return 'Balance Sheet';
      default: return 'Export';
    }
  };

  const getAvailableFormats = (): api.ExportFormat[] => {
    if (exportType === 'transactions') {
      return ['pdf', 'excel', 'csv'];
    } else if (exportType === 'investment_portfolio') {
      return ['pdf', 'excel'];
    } else {
      return ['pdf'];
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            Export {getExportTypeLabel()}
          </DialogTitle>
          <DialogDescription>
            Configure export parameters and download your data
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          {/* Format Selection */}
          <div className="space-y-2">
            <Label htmlFor="format">Export Format *</Label>
            <Select value={format} onValueChange={(value) => setFormat(value as api.ExportFormat)}>
              <SelectTrigger id="format">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {getAvailableFormats().includes('pdf') && (
                  <SelectItem value="pdf">PDF Document</SelectItem>
                )}
                {getAvailableFormats().includes('excel') && (
                  <SelectItem value="excel">Excel Spreadsheet</SelectItem>
                )}
                {getAvailableFormats().includes('csv') && (
                  <SelectItem value="csv">CSV File</SelectItem>
                )}
              </SelectContent>
            </Select>
          </div>

          {/* Transaction-specific filters */}
          {exportType === 'transactions' && (
            <>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="start_date">Start Date</Label>
                  <Input
                    id="start_date"
                    type="date"
                    value={startDate}
                    onChange={(e) => setStartDate(e.target.value)}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="end_date">End Date</Label>
                  <Input
                    id="end_date"
                    type="date"
                    value={endDate}
                    onChange={(e) => setEndDate(e.target.value)}
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="account">Account (Optional)</Label>
                <Select value={accountId} onValueChange={setAccountId}>
                  <SelectTrigger id="account">
                    <SelectValue placeholder="All accounts" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="">All accounts</SelectItem>
                    {accounts?.map((account) => (
                      <SelectItem key={account.id} value={account.id}>
                        {account.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="category">Category (Optional)</Label>
                <Select value={categoryId} onValueChange={setCategoryId}>
                  <SelectTrigger id="category">
                    <SelectValue placeholder="All categories" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="">All categories</SelectItem>
                    {categories?.map((category) => (
                      <SelectItem key={category.id} value={category.id}>
                        {category.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="type">Transaction Type (Optional)</Label>
                <Select value={transactionType} onValueChange={(value) => setTransactionType(value as 'income' | 'expense' | '')}>
                  <SelectTrigger id="type">
                    <SelectValue placeholder="All types" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="">All types</SelectItem>
                    <SelectItem value="income">Income</SelectItem>
                    <SelectItem value="expense">Expense</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </>
          )}

          {/* Investment-specific options */}
          {exportType === 'investment_portfolio' && (
            <>
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="include_transactions"
                  checked={includeTransactions}
                  onCheckedChange={(checked) => setIncludeTransactions(checked as boolean)}
                />
                <Label htmlFor="include_transactions" className="cursor-pointer">
                  Include transaction history
                </Label>
              </div>

              <div className="space-y-2">
                <Label htmlFor="investment_type">Investment Type (Optional)</Label>
                <Select value={investmentType} onValueChange={setInvestmentType}>
                  <SelectTrigger id="investment_type">
                    <SelectValue placeholder="All types" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="">All types</SelectItem>
                    <SelectItem value="stock">Stock</SelectItem>
                    <SelectItem value="etf">ETF</SelectItem>
                    <SelectItem value="crypto">Cryptocurrency</SelectItem>
                    <SelectItem value="bond">Bond</SelectItem>
                    <SelectItem value="mutual_fund">Mutual Fund</SelectItem>
                    <SelectItem value="other">Other</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </>
          )}

          {/* Debt-specific options */}
          {exportType === 'debt_report' && (
            <div className="flex items-center space-x-2">
              <Checkbox
                id="include_paid_off"
                checked={includePaidOff}
                onCheckedChange={(checked) => setIncludePaidOff(checked as boolean)}
              />
              <Label htmlFor="include_paid_off" className="cursor-pointer">
                Include paid-off debts
              </Label>
            </div>
          )}

          {/* Success/Info Alert */}
          <Alert>
            <AlertCircle className="h-4 w-4" />
            <AlertDescription className="text-xs">
              The export will be created and automatically downloaded to your device.
            </AlertDescription>
          </Alert>
        </div>

        <DialogFooter>
          <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button onClick={handleExport} disabled={exportMutation.isPending}>
            {exportMutation.isPending ? (
              <>Exporting...</>
            ) : (
              <>
                <Download className="h-4 w-4 mr-2" />
                Export
              </>
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

