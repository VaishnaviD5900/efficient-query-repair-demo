export type Bounds = { lb: number | null; ub: number | null };

export function parseConstraintBounds(raw?: string): Bounds {
  const s = String(raw ?? "").trim();
  if (!s) return { lb: null, ub: null };

  // Case 1: "[lb, ub]"
  const arr = s.match(/^\s*\[\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)\s*,\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)\s*\]\s*$/);
  if (arr) return { lb: Number(arr[1]), ub: Number(arr[2]) };

  // Case 2: "lb <= ... <= ub" (supports < or <= and unicode ≤; also scientific notation)
  const m = s.match(
    /([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)\s*(?:<=|<|≤)\s*.+?\s*(?:<=|<|≤)\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)/,
  );
  if (m) return { lb: Number(m[1]), ub: Number(m[2]) };

  // Fallback: first and last number if the format is unusual (keeps UI from breaking)
  const nums = s.match(/-?\d*\.?\d+(?:[eE][-+]?\d+)?/g);
  if (nums && nums.length >= 2) {
    return { lb: Number(nums[0]), ub: Number(nums[nums.length - 1]) };
  }
  return { lb: null, ub: null };
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
