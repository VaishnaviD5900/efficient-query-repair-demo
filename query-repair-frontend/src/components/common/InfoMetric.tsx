import { Box, Tooltip } from "@mui/material";
import InfoOutlined from "@mui/icons-material/InfoOutlined";

export function InfoIcon({ title }: { title: string }) {
  return (
    <Tooltip title={title}>
      <InfoOutlined
        fontSize="small"
        sx={{ ml: 0.5, color: "text.secondary", cursor: "help", verticalAlign: "text-bottom" }}
      />
    </Tooltip>
  );
}

export function MetricLabel({ label, info }: { label: string; info: string }) {
  return (
    <Box component="span" sx={{ display: "inline-flex", alignItems: "center" }}>
      <span>{label}</span>
      <InfoIcon title={info} />
    </Box>
  );
}
