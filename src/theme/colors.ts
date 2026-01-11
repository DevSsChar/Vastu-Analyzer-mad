/**
 * VastuWise AI - Theme Colors
 * Central color palette for consistent theming
 */

export const colors = {
  // Primary Colors
  primary: '#db7706',
  primaryDark: '#b45309',
  primaryLight: '#f59e0b',
  
  // Background Colors
  backgroundLight: '#fffaf5',
  backgroundDark: '#231a0f',
  
  // Surface Colors
  surfaceLight: '#ffffff',
  surfaceDark: '#2d2419',
  
  // Text Colors
  textPrimary: '#1b150e',
  textSecondary: '#97754e',
  textLight: '#ffffff',
  textDark: '#0f172a',
  
  // Accent Colors
  accent: '#ca7616',
  accentLight: '#fef3c7',
  
  // Neutral Colors
  gray50: '#fafaf9',
  gray100: '#f5f5f4',
  gray200: '#e7e5e4',
  gray300: '#d6d3d1',
  gray400: '#a8a29e',
  gray500: '#78716c',
  gray600: '#57534e',
  gray700: '#44403c',
  gray800: '#292524',
  gray900: '#1c1917',
  
  // Semantic Colors
  success: '#22c55e',
  error: '#ef4444',
  warning: '#f59e0b',
  info: '#3b82f6',
  
  // Opacity Variants
  primaryOpacity: (opacity: number) => `rgba(219, 119, 6, ${opacity})`,
  whiteOpacity: (opacity: number) => `rgba(255, 255, 255, ${opacity})`,
  blackOpacity: (opacity: number) => `rgba(0, 0, 0, ${opacity})`,
};
