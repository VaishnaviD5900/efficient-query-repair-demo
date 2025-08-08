import React from 'react';
import { AppBar, Toolbar, Typography, IconButton, Box } from '@mui/material';

export default function Header() {
  return (
    <AppBar position="fixed"
    sx={{ backgroundColor: 'rgba(64, 82, 181, 0.6)', backdropFilter: 'blur(6px)' }}
    >
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
