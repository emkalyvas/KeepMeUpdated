import logging
from datetime import datetime, timezone
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.future import select

from app.database import SessionLocal
from app.models import Notification, ScheduleType, Channel, DataSource, CustomVariable
from app.plugins.manager import plugin_manager
from app.api.notifications import calculate_next_run
from app.utils import sanitize_prefix

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
                
            plugin_class = plugin_manager.get_channel_plugin(channel.plugin_id)
            if not plugin_class:
                logger.error(f"Plugin {channel.plugin_id} not found for channel {channel.id}")
                continue
                
            plugin_instance = plugin_class(channel.config)
            
            # 2. Gather Context
            context = {}
            # Defaults
            next_run = None
            if notif.schedule_type != ScheduleType.specific_time:
                next_run = calculate_next_run(notif.schedule_type, notif.schedule_expr, now, notif.exclusions)
                
            context["currentTime"] = now.strftime("%H:%M:%S")
            context["currentDate"] = now.strftime("%Y-%m-%d")
            context["nextNotificationExecution"] = next_run.strftime("%Y-%m-%d %H:%M:%S") if next_run else "Never"
            context["numberOfNotificationExecutions"] = notif.execution_count or 0
            
            # Custom Variables
            cv_stmt = select(CustomVariable).where(CustomVariable.user_id == notif.user_id)
            cv_res = await db.execute(cv_stmt)
            for cv in cv_res.scalars().all():
                context[cv.name] = cv.value
                
            # Data Sources
            ds_stmt = select(DataSource).where(
                DataSource.user_id == notif.user_id,
                DataSource.is_active == True
            )
            ds_res = await db.execute(ds_stmt)
            for ds in ds_res.scalars().all():
                ds_class = plugin_manager.get_datasource_plugin(ds.plugin_id)
                if ds_class:
                    try:
                        ds_instance = ds_class(ds.config)
                        ds_context = await ds_instance.fetch_context()
                        prefix = sanitize_prefix(ds.name)
                        for k, v in ds_context.items():
                            context[f"{prefix}_{k}"] = v
                    except Exception as e:
                        logger.error(f"Error fetching context from datasource {ds.name}: {e}")

            # 3. Format Title, Payload, and Parameters
            formatted_title = notif.title or ""
            formatted_payload = notif.payload or ""
            formatted_parameters = {}
            
            for k, v in context.items():
                formatted_title = formatted_title.replace(f"{{{k}}}", str(v))
                formatted_payload = formatted_payload.replace(f"{{{k}}}", str(v))
                
            if notif.parameters:
                for pk, pv in notif.parameters.items():
                    if isinstance(pv, str):
                        for k, v in context.items():
                            pv = pv.replace(f"{{{k}}}", str(v))
                    formatted_parameters[pk] = pv
            
            # 4. Send notification
            try:
                success = await plugin_instance.send(
                    title=formatted_title, 
                    payload=formatted_payload,
                    parameters=formatted_parameters
                )
                if success:
                    logger.info(f"Successfully sent notification {notif.id} via {channel.plugin_id}")
                    notif.execution_count = (notif.execution_count or 0) + 1
                else:
                    logger.error(f"Failed to send notification {notif.id} via {channel.plugin_id}")
            except Exception as e:
                logger.error(f"Error sending notification {notif.id}: {e}")
                
            # 5. Update next_run_at
            if notif.schedule_type == ScheduleType.specific_time:
                notif.is_active = False 
            else:
                if next_run:
                    notif.next_run_at = next_run
                else:
                    notif.is_active = False
                
        await db.commit()

def start_scheduler():
    # Adding process_notifications to run every 10 seconds for testing/demonstration purposes
    scheduler.add_job(process_notifications, 'interval', seconds=10)
    scheduler.start()
