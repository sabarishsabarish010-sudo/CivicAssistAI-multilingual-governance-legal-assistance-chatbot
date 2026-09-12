from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class UserCreate(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=100)
    name: Optional[str] = Field(default=None, max_length=200)
    state: Optional[str] = Field(default=None, max_length=100)
    language: str = Field(default="en", min_length=2, max_length=20)
    mobile: Optional[str] = Field(default=None, max_length=30)


class UserUpdate(BaseModel):
    name: Optional[str] = Field(default=None, max_length=200)
    state: Optional[str] = Field(default=None, max_length=100)
    language: Optional[str] = Field(default=None, min_length=2, max_length=20)
    mobile: Optional[str] = Field(default=None, max_length=30)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: str
    name: Optional[str] = None
    state: Optional[str] = None
    language: str
    mobile: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    