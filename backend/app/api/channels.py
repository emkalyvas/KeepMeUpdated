from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app import models, schemas
from app.api import deps
from app.database import get_db
from app.plugins.manager import plugin_manager

router = APIRouter()

@router.get("/plugins", response_model=List[dict])
async def read_plugins() -> Any:
    return plugin_manager.get_all_plugins()

@router.get("/", response_model=List[schemas.ChannelResponse])
async def read_channels(
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    result = await db.execute(select(models.Channel).where(models.Channel.user_id == current_user.id))
    return result.scalars().all()

@router.post("/test")
async def test_channel(
    channel_in: schemas.ChannelCreate,
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    plugin_class = plugin_manager.get_channel_plugin(channel_in.plugin_id)
    if not plugin_class:
        raise HTTPException(status_code=400, detail="Invalid plugin_id")
        
    plugin_instance = plugin_class(channel_in.config)
    if not plugin_instance.validate_config():
        raise HTTPException(status_code=400, detail="Invalid configuration")
        
    try:
        success = await plugin_instance.send(
            title="KeepMeUpdated Test",
            payload="This is a test notification from KeepMeUpdated.",
            parameters={}
        )
        if success:
            return {"status": "ok"}
        else:
            raise HTTPException(status_code=400, detail="Test notification failed to send")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/options/{plugin_id}/{field_name}", response_model=List[Any])
async def get_plugin_options(
    plugin_id: str,
    field_name: str,
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    plugin_class = plugin_manager.get_channel_plugin(plugin_id)
    if not plugin_class:
        raise HTTPException(status_code=400, detail="Invalid plugin_id")
        
    try:
        options = await plugin_class.get_dynamic_options(field_name)
        return options
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/", response_model=schemas.ChannelResponse)
async def create_channel(
    channel_in: schemas.ChannelCreate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    plugin_class = plugin_manager.get_channel_plugin(channel_in.plugin_id)
    if not plugin_class:
        raise HTTPException(status_code=400, detail="Invalid plugin_id")
        
    db_channel = models.Channel(**channel_in.model_dump(), user_id=current_user.id)
    
    if db_channel.is_active:
        plugin_instance = plugin_class(db_channel.config)
        if not plugin_instance.validate_config():
            db_channel.is_active = False # Force inactive if invalid config
            
    db.add(db_channel)
    await db.commit()
    await db.refresh(db_channel)
    return db_channel

@router.put("/{channel_id}", response_model=schemas.ChannelResponse)
async def update_channel(
    channel_id: int,
    channel_in: schemas.ChannelUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    result = await db.execute(select(models.Channel).where(
        models.Channel.id == channel_id, 
        models.Channel.user_id == current_user.id
    ))
    db_channel = result.scalars().first()
    if not db_channel:
        raise HTTPException(status_code=404, detail="Channel not found")
        
    update_data = channel_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_channel, field, value)
        
    if db_channel.is_active:
        plugin_class = plugin_manager.get_channel_plugin(db_channel.plugin_id)
        if plugin_class:
            plugin_instance = plugin_class(db_channel.config)
            if not plugin_instance.validate_config():
                db_channel.is_active = False # Force inactive
                
    await db.commit()
    await db.refresh(db_channel)
    return db_channel

@router.delete("/{channel_id}")
async def delete_channel(
    channel_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    result = await db.execute(select(models.Channel).where(
        models.Channel.id == channel_id, 
        models.Channel.user_id == current_user.id
    ))
    db_channel = result.scalars().first()
    if not db_channel:
        raise HTTPException(status_code=404, detail="Channel not found")
        
    await db.delete(db_channel)
    await db.commit()
    return {"status": "ok"}
