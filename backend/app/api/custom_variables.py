from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app import models, schemas
from app.api import deps
from app.database import get_db

router = APIRouter()

@router.get("/", response_model=List[schemas.CustomVariableResponse])
async def read_custom_variables(
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    result = await db.execute(select(models.CustomVariable).where(models.CustomVariable.user_id == current_user.id))
    return result.scalars().all()

@router.post("/", response_model=schemas.CustomVariableResponse)
async def create_custom_variable(
    var_in: schemas.CustomVariableCreate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    # Check if a variable with this name already exists
    result = await db.execute(select(models.CustomVariable).where(
        models.CustomVariable.user_id == current_user.id,
        models.CustomVariable.name == var_in.name
    ))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Custom variable with this name already exists")
        
    db_var = models.CustomVariable(**var_in.model_dump(), user_id=current_user.id)
    db.add(db_var)
    await db.commit()
    await db.refresh(db_var)
    return db_var

@router.put("/{var_id}", response_model=schemas.CustomVariableResponse)
async def update_custom_variable(
    var_id: int,
    var_in: schemas.CustomVariableUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    result = await db.execute(select(models.CustomVariable).where(
        models.CustomVariable.id == var_id, 
        models.CustomVariable.user_id == current_user.id
    ))
    db_var = result.scalars().first()
    if not db_var:
        raise HTTPException(status_code=404, detail="Custom variable not found")
        
    update_data = var_in.model_dump(exclude_unset=True)
    
    if "name" in update_data and update_data["name"] != db_var.name:
        check = await db.execute(select(models.CustomVariable).where(
            models.CustomVariable.user_id == current_user.id,
            models.CustomVariable.name == update_data["name"]
        ))
        if check.scalars().first():
            raise HTTPException(status_code=400, detail="Custom variable with this name already exists")
            
    for field, value in update_data.items():
        setattr(db_var, field, value)
        
    await db.commit()
    await db.refresh(db_var)
    return db_var

@router.delete("/{var_id}")
async def delete_custom_variable(
    var_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    result = await db.execute(select(models.CustomVariable).where(
        models.CustomVariable.id == var_id, 
        models.CustomVariable.user_id == current_user.id
    ))
    db_var = result.scalars().first()
    if not db_var:
        raise HTTPException(status_code=404, detail="Custom variable not found")
        
    await db.delete(db_var)
    await db.commit()
    return {"status": "ok"}
