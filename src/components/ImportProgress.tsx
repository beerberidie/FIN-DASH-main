import { CheckCircle2, XCircle, Loader2 } from 'lucide-react';
import { Progress } from '@/components/ui/progress';

interface ImportProgressProps {
  status: 'uploading' | 'parsing' | 'importing' | 'complete' | 'error';
  progress?: number;
  message?: string;
  importedCount?: number;
  skippedCount?: number;
  errorCount?: number;
}

export function ImportProgress({
  status,
  progress = 0,
  message,
  importedCount = 0,
  skippedCount = 0,
  errorCount = 0,
}: ImportProgressProps) {
  const getStatusIcon = () => {
    switch (status) {
      case 'uploading':
      case 'parsing':
      case 'importing':
        return <Loader2 className="h-8 w-8 animate-spin text-blue-500" />;
      case 'complete':
        return <CheckCircle2 className="h-8 w-8 text-green-500" />;
      case 'error':
        return <XCircle className="h-8 w-8 text-red-500" />;
    }
  };

  const getStatusMessage = () => {
    if (message) return message;

    switch (status) {
      case 'uploading':
        return 'Uploading file...';
      case 'parsing':
        return 'Parsing transactions...';
      case 'importing':
        return 'Importing transactions...';
      case 'complete':
        return 'Import completed successfully!';
      case 'error':
        return 'Import failed. Please try again.';
    }
  };

  const getStatusColor = () => {
    switch (status) {
      case 'uploading':
      case 'parsing':
      case 'importing':
        return 'text-blue-600';
      case 'complete':
        return 'text-green-600';
      case 'error':
        return 'text-red-600';
    }
  };

  return (
    <div className="space-y-6">
      {/* Status Icon and Message */}
      <div className="flex flex-col items-center justify-center py-8">
        {getStatusIcon()}
        <p className={`mt-4 text-lg font-medium ${getStatusColor()}`}>
          {getStatusMessage()}
        </p>
      </div>

      {/* Progress Bar */}
      {(status === 'uploading' || status === 'parsing' || status === 'importing') && (
        <div className="space-y-2">
          <Progress value={progress} className="h-2" />
          <p className="text-sm text-center text-gray-500">{progress}%</p>
        </div>
      )}

      {/* Results Summary */}
      {status === 'complete' && (
        <div className="grid grid-cols-3 gap-4">
          <div className="rounded-lg border p-4 text-center">
            <p className="text-2xl font-bold text-green-600">{importedCount}</p>
            <p className="text-sm text-gray-500 mt-1">Imported</p>
          </div>
          <div className="rounded-lg border p-4 text-center">
            <p className="text-2xl font-bold text-orange-600">{skippedCount}</p>
            <p className="text-sm text-gray-500 mt-1">Skipped</p>
          </div>
          <div className="rounded-lg border p-4 text-center">
            <p className="text-2xl font-bold text-red-600">{errorCount}</p>
            <p className="text-sm text-gray-500 mt-1">Errors</p>
          </div>
        </div>
      )}

      {/* Error Details */}
      {status === 'error' && message && (
        <div className="rounded-md bg-red-50 p-4">
          <p className="text-sm text-red-800">{message}</p>
        </div>
      )}
    </div>
  );
}

