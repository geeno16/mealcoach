import { observer } from "mobx-react-lite";
import { useEffect, useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";

import { ApiError, type UserWrite } from "../api";
import { useStore } from "../root_store/StoreContext";

import { CoachRequests } from "./CoachRequests";
import { CoachTrainees } from "./CoachTrainees";

function isSet<T>(value: T | null | undefined): value is T {
  return value !== null && value !== undefined;
}

export const ProfilePage = observer(function ProfilePage() {
  const { session, coach } = useStore();
  const navigate = useNavigate();

  const [editing, setEditing] = useState(false);
  const [name, setName] = useState("");
  const [surname, setSurname] = useState("");
  const [age, setAge] = useState("");
  const [weight, setWeight] = useState("");
  const [height, setHeight] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);
  const [detaching, setDetaching] = useState(false);

  const user = session.user;

  useEffect(() => {
    if (user?.role === "coach") void coach.load(user.auth_id);
  }, [coach, user]);

  if (!user) return <Navigate to="/app/fork" replace />;

  const handleLogout = async () => {
    await session.logout();
    navigate("/app/login", { replace: true });
  };

  const handleDetach = async () => {
    setError(null);
    setDetaching(true);
    try {
      await session.clearCoach();
    } catch (err) {
      setError(
        err instanceof ApiError ? err.message : "Не удалось открепиться",
      );
      setDetaching(false);
    }
  };

  const startEdit = () => {
    setName(user.name);
    setSurname(user.surname ?? "");
    setAge(user.age?.toString() ?? "");
    setWeight(user.weight?.toString() ?? "");
    setHeight(user.height?.toString() ?? "");
    setError(null);
    setEditing(true);
  };

  const handleSave = async (event: React.FormEvent) => {
    event.preventDefault();
    const payload: UserWrite = {
      ...user,
      name,
      surname: surname || null,
      age: age ? Number(age) : null,
      weight: weight ? Number(weight) : null,
      height: height ? Number(height) : null,
    };

    setError(null);
    setPending(true);
    try {
      await session.updateUser(payload);
      setEditing(false);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Не удалось сохранить");
    } finally {
      setPending(false);
    }
  };

  if (editing) {
    return (
      <div className="screen">
        <form className="card" onSubmit={handleSave}>
          <h1>Редактирование</h1>

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
            <input
              value={surname}
              onChange={(e) => setSurname(e.target.value)}
            />
          </label>

          {user.role === "trainee" && (
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
            </>
          )}

          {error && <p className="error">{error}</p>}

          <button className="button" type="submit" disabled={pending}>
            {pending ? "…" : "Сохранить"}
          </button>
          <button
            className="button button-secondary"
            type="button"
            onClick={() => setEditing(false)}
          >
            Отмена
          </button>
        </form>
      </div>
    );
  }

  return (
    <div className="screen">
      <div className="card">
        <h1>{user.name}</h1>

        <div className="params">
          <div className="param">
            <span>Роль</span>
            <span>{user.role === "coach" ? "Тренер" : "Ученик"}</span>
          </div>
          {user.surname && (
            <div className="param">
              <span>Фамилия</span>
              <span>{user.surname}</span>
            </div>
          )}
          {isSet(user.age) && (
            <div className="param">
              <span>Возраст</span>
              <span>{user.age}</span>
            </div>
          )}
          {isSet(user.weight) && (
            <div className="param">
              <span>Вес, кг</span>
              <span>{user.weight}</span>
            </div>
          )}
          {isSet(user.height) && (
            <div className="param">
              <span>Рост, см</span>
              <span>{user.height}</span>
            </div>
          )}
          {isSet(user.coach_id) && (
            <div className="param">
              <span>ID тренера</span>
              <span>{user.coach_id}</span>
            </div>
          )}
        </div>

        {user.role === "coach" && (
          <>
            <CoachRequests />
            <CoachTrainees />
            {coach.error && <p className="error">{coach.error}</p>}
          </>
        )}

        {error && <p className="error">{error}</p>}

        <button className="button" type="button" onClick={startEdit}>
          Редактировать
        </button>

        {user.role === "trainee" && (
          <button
            className="button button-secondary"
            type="button"
            disabled={detaching}
            onClick={handleDetach}
          >
            {detaching ? "…" : "Открепиться от тренера"}
          </button>
        )}
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
});
