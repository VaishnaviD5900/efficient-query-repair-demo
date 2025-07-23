import React from 'react';
import { AppBar, Toolbar, Typography, IconButton, Box } from '@mui/material';

export default function Header() {
  return (
    <AppBar position="fixed">
      <Toolbar>
        {/* Home button */}
        {/* <IconButton edge="start" color="inherit" aria-label="home" sx={{ mr: 2 }}>
          <HomeIcon />
        </IconButton> */}

        {/* App title */}
        <Typography variant="h6" color="inherit" sx={{ flexGrow: 1 }}>
          Query Repair System
        </Typography>

        {/* Right-side actions (e.g., settings) */}
        {/* <Box>
          <IconButton color="inherit" aria-label="settings">
            <SettingsIcon />
          </IconButton>
        </Box> */}
      </Toolbar>
    </AppBar>
  );
}
