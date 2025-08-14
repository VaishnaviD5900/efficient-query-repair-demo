import React from "react";
import { Alert, Snackbar } from "@mui/material";
import type { AlertColor } from "@mui/material";

type AppAlertProps = {
  open: boolean;
  message: string;
  severity?: AlertColor; // 'error' | 'warning' | 'info' | 'success'
  onClose: () => void;
  autoHideDuration?: number | null; // allow null = no auto-hide
};

export default function AppAlert({
  open,
  message,
  severity = "info",
  onClose,
  autoHideDuration = 3000,
}: AppAlertProps) {
  return (
    <Snackbar
      open={open}
      autoHideDuration={autoHideDuration ?? null}
      // ⬇️ don't close on clickaway (the initial click that triggered the alert)
      onClose={(_event, reason) => {
        if (reason === "clickaway") return;
        onClose();
      }}
      anchorOrigin={{ vertical: "top", horizontal: "right" }} // top-right
    >
      <Alert
        onClose={onClose}           // close icon still works
        severity={severity}
        variant="standard"          // light background
        sx={{ width: "100%" }}
      >
        {message}
      </Alert>
    </Snackbar>
  );
}
