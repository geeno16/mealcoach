import { observer } from "mobx-react-lite";
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { useStore } from "../../root_store/StoreContext";
import { useAsyncAction } from "../../shared/useAsyncAction";

type Phase = "credentials" | "code";

export const SignupPage = observer(function SignupPage() {
  const { session } = useStore();
  const navigate = useNavigate();

  const [phase, setPhase] = useState<Phase>("credentials");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [code, setCode] = useState("");
  const { pending, error, run } = useAsyncAction();

  function handleRegister(event: React.FormEvent) {
    event.preventDefault();
    void run(
      async () => {
        await session.register({ email, password });
        setPhase("code");
      },
      { fallbackMessage: "Не удалось зарегистрироваться" },
    );
  }

  function handleVerify(event: React.FormEvent) {
    event.preventDefault();
    void run(
      async () => {
        await session.verifyEmail({ email, code });
        await session.login({ email, password });
        navigate("/app/fork", { replace: true });
      },
      { fallbackMessage: "Неверный код" },
    );
  }

  function handleResend() {
    void run(() => session.resendCode({ email, password }), {
      fallbackMessage: "Не удалось отправить код",
    });
  }

  if (phase === "code") {
    return (
      <div className="screen">
        <form className="card" onSubmit={handleVerify}>
          <h1>Подтверждение</h1>
          <p className="hint">Код отправлен на {email}</p>

          <label className="field">
            <span>Код из письма</span>
            <input
              value={code}
              onChange={(e) => setCode(e.target.value)}
              required
            />
          </label>

          {error && <p className="error">{error}</p>}

          <button className="button" type="submit" disabled={pending}>
            {pending ? "…" : "Подтвердить"}
          </button>

          <button
            className="button button-secondary"
            type="button"
            onClick={handleResend}
          >
            Отправить код заново
          </button>
        </form>
      </div>
    );
  }

  return (
    <div className="screen">
      <form className="card" onSubmit={handleRegister}>
        <h1>Регистрация</h1>

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
          {pending ? "…" : "Создать аккаунт"}
        </button>

        <p className="hint">
          Уже есть аккаунт? <Link to="/app/login">Войти</Link>
        </p>
      </form>
    </div>
  );
});
