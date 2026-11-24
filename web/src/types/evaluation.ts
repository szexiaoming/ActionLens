import { z } from "zod";

export const RunStatusSchema = z.enum(["success", "failed", "error", "interrupted"]);
export type RunStatus = z.infer<typeof RunStatusSchema>;

const DiagnosisSchema = z.object({
  targetVisible: z.boolean().nullable(),
  targetPosition: z.string().nullable(),
  taskStage: z.string(),
  suspectedFailureStage: z.string().nullable(),
  observations: z.array(z.string()),
  needsHumanReview: z.boolean(),
});

export const RunRecordSchema = z.object({
  schemaVersion: z.literal("1.0"),
  runId: z.string().regex(/^[A-Za-z0-9][A-Za-z0-9._-]*$/),
  dataSource: z.enum(["mock", "real"]),
  task: z.object({
    id: z.string(),
    name: z.string(),
    suite: z.string(),
    taskIndex: z.number().int().nonnegative(),
    instruction: z.string(),
  }),
  condition: z.object({
    type: z.enum(["normal", "disturbed"]),
    perturbation: z.record(z.string(), z.unknown()).nullable(),
  }),
  seed: z.number().int().nonnegative(),
  models: z.object({
    policy: z.string(),
    diagnoser: z.string().nullable(),
  }),
  result: z.object({
    status: RunStatusSchema,
    success: z.boolean(),
    terminationReason: z.string(),
    executedSteps: z.number().int().nonnegative(),
    maxSteps: z.number().int().positive(),
    durationSeconds: z.number().nonnegative(),
    averageInferenceMs: z.number().nonnegative().nullable(),
  }),
  artifacts: z.object({
    videoUrl: z.string().nullable(),
    startFrameUrl: z.string().nullable(),
    middleFrameUrl: z.string().nullable(),
    endFrameUrl: z.string().nullable(),
  }),
  diagnosis: DiagnosisSchema.nullable(),
  humanReview: z.object({
    reviewed: z.boolean(),
    failureCategory: z.string().nullable(),
    comment: z.string().nullable(),
  }),
  createdAt: z.string(),
});

export const RunRecordsSchema = z.array(RunRecordSchema);
export type RunRecord = z.infer<typeof RunRecordSchema>;

const GroupSummarySchema = z.object({
  key: z.union([z.string(), z.array(z.string())]),
  totalRuns: z.number(),
  successCount: z.number(),
  successRate: z.number(),
  statusCounts: z.record(z.string(), z.number()),
  name: z.string().optional(),
});

export const EvaluationSummarySchema = z.object({
  schemaVersion: z.literal("1.0"),
  dataSource: z.enum(["mock", "real"]),
  generatedAt: z.string(),
  totalRuns: z.number(),
  statusCounts: z.object({
    success: z.number(), failed: z.number(), error: z.number(), interrupted: z.number(),
  }),
  success: z.object({ count: z.number(), total: z.number(), rate: z.number() }),
  metrics: z.object({
    averageDurationSeconds: z.number(), averageSuccessfulSteps: z.number(),
  }),
  byTask: z.array(GroupSummarySchema),
  byCondition: z.array(GroupSummarySchema),
  byTaskAndCondition: z.array(GroupSummarySchema),
  failureCategories: z.record(z.string(), z.number()),
  dataQuality: z.object({
    withDiagnosis: z.number(), needsHumanReview: z.number(), missingVideo: z.number(),
  }),
});

export type EvaluationSummary = z.infer<typeof EvaluationSummarySchema>;
export const DataManifestSchema = z.object({
  schemaVersion: z.literal("1.0"),
  activeSource: z.enum(["mock", "real"]),
  runsPath: z.string().startsWith("/"),
  summaryPath: z.string().startsWith("/"),
  updatedAt: z.string(),
});
export interface EvaluationData { runs: RunRecord[]; summary: EvaluationSummary; }
