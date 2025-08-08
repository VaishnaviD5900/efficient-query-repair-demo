import React from 'react';
import { Box, Typography, Link } from '@mui/material';

const Footer: React.FC = () => {
  return (
    <Box
      component="footer"
      sx={{
        // mt: 3,
        py: 3,
        textAlign: 'center',
        bgcolor: 'rgba(214, 214, 227, 0.1)',
      }}
    >
      <Typography variant="body2" color="text.secondary">
        © {new Date().getFullYear()} Query Repair System. Developed as part of an MSc Computer Science project at University of Southampton.
      </Typography>
    </Box>
  );
};

export default Footer;
