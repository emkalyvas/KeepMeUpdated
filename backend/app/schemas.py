from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# --- Channel Schemas ---
class ChannelBase(BaseModel):
    plugin_id: str
    name: str
    config: Dict[str, Any] = {}
    is_active: bool = False

class ChannelCreate(ChannelBase):
    pass

class ChannelUpdate(BaseModel):
    name: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

class ChannelResponse(ChannelBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# --- Notification Schemas ---
class NotificationBase(BaseModel):
    channel_id: int
    title: str
    payload: Optional[str] = None
    schedule_type: str
    schedule_expr: str
    parameters: Dict[str, Any] = {}
    is_active: bool = True

class NotificationCreate(NotificationBase):
    pass

class NotificationUpdate(BaseModel):
    channel_id: Optional[int] = None
    title: Optional[str] = None
    payload: Optional[str] = None
    schedule_type: Optional[str] = None
    schedule_expr: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

class NotificationResponse(NotificationBase):
    id: int
    user_id: int
    next_run_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# --- Repository Schemas ---
class RepositoryBase(BaseModel):
    name: str
    url: str

class RepositoryCreate(RepositoryBase):
    pass

class RepositoryResponse(RepositoryBase):
    id: int
    is_official: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
