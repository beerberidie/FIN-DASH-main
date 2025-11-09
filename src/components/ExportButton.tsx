import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Download } from "lucide-react";
import { ExportDialog } from "./ExportDialog";
import * as api from "@/services/api";

interface ExportButtonProps {
  exportType: api.ExportType;
  defaultFilters?: {
    start_date?: string;
    end_date?: string;
    account_id?: string;
    category_id?: string;
    transaction_type?: 'income' | 'expense';
  };
  variant?: "default" | "outline" | "ghost" | "secondary" | "destructive" | "link";
  size?: "default" | "sm" | "lg" | "icon";
  label?: string;
  className?: string;
}

export const ExportButton = ({
  exportType,
  defaultFilters = {},
  variant = "outline",
  size = "default",
  label,
  className = "",
}: ExportButtonProps) => {
  const [dialogOpen, setDialogOpen] = useState(false);

  const getDefaultLabel = () => {
    switch (exportType) {
      case 'transactions': return 'Export Transactions';
      case 'financial_summary': return 'Export Summary';
      case 'investment_portfolio': return 'Export Portfolio';
      case 'debt_report': return 'Export Debts';
      case 'budget_report': return 'Export Budget';
      case 'income_statement': return 'Export Income Statement';
      case 'balance_sheet': return 'Export Balance Sheet';
      default: return 'Export';
    }
  };

  return (
    <>
      <Button
        variant={variant}
        size={size}
        onClick={() => setDialogOpen(true)}
        className={className}
      >
        <Download className="h-4 w-4 mr-2" />
        {label || getDefaultLabel()}
      </Button>

      <ExportDialog
        open={dialogOpen}
        onOpenChange={setDialogOpen}
        exportType={exportType}
        defaultFilters={defaultFilters}
      />
    </>
  );
};

