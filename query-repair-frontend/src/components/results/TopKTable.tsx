import { Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Typography } from "@mui/material";
import type { Bounds } from "../../utils/constraints";
import { rewriteQueryWithVector } from "../../utils/query";
import { ResultCell } from "./ResultCell";
import { SimilarityCell } from "./SimilarityCell";

type TopKTableProps = {
  title: string;
  rows: { row: Record<string, any> }[];
  showRangeSatisfaction: boolean;
  sqlQuery: string;
  bounds: Bounds;
  maxSim: number;
};

export function TopKTable({
  title, rows, showRangeSatisfaction, sqlQuery, bounds, maxSim
}: TopKTableProps) {
  if (!rows?.length) {
    return (
      <>
        <Typography variant="subtitle1" gutterBottom>{title}</Typography>
        <Typography variant="body2" color="text.secondary" mb={2}>No rows to display.</Typography>
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
              <TableCell width={30}>Rank</TableCell>
              <TableCell>Repaired queries</TableCell>
              <TableCell>Distance from original</TableCell>
              <TableCell>Result</TableCell>
              {showRangeSatisfaction && <TableCell width={50}>Range Satisfaction</TableCell>}
            </TableRow>
          </TableHead>
          <TableBody>
            {rows.map((r, idx) => {
              const row = r.row || {};
              const rawCond = String(row["conditions"] ?? row["Conditions"] ?? "—");
              const similarity = row["Similarity"] ?? "—";
              const result = row["Result"] ?? "—";
              const rangeSat = row["Range Satisfaction"] ?? "—";
              const condSql = rewriteQueryWithVector(sqlQuery, rawCond);

              return (
                <TableRow key={idx}>
                  <TableCell>{idx + 1}</TableCell>
                  <TableCell sx={{ fontFamily: "monospace", whiteSpace: "pre-wrap" }}>{condSql}</TableCell>
                  <TableCell sx={{ verticalAlign: "top", py: 1.25, width: 190 }}>
                    <SimilarityCell similarityValue={similarity} vectorText={rawCond} sql={sqlQuery} max={maxSim} />
                  </TableCell>
                  <TableCell><ResultCell rawResult={result} bounds={bounds} /></TableCell>
                  {showRangeSatisfaction && <TableCell>{rangeSat}</TableCell>}
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </TableContainer>
    </>
  );
}
