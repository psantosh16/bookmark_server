from datetime import datetime
from pydantic import BaseModel

class UserBookmark(BaseModel):
    bookmark_id: list[str]
    created_at: datetime
    updated_at: datetime