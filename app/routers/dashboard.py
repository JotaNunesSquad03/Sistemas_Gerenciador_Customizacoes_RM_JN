# app/routers/dashboard.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from app.database import get_db
from app import models

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("")
def dashboard(db: Session = Depends(get_db)):
    # Totais
    total_fv = db.query(func.count()).select_from(models.AUD_FV).scalar()
    total_sql = db.query(func.count()).select_from(models.AUD_SQL).scalar()
    total_report = db.query(func.count()).select_from(models.AUD_REPORT).scalar()
    total_dep = db.query(func.count()).select_from(models.Dependencias).scalar()


    # Últimos 30 dias
    cutoff = datetime.utcnow() - timedelta(days=30)
    novos_fv = db.query(func.count()).filter(models.AUD_FV.RECCREATEDON >= cutoff).scalar()
    alterados_fv = db.query(func.count()).filter(models.AUD_FV.RECMODIFIEDON != None, models.AUD_FV.RECMODIFIEDON >= cutoff).scalar()

    novos_sql = db.query(func.count()).filter(models.AUD_SQL.RECCREATEDON >= cutoff).scalar()
    alterados_sql = db.query(func.count()).filter(models.AUD_SQL.RECMODIFIEDON != None, models.AUD_SQL.RECMODIFIEDON >= cutoff).scalar()

    novos_report = db.query(func.count()).filter(models.AUD_REPORT.RECCREATEDON >= cutoff).scalar()
    alterados_report = db.query(func.count()).filter(models.AUD_REPORT.DATAULTALTERACAO != None, models.AUD_REPORT.DATAULTALTERACAO >= cutoff).scalar()

    # Documentação faltante
    fv_sem_doc = (
        db.query(func.count(models.AUD_FV.ID))
        .outerjoin(
            models.DOC_CUSTOM,
            (models.DOC_CUSTOM.ID_REGISTRO == models.AUD_FV.ID) &
            (models.DOC_CUSTOM.TABELA == "AUD_FV")
        )
        .filter(models.DOC_CUSTOM.ID == None)
        .scalar()
    )

    sql_sem_doc = (
        db.query(func.count(models.AUD_SQL.CODSENTENCA))
        .outerjoin(
            models.DOC_CUSTOM,
            (models.DOC_CUSTOM.ID_REGISTRO == models.AUD_SQL.CODSENTENCA) &
            (models.DOC_CUSTOM.TABELA == "AUD_SQL")
        )
        .filter(models.DOC_CUSTOM.ID == None)
        .scalar()
    )

    report_sem_doc = (
        db.query(func.count(models.AUD_REPORT.ID))
        .outerjoin(
            models.DOC_CUSTOM,
            (models.DOC_CUSTOM.ID_REGISTRO == models.AUD_REPORT.ID) &
            (models.DOC_CUSTOM.TABELA == "AUD_REPORT")
        )
        .filter(models.DOC_CUSTOM.ID == None)
        .scalar()
    )


    return {
        "totais": {
            "fv": total_fv,
            "sql": total_sql,
            "report": total_report,
            "dependencias": total_dep
        },
        "ultimos_30_dias": {
            "novos": {
                "fv": novos_fv,
                "sql": novos_sql,
                "report": novos_report
            },
            "alterados": {
                "fv": alterados_fv,
                "sql": alterados_sql,
                "report": alterados_report
            },
        },
        "sem_documentacao": {
            "fv": fv_sem_doc,
            "sql": sql_sem_doc,
            "report": report_sem_doc
        }
    }