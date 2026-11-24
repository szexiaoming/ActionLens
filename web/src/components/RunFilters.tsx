import { conditionLabel, statusLabel } from "../domain/presentation";
import { hasActiveFilters, initialRunFilters, type RunFiltersState } from "../domain/filters";
import type { RunRecord, RunStatus } from "../types/evaluation";

interface Props { filters: RunFiltersState; onChange: (value: RunFiltersState) => void; runs: RunRecord[]; }

export function RunFilters({ filters, onChange, runs }: Props) {
  const tasks = Array.from(new Map(runs.map((run) => [run.task.id, run.task.name])).entries());
  const seeds = Array.from(new Set(runs.map((run) => run.seed))).sort((a, b) => a - b);
  const update = <K extends keyof RunFiltersState>(key: K, value: RunFiltersState[K]) =>
    onChange({ ...filters, [key]: value });

  return (
    <div className="filters" aria-label="运行记录筛选">
      <label><span>任务</span><select value={filters.taskId} onChange={(e) => update("taskId", e.target.value)}>
        <option value="all">全部任务</option>{tasks.map(([id, name]) => <option value={id} key={id}>{name}</option>)}
      </select></label>
      <label><span>画面条件</span><select value={filters.condition} onChange={(e) => update("condition", e.target.value as RunFiltersState["condition"])}>
        <option value="all">全部条件</option><option value="normal">{conditionLabel.normal}</option><option value="disturbed">{conditionLabel.disturbed}</option>
      </select></label>
      <label><span>运行状态</span><select value={filters.status} onChange={(e) => update("status", e.target.value as "all" | RunStatus)}>
        <option value="all">全部状态</option>{(Object.keys(statusLabel) as RunStatus[]).map((status) => <option value={status} key={status}>{statusLabel[status]}</option>)}
      </select></label>
      <label><span>随机种子</span><select value={filters.seed} onChange={(e) => update("seed", e.target.value)}>
        <option value="all">全部种子</option>{seeds.map((seed) => <option value={seed} key={seed}>Seed {seed}</option>)}
      </select></label>
      <label><span>视觉诊断</span><select value={filters.diagnosis} onChange={(e) => update("diagnosis", e.target.value as RunFiltersState["diagnosis"])}>
        <option value="all">全部记录</option><option value="present">已有诊断</option><option value="missing">诊断缺失</option>
      </select></label>
      <label><span>人工复核</span><select value={filters.review} onChange={(e) => update("review", e.target.value as RunFiltersState["review"])}>
        <option value="all">全部记录</option><option value="required">需要复核</option>
      </select></label>
      <button className="clear-button" disabled={!hasActiveFilters(filters)} onClick={() => onChange(initialRunFilters)}>清空筛选</button>
    </div>
  );
}
