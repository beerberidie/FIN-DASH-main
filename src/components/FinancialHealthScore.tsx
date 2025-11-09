import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { 
  Heart, 
  TrendingUp, 
  Shield, 
  Target, 
  PiggyBank, 
  CreditCard,
  AlertCircle,
  CheckCircle2,
  Info
} from "lucide-react";
import * as api from "@/services/api";
import { useToast } from "@/hooks/use-toast";

const getStatusColor = (status: string) => {
  switch (status.toLowerCase()) {
    case 'excellent':
      return 'text-green-600 bg-green-50 border-green-200';
    case 'good':
      return 'text-blue-600 bg-blue-50 border-blue-200';
    case 'fair':
      return 'text-yellow-600 bg-yellow-50 border-yellow-200';
    case 'poor':
      return 'text-red-600 bg-red-50 border-red-200';
    default:
      return 'text-gray-600 bg-gray-50 border-gray-200';
  }
};

const getScoreColor = (score: number) => {
  if (score >= 80) return 'text-green-600';
  if (score >= 60) return 'text-blue-600';
  if (score >= 40) return 'text-yellow-600';
  return 'text-red-600';
};

const getProgressColor = (score: number) => {
  if (score >= 80) return 'bg-green-500';
  if (score >= 60) return 'bg-blue-500';
  if (score >= 40) return 'bg-yellow-500';
  return 'bg-red-500';
};

const getMetricIcon = (name: string) => {
  const lowerName = name.toLowerCase();
  if (lowerName.includes('savings')) return <PiggyBank className="h-5 w-5" />;
  if (lowerName.includes('emergency')) return <Shield className="h-5 w-5" />;
  if (lowerName.includes('debt')) return <CreditCard className="h-5 w-5" />;
  if (lowerName.includes('budget')) return <Target className="h-5 w-5" />;
  if (lowerName.includes('worth') || lowerName.includes('trend')) return <TrendingUp className="h-5 w-5" />;
  return <Heart className="h-5 w-5" />;
};

export const FinancialHealthScore = () => {
  const { toast } = useToast();

  const { data: healthScore, isLoading, error } = useQuery({
    queryKey: ['financial-health-score'],
    queryFn: () => api.getFinancialHealthScore(true, true),
    refetchInterval: 60000, // Refetch every minute
    onError: (err: Error) => {
      toast({
        title: "Error loading health score",
        description: err.message || "Failed to load financial health data",
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
        <CardContent className="space-y-6">
          <div className="flex items-center justify-center">
            <Skeleton className="h-48 w-48 rounded-full" />
          </div>
          <Skeleton className="h-24 w-full" />
          <Skeleton className="h-32 w-full" />
        </CardContent>
      </Card>
    );
  }

  if (error || !healthScore) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <AlertCircle className="h-5 w-5 text-destructive" />
            Financial Health Score
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              {error?.message || "Failed to load financial health score"}
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Overall Score Card */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Heart className="h-6 w-6 text-primary" />
            Financial Health Score
          </CardTitle>
          <CardDescription>
            Your overall financial wellness assessment
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Score Circle */}
          <div className="flex flex-col items-center justify-center py-8">
            <div className="relative">
              <div className="w-48 h-48 rounded-full border-8 border-gray-200 flex items-center justify-center">
                <div className="text-center">
                  <div className={`text-6xl font-bold ${getScoreColor(healthScore.overall_score)}`}>
                    {Math.round(healthScore.overall_score)}
                  </div>
                  <div className="text-sm text-muted-foreground mt-1">out of 100</div>
                </div>
              </div>
              <div 
                className="absolute inset-0 rounded-full border-8 border-transparent"
                style={{
                  borderTopColor: getProgressColor(healthScore.overall_score).replace('bg-', ''),
                  borderRightColor: healthScore.overall_score > 25 ? getProgressColor(healthScore.overall_score).replace('bg-', '') : 'transparent',
                  borderBottomColor: healthScore.overall_score > 50 ? getProgressColor(healthScore.overall_score).replace('bg-', '') : 'transparent',
                  borderLeftColor: healthScore.overall_score > 75 ? getProgressColor(healthScore.overall_score).replace('bg-', '') : 'transparent',
                  transform: 'rotate(-90deg)',
                }}
              />
            </div>
            <Badge className={`mt-4 ${getStatusColor(healthScore.overall_status)}`}>
              {healthScore.overall_status.toUpperCase()}
            </Badge>
          </div>

          {/* Strengths & Weaknesses */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Strengths */}
            {healthScore.strengths.length > 0 && (
              <div className="space-y-2">
                <h4 className="font-semibold text-sm flex items-center gap-2 text-green-600">
                  <CheckCircle2 className="h-4 w-4" />
                  Strengths
                </h4>
                <ul className="space-y-1">
                  {healthScore.strengths.map((strength, idx) => (
                    <li key={idx} className="text-sm text-muted-foreground flex items-start gap-2">
                      <span className="text-green-500 mt-0.5">•</span>
                      <span>{strength}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Weaknesses */}
            {healthScore.weaknesses.length > 0 && (
              <div className="space-y-2">
                <h4 className="font-semibold text-sm flex items-center gap-2 text-yellow-600">
                  <Info className="h-4 w-4" />
                  Areas for Improvement
                </h4>
                <ul className="space-y-1">
                  {healthScore.weaknesses.map((weakness, idx) => (
                    <li key={idx} className="text-sm text-muted-foreground flex items-start gap-2">
                      <span className="text-yellow-500 mt-0.5">•</span>
                      <span>{weakness}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          {/* Recommendations */}
          {healthScore.recommendations.length > 0 && (
            <Alert>
              <Info className="h-4 w-4" />
              <AlertDescription>
                <div className="space-y-2">
                  <p className="font-semibold">Recommendations:</p>
                  <ul className="space-y-1">
                    {healthScore.recommendations.map((rec, idx) => (
                      <li key={idx} className="text-sm flex items-start gap-2">
                        <span className="text-primary mt-0.5">{idx + 1}.</span>
                        <span>{rec}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </AlertDescription>
            </Alert>
          )}
        </CardContent>
      </Card>

      {/* Individual Metrics */}
      <Card>
        <CardHeader>
          <CardTitle>Health Metrics Breakdown</CardTitle>
          <CardDescription>
            Detailed breakdown of your financial health indicators
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            {healthScore.metrics.map((metric, idx) => (
              <div key={idx} className="space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className={getScoreColor(metric.score)}>
                      {getMetricIcon(metric.name)}
                    </div>
                    <div>
                      <h4 className="font-semibold text-sm">{metric.name}</h4>
                      <p className="text-xs text-muted-foreground">{metric.description}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className={`text-2xl font-bold ${getScoreColor(metric.score)}`}>
                      {Math.round(metric.score)}
                    </span>
                    <Badge variant="outline" className={getStatusColor(metric.status)}>
                      {metric.status}
                    </Badge>
                  </div>
                </div>
                <Progress 
                  value={metric.score} 
                  className="h-2"
                  // @ts-ignore - custom color prop
                  indicatorClassName={getProgressColor(metric.score)}
                />
                {metric.recommendation && (
                  <p className="text-xs text-muted-foreground italic">
                    💡 {metric.recommendation}
                  </p>
                )}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

