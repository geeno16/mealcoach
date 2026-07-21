import { Link } from "react-router-dom";

export function LandingPage() {
  return (
    <div className="screen">
      <div className="card">
        <h1>Mealcoach</h1>
        <div className="actions">
          <Link className="button" to="/app/login">
            Войти
          </Link>
          <Link className="button button-secondary" to="/app/signup">
            Регистрация
          </Link>
        </div>
      </div>
    </div>
  );
}
