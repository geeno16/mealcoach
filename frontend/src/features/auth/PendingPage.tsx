import { observer } from "mobx-react-lite";
import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { useStore } from "../../root_store/StoreContext";
import { useAsyncAction } from "../../shared/useAsyncAction";

export const PendingPage = observer(function PendingPage() {
  const { session } = useStore();
  const navigate = useNavigate();

  const [coachEmail, setCoachEmail] = useState("");
  const { pending, error, run } = useAsyncAction();

  const user = session.user;
  if (!user) return null;

  const handleLogout = async () => {
    await session.logout();
    navigate("/app/login", { replace: true });
  };

  const hasRequest =
    user.coach_request_id !== null && user.coach_request_id !== undefined;

  const handleCancel = () =>
    run(() => session.clearCoach(), {
      fallbackMessage: "Не удалось отменить заявку",
    });

  const handleRequest = (event: React.FormEvent) => {
    event.preventDefault();
    void run(() => session.requestCoach(coachEmail), {
      fallbackMessage: "Не удалось отправить заявку",
    });
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
