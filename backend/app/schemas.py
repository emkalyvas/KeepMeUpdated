from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any, List
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
    exclusions: Optional[List[Dict[str, Any]]] = []
    start_time: Optional[datetime] = None
    is_active: bool = True
    execution_count: int = 0

class NotificationCreate(NotificationBase):
    pass

class NotificationUpdate(BaseModel):
    channel_id: Optional[int] = None
    title: Optional[str] = None
    payload: Optional[str] = None
    schedule_type: Optional[str] = None
    schedule_expr: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    exclusions: Optional[List[Dict[str, Any]]] = None
    start_time: Optional[datetime] = None
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

class DataSourceBase(BaseModel):
    plugin_id: str
    name: str
    config: Dict[str, Any] = {}
    is_active: bool = False

class DataSourceCreate(DataSourceBase):
    pass

class DataSourceUpdate(BaseModel):
    name: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

class DataSourceResponse(DataSourceBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class CustomVariableBase(BaseModel):
    name: str
    value: str

class CustomVariableCreate(CustomVariableBase):
    pass

class CustomVariableUpdate(BaseModel):
    name: Optional[str] = None
    value: Optional[str] = None

class CustomVariableResponse(CustomVariableBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# --- Plugin Schemas ---
class PluginInstallRequest(BaseModel):
    plugin_id: str
    version: str
    full_file_url: str
    requirements: Optional[List[str]] = []

class PluginUninstallRequest(BaseModel):
    plugin_id: str

# --- API Token Schemas ---
class ApiTokenBase(BaseModel):
    name: str
    expires_at: Optional[datetime] = None

class ApiTokenCreate(ApiTokenBase):
    pass

class ApiTokenResponse(ApiTokenBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ApiTokenCreateResponse(ApiTokenResponse):
    token: str
