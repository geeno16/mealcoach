import { observer } from "mobx-react-lite";
import { useEffect } from "react";
import { Navigate } from "react-router-dom";

import { type PostRead } from "../api";
import { useStore } from "../root_store/StoreContext";

function PostCard({ post }: { post: PostRead }) {
  return (
    <article className="post-card">
      <div className="post-images">
        {(post.meals ?? []).map((meal) => (
          <div className="post-image" key={meal.id} />
        ))}
      </div>
      <h2 className="post-name">{post.name}</h2>
      {post.description && <p className="post-desc">{post.description}</p>}
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
