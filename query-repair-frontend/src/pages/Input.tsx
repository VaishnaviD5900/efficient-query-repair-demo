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

// ---------- Types ----------
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
  size: number; // KB
  file?: string; // single CSV
  files?: Record<string, string>; // multi-CSV (tpch)
};

// ---------- Datasets ----------
const datasetConfig: Dataset[] = [
  {
    id: "acs",
    name: "ACS Income State",
    file: "/datasets/ACSIncome_state_number1 2(in).csv",
    size: 44551,
  },
  {
    id: "healthcare",
    name: "Healthcare 800",
    file: "/datasets/healthcare_800(in).csv",
    size: 34,
  },
  {
    id: "tpch",
    name: "TPC-H 0.1",
    size: 0, // optional
    files: {
      customer: "/datasets/tpch_0_1/customer.csv",
      orders: "/datasets/tpch_0_1/orders.csv",
      lineitem: "/datasets/tpch_0_1/lineitem.csv",
      part: "/datasets/tpch_0_1/part.csv",
      supplier: "/datasets/tpch_0_1/supplier.csv",
      partsupp: "/datasets/tpch_0_1/partsupp.csv",
      nation: "/datasets/tpch_0_1/nation.csv",
      region: "/datasets/tpch_0_1/region.csv",
      // p_type_mapping: "/datasets/tpch_0_1/p_type_mapping.csv",
      // r_name_mapping: "/datasets/tpch_0_1/r_name_mapping.csv",
    },
  },
];

// ---------- Top-level utils (safe to keep outside component) ----------
const parseCsv = async (path: string) =>
  new Promise<Record<string, any>[]>((resolve, reject) => {
    fetch(path)
      .then((r) => r.text())
      .then((csv) =>
        Papa.parse(csv, {
          header: true,
          skipEmptyLines: true,
          complete: (res) => resolve(res.data as Record<string, any>[]),
          error: reject,
        })
      )
      .catch(reject);
  });

const indexBy = (rows: Record<string, any>[], key: string) => {
  const idx: Record<string, Record<string, any>> = {};
  for (const r of rows) idx[r[key]] = r;
  return idx;
};

const TPC_H_CACHE_KEY = "tpch_0_1_preview_v1";

