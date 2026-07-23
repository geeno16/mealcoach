import { ChevronLeft, ChevronRight, Plus } from "lucide-react";
import { observer } from "mobx-react-lite";
import { useEffect, useMemo, useRef, useState } from "react";
import { Navigate } from "react-router-dom";

import { type PostRead } from "../../api";
import { useStore } from "../../root_store/StoreContext";
import { Loader } from "../../shared/Loader";

import { PostModal } from "./PostModal";
import {
  formatDayTotals,
  formatPostDate,
  groupPostsByDate,
  mealsLabel,
  PostMark,
} from "./post-helpers";
import { usePostColumns } from "./usePostColumns";

const PostCard = observer(function PostCard({
  post,
  onOpen,
}: {
  post: PostRead;
  onOpen: () => void;
}) {
  const { posts } = useStore();
  const meals = post.meals ?? [];
  const pictureMeal = meals.find(
    (meal) => meal.picture_id !== null && meal.picture_id !== undefined,
  );
  const commentLabel = post.comment
    ? "Прокомментировано"
    : "Не прокомментировано";

  const hasPicture =
    pictureMeal !== undefined &&
    pictureMeal.picture_id !== null &&
    pictureMeal.picture_id !== undefined;

  return (
    <article className="post-card" onClick={onOpen}>
      {hasPicture && (
        <div className="post-thumb">
          <img
            src={posts.pictureUrl(pictureMeal.picture_id!, pictureMeal.id)}
            alt=""
            width={pictureMeal.picture_width ?? undefined}
            height={pictureMeal.picture_height ?? undefined}
            loading="lazy"
            decoding="async"
          />
        </div>
      )}
      <div className="post-content">
        <h2 className="post-name">{post.name}</h2>
        {post.description && <p className="post-desc">{post.description}</p>}
        <div className="post-divider" />
        <div className="post-foot">
          <div className="post-foot-col">
            <span>{mealsLabel(meals.length)}</span>
            <span className="post-subtle">
              {formatPostDate(post.created_at)}
            </span>
          </div>
          <div className="post-foot-col post-foot-right">
            <PostMark mark={post.mark} />
            <span className="post-subtle">{commentLabel}</span>
          </div>
        </div>
      </div>
    </article>
  );
});

export const PostsPage = observer(function PostsPage() {
  const { session, posts } = useStore();
  const user = session.user;
  const [openId, setOpenId] = useState<number | null>(null);
  const [creating, setCreating] = useState(false);
  const [anchorIndex, setAnchorIndex] = useState(0);
  const columns = usePostColumns();
  const initializedRef = useRef(false);

  useEffect(() => {
    if (user) void posts.load(user.auth_id);
  }, [posts, user]);

  const groups = useMemo(() => groupPostsByDate(posts.items), [posts.items]);
  const maxAnchor = Math.max(0, groups.length - columns);

  useEffect(() => {
    if (groups.length === 0) return;
    if (!initializedRef.current) {
      initializedRef.current = true;
      setAnchorIndex(maxAnchor);
      return;
    }
    setAnchorIndex((prev) => Math.min(prev, maxAnchor));
  }, [maxAnchor, groups.length]);

  if (!user) return <Navigate to="/app/fork" replace />;

  const openPost =
    openId !== null ? posts.items.find((p) => p.id === openId) : undefined;

  const openCard = (post: PostRead) => (
    <PostCard post={post} key={post.id} onOpen={() => setOpenId(post.id)} />
  );

  const visibleGroups = groups.slice(anchorIndex, anchorIndex + columns);
  const prevDisabled = anchorIndex === 0;
  const nextDisabled = anchorIndex >= maxAnchor;

  return (
    <div className="page">
      <div className="page-header">
        <h1>Посты</h1>
        {user.role === "trainee" && (
          <button
            className="button"
            type="button"
            onClick={() => setCreating(true)}
          >
            <Plus size={16} />
            Создать пост
          </button>
        )}
      </div>

      {posts.error && <p className="error">{posts.error}</p>}

      {posts.loading && posts.items.length === 0 ? (
        <Loader />
      ) : posts.items.length === 0 ? (
        <p className="hint">Постов пока нет</p>
      ) : columns === 1 ? (
        <div className="post-date-flow">
          {[...groups].reverse().map((group) => (
            <div className="post-date-section" key={group.dateKey}>
              <div className="post-date-divider-label">{group.label}</div>
              <div className="post-date-divider-totals">
                {formatDayTotals(group.totals)}
              </div>
              <div className="post-date-divider-line" />
              <div className="post-date-flow-cards">
                {group.posts.map(openCard)}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="post-date-row">
          <button
            className="post-date-arrow"
            type="button"
            disabled={prevDisabled}
            onClick={() => setAnchorIndex((i) => Math.max(0, i - columns))}
            aria-label="Более старые даты"
          >
            <ChevronLeft size={20} />
          </button>

          <div
            className="post-date-grid"
            style={{
              gridTemplateColumns: `repeat(${visibleGroups.length}, minmax(0, 1fr))`,
            }}
          >
            {visibleGroups.map((group) => (
              <div className="post-date-col" key={group.dateKey}>
                <div className="post-date-col-header">{group.label}</div>
                <div className="post-date-col-totals">
                  {formatDayTotals(group.totals)}
                </div>
                <div className="post-date-col-line" />
                <div className="post-date-col-cards">
                  {group.posts.map(openCard)}
                </div>
              </div>
            ))}
          </div>

          <button
            className="post-date-arrow"
            type="button"
            disabled={nextDisabled}
            onClick={() =>
              setAnchorIndex((i) => Math.min(maxAnchor, i + columns))
            }
            aria-label="Более новые даты"
          >
            <ChevronRight size={20} />
          </button>
        </div>
      )}

      {openPost && (
        <PostModal post={openPost} onClose={() => setOpenId(null)} />
      )}

      {creating && <PostModal post={null} onClose={() => setCreating(false)} />}
    </div>
  );
});
