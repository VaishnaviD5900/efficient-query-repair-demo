import { useState } from "react";
// Material UI
import {
  Container,
  Typography,
  Grid,
  Card,
  CardActionArea,
  CardContent,
  TextField,
  IconButton,
  Box,
  Button,
  CircularProgress,
  MenuItem,
} from "@mui/material";
// Icons
import AddIcon from "@mui/icons-material/Add";
import RemoveIcon from "@mui/icons-material/Remove";
// Parsing
import Papa from "papaparse";
// Features
import DatasetPreview from "../features/DatasetPreview";
import DatasetSchema from "../features/DatasetSchema";
// Navigation
import { useNavigate } from "react-router-dom";

// Types
type Constraint = {
  field: string;
  op: string;
  value: string;
};

type Aggregation = {
  name: string;
  func: "count" | "sum" | "avg" | "min" | "max";
  predicates: Constraint[];
};

type Dataset = {
  id: string;
  name: string;
  file: string;
  size: number; // in KB
};

const datasetConfig: Dataset[] = [
  {
    id: "acs",
    name: "ACS Income State",
    file: "/datasets/ACSIncome_state_number1 2(in).csv",
    size: 44551, // in KB
  },
  {
    id: "healthcare",
    name: "Healthcare 800",
    file: "/datasets/healthcare_800(in).csv",
    size: 34, // in KB
  },
];

