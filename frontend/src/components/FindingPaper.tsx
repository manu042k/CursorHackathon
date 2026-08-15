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
      <ul className="finding__citations">
        {paper.summary_narrative.citations.map((citation) => (
          <li key={`${citation.agent_id}-${citation.round}-${citation.run_id}`}>
            <button
              type="button"
              className="button-secondary"
              onClick={() => setSelectedRound(citation.round)}
            >
              {citation.agent_id} · R{citation.round} · {citation.run_id}
            </button>
          </li>
        ))}
      </ul>
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
