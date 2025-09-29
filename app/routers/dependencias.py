from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import asc
from typing import List
from app import models, schemas
from app.database import get_db
from app.services.audit import log_aud_alteracao
from datetime import datetime

router = APIRouter(prefix="/dependencias", tags=["Dependências"])

# CREATE
@router.post("", response_model=schemas.DependenciaRead, status_code=201)
def create_dependencia(payload: schemas.DependenciaCreate, db: Session = Depends(get_db)):
    # Validação: não pode depender de si mesmo
    if (payload.TIPO_ORIGEM == payload.TIPO_DESTINO and 
        payload.ID_ORIGEM == payload.ID_DESTINO):
        raise HTTPException(status_code=400, detail="Item não pode depender de si mesmo")
    
    # Verificar se já existe essa dependência
    exists = db.query(models.AUD_DEPENDENCIAS).filter(
        models.AUD_DEPENDENCIAS.CODCOLIGADA == payload.CODCOLIGADA,
        models.AUD_DEPENDENCIAS.TIPO_ORIGEM == payload.TIPO_ORIGEM,
        models.AUD_DEPENDENCIAS.ID_ORIGEM == payload.ID_ORIGEM,
        models.AUD_DEPENDENCIAS.TIPO_DESTINO == payload.TIPO_DESTINO,
        models.AUD_DEPENDENCIAS.ID_DESTINO == payload.ID_DESTINO
    ).first()
    
    if exists:
        raise HTTPException(status_code=409, detail="Dependência já existe")

    dependencia = models.AUD_DEPENDENCIAS(
        CODCOLIGADA=payload.CODCOLIGADA,
        TIPO_ORIGEM=payload.TIPO_ORIGEM,
        ID_ORIGEM=payload.ID_ORIGEM,
        TIPO_DESTINO=payload.TIPO_DESTINO,
        ID_DESTINO=payload.ID_DESTINO,
        RECCREATEDON=payload.RECCREATEDON or datetime.utcnow()
    )
    
    try:
        db.add(dependencia)
        db.commit()
        db.refresh(dependencia)
        
        # AUDITORIA - CREATE
        log_aud_alteracao(
            db=db,
            tabela="AUD_DEPENDENCIAS",
            chave=f"{dependencia.CODCOLIGADA}|{dependencia.TIPO_ORIGEM}:{dependencia.ID_ORIGEM}|{dependencia.TIPO_DESTINO}:{dependencia.ID_DESTINO}",
            acao="CREATE",
            usuario="sistema",  # TODO: pegar do contexto de autenticação
            valor_novo=dependencia.__dict__,
            descricao=f"Nova dependência criada: {dependencia.TIPO_ORIGEM}:{dependencia.ID_ORIGEM} → {dependencia.TIPO_DESTINO}:{dependencia.ID_DESTINO}"
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao salvar Dependência: {str(e)}")
    
    return dependencia

# LIST
@router.get("", response_model=List[schemas.DependenciaRead])
def list_dependencias(
    codcoligada: int = Query(...),
    tipo_origem: str | None = Query(None),
    id_origem: str | None = Query(None),
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    query = db.query(models.AUD_DEPENDENCIAS).filter(
        models.AUD_DEPENDENCIAS.CODCOLIGADA == codcoligada
    )
    
    if tipo_origem:
        query = query.filter(models.AUD_DEPENDENCIAS.TIPO_ORIGEM == tipo_origem)
    
    if id_origem:
        query = query.filter(models.AUD_DEPENDENCIAS.ID_ORIGEM == id_origem)
    
    query = query.order_by(asc(models.AUD_DEPENDENCIAS.TIPO_ORIGEM), asc(models.AUD_DEPENDENCIAS.ID_ORIGEM))
    return query.offset(skip).limit(limit).all()

# GET BY ID
@router.get("/{id}", response_model=schemas.DependenciaRead)
def get_dependencia(id: int, db: Session = Depends(get_db)):
    dependencia = db.query(models.AUD_DEPENDENCIAS).filter_by(ID=id).first()
    if not dependencia:
        raise HTTPException(status_code=404, detail="Dependência não encontrada")
    return dependencia

# DELETE
@router.delete("/{id}", status_code=204)
def delete_dependencia(id: int, db: Session = Depends(get_db)):
    dependencia = db.query(models.AUD_DEPENDENCIAS).filter_by(ID=id).first()
    if not dependencia:
        raise HTTPException(status_code=404, detail="Dependência não encontrada")
    
    # Captura estado antes de deletar
    valor_antigo = dependencia.__dict__.copy()
    
    try:
        db.delete(dependencia)
        db.commit()
        
        # AUDITORIA - DELETE
        log_aud_alteracao(
            db=db,
            tabela="AUD_DEPENDENCIAS",
            chave=f"{dependencia.CODCOLIGADA}|{dependencia.TIPO_ORIGEM}:{dependencia.ID_ORIGEM}|{dependencia.TIPO_DESTINO}:{dependencia.ID_DESTINO}",
            acao="DELETE",
            usuario="sistema",  # TODO: pegar do contexto de autenticação
            valor_anterior=valor_antigo,
            descricao=f"Dependência excluída: {valor_antigo.get('TIPO_ORIGEM')}:{valor_antigo.get('ID_ORIGEM')} → {valor_antigo.get('TIPO_DESTINO')}:{valor_antigo.get('ID_DESTINO')}"
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao excluir Dependência: {str(e)}")
    
    return None

# BUSCAR DEPENDÊNCIAS DE UM ITEM
@router.get("/origem/{tipo}/{id_item}", response_model=List[schemas.DependenciaRead])
def get_dependencias_origem(
    tipo: str, 
    id_item: str, 
    codcoligada: int = Query(...), 
    db: Session = Depends(get_db)
):
    """Retorna tudo que DEPENDE deste item (este item é a origem)"""
    return db.query(models.AUD_DEPENDENCIAS).filter(
        models.AUD_DEPENDENCIAS.CODCOLIGADA == codcoligada,
        models.AUD_DEPENDENCIAS.TIPO_ORIGEM == tipo,
        models.AUD_DEPENDENCIAS.ID_ORIGEM == id_item
    ).all()

@router.get("/destino/{tipo}/{id_item}", response_model=List[schemas.DependenciaRead])
def get_dependencias_destino(
    tipo: str, 
    id_item: str, 
    codcoligada: int = Query(...), 
    db: Session = Depends(get_db)
):
    """Retorna tudo de que este item DEPENDE (este item é o destino)"""
    return db.query(models.AUD_DEPENDENCIAS).filter(
        models.AUD_DEPENDENCIAS.CODCOLIGADA == codcoligada,
        models.AUD_DEPENDENCIAS.TIPO_DESTINO == tipo,
        models.AUD_DEPENDENCIAS.ID_DESTINO == id_item
    ).all()

# SCANNER AUTOMÁTICO
from app.services.dependencias_scanner import popular_dependencias

@router.post("/scan")
def scan_dependencias(db: Session = Depends(get_db)):
    """Executa scanner automático para detectar dependências (FV, SQL, REPORT)"""
    novas = popular_dependencias(db)
    return {"message": f"Scanner executado. Dependências novas detectadas: {novas}"}