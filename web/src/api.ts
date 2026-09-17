// Mirror of the backend contract (api/app/schemas.py).
export type Citation = {
  title: string;
  page: number | null;
  snippet: string;
  score: number;
};

export type Answer = {
  text: string;
  grounded: boolean;
  model: string | null;
  citations: Citation[];
};

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export async function ask(question: string): Promise<Answer> {
  const res = await fetch(`${API_URL}/ask`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ question }),
  });
  if (!res.ok) {
    throw new Error(`API ${res.status}: ${await res.text()}`);
  }
  return res.json();
}
