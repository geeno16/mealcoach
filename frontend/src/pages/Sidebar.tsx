import { observer } from "mobx-react-lite";
import { NavLink } from "react-router-dom";

import { useStore } from "../root_store/StoreContext";

type Item = { to: string; label: string };

export const Sidebar = observer(function Sidebar() {
  const { session } = useStore();
  const user = session.user;
  if (!user) return null;

  const items: Item[] = [
    { to: "/app/profile", label: "Профиль" },
    { to: "/app/notifications", label: "Уведомления" },
  ];
  if (user.role === "trainee") {
    items.push({ to: "/app/posts", label: "Посты" });
    items.push({ to: "/app/stats", label: "Статистика" });
  }
  if (user.role === "coach") {
    items.push({ to: "/app/trainees", label: "Ученики" });
  }

  return (
    <nav className="sidebar">
      <div className="sidebar-title">Mealcoach</div>
      {items.map((item) => (
        <NavLink
          key={item.to}
          to={item.to}
          className={({ isActive }) =>
            isActive ? "nav-link nav-link-active" : "nav-link"
          }
        >
          {item.label}
        </NavLink>
      ))}
    </nav>
  );
});
