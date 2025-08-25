export function rewriteQueryWithVector(originalSql: string, vectorText: string): string {
  if (!originalSql) return "";
  const nums = vectorText.match(/-?\d+(?:\.\d+)?/g) || [];
  if (!nums.length) return originalSql;

  let i = 0;
  const re = /(\b[A-Za-z_][A-Za-z0-9_]*\b\s*(?:>=|<=|==|=|>|<)\s*)(['"]?)(-?\d+(?:\.\d+)?)(['"]?)/g;

  return originalSql.replace(re, (full, left, ql, _oldNum, qr) => {
    if (i >= nums.length) return full;
    const q = ql && ql === qr ? ql : "";
    const next = nums[i++];
    return `${left}${q}${next}${q}`;
  });
}

const normOp = (op: string) => (op === "==" ? "=" : op);
const normCol = (c: string) => c.trim().toUpperCase();
const token = (col: string, op: string) => `${normCol(col)}:${normOp(op)}`;

export function signatureFromSql(sql: string): string {
  if (!sql) return "";
  const re = /([A-Za-z_][A-Za-z0-9_.]*)\s*(>=|<=|==|=|>|<)\s*['"]?-?\d+(?:\.\d+)?['"]?/gi;
  const toks: string[] = []; let m: RegExpExecArray | null;
  while ((m = re.exec(sql)) !== null) toks.push(token(m[1], m[2]));
  return toks.sort().join("|");
}

export function signatureFromRunInfo(qstr: string): string {
  if (!qstr) return "";
  try {
    const json = JSON.parse(qstr.replace(/'/g, '"'));
    if (Array.isArray(json)) {
      const toks = json
        .filter((e: any) => Array.isArray(e) && e.length >= 2)
        .map((e: any[]) => token(String(e[0]), String(e[1])));
      return toks.sort().join("|");
    }
  } catch {}
  const re = /\[\s*['"]([^'"]+)['"]\s*,\s*['"]([^'"]+)['"]/g;
  const toks: string[] = []; let m: RegExpExecArray | null;
  while ((m = re.exec(qstr)) !== null) toks.push(token(m[1], m[2]));
  return toks.sort().join("|");
}

// --- Similarity helpers used by SimilarityCell ---
type Pred = { column: string; op: string; rhs: number | null };

export function parsePredicatesWithRhs(sql: string): Pred[] {
  const preds: Pred[] = [];
  if (!sql) return preds;
  const re = /([A-Za-z_][A-Za-z0-9_]*)\s*(>=|<=|==|=|>|<)\s*'?(-?\d+(?:\.\d+)?)'?/g;
  let m: RegExpExecArray | null;
  while ((m = re.exec(sql)) !== null) {
    const col = m[1];
    const op = m[2] === "==" ? "=" : m[2];
    const rhs = Number(m[3]);
    preds.push({ column: col, op, rhs: Number.isFinite(rhs) ? rhs : null });
  }
  return preds;
}

export const parseVectorNums = (text: string) => (text.match(/-?\d+(?:\.\d+)?/g) || []).map(Number);
