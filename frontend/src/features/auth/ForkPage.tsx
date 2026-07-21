import { observer } from "mobx-react-lite";
import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { type UserRole, type UserWrite } from "../../api";
import { useStore } from "../../root_store/StoreContext";
import { useAsyncAction } from "../../shared/useAsyncAction";

export const ForkPage = observer(function ForkPage() {
  const { session } = useStore();
  const navigate = useNavigate();

  const [role, setRole] = useState<UserRole>("trainee");
  const [name, setName] = useState("");
  const [surname, setSurname] = useState("");
  const [age, setAge] = useState("");
  const [weight, setWeight] = useState("");
  const [height, setHeight] = useState("");
  const [coachEmail, setCoachEmail] = useState("");
  const { pending, error, run } = useAsyncAction();

  async function handleLogout() {
    await session.logout();
    navigate("/app/login", { replace: true });
  }

  if (!session.auth) return null;

  function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    if (!session.auth) return;

    const payload: UserWrite = { auth_id: session.auth.id, role, name };
    if (surname) payload.surname = surname;
    if (role === "trainee") {
      if (age) payload.age = Number(age);
      if (weight) payload.weight = Number(weight);
      if (height) payload.height = Number(height);
      if (coachEmail) payload.coach_email = coachEmail;
    }

    void run(
      async () => {
        await session.createUser(payload);
        navigate(session.awaitingCoach ? "/app/pending" : "/app/profile", {
          replace: true,
        });
      },
      { fallbackMessage: "Не удалось создать профиль" },
    );
  }

  return (
    <div className="screen">
      <form className="card" onSubmit={handleSubmit}>
        <h1>Кто вы?</h1>

        <div className="roles">
          <label className="role">
            <input
              type="radio"
              name="role"
              value="trainee"
              checked={role === "trainee"}
              onChange={() => setRole("trainee")}
            />
            <span>Ученик</span>
          </label>
          <label className="role">
            <input
              type="radio"
              name="role"
              value="coach"
              checked={role === "coach"}
              onChange={() => setRole("coach")}
            />
            <span>Тренер</span>
          </label>
        </div>

        <label className="field">
          <span>Имя</span>
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />
        </label>

        <label className="field">
          <span>Фамилия</span>
          <input value={surname} onChange={(e) => setSurname(e.target.value)} />
        </label>

        {role === "trainee" && (
          <>
            <label className="field">
              <span>Возраст</span>
              <input
                type="number"
                value={age}
                onChange={(e) => setAge(e.target.value)}
              />
            </label>

            <label className="field">
              <span>Вес, кг</span>
              <input
                type="number"
                value={weight}
                onChange={(e) => setWeight(e.target.value)}
              />
            </label>

            <label className="field">
              <span>Рост, см</span>
              <input
                type="number"
                value={height}
                onChange={(e) => setHeight(e.target.value)}
              />
            </label>

            <label className="field">
              <span>Email тренера</span>
              <input
                type="email"
                value={coachEmail}
                onChange={(e) => setCoachEmail(e.target.value)}
                required
              />
            </label>
          </>
        )}

        {error && <p className="error">{error}</p>}

        <button className="button" type="submit" disabled={pending}>
          {pending ? "…" : "Продолжить"}
        </button>

        <button
          className="button button-secondary"
          type="button"
          onClick={handleLogout}
        >
          Выйти и создать другой аккаунт
        </button>
      </form>
    </div>
  );
});
