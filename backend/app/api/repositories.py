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

@router.get("/{repository_id}/plugins", response_model=List[dict])
async def read_repository_plugins(
    repository_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    from app.plugins.manager import plugin_manager
    plugins = await plugin_manager.get_repo_plugins(db, repository_id)
    if not plugins:
        # Check if repo exists
        result = await db.execute(select(models.Repository).where(models.Repository.id == repository_id))
        repo = result.scalars().first()
        if not repo:
            raise HTTPException(status_code=404, detail="Repository not found")
    return plugins

@router.post("/install")
async def install_plugin(
    install_req: schemas.PluginInstallRequest,
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    from app.plugins.manager import plugin_manager
    success = await plugin_manager.install_plugin(
        install_req.plugin_id, 
        install_req.version, 
        install_req.full_file_url,
        install_req.requirements
    )
    if not success:
        raise HTTPException(status_code=400, detail="Failed to install plugin")
    return {"status": "ok", "message": "Plugin installed successfully"}

@router.post("/uninstall")
async def uninstall_plugin(
    uninstall_req: schemas.PluginUninstallRequest,
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    from app.plugins.manager import plugin_manager
    success = plugin_manager.uninstall_plugin(uninstall_req.plugin_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to uninstall plugin")
    return {"status": "ok", "message": "Plugin uninstalled successfully"}

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
        
    if db_repo.is_official:
        raise HTTPException(status_code=400, detail="Cannot delete an official repository")
        
    await db.delete(db_repo)
    await db.commit()
    return {"status": "ok"}
