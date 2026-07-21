import { observer } from "mobx-react-lite";
import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { useStore } from "../../root_store/StoreContext";

import { ForkFormStore } from "./fork.store";

function FieldError({ message }: { message: string | null }) {
  if (!message) return null;
  return <span className="field-error">{message}</span>;
}

export const ForkPage = observer(function ForkPage() {
  const { session } = useStore();
  const navigate = useNavigate();
  const [form] = useState(() => new ForkFormStore(session));

  async function handleLogout() {
    await session.logout();
    navigate("/app/login", { replace: true });
  }

  if (!session.auth) return null;

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    const created = await form.submit();
    if (created) {
      navigate(session.awaitingCoach ? "/app/pending" : "/app/profile", {
        replace: true,
      });
    }
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
              checked={form.role === "trainee"}
              onChange={() => form.setRole("trainee")}
            />
            <span>Ученик</span>
          </label>
          <label className="role">
            <input
              type="radio"
              name="role"
              value="coach"
              checked={form.role === "coach"}
              onChange={() => form.setRole("coach")}
            />
            <span>Тренер</span>
          </label>
        </div>

        <label className="field">
          <span>Имя</span>
          <input
            value={form.name}
            onChange={(e) => form.setName(e.target.value)}
            required
          />
          <FieldError message={form.submitted ? form.nameError : null} />
        </label>

        <label className="field">
          <span>Фамилия</span>
          <input
            value={form.surname}
            onChange={(e) => form.setSurname(e.target.value)}
          />
          <FieldError message={form.submitted ? form.surnameError : null} />
        </label>

        {form.isTrainee && (
          <>
            <label className="field">
              <span>Возраст</span>
              <input
                type="number"
                value={form.age}
                onChange={(e) => form.setAge(e.target.value)}
              />
              <FieldError message={form.submitted ? form.ageError : null} />
            </label>

            <label className="field">
              <span>Вес, кг</span>
              <input
                type="number"
                value={form.weight}
                onChange={(e) => form.setWeight(e.target.value)}
              />
              <FieldError message={form.submitted ? form.weightError : null} />
            </label>

            <label className="field">
              <span>Рост, см</span>
              <input
                type="number"
                value={form.height}
                onChange={(e) => form.setHeight(e.target.value)}
              />
              <FieldError message={form.submitted ? form.heightError : null} />
            </label>

            <label className="field">
              <span>Email тренера</span>
              <input
                type="email"
                value={form.coachEmail}
                onChange={(e) => form.setCoachEmail(e.target.value)}
                required
              />
              <FieldError
                message={form.submitted ? form.coachEmailError : null}
              />
            </label>
          </>
        )}

        {form.error && <p className="error">{form.error}</p>}

        <button className="button" type="submit" disabled={form.pending}>
          {form.pending ? "…" : "Продолжить"}
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
