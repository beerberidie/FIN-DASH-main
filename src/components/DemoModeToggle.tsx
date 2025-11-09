/**
 * Demo Mode Toggle
 * 
 * A switch component to toggle demo mode on/off.
 * Can be placed in navigation or settings.
 */

import React from 'react';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { useDemoMode } from '@/contexts/DemoModeContext';
import { useToast } from '@/hooks/use-toast';
import { Eye, EyeOff } from 'lucide-react';

interface DemoModeToggleProps {
  showLabel?: boolean;
  showIcon?: boolean;
}

export const DemoModeToggle: React.FC<DemoModeToggleProps> = ({ 
  showLabel = true,
  showIcon = true 
}) => {
  const { isDemoMode, toggleDemoMode } = useDemoMode();
  const { toast } = useToast();

  const handleToggle = () => {
    toggleDemoMode();
    
    // Show toast notification
    toast({
      title: isDemoMode ? "Demo Mode Disabled" : "Demo Mode Enabled",
      description: isDemoMode 
        ? "Switched back to your real data." 
        : "Now viewing sample data. Perfect for exploring features!",
    });

    // Reload to refresh data
    setTimeout(() => {
      window.location.reload();
    }, 500);
  };

  return (
    <div className="flex items-center gap-2">
      {showIcon && (
        isDemoMode ? <Eye className="h-4 w-4 text-blue-600" /> : <EyeOff className="h-4 w-4 text-gray-400" />
      )}
      <Switch 
        id="demo-mode" 
        checked={isDemoMode} 
        onCheckedChange={handleToggle}
        className="data-[state=checked]:bg-blue-600"
      />
      {showLabel && (
        <Label 
          htmlFor="demo-mode" 
          className="cursor-pointer text-sm font-medium"
        >
          Demo Mode
        </Label>
      )}
    </div>
  );
};

