import { Box, Chip, Tooltip, Typography } from "@mui/material";
import type { Bounds } from "../../utils/constraints";
import {
  clamp, toPct,
  parseIntervalResult, computeStatusPoint, computeStatusInterval
} from "../../utils/constraints";

const passColor = (theme: any) => theme.palette.success.main;
const failColor = (theme: any) => theme.palette.error.main;
const warnColor = (theme: any) => theme.palette.warning.main;

function barDomainMax(value: number, b: Bounds): number {
  const candidates = [value, ...(b.lb != null ? [b.lb] : []), ...(b.ub != null && b.ub < 1 ? [b.ub] : []), 0.05];
  return Math.max(...candidates);
}

function MiniBar({ value, range, bounds }: { value?: number; range?: [number, number]; bounds: Bounds }) {
  const domain = barDomainMax(range ? range[1] : value ?? 0, bounds);
  const pos = (x: number) => `${clamp(x / domain, 0, 1) * 100}%`;

  return (
    <Box sx={{ position: "relative", width: 180, height: 8, borderRadius: 4, bgcolor: "grey.300" }}>
      {bounds.lb != null && bounds.lb <= domain && (
        // <Tooltip title={`Lower bound ${toPct(bounds.lb)}`}>
        <Tooltip title={`Lower bound ${bounds.lb}`}>
          <Box sx={{ position: "absolute", left: pos(bounds.lb), top: 0, bottom: 0, width: 2, bgcolor: "grey.600" }} />
        </Tooltip>
      )}
      {bounds.ub != null && bounds.ub <= domain && (
        // <Tooltip title={`Upper bound ${toPct(bounds.ub)}`}>
        <Tooltip title={`Upper bound ${bounds.ub}`}>
          <Box sx={{ position: "absolute", left: pos(bounds.ub), top: 0, bottom: 0, width: 2, bgcolor: "grey.600" }} />
        </Tooltip>
      )}
      {typeof value === "number" ? (
        <Box
          sx={{
            position: "absolute", left: pos(value), top: -3, width: 14, height: 14, borderRadius: "50%",
            bgcolor: (theme) => (computeStatusPoint(value, bounds) === "PASS" ? passColor(theme) : failColor(theme)),
            transform: "translateX(-50%)",
          }}
        />
      ) : range ? (
        <>
          <Box
            sx={{
              position: "absolute", left: pos(range[0]),
              width: `calc(${pos(range[1])} - ${pos(range[0])})`,
              top: 2, height: 4,
              bgcolor: (theme) => {
                const s = computeStatusInterval(range[0], range[1], bounds);
                return s === "PASS" ? passColor(theme) : s === "FAIL" ? failColor(theme) : warnColor(theme);
              },
              borderRadius: 2,
            }}
          />
          <Box sx={{ position: "absolute", left: pos(range[0]), top: -2, width: 8, height: 8, borderRadius: "50%", bgcolor: "grey.700", transform: "translateX(-50%)" }} />
          <Box sx={{ position: "absolute", left: pos(range[1]), top: -2, width: 8, height: 8, borderRadius: "50%", bgcolor: "grey.700", transform: "translateX(-50%)" }} />
        </>
      ) : null}
    </Box>
  );
}

function PointResult({ value, bounds }: { value: number; bounds: Bounds }) {
  if (!Number.isFinite(value)) return <span>—</span>;
  const status = computeStatusPoint(value, bounds);
  return (
    <Box display="flex" flexDirection="column" gap={0.5}>
      <Box display="flex" alignItems="center" gap={1}>
        <Typography variant="body2" sx={{ fontFamily: "monospace" }}>
          {/* {toPct(value)} */}
          {value}
        </Typography>
        <Chip size="small" label={status} color={status === "PASS" ? "success" : "error"} variant="outlined" />
      </Box>
      <MiniBar value={value} bounds={bounds} />
    </Box>
  );
}

function RangeResult({ lo, hi, bounds }: { lo: number; hi: number; bounds: Bounds }) {
  const status = computeStatusInterval(lo, hi, bounds);
  const chipColor = status === "PASS" ? "success" : status === "FAIL" ? "error" : "warning";
  return (
    <Box display="flex" flexDirection="column" gap={0.5}>
      <Box display="flex" alignItems="center" gap={1}>
        <Typography variant="body2" sx={{ fontFamily: "monospace" }}>
          {/* {toPct(lo)} - {toPct(hi)} */}
          {lo} - {hi}
        </Typography>
        <Chip size="small" label={status} color={chipColor as any} variant="outlined" />
      </Box>
      <MiniBar range={[lo, hi]} bounds={bounds} />
    </Box>
  );
}

export function ResultCell({ rawResult, bounds }: { rawResult: any; bounds: Bounds }) {
  const text = String(rawResult ?? "");
  const interval = parseIntervalResult(text);
  if (interval) return <RangeResult lo={interval[0]} hi={interval[1]} bounds={bounds} />;
  const num = Number(text);
  return <PointResult value={num} bounds={bounds} />;
}