export default function InputPage() {
  const [selectedDatasetId, setSelectedDatasetId] = useState<string | null>(
    null
  );
  const [datasetPreview, setDatasetPreview] = useState<Record<string, any>[]>(
    []
  );
  const [isLoading, setIsLoading] = useState(false);
  const [constraints, setConstraints] = useState<Constraint[]>([
    { field: "", op: "", value: "" },
  ]);
  const [aggregations, setAggregations] = useState<Aggregation[]>([
    {
      name: "agg1",
      func: "count",
      predicates: [{ field: "", op: "", value: "" }],
    },
  ]);
  const [aggregateConstraintExpr, setAggregateConstraintExpr] =
    useState<string>("");
  const [columnTypes, setColumnTypes] = useState<Record<string, string>>({});
  const navigate = useNavigate();

  const inferType = (value: any): string => {
    const lower = String(value).toLowerCase();
    if (lower === "true" || lower === "false") return "boolean";
    if (!isNaN(Number(value))) return "number";
    return "string";
  };

  const loadDataset = async (filePath: string) => {
    setIsLoading(true);
    const response = await fetch(filePath);
    const csv = await response.text();
    Papa.parse(csv, {
      header: true,
      skipEmptyLines: true,
      complete: (results) => {
        const parsedData = results.data as Record<string, any>[];
        const previewData = parsedData.slice(0, 5);
        setDatasetPreview(previewData);
        const types: Record<string, string> = {};
        if (previewData.length > 0) {
          for (const key of Object.keys(previewData[0])) {
            types[key] = inferType(previewData[0][key]);
          }
        }
        setColumnTypes(types);
        setIsLoading(false);
      },
    });
  };

  const handleDatasetClick = (dataset: Dataset) => {
    setSelectedDatasetId(dataset.id);
    loadDataset(dataset.file);
  };

  const handleConstraintChange = (
    index: number,
    key: keyof Constraint,
    value: string
  ) => {
    const updated = [...constraints];
    updated[index][key] = value;
    if (key === "field") updated[index]["op"] = "";
    setConstraints(updated);
  };

  const handleAddConstraint = () => {
    setConstraints([...constraints, { field: "", op: "", value: "" }]);
  };

  const handleRemoveConstraint = (index: number) => {
    const updated = [...constraints];
    updated.splice(index, 1);
    setConstraints(updated);
  };

  const columnOptions =
    datasetPreview.length > 0 ? Object.keys(datasetPreview[0]) : [];

  const getOperatorsForField = (field: string): string[] => {
    const type = columnTypes[field];
    if (type === "number") return ["<", "<=", "=", ">=", ">"];
    if (type === "string" || type === "boolean") return ["=", "!="];
    return [];
  };

  const buildPredicate = (agg: Aggregation): string => {
    return agg.predicates
      .filter((p) => p.field && p.op && p.value)
      .map((p) => `${p.field} ${p.op} '${p.value}'`)
      .join(" AND ");
  };

  const generateSQLQuery = () => {
    const selectedDataset = datasetConfig.find(
      (d) => d.id === selectedDatasetId
    );
    const tableName = selectedDataset?.id || "uploaded";
    const whereConditions = constraints
      .filter((c) => c.field && c.op && c.value)
      .map((c) => `${c.field} ${c.op} '${c.value}'`);
    const whereClause =
      whereConditions.length > 0
        ? `WHERE ${whereConditions.join(" AND ")}`
        : "";
    const query = `SELECT * FROM ${tableName} ${whereClause};`;
    console.log("Generated SQL Query:", query);
    console.log(
      "Defined Aggregations:",
      aggregations.map((a) => ({ ...a, predicate: buildPredicate(a) }))
    );
    console.log("Constraint Expression:", aggregateConstraintExpr);
    return query;
  };

  return (
    <Container maxWidth="lg" sx={{ pt: 2 }}>
      <Typography variant="h4" fontWeight="bold" gutterBottom>
        SQL Query Repair
      </Typography>

      <Typography variant="h6" gutterBottom>
        Select a Dataset
      </Typography>
      <Grid container spacing={2} mb={3}>
        {datasetConfig.map((dataset) => {
          const isSelected = dataset.id === selectedDatasetId;

          return (
            <Grid size={{ xs: 12, sm: 4 }} key={dataset.id}>
              <Card
                sx={{
                  backgroundColor: isSelected
                    ? "rgba(64, 82, 181, 0.6)"
                    : "grey.300",
                }}
              >
                <CardActionArea onClick={() => handleDatasetClick(dataset)}>
                  <CardContent>
                    <Typography
                      variant="h6"
                      align="center"
                      color={isSelected ? "white" : "black"}
                    >
                      {dataset.name}
                    </Typography>
                  </CardContent>
                </CardActionArea>
              </Card>
            </Grid>
          );
        })}
      </Grid>

      {isLoading && (
        <Box display="flex" justifyContent="center" my={4}>
          <CircularProgress />
        </Box>
      )}

      {!isLoading && datasetPreview.length > 0 && (
        <>
          <DatasetSchema data={datasetPreview} />
          <DatasetPreview data={datasetPreview} />
        </>
      )}

      <Typography variant="h6" gutterBottom>
        Input SQL Query
      </Typography>
      {constraints.map((constraint, index) => (
        <Box key={index} display="flex" alignItems="center" gap={2} mb={2}>
          <TextField
            select
            label="Field"
            size="small"
            value={constraint.field}
            onChange={(e) =>
              handleConstraintChange(index, "field", e.target.value)
            }
            sx={{ minWidth: 210 }}
          >
            {columnOptions.map((col) => (
              <MenuItem key={col} value={col}>
                {col}
              </MenuItem>
            ))}
          </TextField>
          <TextField
            select
            label="Op"
            size="small"
            value={constraint.op}
            onChange={(e) =>
              handleConstraintChange(index, "op", e.target.value)
            }
            sx={{ width: 100 }}
            disabled={!constraint.field}
          >
            {(getOperatorsForField(constraint.field) || []).map((op) => (
              <MenuItem key={op} value={op}>
                {op}
              </MenuItem>
            ))}
          </TextField>
          <TextField
            label="Value"
            size="small"
            value={constraint.value}
            onChange={(e) =>
              handleConstraintChange(index, "value", e.target.value)
            }
          />
          <IconButton onClick={handleAddConstraint}>
            <AddIcon />
          </IconButton>
          {constraints.length > 1 && (
            <IconButton onClick={() => handleRemoveConstraint(index)}>
              <RemoveIcon />
            </IconButton>
          )}
        </Box>
      ))}

      <Typography variant="h6" gutterBottom>
        Define Aggregation Functions
      </Typography>
      {aggregations.map((agg, index) => (
        <Box key={index} mb={2}>
          <Box display="flex" alignItems="center" gap={2}>
            <TextField
              label="Name"
              size="small"
              value={`agg${index + 1}`}
              disabled
              sx={{ width: 100 }}
            />
            <TextField
              select
              label="Function"
              size="small"
              value={agg.func}
              onChange={(e) => {
                const updated = [...aggregations];
                updated[index].func = e.target.value as Aggregation["func"];
                setAggregations(updated);
              }}
              sx={{ width: 120 }}
            >
              {["count", "sum", "avg", "min", "max"].map((fn) => (
                <MenuItem key={fn} value={fn}>
                  {fn}
                </MenuItem>
              ))}
            </TextField>
            <IconButton
              onClick={() => {
                setAggregations([
                  ...aggregations,
                  {
                    name: `agg${aggregations.length + 1}`,
                    func: "count",
                    predicates: [{ field: "", op: "", value: "" }],
                  },
                ]);
              }}
            >
              <AddIcon />
            </IconButton>
            {aggregations.length > 1 && (
              <IconButton
                onClick={() => {
                  const updated = [...aggregations];
                  updated.splice(index, 1);
                  setAggregations(updated);
                }}
              >
                <RemoveIcon />
              </IconButton>
            )}
          </Box>

          {/* Aggregation Predicates */}
          {agg.predicates.map((pred, predIndex) => (
            <Box
              key={predIndex}
              display="flex"
              alignItems="center"
              gap={2}
              mt={1}
              ml={32}
            >
              <TextField
                select
                label="Field"
                size="small"
                value={pred.field}
                onChange={(e) => {
                  const updated = [...aggregations];
                  updated[index].predicates[predIndex].field = e.target.value;
                  setAggregations(updated);
                }}
                sx={{ minWidth: 210 }}
              >
                {columnOptions.map((col) => (
                  <MenuItem key={col} value={col}>
                    {col}
                  </MenuItem>
                ))}
              </TextField>
              <TextField
                select
                label="Op"
                size="small"
                value={pred.op}
                sx={{ width: 100 }}
                onChange={(e) => {
                  const updated = [...aggregations];
                  updated[index].predicates[predIndex].op = e.target.value;
                  setAggregations(updated);
                }}
              >
                {(getOperatorsForField(pred.field) || []).map((op) => (
                  <MenuItem key={op} value={op}>
                    {op}
                  </MenuItem>
                ))}
              </TextField>
              <TextField
                label="Value"
                size="small"
                value={pred.value}
                onChange={(e) => {
                  const updated = [...aggregations];
                  updated[index].predicates[predIndex].value = e.target.value;
                  setAggregations(updated);
                }}
              />
              <IconButton
                onClick={() => {
                  const updated = [...aggregations];
                  updated[index].predicates.push({
                    field: "",
                    op: "",
                    value: "",
                  });
                  setAggregations(updated);
                }}
              >
                <AddIcon />
              </IconButton>
              {agg.predicates.length > 1 && (
                <IconButton
                  onClick={() => {
                    const updated = [...aggregations];
                    updated[index].predicates.splice(predIndex, 1);
                    setAggregations(updated);
                  }}
                >
                  <RemoveIcon />
                </IconButton>
              )}
            </Box>
          ))}
        </Box>
      ))}

      <Typography variant="h6" gutterBottom>
        Constraint Expression
      </Typography>
      <TextField
        label="Expression (e.g., 0.1 <= (agg1 / agg2))"
        fullWidth
        size="small"
        multiline
        value={aggregateConstraintExpr}
        onChange={(e) => setAggregateConstraintExpr(e.target.value)}
      />

      <Button
        variant="contained"
        sx={{
          my: 3,
          backgroundColor: "rgba(64, 82, 181, 0.8)",
          color: "white",
          "&:hover": {
            backgroundColor: "rgba(64, 82, 181, 1)", // slightly darker on hover
          },
        }}
        onClick={() => {
          const query = generateSQLQuery();
          const selectedDataset = datasetConfig.find(
            (d) => d.id === selectedDatasetId
          );

          const aggregatedWithPredicates = aggregations.map((a) => ({
            ...a,
            predicate: buildPredicate(a),
          }));

          localStorage.setItem(
            "queryRepairData",
            JSON.stringify({
              datasetId: selectedDataset?.id || null,
              datasetName: selectedDataset?.name || null,
              size: selectedDataset?.size || 0,
              columnCount: Object.keys(columnTypes).length,
              sqlQuery: query,
              aggregations: aggregatedWithPredicates,
              constraintExpr: aggregateConstraintExpr,
            })
          );
          navigate("/results", {
            state: {
              datasetName: selectedDataset?.name || "Unknown",
              size: selectedDataset?.size || 0,
              columnCount: Object.keys(columnTypes).length,
              query,
            },
          });
        }}
      >
        Run Repair
      </Button>
    </Container>
  );
}
