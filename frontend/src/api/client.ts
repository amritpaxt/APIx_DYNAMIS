const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api/v1";
export type IndexPoint = { date: string; value: number; spread_sub_index: number | null; confidence_score: number; coverage_pct: number; chain_break: boolean };
export type Route = { id: number; origin: string; destination: string; dgca_traffic_weight: number };
async function get<T>(path: string): Promise<T> { const r = await fetch(`${BASE_URL}${path}`); if (!r.ok) throw new Error(await r.text()); return r.json() as Promise<T>; }
export const api = { index: () => get<IndexPoint[]>("/index?freq=daily"), routes: () => get<Route[]>("/routes"), heatmap: () => get<{date:string; cells: {route:string; window:number; fare:number}[]}>("/heatmap"), elasticity: (id:number) => get<{route:string; points:{advance_window:number; average_fare:number}[]}>(`/elasticity/${id}`), backtest: () => get<{status:string; message:string}>("/backtest/summary") };
