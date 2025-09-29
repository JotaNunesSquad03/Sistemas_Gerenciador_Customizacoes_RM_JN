# app/services/monitor_espelhos.py

import time
import json
import re
import hashlib
from app.database import SessionLocal
from app.models import AUD_ALTERACAO, AUD_FV, AUD_SQL, AUD_REPORT
from app.services.audit import log_aud_alteracao
from app.notificacao import notificar_console  # ✅ apenas console

# ---------------------------
# Helpers
# ---------------------------

def _get_ultimo_registro(db, tabela, chave):
    return db.query(AUD_ALTERACAO).filter(
        AUD_ALTERACAO.TABELA == tabela,
        AUD_ALTERACAO.CHAVE == chave
    ).order_by(AUD_ALTERACAO.DATA_HORA.desc()).first()

# ---------------------------
# Extração de dados
# ---------------------------

def _extrair_dados_fv(fv):
    return {
        "CODCOLIGADA": getattr(fv, "CODCOLIGADA", None),
        "ID": getattr(fv, "ID", None),
        "NOME": getattr(fv, "NOME", None),
        "DESCRICAO": getattr(fv, "DESCRICAO", None),
        "USUARIOCRIACAO": getattr(fv, "USUARIOCRIACAO", None),
        "DATACRIACAO": str(getattr(fv, "DATACRIACAO", None)),
        "USUARIOALTERACAO": getattr(fv, "USUARIOALTERACAO", None),
        "DATAALTERACAO": str(getattr(fv, "DATAALTERACAO", None))
    }

def _extrair_dados_sql(sql):
    return {
        "CODCOLIGADA": getattr(sql, "CODCOLIGADA", None),
        "APLICACAO": getattr(sql, "APLICACAO", None),
        "CODSENTENCA": getattr(sql, "CODSENTENCA", None),
        "TITULO": getattr(sql, "TITULO", None),
        "SENTENCA": getattr(sql, "SENTENCA", None),
        "TAMANHO": getattr(sql, "TAMANHO", None),
        "RECCREATEDBY": getattr(sql, "RECCREATEDBY", None),
        "RECCREATEDON": str(getattr(sql, "RECCREATEDON", None)),
        "RECMODIFIEDBY": getattr(sql, "RECMODIFIEDBY", None),
        "RECMODIFIEDON": str(getattr(sql, "RECMODIFIEDON", None)),
    }

def _extrair_dados_report(rep):
    return {
        "CODCOLIGADA": getattr(rep, 'CODCOLIGADA', None),
        "IDREPORT": getattr(rep, 'IDREPORT', None),
        "CODREPORT": getattr(rep, 'CODREPORT', None),
        "DESCRICAO": getattr(rep, 'DESCRICAO', None),
        "USUARIOCRIACAO": getattr(rep, 'USUARIOCRIACAO', None),
        "DATACRIACAO": str(getattr(rep, 'DATACRIACAO', None)),
        "USUARIOALTERACAO": getattr(rep, 'USUARIOALTERACAO', None),
        "DATAALTERACAO": str(getattr(rep, 'DATAALTERACAO', None))
    }

# ---------------------------
# Normalização
# ---------------------------

def _normalize_sql_record(d: dict) -> dict:
    d = dict(d or {})
    d.pop('APLICACAO', None)
    if 'SENTENCA' in d and d['SENTENCA']:
        d['SENTENCA'] = re.sub(r'\s+', ' ', d['SENTENCA']).strip()
    d.pop('RECCREATEDON', None)
    d.pop('RECMODIFIEDON', None)
    return d

def _normalize_fv_record(d: dict) -> dict:
    d = dict(d or {})
    if 'DESCRICAO' in d and d['DESCRICAO']:
        d['DESCRICAO'] = re.sub(r'\s+', ' ', d['DESCRICAO']).strip()
    d.pop('DATACRIACAO', None)
    d.pop('DATAALTERACAO', None)
    return d

