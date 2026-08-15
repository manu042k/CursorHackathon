import type { VariableType } from "@/types/contracts";

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
  fromRound: number,
  variableType: VariableType = "price_change",
  competitorPrice?: number
): string {
  if (variableType === "competitor_entry") {
    const rival = Number.isFinite(competitorPrice) ? competitorPrice! : 0;
    const forked = forkedPrice(rival, delta);
    return `A rival enters at $${forked} against ${product} starting round ${fromRound}.`;
  }
  if (variableType === "marketing_spend") {
    return `Spend ${delta} on marketing for ${product} starting round ${fromRound}.`;
  }
  if (variableType === "feature_change") {
    return `Change ${product} (${delta}) starting round ${fromRound}.`;
  }
  const forked = forkedPrice(price, delta);
  if (forked < price) {
    return `Lower ${product} from $${price} to $${forked} starting round ${fromRound}.`;
  }
  if (forked === price) {
    return `Hold ${product} at $${price} starting round ${fromRound}.`;
  }
  return `Raise ${product} from $${price} to $${forked} starting round ${fromRound}.`;
}
