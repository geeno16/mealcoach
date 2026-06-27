import asyncio
import json
import sys
from getpass import getpass

import httpx

BASE = "http://localhost:8000"


def _show(label: str, response: httpx.Response) -> None:
    print(f"\n[{label}] -> HTTP {response.status_code}")
    try:
        print(json.dumps(response.json(), ensure_ascii=False, indent=2))
    except ValueError:
        print(response.text or "(пустой ответ)")


def _run_flow(email: str, password: str) -> bool:
    creds = {"email": email, "password": password}

    with httpx.Client(base_url=BASE, timeout=30) as client:
        _show("РЕГИСТРАЦИЯ", client.post("/api/auth", json=creds))

        verified = False
        while not verified:
            choice = input(
                "\nКод из письма | 'r' — переотправить | 's' — пропустить: "
            ).strip()
            if choice.lower() == "s":
                break
            if choice.lower() == "r":
                _show(
                    "ПЕРЕОТПРАВКА КОДА",
                    client.post("/api/auth/resend-code", json=creds),
                )
                continue

            response = client.post(
                "/api/auth/verify-email",
                json={"email": email, "code": choice},
            )
            _show("ПОДТВЕРЖДЕНИЕ", response)
            verified = response.status_code == 200

        if not verified:
            return False

        _show("ЛОГИН", client.post("/api/auth/login", json=creds))
        token = client.cookies.get("access_token")
        print(f"\nКука access_token: {'установлена' if token else 'нет'}")

        if input("\nВыйти (logout)? (y/N): ").strip().lower() == "y":
            _show("ЛОГАУТ", client.post("/api/auth/logout"))

    return True


def main() -> None:
    email = input("Email: ").strip()
    password = getpass("Пароль: ")

    _run_flow(email, password)

    if input("\nУдалить тестовый аккаунт из БД? (Y/n): ").strip().lower() != "n":
        from src.common.delete_auth_vstask import _delete

        asyncio.run(_delete(email))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nПрервано.")
        sys.exit(1)
