"""Deterministic mock records used before GPU evaluation is available."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence


FAILURE_STAGE = {
    "target_recognition": "recognition",
    "localization": "approach",
    "grasp": "grasp",
    "placement": "placement",
    "control": "transport",
    "termination": "termination",
    "perturbation": "recognition",
    "system_error": "unknown",
    "unknown": "unknown",
}

FAILURE_COMMENT = {
    "target_recognition": "模拟复核：策略朝错误目标移动。",
    "localization": "模拟复核：末端执行器与目标位置存在偏差。",
    "grasp": "模拟复核：夹爪到达目标附近但未稳定抓取。",
    "placement": "模拟复核：物体未被放入目标区域。",
    "control": "模拟复核：动作出现重复或轨迹振荡。",
    "termination": "模拟复核：画面接近完成，但环境未返回成功。",
    "perturbation": "模拟复核：亮度扰动后目标判断发生退化。",
    "system_error": "模拟复核：运行过程发生系统异常。",
    "unknown": "模拟复核：运行被中断，现有证据不足。",
}


def _load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as file:
        return json.load(file)


def _outcome(task_id: str, condition: str, seed: int) -> str:
    if task_id == "task-a" and condition == "normal":
        return "success" if seed <= 6 else "failed" if seed <= 8 else "error"
    if task_id == "task-a" and condition == "disturbed":
        return "success" if seed <= 3 else "failed" if seed <= 8 else "interrupted"
    if task_id == "task-b" and condition == "normal":
        return "success" if seed <= 7 else "failed"
    if task_id == "task-b" and condition == "disturbed":
        return "success" if seed <= 4 else "failed" if seed <= 8 else "error"
    raise ValueError(f"Unsupported mock matrix entry: {task_id}/{condition}/{seed}")


def _failure_category(task_id: str, condition: str, seed: int, status: str) -> str | None:
    if status == "success":
        return None
    if status == "error":
        return "system_error"
    if status == "interrupted":
        return "unknown"

    categories = {
        ("task-a", "normal", 7): "grasp",
        ("task-a", "normal", 8): "placement",
        ("task-a", "disturbed", 4): "target_recognition",
        ("task-a", "disturbed", 5): "localization",
        ("task-a", "disturbed", 6): "grasp",
        ("task-a", "disturbed", 7): "placement",
        ("task-a", "disturbed", 8): "perturbation",
        ("task-b", "normal", 8): "control",
        ("task-b", "normal", 9): "termination",
        ("task-b", "disturbed", 5): "localization",
        ("task-b", "disturbed", 6): "grasp",
        ("task-b", "disturbed", 7): "placement",
        ("task-b", "disturbed", 8): "control",
    }
    return categories[(task_id, condition, seed)]


def _result(status: str, variant: int, max_steps: int) -> dict[str, Any]:
    if status == "success":
        steps = 220 + (variant * 17) % 150
        termination_reason = "environment_success"
    elif status == "failed":
        steps = max_steps
        termination_reason = "max_steps_reached"
    elif status == "error":
        steps = 55 + (variant * 11) % 70
        termination_reason = "mock_runtime_error"
    else:
        steps = 130 + (variant * 7) % 80
        termination_reason = "manual_interruption"

    return {
        "status": status,
        "success": status == "success",
        "terminationReason": termination_reason,
        "executedSteps": steps,
        "maxSteps": max_steps,
        "durationSeconds": round(4.8 + steps * 0.135 + (variant % 4) * 0.4, 2),
        "averageInferenceMs": None,
    }


def _diagnosis(
    task_id: str,
    condition: str,
    seed: int,
    status: str,
    category: str | None,
) -> dict[str, Any] | None:
    if status == "error" or (task_id, condition, seed) == ("task-a", "normal", 8):
        return None

    if status == "success":
        return {
            "targetVisible": True,
            "targetPosition": "center",
            "taskStage": "completed",
            "suspectedFailureStage": None,
            "observations": ["模拟诊断：目标操作在结束画面中已完成。"],
            "needsHumanReview": False,
        }

    stage = FAILURE_STAGE[category or "unknown"]
    task_stage = stage if stage in {"approach", "grasp", "transport", "placement"} else "unknown"
    return {
        "targetVisible": False if category == "target_recognition" else True,
        "targetPosition": "unknown" if category in {"target_recognition", "unknown"} else "center-left",
        "taskStage": task_stage,
        "suspectedFailureStage": stage,
        "observations": [FAILURE_COMMENT[category or "unknown"]],
        "needsHumanReview": True,
    }


def generate_mock_runs(config_directory: Path) -> list[dict[str, Any]]:
    """Generate the fixed 2-task × 2-condition × 10-seed matrix."""

    tasks = _load_json(config_directory / "tasks.json")["tasks"]
    evaluation = _load_json(config_directory / "evaluation.json")
    created_base = datetime(2026, 11, 24, 10, 0, tzinfo=timezone.utc)
    runs: list[dict[str, Any]] = []

    for task_index, task in enumerate(tasks):
        for condition_index, condition in enumerate(evaluation["conditions"]):
            for seed in evaluation["seeds"]:
                variant = task_index * 20 + condition_index * 10 + seed
                status = _outcome(task["id"], condition["type"], seed)
                category = _failure_category(task["id"], condition["type"], seed, status)
                created_at = created_base + timedelta(minutes=variant)
                runs.append(
                    {
                        "schemaVersion": "1.0",
                        "runId": f"{task['id']}-{condition['type']}-seed-{seed:04d}",
                        "dataSource": "mock",
                        "task": {
                            "id": task["id"],
                            "name": task["name"],
                            "suite": task["suite"],
                            "taskIndex": task["taskIndex"],
                            "instruction": task["instruction"],
                        },
                        "condition": {
                            "type": condition["type"],
                            "perturbation": condition["perturbation"],
                        },
                        "seed": seed,
                        "models": {
                            "policy": "mock-policy-v1",
                            "diagnoser": "mock-vlm-v1",
                        },
                        "result": _result(status, variant, evaluation["maxSteps"]),
                        "artifacts": {
                            "videoUrl": None,
                            "startFrameUrl": None,
                            "middleFrameUrl": None,
                            "endFrameUrl": None,
                        },
                        "diagnosis": _diagnosis(
                            task["id"], condition["type"], seed, status, category
                        ),
                        "humanReview": {
                            "reviewed": status != "success",
                            "failureCategory": category,
                            "comment": FAILURE_COMMENT[category] if category else None,
                        },
                        "createdAt": created_at.isoformat().replace("+00:00", "Z"),
                    }
                )

    return runs


def write_json(path: Path, value: Any) -> None:
    """Write stable UTF-8 JSON suitable for Git and frontend loading."""

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as file:
        json.dump(value, file, ensure_ascii=False, indent=2)
        file.write("\n")
