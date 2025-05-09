from datetime import datetime
from pydantic import BaseModel

class User(BaseModel):
    uid: str
    name: str
    email: str
    avatar: str
    created_at: datetime
    updated_at: datetime