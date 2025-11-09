/**
 * Demo Mode Context
 * 
 * Manages demo mode state across the application.
 * When demo mode is enabled, the app uses sample data instead of real user data.
 */

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface DemoModeContextType {
  isDemoMode: boolean;
  toggleDemoMode: () => void;
  enableDemoMode: () => void;
  disableDemoMode: () => void;
  resetDemoData: () => Promise<void>;
  isResetting: boolean;
}

const DemoModeContext = createContext<DemoModeContextType | undefined>(undefined);

interface DemoModeProviderProps {
  children: ReactNode;
}

export const DemoModeProvider: React.FC<DemoModeProviderProps> = ({ children }) => {
  const [isDemoMode, setIsDemoMode] = useState<boolean>(() => {
    // Initialize from localStorage
    const stored = localStorage.getItem('demoMode');
    return stored === 'true';
  });
  
  const [isResetting, setIsResetting] = useState<boolean>(false);

  // Sync to localStorage whenever demo mode changes
  useEffect(() => {
    localStorage.setItem('demoMode', isDemoMode.toString());
    console.log(`Demo mode ${isDemoMode ? 'enabled' : 'disabled'}`);
  }, [isDemoMode]);

  const toggleDemoMode = () => {
    setIsDemoMode(prev => !prev);
  };

  const enableDemoMode = () => {
    setIsDemoMode(true);
  };

  const disableDemoMode = () => {
    setIsDemoMode(false);
  };

  const resetDemoData = async () => {
    if (!isDemoMode) {
      console.warn('Cannot reset demo data when not in demo mode');
      return;
    }

    setIsResetting(true);
    
    try {
      const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8777/api';
      const response = await fetch(`${API_BASE}/demo/reset`, {
        method: 'POST',
      });

      if (!response.ok) {
        throw new Error('Failed to reset demo data');
      }

      const result = await response.json();
      console.log('Demo data reset:', result);

      // Reload the page to refresh all data
      window.location.reload();
    } catch (error) {
      console.error('Error resetting demo data:', error);
      throw error;
    } finally {
      setIsResetting(false);
    }
  };

  const value: DemoModeContextType = {
    isDemoMode,
    toggleDemoMode,
    enableDemoMode,
    disableDemoMode,
    resetDemoData,
    isResetting,
  };

  return (
    <DemoModeContext.Provider value={value}>
      {children}
    </DemoModeContext.Provider>
  );
};

export const useDemoMode = (): DemoModeContextType => {
  const context = useContext(DemoModeContext);
  if (context === undefined) {
    throw new Error('useDemoMode must be used within a DemoModeProvider');
  }
  return context;
};

