/**
 * Utility functions for formatting data in the frontend.
 */

/**
 * Format a number with thousand separators.
 */
export function formatNumber(num: number | null | undefined): string {
  if (num === null || num === undefined) {
    return "N/A";
  }
  return new Intl.NumberFormat("en-US").format(num);
}

/**
 * Format a date string to a human-readable format.
 */
export function formatDate(dateString: string | null | undefined): string {
  if (!dateString) {
    return "Unknown";
  }
  try {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    }).format(date);
  } catch {
    return dateString;
  }
}

/**
 * Get a freshness indicator color based on days since last update.
 */
export function getFreshnessColor(freshnessDays: number | null | undefined): string {
  if (freshnessDays === null || freshnessDays === undefined) {
    return "text-gray-500";
  }
  if (freshnessDays <= 7) {
    return "text-green-600";
  }
  if (freshnessDays <= 30) {
    return "text-yellow-600";
  }
  return "text-red-600";
}

/**
 * Get a freshness indicator text based on days since last update.
 */
export function getFreshnessText(freshnessDays: number | null | undefined): string {
  if (freshnessDays === null || freshnessDays === undefined) {
    return "Unknown";
  }
  if (freshnessDays === 0) {
    return "Today";
  }
  if (freshnessDays === 1) {
    return "Yesterday";
  }
  if (freshnessDays < 7) {
    return `${freshnessDays} days ago`;
  }
  if (freshnessDays < 30) {
    const weeks = Math.floor(freshnessDays / 7);
    return `${weeks} week${weeks > 1 ? "s" : ""} ago`;
  }
  const months = Math.floor(freshnessDays / 30);
  return `${months} month${months > 1 ? "s" : ""} ago`;
}

/**
 * Get bounding box from extent array.
 */
export function getBBox(extent: [number, number, number, number]): [number, number, number, number] {
  return extent;
}
