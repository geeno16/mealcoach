import { Plus } from "lucide-react";
import { observer } from "mobx-react-lite";
import { useEffect, useState } from "react";
import { Navigate } from "react-router-dom";

import { type PostRead } from "../../api";
import { useStore } from "../../root_store/StoreContext";
import { Loader } from "../../shared/Loader";

import { PostModal } from "./PostModal";
import { formatPostDate, mealsLabel, PostMark } from "./post-helpers";

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

  useEffect(() => {
    if (user) void posts.load(user.auth_id);
  }, [posts, user]);

  if (!user) return <Navigate to="/app/fork" replace />;

  const openPost =
    openId !== null ? posts.items.find((p) => p.id === openId) : undefined;

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
      ) : (
        <div className="post-list">
          {posts.items.map((post) => (
            <PostCard
              post={post}
              key={post.id}
              onOpen={() => setOpenId(post.id)}
            />
          ))}
        </div>
      )}

      {openPost && (
        <PostModal post={openPost} onClose={() => setOpenId(null)} />
      )}

      {creating && <PostModal post={null} onClose={() => setCreating(false)} />}
    </div>
  );
});
