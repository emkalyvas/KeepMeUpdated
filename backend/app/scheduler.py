import logging
from datetime import datetime, timezone
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.future import select

from app.database import SessionLocal
from app.models import Notification, ScheduleType, Channel
from app.plugins.manager import plugin_manager
from app.api.notifications import calculate_next_run

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()

async def process_notifications():
    """Job that runs every minute to find and send due notifications."""
    async with SessionLocal() as db:
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        
        stmt = select(Notification).where(
            Notification.is_active == True,
            Notification.next_run_at <= now
        )
        result = await db.execute(stmt)
        due_notifications = result.scalars().all()
        
        for notif in due_notifications:
            # 1. Fetch channel
            channel_stmt = select(Channel).where(Channel.id == notif.channel_id)
            c_res = await db.execute(channel_stmt)
            channel = c_res.scalars().first()
            
            if not channel or not channel.is_active:
                continue
                
            plugin_class = plugin_manager.get_plugin(channel.plugin_id)
            if not plugin_class:
                logger.error(f"Plugin {channel.plugin_id} not found for channel {channel.id}")
                continue
                
            plugin_instance = plugin_class(channel.config)
            
            # 2. Send notification
            try:
                success = await plugin_instance.send(
                    title=notif.title, 
                    payload=notif.payload,
                    parameters=notif.parameters
                )
                if success:
                    logger.info(f"Successfully sent notification {notif.id} via {channel.plugin_id}")
                else:
                    logger.error(f"Failed to send notification {notif.id} via {channel.plugin_id}")
            except Exception as e:
                logger.error(f"Error sending notification {notif.id}: {e}")
                
            # 3. Update next_run_at
            if notif.schedule_type == ScheduleType.specific_time:
                notif.is_active = False 
            else:
                new_next_run_at = calculate_next_run(notif.schedule_type, notif.schedule_expr, now)
                if new_next_run_at:
                    notif.next_run_at = new_next_run_at
                else:
                    notif.is_active = False 
                
        await db.commit()

def start_scheduler():
    # Adding process_notifications to run every 10 seconds for testing/demonstration purposes
    scheduler.add_job(process_notifications, 'interval', seconds=10)
    scheduler.start()
