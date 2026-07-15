import { observer } from "mobx-react-lite";

import { useStore } from "../root_store/StoreContext";

export const CoachRequests = observer(function CoachRequests() {
  const { coach } = useStore();

  if (coach.requests.length === 0) {
    return <p className="hint">Новых заявок нет</p>;
  }

  return (
    <div className="requests">
      <p className="hint">Заявки в ученики:</p>
      {coach.requests.map((request) => (
        <div className="request" key={request.auth_id}>
          <span>{request.name}</span>
          <div className="request-actions">
            <button
              className="button"
              type="button"
              disabled={coach.pendingId === request.auth_id}
              onClick={() => coach.approve(request.auth_id)}
            >
              Принять
            </button>
            <button
              className="button button-secondary"
              type="button"
              disabled={coach.pendingId === request.auth_id}
              onClick={() => coach.detach(request.auth_id)}
            >
              Отклонить
            </button>
          </div>
        </div>
      ))}
    </div>
  );
});
