import React from "react";
import {
  Typography,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Paper,
} from "@mui/material";

interface DatasetSchemaProps {
  data: Record<string, any>[];
}

const DatasetSchema: React.FC<DatasetSchemaProps> = ({ data }) => {
  if (data.length === 0) return null;

  const inferType = (value: any): string => {
    const lower = String(value).toLowerCase();

    if (lower === "true" || lower === "false") return "boolean";
    if (!isNaN(Number(value))) return "number";
    return "string";
  };

  return (
    <>
      <Typography variant="h6" gutterBottom>
        Dataset Schema
      </Typography>
      <Table component={Paper} size="small" sx={{ mb: 2 }}>
        <TableHead>
          <TableRow>
            <TableCell sx={{ fontWeight: "bold" }}>Column</TableCell>
            <TableCell sx={{ fontWeight: "bold" }}>Inferred Type</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {Object.keys(data[0]).map((key) => {
            const sampleValue = data[0][key];
            return (
              <TableRow key={key}>
                <TableCell>{key}</TableCell>
                <TableCell>{inferType(sampleValue)}</TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>
    </>
  );
};

export default DatasetSchema;
