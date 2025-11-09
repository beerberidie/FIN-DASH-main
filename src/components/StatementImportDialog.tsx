import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { getAccounts } from '@/services/api';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import { useToast } from '@/hooks/use-toast';
import { FileUploadZone } from '@/components/FileUploadZone';
import { ImportPreview } from '@/components/ImportPreview';
import { ImportProgress } from '@/components/ImportProgress';
import { Loader2 } from 'lucide-react';

interface StatementImportDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

type ImportStep = 'upload' | 'preview' | 'importing' | 'complete';

interface ImportPreviewData {
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

export function StatementImportDialog({ open, onOpenChange }: StatementImportDialogProps) {
  const { toast } = useToast();
  const queryClient = useQueryClient();

  const [step, setStep] = useState<ImportStep>('upload');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [accountId, setAccountId] = useState<string>('');
  const [autoCategorize, setAutoCategorize] = useState(true);
  const [skipDuplicates, setSkipDuplicates] = useState(true);
  const [importPreview, setImportPreview] = useState<ImportPreviewData | null>(null);
  const [selectedTransactionIndices, setSelectedTransactionIndices] = useState<number[]>([]);
  const [importResult, setImportResult] = useState<any>(null);

  const { data: accounts = [] } = useQuery({
    queryKey: ['accounts'],
    queryFn: getAccounts,
  });

  const uploadMutation = useMutation({
    mutationFn: async (data: { file: File; accountId: string; autoCategorize: boolean }) => {
      const formData = new FormData();
      formData.append('file', data.file);
      formData.append('account_id', data.accountId);
      formData.append('auto_categorize', data.autoCategorize.toString());

      const response = await fetch('http://localhost:8777/api/import/upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Upload failed');
      }

      return response.json();
    },
    onSuccess: (data) => {
      setImportPreview(data);
      setStep('preview');
    },
    onError: (error: Error) => {
      toast({
        title: 'Upload Failed',
        description: error.message,
        variant: 'destructive',
      });
    },
  });

  const confirmMutation = useMutation({
    mutationFn: async (data: {
      importId: string;
      skipDuplicates: boolean;
      selectedIndices?: number[];
    }) => {
      const response = await fetch(
        `http://localhost:8777/api/import/confirm/${data.importId}`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            skip_duplicates: data.skipDuplicates,
            selected_transaction_indices: data.selectedIndices,
          }),
        }
      );

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Import failed');
      }

      return response.json();
    },
    onSuccess: (data) => {
      setImportResult(data);
      setStep('complete');
      queryClient.invalidateQueries({ queryKey: ['transactions'] });
      queryClient.invalidateQueries({ queryKey: ['summary'] });
      toast({
        title: 'Import Successful',
        description: `${data.imported_count} transactions imported successfully`,
      });
    },
    onError: (error: Error) => {
      toast({
        title: 'Import Failed',
        description: error.message,
        variant: 'destructive',
      });
      setStep('preview');
    },
  });

  const handleFileSelect = (file: File) => {
    setSelectedFile(file);
  };

  const handleUpload = () => {
    if (!selectedFile || !accountId) {
      toast({
        title: 'Validation Error',
        description: 'Please select a file and account',
        variant: 'destructive',
      });
      return;
    }

    uploadMutation.mutate({
      file: selectedFile,
      accountId,
      autoCategorize,
    });
  };

  const handleConfirmImport = () => {
    if (!importPreview) return;

    setStep('importing');
    confirmMutation.mutate({
      importId: importPreview.import_id,
      skipDuplicates,
      selectedIndices: selectedTransactionIndices.length > 0 ? selectedTransactionIndices : undefined,
    });
  };

  const handleClose = () => {
    onOpenChange(false);
    // Reset state after dialog closes
    setTimeout(() => {
      setStep('upload');
      setSelectedFile(null);
      setAccountId('');
      setAutoCategorize(true);
      setSkipDuplicates(true);
      setImportPreview(null);
      setSelectedTransactionIndices([]);
      setImportResult(null);
    }, 300);
  };

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Import Bank Statement</DialogTitle>
          <DialogDescription>
            Upload your bank statement to automatically import transactions
          </DialogDescription>
        </DialogHeader>

        {/* Upload Step */}
        {step === 'upload' && (
          <div className="space-y-4 py-4">
            <div className="grid gap-4">
              {/* Account Selection */}
              <div className="grid gap-2">
                <Label htmlFor="account">Account *</Label>
                <Select value={accountId} onValueChange={setAccountId}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select account" />
                  </SelectTrigger>
                  <SelectContent>
                    {accounts.map((account) => (
                      <SelectItem key={account.id} value={account.id}>
                        {account.name} ({account.type})
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* File Upload */}
              <div className="grid gap-2">
                <Label>Bank Statement File *</Label>
                <FileUploadZone onFileSelect={handleFileSelect} />
              </div>

              {/* Options */}
              <div className="space-y-3 pt-2">
                <div className="flex items-center justify-between">
                  <Label htmlFor="auto-categorize">Auto-categorize transactions</Label>
                  <Switch
                    id="auto-categorize"
                    checked={autoCategorize}
                    onCheckedChange={setAutoCategorize}
                  />
                </div>
                <p className="text-xs text-gray-500">
                  Automatically assign categories based on transaction descriptions
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Preview Step */}
        {step === 'preview' && importPreview && (
          <div className="space-y-4 py-4">
            <div className="flex items-center justify-between mb-4">
              <div>
                <p className="text-sm font-medium">File: {importPreview.file_name}</p>
                <p className="text-xs text-gray-500">
                  Format: {importPreview.file_type.toUpperCase()}
                </p>
              </div>
              <div className="flex items-center gap-2">
                <Label htmlFor="skip-duplicates" className="text-sm">
                  Skip duplicates
                </Label>
                <Switch
                  id="skip-duplicates"
                  checked={skipDuplicates}
                  onCheckedChange={setSkipDuplicates}
                />
              </div>
            </div>

            <ImportPreview
              transactions={importPreview.transactions}
              onSelectionChange={setSelectedTransactionIndices}
              skipDuplicates={skipDuplicates}
            />
          </div>
        )}

        {/* Importing Step */}
        {step === 'importing' && (
          <div className="py-8">
            <ImportProgress status="importing" progress={50} />
          </div>
        )}

        {/* Complete Step */}
        {step === 'complete' && importResult && (
          <div className="py-8">
            <ImportProgress
              status="complete"
              importedCount={importResult.imported_count}
              skippedCount={importResult.skipped_count}
              errorCount={importResult.errors?.length || 0}
            />
          </div>
        )}

        <DialogFooter>
          {step === 'upload' && (
            <>
              <Button variant="outline" onClick={handleClose}>
                Cancel
              </Button>
              <Button
                onClick={handleUpload}
                disabled={!selectedFile || !accountId || uploadMutation.isPending}
              >
                {uploadMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Upload & Parse
              </Button>
            </>
          )}

          {step === 'preview' && (
            <>
              <Button variant="outline" onClick={() => setStep('upload')}>
                Back
              </Button>
              <Button onClick={handleConfirmImport} disabled={selectedTransactionIndices.length === 0}>
                Import {selectedTransactionIndices.length} Transaction(s)
              </Button>
            </>
          )}

          {step === 'complete' && (
            <Button onClick={handleClose}>Done</Button>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

