import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { IndexPoint } from "../../api/client";
export function TrendChart({ data }: { data: IndexPoint[] }) { return <ResponsiveContainer width="100%" height={300}><LineChart data={data}><XAxis dataKey="date" hide/><YAxis domain={["auto", "auto"]}/><Tooltip/><Line type="monotone" dataKey="value" stroke="#0f766e" dot={false}/></LineChart></ResponsiveContainer>; }
