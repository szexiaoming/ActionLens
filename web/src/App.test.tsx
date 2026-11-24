import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import runs from "../public/data/runs.json";
import summary from "../public/data/summary.json";
import manifest from "../public/data/manifest.json";
import App from "./App";

describe("App", () => {
  beforeEach(() => {
    window.location.hash = "#/";
    vi.stubGlobal("fetch", vi.fn(async (input: RequestInfo | URL) => ({
      ok: true,
      status: 200,
      json: async () => String(input).includes("manifest") ? manifest : String(input).includes("summary") ? summary : runs,
    }) as Response));
  });

  afterEach(() => {
    cleanup();
    vi.unstubAllGlobals();
    window.location.hash = "#/";
  });

  it("loads the validated dashboard and filters failed runs", async () => {
    render(<App />);
    expect(await screen.findByRole("heading", { name: "实验总览" })).toBeInTheDocument();
    expect(screen.getByText("40 条模拟记录")).toBeInTheDocument();
    expect(screen.getByText("显示 40 / 40 条记录")).toBeInTheDocument();

    fireEvent.change(screen.getByLabelText("运行状态"), { target: { value: "failed" } });
    expect(screen.getByText("显示 13 / 40 条记录")).toBeInTheDocument();
  });

  it("opens a run detail directly from its URL", async () => {
    window.location.hash = "#/runs/task-a-normal-seed-0000";
    render(<App />);

    expect(await screen.findByRole("heading", { name: "抓取并放置目标物体" })).toBeInTheDocument();
    expect(screen.getByText("视频尚未生成")).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "视觉诊断" })).toBeInTheDocument();
  });
});
