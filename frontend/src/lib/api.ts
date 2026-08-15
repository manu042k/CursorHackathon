import type { CreateExperimentRequest, CreateExperimentResponse } from "@/types/contracts";

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
