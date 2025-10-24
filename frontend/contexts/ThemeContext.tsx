/**
 * Theme Context Provider
 *
 * Provides dark/light theme toggle with localStorage persistence.
 *
 * Phase 4A: UX Polish - Theme System
 */

import React, { createContext, useContext, useEffect, useState } from 'react';

type Theme = 'dark' | 'light';

interface ThemeColors {
  background: string;
  backgroundSecondary: string;
  backgroundTertiary: string;
  text: string;
  textSecondary: string;
  textTertiary: string;
  primary: string;
  primaryHover: string;
  success: string;
  error: string;
  warning: string;
  border: string;
  borderHover: string;
  glass: string;
  shadow: string;
}

interface ThemeContextType {
  theme: Theme;
  toggleTheme: () => void;
  colors: ThemeColors;
}

const darkTheme: ThemeColors = {
  background: '#0f172a',
  backgroundSecondary: '#1e293b',
  backgroundTertiary: '#334155',
  text: '#ffffff',
  textSecondary: '#cbd5e1',
  textTertiary: '#94a3b8',
  primary: '#10b981',
  primaryHover: '#059669',
  success: '#10b981',
  error: '#ef4444',
  warning: '#f59e0b',
  border: 'rgba(71, 85, 105, 0.3)',
  borderHover: 'rgba(71, 85, 105, 0.6)',
  glass: 'rgba(15, 23, 42, 0.6)',
  shadow: 'rgba(0, 0, 0, 0.3)',
};

const lightTheme: ThemeColors = {
  background: '#ffffff',
  backgroundSecondary: '#f8fafc',
  backgroundTertiary: '#e2e8f0',
  text: '#0f172a',
  textSecondary: '#475569',
  textTertiary: '#64748b',
  primary: '#10b981',
  primaryHover: '#059669',
  success: '#10b981',
  error: '#ef4444',
  warning: '#f59e0b',
  border: 'rgba(203, 213, 225, 0.5)',
  borderHover: 'rgba(203, 213, 225, 0.8)',
  glass: 'rgba(255, 255, 255, 0.8)',
  shadow: 'rgba(0, 0, 0, 0.1)',
};

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [theme, setTheme] = useState<Theme>('dark');
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    // Load theme from localStorage
    const savedTheme = localStorage.getItem('paiid-theme') as Theme;
    if (savedTheme) {
      setTheme(savedTheme);
    } else {
      // Check system preference
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      setTheme(prefersDark ? 'dark' : 'light');
    }
    setMounted(true);
  }, []);

  useEffect(() => {
    if (mounted) {
      // Save theme to localStorage
      localStorage.setItem('paiid-theme', theme);

      // Update document class for global styles
      document.documentElement.classList.remove('dark', 'light');
      document.documentElement.classList.add(theme);

      // Update meta theme-color for mobile browsers
      const metaThemeColor = document.querySelector('meta[name="theme-color"]');
      if (metaThemeColor) {
        metaThemeColor.setAttribute('content', theme === 'dark' ? '#0f172a' : '#ffffff');
      }
    }
  }, [theme, mounted]);

  const toggleTheme = () => {
    setTheme((prev) => (prev === 'dark' ? 'light' : 'dark'));
  };

  const colors = theme === 'dark' ? darkTheme : lightTheme;

  if (!mounted) {
    // Prevent flash of unstyled content
    return null;
  }

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme, colors }}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider');
  }
  return context;
};

export default ThemeContext;
