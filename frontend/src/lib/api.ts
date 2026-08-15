import type {
  CreateExperimentRequest,
  CreateExperimentResponse,
  ExperimentListItem,
  HealthResponse,
  Roster,
} from "@/types/contracts";

export const API_BASE =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") || "http://localhost:8000";

export class ApiDownError extends Error {
  constructor(message = "API is not running.") {
    super(message);
    this.name = "ApiDownError";
  }
}

export async function getExperiment(id: string): Promise<{
  status: number;
  body: unknown;
}> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE}/experiments/${id}`);
  } catch {
    throw new ApiDownError();
  }
  let body: unknown = null;
  try {
    body = await response.json();
  } catch {
    body = null;
  }
  return { status: response.status, body };
}

export async function listExperiments(): Promise<ExperimentListItem[]> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE}/experiments`);
  } catch {
    throw new ApiDownError();
  }
  if (!response.ok) throw new ApiDownError(`API returned ${response.status}.`);
  return (await response.json()) as ExperimentListItem[];
}

export async function createExperiment(
  body: CreateExperimentRequest
): Promise<CreateExperimentResponse> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE}/experiments`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
  } catch {
    throw new ApiDownError();
  }
  if (!response.ok && response.status !== 202) {
    throw new ApiDownError(`API returned ${response.status}.`);
  }
  return (await response.json()) as CreateExperimentResponse;
}

export async function startExperiment(id: string): Promise<CreateExperimentResponse> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE}/experiments/${id}/start`, { method: "POST" });
  } catch {
    throw new ApiDownError();
  }
  if (!response.ok && response.status !== 202) {
    throw new ApiDownError(`API returned ${response.status}.`);
  }
  return (await response.json()) as CreateExperimentResponse;
}

export async function waitRosterReady(id: string, timeoutMs = 20000): Promise<Roster> {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    const { status, body } = await getExperiment(id);
    if (
      status === 200 &&
      body &&
      typeof body === "object" &&
      (body as { status?: string }).status === "roster_ready" &&
      "roster" in body
    ) {
      return (body as { roster: Roster }).roster;
    }
    await new Promise((resolve) => setTimeout(resolve, 200));
  }
  throw new ApiDownError("Roster was not ready in time.");
}

export async function getHealth(): Promise<HealthResponse | null> {
  try {
    const response = await fetch(`${API_BASE}/health`);
    if (!response.ok) return null;
    return (await response.json()) as HealthResponse;
  } catch {
    return null;
  }
}
