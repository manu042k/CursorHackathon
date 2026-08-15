"use client";

import { useState } from "react";
import { Receipt } from "@/components/Receipt";
import { MetricCards, PaperHeader } from "@/components/PaperHeader";
import { AttributionBar } from "@/components/AttributionBar";
import { ReasonTrace } from "@/components/ReasonTrace";
import { TwinChart } from "@/components/TwinChart";
import { firstMajorRound } from "@/lib/rounds";
import type { ExperimentPaper } from "@/types/contracts";

export function FindingPaper({ paper }: { paper: ExperimentPaper }) {
  const [selectedRound, setSelectedRound] = useState(() => firstMajorRound(paper));
  return (
    <article className="finding">
      <PaperHeader paper={paper} />
      <p className="finding__narrative">{paper.summary_narrative.text}</p>
      <MetricCards paper={paper} />
      <TwinChart
        paper={paper}
        selectedRound={selectedRound}
        onSelectRound={setSelectedRound}
      />
      <AttributionBar paper={paper} selectedRound={selectedRound} />
      <ReasonTrace
        paper={paper}
        selectedRound={selectedRound}
        onSelectRound={setSelectedRound}
      />
      <Receipt receipt={paper.receipt} />
    </article>
  );
}
