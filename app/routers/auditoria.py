from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List, Optional
from datetime import datetime, timedelta
from app import models, schemas
from app.database import get_db
from app.services.audit import log_aud_alteracao 

router = APIRouter(prefix="/aud", tags=["Auditoria"])

@router.get("", response_model=List[schemas.AudAlteracaoRead])
def list_alteracoes(
    tabela: Optional[str] = Query(None),
    usuario: Optional[str] = Query(None),
    acao: Optional[str] = Query(None),
    data_inicio: Optional[datetime] = Query(None),
    data_fim: Optional[datetime] = Query(None),
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    q = db.query(models.AUD_ALTERACAO)
    if tabela:
        q = q.filter(models.AUD_ALTERACAO.TABELA == tabela)
    if usuario:
        q = q.filter(models.AUD_ALTERACAO.USUARIO.ilike(f"%{usuario}%"))
    if acao:
        q = q.filter(models.AUD_ALTERACAO.ACAO == acao)
    if data_inicio:
        q = q.filter(models.AUD_ALTERACAO.DATA_HORA >= data_inicio)
    if data_fim:
        q = q.filter(models.AUD_ALTERACAO.DATA_HORA <= data_fim)
    return q.order_by(desc(models.AUD_ALTERACAO.DATA_HORA)).offset(skip).limit(limit).all()

@router.get("/{id_aud}", response_model=schemas.AudAlteracaoRead)
def get_alteracao(id_aud: int, db: Session = Depends(get_db)):
    r = db.query(models.AUD_ALTERACAO).filter_by(ID_AUD=id_aud).first()
    if not r:
        raise HTTPException(status_code=404, detail="Alteração não encontrada")
    return r

@router.get("/historico/{tabela}/{chave}", response_model=List[schemas.AudAlteracaoRead])
def historico_item(tabela: str, chave: str, db: Session = Depends(get_db)):
    return db.query(models.AUD_ALTERACAO).filter(
        models.AUD_ALTERACAO.TABELA == tabela,
        models.AUD_ALTERACAO.CHAVE == chave
    ).order_by(desc(models.AUD_ALTERACAO.DATA_HORA)).all()

@router.get("/stats/resumo")
def stats(db: Session = Depends(get_db)):
    cutoff = datetime.utcnow() - timedelta(days=30)
    total = db.query(func.count()).select_from(models.AUD_ALTERACAO).scalar()
    por_tabela = db.query(
        models.AUD_ALTERACAO.TABELA, func.count()
    ).group_by(models.AUD_ALTERACAO.TABELA).all()
    por_acao = db.query(
        models.AUD_ALTERACAO.ACAO, func.count()
    ).group_by(models.AUD_ALTERACAO.ACAO).all()
    ult_30 = db.query(func.count()).filter(models.AUD_ALTERACAO.DATA_HORA >= cutoff).scalar()
    return {
        "total": total,
        "por_tabela": [{"tabela": t, "total": n} for t, n in por_tabela],
        "por_acao": [{"acao": a, "total": n} for a, n in por_acao],
        "ultimos_30_dias": ult_30
    }

@router.post("/teste")
def teste_auditoria(db: Session = Depends(get_db)):
    """
    Endpoint de teste: força a criação de uma auditoria fake
    e dispara notificação em tempo real pelo WebSocket.
    """
    registro = log_aud_alteracao(
        db=db,
        tabela="AUD_SQL",
        chave="1|999",
        acao="CREATE",
        usuario="Camy",
        descricao="Teste via endpoint",
        valor_anterior=None,
        valor_novo={"SQL": "SELECT * FROM CLIENTES"}
    )

    if not registro:
        raise HTTPException(status_code=500, detail="Erro ao registrar alteração")

    return {"msg": "Alteração de teste registrada", "id": registro.ID_AUD}