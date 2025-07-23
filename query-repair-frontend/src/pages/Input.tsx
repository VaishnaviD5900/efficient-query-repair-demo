import React, { useState } from 'react';
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
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import RemoveIcon from '@mui/icons-material/Remove';
import Papa from 'papaparse';
import DatasetPreview from '../features/DatasetPreview';
import DatasetSchema from '../features/DatasetSchema';

const datasetConfig = [
  {
    id: 'acs',
    name: 'ACS Income State',
    file: '/datasets/ACSIncome_state_number1 2(in).csv',
  },
  {
    id: 'healthcare',
    name: 'Healthcare 800',
    file: '/datasets/healthcare_800(in).csv',
  },
];

export default function InputPage() {
  const [selectedDatasetId, setSelectedDatasetId] = useState<string | null>(null);
  const [datasetPreview, setDatasetPreview] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [constraints, setConstraints] = useState([{ field: '', op: '', value: '' }]);
  const [aggregateConstraints, setAggregateConstraints] = useState([
    { field: '', value: '', aggOp: '', amount: '' },
  ]);

  const loadDataset = async (filePath: string) => {
    setIsLoading(true);
    const response = await fetch(filePath);
    const csv = await response.text();
    Papa.parse(csv, {
      header: true,
      skipEmptyLines: true,
      complete: (results) => {
        setDatasetPreview(results.data.slice(0, 5));
        setIsLoading(false);
      },
    });
  };

  const handleDatasetClick = (dataset: any) => {
    setSelectedDatasetId(dataset.id);
    loadDataset(dataset.file);
  };

  const handleConstraintChange = (
    index: number,
    key: 'field' | 'op' | 'value',
    value: string
  ) => {
    const updated = [...constraints];
    updated[index][key] = value;
    setConstraints(updated);
  };

  const handleAddConstraint = () => {
    setConstraints([...constraints, { field: '', op: '', value: '' }]);
  };

  const handleRemoveConstraint = (index: number) => {
    const updated = [...constraints];
    updated.splice(index, 1);
    setConstraints(updated);
  };

  const handleAggregateChange = (
    index: number,
    key: 'field' | 'value' | 'aggOp' | 'amount',
    value: string
  ) => {
    const updated = [...aggregateConstraints];
    updated[index][key] = value;
    setAggregateConstraints(updated);
  };

  const handleAddAggregate = () => {
    setAggregateConstraints([
      ...aggregateConstraints,
      { field: '', value: '', aggOp: '', amount: '' },
    ]);
  };

  const handleRemoveAggregate = (index: number) => {
    const updated = [...aggregateConstraints];
    updated.splice(index, 1);
    setAggregateConstraints(updated);
  };

  const columnOptions = datasetPreview.length > 0 ? Object.keys(datasetPreview[0]) : [];

  return (
    <Container maxWidth="lg" sx={{ pt: 4, pb: 8 }}>
      <Typography variant="h4" fontWeight="bold" gutterBottom>
        SQL Query Repair
      </Typography>

      <Typography variant="h6" gutterBottom>
        Select a Dataset
      </Typography>
      <Grid container spacing={2} mb={3}>
        {datasetConfig.map((dataset) => (
          <Grid size={{ xs: 12, sm: 4 }} key={dataset.id}>
            <Card
              sx={{
                backgroundColor:
                  dataset.id === selectedDatasetId ? 'primary.light' : 'grey.300',
              }}
            >
              <CardActionArea onClick={() => handleDatasetClick(dataset)}>
                <CardContent>
                  <Typography variant="h6" align="center">
                    {dataset.name}
                  </Typography>
                </CardContent>
              </CardActionArea>
            </Card>
          </Grid>
        ))}
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
            onChange={(e) => handleConstraintChange(index, 'field', e.target.value)}
            sx={{ minWidth: 210 }}
          >
            {columnOptions.map((col) => (
              <MenuItem key={col} value={col}>
                {col}
              </MenuItem>
            ))}
          </TextField>
          <TextField
            label="Op"
            size="small"
            value={constraint.op}
            onChange={(e) => handleConstraintChange(index, 'op', e.target.value)}
          />
          <TextField
            label="Value"
            size="small"
            value={constraint.value}
            onChange={(e) => handleConstraintChange(index, 'value', e.target.value)}
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
        Define Aggregate Constraints
      </Typography>
      {aggregateConstraints.map((agg, index) => (
        <Box key={index} display="flex" alignItems="center" gap={2} mb={2}>
          <TextField
            select
            label="Field"
            size="small"
            value={agg.field}
            onChange={(e) => handleAggregateChange(index, 'field', e.target.value)}
            sx={{ minWidth: 210 }}
          >
            {columnOptions.map((col) => (
              <MenuItem key={col} value={col}>
                {col}
              </MenuItem>
            ))}
          </TextField>
          <TextField
            label="="
            size="small"
            value={agg.value}
            onChange={(e) => handleAggregateChange(index, 'value', e.target.value)}
          />
          <Box display="flex" gap={1}>
            <TextField
              label="C-Op"
              size="small"
              value={agg.aggOp}
              onChange={(e) => handleAggregateChange(index, 'aggOp', e.target.value)}
              sx={{ width: 100 }}
            />
            <TextField
              label="Amount"
              size="small"
              value={agg.amount}
              onChange={(e) => handleAggregateChange(index, 'amount', e.target.value)}
              sx={{ width: 100 }}
            />
          </Box>
          <IconButton onClick={handleAddAggregate}>
            <AddIcon />
          </IconButton>
          {aggregateConstraints.length > 1 && (
            <IconButton onClick={() => handleRemoveAggregate(index)}>
              <RemoveIcon />
            </IconButton>
          )}
        </Box>
      ))}

      <Button variant="contained" color="primary" sx={{ mt: 3 }}>
        Run Repair
      </Button>
    </Container>
  );
}
