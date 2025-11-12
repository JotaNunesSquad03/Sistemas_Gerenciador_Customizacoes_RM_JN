from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List, Optional
from datetime import datetime, timedelta
from app import models, schemas
from app.database import get_db
from app.services.audit import log_aud_alteracao  # Função de log de auditoria

router = APIRouter(prefix="/aud", tags=["Auditoria"])

# 📋 Listagem geral de alterações
@router.get("", response_model=List[schemas.SQLRead])
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
    q = db.query(models.AUD_SQL)
    if tabela:
        q = q.filter(models.AUD_SQL.APLICACAO == tabela)
    if usuario:
        q = q.filter(models.AUD_SQL.RECCREATEDBY.ilike(f"%{usuario}%"))
    if acao:
        q = q.filter(models.AUD_SQL.CODSENTENCA == acao)
    if data_inicio:
        q = q.filter(models.AUD_SQL.RECCREATEDON >= data_inicio)
    if data_fim:
        q = q.filter(models.AUD_SQL.RECCREATEDON <= data_fim)
    return q.order_by(desc(models.AUD_SQL.RECCREATEDON)).offset(skip).limit(limit).all()


@router.get("/ultimos")
def ultimos_registros(db: Session = Depends(get_db)):
    """
    Retorna os 5 últimos registros criados ou alterados
    nas tabelas AUD_SQL, AUD_FV e AUD_REPORT.
    """

    def formatar_registro(origem, descricao, usuario, data):
        return {
            "origem": origem,
            "descricao": descricao,
            "usuario": usuario,
            "data": data,
        }

    registros = []

    # AUD_SQL
    for r in (
        db.query(
            models.AUD_SQL.TITULO.label("descricao"),
            models.AUD_SQL.RECMODIFIEDBY,
            models.AUD_SQL.RECMODIFIEDON,
            models.AUD_SQL.RECCREATEDBY,
            models.AUD_SQL.RECCREATEDON,
        )
        .order_by(models.AUD_SQL.RECMODIFIEDON.desc(), models.AUD_SQL.RECCREATEDON.desc())
        .limit(5)
        .all()
    ):
        data = r.RECMODIFIEDON or r.RECCREATEDON
        usuario = r.RECMODIFIEDBY or r.RECCREATEDBY
        registros.append(formatar_registro("AUD_SQL", r.descricao, usuario, data))

    # AUD_FV
    for r in (
        db.query(
            models.AUD_FV.NOME.label("descricao"),
            models.AUD_FV.RECMODIFIEDBY,
            models.AUD_FV.RECMODIFIEDON,
            models.AUD_FV.RECCREATEDBY,
            models.AUD_FV.RECCREATEDON,
        )
        .order_by(models.AUD_FV.RECMODIFIEDON.desc(), models.AUD_FV.RECCREATEDON.desc())
        .limit(5)
        .all()
    ):
        data = r.RECMODIFIEDON or r.RECCREATEDON
        usuario = r.RECMODIFIEDBY or r.RECCREATEDBY
        registros.append(formatar_registro("AUD_FV", r.descricao, usuario, data))

    # AUD_REPORT
    for r in (
        db.query(
            models.AUD_REPORT.DESCRICAO.label("descricao"),
            models.AUD_REPORT.USRULTALTERACAO.label("modificado_por"),
            models.AUD_REPORT.DATAULTALTERACAO.label("modificado_em"),
            models.AUD_REPORT.RECCREATEDBY,
            models.AUD_REPORT.RECCREATEDON,
        )
        .order_by(models.AUD_REPORT.DATAULTALTERACAO.desc(), models.AUD_REPORT.RECCREATEDON.desc())
        .limit(5)
        .all()
    ):
        data = r.modificado_em or r.RECCREATEDON
        usuario = r.modificado_por or r.RECCREATEDBY
        registros.append(formatar_registro("AUD_REPORT", r.descricao, usuario, data))

    # Junta tudo e pega os 5 mais recentes
    registros = sorted(registros, key=lambda x: x["data"] or datetime.min, reverse=True)[:5]

    return registros

# Obter uma alteração específica
@router.get("/{id_aud}", response_model=schemas.SQLRead)
def get_alteracao(id_aud: int, db: Session = Depends(get_db)):
    r = db.query(models.AUD_SQL).filter_by(ID=id_aud).first()
    if not r:
        raise HTTPException(status_code=404, detail="Alteração não encontrada")
    return r

# Histórico de uma tabela/chave
@router.get("/historico/{tabela}/{chave}", response_model=List[schemas.SQLRead])
def historico_item(tabela: str, chave: str, db: Session = Depends(get_db)):
    return db.query(models.AUD_SQL).filter(
        models.AUD_SQL.APLICACAO == tabela,
        models.AUD_SQL.CODSENTENCA == chave
    ).order_by(desc(models.AUD_SQL.RECCREATEDON)).all()


# Estatísticas gerais (com últimos 30 dias)
@router.get("/stats/resumo")
def stats(db: Session = Depends(get_db)):
    cutoff = datetime.utcnow() - timedelta(days=30)
    total = db.query(func.count()).select_from(models.AUD_SQL).scalar()

    por_tabela = db.query(
        models.AUD_SQL.APLICACAO, func.count()
    ).group_by(models.AUD_SQL.APLICACAO).all()

    por_acao = db.query(
        models.AUD_SQL.CODSENTENCA, func.count()
    ).group_by(models.AUD_SQL.CODSENTENCA).all()

    ult_30 = db.query(func.count()).filter(models.AUD_SQL.RECCREATEDON >= cutoff).scalar()

    return {
        "total": total,
        "por_tabela": [{"tabela": t, "total": n} for t, n in por_tabela],
        "por_acao": [{"acao": a, "total": n} for a, n in por_acao],
        "ultimos_30_dias": ult_30
    }


# Endpoint de teste
@router.post("/teste")
def teste_auditoria(db: Session = Depends(get_db)):
    """
    Cria um registro fake na tabela AUD_SQL
    e envia via WebSocket para testar integração.
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

    return {"msg": "Alteração de teste registrada", "id": registro.ID}