import type { ReactNode } from "react";

export function AppLayout({ active, children, dataSource }: { active: "dashboard" | "runs"; children: ReactNode; dataSource?: "mock" | "real" }) {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <a className="brand" href="#/" aria-label="ActionLens 首页">
          <span className="brand__mark">AL</span>
          <span><strong>ActionLens</strong><small>Robot evaluation</small></span>
        </a>
        <nav className="sidebar__nav" aria-label="主导航">
          <a className={active === "dashboard" ? "is-active" : ""} href="#/">
            <span className="nav-icon" aria-hidden="true">◫</span>实验总览
          </a>
          <a className={active === "runs" ? "is-active" : ""} href="#/runs">
            <span className="nav-icon" aria-hidden="true">≡</span>运行记录
          </a>
        </nav>
        <div className="sidebar__footer">
          <div className="system-state">
            <span className="system-state__dot" />
            <span><strong>本地数据模式</strong><small>无需 GPU</small></span>
          </div>
          <p>已完成 4 / 5 阶段</p>
        </div>
      </aside>
      <div className="workspace">
        <div className="workspace__topbar">
          <span>VLA Evaluation / VLM Diagnosis</span><span className={`data-badge data-badge--${dataSource ?? "loading"}`}>{dataSource === "real" ? "真实评测数据" : dataSource === "mock" ? "模拟数据" : "数据载入中"}</span>
        </div>
        <main className="workspace__content">{children}</main>
      </div>
    </div>
  );
}
