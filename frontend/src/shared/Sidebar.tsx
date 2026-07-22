import { BarChart3, Bell, User, Users, UtensilsCrossed } from "lucide-react";
import { observer } from "mobx-react-lite";
import { NavLink } from "react-router-dom";

import { useStore } from "../root_store/StoreContext";

type Item = { to: string; label: string; icon: typeof User };

export const Sidebar = observer(function Sidebar() {
  const { session } = useStore();
  const user = session.user;
  if (!user) return null;

  const items: Item[] = [
    { to: "/app/profile", label: "Профиль", icon: User },
    { to: "/app/notifications", label: "Уведомления", icon: Bell },
  ];
  if (user.role === "trainee") {
    items.push({ to: "/app/posts", label: "Посты", icon: UtensilsCrossed });
    items.push({ to: "/app/stats", label: "Статистика", icon: BarChart3 });
  }
  if (user.role === "coach") {
    items.push({ to: "/app/trainees", label: "Ученики", icon: Users });
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
          <item.icon className="nav-link-icon" size={18} />
          {item.label}
        </NavLink>
      ))}
    </nav>
  );
});
