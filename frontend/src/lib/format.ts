export function formatCurrency(n: number): string {
  const safe = Number.isFinite(n) ? n : 0
  return 'Rs.' + safe.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

export function formatMoney(n: number): string {
  const safe = Number.isFinite(n) ? n : 0
  return 'Rs.' + safe.toLocaleString('en-IN', { maximumFractionDigits: 0 })
}

export const sleep = (ms: number) => new Promise<void>((resolve) => setTimeout(resolve, ms))
