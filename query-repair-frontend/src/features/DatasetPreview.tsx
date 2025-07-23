import React from 'react';
import {
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
} from '@mui/material';

interface DatasetPreviewProps {
  data: Record<string, any>[];
}

const DatasetPreview: React.FC<DatasetPreviewProps> = ({ data }) => {
  if (data.length === 0) return null;

  return (
    <>
      <Typography variant="h6" gutterBottom>
        Dataset Preview
      </Typography>
      <TableContainer component={Paper} sx={{ mb: 4 }}>
        <Table size="small">
          <TableHead>
            <TableRow>
              {Object.keys(data[0]).map((key) => (
                <TableCell key={key} sx={{ fontWeight: 'bold' }}>
                  {key}
                </TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {data.map((row, idx) => (
              <TableRow key={idx}>
                {Object.values(row).map((value, i) => (
                  <TableCell key={i}>{String(value)}</TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </>
  );
};

export default DatasetPreview;
