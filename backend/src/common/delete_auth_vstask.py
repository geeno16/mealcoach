import asyncio
import sys

from sqlalchemy.ext.asyncio import async_sessionmaker

from src.auth.repository import AuthRepository
from src.common.database import engine
from src.email_code.repository import EmailCodeRepository


async def _delete(email: str) -> None:
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        auth = await AuthRepository(session).get_by_email(email)
        if auth is None:
            print(f"Аккаунт {email} не найден")
            return
        await EmailCodeRepository(session).delete_by_auth_id(auth.id)
        await AuthRepository(session).delete_by_id(auth.id)
        print(f"Удалён аккаунт {email} (id={auth.id}) и его коды")
    await engine.dispose()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: python -m src.common.delete_auth_vstask <email>")
        sys.exit(1)
    asyncio.run(_delete(sys.argv[1]))
