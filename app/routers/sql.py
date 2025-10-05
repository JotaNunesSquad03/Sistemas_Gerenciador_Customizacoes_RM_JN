from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import asc
from typing import List
from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/sql", tags=["SQL"])

# LIST
@router.get("", response_model=List[schemas.SQLRead])
def list_sql(
    codcoligada: int = Query(...),
    aplicacao: str | None = Query(None),
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    query = db.query(models.AUD_SQL).filter(models.AUD_SQL.CODCOLIGADA == codcoligada)

    if aplicacao:
        query = query.filter(models.AUD_SQL.APLICACAO == aplicacao)

    query = query.order_by(
        asc(models.AUD_SQL.APLICACAO),
        asc(models.AUD_SQL.CODSENTENCA)
    )
    return query.offset(skip).limit(limit).all()

# GET BY ID
@router.get("/{id}", response_model=schemas.SQLRead)
def get_sql(id: int, db: Session = Depends(get_db)):
    sql = db.query(models.AUD_SQL).filter(models.AUD_SQL.ID == id).first()
    if not sql:
        raise HTTPException(status_code=404, detail="SQL não encontrada")
    return sql
