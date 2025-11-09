/**
 * Formatting utilities for currency, dates, and numbers
 */

/**
 * Format currency in South African Rand (ZAR)
 */
export const formatCurrency = (amount: number): string => {
  return new Intl.NumberFormat('en-ZA', {
    style: 'currency',
    currency: 'ZAR',
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  }).format(amount).replace('ZAR', 'R');
};

/**
 * Format percentage
 */
export const formatPercentage = (value: number, decimals: number = 1): string => {
  return `${value >= 0 ? '+' : ''}${value.toFixed(decimals)}%`;
};

/**
 * Format date to readable format (e.g., "Oct 5, 2025")
 */
export const formatDate = (dateString: string): string => {
  const date = new Date(dateString);
  return new Intl.DateTimeFormat('en-ZA', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  }).format(date);
};

/**
 * Format date to short format (e.g., "Oct 5")
 */
export const formatDateShort = (dateString: string): string => {
  const date = new Date(dateString);
  return new Intl.DateTimeFormat('en-ZA', {
    month: 'short',
    day: 'numeric',
  }).format(date);
};

/**
 * Get trend direction from percentage change
 */
export const getTrend = (change: number): 'up' | 'down' => {
  return change >= 0 ? 'up' : 'down';
};

/**
 * Format large numbers with K/M suffix
 */
export const formatCompactNumber = (num: number): string => {
  if (num >= 1000000) {
    return `R ${(num / 1000000).toFixed(1)}M`;
  }
  if (num >= 1000) {
    return `R ${(num / 1000).toFixed(1)}K`;
  }
  return formatCurrency(num);
};

