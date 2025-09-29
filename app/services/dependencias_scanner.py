import re
from sqlalchemy.orm import Session
from datetime import datetime
from app import models

def popular_dependencias(db: Session) -> int:
    """
    Varre AUD_FV, AUD_SQL e AUD_REPORT e popula AUD_DEPENDENCIAS.
    Retorna o número de novas dependências identificadas.
    """
    novas = 0

    # -------- FV -> SQL --------
    fvs = db.query(models.AUD_FV).all()
    for fv in fvs:
        texto = (fv.DESCRICAO or "") + " " + (fv.NOME or "")
        # exemplo simples: procurar frases CODEF####.####
        encontrados = re.findall(r"CODEF\d+\.\d+", texto, flags=re.IGNORECASE)
        for cod in encontrados:
            if _inserir_dependencia(
                db,
                codcoligada=fv.CODCOLIGADA,
                tipo_origem="FV",
                id_origem=str(fv.ID),
                tipo_destino="SQL",
                id_destino=cod
            ):
                novas += 1

    # -------- SQL -> SQL --------
    sqls = db.query(models.AUD_SQL).all()
    for sql in sqls:
        sentenca = sql.SENTENCA or ""
        encontrados = re.findall(r"CODEF\d+\.\d+", sentenca, flags=re.IGNORECASE)
        for cod in encontrados:
            if cod != sql.CODSENTENCA:  # evitar auto-dependência
                if _inserir_dependencia(
                    db,
                    codcoligada=sql.CODCOLIGADA,
                    tipo_origem="SQL",
                    id_origem=sql.CODSENTENCA,
                    tipo_destino="SQL",
                    id_destino=cod
                ):
                    novas += 1

    # -------- REPORT -> SQL --------
    reports = db.query(models.AUD_REPORT).all()
    for r in reports:
        desc = r.DESCRICAO or ""
        encontrados = re.findall(r"CODEF\d+\.\d+", desc, flags=re.IGNORECASE)
        for cod in encontrados:
            if _inserir_dependencia(
                db,
                codcoligada=r.CODCOLIGADA,
                tipo_origem="REPORT",
                id_origem=str(r.ID),
                tipo_destino="SQL",
                id_destino=cod
            ):
                novas += 1

    db.commit()
    return novas


def _inserir_dependencia(db: Session, codcoligada: int,
                         tipo_origem: str, id_origem: str,
                         tipo_destino: str, id_destino: str) -> bool:
    """
    Insere dependência somente se não existir ainda.
    Retorna True se inseriu, False se já existia.
    """
    exists = db.query(models.AUD_DEPENDENCIAS).filter_by(
        CODCOLIGADA=codcoligada,
        TIPO_ORIGEM=tipo_origem,
        ID_ORIGEM=id_origem,
        TIPO_DESTINO=tipo_destino,
        ID_DESTINO=id_destino
    ).first()

    if not exists:
        dep = models.AUD_DEPENDENCIAS(
            CODCOLIGADA=codcoligada,
            TIPO_ORIGEM=tipo_origem,
            ID_ORIGEM=id_origem,
            TIPO_DESTINO=tipo_destino,
            ID_DESTINO=id_destino,
            RECCREATEDON=datetime.utcnow()
        )
        db.add(dep)
        return True
    return False