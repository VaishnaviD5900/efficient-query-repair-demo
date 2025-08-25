import { Box, LinearProgress, Typography } from "@mui/material";
import { MetricLabel } from "./InfoMetric";

type StatBarProps = {
  label: string;
  info: string;
  value?: React.ReactNode;
  progress?: number;          // 0-100
  color?: "primary" | "secondary";
  mb?: number;                // bottom margin (default 2)
};

export function StatBar({
  label,
  info,
  value,
  progress = 0,
  color = "primary",
  mb = 1,
}: StatBarProps) {
  const pct = Math.max(0, Math.min(100, Number(progress) || 0));
  return (
    <Box sx={{ mb }}>
      <Typography variant="body2" sx={{ mb: 0.5 }}>
        <MetricLabel label={label} info={info} />{value !== undefined ? <>: {value}</> : null}
      </Typography>
      <LinearProgress variant="determinate" value={pct} color={color} />
    </Box>
  );
}
