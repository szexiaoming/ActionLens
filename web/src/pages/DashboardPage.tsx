import { useMemo, useState } from "react";
import { RunFilters } from "../components/RunFilters";
import { RunTable } from "../components/RunTable";
import { SummaryPanel } from "../components/SummaryPanel";
import { applyRunFilters, initialRunFilters } from "../domain/filters";
import type { EvaluationSummary, RunRecord } from "../types/evaluation";

export function DashboardPage({ runs, summary }: { runs: RunRecord[]; summary: EvaluationSummary }) {
  const [filters, setFilters] = useState(initialRunFilters);
  const filteredRuns = useMemo(() => applyRunFilters(runs, filters), [runs, filters]);
  return <>
    <header className="page-header"><div><p className="eyebrow">Evaluation dashboard</p><h1>实验总览</h1><p>检查每一次运行，而不只展示一个成功演示。</p></div><div className="header-note"><strong>{summary.totalRuns} 条{summary.dataSource === "mock" ? "模拟" : "真实"}记录</strong><span>数据结构已通过 Schema 校验</span></div></header>
    {summary.dataSource === "mock" ? <div className="mock-notice" role="note"><strong>当前为模拟数据。</strong> 页面功能和统计流程可用，但结果不能代表 SmolVLA 的真实表现。</div> : <div className="real-notice" role="note"><strong>当前为真实评测数据。</strong> 成功状态来自仿真环境，VLM 结果仅用于辅助诊断。</div>}
    <SummaryPanel summary={summary} />
    <section className="runs-section" id="runs" aria-labelledby="runs-title">
      <div className="section-heading"><div><p className="eyebrow">Run explorer</p><h2 id="runs-title">运行记录</h2></div><p>显示 {filteredRuns.length} / {runs.length} 条记录</p></div>
      <RunFilters filters={filters} onChange={setFilters} runs={runs} />
      <RunTable runs={filteredRuns} />
    </section>
  </>;
}
