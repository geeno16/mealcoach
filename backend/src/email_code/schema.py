from datetime import datetime

from pydantic import BaseModel


class EmailCodeWrite(BaseModel):
    auth_id: int
    code_hash: str
    expires_at: datetime
