export function ConfidenceBadge({ score, coverage, chainBreak }: { score: number; coverage: number; chainBreak: boolean }) {
  const label = chainBreak ? "Coverage break" : score >= 85 ? "High confidence" : "Limited confidence";
  return <span title={`${coverage.toFixed(0)}% basket coverage`} className={chainBreak ? "badge warning" : "badge"}>{label} {score.toFixed(0)}%</span>;
}
