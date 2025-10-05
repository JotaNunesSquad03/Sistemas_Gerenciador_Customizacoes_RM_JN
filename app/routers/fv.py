from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import asc
from typing import List
from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/fv", tags=["Fórmulas Visuais"])

# LIST (GET ALL)
@router.get("", response_model=List[schemas.FVRead])
def list_fv(
    codcoligada: int = Query(...),
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    query = db.query(models.AUD_FV).filter(models.AUD_FV.CODCOLIGADA == codcoligada)
    query = query.order_by(asc(models.AUD_FV.ID))
    return query.offset(skip).limit(limit).all()

# GET BY ID
@router.get("/{id}", response_model=schemas.FVRead)
def get_fv(id: int, db: Session = Depends(get_db)):
    fv = db.query(models.AUD_FV).filter(models.AUD_FV.ID == id).first()
    if not fv:
        raise HTTPException(status_code=404, detail="FV não encontrada")
    return fv
