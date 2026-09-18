import { useEffect, useState } from "react"; import { api } from "../api/client";
export function Backtest() { const [status, setStatus] = useState("Loading"); useEffect(() => { api.backtest().then(x => setStatus(x.message)); }, []); return <><h1>APIx and DGCA backtest</h1><p>{status}</p></>; }
