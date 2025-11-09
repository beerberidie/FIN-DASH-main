import { useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { ArrowRightLeft, Calculator, AlertCircle } from "lucide-react";
import * as api from "@/services/api";
import { useToast } from "@/hooks/use-toast";
import { CurrencySelector } from "./CurrencySelector";

export const CurrencyConverter = () => {
  const { toast } = useToast();
  const [amount, setAmount] = useState<number>(100);
  const [fromCurrency, setFromCurrency] = useState<string>('USD');
  const [toCurrency, setToCurrency] = useState<string>('ZAR');
  const [result, setResult] = useState<api.CurrencyConversionResult | null>(null);

  const convertMutation = useMutation({
    mutationFn: api.convertCurrency,
    onSuccess: (data) => {
      setResult(data);
    },
    onError: (err: Error) => {
      toast({
        title: "Conversion error",
        description: err.message || "Failed to convert currency",
        variant: "destructive",
      });
      setResult(null);
    },
  });

  const handleConvert = () => {
    if (amount <= 0) {
      toast({
        title: "Invalid amount",
        description: "Amount must be greater than 0",
        variant: "destructive",
      });
      return;
    }

    if (fromCurrency === toCurrency) {
      toast({
        title: "Invalid currencies",
        description: "From and To currencies must be different",
        variant: "destructive",
      });
      return;
    }

    convertMutation.mutate({
      amount,
      from_currency: fromCurrency,
      to_currency: toCurrency,
    });
  };

  const handleSwapCurrencies = () => {
    const temp = fromCurrency;
    setFromCurrency(toCurrency);
    setToCurrency(temp);
    setResult(null);
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Calculator className="h-6 w-6 text-primary" />
          Currency Converter
        </CardTitle>
        <CardDescription>
          Convert amounts between different currencies
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Amount Input */}
        <div className="space-y-2">
          <Label htmlFor="amount">Amount</Label>
          <Input
            id="amount"
            type="number"
            step="0.01"
            min="0"
            placeholder="0.00"
            value={amount}
            onChange={(e) => {
              setAmount(parseFloat(e.target.value) || 0);
              setResult(null);
            }}
          />
        </div>

        {/* From Currency */}
        <div className="space-y-2">
          <Label htmlFor="from_currency">From Currency</Label>
          <CurrencySelector
            id="from_currency"
            value={fromCurrency}
            onValueChange={(value) => {
              setFromCurrency(value);
              setResult(null);
            }}
          />
        </div>

        {/* Swap Button */}
        <div className="flex justify-center">
          <Button
            type="button"
            variant="outline"
            size="icon"
            onClick={handleSwapCurrencies}
            className="rounded-full"
          >
            <ArrowRightLeft className="h-4 w-4" />
          </Button>
        </div>

        {/* To Currency */}
        <div className="space-y-2">
          <Label htmlFor="to_currency">To Currency</Label>
          <CurrencySelector
            id="to_currency"
            value={toCurrency}
            onValueChange={(value) => {
              setToCurrency(value);
              setResult(null);
            }}
          />
        </div>

        {/* Convert Button */}
        <Button
          onClick={handleConvert}
          disabled={convertMutation.isPending}
          className="w-full"
        >
          {convertMutation.isPending ? "Converting..." : "Convert"}
        </Button>

        {/* Result */}
        {result && (
          <div className="p-4 bg-primary/10 border border-primary/20 rounded-lg space-y-3">
            <div className="text-center">
              <p className="text-sm text-muted-foreground mb-1">Converted Amount</p>
              <p className="text-3xl font-bold text-primary">
                {result.converted_amount.toFixed(2)} {result.to_currency}
              </p>
            </div>
            
            <div className="pt-3 border-t border-primary/20 space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Original Amount:</span>
                <span className="font-semibold">
                  {result.original_amount.toFixed(2)} {result.from_currency}
                </span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Exchange Rate:</span>
                <span className="font-semibold">
                  1 {result.from_currency} = {result.exchange_rate.toFixed(6)} {result.to_currency}
                </span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Conversion Date:</span>
                <span className="font-semibold">
                  {new Date(result.conversion_date).toLocaleDateString()}
                </span>
              </div>
            </div>

            {/* Reverse Calculation */}
            <div className="pt-3 border-t border-primary/20">
              <p className="text-xs text-muted-foreground text-center">
                Reverse: 1 {result.to_currency} = {(1 / result.exchange_rate).toFixed(6)} {result.from_currency}
              </p>
            </div>
          </div>
        )}

        {/* Info */}
        <Alert>
          <AlertCircle className="h-4 w-4" />
          <AlertDescription className="text-xs">
            Conversion uses the latest available exchange rate. For historical conversions, use the transaction forms with specific dates.
          </AlertDescription>
        </Alert>
      </CardContent>
    </Card>
  );
};

