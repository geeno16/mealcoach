import { useEffect, useRef, useState } from "react";

import { type MealRead, type PostRead, type PostWrite } from "../../api";
import { useStore } from "../../root_store/StoreContext";
import { ConfirmDialog, Modal } from "../../shared/Modal";
import { useAsyncAction } from "../../shared/useAsyncAction";

import { formatPostDate, mealsLabel, PostMark } from "./post-helpers";

const MIN_POST_MEALS = 1;
const MAX_POST_MEALS = 3;

type MealDraft = {
  id: number;
  name: string;
  cal: string;
  protein: string;
  fat: string;
  carbohydrate: string;
};

function emptyDraft(id: number): MealDraft {
  return { id, name: "", cal: "", protein: "", fat: "", carbohydrate: "" };
}

function toDraft(meal: MealRead): MealDraft {
  return {
    id: meal.id,
    name: meal.name ?? "",
    cal: meal.cal?.toString() ?? "",
    protein: meal.protein?.toString() ?? "",
    fat: meal.fat?.toString() ?? "",
    carbohydrate: meal.carbohydrate?.toString() ?? "",
  };
}

function toNumber(value: string): number | null {
  return value === "" ? null : Number(value);
}

function macro(value: number | null | undefined, unit: string): string {
  return value === null || value === undefined ? "—" : `${value} ${unit}`;
}

function revokePreviews(previews: Record<number, string>): void {
  Object.values(previews).forEach((url) => URL.revokeObjectURL(url));
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

  return (
    <div className="meal-thumb-wrap">
      {src && (
        <img
          className="meal-thumb"
          src={src}
          alt=""
          loading="lazy"
          decoding="async"
        />
      )}
      {editable && (
        <label className="meal-photo-btn">
          {src ? "Заменить фото" : "Добавить фото"}
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
      )}
    </div>
  );
}

