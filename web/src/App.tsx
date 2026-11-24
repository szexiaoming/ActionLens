import { useEffect, useState } from "react";
import { AppLayout } from "./components/AppLayout";
import { DashboardPage } from "./pages/DashboardPage";
import { RunDetailPage } from "./pages/RunDetailPage";
import { loadEvaluationData } from "./services/runData";
import type { EvaluationData } from "./types/evaluation";

type Route = { name: "dashboard" } | { name: "runs" } | { name: "run"; runId: string };

function readRoute(): Route {
  const hash = window.location.hash.replace(/^#/, "") || "/";
  const match = hash.match(/^\/runs\/(.+)$/);
  if (match) return { name: "run", runId: decodeURIComponent(match[1]) };
  return hash === "/runs" ? { name: "runs" } : { name: "dashboard" };
}

function App() {
  const [route, setRoute] = useState<Route>(readRoute);
  const [data, setData] = useState<EvaluationData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    const handleHashChange = () => setRoute(readRoute());
    window.addEventListener("hashchange", handleHashChange);
    return () => window.removeEventListener("hashchange", handleHashChange);
  }, []);

  useEffect(() => {
    let cancelled = false;
    setError(null);
    loadEvaluationData()
      .then((loadedData) => {
        if (!cancelled) setData(loadedData);
      })
      .catch((reason: unknown) => {
        if (!cancelled) {
          setError(reason instanceof Error ? reason.message : "无法加载评测数据");
        }
      });
    return () => {
      cancelled = true;
    };
  }, [reloadKey]);

  useEffect(() => {
    if (route.name === "runs" && data) {
      window.requestAnimationFrame(() => document.getElementById("runs")?.scrollIntoView());
    }
  }, [route, data]);

  if (error) {
    return (
      <AppLayout active="dashboard">
        <section className="state-panel" role="alert">
          <p className="eyebrow">数据加载失败</p>
          <h1>当前无法打开评测结果</h1>
          <p>{error}</p>
          <button className="primary-button" onClick={() => setReloadKey((value) => value + 1)}>
            重新加载
          </button>
        </section>
      </AppLayout>
    );
  }

  if (!data) {
    return (
      <AppLayout active="dashboard">
        <section className="state-panel" aria-live="polite">
          <div className="loading-mark" />
          <p className="eyebrow">正在校验数据</p>
          <h1>载入 ActionLens 评测记录</h1>
        </section>
      </AppLayout>
    );
  }

  if (route.name === "run") {
    const run = data.runs.find((item) => item.runId === route.runId);
    return (
      <AppLayout active="runs" dataSource={data.summary.dataSource}>
        <RunDetailPage run={run} />
      </AppLayout>
    );
  }

  return (
    <AppLayout active={route.name === "runs" ? "runs" : "dashboard"} dataSource={data.summary.dataSource}>
      <DashboardPage runs={data.runs} summary={data.summary} />
    </AppLayout>
  );
}

export default App;
