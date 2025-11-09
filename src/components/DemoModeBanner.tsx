/**
 * Demo Mode Banner
 * 
 * Displays a prominent banner when demo mode is active.
 * Shows controls to reset demo data or exit demo mode.
 */

import React from 'react';
import { Info, RefreshCw, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useDemoMode } from '@/contexts/DemoModeContext';
import { useToast } from '@/hooks/use-toast';

export const DemoModeBanner: React.FC = () => {
  const { isDemoMode, disableDemoMode, resetDemoData, isResetting } = useDemoMode();
  const { toast } = useToast();

  if (!isDemoMode) {
    return null;
  }

  const handleReset = async () => {
    try {
      await resetDemoData();
      toast({
        title: "Demo Data Reset",
        description: "Demo data has been reset to initial state.",
      });
    } catch (error) {
      toast({
        title: "Reset Failed",
        description: "Failed to reset demo data. Please try again.",
        variant: "destructive",
      });
    }
  };

  const handleExit = () => {
    disableDemoMode();
    toast({
      title: "Demo Mode Disabled",
      description: "Switched back to your real data.",
    });
    // Reload to refresh data
    window.location.reload();
  };

  return (
    <div className="bg-blue-600 text-white px-4 py-3 shadow-md">
      <div className="container mx-auto flex items-center justify-between flex-wrap gap-2">
        <div className="flex items-center gap-3">
          <Info className="h-5 w-5 flex-shrink-0" />
          <div className="flex flex-col sm:flex-row sm:items-center sm:gap-2">
            <span className="font-semibold">Demo Mode Active</span>
            <span className="text-sm text-blue-100">
              Viewing sample data - Changes won't be saved
            </span>
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          <Button
            onClick={handleReset}
            disabled={isResetting}
            variant="secondary"
            size="sm"
            className="bg-white/20 hover:bg-white/30 text-white border-white/30"
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${isResetting ? 'animate-spin' : ''}`} />
            Reset Demo
          </Button>
          
          <Button
            onClick={handleExit}
            variant="secondary"
            size="sm"
            className="bg-white/20 hover:bg-white/30 text-white border-white/30"
          >
            <X className="h-4 w-4 mr-2" />
            Exit Demo
          </Button>
        </div>
      </div>
    </div>
  );
};

