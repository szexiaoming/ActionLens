import { conditionLabel, formatDuration } from "../domain/presentation";
import type { RunRecord } from "../types/evaluation";
import { StatusBadge } from "./StatusBadge";

export function RunTable({ runs }: { runs: RunRecord[] }) {
  if (runs.length === 0) return <div className="empty-state"><div className="empty-state__mark">0</div><h3>没有符合条件的运行记录</h3><p>调整筛选条件或清空筛选后再查看。</p></div>;
  return (
    <div className="table-wrap"><table><thead><tr><th>运行编号</th><th>任务</th><th>条件</th><th>Seed</th><th>控制步数</th><th>耗时</th><th>结果</th><th aria-label="详情" /></tr></thead>
      <tbody>{runs.map((run) => <tr key={run.runId}>
        <td><code>{run.runId}</code></td><td><strong>{run.task.name}</strong><small>{run.task.suite}</small></td>
        <td><span className={`condition-tag condition-tag--${run.condition.type}`}>{conditionLabel[run.condition.type]}</span></td>
        <td>{run.seed}</td><td>{run.result.executedSteps} / {run.result.maxSteps}</td><td>{formatDuration(run.result.durationSeconds)}</td>
        <td><StatusBadge status={run.result.status} /></td><td><a className="detail-link" href={`#/runs/${encodeURIComponent(run.runId)}`}>查看</a></td>
      </tr>)}</tbody></table></div>
  );
}
