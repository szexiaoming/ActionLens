import { DataManifestSchema, EvaluationSummarySchema, RunRecordsSchema, type EvaluationData } from "../types/evaluation";

async function fetchJson(path: string): Promise<unknown> {
  const response = await fetch(path);
  if (!response.ok) throw new Error(`请求 ${path} 失败，状态码 ${response.status}`);
  return response.json();
}

export async function loadEvaluationData(): Promise<EvaluationData> {
  const manifestResult = DataManifestSchema.safeParse(await fetchJson("/data/manifest.json"));
  if (!manifestResult.success) {
    const issue = manifestResult.error.issues[0];
    throw new Error(`数据清单格式错误：${issue.path.join(".") || "$"} ${issue.message}`);
  }
  const manifest = manifestResult.data;
  const [runsValue, summaryValue] = await Promise.all([
    fetchJson(manifest.runsPath), fetchJson(manifest.summaryPath),
  ]);
  const runsResult = RunRecordsSchema.safeParse(runsValue);
  if (!runsResult.success) {
    const issue = runsResult.error.issues[0];
    throw new Error(`运行数据格式错误：${issue.path.join(".") || "$"} ${issue.message}`);
  }
  const summaryResult = EvaluationSummarySchema.safeParse(summaryValue);
  if (!summaryResult.success) {
    const issue = summaryResult.error.issues[0];
    throw new Error(`汇总数据格式错误：${issue.path.join(".") || "$"} ${issue.message}`);
  }
  if (runsResult.data.length !== summaryResult.data.totalRuns) {
    throw new Error("运行记录数量与汇总数据不一致");
  }
  if (manifest.activeSource !== summaryResult.data.dataSource) {
    throw new Error("数据清单与汇总数据的数据来源不一致");
  }
  return { runs: runsResult.data, summary: summaryResult.data };
}
