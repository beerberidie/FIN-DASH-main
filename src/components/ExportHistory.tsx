import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { Download, Trash2, AlertCircle, FileText, History, File } from "lucide-react";
import * as api from "@/services/api";
import { useToast } from "@/hooks/use-toast";

export const ExportHistory = () => {
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [fileToDelete, setFileToDelete] = useState<api.ExportFile | null>(null);

  const { data: exports, isLoading, error } = useQuery({
    queryKey: ['exports'],
    queryFn: api.listExports,
    refetchInterval: 30000, // Refetch every 30 seconds
    onError: (err: Error) => {
      toast({
        title: "Error loading exports",
        description: err.message || "Failed to load export history",
        variant: "destructive",
      });
    },
  });

  const downloadMutation = useMutation({
    mutationFn: api.downloadExport,
    onSuccess: (_, filename) => {
      toast({
        title: "Download started",
        description: `Downloading ${filename}...`,
      });
    },
    onError: (err: Error) => {
      toast({
        title: "Download failed",
        description: err.message || "Failed to download file",
        variant: "destructive",
      });
    },
  });

  const handleDownload = (filename: string) => {
    downloadMutation.mutate(filename);
  };

  const handleDeleteClick = (file: api.ExportFile) => {
    setFileToDelete(file);
    setDeleteDialogOpen(true);
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getFormatBadgeColor = (format: string) => {
    switch (format.toLowerCase()) {
      case 'pdf': return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
      case 'xlsx':
      case 'excel': return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
      case 'csv': return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200';
      default: return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200';
    }
  };

  const getExportTypeLabel = (type: string) => {
    switch (type) {
      case 'transactions': return 'Transactions';
      case 'financial_summary': return 'Financial Summary';
      case 'investment_portfolio': return 'Investment Portfolio';
      case 'debt_report': return 'Debt Report';
      case 'budget_report': return 'Budget Report';
      default: return type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    }
  };

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <Skeleton className="h-6 w-48" />
          <Skeleton className="h-4 w-64 mt-2" />
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <Skeleton key={i} className="h-16 w-full" />
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <AlertCircle className="h-5 w-5 text-destructive" />
            Export History
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              {error.message || "Failed to load export history"}
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>
    );
  }

  return (
    <>
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <History className="h-6 w-6 text-primary" />
            Export History
          </CardTitle>
          <CardDescription>
            Download or manage your previously exported files
          </CardDescription>
        </CardHeader>
        <CardContent>
          {exports && exports.length > 0 ? (
            <div className="border rounded-lg overflow-hidden">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Filename</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead>Format</TableHead>
                    <TableHead>Size</TableHead>
                    <TableHead>Created</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {exports.map((file) => (
                    <TableRow key={file.filename}>
                      <TableCell className="font-medium">
                        <div className="flex items-center gap-2">
                          <File className="h-4 w-4 text-muted-foreground" />
                          <span className="truncate max-w-xs">{file.filename}</span>
                        </div>
                      </TableCell>
                      <TableCell>
                        <span className="text-sm text-muted-foreground">
                          {getExportTypeLabel(file.export_type)}
                        </span>
                      </TableCell>
                      <TableCell>
                        <Badge variant="outline" className={getFormatBadgeColor(file.format)}>
                          {file.format.toUpperCase()}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-sm text-muted-foreground">
                        {formatFileSize(file.file_size)}
                      </TableCell>
                      <TableCell className="text-sm text-muted-foreground">
                        {formatDate(file.created_at)}
                      </TableCell>
                      <TableCell className="text-right">
                        <div className="flex items-center justify-end gap-2">
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => handleDownload(file.filename)}
                            disabled={downloadMutation.isPending}
                          >
                            <Download className="h-4 w-4" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          ) : (
            <Alert>
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>
                No exports found. Create your first export using the export buttons on various pages.
              </AlertDescription>
            </Alert>
          )}

          {/* Info Box */}
          <div className="mt-6 p-4 bg-muted rounded-lg">
            <h4 className="font-semibold text-sm mb-2">Export Information</h4>
            <ul className="text-sm text-muted-foreground space-y-1">
              <li>• Exports are stored locally on your device</li>
              <li>• PDF exports are best for printing and sharing</li>
              <li>• Excel exports allow further data analysis</li>
              <li>• CSV exports can be imported into other applications</li>
              <li>• Files are automatically downloaded when created</li>
            </ul>
          </div>
        </CardContent>
      </Card>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Export File?</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete {fileToDelete?.filename}?
              This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  );
};

