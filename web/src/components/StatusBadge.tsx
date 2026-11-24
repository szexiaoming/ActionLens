import { statusLabel } from "../domain/presentation";
import type { RunStatus } from "../types/evaluation";

export function StatusBadge({ status }: { status: RunStatus }) {
  return <span className={`status-badge status-badge--${status}`}>{statusLabel[status]}</span>;
}
