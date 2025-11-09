import { useQuery } from "@tanstack/react-query";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import * as api from "@/services/api";

interface CurrencySelectorProps {
  value: string;
  onValueChange: (value: string) => void;
  disabled?: boolean;
  id?: string;
}

export const CurrencySelector = ({ value, onValueChange, disabled, id }: CurrencySelectorProps) => {
  const { data: currencies, isLoading } = useQuery({
    queryKey: ['currencies', true],
    queryFn: () => api.getCurrencies(true), // Only active currencies
  });

  if (isLoading) {
    return <Skeleton className="h-10 w-full" />;
  }

  return (
    <Select value={value} onValueChange={onValueChange} disabled={disabled}>
      <SelectTrigger id={id}>
        <SelectValue placeholder="Select currency" />
      </SelectTrigger>
      <SelectContent>
        {currencies?.map((currency) => (
          <SelectItem key={currency.code} value={currency.code}>
            <div className="flex items-center gap-2">
              <span className="font-semibold">{currency.code}</span>
              <span className="text-muted-foreground">-</span>
              <span className="text-lg">{currency.symbol}</span>
              <span className="text-muted-foreground text-sm">({currency.name})</span>
            </div>
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
};

