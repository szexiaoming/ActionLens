# ActionLens 运行数据格式

模拟记录和真实评测记录使用同一份 `schemas/run.schema.json`。统一格式使 React 页面不依赖仿真器和模型的内部数据结构。

## 核心约束

- `schemaVersion` 当前固定为 `1.0`；
- `runId` 必须唯一，只能包含字母、数字、点、下划线和连字符；
- `dataSource` 必须是 `mock` 或 `real`；
- 只有仿真环境可以决定 `result.success`；
- `result.success` 只在 `result.status` 为 `success` 时为真；
- `executedSteps` 不能超过 `maxSteps`；
- 正常条件的 `perturbation` 必须为 `null`；
- 扰动条件必须记录扰动配置；
- VLM 诊断不替代成功判定；
- 缺失的视频、关键帧或诊断使用 `null`；
- 时间使用 ISO 8601 UTC 字符串。

## 结果状态

| 状态 | 含义 |
|---|---|
| `success` | 仿真环境确认任务成功 |
| `failed` | 回合结束但未成功 |
| `error` | 环境、模型或保存流程异常 |
| `interrupted` | 回合被主动中断 |

异常和中断会单独统计，不会合并为普通失败。

## 数据清单

前端首先读取 `web/public/data/manifest.json`：

```json
{
  "schemaVersion": "1.0",
  "activeSource": "mock",
  "runsPath": "/data/runs.json",
  "summaryPath": "/data/summary.json",
  "updatedAt": "2026-11-24T10:39:00Z"
}
```

`activeSource` 必须与汇总文件中的 `dataSource` 一致，否则页面拒绝加载。

## 生成和校验

```powershell
.\.venv\Scripts\python.exe scripts\generate_mock_data.py
.\.venv\Scripts\python.exe scripts\validate_results.py
```

模拟生成器使用固定任务矩阵、状态分布和时间戳，多次执行产生相同数据。校验错误会包含字段路径，例如 `$[0].result.status`。
