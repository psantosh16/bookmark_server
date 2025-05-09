from datetime import datetime
from pydantic import BaseModel


class Bookmark(BaseModel):
    title: str
    description: str
    created_at: datetime
    image_url: str
    author_id: str
    source_url: str
    source_type: str
