import type { Receipt as ReceiptModel } from "@/types/contracts";

function shortHash(value: string | undefined): string {
  if (!value || value === "—") return "—";
  const hex = value.replace(/^sha256:/, "");
  if (hex.length <= 8) return value;
  return `sha256:${hex.slice(0, 8)}`;
}

const EMPTY: ReceiptModel = {
  random_seed: 42,
  prompt_hash: "—",
  roster_hash: "—",
  other_variables_changed: 0,
  adapter: "fixture",
  runtime: "local",
  model: "—",
  tools: [],
};

type Props = {
  receipt?: Partial<ReceiptModel> | null;
};

export function Receipt({ receipt }: Props) {
  const value = { ...EMPTY, ...receipt };
  const rows = [
    ["adapter", value.adapter],
    ["runtime", value.runtime],
    ["model", value.model || "—"],
    ["prompt_hash", shortHash(value.prompt_hash)],
    ["roster_hash", shortHash(value.roster_hash)],
    ["other_variables_changed", "0"],
  ];
  return (
    <dl className="receipt">
      {rows.map(([label, item]) => (
        <div key={label} className="receipt__row">
          <dt>{label}</dt>
          <dd>{item}</dd>
        </div>
      ))}
    </dl>
  );
}
