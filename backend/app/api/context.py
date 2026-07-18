from typing import Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app import models
from app.api import deps
from app.database import get_db
from app.plugins.manager import plugin_manager
from app.utils import sanitize_prefix

router = APIRouter()

@router.get("/", response_model=List[dict])
async def get_context_variables(
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    # 1. Default Variables
    default_vars = {
        "category": "Default",
        "variables": [
            {"name": "currentTime", "description": "The current system time", "example": "16:42:00"},
            {"name": "currentDate", "description": "The current system date", "example": "2026-07-18"},
            {"name": "nextNotificationExecution", "description": "The next scheduled execution time for this notification", "example": "2026-07-18 16:52:00"},
            {"name": "numberOfNotificationExecutions", "description": "Total times this notification has run", "example": "5"}
        ]
    }
    
    # 2. Custom Variables
    custom_vars = {"category": "Custom", "variables": []}
    result = await db.execute(select(models.CustomVariable).where(models.CustomVariable.user_id == current_user.id))
    for cv in result.scalars().all():
        custom_vars["variables"].append({
            "name": cv.name,
            "description": "User defined custom variable",
            "example": cv.value
        })
        
    # 3. Data Source Plugins
    datasource_categories = []
    # We should get all data sources that are ACTIVE for the user to provide context
    ds_result = await db.execute(select(models.DataSource).where(
        models.DataSource.user_id == current_user.id,
        models.DataSource.is_active == True
    ))
    active_sources = ds_result.scalars().all()
    
    for ds in active_sources:
        plugin_class = plugin_manager.get_datasource_plugin(ds.plugin_id)
        if plugin_class:
            schema = plugin_class.get_context_schema()
            if schema:
                prefix = sanitize_prefix(ds.name)
                prefixed_schema = []
                for var in schema:
                    prefixed_schema.append({
                        "name": f"{prefix}_{var['name']}",
                        "description": var["description"],
                        "example": var["example"]
                    })
                datasource_categories.append({
                    "category": ds.name or plugin_class.get_name(),
                    "variables": prefixed_schema
                })
                
    response = [default_vars]
    if custom_vars["variables"]:
        response.append(custom_vars)
    response.extend(datasource_categories)
    
    return response
