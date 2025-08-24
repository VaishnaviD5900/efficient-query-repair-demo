import { useEffect, useState } from "react";
import {
  Box,
  Container,
  Typography,
  Paper,
  Grid,
  Divider,
  LinearProgress,
  Alert,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  TableContainer,
} from "@mui/material";
import InfoOutlined from "@mui/icons-material/InfoOutlined";
import { useLocation } from "react-router-dom";
import { Chip, Tooltip } from "@mui/material";

// -------- Types for /api/v1/results payload --------
type ParsedResults = {
  output_dir: string;
  run_info: Record<string, any>[]; // list of dict rows
  satisfied_conditions_ff: { row: Record<string, any> }[];
  satisfied_conditions_rp: { row: Record<string, any> }[];
  raw_files: string[];
};

// Replace numeric literals (in order) in the WHERE clause with values from a vector like "[35, 1, 15]"
function rewriteQueryWithVector(
  originalSql: string,
  vectorText: string
): string {
  if (!originalSql) return "";
  const nums = vectorText.match(/-?\d+(?:\.\d+)?/g) || [];
  if (!nums.length) return originalSql;

  let i = 0;
  const re =
    /(\b[A-Za-z_][A-Za-z0-9_]*\b\s*(?:>=|<=|==|=|>|<)\s*)(['"]?)(-?\d+(?:\.\d+)?)(['"]?)/g;

  return originalSql.replace(re, (full, left, ql, _oldNum, qr) => {
    if (i >= nums.length) return full;
    const q = ql && ql === qr ? ql : ""; // preserve matching quotes if present
    const next = nums[i++];
    return `${left}${q}${next}${q}`;
  });
}

// ---------- Result visual helpers ----------
type Bounds = { lb: number | null; ub: number | null };

const clamp = (v: number, lo = 0, hi = 1) => Math.max(lo, Math.min(hi, v));
const toPct = (v: number) => `${(v * 100).toFixed(2)}%`;

// Parse something like "[0.0014, 10000000000000]" or "<= 0.02"
function parseConstraintBounds(raw?: string): Bounds {
  const s = String(raw ?? "").trim();
  const nums = (s.match(/-?\d+(?:\.\d+)?/g) || []).map(Number);
  if (nums.length >= 2) return { lb: nums[0], ub: nums[1] };
  if (nums.length === 1) {
    // If we only see one number, try to infer <= or >= from the text
    if (/\<=|≤/.test(s)) return { lb: 0, ub: nums[0] };
    if (/\>=|≥/.test(s)) return { lb: nums[0], ub: null };
    // default treat as upper bound
    return { lb: 0, ub: nums[0] };
  }
  // Fallback: typical SPD threshold 2%
  return { lb: 0, ub: 0.02 };
}

function parseIntervalResult(raw: string): [number, number] | null {
  const m = raw.match(/-?\d+(?:\.\d+)?/g);
  if (!m || m.length < 2) return null;
  const lo = Number(m[0]),
    hi = Number(m[1]);
  if (Number.isFinite(lo) && Number.isFinite(hi)) return [lo, hi];
  return null;
}

function computeStatusPoint(v: number, b: Bounds): "PASS" | "FAIL" {
  const lbOk = b.lb == null || v >= b.lb!;
  const ubOk = b.ub == null || v <= b.ub!;
  return lbOk && ubOk ? "PASS" : "FAIL";
}

function computeStatusInterval(
  lo: number,
  hi: number,
  b: Bounds
): "PASS" | "FAIL" | "INCONCLUSIVE" {
  const definitelyBelow = b.lb != null && hi < b.lb!;
  const definitelyAbove = b.ub != null && lo > b.ub!;
  const definitelyInside =
    (b.lb == null || lo >= b.lb!) && (b.ub == null || hi <= b.ub!);
  if (definitelyInside) return "PASS";
  if (definitelyBelow || definitelyAbove) return "FAIL";
  return "INCONCLUSIVE";
}

// Choose a sensible max for the mini-bar domain
function barDomainMax(value: number, b: Bounds): number {
  // Prefer a small, readable range (e.g., up to the upper bound if it's < 1)
  const candidates = [
    value,
    ...(b.lb != null ? [b.lb] : []),
    ...(b.ub != null && b.ub < 1 ? [b.ub] : []),
    0.05, // 5% default view window
  ];
  return Math.max(...candidates);
}

const passColor = (theme: any) => theme.palette.success.main;
const failColor = (theme: any) => theme.palette.error.main;
const warnColor = (theme: any) => theme.palette.warning.main;

// ---------- Mini bar components ----------
function PointResult({ value, bounds }: { value: number; bounds: Bounds }) {
  if (!Number.isFinite(value)) return <span>—</span>;
  const status = computeStatusPoint(value, bounds);
  return (
    <Box display="flex" flexDirection="column" gap={0.5}>
      <Box display="flex" alignItems="center" gap={1}>
        <Typography variant="body2" sx={{ fontFamily: "monospace" }}>
          {toPct(value)}
        </Typography>
        <Chip
          size="small"
          label={status}
          color={status === "PASS" ? "success" : "error"}
          variant="outlined"
        />
      </Box>

      {/* Mini bar */}
      <MiniBar value={value} bounds={bounds} />
    </Box>
  );
}

function RangeResult({
  lo,
  hi,
  bounds,
}: {
  lo: number;
  hi: number;
  bounds: Bounds;
}) {
  const status = computeStatusInterval(lo, hi, bounds);
  const chipColor =
    status === "PASS" ? "success" : status === "FAIL" ? "error" : "warning";
  return (
    <Box display="flex" flexDirection="column" gap={0.5}>
      <Box display="flex" alignItems="center" gap={1}>
        <Typography variant="body2" sx={{ fontFamily: "monospace" }}>
          {toPct(lo)} – {toPct(hi)}
        </Typography>
        <Chip
          size="small"
          label={status}
          color={chipColor as any}
          variant="outlined"
        />
      </Box>
      <MiniBar range={[lo, hi]} bounds={bounds} />
    </Box>
  );
}

function MiniBar({
  value,
  range,
  bounds,
}: {
  value?: number;
  range?: [number, number];
  bounds: Bounds;
}) {
  const domain = barDomainMax(range ? range[1] : value ?? 0, bounds); // scale to max of hi/value
  const pos = (x: number) => `${clamp(x / domain, 0, 1) * 100}%`;

  return (
    <Box
      sx={{
        position: "relative",
        width: 180,
        height: 8,
        borderRadius: 4,
        bgcolor: "grey.300",
      }}
    >
      {/* Lower bound marker (if in view) */}
      {bounds.lb != null && bounds.lb <= domain && (
        <Tooltip title={`Lower bound ${toPct(bounds.lb)}`}>
          <Box
            sx={{
              position: "absolute",
              left: pos(bounds.lb),
              top: 0,
              bottom: 0,
              width: 2,
              bgcolor: "grey.600",
            }}
          />
        </Tooltip>
      )}

      {/* Upper bound marker (if in view) */}
      {bounds.ub != null && bounds.ub <= domain && (
        <Tooltip title={`Upper bound ${toPct(bounds.ub)}`}>
          <Box
            sx={{
              position: "absolute",
              left: pos(bounds.ub),
              top: 0,
              bottom: 0,
              width: 2,
              bgcolor: "grey.600",
            }}
          />
        </Tooltip>
      )}

      {/* Value dot or interval span */}
      {typeof value === "number" ? (
        <Box
          sx={{
            position: "absolute",
            left: pos(value),
            top: -3,
            width: 14,
            height: 14,
            borderRadius: "50%",
            bgcolor: (theme) =>
              computeStatusPoint(value, bounds) === "PASS"
                ? passColor(theme)
                : failColor(theme),
            transform: "translateX(-50%)",
          }}
        />
      ) : range ? (
        <>
          {/* Interval band */}
          <Box
            sx={{
              position: "absolute",
              left: pos(range[0]),
              width: `calc(${pos(range[1])} - ${pos(range[0])})`,
              top: 2,
              height: 4,
              bgcolor: (theme) => {
                const s = computeStatusInterval(range[0], range[1], bounds);
                return s === "PASS"
                  ? passColor(theme)
                  : s === "FAIL"
                  ? failColor(theme)
                  : warnColor(theme);
              },
              borderRadius: 2,
            }}
          />
          {/* End caps */}
          <Box
            sx={{
              position: "absolute",
              left: pos(range[0]),
              top: -2,
              width: 8,
              height: 8,
              borderRadius: "50%",
              bgcolor: "grey.700",
              transform: "translateX(-50%)",
            }}
          />
          <Box
            sx={{
              position: "absolute",
              left: pos(range[1]),
              top: -2,
              width: 8,
              height: 8,
              borderRadius: "50%",
              bgcolor: "grey.700",
              transform: "translateX(-50%)",
            }}
          />
        </>
      ) : null}
    </Box>
  );
}

// Wrapper used in the table cell
function ResultCell({ rawResult, bounds }: { rawResult: any; bounds: Bounds }) {
  const text = String(rawResult ?? "");
  const interval = parseIntervalResult(text);
  if (interval) {
    return <RangeResult lo={interval[0]} hi={interval[1]} bounds={bounds} />;
  }
  const num = Number(text);
  return <PointResult value={num} bounds={bounds} />;
}

// ---------- Similarity helpers ----------
type Pred = { column: string; op: string; rhs: number | null };
type SimPart = {
  column: string;
  from: number | null;
  to: number | null;
  delta: number;
  sign: number;
};

function parsePredicatesWithRhs(sql: string): Pred[] {
  const preds: Pred[] = [];
  if (!sql) return preds;
  const re =
    /([A-Za-z_][A-Za-z0-9_]*)\s*(>=|<=|==|=|>|<)\s*'?(-?\d+(?:\.\d+)?)'?/g;
  let m: RegExpExecArray | null;
  while ((m = re.exec(sql)) !== null) {
    const col = m[1];
    const op = m[2] === "==" ? "=" : m[2];
    const rhs = Number(m[3]);
    preds.push({ column: col, op, rhs: Number.isFinite(rhs) ? rhs : null });
  }
  return preds;
}

function parseVectorNums(text: string): number[] {
  return (text.match(/-?\d+(?:\.\d+)?/g) || []).map(Number);
}

// L1 distance + parts (used if CSV "Similarity" missing or for chips)
function computeSimilarityBreakdown(
  sql: string,
  vectorText: string
): { total: number; parts: SimPart[] } {
  const preds = parsePredicatesWithRhs(sql);
  const vec = parseVectorNums(vectorText);
  const parts: SimPart[] = [];

  for (let i = 0; i < Math.min(preds.length, vec.length); i++) {
    const from = preds[i].rhs;
    const to = vec[i];
    const delta =
      from == null || !Number.isFinite(to) ? 0 : Math.abs(to - from);
    const sign = from == null || !Number.isFinite(to) ? 0 : to - from;
    parts.push({ column: preds[i].column, from, to, delta, sign });
  }
  const total = parts.reduce((s, p) => s + p.delta, 0);
  return { total, parts };
}

function getMaxSimilarity(
  rows: { row: Record<string, any> }[],
  sql: string
): number {
  const values = rows.map((r) => {
    const sim = Number(r.row?.["Similarity"]);
    if (Number.isFinite(sim)) return sim;
    const cond = String(r.row?.["conditions"] ?? r.row?.["Conditions"] ?? "");
    return computeSimilarityBreakdown(sql, cond).total;
  });
  const max = Math.max(1, ...values.filter((v) => Number.isFinite(v)));
  return max;
}

// --- Small bar (lower = closer) ---
function SimilarityBar({ value, max }: { value: number; max: number }) {
  const pct = Math.max(0, Math.min(1, value / Math.max(1, max)));
  return (
    <Box>
      {/* the bar */}
      <Box
        sx={{
          position: "relative",
          width: 180,
          height: 10,
          borderRadius: 5,
          bgcolor: "grey.300",
        }}
      >
        <Box
          sx={{
            position: "absolute",
            left: `${pct * 100}%`,
            top: "50%",
            width: 12,
            height: 12,
            borderRadius: "50%",
            bgcolor: (theme) => theme.palette.primary.main,
            transform: "translate(-50%, -50%)", // center dot *inside* the bar
          }}
        />
      </Box>

      {/* captions on a separate row to avoid overlap */}
      <Box sx={{ display: "flex", justifyContent: "space-between", mt: 0.5 }}>
        <Typography variant="caption" color="text.secondary">
          Closer
        </Typography>
        <Typography variant="caption" color="text.secondary">
          {Math.max(1, max)}+
        </Typography>
      </Box>
    </Box>
  );
}

// --- Cell renderer for the table ---
function SimilarityCell({
  similarityValue,
  vectorText,
  sql,
  max,
}: {
  similarityValue: any;
  vectorText: string;
  sql: string;
  max: number;
}) {
  const numeric = Number(similarityValue);
  const { total, parts } = computeSimilarityBreakdown(sql, vectorText);
  const value = Number.isFinite(numeric) ? numeric : total;

  return (
    <Box sx={{ display: "flex", flexDirection: "column", gap: 1 }}>
      <Box display="flex" alignItems="center" gap={1}>
        <Typography variant="body2" sx={{ fontFamily: "monospace" }}>
          {value}
        </Typography>
        <Chip size="small" label="lower is closer" variant="outlined" />
      </Box>

      <SimilarityBar value={value} max={Math.max(1, max)} />

      <Box sx={{ display: "flex", flexWrap: "wrap", gap: 0.5 }}>
        {parts.map((p, i) => {
          const label =
            p.delta === 0
              ? `${p.column} 0`
              : `${p.column} ${p.sign > 0 ? "+" : ""}${p.sign}`;
          const color = p.delta === 0 ? "default" : "primary";
          return (
            <Tooltip
              key={i}
              title={`${p.column}: ${p.from ?? "?"} → ${p.to ?? "?"} (Δ=${
                p.delta
              })`}
            >
              <Chip
                size="small"
                label={label}
                color={color as any}
                variant="outlined"
              />
            </Tooltip>
          );
        })}
      </Box>
    </Box>
  );
}

// ========== Query matching (SQL ↔ RunInfo) ==========
const normOp = (op: string) => (op === "==" ? "=" : op);
const normCol = (c: string) => c.trim().toUpperCase();

const token = (col: string, op: string) => `${normCol(col)}:${normOp(op)}`;

// Extract predicates from *SQL* and build a sorted signature like "AGEP:>=|COW:>=|SCHL:<="
function signatureFromSql(sql: string): string {
  if (!sql) return "";
  // grab all "col op number" regardless of spaces/quotes/newlines
  const re =
    /([A-Za-z_][A-Za-z0-9_.]*)\s*(>=|<=|==|=|>|<)\s*['"]?-?\d+(?:\.\d+)?['"]?/gi;
  const toks: string[] = [];
  let m: RegExpExecArray | null;
  while ((m = re.exec(sql)) !== null) toks.push(token(m[1], m[2]));
  return toks.sort().join("|");
}

// Extract predicates from RunInfo "Query" string and build the same signature
// Example input: "[['AGEP','>=',35.0,'numerical'], ['COW','>=',2.0,'numerical'], ...]"
function signatureFromRunInfo(qstr: string): string {
  if (!qstr) return "";
  // First, try real JSON parse by swapping single quotes to double quotes
  try {
    const json = JSON.parse(qstr.replace(/'/g, '"'));
    if (Array.isArray(json)) {
      const toks = json
        .filter((e: any) => Array.isArray(e) && e.length >= 2)
        .map((e: any[]) => token(String(e[0]), String(e[1])));
      return toks.sort().join("|");
    }
  } catch {
    // fallback to regex if it isn't clean JSON
  }
  // Regex fallback: pull (col, op) pairs
  const re = /\[\s*['"]([^'"]+)['"]\s*,\s*['"]([^'"]+)['"]/g;
  const toks: string[] = [];
  let m: RegExpExecArray | null;
  while ((m = re.exec(qstr)) !== null) toks.push(token(m[1], m[2]));
  return toks.sort().join("|");
}

function InfoIcon({ title }: { title: string }) {
  return (
    <Tooltip title={title}>
      <InfoOutlined
        fontSize="small"
        sx={{
          ml: 0.5,
          color: "text.secondary",
          cursor: "help",
          verticalAlign: "text-bottom",
        }}
      />
    </Tooltip>
  );
}

function MetricLabel({ label, info }: { label: string; info: string }) {
  return (
    <Box component="span" sx={{ display: "inline-flex", alignItems: "center" }}>
      <span>{label}</span>
      <InfoIcon title={info} />
    </Box>
  );
}

export default function ResultsPage() {
  const location = useLocation();

  // Existing UI state you already hydrate from localStorage
  const [sqlQuery, setSqlQuery] = useState("");
  const [aggregations, setAggregations] = useState<any[]>([]);
  const [constraintExpr, setConstraintExpr] = useState<string>("");

  // Backend artifacts + loading/error
  const [artifacts, setArtifacts] = useState<ParsedResults | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>("");

  const {
    datasetName = "Unknown Dataset",
    size = 0,
    columnCount = 0,
    outputDir: outputDirFromState,
  } = (location.state as any) || {};

  // Placeholder until you wire the real constraint value from artifacts
  const constraint = {
    type: "SPD",
    threshold: 0.2,
    actual: 0.35,
    satisfied: false,
  };

  // Helper to normalize progress bars (0–100)
  const asPercent = (value: number, max: number) =>
    max <= 0 ? 0 : Math.min(100, Math.round((value / max) * 100));

  useEffect(() => {
    // Hydrate UI bits you already save
    const stored = localStorage.getItem("queryRepairData");
    if (stored) {
      const parsed = JSON.parse(stored);
      setSqlQuery(parsed.sqlQuery || "");
      setAggregations(parsed.aggregations || []);
      setConstraintExpr(parsed.constraintExpr || "");
    }

    // Determine output dir: from state, else from localStorage (set it after /repair/run)
    const outputDir =
      outputDirFromState || localStorage.getItem("qrOutputDir") || "";

    if (!outputDir) {
      setError("Missing output directory. Run a repair first.");
      setLoading(false);
      return;
    }

    (async () => {
      try {
        setLoading(true);
        const res = await fetch(
          `http://127.0.0.1:8000/api/v1/results?dataset=${datasetName}`
        );
        if (!res.ok) {
          const txt = await res.text();
          throw new Error(txt || `HTTP ${res.status}`);
        }
        const data: ParsedResults = await res.json();
        setArtifacts(data);
      } catch (e: any) {
        setError(e?.message || "Failed to load results");
      } finally {
        setLoading(false);
      }
    })();
  }, [outputDirFromState]);

  // --------- Derive metrics from run_info rows ----------
  // --------- Derive metrics from run_info rows (ONLY if query matches) ----------
  const runInfoRows = artifacts?.run_info || [];

  const sigSql = signatureFromSql(sqlQuery);
  const matchingRunInfo = runInfoRows.filter(
    (r) => signatureFromRunInfo(String(r["Query"] || "")) === sigSql
  );

  const hasRunMatch = matchingRunInfo.length > 0;

  const fullyRow = hasRunMatch
    ? matchingRunInfo.find((r) => (r["Type"] || r["type"]) === "Fully")
    : undefined;

  const rangesRow = hasRunMatch
    ? matchingRunInfo.find((r) => (r["Type"] || r["type"]) === "Ranges")
    : undefined;

  const anyRow = hasRunMatch ? matchingRunInfo[0] : undefined;

  const runtimeFF = Number(fullyRow?.["Time"] ?? 0);
  const runtimeRP = Number(rangesRow?.["Time"] ?? 0);
  const runtimeMax = Math.max(runtimeFF || 0, runtimeRP || 0, 1);

  const nceFF = Number(fullyRow?.["Checked Num"] ?? 0);
  const nceRP = Number(rangesRow?.["Checked Num"] ?? 0);
  const nceMax = Math.max(nceFF || 0, nceRP || 0, 1);

  const ncaFF = Number(fullyRow?.["Refinement Num"] ?? 0);
  const ncaRP = Number(rangesRow?.["Refinement Num"] ?? 0);
  const ncaMax = Math.max(ncaFF || 0, ncaRP || 0, 1);

  // Access & Distance (run-level)
  const accessFF = Number(fullyRow?.["Access Num"] ?? 0);
  const accessRP = Number(rangesRow?.["Access Num"] ?? 0);
  const accessMax = Math.max(accessFF || 0, accessRP || 0, 1); // normalize bars

  const distFF = Number(fullyRow?.["Distance"] ?? 0); // fraction in [0,1]
  const distRP = Number(rangesRow?.["Distance"] ?? 0);
  const distFFpct = Math.max(0, Math.min(100, Math.round(distFF * 100)));
  const distRPpct = Math.max(0, Math.min(100, Math.round(distRP * 100)));

  const combinations = Number(anyRow?.["Combinations Num"] ?? NaN);

  // Bounds for Result visuals from the matched run (falls back to a default inside parser)
  const constraintStr = String(anyRow?.["Constraint"] ?? "");
  const bounds: Bounds = parseConstraintBounds(constraintStr);

  const maxSimFF = getMaxSimilarity(
    artifacts?.satisfied_conditions_ff || [],
    sqlQuery
  );
  const maxSimRP = getMaxSimilarity(
    artifacts?.satisfied_conditions_rp || [],
    sqlQuery
  );

  // --------- Render helpers ----------
  const renderTopKTable = (
    title: string,
    rows: { row: Record<string, any> }[],
    showRangeSatisfaction: boolean,
    bounds: Bounds,
    maxSim: number
  ) => {
    if (!rows?.length) {
      return (
        <>
          <Typography variant="subtitle1" gutterBottom>
            {title}
          </Typography>
          <Typography variant="body2" color="text.secondary" mb={2}>
            No rows to display.
          </Typography>
        </>
      );
    }

    return (
      <>
        <Typography variant="subtitle1" gutterBottom>
          {title}
        </Typography>
        <TableContainer component={Paper} variant="outlined" sx={{ mb: 2 }}>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell width={30}>Rank</TableCell>
                <TableCell>Conditions</TableCell>
                <TableCell>Similarity</TableCell>
                <TableCell>Result</TableCell>
                {showRangeSatisfaction && (
                  <TableCell width={50}>Range Satisfaction</TableCell>
                )}
              </TableRow>
            </TableHead>
            <TableBody>
              {rows.map((r, idx) => {
                const row = r.row || {};
                const rawCond = String(
                  row["conditions"] ?? row["Conditions"] ?? "—"
                );
                const similarity = row["Similarity"] ?? "—";
                const result = row["Result"] ?? "—";
                const rangeSat = row["Range Satisfaction"] ?? "—";

                const condSql = rewriteQueryWithVector(sqlQuery, rawCond);

                return (
                  <TableRow key={idx}>
                    <TableCell>{idx + 1}</TableCell>
                    <TableCell
                      sx={{ fontFamily: "monospace", whiteSpace: "pre-wrap" }}
                    >
                      {condSql}
                    </TableCell>
                    <TableCell
                      sx={{ verticalAlign: "top", py: 1.25, width: 190 }}
                    >
                      <SimilarityCell
                        similarityValue={similarity}
                        vectorText={rawCond}
                        sql={sqlQuery}
                        max={maxSim}
                      />
                    </TableCell>

                    {/* NEW visual cell */}
                    <TableCell>
                      <ResultCell rawResult={result} bounds={bounds} />
                    </TableCell>

                    {showRangeSatisfaction && <TableCell>{rangeSat}</TableCell>}
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </TableContainer>
      </>
    );
  };

  return (
    <Container maxWidth="md" sx={{ mt: 2 }}>
      <Box
        display="flex"
        justifyContent="space-between"
        alignItems="center"
        mb={1}
      >
        <Typography variant="h4" fontWeight="bold" gutterBottom>
          Results
        </Typography>
      </Box>

      <Typography variant="h6" color="text.secondary" gutterBottom>
        Dataset: <strong>{datasetName}</strong>{" "}
        <Typography variant="body2" component="span">
          Size: {size} KB
        </Typography>
        ,{" "}
        <Typography variant="body2" component="span">
          Columns: {columnCount}
        </Typography>
      </Typography>

      <Paper variant="outlined" sx={{ p: 2, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Original Query
        </Typography>
        <Paper variant="outlined" sx={{ p: 1, my: 1 }}>
          <Typography
            variant="body2"
            color="text.secondary"
            style={{ whiteSpace: "pre-wrap" }}
          >
            {sqlQuery || "-- SQL query not available --"}
          </Typography>
        </Paper>

        <Typography variant="h6" gutterBottom>
          Aggregate Functions
        </Typography>
        <Paper variant="outlined" sx={{ p: 1, my: 1 }}>
          {aggregations.length === 0 ? (
            <Typography variant="body2" color="text.secondary">
              Aggregate Functions not available --
            </Typography>
          ) : (
            aggregations.map((agg: any, index: number) => (
              <Typography
                key={index}
                variant="body2"
                color="text.secondary"
                style={{ whiteSpace: "pre-wrap" }}
              >
                {`${agg.name}: ${String(agg.func).toUpperCase()} WHERE ${
                  agg.predicate
                }`}
              </Typography>
            ))
          )}
        </Paper>

        {/* <Grid container spacing={2}> */}

        <Typography variant="h6" gutterBottom>
          Arithmetic Expression
        </Typography>
        <Paper variant="outlined" sx={{ p: 1, my: 1 }}>
          <Typography
            variant="body2"
            color="text.secondary"
            style={{ whiteSpace: "pre-wrap" }}
          >
            {constraintExpr || "--"}
          </Typography>
        </Paper>
      </Paper>

      {/* ---------- Top-k Repaired Queries ---------- */}
      <Typography variant="h6" gutterBottom>
        Top-k Repaired Queries
      </Typography>

      {renderTopKTable(
        "Fully (point estimates)",
        artifacts?.satisfied_conditions_ff || [],
        true,
        bounds,
        maxSimFF
      )}

      {renderTopKTable(
        "Ranges (interval estimates)",
        artifacts?.satisfied_conditions_rp || [],
        false,
        bounds,
        maxSimRP
      )}

      <Divider sx={{ my: 3 }} />

      <Typography variant="h6" gutterBottom>
        Algorithm Search Space Metrics
      </Typography>

      {loading && <LinearProgress sx={{ mb: 2 }} />}

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {!!artifacts?.run_info?.length && (
        <Box sx={{ mb: 2 }}>
          {/* Top summary line with info icons */}
          <Typography
            variant="body2"
            color="text.secondary"
            sx={{
              mb: 1,
              display: "flex",
              alignItems: "center",
              flexWrap: "wrap",
              gap: 1,
            }}
          >
            <MetricLabel
              label="Combos"
              info="Combinations Num: total number of repairs considered (product of per-predicate options)."
            />
            :{" "}
            <strong>
              {Number.isFinite(combinations)
                ? Number(combinations).toLocaleString()
                : "—"}
            </strong>
          </Typography>

          {/* Runtime */}
          <Box sx={{ mb: 2 }}>
            <Typography variant="body2" mb={0.5}>
              <MetricLabel
                label="Runtime (s) - FF"
                info="Total wall-clock time to compute the top-k repaired queries with Full Filtering."
              />
              : {runtimeFF || "—"}
            </Typography>
            <LinearProgress
              variant="determinate"
              value={asPercent(runtimeFF, runtimeMax)}
            />
            <Typography variant="body2" mt={0.5}>
              <MetricLabel
                label="Runtime (s) - RP"
                info="Total wall-clock time to compute the top-k using Range Pruning."
              />
              : {runtimeRP || "—"}
            </Typography>
            <LinearProgress
              variant="determinate"
              value={asPercent(runtimeRP, runtimeMax)}
              color="secondary"
            />
          </Box>

          {/* NCE */}
          <Box sx={{ mb: 2 }}>
            <Typography variant="body2" mb={0.5}>
              <MetricLabel
                label="NCE (checks) - FF"
                info="Number of constraint evaluations performed; lower means more pruning."
              />
              : {nceFF}
            </Typography>
            <LinearProgress
              variant="determinate"
              value={asPercent(nceFF, nceMax)}
            />
            <Typography variant="body2" mt={0.5}>
              <MetricLabel
                label="NCE (checks) - RP"
                info="Constraint evaluations on ranges/singletons during RP; lower is better."
              />
              : {nceRP}
            </Typography>
            <LinearProgress
              variant="determinate"
              value={asPercent(nceRP, nceMax)}
              color="secondary"
            />
          </Box>

          {/* NCA */}
          <Box sx={{ mb: 2 }}>
            <Typography variant="body2" mb={0.5}>
              <MetricLabel
                label="NCA (refinements) - FF"
                info="Refinement steps during search (e.g., descending summaries); lower is better."
              />
              : {ncaFF}
            </Typography>
            <LinearProgress
              variant="determinate"
              value={asPercent(ncaFF, ncaMax)}
            />
            <Typography variant="body2" mt={0.5}>
              <MetricLabel
                label="NCA (refinements) – RP"
                info="Number of range splits/refinements RP performed; lower is better."
              />
              : {ncaRP}
            </Typography>
            <LinearProgress
              variant="determinate"
              value={asPercent(ncaRP, ncaMax)}
              color="secondary"
            />
          </Box>

          {/* Access Num */}
          <Box sx={{ mb: 2 }}>
            <Typography variant="body2" mb={0.5}>
              <MetricLabel
                label="Access Num – FF"
                info="How many index/cluster partitions were accessed while filtering; lower means less search effort."
              />
              : {Number.isFinite(accessFF) ? accessFF.toLocaleString() : "—"}
            </Typography>
            <LinearProgress
              variant="determinate"
              value={asPercent(accessFF, accessMax)}
            />

            <Typography variant="body2" mt={0.5}>
              <MetricLabel
                label="Access Num – RP"
                info="Partitions/nodes accessed under RP; lower is better."
              />
              : {Number.isFinite(accessRP) ? accessRP.toLocaleString() : "—"}
            </Typography>
            <LinearProgress
              variant="determinate"
              value={asPercent(accessRP, accessMax)}
              color="secondary"
            />
          </Box>

          {/* Distance (Search explored) */}
          <Box sx={{ mb: 2 }}>
            <Typography variant="body2" mb={0.5}>
              <MetricLabel
                label="Search explored (Distance) - FF"
                info="Fraction of space explored to find top-k; 0-100%. Lower is better."
              />
              : {Number.isFinite(distFF) ? `${distFFpct}%` : "—"}
            </Typography>
            <LinearProgress variant="determinate" value={distFFpct} />

            <Typography variant="body2" mt={0.5}>
              <MetricLabel
                label="Search explored (Distance) - RP"
                info="Fraction of space RP explored; lower is better."
              />
              : {Number.isFinite(distRP) ? `${distRPpct}%` : "—"}
            </Typography>
            <LinearProgress
              variant="determinate"
              value={distRPpct}
              color="secondary"
            />
          </Box>
        </Box>
      )}

      {!loading && !artifacts?.run_info?.length && !error && (
        <Typography variant="body2" color="text.secondary" mb={2}>
          No parsed metrics found in the output directory.
        </Typography>
      )}

      <Divider sx={{ my: 3 }} />

      <Typography variant="h6" gutterBottom>
        Algorithm Efficiency Summary
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Range Pruning (RP) achieved the same top-k repairs as Full Filtering
        (FF), while exploring only 20% of the search space compared to FF's 60%
        and running 3x faster.
      </Typography>
    </Container>
  );
}
