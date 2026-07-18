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

def is_excluded(dt: datetime, exclusions: List[dict] = None) -> bool:
    if not exclusions:
        return False
        
    for exc in exclusions:
        tz_offset = exc.get("tz_offset", 0)
        local_dt = dt - timedelta(minutes=tz_offset)
        
        if exc.get("type") == "time":
            start_str = exc.get("start")
            end_str = exc.get("end")
            if not start_str or not end_str:
                continue
            
            try:
                start_t = datetime.strptime(start_str, "%H:%M").time()
                end_t = datetime.strptime(end_str, "%H:%M").time()
                dt_t = local_dt.time()
                
                if start_t <= end_t:
                    if start_t <= dt_t <= end_t:
                        return True
                else:
                    if dt_t >= start_t or dt_t <= end_t:
                        return True
            except:
                continue
                    
        elif exc.get("type") == "weekday":
            days = exc.get("days", [])
            if local_dt.weekday() in days:
                return True
                
    return False

def calculate_next_run(schedule_type: str, schedule_expr: str, base_time: datetime = None, exclusions: List[dict] = None, start_time: datetime = None, is_initial: bool = False):
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    
    if start_time and start_time.tzinfo:
        start_time = start_time.astimezone(timezone.utc).replace(tzinfo=None)
    if base_time and base_time.tzinfo:
        base_time = base_time.astimezone(timezone.utc).replace(tzinfo=None)
        
    if base_time is None:
        base_time = now
        
    if is_initial and start_time and start_time > now and schedule_type != "specific_time":
        dt = start_time
        if schedule_type == "cron":
            try:
                iter = croniter(schedule_expr, start_time - timedelta(seconds=1))
                dt = iter.get_next(datetime)
            except:
                return None
                
        iterations = 0
        if schedule_type == "interval":
            try:
                parts = schedule_expr.strip().split()
                value = int(parts[0])
                unit = parts[1].lower() if len(parts) > 1 else "minutes"
                if unit.startswith("min"): delta = timedelta(minutes=value)
                elif unit.startswith("hour"): delta = timedelta(hours=value)
                elif unit.startswith("day"): delta = timedelta(days=value)
                else: delta = timedelta(minutes=value)
            except:
                return None
            while is_excluded(dt, exclusions) and iterations < 10000:
                dt += delta
                iterations += 1
        elif schedule_type == "cron":
            while is_excluded(dt, exclusions) and iterations < 10000:
                dt = iter.get_next(datetime)
                iterations += 1
        return dt if iterations < 10000 else None


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
                
            dt = base_time + delta
            iterations = 0
            while is_excluded(dt, exclusions) and iterations < 10000:
                dt += delta
                iterations += 1
            if iterations >= 10000:
                return None
            return dt
        except:
            return None
    elif schedule_type == "cron":
        try:
            iter = croniter(schedule_expr, base_time)
            dt = iter.get_next(datetime)
            iterations = 0
            while is_excluded(dt, exclusions) and iterations < 10000:
                dt = iter.get_next(datetime)
                iterations += 1
            if iterations >= 10000:
                return None
            return dt
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
    if db_notif.is_active:
        db_notif.next_run_at = calculate_next_run(db_notif.schedule_type, db_notif.schedule_expr, None, db_notif.exclusions, db_notif.start_time, True)
    else:
        db_notif.next_run_at = None
    
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
            
    schedule_changed = any(k in update_data for k in ["schedule_type", "schedule_expr", "exclusions"])
    was_active = db_notif.is_active
            
    for field, value in update_data.items():
        setattr(db_notif, field, value)
        
    is_now_active = db_notif.is_active
    became_active = not was_active and is_now_active
    
    if is_now_active:
        if became_active or schedule_changed or db_notif.next_run_at is None:
            db_notif.next_run_at = calculate_next_run(db_notif.schedule_type, db_notif.schedule_expr, None, db_notif.exclusions, db_notif.start_time, schedule_changed)
    else:
        db_notif.next_run_at = None
    
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

@router.post("/{notification_id}/skip", response_model=schemas.NotificationResponse)
async def skip_notification(
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
        
    if not db_notif.is_active:
        raise HTTPException(status_code=400, detail="Cannot skip an inactive notification")
        
    if db_notif.schedule_type == models.ScheduleType.specific_time:
        raise HTTPException(status_code=400, detail="Cannot skip a specific time notification")
        
    base_time = db_notif.next_run_at if db_notif.next_run_at else datetime.now(timezone.utc).replace(tzinfo=None)
    new_run = calculate_next_run(db_notif.schedule_type, db_notif.schedule_expr, base_time, db_notif.exclusions)
    
    if new_run:
        db_notif.next_run_at = new_run
    else:
        db_notif.next_run_at = None
        
    await db.commit()
    await db.refresh(db_notif)
    return db_notif
