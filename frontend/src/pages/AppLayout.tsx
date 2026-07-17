import { Outlet } from "react-router-dom";

import { Sidebar } from "./Sidebar";

export function AppLayout() {
  return (
    <div className="layout">
      <Sidebar />
      <main className="content">
        <Outlet />
      </main>
    </div>
  );
}
