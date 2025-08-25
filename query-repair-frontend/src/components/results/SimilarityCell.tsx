import { Box, Chip, Tooltip, Typography } from "@mui/material";
import { parsePredicatesWithRhs, parseVectorNums } from "../../utils/query";

type SimPart = { column: string; from: number | null; to: number | null; delta: number; sign: number };

const EPS = 1e-9;
const nearlyEqual = (a: number, b: number) => Math.abs(a - b) <= EPS;

function computeSimilarityBreakdown(sql: string, vectorText: string): { total: number; parts: SimPart[] } {
  const preds = parsePredicatesWithRhs(sql);
  const vec = parseVectorNums(vectorText);
  const parts: SimPart[] = [];
for (let i = 0; i < Math.min(preds.length, vec.length); i++) {
  const from = preds[i].rhs;
  const to = vec[i];

  let delta = 0;
  let sign = 0;

  if (from != null && Number.isFinite(to)) {
    if (!nearlyEqual(to, from)) {
      const diff = to - from;
      delta = Math.abs(diff);
      sign = diff;
    }
  }

  parts.push({ column: preds[i].column, from, to, delta, sign });
}
  const total = parts.reduce((s, p) => s + p.delta, 0);
  return { total, parts };
}

function SimilarityBar({ value, max }: { value: number; max: number }) {
  const pct = Math.max(0, Math.min(1, value / Math.max(1, max)));
  return (
    <Box>
      <Box sx={{ position: "relative", width: 180, height: 10, borderRadius: 5, bgcolor: "grey.300" }}>
        <Box
          sx={{
            position: "absolute",
            left: `${pct * 100}%`,
            top: "50%",
            width: 12,
            height: 12,
            borderRadius: "50%",
            bgcolor: (theme) => theme.palette.primary.main,
            transform: "translate(-50%, -50%)",
          }}
        />
      </Box>
      <Box sx={{ display: "flex", justifyContent: "space-between", mt: 0.5 }}>
        <Typography variant="caption" color="text.secondary">Closer</Typography>
        <Typography variant="caption" color="text.secondary">{Math.max(1, max)}+</Typography>
      </Box>
    </Box>
  );
}

export function SimilarityCell({
  similarityValue, vectorText, sql, max,
}: {
  similarityValue: any; vectorText: string; sql: string; max: number;
}) {
  const numeric = Number(similarityValue);
  const { total, parts } = computeSimilarityBreakdown(sql, vectorText);
  const value = Number.isFinite(numeric) ? numeric : total;

  return (
    <Box sx={{ display: "flex", flexDirection: "column", gap: 1 }}>
      <Box display="flex" alignItems="center" gap={1}>
        <Typography variant="body2" sx={{ fontFamily: "monospace" }}>{value}</Typography>
        <Chip size="small" label="lower is closer" variant="outlined" />
      </Box>
      <SimilarityBar value={value} max={Math.max(1, max)} />
      <Box sx={{ display: "flex", flexWrap: "wrap", gap: 0.5 }}>
        {parts.map((p, i) => {
          const label = p.delta === 0 ? `${p.column} 0` : `${p.column} ${p.sign > 0 ? "+" : ""}${p.sign}`;
          const color = p.delta === 0 ? "default" : "primary";
          return (
            <Tooltip key={i} title={`${p.column}: ${p.from ?? "?"} → ${p.to ?? "?"} (Δ=${p.delta})`}>
              <Chip size="small" label={label} color={color as any} variant="outlined" />
            </Tooltip>
          );
        })}
      </Box>
    </Box>
  );
}

// helper for page to compute per-table max
export function getMaxSimilarity(rows: { row: Record<string, any> }[], sql: string): number {
  const values = rows.map((r) => {
    const sim = Number(r.row?.["Similarity"]);
    if (Number.isFinite(sim)) return sim;
    const cond = String(r.row?.["conditions"] ?? r.row?.["Conditions"] ?? "");
    const { total } = computeSimilarityBreakdown(sql, cond);
    return total;
  });
  return Math.max(1, ...values.filter((v) => Number.isFinite(v)));
}
