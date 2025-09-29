import time
import json
import asyncio
from datetime import datetime
from app.database import SessionLocal
from app.models import AUD_ALTERACAO, AUD_DEPENDENCIAS  
from app.services.websocket_manager import manager, loop  # loop global thread-safe

WS_AVAILABLE = True


def _get_last_seen_id(db):
    """Busca o maior ID_AUD existente para começar a ler a partir dele."""
    last = db.query(AUD_ALTERACAO).order_by(AUD_ALTERACAO.ID_AUD.desc()).first()
    return last.ID_AUD if last else 0


def _get_dependencias(db, tabela, id_item, codcoligada):
    """Retorna dependências relacionadas ao item alterado."""
    depende_de_item = db.query(AUD_DEPENDENCIAS).filter(
        AUD_DEPENDENCIAS.CODCOLIGADA == codcoligada,
        AUD_DEPENDENCIAS.TIPO_ORIGEM == tabela,
        AUD_DEPENDENCIAS.ID_ORIGEM == id_item
    ).all()

    item_depende = db.query(AUD_DEPENDENCIAS).filter(
        AUD_DEPENDENCIAS.CODCOLIGADA == codcoligada,
        AUD_DEPENDENCIAS.TIPO_DESTINO == tabela,
        AUD_DEPENDENCIAS.ID_DESTINO == id_item
    ).all()

    return {
        "depende_de_item": [
            {"tipo_destino": d.TIPO_DESTINO, "id_destino": d.ID_DESTINO} for d in depende_de_item
        ],
        "item_depende": [
            {"tipo_origem": d.TIPO_ORIGEM, "id_origem": d.ID_ORIGEM} for d in item_depende
        ]
    }


def _to_payload(record, db):
    """Monta JSON leve para enviar aos clientes WebSocket, incluindo dependências."""
    dependencias = _get_dependencias(db, record.TABELA, record.CHAVE, getattr(record, "CODCOLIGADA", 0))
    return json.dumps(
        {
            "id": record.ID_AUD,
            "tabela": record.TABELA,
            "chave": getattr(record, "CHAVE", None),
            "acao": record.ACAO,
            "usuario": record.USUARIO,
            "data_hora": record.DATA_HORA.isoformat() if isinstance(record.DATA_HORA, datetime) else str(record.DATA_HORA),
            "descricao": record.DESCRICAO,
            "dependencias": dependencias 
        },
        ensure_ascii=False,
    )


def notification_loop(interval_seconds=5):
    """Loop que verifica a tabela AUD_ALTERACAO por novos registros e envia notificações via WebSocket."""
    db = SessionLocal()
    try:
        last_seen_id = _get_last_seen_id(db)
    finally:
        db.close()

    while True:
        db = SessionLocal()
        try:
            novos = (
                db.query(AUD_ALTERACAO)
                .filter(AUD_ALTERACAO.ID_AUD > last_seen_id)
                .order_by(AUD_ALTERACAO.ID_AUD.asc())
                .all()
            )

            for registro in novos:
                if WS_AVAILABLE:
                    db_ws = SessionLocal()
                    try:
                        payload = _to_payload(registro, db_ws)
                        asyncio.run_coroutine_threadsafe(manager.broadcast(payload), loop)
                    finally:
                        db_ws.close()

                last_seen_id = registro.ID_AUD

        except Exception as e:
            # Mostra apenas erros importantes no console
            print(f"[ERRO] Falha ao checar alterações: {e}")

        finally:
            db.close()

        time.sleep(interval_seconds)


if __name__ == "__main__":
    notification_loop()
