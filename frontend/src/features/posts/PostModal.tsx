import { Eye, Image, Pencil, Save, Trash2 } from "lucide-react";
import { observer } from "mobx-react-lite";
import { useEffect, useState } from "react";

import { type MealRead, type PostRead } from "../../api";
import { useStore } from "../../root_store/StoreContext";
import { ConfirmDialog, Modal } from "../../shared/Modal";
import { MAX_POST_MEALS, MIN_POST_MEALS } from "../../shared/validation";

import { PostDraftStore, type MealDraft } from "./post-draft.store";
import { formatPostDate, mealsLabel, PostMark } from "./post-helpers";

function macro(value: number | null | undefined, unit: string): string {
  return value === null || value === undefined ? "—" : `${value} ${unit}`;
}

function FieldError({ message }: { message: string | null }) {
  if (!message) return null;
  return <span className="field-error">{message}</span>;
}

function MealPhoto({
  meal,
  editable,
  previewSrc,
  pictureUrl,
  onSelectFile,
}: {
  meal: MealRead | null;
  editable: boolean;
  previewSrc: string | undefined;
  pictureUrl: (pictureId: number, mealId: number) => string;
  onSelectFile: (file: File) => void;
}) {
  const hasPicture =
    meal !== null && meal.picture_id !== null && meal.picture_id !== undefined;
  const src =
    previewSrc ??
    (hasPicture ? pictureUrl(meal.picture_id!, meal.id) : undefined);

  const content = src ? (
    <img
      className="meal-thumb"
      src={src}
      alt=""
      loading="lazy"
      decoding="async"
    />
  ) : (
    <div className="meal-thumb-placeholder">
      <Image size={28} />
    </div>
  );

  const [viewerOpen, setViewerOpen] = useState(false);

  if (!editable) {
    if (!src) {
      return <div className="meal-thumb-wrap">{content}</div>;
    }
    return (
      <>
        <button
          className="meal-thumb-wrap meal-thumb-viewable"
          type="button"
          onClick={() => setViewerOpen(true)}
        >
          {content}
          <span className="meal-thumb-overlay">
            <Eye size={20} />
          </span>
        </button>
        {viewerOpen && (
          <Modal
            className="photo-viewer-backdrop"
            onClose={() => setViewerOpen(false)}
          >
            <img className="photo-viewer-img" src={src} alt="" />
          </Modal>
        )}
      </>
    );
  }

  return (
    <label className="meal-thumb-wrap meal-thumb-editable">
      {content}
      <span className="meal-thumb-overlay">
        <Pencil size={20} />
      </span>
      <input
        type="file"
        accept="image/*"
        hidden
        onChange={(e) => {
          const file = e.target.files?.[0];
          if (file) onSelectFile(file);
          e.target.value = "";
        }}
      />
    </label>
  );
}

