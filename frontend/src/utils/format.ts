export const getBBox = (extent: [number, number, number, number]): [number, number, number, number] => {
  return extent;
}

export const formatDate = (dateString: string): string => {
  try {
    const date = new Date(dateString);
    return date.toLocaleDateString();
  } catch {
    return dateString;
  }
}

export const formatNumber = (num: number | null | undefined): string => {
  if (num === null || num === undefined) return "-";
  return num.toLocaleString();
}

