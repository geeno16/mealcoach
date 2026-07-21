import { observer } from "mobx-react-lite";
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { useStore } from "../../root_store/StoreContext";
import { useAsyncAction } from "../../shared/useAsyncAction";

export const LoginPage = observer(function LoginPage() {
  const { session } = useStore();
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const { pending, error, run } = useAsyncAction();

  function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    void run(
      async () => {
        await session.login({ email, password });
        const target = !session.hasProfile
          ? "/app/fork"
          : session.awaitingCoach
            ? "/app/pending"
            : "/app/profile";
        navigate(target, { replace: true });
      },
      { fallbackMessage: "Не удалось войти" },
    );
  }

  return (
    <div className="screen">
      <form className="card" onSubmit={handleSubmit}>
        <h1>Вход</h1>

        <label className="field">
          <span>Email</span>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </label>

        <label className="field">
          <span>Пароль</span>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </label>

        {error && <p className="error">{error}</p>}

        <button className="button" type="submit" disabled={pending}>
          {pending ? "…" : "Войти"}
        </button>

        <p className="hint">
          Нет аккаунта? <Link to="/app/signup">Регистрация</Link>
        </p>
        <p className="hint">
          Забыли пароль? <Link to="/app/reset">Восстановить</Link>
        </p>
      </form>
    </div>
  );
});
