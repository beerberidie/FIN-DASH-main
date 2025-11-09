import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { DemoModeProvider } from "@/contexts/DemoModeContext";
import { DemoModeBanner } from "@/components/DemoModeBanner";
import Index from "./pages/Index";
import Analytics from "./pages/Analytics";
import Investments from "./pages/Investments";
import Currencies from "./pages/Currencies";
import Exports from "./pages/Exports";
import Cards from "./pages/Cards";
import Accounts from "./pages/Accounts";
import Categories from "./pages/Categories";
import Budgets from "./pages/Budgets";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <DemoModeProvider>
      <TooltipProvider>
        <Toaster />
        <Sonner />
        <BrowserRouter>
          <DemoModeBanner />
          <Routes>
            <Route path="/" element={<Index />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/investments" element={<Investments />} />
            <Route path="/currencies" element={<Currencies />} />
            <Route path="/exports" element={<Exports />} />
            <Route path="/cards" element={<Cards />} />
            <Route path="/accounts" element={<Accounts />} />
            <Route path="/categories" element={<Categories />} />
            <Route path="/budgets" element={<Budgets />} />
            {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
            <Route path="*" element={<NotFound />} />
          </Routes>
        </BrowserRouter>
      </TooltipProvider>
    </DemoModeProvider>
  </QueryClientProvider>
);

export default App;
