from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app import models, schemas
from app.api import deps
from app.database import get_db
from app.core import security

router = APIRouter()

@router.get("/", response_model=List[schemas.ApiTokenResponse])
async def read_api_tokens(
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Retrieve all API tokens for the current user.
    """
    result = await db.execute(select(models.ApiToken).where(models.ApiToken.user_id == current_user.id))
    return result.scalars().all()

@router.post("/", response_model=schemas.ApiTokenCreateResponse)
async def create_api_token(
    token_in: schemas.ApiTokenCreate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Create a new API token. The raw token is returned exactly once in this response.
    """
    raw_token = security.generate_api_token()
    token_hash = security.get_api_token_hash(raw_token)
    
    new_token = models.ApiToken(
        user_id=current_user.id,
        name=token_in.name,
        token_hash=token_hash,
        expires_at=token_in.expires_at,
    )
    db.add(new_token)
    await db.commit()
    await db.refresh(new_token)
    
    base_response = schemas.ApiTokenResponse.model_validate(new_token)
    response = schemas.ApiTokenCreateResponse(
        **base_response.model_dump(),
        token=raw_token
    )
    return response

@router.delete("/{token_id}")
async def delete_api_token(
    token_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Delete (revoke) an API token.
    """
    result = await db.execute(
        select(models.ApiToken)
        .where(models.ApiToken.id == token_id)
        .where(models.ApiToken.user_id == current_user.id)
    )
    token = result.scalars().first()
    if not token:
        raise HTTPException(status_code=404, detail="API token not found")
    
    await db.delete(token)
    await db.commit()
    return {"ok": True}