export function PostModal({
  post,
  onClose,
}: {
  post: PostRead | null;
  onClose: () => void;
}) {
  const { posts, session } = useStore();
  const isCreate = post === null;

  const [editing, setEditing] = useState(isCreate);
  const [name, setName] = useState(post?.name ?? "");
  const [description, setDescription] = useState(post?.description ?? "");
  const nextDraftId = useRef(-1);
  const [mealDrafts, setMealDrafts] = useState<MealDraft[]>(() =>
    isCreate ? [emptyDraft(nextDraftId.current--)] : [],
  );
  const [photoFiles, setPhotoFiles] = useState<Record<number, File>>({});
  const [photoPreviews, setPhotoPreviews] = useState<Record<number, string>>(
    {},
  );
  const { pending, error, setError, run } = useAsyncAction();
  const [confirmingDelete, setConfirmingDelete] = useState(false);
  const [confirmingClose, setConfirmingClose] = useState(false);

  const photoPreviewsRef = useRef(photoPreviews);
  photoPreviewsRef.current = photoPreviews;

  useEffect(() => {
    return () => revokePreviews(photoPreviewsRef.current);
  }, []);

  const meals = post?.meals ?? [];

  const resetPhotoDrafts = () => {
    setPhotoPreviews((previews) => {
      revokePreviews(previews);
      return {};
    });
    setPhotoFiles({});
  };

  const startEdit = () => {
    setName(post!.name);
    setDescription(post!.description ?? "");
    setMealDrafts(meals.map(toDraft));
    resetPhotoDrafts();
    setError(null);
    setEditing(true);
  };

  const cancelEdit = () => {
    resetPhotoDrafts();
    setEditing(false);
  };

  const requestClose = () => {
    if (pending) return;
    if (isCreate) {
      setConfirmingClose(true);
      return;
    }
    onClose();
  };

  const updateMealDraft = (id: number, patch: Partial<MealDraft>) => {
    setMealDrafts((drafts) =>
      drafts.map((d) => (d.id === id ? { ...d, ...patch } : d)),
    );
  };

  const addMealDraft = () => {
    setMealDrafts((drafts) => {
      if (drafts.length >= MAX_POST_MEALS) return drafts;
      return [...drafts, emptyDraft(nextDraftId.current--)];
    });
  };

  const removeMealDraft = (id: number) => {
    setMealDrafts((drafts) => {
      if (drafts.length <= MIN_POST_MEALS) return drafts;
      return drafts.filter((d) => d.id !== id);
    });
    setPhotoFiles((files) => {
      if (!(id in files)) return files;
      const { [id]: _removed, ...rest } = files;
      return rest;
    });
    setPhotoPreviews((previews) => {
      const url = previews[id];
      if (!url) return previews;
      URL.revokeObjectURL(url);
      const { [id]: _removed, ...rest } = previews;
      return rest;
    });
  };

  const selectMealPhoto = (mealId: number, file: File) => {
    setPhotoFiles((files) => ({ ...files, [mealId]: file }));
    setPhotoPreviews((previews) => {
      const next = { ...previews };
      const old = next[mealId];
      if (old) URL.revokeObjectURL(old);
      next[mealId] = URL.createObjectURL(file);
      return next;
    });
  };

  const handleDelete = () =>
    run(
      async () => {
        await posts.deletePost(post!.id);
        onClose();
      },
      {
        fallbackMessage: "Не удалось удалить",
        onError: () => setConfirmingDelete(false),
      },
    );

  const handleUpdate = () =>
    run(
      async () => {
        for (const [mealId, file] of Object.entries(photoFiles)) {
          await posts.setMealPicture(post!.id, Number(mealId), file);
        }

        const payload: PostWrite = {
          auth_id: post!.auth_id,
          name,
          description: description || null,
          mark: post!.mark,
          comment: post!.comment,
          meals: mealDrafts.map((d) => ({
            name: d.name || null,
            cal: toNumber(d.cal),
            protein: toNumber(d.protein),
            fat: toNumber(d.fat),
            carbohydrate: toNumber(d.carbohydrate),
          })),
        };
        await posts.updatePost(post!.id, payload);

        resetPhotoDrafts();
        setEditing(false);
      },
      { fallbackMessage: "Не удалось сохранить" },
    );

  const handleCreate = () =>
    run(
      async () => {
        const payload: PostWrite = {
          auth_id: session.user!.auth_id,
          name,
          description: description || null,
          meals: mealDrafts.map((d) => ({
            name: d.name || null,
            cal: toNumber(d.cal),
            protein: toNumber(d.protein),
            fat: toNumber(d.fat),
            carbohydrate: toNumber(d.carbohydrate),
          })),
        };
        const created = await posts.createPost(payload);

        for (const [index, draft] of mealDrafts.entries()) {
          const file = photoFiles[draft.id];
          const createdMeal = created.meals?.[index];
          if (file && createdMeal) {
            await posts.setMealPicture(created.id, createdMeal.id, file);
          }
        }

        resetPhotoDrafts();
        onClose();
      },
      { fallbackMessage: "Не удалось создать пост" },
    );

  const renderMealFields = (draft: MealDraft) => (
    <>
      <input
        className="meal-name-input"
        value={draft.name}
        onChange={(e) => updateMealDraft(draft.id, { name: e.target.value })}
        placeholder="Название"
      />
      <div className="meal-macro-inputs">
        <label className="meal-macro-field">
          <span>Ккал</span>
          <input
            type="number"
            value={draft.cal}
            onChange={(e) => updateMealDraft(draft.id, { cal: e.target.value })}
          />
        </label>
        <label className="meal-macro-field">
          <span>Белки</span>
          <input
            type="number"
            value={draft.protein}
            onChange={(e) =>
              updateMealDraft(draft.id, { protein: e.target.value })
            }
          />
        </label>
        <label className="meal-macro-field">
          <span>Жиры</span>
          <input
            type="number"
            value={draft.fat}
            onChange={(e) => updateMealDraft(draft.id, { fat: e.target.value })}
          />
        </label>
        <label className="meal-macro-field">
          <span>Углеводы</span>
          <input
            type="number"
            value={draft.carbohydrate}
            onChange={(e) =>
              updateMealDraft(draft.id, { carbohydrate: e.target.value })
            }
          />
        </label>
      </div>
    </>
  );

  return (
    <Modal onClose={requestClose}>
      <div className="post-modal">
        {editing ? (
          <input
            className="post-detail-title-input"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Название поста"
            required
          />
        ) : (
          <h1 className="post-detail-title">{post!.name}</h1>
        )}

        {!isCreate && (
          <span className="post-subtle">
            {formatPostDate(post.created_at)} · {mealsLabel(meals.length)}
          </span>
        )}

        {editing ? (
          <textarea
            className="post-detail-textarea"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Описание"
          />
        ) : (
          post!.description && <p className="post-desc">{post!.description}</p>
        )}

        {!isCreate && (
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
            {isCreate
              ? mealDrafts.map((draft) => (
                  <div className="meal-card" key={draft.id}>
                    <MealPhoto
                      meal={null}
                      editable
                      previewSrc={photoPreviews[draft.id]}
                      pictureUrl={posts.pictureUrl}
                      onSelectFile={(file) => selectMealPhoto(draft.id, file)}
                    />
                    <div className="meal-info">{renderMealFields(draft)}</div>
                    {mealDrafts.length > MIN_POST_MEALS && (
                      <button
                        className="meal-remove-btn"
                        type="button"
                        onClick={() => removeMealDraft(draft.id)}
                        aria-label="Удалить мил"
                      >
                        ×
                      </button>
                    )}
                  </div>
                ))
              : meals.map((meal) => {
                  const draft = mealDrafts.find((d) => d.id === meal.id);
                  return (
                    <div className="meal-card" key={meal.id}>
                      <MealPhoto
                        meal={meal}
                        editable={editing}
                        previewSrc={photoPreviews[meal.id]}
                        pictureUrl={posts.pictureUrl}
                        onSelectFile={(file) => selectMealPhoto(meal.id, file)}
                      />
                      <div className="meal-info">
                        {editing && draft ? (
                          renderMealFields(draft)
                        ) : (
                          <>
                            <span className="meal-name">
                              {meal.name ?? "Без названия"}
                            </span>
                            <div className="meal-macros">
                              <span>{macro(meal.cal, "ккал")}</span>
                              <span>Б: {macro(meal.protein, "г")}</span>
                              <span>Ж: {macro(meal.fat, "г")}</span>
                              <span>У: {macro(meal.carbohydrate, "г")}</span>
                            </div>
                          </>
                        )}
                      </div>
                    </div>
                  );
                })}

            {isCreate && mealDrafts.length < MAX_POST_MEALS && (
              <button
                className="meal-add-card"
                type="button"
                onClick={addMealDraft}
              >
                <span className="meal-add-icon">+</span>
                Добавить мил
              </button>
            )}
          </div>
        </div>

        {error && <p className="error">{error}</p>}

        <div className="post-modal-actions">
          {isCreate ? (
            <>
              <button
                className="button"
                type="button"
                disabled={pending}
                onClick={handleCreate}
              >
                {pending ? "Создание…" : "Создать"}
              </button>
              <button
                className="button button-secondary"
                type="button"
                disabled={pending}
                onClick={requestClose}
              >
                Отмена
              </button>
            </>
          ) : editing ? (
            <>
              <button
                className="button"
                type="button"
                disabled={pending}
                onClick={handleUpdate}
              >
                {pending ? "Сохранение…" : "Сохранить"}
              </button>
              <button
                className="button button-secondary"
                type="button"
                disabled={pending}
                onClick={cancelEdit}
              >
                Отмена
              </button>
            </>
          ) : (
            <>
              <button className="button" type="button" onClick={startEdit}>
                Редактировать
              </button>
              <button
                className="button button-secondary"
                type="button"
                onClick={() => setConfirmingDelete(true)}
              >
                Удалить
              </button>
            </>
          )}
        </div>
      </div>

      {confirmingDelete && (
        <ConfirmDialog
          message="Удалить этот пост? Это действие нельзя отменить."
          confirmLabel="Да, удалить"
          pendingLabel="Удаление…"
          pending={pending}
          onConfirm={handleDelete}
          onCancel={() => setConfirmingDelete(false)}
        />
      )}

      {confirmingClose && (
        <ConfirmDialog
          message="Закрыть без сохранения? Пост не будет создан, а введённые данные пропадут."
          confirmLabel="Да, закрыть"
          pendingLabel="Закрытие…"
          pending={pending}
          onConfirm={onClose}
          onCancel={() => setConfirmingClose(false)}
        />
      )}
    </Modal>
  );
}
