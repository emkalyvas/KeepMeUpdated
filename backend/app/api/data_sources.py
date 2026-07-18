from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app import models, schemas
from app.api import deps
from app.database import get_db
from app.plugins.manager import plugin_manager
from app.utils import sanitize_prefix

router = APIRouter()

@router.get("/plugins", response_model=List[dict])
async def read_plugins() -> Any:
    return plugin_manager.get_all_plugins()

@router.get("/", response_model=List[schemas.DataSourceResponse])
async def read_data_sources(
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    result = await db.execute(select(models.DataSource).where(models.DataSource.user_id == current_user.id))
    return result.scalars().all()

@router.post("/test")
async def test_data_source(
    data_source_in: schemas.DataSourceCreate,
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    plugin_class = plugin_manager.get_datasource_plugin(data_source_in.plugin_id)
    if not plugin_class:
        raise HTTPException(status_code=400, detail="Invalid plugin_id")
        
    plugin_instance = plugin_class(data_source_in.config)
    if not plugin_instance.validate_config():
        raise HTTPException(status_code=400, detail="Invalid configuration")
        
    try:
        context = await plugin_instance.fetch_context()
        if isinstance(context, dict):
            prefix = sanitize_prefix(data_source_in.name)
            prefixed_context = {f"{prefix}_{k}": v for k, v in context.items()}
            return {"status": "ok", "context": prefixed_context}
        else:
            raise HTTPException(status_code=400, detail="Data source returned invalid context")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/", response_model=schemas.DataSourceResponse)
async def create_data_source(
    data_source_in: schemas.DataSourceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    plugin_class = plugin_manager.get_datasource_plugin(data_source_in.plugin_id)
    if not plugin_class:
        raise HTTPException(status_code=400, detail="Invalid plugin_id")
        
    db_data_source = models.DataSource(**data_source_in.model_dump(), user_id=current_user.id)
    
    if db_data_source.is_active:
        plugin_instance = plugin_class(db_data_source.config)
        if not plugin_instance.validate_config():
            db_data_source.is_active = False # Force inactive if invalid config
            
    db.add(db_data_source)
    await db.commit()
    await db.refresh(db_data_source)
    return db_data_source

@router.put("/{data_source_id}", response_model=schemas.DataSourceResponse)
async def update_data_source(
    data_source_id: int,
    data_source_in: schemas.DataSourceUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    result = await db.execute(select(models.DataSource).where(
        models.DataSource.id == data_source_id, 
        models.DataSource.user_id == current_user.id
    ))
    db_data_source = result.scalars().first()
    if not db_data_source:
        raise HTTPException(status_code=404, detail="DataSource not found")
        
    update_data = data_source_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_data_source, field, value)
        
    if db_data_source.is_active:
        plugin_class = plugin_manager.get_datasource_plugin(db_data_source.plugin_id)
        if plugin_class:
            plugin_instance = plugin_class(db_data_source.config)
            if not plugin_instance.validate_config():
                db_data_source.is_active = False # Force inactive
                
    await db.commit()
    await db.refresh(db_data_source)
    return db_data_source

@router.delete("/{data_source_id}")
async def delete_data_source(
    data_source_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    result = await db.execute(select(models.DataSource).where(
        models.DataSource.id == data_source_id, 
        models.DataSource.user_id == current_user.id
    ))
    db_data_source = result.scalars().first()
    if not db_data_source:
        raise HTTPException(status_code=404, detail="DataSource not found")
        
    await db.delete(db_data_source)
    await db.commit()
    return {"status": "ok"}
