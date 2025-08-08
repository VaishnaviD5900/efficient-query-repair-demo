import { useEffect, useState } from "react";
import {
  Box,
  Container,
  Typography,
  Paper,
  Grid,
  Divider,
  Button,
  Chip,
  LinearProgress,
} from "@mui/material";
import { CheckCircle, Cancel } from "@mui/icons-material";
import { useLocation } from "react-router-dom";

export default function ResultsPage() {
  const location = useLocation();
  const [sqlQuery, setSqlQuery] = useState("");
  const [aggregations, setAggregations] = useState<any[]>([]);
  const [constraintExpr, setConstraintExpr] = useState<string>("");
  const {
    datasetName = "Unknown Dataset",
    size = 0,
    columnCount = 0,
  } = location.state || {};

  const constraint = {
    type: "SPD",
    threshold: 0.2,
    actual: 0.35,
    satisfied: false,
  };

  useEffect(() => {
    const stored = localStorage.getItem("queryRepairData");
    if (stored) {
      const parsed = JSON.parse(stored);
      setSqlQuery(parsed.sqlQuery || "");
      setAggregations(parsed.aggregations || []);
      setConstraintExpr(parsed.constraintExpr || "");
    }
  }, []);

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
        {/* <Button variant="contained">Export</Button> */}
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
          {" "}
          Original Query{" "}
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
          Aggregate Functions{" "}
        </Typography>
        <Paper variant="outlined" sx={{ p: 1, my: 1, minHeight: 60 }}>
          {aggregations.length === 0 ? (
            <Typography variant="body2" color="text.secondary">
              Aggregate Functions not available --
            </Typography>
          ) : (
            aggregations.map((agg, index) => (
              <Typography
                key={index}
                variant="body2"
                color="text.secondary"
                style={{ whiteSpace: "pre-wrap" }}
              >
                {`${agg.name}: ${agg.func.toUpperCase()} WHERE ${
                  agg.predicate
                }`}
              </Typography>
            ))
          )}
        </Paper>

        <Grid container spacing={2}>
          <Grid size={{ xs: 6 }}>
            <Typography variant="h6">
              Arithmetic Expression: {constraintExpr || "--"}
            </Typography>
          </Grid>
          <Grid size={{ xs: 6 }}>
            <Typography variant="h6">
              Constraint Status: {constraint.actual}
              {constraint.satisfied ? (
                <CheckCircle color="success" sx={{ ml: 1 }} />
              ) : (
                <Cancel color="error" sx={{ ml: 1 }} />
              )}
            </Typography>
          </Grid>
        </Grid>
      </Paper>

      <Typography variant="h6" gutterBottom>
        Top-k Repaired Queries
      </Typography>
      <Typography variant="body2" color="text.secondary" mb={2}>
        -- Awaiting repair data from backend --
      </Typography>

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

      {["Runtime (s)", "NCE", "NCA", "Search Space (%)"].map((metric) => (
        <Box key={metric} sx={{ mb: 2 }}>
          <Typography variant="body2" mb={0.5}>
            {metric} - FF
          </Typography>
          <LinearProgress variant="determinate" value={70} />
          <Typography variant="body2" mt={0.5}>
            {metric} - RP
          </Typography>
          <LinearProgress variant="determinate" value={20} color="secondary" />
        </Box>
      ))}

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
