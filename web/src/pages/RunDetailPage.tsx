import { StatusBadge } from "../components/StatusBadge";
import { conditionLabel, failureLabel, formatDuration, formatTimestamp, taskStageLabel } from "../domain/presentation";
import type { RunRecord } from "../types/evaluation";

function MediaPlaceholder({ label }: { label: string }) {
  return <div className="media-placeholder"><div className="media-placeholder__robot" aria-hidden="true"><i /><i /><i /></div><strong>{label}</strong><span>等待 GPU 阶段生成真实素材</span></div>;
}

export function RunDetailPage({ run }: { run?: RunRecord }) {
  if (!run) return <section className="state-panel"><p className="eyebrow">记录不存在</p><h1>找不到这次运行</h1><p>链接中的运行编号可能不正确，或数据文件已经更新。</p><a className="primary-button" href="#/">返回实验总览</a></section>;
  const frames = [["开始画面", run.artifacts.startFrameUrl], ["中间画面", run.artifacts.middleFrameUrl], ["结束画面", run.artifacts.endFrameUrl]] as const;
  return <>
    <a className="back-link" href="#/runs">返回运行列表</a>
    <header className="detail-header"><div><p className="eyebrow">{run.runId}</p><h1>{run.task.name}</h1><p>{run.task.instruction}</p></div><StatusBadge status={run.result.status} /></header>
    <div className="detail-grid">
      <section className="panel video-panel" aria-labelledby="video-title"><div className="panel__heading"><div><p className="eyebrow">Episode video</p><h2 id="video-title">完整运行视频</h2></div><span className="data-badge">{run.dataSource === "mock" ? "模拟记录" : "真实记录"}</span></div>{run.artifacts.videoUrl ? <video controls src={run.artifacts.videoUrl} aria-label="机器人运行视频" /> : <MediaPlaceholder label="视频尚未生成" />}</section>
      <aside className="panel metadata-panel" aria-labelledby="metadata-title"><p className="eyebrow">Run metadata</p><h2 id="metadata-title">运行信息</h2><dl>
        <div><dt>任务套件</dt><dd>{run.task.suite} / #{run.task.taskIndex}</dd></div><div><dt>画面条件</dt><dd>{conditionLabel[run.condition.type]}</dd></div><div><dt>随机种子</dt><dd>{run.seed}</dd></div><div><dt>控制步数</dt><dd>{run.result.executedSteps} / {run.result.maxSteps}</dd></div><div><dt>运行耗时</dt><dd>{formatDuration(run.result.durationSeconds)}</dd></div><div><dt>终止原因</dt><dd><code>{run.result.terminationReason}</code></dd></div><div><dt>动作策略</dt><dd>{run.models.policy}</dd></div><div><dt>记录时间</dt><dd>{formatTimestamp(run.createdAt)}</dd></div>
      </dl></aside>
    </div>
    <section className="panel keyframes-panel" aria-labelledby="keyframes-title"><div className="panel__heading"><div><p className="eyebrow">Keyframes</p><h2 id="keyframes-title">关键画面</h2></div><span className="panel__meta">开始 / 中间 / 结束</span></div><div className="keyframe-grid">{frames.map(([label, url]) => <article key={label}>{url ? <img src={url} alt={label} /> : <MediaPlaceholder label={label} />}</article>)}</div></section>
    <div className="diagnosis-grid">
      <section className="panel diagnosis-panel" aria-labelledby="diagnosis-title"><p className="eyebrow">VLM diagnosis</p><h2 id="diagnosis-title">视觉诊断</h2>{run.diagnosis ? <>
        <div className="diagnosis-facts"><div><span>目标可见</span><strong>{run.diagnosis.targetVisible === null ? "未知" : run.diagnosis.targetVisible ? "是" : "否"}</strong></div><div><span>目标位置</span><strong>{run.diagnosis.targetPosition ?? "未知"}</strong></div><div><span>任务阶段</span><strong>{taskStageLabel[run.diagnosis.taskStage] ?? run.diagnosis.taskStage}</strong></div><div><span>疑似失败阶段</span><strong>{run.diagnosis.suspectedFailureStage ? taskStageLabel[run.diagnosis.suspectedFailureStage] ?? run.diagnosis.suspectedFailureStage : "无"}</strong></div></div>
        <ul className="observation-list">{run.diagnosis.observations.map((item) => <li key={item}>{item}</li>)}</ul>{run.diagnosis.needsHumanReview && <div className="review-alert">该诊断需要人工复核</div>}
      </> : <div className="inline-empty"><strong>视觉诊断缺失</strong><p>本次记录没有可解析的诊断结果，页面保留该状态供后续检查。</p></div>}</section>
      <section className="panel human-panel" aria-labelledby="human-title"><p className="eyebrow">Human review</p><h2 id="human-title">人工复核</h2><div className="human-status"><span>{run.humanReview.reviewed ? "已复核" : "未复核"}</span></div><dl><div><dt>失败分类</dt><dd>{run.humanReview.failureCategory ? failureLabel[run.humanReview.failureCategory] ?? run.humanReview.failureCategory : "不适用"}</dd></div><div><dt>复核意见</dt><dd>{run.humanReview.comment ?? "本次成功记录暂不需要人工补充意见。"}</dd></div></dl></section>
    </div>
  </>;
}
