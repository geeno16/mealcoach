import { observer } from "mobx-react-lite";
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { useStore } from "../../root_store/StoreContext";
import { useAsyncAction } from "../../shared/useAsyncAction";

type Phase = "request" | "reset";

export const ForgotPasswordPage = observer(function ForgotPasswordPage() {
  const { session } = useStore();
  const navigate = useNavigate();

  const [phase, setPhase] = useState<Phase>("request");
  const [email, setEmail] = useState("");
  const [code, setCode] = useState("");
  const [password, setPassword] = useState("");
  const { pending, error, run } = useAsyncAction();

  function handleRequest(event: React.FormEvent) {
    event.preventDefault();
    void run(
      async () => {
        await session.forgotPassword(email);
        setPhase("reset");
      },
      { fallbackMessage: "Не удалось отправить код" },
    );
  }

  function handleReset(event: React.FormEvent) {
    event.preventDefault();
    void run(
      async () => {
        await session.resetPassword(email, code, password);
        navigate("/app/login", { replace: true });
      },
      { fallbackMessage: "Не удалось сбросить пароль" },
    );
  }

  if (phase === "reset") {
    return (
      <div className="screen">
        <form className="card" onSubmit={handleReset}>
          <h1>Новый пароль</h1>
          <p className="hint">
            Если аккаунт существует, код отправлен на {email}
          </p>

          <label className="field">
            <span>Код из письма</span>
            <input
              value={code}
              onChange={(e) => setCode(e.target.value)}
              required
            />
          </label>

          <label className="field">
            <span>Новый пароль</span>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </label>

          {error && <p className="error">{error}</p>}

          <button className="button" type="submit" disabled={pending}>
            {pending ? "…" : "Сбросить пароль"}
          </button>
        </form>
      </div>
    );
  }

  return (
    <div className="screen">
      <form className="card" onSubmit={handleRequest}>
        <h1>Восстановление пароля</h1>

        <label className="field">
          <span>Email</span>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </label>

        {error && <p className="error">{error}</p>}

        <button className="button" type="submit" disabled={pending}>
          {pending ? "…" : "Отправить код"}
        </button>

        <p className="hint">
          Вспомнили пароль? <Link to="/app/login">Войти</Link>
        </p>
      </form>
    </div>
  );
});
