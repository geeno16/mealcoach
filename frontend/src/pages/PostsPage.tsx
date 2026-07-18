import { observer } from "mobx-react-lite";
import { useEffect } from "react";
import { Navigate } from "react-router-dom";

import { type PostRead } from "../api";
import { useStore } from "../root_store/StoreContext";

function PostMark({ mark }: { mark: number | null | undefined }) {
  if (mark === null || mark === undefined) {
    return <span className="post-unrated">Не оценено</span>;
  }
  return (
    <div className="post-stars">
      {[1, 2, 3, 4, 5].map((n) => (
        <span key={n} className={n <= mark ? "star star-filled" : "star"}>
          ★
        </span>
      ))}
    </div>
  );
}

function mealsLabel(count: number): string {
  const word = count === 1 ? "приём пищи" : "приёма пищи";
  return `${count} ${word}`;
}

function formatPostDate(iso: string): string {
  const date = new Date(iso);
  const day = String(date.getDate()).padStart(2, "0");
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const hours = String(date.getHours()).padStart(2, "0");
  const minutes = String(date.getMinutes()).padStart(2, "0");
  return `${day}.${month} ${hours}:${minutes}`;
}

function PostCard({ post }: { post: PostRead }) {
  const meals = post.meals ?? [];
  const pictureId = meals.find(
    (meal) => meal.picture_id !== null && meal.picture_id !== undefined,
  )?.picture_id;
  const hasPicture = pictureId !== null && pictureId !== undefined;
  const commentLabel = post.comment
    ? "Прокомментировано"
    : "Не прокомментировано";

  return (
    <article className="post-card">
      {hasPicture && (
        <div className="post-thumb">
          <img
            src={`/api/pictures/${pictureId}`}
            alt=""
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
}

export const PostsPage = observer(function PostsPage() {
  const { session, posts } = useStore();
  const user = session.user;

  useEffect(() => {
    if (user) void posts.load(user.auth_id);
  }, [posts, user]);

  if (!user) return <Navigate to="/app/fork" replace />;

  return (
    <div className="page">
      <h1>Посты</h1>

      {posts.error && <p className="error">{posts.error}</p>}

      {posts.items.length === 0 && !posts.loading ? (
        <p className="hint">Постов пока нет</p>
      ) : (
        <div className="post-list">
          {posts.items.map((post) => (
            <PostCard post={post} key={post.id} />
          ))}
        </div>
      )}
    </div>
  );
});
