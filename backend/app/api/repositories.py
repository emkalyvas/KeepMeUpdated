from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app import models, schemas
from app.api import deps
from app.database import get_db

router = APIRouter()

@router.get("/", response_model=List[schemas.RepositoryResponse])
async def read_repositories(
    db: AsyncSession = Depends(get_db)
) -> Any:
    # Repositories are system-wide
    result = await db.execute(select(models.Repository))
    return result.scalars().all()

@router.post("/sync")
async def sync_repositories(
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    from app.plugins.manager import plugin_manager
    await plugin_manager.sync_plugins(db)
    return {"status": "ok", "message": "Plugins synced successfully"}

@router.post("/", response_model=schemas.RepositoryResponse)
async def create_repository(
    repo_in: schemas.RepositoryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    db_repo = models.Repository(**repo_in.model_dump())
    db.add(db_repo)
    await db.commit()
    await db.refresh(db_repo)
    return db_repo

@router.delete("/{repository_id}")
async def delete_repository(
    repository_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    result = await db.execute(select(models.Repository).where(models.Repository.id == repository_id))
    db_repo = result.scalars().first()
    if not db_repo:
        raise HTTPException(status_code=404, detail="Repository not found")
        
    await db.delete(db_repo)
    await db.commit()
    return {"status": "ok"}
