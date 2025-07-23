import React, { useState } from 'react';
import {
  Container,
  Box,
  Typography,
  Button,
  Paper,
  TextField,
  TableContainer,
  Table,
  TableHead,
  TableRow,
  TableCell,
  TableBody,
  Stack,
} from '@mui/material';
import Editor from '@monaco-editor/react';
import { useNavigate } from 'react-router-dom';

export default function QueryEditor() {
  const [query, setQuery] = useState('SELECT * FROM uploaded;');
  const [constraint, setConstraint] = useState('');
  const [csvData, setCsvData] = useState<string[][] | null>(null);
  const [fileName, setFileName] = useState<string | null>(null);

  const navigate = useNavigate();

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setFileName(file.name); // store file name

    const reader = new FileReader();
    reader.onload = (event) => {
      const text = event.target?.result as string;
      const rows = text.trim().split('\n').map((row) => row.split(','));
      setCsvData(rows);
    };
    reader.readAsText(file);
  };

  const handleSubmit = () => {
    console.log('Submit clicked', { query, constraint, csvData });
    navigate('/results');
  };

  return (
    <Container maxWidth="md" sx={{ py: 2 }}>
      <Typography variant="h4" fontWeight="bold" gutterBottom>
        SQL Query Repair
      </Typography>

      {/* Upload Dataset */}
      <Box mb={3}>
        <Typography variant="h6" gutterBottom>
          Upload Dataset
        </Typography>
        <Stack direction="row" alignItems="center" spacing={2}>
          <Button variant="outlined" component="label">
            Upload CSV File
            <input type="file" hidden accept=".csv" onChange={handleFileUpload} />
          </Button>
          {fileName && (
            <Typography variant="body2" color="text.secondary">
              {fileName}
            </Typography>
          )}
        </Stack>
      </Box>

      {/* Dataset Preview */}
      {csvData && (
        <Box mb={3}>
          <TableContainer component={Paper}>
            <Table size="small">
              <TableHead>
                <TableRow>
                  {csvData[0].map((header, i) => (
                    <TableCell key={i}>{header}</TableCell>
                  ))}
                </TableRow>
              </TableHead>
              <TableBody>
                {csvData.slice(1, 6).map((row, rowIndex) => (
                  <TableRow key={rowIndex}>
                    {row.map((cell, colIndex) => (
                      <TableCell key={colIndex}>{cell}</TableCell>
                    ))}
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
          <Typography variant="caption" color="text.secondary" mt={1} display="block">
            Showing first 5 rows
          </Typography>
        </Box>
      )}

      {/* Input SQL Query */}
      <Box mb={3}>
        <Typography variant="h6" gutterBottom>
          Input SQL Query
        </Typography>
        <Paper variant="outlined" sx={{ p: 1 }}>
          <Editor
            height="200px"
            defaultLanguage="sql"
            value={query}
            onChange={(val) => setQuery(val || '')}
            theme="vs-dark"
            options={{ fontSize: 14, minimap: { enabled: false } }}
          />
        </Paper>
      </Box>

      {/* Define Constraints */}
      <Box mb={3}>
        <Typography variant="h6" gutterBottom>
          Define Aggregate Constraints
        </Typography>
        <TextField
          fullWidth
          value={constraint}
          onChange={(e) => setConstraint(e.target.value)}
          placeholder="e.g., sum(salary) <= 100000"
          size="small"
        />
      </Box>

      {/* Submit Button */}
      <Box textAlign="right">
        <Button
          variant="contained"
          color="primary"
          onClick={handleSubmit}
        >
          Submit
        </Button>
      </Box>
    </Container>
  );
}
