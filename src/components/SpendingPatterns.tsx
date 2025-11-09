import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { 
  AlertCircle, 
  TrendingUp, 
  TrendingDown, 
  Calendar,
  Repeat,
  Activity
} from "lucide-react";
import * as api from "@/services/api";
import { formatCurrency } from "@/lib/formatters";
import { useToast } from "@/hooks/use-toast";

const getPatternIcon = (patternType: string) => {
  switch (patternType.toLowerCase()) {
    case 'consistent':
      return <Repeat className="h-5 w-5 text-blue-600" />;
    case 'increasing':
      return <TrendingUp className="h-5 w-5 text-red-600" />;
    case 'decreasing':
      return <TrendingDown className="h-5 w-5 text-green-600" />;
    case 'seasonal':
      return <Calendar className="h-5 w-5 text-purple-600" />;
    default:
      return <Activity className="h-5 w-5 text-gray-600" />;
  }
};

const getPatternColor = (patternType: string) => {
  switch (patternType.toLowerCase()) {
    case 'consistent':
      return 'bg-blue-50 text-blue-700 border-blue-200';
    case 'increasing':
      return 'bg-red-50 text-red-700 border-red-200';
    case 'decreasing':
      return 'bg-green-50 text-green-700 border-green-200';
    case 'seasonal':
      return 'bg-purple-50 text-purple-700 border-purple-200';
    default:
      return 'bg-gray-50 text-gray-700 border-gray-200';
  }
};

const getFrequencyBadge = (frequency: string) => {
  const colors: Record<string, string> = {
    daily: 'bg-orange-100 text-orange-800',
    weekly: 'bg-blue-100 text-blue-800',
    monthly: 'bg-green-100 text-green-800',
    quarterly: 'bg-purple-100 text-purple-800',
    yearly: 'bg-indigo-100 text-indigo-800',
  };
  
  return colors[frequency.toLowerCase()] || 'bg-gray-100 text-gray-800';
};

const getConfidenceLevel = (confidence: number) => {
  if (confidence >= 0.8) return { label: 'High', color: 'text-green-600' };
  if (confidence >= 0.5) return { label: 'Medium', color: 'text-yellow-600' };
  return { label: 'Low', color: 'text-red-600' };
};

export const SpendingPatterns = () => {
  const { toast } = useToast();

  const { data: patterns, isLoading, error } = useQuery({
    queryKey: ['spending-patterns'],
    queryFn: () => api.getSpendingPatterns(),
    onError: (err: Error) => {
      toast({
        title: "Error loading spending patterns",
        description: err.message || "Failed to load spending pattern data",
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
            {[1, 2, 3, 4].map((i) => (
              <Skeleton key={i} className="h-32 w-full" />
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error || !patterns) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <AlertCircle className="h-5 w-5 text-destructive" />
            Spending Patterns
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              {error?.message || "Failed to load spending patterns"}
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>
    );
  }

  if (patterns.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-6 w-6 text-primary" />
            Spending Patterns
          </CardTitle>
          <CardDescription>
            Detected patterns in your spending behavior
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Alert>
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              Not enough data to detect spending patterns. Continue tracking your expenses to see insights.
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>
    );
  }

  // Sort patterns by confidence (highest first)
  const sortedPatterns = [...patterns].sort((a, b) => b.confidence - a.confidence);

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Activity className="h-6 w-6 text-primary" />
          Spending Patterns
        </CardTitle>
        <CardDescription>
          Detected patterns in your spending behavior ({patterns.length} patterns found)
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {sortedPatterns.map((pattern, idx) => {
            const confidenceInfo = getConfidenceLevel(pattern.confidence);
            
            return (
              <Card key={idx} className="border-2">
                <CardContent className="pt-6">
                  <div className="space-y-4">
                    {/* Header */}
                    <div className="flex items-start justify-between">
                      <div className="flex items-start gap-3">
                        <div className="p-2 rounded-lg bg-primary/10">
                          {getPatternIcon(pattern.pattern_type)}
                        </div>
                        <div>
                          <h3 className="font-semibold text-lg">{pattern.category}</h3>
                          <p className="text-sm text-muted-foreground mt-1">
                            {pattern.description}
                          </p>
                        </div>
                      </div>
                      <Badge className={getPatternColor(pattern.pattern_type)}>
                        {pattern.pattern_type}
                      </Badge>
                    </div>

                    {/* Metrics */}
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                      <div>
                        <p className="text-xs text-muted-foreground">Average Amount</p>
                        <p className="text-xl font-bold">{formatCurrency(pattern.average_amount)}</p>
                      </div>
                      <div>
                        <p className="text-xs text-muted-foreground">Frequency</p>
                        <Badge className={getFrequencyBadge(pattern.frequency)}>
                          {pattern.frequency}
                        </Badge>
                      </div>
                      <div>
                        <p className="text-xs text-muted-foreground">Confidence</p>
                        <div className="flex items-center gap-2">
                          <span className={`text-xl font-bold ${confidenceInfo.color}`}>
                            {(pattern.confidence * 100).toFixed(0)}%
                          </span>
                          <span className={`text-xs ${confidenceInfo.color}`}>
                            {confidenceInfo.label}
                          </span>
                        </div>
                      </div>
                    </div>

                    {/* Confidence Bar */}
                    <div className="space-y-1">
                      <div className="flex items-center justify-between text-xs">
                        <span className="text-muted-foreground">Pattern Confidence</span>
                        <span className={confidenceInfo.color}>{confidenceInfo.label}</span>
                      </div>
                      <Progress 
                        value={pattern.confidence * 100} 
                        className="h-2"
                        // @ts-ignore
                        indicatorClassName={
                          pattern.confidence >= 0.8 ? 'bg-green-500' :
                          pattern.confidence >= 0.5 ? 'bg-yellow-500' :
                          'bg-red-500'
                        }
                      />
                    </div>

                    {/* Insights */}
                    {pattern.pattern_type === 'increasing' && (
                      <Alert className="bg-red-50 border-red-200">
                        <TrendingUp className="h-4 w-4 text-red-600" />
                        <AlertDescription className="text-red-800">
                          Your spending in this category is increasing. Consider reviewing your budget.
                        </AlertDescription>
                      </Alert>
                    )}
                    
                    {pattern.pattern_type === 'decreasing' && (
                      <Alert className="bg-green-50 border-green-200">
                        <TrendingDown className="h-4 w-4 text-green-600" />
                        <AlertDescription className="text-green-800">
                          Great job! Your spending in this category is decreasing.
                        </AlertDescription>
                      </Alert>
                    )}

                    {pattern.pattern_type === 'seasonal' && (
                      <Alert className="bg-purple-50 border-purple-200">
                        <Calendar className="h-4 w-4 text-purple-600" />
                        <AlertDescription className="text-purple-800">
                          This category shows seasonal patterns. Plan ahead for peak periods.
                        </AlertDescription>
                      </Alert>
                    )}
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
};

