from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import datetime

from app.core.security import SECRET_KEY, ALGORITHM, get_api_token_hash
from app.database import get_db
from app import models, schemas

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

async def get_current_user(
    db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> models.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = schemas.TokenData(email=email)
        
        result = await db.execute(select(models.User).where(models.User.email == token_data.email))
        user = result.scalars().first()
    except JWTError:
        # Fallback to API Token
        if token.startswith("kmu_"):
            token_hash = get_api_token_hash(token)
            result = await db.execute(select(models.ApiToken).where(models.ApiToken.token_hash == token_hash))
            api_token = result.scalars().first()
            if api_token:
                if api_token.expires_at and api_token.expires_at < datetime.datetime.now():
                    raise credentials_exception
                
                user_result = await db.execute(select(models.User).where(models.User.id == api_token.user_id))
                user = user_result.scalars().first()
            else:
                raise credentials_exception
        else:
            raise credentials_exception
    
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
