import type { RunRecord, RunStatus } from "../types/evaluation";

export interface RunFiltersState {
  taskId: string;
  condition: "all" | "normal" | "disturbed";
  status: "all" | RunStatus;
  seed: string;
  diagnosis: "all" | "present" | "missing";
  review: "all" | "required";
}

export const initialRunFilters: RunFiltersState = {
  taskId: "all", condition: "all", status: "all", seed: "all", diagnosis: "all", review: "all",
};

export function applyRunFilters(runs: RunRecord[], filters: RunFiltersState): RunRecord[] {
  return runs.filter((run) => {
    if (filters.taskId !== "all" && run.task.id !== filters.taskId) return false;
    if (filters.condition !== "all" && run.condition.type !== filters.condition) return false;
    if (filters.status !== "all" && run.result.status !== filters.status) return false;
    if (filters.seed !== "all" && run.seed !== Number(filters.seed)) return false;
    if (filters.diagnosis === "present" && run.diagnosis === null) return false;
    if (filters.diagnosis === "missing" && run.diagnosis !== null) return false;
    if (filters.review === "required" && !run.diagnosis?.needsHumanReview) return false;
    return true;
  });
}

export function hasActiveFilters(filters: RunFiltersState): boolean {
  return Object.values(filters).some((value) => value !== "all");
}
