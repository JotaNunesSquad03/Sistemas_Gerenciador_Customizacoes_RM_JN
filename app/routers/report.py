from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import asc
from typing import List
from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/report", tags=["Reports"])

# LIST
@router.get("", response_model=List[schemas.ReportRead])
def list_report(
    codcoligada: int = Query(...),
    codigo: str | None = Query(None),
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    query = db.query(models.AUD_REPORT).filter(models.AUD_REPORT.CODCOLIGADA == codcoligada)
    
    if codigo:
        query = query.filter(models.AUD_REPORT.CODIGO.ilike(f"%{codigo}%"))
    
    query = query.order_by(asc(models.AUD_REPORT.ID))
    return query.offset(skip).limit(limit).all()

# GET BY ID
@router.get("/{codcoligada}/{id}", response_model=schemas.ReportRead)
def get_report(codcoligada: int, id: int, db: Session = Depends(get_db)):
    report = db.query(models.AUD_REPORT).filter_by(CODCOLIGADA=codcoligada, ID=id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report não encontrado")
    return report