export const PostModal = observer(function PostModal({
  post,
  onClose,
}: {
  post: PostRead | null;
  onClose: () => void;
}) {
  const { posts, session } = useStore();
  const [draft] = useState(() => new PostDraftStore(posts, session, post));
  const isCreate = draft.isCreate;

  useEffect(() => () => draft.dispose(), [draft]);

  const meals = draft.meals;

  const requestClose = () => {
    if (draft.beginClose()) onClose();
  };

  const renderMealFields = (mealDraft: MealDraft) => {
    const errors = draft.submitted
      ? draft.mealErrors(mealDraft)
      : { name: null, cal: null, protein: null, fat: null, carbohydrate: null };
    return (
      <>
        <input
          className="meal-name-input"
          value={mealDraft.name}
          onChange={(e) =>
            draft.updateMealDraft(mealDraft.id, { name: e.target.value })
          }
          placeholder="Название"
        />
        <FieldError message={errors.name} />
        <div className="meal-macro-inputs">
          <label className="meal-macro-field">
            <span>Ккал</span>
            <input
              type="number"
              value={mealDraft.cal}
              onChange={(e) =>
                draft.updateMealDraft(mealDraft.id, { cal: e.target.value })
              }
            />
            <FieldError message={errors.cal} />
          </label>
          <label className="meal-macro-field">
            <span>Белки</span>
            <input
              type="number"
              value={mealDraft.protein}
              onChange={(e) =>
                draft.updateMealDraft(mealDraft.id, {
                  protein: e.target.value,
                })
              }
            />
            <FieldError message={errors.protein} />
          </label>
          <label className="meal-macro-field">
            <span>Жиры</span>
            <input
              type="number"
              value={mealDraft.fat}
              onChange={(e) =>
                draft.updateMealDraft(mealDraft.id, { fat: e.target.value })
              }
            />
            <FieldError message={errors.fat} />
          </label>
          <label className="meal-macro-field">
            <span>Углеводы</span>
            <input
              type="number"
              value={mealDraft.carbohydrate}
              onChange={(e) =>
                draft.updateMealDraft(mealDraft.id, {
                  carbohydrate: e.target.value,
                })
              }
            />
            <FieldError message={errors.carbohydrate} />
          </label>
        </div>
      </>
    );
  };

  return (
    <Modal onClose={requestClose}>
      <div className="post-modal">
        {draft.editing ? (
          <>
            <input
              className="post-detail-title-input"
              value={draft.name}
              onChange={(e) => draft.setName(e.target.value)}
              placeholder="Название поста"
              required
            />
            <FieldError message={draft.submitted ? draft.nameError : null} />
          </>
        ) : (
          post && <h1 className="post-detail-title">{post.name}</h1>
        )}

        {post && (
          <span className="post-subtle">
            {formatPostDate(post.created_at)} · {mealsLabel(meals.length)}
          </span>
        )}

        {draft.editing ? (
          <>
            <textarea
              className="post-detail-textarea"
              value={draft.description}
              onChange={(e) => draft.setDescription(e.target.value)}
              placeholder="Описание"
            />
            <FieldError
              message={draft.submitted ? draft.descriptionError : null}
            />
          </>
        ) : (
          post?.description && <p className="post-desc">{post.description}</p>
        )}

        {post && (
          <>
            <div className="post-divider" />

            <div className="post-detail-grade-row">
              <div className="post-detail-grade-block">
                <span className="post-detail-grade-label">Оценка</span>
                <PostMark mark={post.mark} />
              </div>
              <div className="post-detail-grade-block">
                <span className="post-detail-grade-label">
                  Комментарий тренера
                </span>
                <p className="post-detail-comment">
                  {post.comment ?? "Комментария нет"}
                </p>
              </div>
            </div>
          </>
        )}

        <div className="post-divider" />

        <div className="post-modal-meals">
          <h2 className="post-detail-subheading">Милы</h2>

          <div className="meal-list">
            {draft.editing
              ? draft.mealDrafts.map((mealDraft) => {
                  const originalMeal =
                    meals.find((m) => m.id === mealDraft.id) ?? null;
                  return (
                    <div className="meal-card" key={mealDraft.id}>
                      <MealPhoto
                        meal={originalMeal}
                        editable
                        previewSrc={draft.photoPreviews[mealDraft.id]}
                        pictureUrl={posts.pictureUrl}
                        onSelectFile={(file) =>
                          draft.selectMealPhoto(mealDraft.id, file)
                        }
                      />
                      <div className="meal-info">
                        {renderMealFields(mealDraft)}
                      </div>
                      {draft.mealDrafts.length > MIN_POST_MEALS && (
                        <button
                          className="meal-remove-btn"
                          type="button"
                          onClick={() => draft.removeMealDraft(mealDraft.id)}
                          aria-label="Удалить мил"
                        >
                          ×
                        </button>
                      )}
                    </div>
                  );
                })
              : meals.map((meal) => (
                  <div className="meal-card" key={meal.id}>
                    <MealPhoto
                      meal={meal}
                      editable={false}
                      previewSrc={undefined}
                      pictureUrl={posts.pictureUrl}
                      onSelectFile={() => {}}
                    />
                    <div className="meal-info">
                      <span className="meal-name">
                        {meal.name ?? "Без названия"}
                      </span>
                      <div className="meal-macros">
                        <span>{macro(meal.cal, "ккал")}</span>
                        <span>Б: {macro(meal.protein, "г")}</span>
                        <span>Ж: {macro(meal.fat, "г")}</span>
                        <span>У: {macro(meal.carbohydrate, "г")}</span>
                      </div>
                    </div>
                  </div>
                ))}

            {draft.editing && draft.mealDrafts.length < MAX_POST_MEALS && (
              <button
                className="meal-add-card"
                type="button"
                onClick={() => draft.addMealDraft()}
              >
                <span className="meal-add-icon">+</span>
                Добавить мил
              </button>
            )}
          </div>
        </div>

        {draft.error && <p className="error">{draft.error}</p>}

        <div className="post-modal-actions">
          {isCreate ? (
            <>
              <button
                className="button"
                type="button"
                disabled={draft.pending}
                onClick={() => draft.handleCreate(onClose)}
              >
                <Save size={16} />
                {draft.pending ? "Создание…" : "Создать"}
              </button>
              <button
                className="button button-secondary"
                type="button"
                disabled={draft.pending}
                onClick={requestClose}
              >
                Отмена
              </button>
            </>
          ) : draft.editing ? (
            <>
              <button
                className="button"
                type="button"
                disabled={draft.pending}
                onClick={() => draft.handleUpdate()}
              >
                <Save size={16} />
                {draft.pending ? "Сохранение…" : "Сохранить"}
              </button>
              <button
                className="button button-secondary"
                type="button"
                disabled={draft.pending}
                onClick={() => draft.beginCancelEdit()}
              >
                Отмена
              </button>
            </>
          ) : (
            <>
              <button
                className="button"
                type="button"
                onClick={() => draft.startEdit()}
              >
                <Pencil size={16} />
                Редактировать
              </button>
              <button
                className="button button-secondary"
                type="button"
                onClick={() => draft.requestDelete()}
              >
                <Trash2 size={16} />
                Удалить
              </button>
            </>
          )}
        </div>
      </div>

      {draft.confirmingDelete && (
        <ConfirmDialog
          message="Удалить этот пост? Это действие нельзя отменить."
          confirmLabel="Да, удалить"
          pendingLabel="Удаление…"
          pending={draft.pending}
          onConfirm={() => draft.handleDelete(onClose)}
          onCancel={() => draft.dismissDelete()}
        />
      )}

      {draft.confirmingClose && (
        <ConfirmDialog
          message={
            isCreate
              ? "Закрыть без сохранения? Пост не будет создан, а введённые данные пропадут."
              : "Закрыть без сохранения? Внесённые изменения пропадут."
          }
          confirmLabel="Да, закрыть"
          pendingLabel="Закрытие…"
          pending={draft.pending}
          onConfirm={onClose}
          onCancel={() => draft.dismissClose()}
        />
      )}

      {draft.confirmingCancelEdit && (
        <ConfirmDialog
          message="Закрыть без сохранения? Внесённые изменения пропадут."
          confirmLabel="Да, закрыть"
          pendingLabel="Закрытие…"
          pending={draft.pending}
          onConfirm={() => draft.cancelEdit()}
          onCancel={() => draft.dismissCancelEdit()}
        />
      )}
    </Modal>
  );
});
