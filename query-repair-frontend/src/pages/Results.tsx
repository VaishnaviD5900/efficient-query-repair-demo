import { useEffect, useState } from "react";
import {
  Box, Container, Typography, Paper, Divider, LinearProgress, Alert,
} from "@mui/material";
import { useLocation } from "react-router-dom";

import { MetricLabel } from "../components/common/InfoMetric";
import { StatBar } from "../components/common/StatBar";
import { TopKTable } from "../components/results/TopKTable";
import { getMaxSimilarity } from "../components/results/SimilarityCell";
import { parseConstraintBounds } from "../utils/constraints";
import type { Bounds } from "../utils/constraints";
import { signatureFromRunInfo, signatureFromSql } from "../utils/query";

type ParsedResults = {
  output_dir: string;
  run_info: Record<string, any>[];
  satisfied_conditions_ff: { row: Record<string, any> }[];
  satisfied_conditions_rp: { row: Record<string, any> }[];
  raw_files: string[];
};
const API_BASE ="https://query-repair-frontend-cee9fgg6fsdehcdj.uksouth-01.azurewebsites.net"

export default function ResultsPage() {
  const location = useLocation();

  const [sqlQuery, setSqlQuery] = useState("");
  const [aggregations, setAggregations] = useState<any[]>([]);
  const [constraintExpr, setConstraintExpr] = useState<string>("");

  const [artifacts, setArtifacts] = useState<ParsedResults | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>("");

  const {
    datasetName = "Unknown Dataset",
    size = 0,
    columnCount = 0,
    outputDir: outputDirFromState,
  } = (location.state as any) || {};

  const asPercent = (value: number, max: number) =>
    max <= 0 ? 0 : Math.min(100, Math.round((value / max) * 100));

  useEffect(() => {
    const stored = localStorage.getItem("queryRepairData");
    if (stored) {
      const parsed = JSON.parse(stored);
      setSqlQuery(parsed.sqlQuery || "");
      setAggregations(parsed.aggregations || []);
      setConstraintExpr(parsed.constraintExpr || "");
    }

    const outputDir = outputDirFromState || localStorage.getItem("qrOutputDir") || "";
    if (!outputDir) {
      setError("Missing output directory. Run a repair first.");
      setLoading(false);
      return;
    }

    (async () => {
      try {
        setLoading(true);
        const res = await fetch(`${API_BASE}/api/v1/results?dataset=${datasetName}`);
        if (!res.ok) throw new Error(await res.text());
        const data: ParsedResults = await res.json();
        setArtifacts(data);
      } catch (e: any) {
        setError(e?.message || "Failed to load results");
      } finally {
        setLoading(false);
      }
    })();
  }, [outputDirFromState]);

  // ----- RunInfo matching (SQL ↔ RunInfo) -----
  const runInfoRows = artifacts?.run_info || [];
  const sigSql = signatureFromSql(sqlQuery);
  const matchingRunInfo = runInfoRows.filter((r) => signatureFromRunInfo(String(r["Query"] || "")) === sigSql);

  const hasRunMatch = matchingRunInfo.length > 0;
  const fullyRow = hasRunMatch ? matchingRunInfo.find((r) => (r["Type"] || r["type"]) === "Fully") : undefined;
  const rangesRow = hasRunMatch ? matchingRunInfo.find((r) => (r["Type"] || r["type"]) === "Ranges") : undefined;
  const anyRow = hasRunMatch ? matchingRunInfo[0] : undefined;

  const runtimeFF = Number(fullyRow?.["Time"] ?? 0);
  const runtimeRP = Number(rangesRow?.["Time"] ?? 0);
  const runtimeMax = Math.max(runtimeFF || 0, runtimeRP || 0, 1);

  const nceFF = Number(fullyRow?.["Checked Num"] ?? 0);
  const nceRP = Number(rangesRow?.["Checked Num"] ?? 0);

  const ncaFF = Number(fullyRow?.["Refinement Num"] ?? 0);
  const ncaRP = Number(rangesRow?.["Refinement Num"] ?? 0);

  const accessFF = Number(fullyRow?.["Access Num"] ?? 0);
  const accessRP = Number(rangesRow?.["Access Num"] ?? 0);

  const distFF = Number(fullyRow?.["Distance"] ?? 0);
  const distRP = Number(rangesRow?.["Distance"] ?? 0);
  const distFFpct = Math.max(0, Math.min(100, Math.round(distFF * 100)));
  const distRPpct = Math.max(0, Math.min(100, Math.round(distRP * 100)));

  const combinations = Number(anyRow?.["Combinations Num"] ?? NaN);

  const constraintStr = String(
    anyRow?.["Arithmetic Expression"] ??
    anyRow?.["Constraint"] ?? // keep as backup if your CSV still has this
    ""
  );
  const bounds: Bounds = parseConstraintBounds(constraintStr);

  const maxSimFF = getMaxSimilarity(artifacts?.satisfied_conditions_ff || [], sqlQuery);
  const maxSimRP = getMaxSimilarity(artifacts?.satisfied_conditions_rp || [], sqlQuery);

  return (
    <Container maxWidth="md" sx={{ mt: 2 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
        <Typography variant="h4" fontWeight="bold" gutterBottom>Results</Typography>
      </Box>

      <Typography variant="h6" color="text.secondary" gutterBottom>
        Dataset: <strong>{datasetName}</strong>{" "}
        <Typography variant="body2" component="span">Size: {size} KB</Typography>,{" "}
        <Typography variant="body2" component="span">Columns: {columnCount}</Typography>
      </Typography>

      <Paper variant="outlined" sx={{ p: 2, mb: 3 }}>
        <Typography variant="h6" gutterBottom>Original Query</Typography>
        <Paper variant="outlined" sx={{ p: 1, my: 1 }}>
          <Typography variant="body2" color="text.secondary" style={{ whiteSpace: "pre-wrap" }}>
            {sqlQuery || "-- SQL query not available --"}
          </Typography>
        </Paper>

        <Typography variant="h6" gutterBottom>Aggregate Functions</Typography>
        <Paper variant="outlined" sx={{ p: 1, my: 1 }}>
          {(aggregations?.length ?? 0) === 0 ? (
            <Typography variant="body2" color="text.secondary">Aggregate Functions not available --</Typography>
          ) : (
            aggregations.map((agg: any, index: number) => (
              <Typography key={index} variant="body2" color="text.secondary" style={{ whiteSpace: "pre-wrap" }}>
                {`${agg.name}: ${String(agg.func).toUpperCase()} WHERE ${agg.predicate}`}
              </Typography>
            ))
          )}
        </Paper>

        <Typography variant="h6" gutterBottom>Arithmetic Expression</Typography>
        <Paper variant="outlined" sx={{ p: 1, my: 1 }}>
          <Typography variant="body2" color="text.secondary" style={{ whiteSpace: "pre-wrap" }}>
            {constraintExpr || "--"}
          </Typography>
        </Paper>
      </Paper>

      {/* Top-k tables */}
      <Typography variant="h6" gutterBottom>Top-k Repaired Queries</Typography>
      <TopKTable
        title="Full Filtering (point estimates)"
        rows={artifacts?.satisfied_conditions_ff || []}
        showRangeSatisfaction={false}
        sqlQuery={sqlQuery}
        bounds={bounds}
        maxSim={maxSimFF}
      />
      <TopKTable
        title="Range Pruning (interval estimates)"
        rows={artifacts?.satisfied_conditions_rp || []}
        showRangeSatisfaction={false}
        sqlQuery={sqlQuery}
        bounds={bounds}
        maxSim={maxSimRP}
      />

      <Divider sx={{ my: 3 }} />

      <Typography variant="h6" gutterBottom>Algorithm Search Space Metrics</Typography>
      {loading && <LinearProgress sx={{ mb: 2 }} />}
      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      {!!artifacts?.run_info?.length && (
        <Box sx={{ mb: 2 }}>
          {/* summary line with info icons */}
          <Typography
            variant="body2"
            color="text.secondary"
            sx={{ mb: 3, display: "flex", alignItems: "center", flexWrap: "wrap", gap: 1 }}
          >
            <MetricLabel
              label="Combos"
              info="Combinations Num: total number of candidate repairs considered (product of per-predicate options)."
            />
            : <strong>{Number.isFinite(combinations) ? Number(combinations).toLocaleString() : "—"}</strong>
          </Typography>

          {/* bars */}
          <StatBar
            label="Runtime (s) - FF"
            info="Wall-clock time to compute top-k with Full Filtering."
            value={runtimeFF || "—"}
            progress={asPercent(runtimeFF, runtimeMax)}
          />
          <StatBar
            label="Runtime (s) - RP"
            info="Wall-clock time to compute top-k with Range Pruning."
            value={runtimeRP || "—"}
            progress={asPercent(runtimeRP, runtimeMax)}
            color="secondary"
            mb={3}
          />

          <StatBar
            label="NCE (checks) - FF"
            info="Constraint evaluations performed; lower means more pruning."
            value={nceFF}
            progress={asPercent(nceFF, Math.max(nceFF, nceRP, 1))}
          />
          <StatBar
            label="NCE (checks) - RP"
            info="Constraint evaluations on ranges/singletons during RP."
            value={nceRP}
            progress={asPercent(nceRP, Math.max(nceFF, nceRP, 1))}
            color="secondary"
            mb={3}
          />

          <StatBar
            label="NCA (refinements) - FF"
            info="Refinement steps during search; lower is better."
            value={ncaFF}
            progress={asPercent(ncaFF, Math.max(ncaFF, ncaRP, 1))}
          />
          <StatBar
            label="NCA (refinements) - RP"
            info="Range splits/refinements performed by RP."
            value={ncaRP}
            progress={asPercent(ncaRP, Math.max(ncaFF, ncaRP, 1))}
            color="secondary"
            mb={3}
          />

          <StatBar
            label="Access Num - FF"
            info="How many index/cluster partitions were accessed; lower means less effort."
            value={Number.isFinite(accessFF) ? accessFF.toLocaleString() : "—"}
            progress={asPercent(accessFF, Math.max(accessFF, accessRP, 1))}
          />
          <StatBar
            label="Access Num - RP"
            info="Partitions/nodes accessed under RP; lower is better."
            value={Number.isFinite(accessRP) ? accessRP.toLocaleString() : "—"}
            progress={asPercent(accessRP, Math.max(accessFF, accessRP, 1))}
            color="secondary"
            mb={3}
          />

          <StatBar
            label="Search explored (Distance) - FF"
            info="Fraction of candidate space explored; 0-100%. Lower is better."
            value={Number.isFinite(distFF) ? `${distFFpct}%` : "—"}
            progress={distFFpct}
          />
          <StatBar
            label="Search explored (Distance) - RP"
            info="Fraction of candidate space explored by RP; lower is better."
            value={Number.isFinite(distRP) ? `${distRPpct}%` : "—"}
            progress={distRPpct}
            color="secondary"
            mb={3}
          />
        </Box>
      )}

      {!loading && !artifacts?.run_info?.length && !error && (
        <Typography variant="body2" color="text.secondary" mb={2}>
          No parsed metrics found in the output directory.
        </Typography>
      )}

      {/* <Divider sx={{ my: 3 }} /> */}

      {/* <Typography variant="h6" gutterBottom>Algorithm Efficiency Summary</Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Range Pruning (RP) achieved the same top-k repairs as Full Filtering (FF),
        while exploring only a fraction of the search space.
      </Typography> */}
    </Container>
  );
}
