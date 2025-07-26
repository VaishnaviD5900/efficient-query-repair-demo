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
} from '@mui/material';
import { CheckCircle, Cancel } from '@mui/icons-material';

export default function ResultsPage() {
  const datasetInfo = {
    name: 'Products',
    size: 1000,
    columns: 5,
  };

  const constraint = {
    type: 'SPD',
    threshold: 0.2,
    actual: 0.35,
    satisfied: false,
  };

  return (
    <Container maxWidth="md" sx={{ mt: 4 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h5">Results</Typography>
        <Button variant="contained">Export</Button>
      </Box>

      <Typography variant="body2" color="text.secondary" gutterBottom>
        Dataset: <strong>{datasetInfo.name}</strong>, Size: {datasetInfo.size} rows, Columns: {datasetInfo.columns}
      </Typography>

      <Paper variant="outlined" sx={{ p: 2, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Original Query & Constraint Status
        </Typography>

        <Typography variant="subtitle2">Original Query</Typography>
        <Paper variant="outlined" sx={{ p: 1, my: 1, minHeight: 60 }}>
          <Typography variant="body2" color="text.secondary">-- SQL query goes here --</Typography>
        </Paper>

        <Grid container spacing={2}>
          <Grid size={{xs:6}}>
            <Typography variant="body2">
              <strong>Constraint</strong>: {constraint.type} ≤ {constraint.threshold}
            </Typography>
          </Grid>
          <Grid size={{xs:6}}>
            <Typography variant="body2">
              <strong>Constraint Status</strong>: {constraint.actual}
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

      {['Runtime (s)', 'NCE', 'NCA', 'Search Space (%)'].map((metric) => (
        <Box key={metric} sx={{ mb: 2 }}>
          <Typography variant="body2" mb={0.5}>{metric} - FF</Typography>
          <LinearProgress variant="determinate" value={70} />
          <Typography variant="body2" mt={0.5}>{metric} - RP</Typography>
          <LinearProgress variant="determinate" value={20} color="secondary" />
        </Box>
      ))}

      <Divider sx={{ my: 3 }} />

      <Typography variant="h6" gutterBottom>
        Algorithm Efficiency Summary
      </Typography>
      <Typography variant="body2" color="text.secondary">
        Range Pruning (RP) achieved the same top-k repairs as Full Filtering (FF), while exploring only 20% of the
        search space compared to FF's 60% and running 3x faster.
      </Typography>
    </Container>
  );
}