// ---------- Component ----------
export default function InputPage() {
  const [selectedDatasetId, setSelectedDatasetId] = useState<string | null>(null);
  const [datasetPreview, setDatasetPreview] = useState<Record<string, any>[]>([]);
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
  const [aggregateConstraintExpr, setAggregateConstraintExpr] = useState<string>("");
  const [columnTypes, setColumnTypes] = useState<Record<string, string>>({});
  const navigate = useNavigate();

  // ---- inference helpers (inside component so they can be reused safely)
  const inferType = (value: any): string => {
    const lower = String(value).toLowerCase();
    if (lower === "true" || lower === "false") return "boolean";
    if (!isNaN(Number(value))) return "number";
    return "string";
  };

  const inferColumnTypes = (rows: Record<string, any>[]) => {
    const types: Record<string, string> = {};
    if (rows.length === 0) return types;
    for (const key of Object.keys(rows[0])) {
      types[key] = inferType(rows[0][key]);
    }
    return types;
  };

  // ---- dataset loaders (inside component so they can call setState)
  const loadSingleCsvDataset = async (filePath: string) => {
    setIsLoading(true);
    const rows = await parseCsv(filePath);
    const previewData = rows.slice(0, 5);
    setDatasetPreview(previewData);
    setColumnTypes(inferColumnTypes(previewData));
    setIsLoading(false);
  };

  const withPrefix = (row: Record<string, any> | undefined, prefix: string) => {
  if (!row) return {};
  const out: Record<string, any> = {};
  for (const k of Object.keys(row)) out[`${prefix}${k}`] = row[k];
  return out;
};

  const loadTpchDataset = async (files: NonNullable<Dataset["files"]>) => {
    setIsLoading(true);

    // 1) try cache
    const cacheRaw = localStorage.getItem(TPC_H_CACHE_KEY);
    if (cacheRaw) {
      try {
        const cached = JSON.parse(cacheRaw);
        setDatasetPreview(cached.preview);
        setColumnTypes(cached.columnTypes);
        setIsLoading(false);
        return;
      } catch {
        // ignore bad cache and continue
      }
    }

    // 2) fetch all CSVs
   const [
    customer, orders, lineitem, part,
    supplier, partsupp, nation, region
  ] = await Promise.all([
    parseCsv(files.customer),
    parseCsv(files.orders),
    parseCsv(files.lineitem),
    parseCsv(files.part),
    parseCsv(files.supplier),
    parseCsv(files.partsupp),
    parseCsv(files.nation),
    parseCsv(files.region),
  ]);

    // 3) build indexes for joins
    const custByKey = indexBy(customer, "c_custkey");
  const orderByKey = indexBy(orders, "o_orderkey");
  const partByKey = indexBy(part, "p_partkey");
  const suppByKey = indexBy(supplier, "s_suppkey");
  const partsuppByComposite: Record<string, Record<string, any>> = {};
  for (const ps of partsupp) {
    partsuppByComposite[`${ps.ps_partkey}|${ps.ps_suppkey}`] = ps;
  }
  const nationByKey = indexBy(nation, "n_nationkey");
  const regionByKey = indexBy(region, "r_regionkey");

    // 4) denormalized lineitem-centric preview (first 5 rows)
    const joined: Record<string, any>[] = [];
  for (const li of lineitem.slice(0, 5)) {
    const ord = orderByKey[li.l_orderkey];
    const cust = ord ? custByKey[ord.o_custkey] : undefined;
    const ps = partsuppByComposite[`${li.l_partkey}|${li.l_suppkey}`];
    const prt = partByKey[li.l_partkey];
    const sup = suppByKey[li.l_suppkey];

    const custNation = cust ? nationByKey[cust.c_nationkey] : undefined;
    const custRegion = custNation ? regionByKey[custNation.n_regionkey] : undefined;
    const supNation = sup ? nationByKey[sup.s_nationkey] : undefined;
    const supRegion = supNation ? regionByKey[supNation.n_regionkey] : undefined;

    joined.push({
      // --- Required Q7 columns ---
      p_partkey: prt?.p_partkey,
      p_size: prt?.p_size,
      p_type: prt?.p_type,
      ps_partkey: ps?.ps_partkey,
      ps_suppkey: ps?.ps_suppkey,
      s_suppkey: sup?.s_suppkey,
      s_nationkey: sup?.s_nationkey,
      n_nationkey: supNation?.n_nationkey,
      n_regionkey: supNation?.n_regionkey,
      r_regionkey: supRegion?.r_regionkey,
      r_name: supRegion?.r_name,
      l_partkey: li.l_partkey,
      l_suppkey: li.l_suppkey,

      // --- Extra context columns (prefixed) ---
      ...withPrefix(prt && {
        p_name: prt.p_name,
        p_brand: prt.p_brand
      }, "part_"),

      ...withPrefix(ps && {
        ps_availqty: ps.ps_availqty,
        ps_supplycost: ps.ps_supplycost
      }, "partsupp_"),

      ...withPrefix(sup && {
        s_name: sup.s_name,
        s_acctbal: sup.s_acctbal
      }, "supplier_"),

      ...withPrefix(supNation && { n_name: supNation.n_name }, "nation_"),

      ...withPrefix(ord && {
        o_orderkey: ord.o_orderkey,
        o_custkey: ord.o_custkey,
        o_orderdate: ord.o_orderdate,
        o_totalprice: ord.o_totalprice
      }, "orders_"),

      ...withPrefix(cust && {
        c_custkey: cust.c_custkey,
        c_name: cust.c_name,
        c_acctbal: cust.c_acctbal
      }, "customer_"),

      ...withPrefix(custNation && { n_name: custNation.n_name }, "custNation_"),
      ...withPrefix(custRegion && { r_name: custRegion.r_name }, "custRegion_"),

      ...withPrefix(li && {
        l_orderkey: li.l_orderkey,
        l_quantity: li.l_quantity,
        l_extendedprice: li.l_extendedprice,
        l_discount: li.l_discount
      }, "lineitem_"),
    });
  }

  // 5) Infer column types
  const columnTypes = inferColumnTypes(joined);

  // 6) Cache + set state
  localStorage.setItem(
    TPC_H_CACHE_KEY,
    JSON.stringify({ preview: joined, columnTypes })
  );

  setDatasetPreview(joined);
  setColumnTypes(columnTypes);
  setIsLoading(false);
  };

  // ---- dispatcher
  const loadDataset = async (dataset: Dataset) => {
    if (dataset.files) return loadTpchDataset(dataset.files);
    if (dataset.file) return loadSingleCsvDataset(dataset.file);
  };

  const handleDatasetClick = (dataset: Dataset) => {
    setSelectedDatasetId(dataset.id);
    loadDataset(dataset);
  };

  // ---- constraints / aggregations helpers
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

  const buildPredicate = (agg: Aggregation): string =>
    agg.predicates
      .filter((p) => p.field && p.op && p.value)
      .map((p) => `${p.field} ${p.op} '${p.value}'`)
      .join(" AND ");

  const generateSQLQuery = () => {
    const selectedDataset = datasetConfig.find((d) => d.id === selectedDatasetId);
    const tableName =
      selectedDatasetId === "tpch"
        ? "tpch_join"
        : selectedDataset?.id || "uploaded";

    const whereConditions = constraints
      .filter((c) => c.field && c.op && c.value)
      .map((c) => `${c.field} ${c.op} '${c.value}'`);

    const whereClause =
      whereConditions.length > 0 ? `WHERE ${whereConditions.join(" AND ")}` : "";

    const query = `SELECT * FROM ${tableName} ${whereClause};`;

    console.log("Generated SQL Query:", query);
    console.log(
      "Defined Aggregations:",
      aggregations.map((a) => ({ ...a, predicate: buildPredicate(a) }))
    );
    console.log("Constraint Expression:", aggregateConstraintExpr);

    return query;
  };

  // ---------- Render ----------
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
            <Grid size={{xs:12, sm:4}} key={dataset.id}>
              <Card
                sx={{
                  backgroundColor: isSelected ? "rgba(64, 82, 181, 0.6)" : "grey.300",
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
            onChange={(e) => handleConstraintChange(index, "field", e.target.value)}
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
            onChange={(e) => handleConstraintChange(index, "op", e.target.value)}
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
            onChange={(e) => handleConstraintChange(index, "value", e.target.value)}
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
            <TextField label="Name" size="small" value={`agg${index + 1}`} disabled sx={{ width: 100 }} />
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
            <Box key={predIndex} display="flex" alignItems="center" gap={2} mt={1} ml={4}>
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
                  updated[index].predicates.push({ field: "", op: "", value: "" });
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
          "&:hover": { backgroundColor: "rgba(64, 82, 181, 1)" },
        }}
        onClick={() => {
          const query = generateSQLQuery();
          const selectedDataset = datasetConfig.find((d) => d.id === selectedDatasetId);

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
