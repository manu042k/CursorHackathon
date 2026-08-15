"use client";

import Link from "next/link";
import { useState } from "react";
import { Receipt } from "@/components/Receipt";
import { MetricCards, PaperHeader } from "@/components/PaperHeader";
import { AttributionBar } from "@/components/AttributionBar";
import { ReasonTrace } from "@/components/ReasonTrace";
import { RosterPreview } from "@/components/RosterPreview";
import { TwinChart } from "@/components/TwinChart";
import { PersonaOutcomes } from "@/components/PersonaOutcomes";
import { CompetitorPath } from "@/components/CompetitorPath";
import { Button } from "@/components/ui/button";
import { firstMajorRound } from "@/lib/rounds";
import type { ExperimentPaper } from "@/types/contracts";

export function FindingPaper({ paper }: { paper: ExperimentPaper }) {
  const [selectedRound, setSelectedRound] = useState(() => firstMajorRound(paper));
  return (
    <article className="finding mx-auto max-w-5xl px-6 py-10">
      <PaperHeader paper={paper} />
      <p className="finding__narrative mt-6 text-lg text-muted-foreground">{paper.summary_narrative.text}</p>
      <ul className="finding__citations mt-4 mb-8 flex flex-wrap gap-2">
        {paper.summary_narrative.citations.map((citation) => (
          <li key={`${citation.agent_id}-${citation.round}-${citation.run_id}`}>
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={() => setSelectedRound(citation.round)}
            >
              {citation.agent_id} · R{citation.round} · {citation.run_id}
            </Button>
          </li>
        ))}
      </ul>
      <MetricCards paper={paper} />
      <TwinChart
        paper={paper}
        selectedRound={selectedRound}
        onSelectRound={setSelectedRound}
      />
      <PersonaOutcomes paper={paper} />
      <CompetitorPath paper={paper} />
      <AttributionBar paper={paper} selectedRound={selectedRound} />
      <ReasonTrace
        paper={paper}
        selectedRound={selectedRound}
        onSelectRound={setSelectedRound}
      />
      <RosterPreview paper={paper} />
      <Receipt receipt={paper.receipt} />
      <p className="finding__next mt-10">
        <Button asChild>
          <Link href="/new">New experiment</Link>
        </Button>
      </p>
    </article>
  );
}
