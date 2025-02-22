from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class URLBase(BaseModel):
    url: str
    title: Optional[str] = None
    description: Optional[str] = None
    image: Optional[str] = None

class URLCreate(URLBase):
    pass

class URL(URLBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode: True