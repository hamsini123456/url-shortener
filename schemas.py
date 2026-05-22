from pydantic import BaseModel
from datetime import datetime

class URLCreate(BaseModel):
    long_url: str

class URLResponse(BaseModel):
    short_code: str
    short_url:  str
    long_url:   str
    hit_count:  int
    created_at: datetime

    class Config:
        from_attributes = True