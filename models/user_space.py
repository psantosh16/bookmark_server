from datetime import datetime
from pydantic import BaseModel


class UserSpace(BaseModel):
    space_id: str
    space_name: str
    bookmarks: list[str]
    created_at: datetime
    updated_at: datetime