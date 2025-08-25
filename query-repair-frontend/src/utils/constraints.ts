export type Bounds = { lb: number | null; ub: number | null };

export function parseConstraintBounds(raw?: string): Bounds {
  const s = String(raw ?? "").trim();
  const nums = (s.match(/-?\d+(?:\.\d+)?/g) || []).map(Number);
  if (nums.length >= 2) return { lb: nums[0], ub: nums[1] };
  if (nums.length === 1) {
    if (/\<=|≤/.test(s)) return { lb: 0, ub: nums[0] };
    if (/\>=|≥/.test(s)) return { lb: nums[0], ub: null };
    return { lb: 0, ub: nums[0] };
  }
  return { lb: 0, ub: 0.02 };
}

export const clamp = (v: number, lo = 0, hi = 1) => Math.max(lo, Math.min(hi, v));
export const toPct = (v: number) => `${(v * 100).toFixed(2)}%`;

export function parseIntervalResult(raw: string): [number, number] | null {
  const m = raw.match(/-?\d+(?:\.\d+)?/g);
  if (!m || m.length < 2) return null;
  const lo = Number(m[0]), hi = Number(m[1]);
  return Number.isFinite(lo) && Number.isFinite(hi) ? [lo, hi] : null;
}

export function computeStatusPoint(v: number, b: Bounds): "PASS" | "FAIL" {
  const lbOk = b.lb == null || v >= b.lb!;
  const ubOk = b.ub == null || v <= b.ub!;
  return lbOk && ubOk ? "PASS" : "FAIL";
}

export function computeStatusInterval(
  lo: number,
  hi: number,
  b: Bounds
): "PASS" | "FAIL" | "INCONCLUSIVE" {
  const definitelyBelow = b.lb != null && hi < b.lb!;
  const definitelyAbove = b.ub != null && lo > b.ub!;
  const definitelyInside = (b.lb == null || lo >= b.lb!) && (b.ub == null || hi <= b.ub!);
  if (definitelyInside) return "PASS";
  if (definitelyBelow || definitelyAbove) return "FAIL";
  return "INCONCLUSIVE";
}
