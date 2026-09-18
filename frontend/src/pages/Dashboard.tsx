import { useEffect, useState } from "react";
import { api, IndexPoint } from "../api/client";
import { ConfidenceBadge } from "../components/ConfidenceBadge";
import { TrendChart } from "../components/charts/TrendChart";
export function Dashboard() { const [data, setData] = useState<IndexPoint[]>([]); const [error, setError] = useState(""); useEffect(() => { api.index().then(setData).catch(() => setError("API unavailable. Start the FastAPI service to load the demo series.")); }, []); const latest = data.at(-1); return <><h1>APIx Airfare Price Index</h1><p>Daily chained Törnqvist index. Channel convenience fees are excluded; confidence is published with every point.</p>{error && <p className="error">{error}</p>}{latest && <p className="metric">{latest.value.toFixed(2)} <ConfidenceBadge score={latest.confidence_score} coverage={latest.coverage_pct} chainBreak={latest.chain_break}/></p>}<TrendChart data={data}/></>; }
