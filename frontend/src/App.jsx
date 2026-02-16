import { useEffect, useState } from "react";

const emptyState = {
  input_a: null,
  input_b: null,
  output_csv: null,
  rows_input_a: 0,
  rows_input_b: 0,
  rows_output: 0,
  generated_at: null,
  total_valid_visits: 0,
  total_walk_ins: 0,
  top_members: []
};

const formatGeneratedAt = (value) => {
  if (!value) return "Not available";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return new Intl.DateTimeFormat("en-US", {
    dateStyle: "medium",
    timeStyle: "short"
  }).format(date);
};

const SummaryCard = ({ data }) => (
  <div className="order-1 rounded-2xl border border-white/30 bg-[#0b0f14] p-5 shadow-[0_16px_40px_rgba(0,0,0,0.28)] md:order-none">
    <p className="text-xs uppercase tracking-[0.2em] text-[#b3b3b3]">Summary</p>
    <div className="mt-3 space-y-3 text-sm text-[#e5e5e5]">
      <div className="flex items-center justify-between">
        <div className="font-medium text-[#e5e5e5]">Total valid visits</div>
        <div className="text-2xl font-semibold text-[#e5e5e5]">{data.total_valid_visits ?? 0}</div>
      </div>
      <div className="flex items-center justify-between">
        <div className="font-medium text-[#e5e5e5]">Total walk-ins</div>
        <div className="text-lg font-semibold text-[#e5e5e5]">{data.total_walk_ins ?? 0}</div>
      </div>
      <div>
        <div className="font-medium text-[#e5e5e5]">Generated at</div>
        <div className="text-xs text-[#cfcfcf] break-words">{formatGeneratedAt(data.generated_at)}</div>
      </div>
    </div>
  </div>
);

const TopMembersCard = ({ data }) => (
  <div className="order-2 rounded-2xl border border-white/30 bg-[#0b0f14] p-5 shadow-[0_16px_40px_rgba(0,0,0,0.28)] md:order-none">
    <p className="text-xs uppercase tracking-[0.2em] text-[#b3b3b3]">Top 5 members</p>
    <div className="mt-3 space-y-2 text-xs text-[#e5e5e5]">
      <div className="flex items-center justify-between px-3 text-[10px] uppercase tracking-[0.2em] text-[#9ca3af]">
        <span>Member Id</span>
        <span>Visits</span>
      </div>
      {data.top_members?.length ? (
        <ul className="space-y-2">
          {data.top_members.map((item) => (
            <li
              key={item.member_id}
              className="flex items-center gap-2 rounded-xl border border-white/10 bg-[#1f1f1f] px-3 py-2"
            >
              <span className="min-w-0 flex-1 truncate font-medium text-[#e5e5e5]">{item.member_id}</span>
              <span className="shrink-0 text-[#cfcfcf]">{item.visit_count}</span>
            </li>
          ))}
        </ul>
      ) : (
        <div className="text-xs text-[#cfcfcf]">No visits yet.</div>
      )}
    </div>
  </div>
);

export default function App() {
  const [data, setData] = useState(emptyState);
  const [error, setError] = useState(null);
  const [runError, setRunError] = useState(null);
  const [isRunning, setIsRunning] = useState(false);
  const [copyState, setCopyState] = useState("Copy");
  const fetchSummary = () => {
    setError(null);
    return fetch("/api/result")
      .then((res) => {
        if (!res.ok) {
          throw new Error("Run the processor either here or in the CLI to generate both CSV and summary data for the dashboard.");
        }
        return res.json();
      })
      .then((json) => setData(json))
      .catch((err) => setError(err.message));
  };

  useEffect(() => {
    fetchSummary();
  }, []);

  const handleRun = async () => {
    setIsRunning(true);
    setRunError(null);
    setError(null);
    try {
      const res = await fetch("/api/run", { method: "POST" });
      if (!res.ok) {
        let message = "Failed to run the processor.";
        try {
          const payload = await res.json();
          message = payload?.detail || message;
        } catch {
          // Keep default message when response is not JSON.
        }
        throw new Error(message);
      }
      await fetchSummary();
    } catch (err) {
      setRunError(err.message);
    } finally {
      setIsRunning(false);
    }
  };

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText("python3 backend/processor.py");
      setCopyState("Copied");
      window.setTimeout(() => setCopyState("Copy"), 1500);
    } catch {
      setCopyState("Failed");
      window.setTimeout(() => setCopyState("Copy"), 1500);
    }
  };

  return (
    <main className="min-h-screen bg-[#1f1f1f] px-6 py-12 text-[#e5e5e5]">
      <section className="mx-auto w-full max-w-5xl">
        <header className="mb-8">
          <p className="text-xs uppercase tracking-[0.4em] text-[#b3b3b3]">
            Cineville Backend Technical Challenge
          </p>
          <h1 className="mt-4 text-3xl font-semibold text-[#e5e5e5] md:text-4xl">
            Member Visits Overview
          </h1>
          <p className="mt-3 text-sm text-[#cfcfcf] md:text-base">
            The dashboard reflects the latest CLI run and summary generation. 
          </p>
        </header>

        {error ? (
          <div className="rounded-2xl border border-white/30 bg-[#262626] p-4 text-sm text-[#e5e5e5]">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>{error}</div>
              <button
                type="button"
                onClick={handleRun}
                disabled={isRunning}
                className="ml-auto inline-flex items-center justify-center rounded-lg border border-white/20 bg-[#1f1f1f] px-4 py-2 text-xs font-semibold tracking-[0.2em] text-[#e5e5e5] transition hover:bg-[#2a2a2a] disabled:cursor-not-allowed disabled:opacity-60"
              >
                {isRunning ? "Generating..." : "Generate summary"}
              </button>
            </div>
            {runError ? <div className="mt-2 text-xs text-[#d6d6d6]">{runError}</div> : null}
          </div>
        ) : (
          <div className="grid gap-4 md:grid-cols-2">
            <SummaryCard data={data} />
            <TopMembersCard data={data} />
          </div>
        )}

        <footer className="mt-8">
          <div className="w-full rounded-2xl border border-white/30 bg-[#0b0f14] p-4 shadow-[0_16px_40px_rgba(0,0,0,0.28)]">
            <div className="flex items-center justify-between">
              <span className="text-xs uppercase tracking-[0.2em] text-[#b3b3b3]">Terminal</span>
              <button
                type="button"
                onClick={handleCopy}
                className="inline-flex h-8 w-8 items-center justify-center rounded-md  text-[#9ca3af] transition hover:text-[#e5e5e5]"
                aria-label="Copy CLI command"
                title={copyState}
              >
                <svg
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="1.6"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <rect x="9" y="9" width="13" height="13" rx="2" />
                  <path d="M5 15V5a2 2 0 0 1 2-2h10" />
                </svg>
              </button>
            </div>
            <div className="mt-3 rounded-xl  bg-[#2a1a2c] px-4 py-3 font-mono text-sm text-[#e0e0e0]">
              <span className="text-[#f472b6]">python3</span>{" "}
              <span className="text-[#7dd3fc]">backend/processor.py</span>
            </div>
          </div>
          <div className="mt-3 text-right text-xs text-[#9ca3af]">Built by <span className="text-[#b90fe0]">Alex Botwinick</span></div>
        </footer>
      </section>
    </main>
  );
}
