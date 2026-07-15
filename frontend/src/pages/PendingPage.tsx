import { observer } from "mobx-react-lite";
import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { ApiError } from "../api";
import { useStore } from "../root_store/StoreContext";

export const PendingPage = observer(function PendingPage() {
  const { session } = useStore();
  const navigate = useNavigate();

  const [coachEmail, setCoachEmail] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  const user = session.user;
  if (!user) return null;

  const handleLogout = async () => {
    await session.logout();
    navigate("/app/login", { replace: true });
  };

  const hasRequest =
    user.coach_request_id !== null && user.coach_request_id !== undefined;

  const handleCancel = async () => {
    setError(null);
    setPending(true);
    try {
      await session.clearCoach();
    } catch (err) {
      setError(
        err instanceof ApiError ? err.message : "Не удалось отменить заявку",
      );
    } finally {
      setPending(false);
    }
  };

  const handleRequest = async (event: React.FormEvent) => {
    event.preventDefault();
    setError(null);
    setPending(true);
    try {
      await session.requestCoach(coachEmail);
    } catch (err) {
      setError(
        err instanceof ApiError ? err.message : "Не удалось отправить заявку",
      );
    } finally {
      setPending(false);
    }
  };

  if (hasRequest) {
    return (
      <div className="screen">
        <div className="card">
          <h1>Заявка отправлена</h1>
          <p className="hint">Дождитесь, пока тренер подтвердит вашу заявку.</p>

          {error && <p className="error">{error}</p>}

          <button
            className="button"
            type="button"
            disabled={pending}
            onClick={handleCancel}
          >
            {pending ? "…" : "Отменить заявку"}
          </button>
          <button
            className="button button-secondary"
            type="button"
            onClick={handleLogout}
          >
            Выйти
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="screen">
      <form className="card" onSubmit={handleRequest}>
        <h1>Тренер не назначен</h1>
        <p className="hint">Укажите email тренера, чтобы отправить заявку.</p>

        <label className="field">
          <span>Email тренера</span>
          <input
            type="email"
            value={coachEmail}
            onChange={(e) => setCoachEmail(e.target.value)}
            required
          />
        </label>

        {error && <p className="error">{error}</p>}

        <button className="button" type="submit" disabled={pending}>
          {pending ? "…" : "Отправить заявку"}
        </button>
        <button
          className="button button-secondary"
          type="button"
          onClick={handleLogout}
        >
          Выйти
        </button>
      </form>
    </div>
  );
});
