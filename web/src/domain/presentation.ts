import type { RunStatus } from "../types/evaluation";

export const statusLabel: Record<RunStatus, string> = {
  success: "成功", failed: "失败", error: "异常", interrupted: "中断",
};
export const conditionLabel = { normal: "正常画面", disturbed: "亮度扰动" } as const;
export const failureLabel: Record<string, string> = {
  target_recognition: "目标识别", localization: "定位偏差", grasp: "抓取失败",
  placement: "放置失败", control: "控制异常", termination: "终止判断",
  perturbation: "扰动影响", system_error: "系统异常", unknown: "原因未知",
};
export const taskStageLabel: Record<string, string> = {
  initial: "初始阶段", recognition: "目标识别", approach: "接近目标", grasp: "抓取阶段",
  transport: "移动阶段", placement: "放置阶段", termination: "终止判断",
  completed: "任务完成", unknown: "无法判断",
};
export function formatDuration(seconds: number): string { return `${seconds.toFixed(1)} 秒`; }
export function formatTimestamp(timestamp: string): string {
  return new Intl.DateTimeFormat("zh-CN", {
    dateStyle: "medium", timeStyle: "short", timeZone: "UTC",
  }).format(new Date(timestamp));
}