def _normalize_report_record(d: dict) -> dict:
    d = dict(d or {})
    if 'DESCRICAO' in d and d['DESCRICAO']:
        d['DESCRICAO'] = re.sub(r'\s+', ' ', d['DESCRICAO']).strip()
    d.pop('DATACRIACAO', None)
    d.pop('DATAALTERACAO', None)
    return d

def _valores_diferentes(valor_atual: dict, valor_anterior_json: str, normalizer=None) -> bool:
    if not valor_anterior_json:
        return True
    try:
        valor_anterior = json.loads(valor_anterior_json)
        va = normalizer(valor_atual) if normalizer else valor_atual
        vp = normalizer(valor_anterior) if normalizer else valor_anterior
        return va != vp
    except Exception:
        return True

# ---------------------------
# Chaves únicas
# ---------------------------

def _chave_sql(sql):
    codsent = getattr(sql, 'CODSENTENCA', None)
    if codsent is None:
        return None
    return f"{getattr(sql, 'CODCOLIGADA', 0)}|{codsent}"

def _chave_report(rep):
    codcol = getattr(rep, 'CODCOLIGADA', 0)
    ident = getattr(rep, 'IDREPORT', None) or getattr(rep, 'CODREPORT', None)
    if ident is None:
        desc = getattr(rep, 'DESCRICAO', '') or ''
        ident = hashlib.md5(desc.encode('utf-8')).hexdigest()[:8]
    return f"{codcol}|{ident}"

# ---------------------------
# Monitores
# ---------------------------

def _monitorar_fv(db):
    fvs = db.query(AUD_FV).all()
    chaves_existentes = {log.CHAVE for log in db.query(AUD_ALTERACAO).filter(AUD_ALTERACAO.TABELA == "AUD_FV").all()}
    chaves_atuais = set()

    for fv in fvs:
        chave = f"{getattr(fv, 'CODCOLIGADA', 0)}|{getattr(fv, 'ID', None)}"
        chaves_atuais.add(chave)
        dados_norm = _normalize_fv_record(_extrair_dados_fv(fv))
        ultimo_log = _get_ultimo_registro(db, "AUD_FV", chave)

        if not ultimo_log:
            log_aud_alteracao(db, "AUD_FV", chave, "CREATE", dados_norm.get("USUARIOCRIACAO") or "SYSTEM", valor_novo=dados_norm, descricao="CREATE detectado em AUD_FV")
        elif _valores_diferentes(dados_norm, ultimo_log.VALOR_NOVO):
            valor_anterior = _normalize_fv_record(json.loads(ultimo_log.VALOR_NOVO) if ultimo_log.VALOR_NOVO else {})
            log_aud_alteracao(db, "AUD_FV", chave, "UPDATE", dados_norm.get("USUARIOALTERACAO") or "SYSTEM", valor_anterior=valor_anterior, valor_novo=dados_norm, descricao="UPDATE detectado em AUD_FV")

    for chave_deletada in chaves_existentes - chaves_atuais:
        ultimo_log = _get_ultimo_registro(db, "AUD_FV", chave_deletada)
        if ultimo_log and ultimo_log.ACAO != "DELETE":
            valor_anterior = json.loads(ultimo_log.VALOR_NOVO) if ultimo_log.VALOR_NOVO else {}
            log_aud_alteracao(db, "AUD_FV", chave_deletada, "DELETE", "SYSTEM", valor_anterior=valor_anterior, descricao="DELETE detectado em AUD_FV")

