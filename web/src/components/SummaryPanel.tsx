import { formatDuration } from "../domain/presentation";
import type { EvaluationSummary } from "../types/evaluation";

export function SummaryPanel({ summary }: { summary: EvaluationSummary }) {
  const normal = summary.byCondition.find((item) => item.key === "normal");
  const disturbed = summary.byCondition.find((item) => item.key === "disturbed");
  return <>
    <section className="metric-grid" aria-label="实验核心指标">
      <article className="metric-card"><span>全部运行</span><strong>{summary.totalRuns}</strong><small>2 个任务 · 2 种条件</small></article>
      <article className="metric-card metric-card--success"><span>成功次数</span><strong>{summary.success.count}<small> / {summary.success.total}</small></strong><small>模拟成功率 {(summary.success.rate * 100).toFixed(0)}%</small></article>
      <article className="metric-card metric-card--failed"><span>失败次数</span><strong>{summary.statusCounts.failed}</strong><small>另有 {summary.statusCounts.error} 次异常，{summary.statusCounts.interrupted} 次中断</small></article>
      <article className="metric-card"><span>平均运行耗时</span><strong>{formatDuration(summary.metrics.averageDurationSeconds)}</strong><small>成功回合平均 {summary.metrics.averageSuccessfulSteps.toFixed(0)} 步</small></article>
    </section>
    <section className="analysis-grid">
      <article className="panel task-comparison">
        <div className="panel__heading"><div><p className="eyebrow">任务对比</p><h2>正常画面与亮度扰动</h2></div><span className="panel__meta">成功次数 / 总次数</span></div>
        <div className="comparison-list">{summary.byTask.map((task) => {
          const normalItem = summary.byTaskAndCondition.find((item) => Array.isArray(item.key) && item.key[0] === task.key && item.key[1] === "normal");
          const disturbedItem = summary.byTaskAndCondition.find((item) => Array.isArray(item.key) && item.key[0] === task.key && item.key[1] === "disturbed");
          return <div className="comparison-row" key={String(task.key)}>
            <div className="comparison-row__label"><strong>{task.name}</strong><small>{task.successCount} / {task.totalRuns} 总体成功</small></div>
            <div className="bar-group">
              <div className="bar-line"><span>正常</span><div className="bar-track"><i style={{ width: `${(normalItem?.successRate ?? 0) * 100}%` }} /></div><strong>{normalItem?.successCount} / {normalItem?.totalRuns}</strong></div>
              <div className="bar-line bar-line--disturbed"><span>扰动</span><div className="bar-track"><i style={{ width: `${(disturbedItem?.successRate ?? 0) * 100}%` }} /></div><strong>{disturbedItem?.successCount} / {disturbedItem?.totalRuns}</strong></div>
            </div>
          </div>;
        })}</div>
      </article>
      <article className="panel condition-impact">
        <p className="eyebrow">条件影响</p><h2>扰动后少成功</h2>
        <div className="impact-number">{(normal?.successCount ?? 0) - (disturbed?.successCount ?? 0)}<span>次</span></div>
        <p>相同的 20 次计划运行中，正常画面成功 {normal?.successCount} 次，亮度扰动成功 {disturbed?.successCount} 次。</p>
        <div className="stacked-bar" aria-label="运行状态分布"><i className="stacked-bar__success" style={{ width: `${summary.success.rate * 100}%` }} /><i className="stacked-bar__failed" style={{ width: `${summary.statusCounts.failed / summary.totalRuns * 100}%` }} /><i className="stacked-bar__other" /></div>
        <div className="legend"><span><i className="legend__success" />成功 {summary.statusCounts.success}</span><span><i className="legend__failed" />失败 {summary.statusCounts.failed}</span><span><i className="legend__other" />异常/中断 {summary.statusCounts.error + summary.statusCounts.interrupted}</span></div>
      </article>
    </section>
  </>;
}
