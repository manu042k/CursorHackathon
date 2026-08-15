import type { FailedEvent, RoundCompleteEvent } from "@/types/contracts";
import { API_BASE } from "@/lib/api";

export type ProgressHandlers = {
  onRound: (event: RoundCompleteEvent) => void;
  onComplete: (id: string) => void;
  onFailed: (error: string) => void;
};

export function subscribeExperimentEvents(id: string, handlers: ProgressHandlers): () => void {
  const source = new EventSource(`${API_BASE}/experiments/${id}/events`);
  source.addEventListener("round_complete", (message) => {
    handlers.onRound(JSON.parse((message as MessageEvent).data) as RoundCompleteEvent);
  });
  source.addEventListener("complete", (message) => {
    const payload = JSON.parse((message as MessageEvent).data) as { id: string };
    handlers.onComplete(payload.id);
    source.close();
  });
  source.addEventListener("failed", (message) => {
    const payload = JSON.parse((message as MessageEvent).data) as FailedEvent;
    handlers.onFailed(payload.error);
    source.close();
  });
  source.onerror = () => {
    /* EventSource reconnects; the server replays the log. Do not invent ticks. */
  };
  return () => source.close();
}