def _monitorar_sql(db):
    sqls = db.query(AUD_SQL).all()
    chaves_existentes = {log.CHAVE for log in db.query(AUD_ALTERACAO).filter(AUD_ALTERACAO.TABELA == "AUD_SQL").all()}
    chaves_atuais = set()

    for sql in sqls:
        chave = _chave_sql(sql)
        if not chave:
            continue
        chaves_atuais.add(chave)
        dados_norm = _normalize_sql_record(_extrair_dados_sql(sql))
        ultimo_log = _get_ultimo_registro(db, "AUD_SQL", chave)

        if not ultimo_log:
            log_aud_alteracao(db, "AUD_SQL", chave, "CREATE", dados_norm.get("RECCREATEDBY") or "SYSTEM", valor_novo=dados_norm, descricao="CREATE detectado em AUD_SQL")
        elif _valores_diferentes(dados_norm, ultimo_log.VALOR_NOVO):
            valor_anterior = _normalize_sql_record(json.loads(ultimo_log.VALOR_NOVO) if ultimo_log.VALOR_NOVO else {})
            log_aud_alteracao(db, "AUD_SQL", chave, "UPDATE", dados_norm.get("RECMODIFIEDBY") or "SYSTEM", valor_anterior=valor_anterior, valor_novo=dados_norm, descricao="UPDATE detectado em AUD_SQL")

    for chave_deletada in chaves_existentes - chaves_atuais:
        ultimo_log = _get_ultimo_registro(db, "AUD_SQL", chave_deletada)
        if ultimo_log and ultimo_log.ACAO != "DELETE":
            valor_anterior = json.loads(ultimo_log.VALOR_NOVO) if ultimo_log.VALOR_NOVO else {}
            log_aud_alteracao(db, "AUD_SQL", chave_deletada, "DELETE", valor_anterior=valor_anterior, descricao="DELETE detectado em AUD_SQL")

def _monitorar_report(db):
    reports = db.query(AUD_REPORT).all()
    chaves_existentes = {log.CHAVE for log in db.query(AUD_ALTERACAO).filter(AUD_ALTERACAO.TABELA == "AUD_REPORT").all()}
    chaves_atuais = set()

    for rep in reports:
        chave = _chave_report(rep)
        chaves_atuais.add(chave)
        dados_norm = _normalize_report_record(_extrair_dados_report(rep))
        ultimo_log = _get_ultimo_registro(db, "AUD_REPORT", chave)

        if not ultimo_log:
            log_aud_alteracao(db, "AUD_REPORT", chave, "CREATE", dados_norm.get("USUARIOCRIACAO") or "SYSTEM", valor_novo=dados_norm, descricao="CREATE detectado em AUD_REPORT")
        elif _valores_diferentes(dados_norm, ultimo_log.VALOR_NOVO):
            valor_anterior = _normalize_report_record(json.loads(ultimo_log.VALOR_NOVO) if ultimo_log.VALOR_NOVO else {})
            log_aud_alteracao(db, "AUD_REPORT", chave, "UPDATE", dados_norm.get("USUARIOALTERACAO") or "SYSTEM", valor_anterior=valor_anterior, valor_novo=dados_norm, descricao="UPDATE detectado em AUD_REPORT")

    for chave_deletada in chaves_existentes - chaves_atuais:
        if not chave_deletada or str(chave_deletada).endswith('|None'):
            continue
        ultimo_log = _get_ultimo_registro(db, "AUD_REPORT", chave_deletada)
        if ultimo_log and ultimo_log.ACAO != "DELETE":
            valor_anterior = json.loads(ultimo_log.VALOR_NOVO) if ultimo_log.VALOR_NOVO else {}
            log_aud_alteracao(db, "AUD_REPORT", chave_deletada, "DELETE", valor_anterior=valor_anterior, descricao="DELETE detectado em AUD_REPORT")

# ---------------------------
# Loop principal
# ---------------------------

def monitor_espelhos(interval_seconds=30):

    while True:
        db = SessionLocal()
        try:
            _monitorar_fv(db)
            _monitorar_sql(db)
            _monitorar_report(db)
        except Exception as e:
            print(f"[ERRO] Falha no monitor de espelhos: {e}")
        finally:
            db.close()
        time.sleep(interval_seconds)


if __name__ == "__main__":
    monitor_espelhos()
