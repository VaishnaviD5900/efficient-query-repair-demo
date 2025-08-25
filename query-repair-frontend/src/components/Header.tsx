import React from 'react';
import { AppBar, Toolbar, Typography, IconButton, Tooltip } from '@mui/material';
import HomeIcon from "@mui/icons-material/Home";
import { Link, useLocation } from "react-router-dom";

export default function Header() {
  const location = useLocation();
  const showHome = location.pathname.startsWith("/results");
  return (
    <AppBar position="fixed"
    sx={{ backgroundColor: 'rgba(64, 82, 181, 0.6)', backdropFilter: 'blur(6px)' }}
    >
      <Toolbar>
        {/* App title */}
        <Typography variant="h6" color="inherit" sx={{ flexGrow: 1 }}>
          Query Repair System
        </Typography>
        {showHome && (
          <Tooltip title="Home">
            <IconButton
              edge="end"
              color="inherit"
              component={Link}
              to="/"
              aria-label="home"
              size="large"
            >
              <HomeIcon />
            </IconButton>
          </Tooltip>
        )}
      </Toolbar>
    </AppBar>
  );
}
