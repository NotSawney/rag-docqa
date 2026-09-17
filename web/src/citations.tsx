import { Fragment } from "react";

// Split an answer on `[n]` tokens and render each as a clickable chip that maps
// to citations[n-1]. Tokens out of range (defensive) render as plain text.
export function AnswerText({
  text,
  count,
  onCite,
}: {
  text: string;
  count: number;
  onCite: (n: number) => void;
}) {
  const parts = text.split(/(\[\d+\])/g);
  return (
    <p className="answer-text">
      {parts.map((part, i) => {
        const m = part.match(/^\[(\d+)\]$/);
        if (m) {
          const n = Number(m[1]);
          if (n >= 1 && n <= count) {
            return (
              <sup key={i}>
                <button
                  type="button"
                  className="cite-chip"
                  onClick={() => onCite(n)}
                  aria-label={`Jump to source ${n}`}
                >
                  {n}
                </button>
              </sup>
            );
          }
        }
        return <Fragment key={i}>{part}</Fragment>;
      })}
    </p>
  );
}
