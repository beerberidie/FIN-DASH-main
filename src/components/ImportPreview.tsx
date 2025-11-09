import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { getCategories } from '@/services/api';
import { Checkbox } from '@/components/ui/checkbox';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { AlertCircle, CheckCircle2 } from 'lucide-react';

interface Transaction {
  date: string;
  description: string;
  amount: number;
  type: string;
  category_id?: string;
  is_duplicate: boolean;
  balance?: number;
}

interface ImportPreviewProps {
  transactions: Transaction[];
  onSelectionChange: (selectedIndices: number[]) => void;
  skipDuplicates: boolean;
}

export function ImportPreview({
  transactions,
  onSelectionChange,
  skipDuplicates,
}: ImportPreviewProps) {
  const [selectedIndices, setSelectedIndices] = useState<Set<number>>(
    new Set(
      transactions
        .map((_, index) => index)
        .filter((index) => !skipDuplicates || !transactions[index].is_duplicate)
    )
  );

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

  const formatDate = (dateStr: string) => {
    try {
      const date = new Date(dateStr);
      return date.toLocaleDateString('en-ZA', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
      });
    } catch {
      return dateStr;
    }
  };

  const getCategoryName = (categoryId?: string) => {
    if (!categoryId) return 'Uncategorized';
    const category = categories.find((c) => c.id === categoryId);
    return category?.name || 'Unknown';
  };

  const toggleTransaction = (index: number) => {
    const newSelected = new Set(selectedIndices);
    if (newSelected.has(index)) {
      newSelected.delete(index);
    } else {
      newSelected.add(index);
    }
    setSelectedIndices(newSelected);
    onSelectionChange(Array.from(newSelected));
  };

  const toggleAll = () => {
    if (selectedIndices.size === transactions.length) {
      setSelectedIndices(new Set());
      onSelectionChange([]);
    } else {
      const allIndices = new Set(transactions.map((_, index) => index));
      setSelectedIndices(allIndices);
      onSelectionChange(Array.from(allIndices));
    }
  };

  const newTransactions = transactions.filter((t) => !t.is_duplicate);
  const duplicateTransactions = transactions.filter((t) => t.is_duplicate);

  return (
    <div className="space-y-4">
      {/* Summary */}
      <div className="grid grid-cols-3 gap-4">
        <div className="rounded-lg border p-3">
          <p className="text-sm text-gray-500">Total Transactions</p>
          <p className="text-2xl font-bold">{transactions.length}</p>
        </div>
        <div className="rounded-lg border p-3">
          <p className="text-sm text-gray-500">New Transactions</p>
          <p className="text-2xl font-bold text-green-600">{newTransactions.length}</p>
        </div>
        <div className="rounded-lg border p-3">
          <p className="text-sm text-gray-500">Duplicates</p>
          <p className="text-2xl font-bold text-orange-600">{duplicateTransactions.length}</p>
        </div>
      </div>

      {/* Transaction List */}
      <div className="rounded-lg border">
        <div className="border-b p-3 bg-gray-50">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Checkbox
                checked={selectedIndices.size === transactions.length}
                onCheckedChange={toggleAll}
              />
              <span className="text-sm font-medium">
                {selectedIndices.size} of {transactions.length} selected
              </span>
            </div>
          </div>
        </div>

        <ScrollArea className="h-[400px]">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-12"></TableHead>
                <TableHead>Date</TableHead>
                <TableHead>Description</TableHead>
                <TableHead>Category</TableHead>
                <TableHead className="text-right">Amount</TableHead>
                <TableHead>Status</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {transactions.map((transaction, index) => (
                <TableRow
                  key={index}
                  className={transaction.is_duplicate ? 'bg-orange-50' : ''}
                >
                  <TableCell>
                    <Checkbox
                      checked={selectedIndices.has(index)}
                      onCheckedChange={() => toggleTransaction(index)}
                      disabled={skipDuplicates && transaction.is_duplicate}
                    />
                  </TableCell>
                  <TableCell className="font-medium">
                    {formatDate(transaction.date)}
                  </TableCell>
                  <TableCell>
                    <div className="max-w-xs truncate" title={transaction.description}>
                      {transaction.description}
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline">{getCategoryName(transaction.category_id)}</Badge>
                  </TableCell>
                  <TableCell className="text-right">
                    <span
                      className={
                        transaction.amount >= 0 ? 'text-green-600' : 'text-red-600'
                      }
                    >
                      {formatCurrency(transaction.amount)}
                    </span>
                  </TableCell>
                  <TableCell>
                    {transaction.is_duplicate ? (
                      <div className="flex items-center gap-1 text-orange-600">
                        <AlertCircle className="h-4 w-4" />
                        <span className="text-xs">Duplicate</span>
                      </div>
                    ) : (
                      <div className="flex items-center gap-1 text-green-600">
                        <CheckCircle2 className="h-4 w-4" />
                        <span className="text-xs">New</span>
                      </div>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </ScrollArea>
      </div>

      {/* Info Messages */}
      {duplicateTransactions.length > 0 && (
        <div className="rounded-md bg-orange-50 p-3">
          <div className="flex items-start gap-2">
            <AlertCircle className="h-5 w-5 text-orange-600 mt-0.5" />
            <div>
              <p className="text-sm font-medium text-orange-800">
                {duplicateTransactions.length} duplicate transaction(s) detected
              </p>
              <p className="text-xs text-orange-700 mt-1">
                These transactions appear to already exist in your account. They will be skipped
                unless you manually select them.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

