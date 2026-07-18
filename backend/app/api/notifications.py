from typing import Any, List
from datetime import datetime, timezone, timedelta
import dateutil.parser
from croniter import croniter
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app import models, schemas
from app.api import deps
from app.database import get_db

router = APIRouter()

@router.get("/", response_model=List[schemas.NotificationResponse])
async def read_notifications(
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    result = await db.execute(select(models.Notification).where(models.Notification.user_id == current_user.id))
    return result.scalars().all()

def calculate_next_run(schedule_type: str, schedule_expr: str, base_time: datetime = None):
    if base_time is None:
        base_time = datetime.now(timezone.utc).replace(tzinfo=None)
        
    if schedule_type == "specific_time":
        try:
            dt = dateutil.parser.isoparse(schedule_expr)
            if dt.tzinfo is not None:
                dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
            return dt
        except:
            return None
    elif schedule_type == "interval":
        try:
            parts = schedule_expr.strip().split()
            value = int(parts[0])
            unit = parts[1].lower() if len(parts) > 1 else "minutes"
            
            if unit.startswith("min"):
                delta = timedelta(minutes=value)
            elif unit.startswith("hour"):
                delta = timedelta(hours=value)
            elif unit.startswith("day"):
                delta = timedelta(days=value)
            else:
                delta = timedelta(minutes=value)
                
            return base_time + delta
        except:
            return None
    elif schedule_type == "cron":
        try:
            iter = croniter(schedule_expr, base_time)
            return iter.get_next(datetime)
        except:
            return None
            
    return None

@router.post("/", response_model=schemas.NotificationResponse)
async def create_notification(
    notif_in: schemas.NotificationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    # Validate channel belongs to user
    c_res = await db.execute(select(models.Channel).where(
        models.Channel.id == notif_in.channel_id,
        models.Channel.user_id == current_user.id
    ))
    if not c_res.scalars().first():
        raise HTTPException(status_code=400, detail="Invalid channel_id")

    db_notif = models.Notification(**notif_in.model_dump(), user_id=current_user.id)
    db_notif.next_run_at = calculate_next_run(db_notif.schedule_type, db_notif.schedule_expr)
    
    db.add(db_notif)
    await db.commit()
    await db.refresh(db_notif)
    return db_notif

@router.put("/{notification_id}", response_model=schemas.NotificationResponse)
async def update_notification(
    notification_id: int,
    notif_in: schemas.NotificationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    result = await db.execute(select(models.Notification).where(
        models.Notification.id == notification_id, 
        models.Notification.user_id == current_user.id
    ))
    db_notif = result.scalars().first()
    if not db_notif:
        raise HTTPException(status_code=404, detail="Notification not found")
        
    update_data = notif_in.model_dump(exclude_unset=True)
    if "channel_id" in update_data:
        c_res = await db.execute(select(models.Channel).where(
            models.Channel.id == update_data["channel_id"],
            models.Channel.user_id == current_user.id
        ))
        if not c_res.scalars().first():
            raise HTTPException(status_code=400, detail="Invalid channel_id")
            
    for field, value in update_data.items():
        setattr(db_notif, field, value)
        
    db_notif.next_run_at = calculate_next_run(db_notif.schedule_type, db_notif.schedule_expr)
    
    await db.commit()
    await db.refresh(db_notif)
    return db_notif

@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    result = await db.execute(select(models.Notification).where(
        models.Notification.id == notification_id, 
        models.Notification.user_id == current_user.id
    ))
    db_notif = result.scalars().first()
    if not db_notif:
        raise HTTPException(status_code=404, detail="Notification not found")
        
    await db.delete(db_notif)
    await db.commit()
    return {"status": "ok"}
