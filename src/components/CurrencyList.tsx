import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
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
import { AlertCircle, Coins, CheckCircle, XCircle } from "lucide-react";
import * as api from "@/services/api";
import { useToast } from "@/hooks/use-toast";

export const CurrencyList = () => {
  const { toast } = useToast();

  const { data: currencies, isLoading, error } = useQuery({
    queryKey: ['currencies'],
    queryFn: () => api.getCurrencies(false),
    onError: (err: Error) => {
      toast({
        title: "Error loading currencies",
        description: err.message || "Failed to load currencies",
        variant: "destructive",
      });
    },
  });

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <Skeleton className="h-6 w-48" />
          <Skeleton className="h-4 w-64 mt-2" />
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[1, 2, 3, 4, 5].map((i) => (
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
            Currencies
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              {error.message || "Failed to load currencies"}
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>
    );
  }

  const activeCurrencies = currencies?.filter(c => c.is_active) || [];
  const inactiveCurrencies = currencies?.filter(c => !c.is_active) || [];

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Coins className="h-6 w-6 text-primary" />
          Supported Currencies
        </CardTitle>
        <CardDescription>
          {activeCurrencies.length} active currencies available for transactions
        </CardDescription>
      </CardHeader>
      <CardContent>
        {currencies && currencies.length > 0 ? (
          <div className="space-y-6">
            {/* Active Currencies */}
            {activeCurrencies.length > 0 && (
              <div>
                <h3 className="text-sm font-semibold mb-3 flex items-center gap-2">
                  <CheckCircle className="h-4 w-4 text-green-600" />
                  Active Currencies ({activeCurrencies.length})
                </h3>
                <div className="border rounded-lg overflow-hidden">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Code</TableHead>
                        <TableHead>Name</TableHead>
                        <TableHead>Symbol</TableHead>
                        <TableHead>Status</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {activeCurrencies.map((currency) => (
                        <TableRow key={currency.code}>
                          <TableCell className="font-bold">{currency.code}</TableCell>
                          <TableCell>{currency.name}</TableCell>
                          <TableCell className="text-lg">{currency.symbol}</TableCell>
                          <TableCell>
                            <Badge className="bg-green-100 text-green-800">
                              Active
                            </Badge>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              </div>
            )}

            {/* Inactive Currencies */}
            {inactiveCurrencies.length > 0 && (
              <div>
                <h3 className="text-sm font-semibold mb-3 flex items-center gap-2">
                  <XCircle className="h-4 w-4 text-gray-600" />
                  Inactive Currencies ({inactiveCurrencies.length})
                </h3>
                <div className="border rounded-lg overflow-hidden">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Code</TableHead>
                        <TableHead>Name</TableHead>
                        <TableHead>Symbol</TableHead>
                        <TableHead>Status</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {inactiveCurrencies.map((currency) => (
                        <TableRow key={currency.code}>
                          <TableCell className="font-bold text-muted-foreground">
                            {currency.code}
                          </TableCell>
                          <TableCell className="text-muted-foreground">
                            {currency.name}
                          </TableCell>
                          <TableCell className="text-lg text-muted-foreground">
                            {currency.symbol}
                          </TableCell>
                          <TableCell>
                            <Badge variant="outline" className="bg-gray-100 text-gray-800">
                              Inactive
                            </Badge>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              </div>
            )}

            {/* Currency Info */}
            <div className="p-4 bg-muted rounded-lg">
              <h4 className="font-semibold text-sm mb-2">Currency Information</h4>
              <ul className="text-sm text-muted-foreground space-y-1">
                <li>• All currencies follow ISO 4217 standard (3-letter codes)</li>
                <li>• Active currencies can be used in transactions and investments</li>
                <li>• Exchange rates are required for multi-currency conversions</li>
                <li>• Base currency for reporting: ZAR (South African Rand)</li>
              </ul>
            </div>
          </div>
        ) : (
          <Alert>
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              No currencies found. Please contact support.
            </AlertDescription>
          </Alert>
        )}
      </CardContent>
    </Card>
  );
};

