from pydantic import BaseModel


class MigrationWrite(BaseModel):
    name: str
