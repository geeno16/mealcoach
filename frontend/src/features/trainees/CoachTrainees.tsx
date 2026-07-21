import { observer } from "mobx-react-lite";

import { useStore } from "../../root_store/StoreContext";

export const CoachTrainees = observer(function CoachTrainees() {
  const { coach } = useStore();

  if (coach.trainees.length === 0) {
    return <p className="hint">Учеников пока нет</p>;
  }

  return (
    <div className="requests">
      <p className="hint">Ученики:</p>
      {coach.trainees.map((trainee) => (
        <div className="request" key={trainee.auth_id}>
          <span>{trainee.name}</span>
          <div className="request-actions">
            <button
              className="button button-secondary"
              type="button"
              disabled={coach.pendingId === trainee.auth_id}
              onClick={() => coach.detach(trainee.auth_id)}
            >
              Удалить
            </button>
          </div>
        </div>
      ))}
    </div>
  );
});
