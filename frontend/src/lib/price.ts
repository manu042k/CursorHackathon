export function forkedPrice(base: number, delta: string): number {
  const text = delta.trim();
  if (text.endsWith("%")) {
    const pct = Number.parseFloat(text.slice(0, -1));
    return Math.round(base * (1 + pct / 100));
  }
  return base + Number.parseFloat(text);
}

export function hypothesisSentence(
  product: string,
  price: number,
  delta: string,
  fromRound: number
): string {
  const forked = forkedPrice(price, delta);
  return `Raise ${product} from $${price} to $${forked} starting round ${fromRound}.`;
}
