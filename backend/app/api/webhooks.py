from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app import models
from app.database import get_db
from app.scheduler import execute_notification_now

router = APIRouter()

@router.post("/{webhook_id}")
@router.get("/{webhook_id}")
async def trigger_webhook(
    webhook_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(models.Notification).where(
        models.Notification.schedule_expr == webhook_id,
        models.Notification.schedule_type == models.ScheduleType.webhook,
        models.Notification.is_active == True
    ))
    db_notif = result.scalars().first()
    
    if not db_notif:
        raise HTTPException(status_code=404, detail="Webhook not found or inactive")
        
    success = await execute_notification_now(db_notif, db)
    
    if success:
        await db.commit()
        return {"status": "success", "message": "Notification triggered"}
    else:
        return {"status": "error", "message": "Failed to trigger notification"}
