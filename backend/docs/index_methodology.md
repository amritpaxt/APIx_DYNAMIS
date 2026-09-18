# APIx Index Methodology

APIx is a daily chained Törnqvist index of eligible economy fares. The eligible fare is `base_fare + statutory_taxes`; OTA convenience fees are retained for audit but excluded. Cancelled, sold-out, imputed, and MAD-flagged records are visible in storage and excluded from the headline calculation.

For route `r`, the daily route price is the booking-window-weighted mean. Route weights are normalized DGCA traffic shares; booking-window weights are derived from observed APIx records. The chain step is:

`I_t = I_(t-1) * exp(sum_r w_r * ln(P_r,t / P_r,t-1))`

If coverage is below 60%, APIx carries the preceding valid level forward and sets `chain_break=true`. Confidence is `coverage_pct * (1 - outlier_rate)` and is returned with each index point.

This is a prototype methodology, not an official CPI series. The documented rule makes data limitations explicit instead of silently creating an index point.
