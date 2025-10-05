from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import asc
from typing import List
from app import models, schemas
from app.database import get_db
from datetime import datetime

router = APIRouter(prefix="/dependencias", tags=["Dependências"])

# CREATE
@router.post("", response_model=schemas.DependenciaRead, status_code=201)
def create_dependencia(payload: schemas.DependenciaCreate, db: Session = Depends(get_db)):
    # Verificar se já existe essa dependência
    exists = db.query(models.DEPENDENCIA).filter(
        models.DEPENDENCIA.ID_SQL == payload.ID_SQL,
        models.DEPENDENCIA.ID_FV == payload.ID_FV,
        models.DEPENDENCIA.ID_REPORT == payload.ID_REPORT
    ).first()
    
    if exists:
        raise HTTPException(status_code=409, detail="Dependência já existe")

    dependencia = models.DEPENDENCIA(
        ID_SQL=payload.ID_SQL,
        ID_FV=payload.ID_FV,
        ID_REPORT=payload.ID_REPORT,
        DESCRICAO=payload.DESCRICAO
    )
    
    try:
        db.add(dependencia)
        db.commit()
        db.refresh(dependencia)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao salvar Dependência: {str(e)}")
    
    return dependencia

# LIST
@router.get("", response_model=List[schemas.DependenciaRead])
def list_dependencias(
    id_sql: int | None = Query(None),
    id_fv: int | None = Query(None),
    id_report: int | None = Query(None),
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    query = db.query(models.DEPENDENCIA)

    if id_sql is not None:
        query = query.filter(models.DEPENDENCIA.ID_SQL == id_sql)
    if id_fv is not None:
        query = query.filter(models.DEPENDENCIA.ID_FV == id_fv)
    if id_report is not None:
        query = query.filter(models.DEPENDENCIA.ID_REPORT == id_report)
    
    query = query.order_by(
        asc(models.DEPENDENCIA.ID_SQL),
        asc(models.DEPENDENCIA.ID_FV),
        asc(models.DEPENDENCIA.ID_REPORT)
    )
    return query.offset(skip).limit(limit).all()

# GET BY COMPOSITE KEY
@router.get("/{id_sql}/{id_fv}/{id_report}", response_model=schemas.DependenciaRead)
def get_dependencia(id_sql: int, id_fv: int, id_report: int, db: Session = Depends(get_db)):
    dependencia = db.query(models.DEPENDENCIA).filter_by(
        ID_SQL=id_sql, ID_FV=id_fv, ID_REPORT=id_report
    ).first()
    if not dependencia:
        raise HTTPException(status_code=404, detail="Dependência não encontrada")
    return dependencia

# DELETE
@router.delete("/{id_sql}/{id_fv}/{id_report}", status_code=204)
def delete_dependencia(id_sql: int, id_fv: int, id_report: int, db: Session = Depends(get_db)):
    dependencia = db.query(models.DEPENDENCIA).filter_by(
        ID_SQL=id_sql, ID_FV=id_fv, ID_REPORT=id_report
    ).first()
    if not dependencia:
        raise HTTPException(status_code=404, detail="Dependência não encontrada")
    
    try:
        db.delete(dependencia)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao excluir Dependência: {str(e)}")
    
    return None
