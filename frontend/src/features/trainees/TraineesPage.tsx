import { observer } from "mobx-react-lite";
import { useEffect } from "react";
import { Navigate } from "react-router-dom";

import { useStore } from "../../root_store/StoreContext";

import { CoachTrainees } from "./CoachTrainees";

export const TraineesPage = observer(function TraineesPage() {
  const { session, coach } = useStore();
  const user = session.user;

  useEffect(() => {
    if (user?.role === "coach") void coach.load(user.auth_id);
  }, [coach, user]);

  if (!user) return <Navigate to="/app/fork" replace />;
  if (user.role !== "coach") return <Navigate to="/app/profile" replace />;

  return (
    <div className="screen">
      <div className="card">
        <h1>Ученики</h1>
        <CoachTrainees />
        {coach.error && <p className="error">{coach.error}</p>}
      </div>
    </div>
  );
});
