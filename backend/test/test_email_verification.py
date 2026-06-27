from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.email_code import EmailCodeRepository
from test.helpers import (
    basic_email,
    basic_password,
    create_account,
    login,
    resend_code,
    verify_email,
)


def _wrong(code: str) -> str:
    return "000000" if code != "000000" else "111111"


@pytest.mark.asyncio
async def test_register_sends_code_unverified(
    async_client, captured_codes
):
    response = await create_account(
        basic_email, basic_password, async_client
    )

    assert response.status_code == 201
    assert response.json()["is_verified"] is False
    assert basic_email in captured_codes


@pytest.mark.asyncio
async def test_verify_with_correct_code(async_client, captured_codes):
    await create_account(basic_email, basic_password, async_client)
    response = await verify_email(basic_email, async_client)

    assert response.status_code == 200
    assert response.json()["is_verified"] is True


@pytest.mark.asyncio
async def test_verify_enables_login(async_client, captured_codes):
    await create_account(basic_email, basic_password, async_client)
    await verify_email(basic_email, async_client)

    response = await login(basic_email, basic_password, async_client)
    assert response.status_code == 200
    assert async_client.cookies.get("access_token")


@pytest.mark.asyncio
async def test_verify_unknown_email_fails(async_client):
    response = await verify_email(
        basic_email, async_client, code="123456"
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_verify_wrong_code_fails(async_client, captured_codes):
    await create_account(basic_email, basic_password, async_client)
    code = captured_codes[basic_email]

    response = await verify_email(
        basic_email, async_client, code=_wrong(code)
    )
    assert response.status_code == 401

    login_resp = await login(basic_email, basic_password, async_client)
    assert login_resp.status_code == 403


@pytest.mark.asyncio
async def test_verify_idempotent_when_already_verified(
    async_client, captured_codes
):
    await create_account(basic_email, basic_password, async_client)
    await verify_email(basic_email, async_client)

    again = await verify_email(basic_email, async_client, code="000000")
    assert again.status_code == 200
    assert again.json()["is_verified"] is True


@pytest.mark.asyncio
async def test_too_many_attempts_locks_code(
    async_client, captured_codes
):
    await create_account(basic_email, basic_password, async_client)
    code = captured_codes[basic_email]
    wrong = _wrong(code)

    for _ in range(5):
        resp = await verify_email(basic_email, async_client, code=wrong)
        assert resp.status_code == 401

    resp = await verify_email(basic_email, async_client, code=code)
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_expired_code_fails(
    async_client, captured_codes, db_session: AsyncSession
):
    response = await create_account(
        basic_email, basic_password, async_client
    )
    auth_id = response.json()["id"]
    code = captured_codes[basic_email]

    row = await EmailCodeRepository(db_session).get_active_by_auth_id(
        auth_id
    )
    assert row is not None
    row.expires_at = datetime.now(UTC) - timedelta(seconds=1)
    await db_session.commit()

    result = await verify_email(basic_email, async_client, code=code)
    assert result.status_code == 401


@pytest.mark.asyncio
async def test_register_rolls_back_on_mail_failure(
    async_client, monkeypatch
):
    async def boom(email: str, code: str) -> None:
        raise RuntimeError("smtp down")

    monkeypatch.setattr(
        "src.mailer.sender.send_verification_code", boom
    )

    response = await create_account(
        basic_email, basic_password, async_client
    )
    assert response.status_code == 502

    login_resp = await login(basic_email, basic_password, async_client)
    assert login_resp.status_code == 401


@pytest.mark.asyncio
async def test_resend_requires_correct_password(
    async_client, captured_codes
):
    await create_account(basic_email, basic_password, async_client)
    resp = await resend_code(basic_email, "wrongpass1", async_client)
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_resend_when_already_verified_fails(
    async_client, captured_codes
):
    await create_account(basic_email, basic_password, async_client)
    await verify_email(basic_email, async_client)

    resp = await resend_code(basic_email, basic_password, async_client)
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_resend_is_rate_limited(async_client, captured_codes):
    await create_account(basic_email, basic_password, async_client)
    resp = await resend_code(basic_email, basic_password, async_client)
    assert resp.status_code == 429


@pytest.mark.asyncio
async def test_resend_issues_new_working_code(
    async_client, captured_codes, db_session: AsyncSession
):
    response = await create_account(
        basic_email, basic_password, async_client
    )
    auth_id = response.json()["id"]

    row = await EmailCodeRepository(db_session).get_active_by_auth_id(
        auth_id
    )
    assert row is not None
    row.created_at = datetime.now(UTC) - timedelta(seconds=120)
    await db_session.commit()

    resp = await resend_code(basic_email, basic_password, async_client)
    assert resp.status_code == 200

    new_code = captured_codes[basic_email]
    verify = await verify_email(
        basic_email, async_client, code=new_code
    )
    assert verify.status_code == 200
    assert verify.json()["is_verified"] is True
