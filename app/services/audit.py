from sqlalchemy.orm import Session
from datetime import datetime
import json
import asyncio
from app import models


def log_aud_alteracao(
    db: Session,
    tabela: str,
    chave: str,
    acao: str,
    usuario: str,
    valor_anterior=None,
    valor_novo=None,
    descricao=None
):
    """
    Registra uma alteração na tabela AUD_SQL
    e dispara notificação em tempo real via WebSocket.
    """

    # Preparação dos valores
    if isinstance(valor_anterior, dict):
        valor_anterior = {k: v for k, v in valor_anterior.items() if not k.startswith('_')}
    if isinstance(valor_novo, dict):
        valor_novo = {k: v for k, v in valor_novo.items() if not k.startswith('_')}

    registro = models.AUD_SQL(
        CODCOLIGADA=None,  # ou preencha se tiver valor
        APLICACAO=tabela,
        CODSENTENCA=chave,
        TITULO=None,
        SENTENCA=None,
        TAMANHO=None,
        RECCREATEDBY=usuario or "SYSTEM",
        RECCREATEDON=datetime.utcnow()
    )

    try:
        db.add(registro)
        db.commit()
        db.refresh(registro)

        msg = {
            "id": registro.ID,
            "tabela": registro.APLICACAO,
            "acao": acao,
            "usuario": registro.RECCREATEDBY,
            "data_hora": str(registro.RECCREATEDON),
            "descricao": descricao
        }

        try:
            asyncio.run_coroutine_threadsafe(manager.broadcast(json.dumps(msg)), loop)
        except Exception as e:
            print(f"⚠️ Erro ao enviar notificação WebSocket: {e}")

        return registro

    except Exception as e:
        db.rollback()
        print(f"❌ Erro ao registrar auditoria: {e}")
        return None

