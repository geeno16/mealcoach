import { observer } from "mobx-react-lite";
import { useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";

import { useStore } from "../../root_store/StoreContext";
import { useAsyncAction } from "../../shared/useAsyncAction";

import { ProfileEditStore } from "./profile-edit.store";

function isSet<T>(value: T | null | undefined): value is T {
  return value !== null && value !== undefined;
}

function FieldError({ message }: { message: string | null }) {
  if (!message) return null;
  return <span className="field-error">{message}</span>;
}

export const ProfilePage = observer(function ProfilePage() {
  const { session } = useStore();
  const navigate = useNavigate();
  const [edit] = useState(() => new ProfileEditStore(session));

  const {
    pending: detaching,
    error: detachError,
    run: runDetach,
  } = useAsyncAction();

  const user = session.user;
  if (!user) return <Navigate to="/app/fork" replace />;

  const handleLogout = async () => {
    await session.logout();
    navigate("/app/login", { replace: true });
  };

  const handleDetach = () =>
    runDetach(() => session.clearCoach(), {
      fallbackMessage: "Не удалось открепиться",
    });

  const handleSave = (event: React.FormEvent) => {
    event.preventDefault();
    void edit.save();
  };

  if (edit.editing) {
    return (
      <div className="screen">
        <form className="card" onSubmit={handleSave}>
          <h1>Редактирование</h1>

          <label className="field">
            <span>Имя</span>
            <input
              value={edit.name}
              onChange={(e) => edit.setName(e.target.value)}
              required
            />
            <FieldError message={edit.submitted ? edit.nameError : null} />
          </label>

          <label className="field">
            <span>Фамилия</span>
            <input
              value={edit.surname}
              onChange={(e) => edit.setSurname(e.target.value)}
            />
            <FieldError message={edit.submitted ? edit.surnameError : null} />
          </label>

          {user.role === "trainee" && (
            <>
              <label className="field">
                <span>Возраст</span>
                <input
                  type="number"
                  value={edit.age}
                  onChange={(e) => edit.setAge(e.target.value)}
                />
                <FieldError message={edit.submitted ? edit.ageError : null} />
              </label>

              <label className="field">
                <span>Вес, кг</span>
                <input
                  type="number"
                  value={edit.weight}
                  onChange={(e) => edit.setWeight(e.target.value)}
                />
                <FieldError
                  message={edit.submitted ? edit.weightError : null}
                />
              </label>

              <label className="field">
                <span>Рост, см</span>
                <input
                  type="number"
                  value={edit.height}
                  onChange={(e) => edit.setHeight(e.target.value)}
                />
                <FieldError
                  message={edit.submitted ? edit.heightError : null}
                />
              </label>
            </>
          )}

          {edit.error && <p className="error">{edit.error}</p>}

          <button className="button" type="submit" disabled={edit.pending}>
            {edit.pending ? "…" : "Сохранить"}
          </button>
          <button
            className="button button-secondary"
            type="button"
            onClick={() => edit.cancelEdit()}
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

        {detachError && <p className="error">{detachError}</p>}

        <button
          className="button button-secondary"
          type="button"
          onClick={() => edit.startEdit()}
        >
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
