import { observer } from "mobx-react-lite";
import { Navigate, Outlet } from "react-router-dom";

import { useStore } from "../root_store/StoreContext";

const loading = <div className="screen">Загрузка…</div>;

export const RequireAuth = observer(function RequireAuth() {
  const { session } = useStore();

  if (session.status === "loading") return loading;
  if (!session.isAuthenticated) return <Navigate to="/app/login" replace />;

  return <Outlet />;
});

export const RequireGuest = observer(function RequireGuest() {
  const { session } = useStore();

  if (session.status === "loading") return loading;
  if (session.isAuthenticated) return <Navigate to="/app/fork" replace />;

  return <Outlet />;
});

export const RequireNoProfile = observer(function RequireNoProfile() {
  const { session } = useStore();

  if (session.status === "loading") return loading;
  if (!session.isAuthenticated) return <Navigate to="/app/login" replace />;
  if (session.hasProfile) {
    return (
      <Navigate
        to={session.awaitingCoach ? "/app/pending" : "/app/profile"}
        replace
      />
    );
  }

  return <Outlet />;
});

export const RequirePending = observer(function RequirePending() {
  const { session } = useStore();

  if (session.status === "loading") return loading;
  if (!session.isAuthenticated) return <Navigate to="/app/login" replace />;
  if (!session.hasProfile) return <Navigate to="/app/fork" replace />;
  if (!session.awaitingCoach) return <Navigate to="/app/profile" replace />;

  return <Outlet />;
});

export const RequireActive = observer(function RequireActive() {
  const { session } = useStore();

  if (session.status === "loading") return loading;
  if (!session.isAuthenticated) return <Navigate to="/app/login" replace />;
  if (!session.hasProfile) return <Navigate to="/app/fork" replace />;
  if (session.awaitingCoach) return <Navigate to="/app/pending" replace />;

  return <Outlet />;
});
