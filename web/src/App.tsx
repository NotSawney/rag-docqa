import { useState } from "react";
import { ask, type Answer } from "./api";
import { AnswerText } from "./citations";

type Turn = {
  id: number;
  question: string;
  answer: Answer | null; // null while loading
  error: string | null;
};

const EXAMPLES = [
  "How many data sources can I connect on the Starter plan?",
  "How long are cached query results retained?",
  "Does Aurora support single sign-on?",
];

// Pretty label for the model badge (answer.model is a raw id).
function modelLabel(model: string): string {
  if (model.includes("haiku")) return "Claude Haiku 4.5";
  if (model.includes("sonnet")) return "Claude Sonnet 5";
  return model; // e.g. an Ollama model id
}

export default function App() {
  const [input, setInput] = useState("");
  const [turns, setTurns] = useState<Turn[]>([]);
  const [busy, setBusy] = useState(false);
  const [active, setActive] = useState<string | null>(null); // `${turnId}-${n}`

  async function submit(question: string) {
    const q = question.trim();
    if (!q || busy) return;
    const id = Date.now();
    setInput("");
    setBusy(true);
    setTurns((t) => [...t, { id, question: q, answer: null, error: null }]);
    try {
      const answer = await ask(q);
      setTurns((t) => t.map((x) => (x.id === id ? { ...x, answer } : x)));
    } catch (e) {
      const msg = e instanceof Error ? e.message : "Request failed";
      setTurns((t) => t.map((x) => (x.id === id ? { ...x, error: msg } : x)));
    } finally {
      setBusy(false);
    }
  }

  function jumpToSource(turnId: number, n: number) {
    const key = `${turnId}-${n}`;
    setActive(key);
    document.getElementById(`src-${key}`)?.scrollIntoView({ behavior: "smooth", block: "center" });
  }

  return (
    <div className="app">
      <header className="header">
        <h1>RAG Document Q&amp;A</h1>
        <p className="pitch">Grounded answers with source citations — RAG on your own infra, not a third-party SaaS.</p>
        <p className="stack">pgvector · local embeddings · anti-hallucination guard</p>
      </header>

      <main className="transcript">
        {turns.length === 0 && (
          <div className="empty">
            <p>Ask a question about the Aurora Analytics docs:</p>
            <div className="examples">
              {EXAMPLES.map((ex) => (
                <button key={ex} type="button" className="example" onClick={() => submit(ex)}>
                  {ex}
                </button>
              ))}
            </div>
          </div>
        )}

        {turns.map((turn) => (
          <section key={turn.id} className="turn">
            <div className="question">{turn.question}</div>

            {turn.answer === null && turn.error === null && (
              <div className="loading" aria-live="polite">
                <span className="dot" /> retrieving → generating…
              </div>
            )}

            {turn.error && <div className="error">Error: {turn.error}</div>}

            {turn.answer && !turn.answer.grounded && (
              <div className="refused">
                <span className="tag">outside corpus</span>
                <p>{turn.answer.text}</p>
              </div>
            )}

            {turn.answer && turn.answer.grounded && (
              <div className="answer">
                <div className="answer-head">
                  {turn.answer.model && <span className="model">{modelLabel(turn.answer.model)}</span>}
                </div>
                <AnswerText
                  text={turn.answer.text}
                  count={turn.answer.citations.length}
                  onCite={(n) => jumpToSource(turn.id, n)}
                />
                {turn.answer.citations.length > 0 && (
                  <div className="sources">
                    <h3>Sources</h3>
                    {turn.answer.citations.map((c, i) => {
                      const n = i + 1;
                      const key = `${turn.id}-${n}`;
                      return (
                        <div
                          key={key}
                          id={`src-${key}`}
                          className={`source ${active === key ? "active" : ""}`}
                        >
                          <div className="source-head">
                            <span className="source-n">{n}</span>
                            <span className="source-title">
                              {c.title}
                              {c.page != null && <span className="page"> · p. {c.page}</span>}
                            </span>
                            <span className="score" title="cosine similarity">
                              <span className="score-bar" style={{ width: `${Math.round(c.score * 100)}%` }} />
                              {c.score.toFixed(2)}
                            </span>
                          </div>
                          <p className="snippet">{c.snippet}</p>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            )}
          </section>
        ))}
      </main>

      <form
        className="composer"
        onSubmit={(e) => {
          e.preventDefault();
          submit(input);
        }}
      >
        <label htmlFor="q" className="sr-only">
          Question
        </label>
        <textarea
          id="q"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              submit(input);
            }
          }}
          placeholder="Ask about the Aurora Analytics docs…  (Enter to send, Shift+Enter for newline)"
          rows={2}
        />
        <button type="submit" disabled={busy || input.trim() === ""}>
          Ask
        </button>
      </form>
    </div>
  );
}
