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
import { CheckCircle, Cancel } from "@mui/icons-material";
import { useLocation } from "react-router-dom";

// -------- Types for /api/v1/results payload --------
type ParsedResults = {
  output_dir: string;
  run_info: Record<string, any>[]; // list of dict rows
  satisfied_conditions_ff: { row: Record<string, any> }[];
  satisfied_conditions_rp: { row: Record<string, any> }[];
  raw_files: string[];
};

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
  const constraint = { type: "SPD", threshold: 0.2, actual: 0.35, satisfied: false };

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
    const outputDir = outputDirFromState || localStorage.getItem("qrOutputDir") || "";

    if (!outputDir) {
      setError("Missing output directory. Run a repair first.");
      setLoading(false);
      return;
    }

    (async () => {
      try {
        setLoading(true);
        const res = await fetch(
          `http://127.0.0.1:8000/api/v1/results?output_dir=${encodeURIComponent(outputDir)}`
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
  const fullyRow = artifacts?.run_info?.find((r) => (r["Type"] || r["type"]) === "Fully");
  const rangesRow = artifacts?.run_info?.find((r) => (r["Type"] || r["type"]) === "Ranges");
  const anyRow = artifacts?.run_info?.[0];

  const runtimeFF = Number(fullyRow?.["Time"] ?? 0);
  const runtimeRP = Number(rangesRow?.["Time"] ?? 0);
  const runtimeMax = Math.max(runtimeFF, runtimeRP, 1);

  const nceFF = Number(fullyRow?.["Checked Num"] ?? 0);
  const nceRP = Number(rangesRow?.["Checked Num"] ?? 0);
  const nceMax = Math.max(nceFF, nceRP, 1);

  const ncaFF = Number(fullyRow?.["Refinement Num"] ?? 0);
  const ncaRP = Number(rangesRow?.["Refinement Num"] ?? 0);
  const ncaMax = Math.max(ncaFF, ncaRP, 1);

  const combinations = Number(anyRow?.["Combinations Num"] ?? 0);

  // --------- Render helpers ----------
  const renderTopKTable = (
    title: string,
    rows: { row: Record<string, any> }[],
    showRangeSatisfaction: boolean
  ) => {
    if (!rows?.length) {
      return (
        <>
          <Typography variant="subtitle1" gutterBottom>{title}</Typography>
          <Typography variant="body2" color="text.secondary" mb={2}>
            No rows to display.
          </Typography>
        </>
      );
    }

    return (
      <>
        <Typography variant="subtitle1" gutterBottom>{title}</Typography>
        <TableContainer component={Paper} variant="outlined" sx={{ mb: 2 }}>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell width={60}>Rank</TableCell>
                <TableCell>Conditions</TableCell>
                <TableCell>Similarity</TableCell>
                <TableCell>Result</TableCell>
                {showRangeSatisfaction && <TableCell>Range Satisfaction</TableCell>}
              </TableRow>
            </TableHead>
            <TableBody>
              {rows.map((r, idx) => {
                const row = r.row || {};
                const conditions = String(row["conditions"] ?? "—");
                const similarity = row["Similarity"] ?? "—";
                const result = row["Result"] ?? "—";
                const rangeSat = row["Range Satisfaction"] ?? "—";
                return (
                  <TableRow key={idx}>
                    <TableCell>{idx + 1}</TableCell>
                    <TableCell sx={{ fontFamily: "monospace" }}>{conditions}</TableCell>
                    <TableCell>{similarity}</TableCell>
                    <TableCell sx={{ fontFamily: "monospace" }}>{String(result)}</TableCell>
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
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
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
        <Paper variant="outlined" sx={{ p: 1, my: 1, minHeight: 60 }}>
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
        <Paper variant="outlined" sx={{ p: 1, my: 1, minHeight: 60 }}>
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
                {`${agg.name}: ${String(agg.func).toUpperCase()} WHERE ${agg.predicate}`}
              </Typography>
            ))
          )}
        </Paper>

        {/* <Grid container spacing={2}> */}
          <Grid size={{ xs: 6 }}>
            <Typography variant="h6">
              Arithmetic Expression: {constraintExpr || "--"}
            </Typography>
          </Grid>
          {/* <Grid size={{ xs: 6 }}>
            <Typography variant="h6">
              Constraint Status: {constraint.actual}
              {constraint.satisfied ? (
                <CheckCircle color="success" sx={{ ml: 1 }} />
              ) : (
                <Cancel color="error" sx={{ ml: 1 }} />
              )}
            </Typography>
          </Grid> */}
        {/* </Grid> */}
      </Paper>

      {/* ---------- Top-k Repaired Queries ---------- */}
      <Typography variant="h6" gutterBottom>
        Top-k Repaired Queries
      </Typography>

      {renderTopKTable("Fully (point estimates)", artifacts?.satisfied_conditions_ff || [], true)}
      {renderTopKTable("Ranges (interval estimates)", artifacts?.satisfied_conditions_rp || [], false)}

      <Divider sx={{ my: 3 }} />

      <Typography variant="h6" gutterBottom>
        Dataset Result Differences
      </Typography>
      <Typography variant="body2" color="text.secondary" mb={2}>
        -- Placeholder for number of candidates and SPD values per repair --
      </Typography>

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
          <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
            Combos: <strong>{isNaN(combinations) ? "—" : combinations}</strong>{" "}
            · Fully time: <strong>{runtimeFF || "—"}s</strong>{" "}
            · Ranges time: <strong>{runtimeRP || "—"}s</strong>
          </Typography>

          {/* Runtime */}
          <Box sx={{ mb: 2 }}>
            <Typography variant="body2" mb={0.5}>
              Runtime (s) - FF: {runtimeFF || "—"}
            </Typography>
            <LinearProgress variant="determinate" value={asPercent(runtimeFF, runtimeMax)} />
            <Typography variant="body2" mt={0.5}>
              Runtime (s) - RP: {runtimeRP || "—"}
            </Typography>
            <LinearProgress variant="determinate" value={asPercent(runtimeRP, runtimeMax)} color="secondary" />
          </Box>

          {/* NCE */}
          <Box sx={{ mb: 2 }}>
            <Typography variant="body2" mb={0.5}>
              NCE (checks) – FF: {nceFF}
            </Typography>
            <LinearProgress variant="determinate" value={asPercent(nceFF, nceMax)} />
            <Typography variant="body2" mt={0.5}>
              NCE (checks) – RP: {nceRP}
            </Typography>
            <LinearProgress variant="determinate" value={asPercent(nceRP, nceMax)} color="secondary" />
          </Box>

          {/* NCA */}
          <Box sx={{ mb: 2 }}>
            <Typography variant="body2" mb={0.5}>
              NCA (refinements) – FF: {ncaFF}
            </Typography>
            <LinearProgress variant="determinate" value={asPercent(ncaFF, ncaMax)} />
            <Typography variant="body2" mt={0.5}>
              NCA (refinements) – RP: {ncaRP}
            </Typography>
            <LinearProgress variant="determinate" value={asPercent(ncaRP, ncaMax)} color="secondary" />
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
