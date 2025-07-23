import React from 'react';
import { Box, Typography, Link } from '@mui/material';

const Footer: React.FC = () => {
  return (
    <Box
      component="footer"
      sx={{
        mt: 3,
        py: 3,
        textAlign: 'center',
        bgcolor: 'background.paper',
      }}
    >
      <Typography variant="body2" color="text.secondary">
        © {new Date().getFullYear()} Query Repair System. Developed as part of an MSc Computer Science project at University of Southampton
        {/* {' '}
        <Link href="https://www.southampton.ac.uk" target="_blank" rel="noopener noreferrer">
          University of Southampton
        </Link> */}
        .
      </Typography>
    </Box>
  );
};

export default Footer;
