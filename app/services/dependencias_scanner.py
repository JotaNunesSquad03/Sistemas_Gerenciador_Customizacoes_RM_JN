import re
from sqlalchemy.orm import Session
from datetime import datetime
from app import models

def popular_dependencias(db: Session) -> int:
    """
    Varre AUD_FV, AUD_SQL e AUD_REPORT e popula AUD_DEPENDENCIA.
    Retorna o número de novas dependências identificadas.
    """
    novas = 0

    # -------- FV -> SQL --------
    fvs = db.query(models.AUD_FV).all()
    sqls = {s.CODSENTENCA: s for s in db.query(models.AUD_SQL).all()}  # para referência rápida

    for fv in fvs:
        texto = (fv.DESCRICAO or "") + " " + (fv.NOME or "")
        encontrados = re.findall(r"CODEF\d+\.\d+", texto, flags=re.IGNORECASE)
        for cod in encontrados:
            sql_ref = sqls.get(cod)
            if sql_ref:
                if _inserir_dependencia(db, id_sql=sql_ref.ID, id_fv=fv.ID, id_report=0):
                    novas += 1

    # -------- SQL -> SQL --------
    for sql in sqls.values():
        sentenca = sql.SENTENCA or ""
        encontrados = re.findall(r"CODEF\d+\.\d+", sentenca, flags=re.IGNORECASE)
        for cod in encontrados:
            if cod != sql.CODSENTENCA:  # evitar auto-dependência
                sql_ref = sqls.get(cod)
                if sql_ref:
                    if _inserir_dependencia(db, id_sql=sql_ref.ID, id_fv=0, id_report=0):
                        novas += 1

    # -------- REPORT -> SQL --------
    reports = db.query(models.AUD_REPORT).all()
    for r in reports:
        desc = r.DESCRICAO or ""
        encontrados = re.findall(r"CODEF\d+\.\d+", desc, flags=re.IGNORECASE)
        for cod in encontrados:
            sql_ref = sqls.get(cod)
            if sql_ref:
                if _inserir_dependencia(db, id_sql=sql_ref.ID, id_fv=0, id_report=r.ID):
                    novas += 1

    db.commit()
    return novas


def _inserir_dependencia(db: Session, id_sql: int, id_fv: int, id_report: int) -> bool:
    """
    Insere dependência somente se não existir ainda.
    Retorna True se inseriu, False se já existia.
    """
    exists = db.query(models.DEPENDENCIA).filter_by(
        ID_SQL=id_sql,
        ID_FV=id_fv,
        ID_REPORT=id_report
    ).first()

    if not exists:
        dep = models.DEPENDENCIA(
            ID_SQL=id_sql,
            ID_FV=id_fv,
            ID_REPORT=id_report,
            DESCRICAO=None
        )
        db.add(dep)
        return True
    return False
