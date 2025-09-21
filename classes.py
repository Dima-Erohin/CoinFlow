from pydantic import BaseModel

class UserIn(BaseModel):
    id: int
    username: str | None
    phone: str | None