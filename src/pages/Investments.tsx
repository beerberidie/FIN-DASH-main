import { useState } from "react";
import { Link } from "react-router-dom";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { InvestmentList } from "@/components/InvestmentList";
import { PortfolioDashboard } from "@/components/PortfolioDashboard";
import { AssetAllocationChart } from "@/components/AssetAllocationChart";
import { PerformanceChart } from "@/components/PerformanceChart";
import { ExportButton } from "@/components/ExportButton";
import {
  TrendingUp,
  List,
  PieChart,
  BarChart3,
  Wallet,
  ArrowLeft
} from "lucide-react";

const Investments = () => {
  const [activeTab, setActiveTab] = useState("portfolio");

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
                <h1 className="text-2xl font-bold text-foreground">FIN-DASH Investments</h1>
                <p className="text-sm text-muted-foreground">Track and manage your investment portfolio</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <ExportButton
                exportType="investment_portfolio"
                variant="outline"
                size="sm"
                label="Export Portfolio"
              />
              <div className="hidden sm:block text-right">
                <p className="text-sm font-medium text-muted-foreground">October 2025</p>
                <p className="text-xs text-muted-foreground">Investment Tracking</p>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-4 lg:w-auto lg:inline-grid">
            <TabsTrigger value="portfolio" className="flex items-center gap-2">
              <TrendingUp className="h-4 w-4" />
              <span className="hidden sm:inline">Portfolio</span>
            </TabsTrigger>
            <TabsTrigger value="investments" className="flex items-center gap-2">
              <List className="h-4 w-4" />
              <span className="hidden sm:inline">Investments</span>
            </TabsTrigger>
            <TabsTrigger value="allocation" className="flex items-center gap-2">
              <PieChart className="h-4 w-4" />
              <span className="hidden sm:inline">Allocation</span>
            </TabsTrigger>
            <TabsTrigger value="performance" className="flex items-center gap-2">
              <BarChart3 className="h-4 w-4" />
              <span className="hidden sm:inline">Performance</span>
            </TabsTrigger>
          </TabsList>

          {/* Portfolio Dashboard Tab */}
          <TabsContent value="portfolio" className="space-y-6">
            <PortfolioDashboard />
          </TabsContent>

          {/* Investments List Tab */}
          <TabsContent value="investments" className="space-y-6">
            <InvestmentList />
          </TabsContent>

          {/* Asset Allocation Tab */}
          <TabsContent value="allocation" className="space-y-6">
            <AssetAllocationChart />
          </TabsContent>

          {/* Performance Tab */}
          <TabsContent value="performance" className="space-y-6">
            <PerformanceChart />
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
};

export default Investments;

