import { describe, expect, it } from "vitest";
import runsValue from "../../public/data/runs.json";
import { RunRecordsSchema } from "../types/evaluation";
import { applyRunFilters, initialRunFilters } from "./filters";

const runs = RunRecordsSchema.parse(runsValue);

describe("applyRunFilters", () => {
  it("combines task, condition, and status filters", () => {
    const result = applyRunFilters(runs, {
      ...initialRunFilters,
      taskId: "task-a",
      condition: "disturbed",
      status: "failed",
    });
    expect(result).toHaveLength(5);
  });

  it("finds all records with a missing diagnosis", () => {
    const result = applyRunFilters(runs, {
      ...initialRunFilters,
      diagnosis: "missing",
    });
    expect(result).toHaveLength(3);
  });

  it("finds diagnoses requiring human review", () => {
    const result = applyRunFilters(runs, {
      ...initialRunFilters,
      review: "required",
    });
    expect(result).toHaveLength(13);
  });
});
