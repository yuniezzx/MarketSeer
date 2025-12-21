import { clsx } from "clsx";
import { twMerge } from "tailwind-merge"

export function cn(...inputs) {
  return twMerge(clsx(inputs));
}

export function getTurnoverRateColor(rate) {
  if (rate < 1) return 'text-neutral-stock';
  if (rate < 3) return 'text-primary dark:text-primary';
  if (rate < 7) return 'text-bull';
  if (rate < 15) return 'text-orange-500 dark:text-orange-400';
  if (rate < 30) return 'text-red-600 dark:text-red-400';
  if (rate < 50) return 'text-red-700 dark:text-red-300';
  return 'text-pink-600 dark:text-pink-400';
}
