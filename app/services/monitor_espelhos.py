import time
import json
import re
from app.database import SessionLocal
from app.models import AUD_SQL, AUD_FV, AUD_REPORT
from app.services.audit import log_aud_alteracao  

# ---------------------------
# Helpers
# ---------------------------

def _extrair_sql(sql):
    return {
        "CODCOLIGADA": getattr(sql, "CODCOLIGADA", None),
        "APLICACAO": getattr(sql, "APLICACAO", None),
        "CODSENTENCA": getattr(sql, "CODSENTENCA", None),
        "TITULO": getattr(sql, "TITULO", None),
        "SENTENCA": (getattr(sql, "SENTENCA", "") or "").strip(),
        "TAMANHO": getattr(sql, "TAMANHO", None),
        "RECCREATEDBY": getattr(sql, "RECCREATEDBY", None),
        "RECCREATEDON": str(getattr(sql, "RECCREATEDON", None)),
        "RECMODIFIEDBY": getattr(sql, "RECMODIFIEDBY", None),
        "RECMODIFIEDON": str(getattr(sql, "RECMODIFIEDON", None)),
    }

def _normalize(d: dict, ignore_keys=None):
    d = dict(d or {})
    if ignore_keys:
        for k in ignore_keys:
            d.pop(k, None)
    for k, v in d.items():
        if isinstance(v, str):
            d[k] = re.sub(r'\s+', ' ', v).strip()
    return d

def _chave_sql(sql):
    cod = getattr(sql, 'CODSENTENCA', None)
    col = getattr(sql, 'CODCOLIGADA', 0)
    return f"{col}|{cod}" if cod else None

def _chave_fv(fv):
    return f"FV_{fv.ID}"

def _chave_report(r):
    return f"REPORT_{r.ID}"

def _valores_diferentes(atual, anterior):
    return atual != anterior

def _get_ultimo_log(db, tabela, chave):
    logs = db.query(AUD_SQL if tabela=="AUD_SQL" else AUD_FV if tabela=="AUD_FV" else AUD_REPORT).all()
    for l in reversed(logs):
        c = _chave_sql(l) if tabela=="AUD_SQL" else _chave_fv(l) if tabela=="AUD_FV" else _chave_report(l)
        if c == chave:
            return l
    return None

# ---------------------------
# Monitores
# ---------------------------

def _monitor_sql(db):
    for sql in db.query(AUD_SQL).all():
        chave = _chave_sql(sql)
        if not chave or "None" in chave:  # Ignora chaves inválidas
            continue
        dados_norm = _normalize(_extrair_sql(sql), ignore_keys=["RECCREATEDON","RECMODIFIEDON"])
        ultimo = _get_ultimo_log(db, "AUD_SQL", chave)
        if not ultimo:
            log_aud_alteracao(db, "AUD_SQL", chave, "CREATE", dados_norm.get("RECCREATEDBY") or "SYSTEM", valor_novo=dados_norm)
        else:
            anterior = _normalize(_extrair_sql(ultimo), ignore_keys=["RECCREATEDON","RECMODIFIEDON"])
            if _valores_diferentes(dados_norm, anterior):
                log_aud_alteracao(db, "AUD_SQL", chave, "UPDATE", dados_norm.get("RECMODIFIEDBY") or "SYSTEM", valor_anterior=anterior, valor_novo=dados_norm)

def _monitor_fv(db):
    for fv in db.query(AUD_FV).all():
        chave = _chave_fv(fv)
        dados_norm = _normalize({
            "CODCOLIGADA": fv.CODCOLIGADA,
            "NOME": fv.NOME,
            "DESCRICAO": fv.DESCRICAO,
            "IDCATEGORIA": fv.IDCATEGORIA,
            "ATIVO": fv.ATIVO,
            "RECCREATEDBY": fv.RECCREATEDBY,
            "RECMODIFIEDBY": fv.RECMODIFIEDBY
        })
        ultimo = _get_ultimo_log(db, "AUD_FV", chave)
        if not ultimo:
            log_aud_alteracao(db, "AUD_FV", chave, "CREATE", fv.RECCREATEDBY or "SYSTEM", valor_novo=dados_norm)
        else:
            anterior = _normalize({
                "CODCOLIGADA": ultimo.CODCOLIGADA,
                "NOME": ultimo.NOME,
                "DESCRICAO": ultimo.DESCRICAO,
                "IDCATEGORIA": getattr(ultimo, "IDCATEGORIA", None),
                "ATIVO": getattr(ultimo, "ATIVO", None),
                "RECCREATEDBY": ultimo.RECCREATEDBY,
                "RECMODIFIEDBY": ultimo.RECMODIFIEDBY
            })
            if _valores_diferentes(dados_norm, anterior):
                log_aud_alteracao(db, "AUD_FV", chave, "UPDATE", fv.RECMODIFIEDBY or "SYSTEM", valor_anterior=anterior, valor_novo=dados_norm)

def _monitor_report(db):
    for r in db.query(AUD_REPORT).all():
        chave = _chave_report(r)
        dados_norm = _normalize({
            "CODCOLIGADA": r.CODCOLIGADA,
            "CODAPLICACAO": r.CODAPLICACAO,
            "CODIGO": r.CODIGO,
            "DESCRICAO": r.DESCRICAO,
            "RECCREATEDBY": r.RECCREATEDBY,
            "USRULTALTERACAO": r.USRULTALTERACAO,
            "LIDA": r.LIDA
        })
        ultimo = _get_ultimo_log(db, "AUD_REPORT", chave)
        if not ultimo:
            log_aud_alteracao(db, "AUD_REPORT", chave, "CREATE", r.RECCREATEDBY or "SYSTEM", valor_novo=dados_norm)
        else:
            anterior = _normalize({
                "CODCOLIGADA": ultimo.CODCOLIGADA,
                "CODAPLICACAO": ultimo.CODAPLICACAO,
                "CODIGO": ultimo.CODIGO,
                "DESCRICAO": ultimo.DESCRICAO,
                "RECCREATEDBY": ultimo.RECCREATEDBY,
                "USRULTALTERACAO": ultimo.USRULTALTERACAO,
                "LIDA": getattr(ultimo, "LIDA", False)
            })
            if _valores_diferentes(dados_norm, anterior):
                log_aud_alteracao(db, "AUD_REPORT", chave, "UPDATE", r.USRULTALTERACAO or "SYSTEM", valor_anterior=anterior, valor_novo=dados_norm)

# ---------------------------
# Loop principal
# ---------------------------

def monitor_espelhos(interval_seconds=30):
    while True:
        db = SessionLocal()
        try:
            _monitor_sql(db)
            _monitor_fv(db)
            _monitor_report(db)
        except Exception as e:
            print(f"[ERRO] Falha no monitor de espelhos: {e}")
        finally:
            db.close()
        time.sleep(interval_seconds)

if __name__ == "__main__":
    monitor_espelhos()
