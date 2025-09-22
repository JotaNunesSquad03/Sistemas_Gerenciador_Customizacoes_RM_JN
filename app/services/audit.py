from sqlalchemy.orm import Session
from datetime import datetime
from app import models
import json
import asyncio
from app.services.websocket_manager import manager, loop  # importa o loop global


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
    Registra uma alteração na tabela AUD_ALTERACAO
    e dispara notificação em tempo real via WebSocket.
    """

    # Preparação dos valores
    if isinstance(valor_anterior, dict):
        valor_anterior = {k: v for k, v in valor_anterior.items() if not k.startswith('_')}
    if isinstance(valor_novo, dict):
        valor_novo = {k: v for k, v in valor_novo.items() if not k.startswith('_')}

    registro = models.AUD_ALTERACAO(
        TABELA=tabela,
        CHAVE=chave,
        ACAO=acao,
        USUARIO=usuario or "SYSTEM",
        DATA_HORA=datetime.utcnow(),
        DESCRICAO=descricao,
        VALOR_ANTERIOR=json.dumps(valor_anterior, default=str) if valor_anterior is not None else None,
        VALOR_NOVO=json.dumps(valor_novo, default=str) if valor_novo is not None else None,
    )

    try:
        db.add(registro)
        db.commit()
        db.refresh(registro)

        msg = {
            "id": registro.ID_AUD,
            "tabela": registro.TABELA,
            "acao": registro.ACAO,
            "usuario": registro.USUARIO,
            "data_hora": str(registro.DATA_HORA),
            "descricao": registro.DESCRICAO
        }

        try:
            # dispara no loop global do servidor
            asyncio.run_coroutine_threadsafe(manager.broadcast(json.dumps(msg)), loop)
        except Exception as e:
            print(f"⚠️ Erro ao enviar notificação WebSocket: {e}")

        return registro

    except Exception as e:
        db.rollback()
        print(f"❌ Erro ao registrar auditoria: {e}")
        return None