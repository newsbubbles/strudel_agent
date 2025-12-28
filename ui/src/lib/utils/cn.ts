/**
 * Class Name Utility
 *
 * Merges Tailwind CSS classes using tailwind-merge and clsx
 * Prevents class conflicts and handles conditional classes
 */

import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

/**
 * Merge class names with Tailwind-aware deduplication
 *
 * @param inputs - Class names to merge
 * @returns Merged class string
 *
 * @example
 * cn('px-4 py-2', 'px-6') // => 'py-2 px-6' (px-4 overridden)
 * cn('text-red-500', condition && 'text-blue-500') // => conditional classes
 */
export function cn(...inputs: ClassValue[]) {
	return twMerge(clsx(inputs));
}
