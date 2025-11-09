import { useState } from "react";
import { Link } from "react-router-dom";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { FinancialHealthScore } from "@/components/FinancialHealthScore";
import { TrendAnalysisChart } from "@/components/TrendAnalysisChart";
import { YearOverYearComparison } from "@/components/YearOverYearComparison";
import { SpendingPatterns } from "@/components/SpendingPatterns";
import { PredictionsChart } from "@/components/PredictionsChart";
import { ExportButton } from "@/components/ExportButton";
import {
  BarChart3,
  TrendingUp,
  Activity,
  Brain,
  Heart,
  Wallet,
  ArrowLeft
} from "lucide-react";

const Analytics = () => {
  const [activeTab, setActiveTab] = useState("health");

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card shadow-sm">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Link to="/">
                <Button variant="ghost" size="icon">
                  <ArrowLeft className="h-5 w-5" />
                </Button>
              </Link>
              <div className="p-2 rounded-lg bg-gradient-primary">
                <Wallet className="h-6 w-6 text-primary-foreground" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-foreground">FIN-DASH Analytics</h1>
                <p className="text-sm text-muted-foreground">Advanced financial insights and predictions</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <ExportButton
                exportType="financial_summary"
                variant="outline"
                size="sm"
                label="Export Report"
              />
              <div className="hidden sm:block text-right">
                <p className="text-sm font-medium text-muted-foreground">October 2025</p>
                <p className="text-xs text-muted-foreground">Enhanced Reporting & Analytics</p>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-5 lg:w-auto lg:inline-grid">
            <TabsTrigger value="health" className="flex items-center gap-2">
              <Heart className="h-4 w-4" />
              <span className="hidden sm:inline">Health Score</span>
            </TabsTrigger>
            <TabsTrigger value="trends" className="flex items-center gap-2">
              <TrendingUp className="h-4 w-4" />
              <span className="hidden sm:inline">Trends</span>
            </TabsTrigger>
            <TabsTrigger value="yoy" className="flex items-center gap-2">
              <BarChart3 className="h-4 w-4" />
              <span className="hidden sm:inline">Year-over-Year</span>
            </TabsTrigger>
            <TabsTrigger value="patterns" className="flex items-center gap-2">
              <Activity className="h-4 w-4" />
              <span className="hidden sm:inline">Patterns</span>
            </TabsTrigger>
            <TabsTrigger value="predictions" className="flex items-center gap-2">
              <Brain className="h-4 w-4" />
              <span className="hidden sm:inline">Predictions</span>
            </TabsTrigger>
          </TabsList>

          {/* Financial Health Score Tab */}
          <TabsContent value="health" className="space-y-6">
            <FinancialHealthScore />
          </TabsContent>

          {/* Trend Analysis Tab */}
          <TabsContent value="trends" className="space-y-6">
            <TrendAnalysisChart />
            
            {/* Additional Trend Charts */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <TrendAnalysisChart 
                defaultMetric="expenses" 
                defaultPeriodType="monthly"
                showControls={false}
              />
              <TrendAnalysisChart 
                defaultMetric="net" 
                defaultPeriodType="monthly"
                showControls={false}
              />
            </div>
          </TabsContent>

          {/* Year-over-Year Tab */}
          <TabsContent value="yoy" className="space-y-6">
            <YearOverYearComparison />
          </TabsContent>

          {/* Spending Patterns Tab */}
          <TabsContent value="patterns" className="space-y-6">
            <SpendingPatterns />
          </TabsContent>

          {/* Predictions Tab */}
          <TabsContent value="predictions" className="space-y-6">
            <PredictionsChart />
            
            {/* Additional Prediction Charts */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="space-y-4">
                <h3 className="text-lg font-semibold">Income Forecast</h3>
                <PredictionsChart />
              </div>
              <div className="space-y-4">
                <h3 className="text-lg font-semibold">Expense Forecast</h3>
                <PredictionsChart />
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
};

export default Analytics;

