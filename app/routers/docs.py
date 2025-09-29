from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/docs", tags=["Documentação"])

@router.post("/", response_model=schemas.DocRead)
def create_doc(doc: schemas.DocCreate, db: Session = Depends(get_db)):
    """Criar nova documentação para uma customização"""
    # Verificar se já existe doc com mesmo CHAVE + TITULO
    existing = db.query(models.AUD_DOCS).filter(
        models.AUD_DOCS.CHAVE == doc.CHAVE,
        models.AUD_DOCS.TITULO == doc.TITULO
    ).first()
    
    if existing:
        raise HTTPException(400, f"Já existe documentação com título '{doc.TITULO}' para a chave '{doc.CHAVE}'")
    
    db_doc = models.AUD_DOCS(**doc.dict())
    db.add(db_doc)
    try:
        db.commit()
        db.refresh(db_doc)
    except Exception as e:
        db.rollback()
        raise HTTPException(500, f"Erro ao criar documentação: {str(e)}")
    
    return db_doc

@router.get("/{id_doc}", response_model=schemas.DocRead)
def read_doc(id_doc: int, db: Session = Depends(get_db)):
    """Buscar documentação por ID"""
    db_doc = db.query(models.AUD_DOCS).filter(models.AUD_DOCS.ID_DOC == id_doc).first()
    if not db_doc:
        raise HTTPException(404, "Documento não encontrado")
    return db_doc

@router.get("/", response_model=List[schemas.DocRead])
def list_docs(
    chave: Optional[str] = Query(None, description="Filtrar por CHAVE ex.: SQL|0|CODEF001.0005"),
    search: Optional[str] = Query(None, description="Busca por título ou conteúdo"),
    autor: Optional[str] = Query(None, description="Filtrar por autor"),
    tags: Optional[str] = Query(None, description="Filtrar por tags (busca parcial)"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Listar documentações com filtros opcionais"""
    q = db.query(models.AUD_DOCS)
    
    if chave:
        q = q.filter(models.AUD_DOCS.CHAVE == chave)
    
    if search:
        like_pattern = f"%{search}%"
        q = q.filter(
            (models.AUD_DOCS.TITULO.ilike(like_pattern)) | 
            (models.AUD_DOCS.CONTEUDO.ilike(like_pattern))
        )
    
    if autor:
        q = q.filter(models.AUD_DOCS.AUTOR.ilike(f"%{autor}%"))
    
    if tags:
        q = q.filter(models.AUD_DOCS.TAGS.ilike(f"%{tags}%"))
    
    return q.order_by(models.AUD_DOCS.DATA_ATUALIZACAO.desc()).offset(offset).limit(limit).all()

@router.put("/{id_doc}", response_model=schemas.DocRead)
def update_doc(id_doc: int, doc: schemas.DocUpdate, db: Session = Depends(get_db)):
    """Atualizar documentação existente"""
    db_doc = db.query(models.AUD_DOCS).filter(models.AUD_DOCS.ID_DOC == id_doc).first()
    if not db_doc:
        raise HTTPException(404, "Documento não encontrado")
    
    # Atualizar apenas campos fornecidos
    update_data = doc.dict(exclude_unset=True)
    if update_data:
        for field, value in update_data.items():
            setattr(db_doc, field, value)
        
        # Atualizar timestamp
        db_doc.DATA_ATUALIZACAO = func.now()
        
        try:
            db.commit()
            db.refresh(db_doc)
        except Exception as e:
            db.rollback()
            raise HTTPException(500, f"Erro ao atualizar documentação: {str(e)}")
    
    return db_doc

@router.delete("/{id_doc}")
def delete_doc(id_doc: int, db: Session = Depends(get_db)):
    """Deletar documentação"""
    db_doc = db.query(models.AUD_DOCS).filter(models.AUD_DOCS.ID_DOC == id_doc).first()
    if not db_doc:
        raise HTTPException(404, "Documento não encontrado")
    
    try:
        db.delete(db_doc)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(500, f"Erro ao deletar documentação: {str(e)}")
    
    return {"message": "Documentação deletada com sucesso", "id_doc": id_doc}

@router.get("/by-chave/{chave}", response_model=List[schemas.DocRead])
def get_docs_by_chave(chave: str, db: Session = Depends(get_db)):
    """Buscar todas as documentações de uma customização específica"""
    docs = db.query(models.AUD_DOCS).filter(
        models.AUD_DOCS.CHAVE == chave
    ).order_by(models.AUD_DOCS.DATA_ATUALIZACAO.desc()).all()
    
    return docs