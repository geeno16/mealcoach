import { observer } from "mobx-react-lite";
import { useEffect } from "react";
import { Link } from "react-router-dom";

import { type NotificationRead } from "../../api";
import { useStore } from "../../root_store/StoreContext";
import { Loader } from "../../shared/Loader";

function describe(item: NotificationRead): string {
  const who = item.actor_name ?? "Пользователь";
  const post = item.post_name ? `«${item.post_name}»` : "ваш пост";
  switch (item.type) {
    case "coach_request":
      return `${who} хочет стать вашим учеником`;
    case "trainee_added":
      return `${who} добавлен в ученики`;
    case "trainee_removed":
      return `${who} больше не ваш ученик`;
    case "request_accepted":
      return `Тренер ${who} принял вашу заявку`;
    case "post_graded":
      return `Тренер ${who} оценил ${post}`;
    case "post_created":
      return `${who} опубликовал ${post}`;
    default:
      return "Уведомление";
  }
}

export const NotificationsPage = observer(function NotificationsPage() {
  const { notifications } = useStore();

  useEffect(() => {
    void notifications.load();
  }, [notifications]);

  return (
    <div className="screen">
      <div className="card">
        <h1>Уведомления</h1>

        {notifications.error && <p className="error">{notifications.error}</p>}

        {notifications.loading ? (
          <Loader />
        ) : notifications.items.length === 0 ? (
          <p className="hint">Уведомлений нет</p>
        ) : (
          <div className="requests">
            {notifications.items.map((item) => (
              <div className="request" key={item.id}>
                <span>{describe(item)}</span>
                {item.type === "coach_request" && item.actor_id !== null && (
                  <div className="request-actions">
                    <button
                      className="button"
                      type="button"
                      disabled={notifications.pendingId === item.actor_id}
                      onClick={() => notifications.accept(item.actor_id!)}
                    >
                      Принять
                    </button>
                    <button
                      className="button button-secondary"
                      type="button"
                      disabled={notifications.pendingId === item.actor_id}
                      onClick={() => notifications.reject(item.actor_id!)}
                    >
                      Отклонить
                    </button>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}

        <Link className="button button-secondary" to="/app/profile">
          Назад в профиль
        </Link>
      </div>
    </div>
  );
});
