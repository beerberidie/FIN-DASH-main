import { useState } from "react";
import { Link } from "react-router-dom";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { CurrencyList } from "@/components/CurrencyList";
import { ExchangeRateManager } from "@/components/ExchangeRateManager";
import { CurrencyConverter } from "@/components/CurrencyConverter";
import { 
  Coins, 
  TrendingUp, 
  Calculator,
  List,
  ArrowLeft
} from "lucide-react";

const Currencies = () => {
  const [activeTab, setActiveTab] = useState("currencies");

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
                <Coins className="h-6 w-6 text-primary-foreground" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-foreground">FIN-DASH Currencies</h1>
                <p className="text-sm text-muted-foreground">Manage currencies and exchange rates</p>
              </div>
            </div>
            <div className="hidden sm:block text-right">
              <p className="text-sm font-medium text-muted-foreground">October 2025</p>
              <p className="text-xs text-muted-foreground">Multi-Currency Support</p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-3 lg:w-auto lg:inline-grid">
            <TabsTrigger value="currencies" className="flex items-center gap-2">
              <List className="h-4 w-4" />
              <span className="hidden sm:inline">Currencies</span>
            </TabsTrigger>
            <TabsTrigger value="rates" className="flex items-center gap-2">
              <TrendingUp className="h-4 w-4" />
              <span className="hidden sm:inline">Exchange Rates</span>
            </TabsTrigger>
            <TabsTrigger value="converter" className="flex items-center gap-2">
              <Calculator className="h-4 w-4" />
              <span className="hidden sm:inline">Converter</span>
            </TabsTrigger>
          </TabsList>

          {/* Currencies Tab */}
          <TabsContent value="currencies" className="space-y-6">
            <CurrencyList />
          </TabsContent>

          {/* Exchange Rates Tab */}
          <TabsContent value="rates" className="space-y-6">
            <ExchangeRateManager />
          </TabsContent>

          {/* Converter Tab */}
          <TabsContent value="converter" className="space-y-6">
            <div className="max-w-2xl mx-auto">
              <CurrencyConverter />
            </div>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
};

export default Currencies;

