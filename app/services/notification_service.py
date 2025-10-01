import time
import json
import asyncio
from datetime import datetime
from app.database import SessionLocal
from app.models import AUD_ALTERACAO, AUD_DEPENDENCIAS, Notificacao
from app.services.websocket_manager import manager, loop  # loop global thread-safe

WS_AVAILABLE = True  # ativa envio via WebSocket

def _get_last_seen_id(db):
    """Busca o maior ID_AUD existente para começar a ler a partir dele."""
    last = db.query(AUD_ALTERACAO).order_by(AUD_ALTERACAO.ID_AUD.desc()).first()
    return last.ID_AUD if last else 0

def _get_usuarios_dependentes(db, tabela, id_item, codcoligada):
    """Retorna lista de usuários que devem receber notificações pela dependência."""
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

    usuarios = set()
    for dep in depende_de_item + item_depende:
        if hasattr(dep, "USUARIO") and dep.USUARIO:
            usuarios.add(dep.USUARIO)
    return list(usuarios)

def _to_payload(notificacao):
    """Transforma a notificação em JSON para WebSocket."""
    return json.dumps(
        {
            "id": notificacao.id,
            "usuario": notificacao.usuario,
            "tabela": notificacao.tabela,
            "chave": notificacao.chave,
            "acao": notificacao.acao,
            "descricao": notificacao.descricao,
            "data_hora": notificacao.data_hora.isoformat(),
            "lida": notificacao.lida
        },
        ensure_ascii=False
    )

def notification_loop(interval_seconds=5):
    """Loop que verifica AUD_ALTERACAO e cria notificações."""
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
                # busca usuários que devem receber a notificação
                usuarios = _get_usuarios_dependentes(
                    db, registro.TABELA, getattr(registro, "CHAVE", None), getattr(registro, "CODCOLIGADA", 0)
                )

                for usuario in usuarios:
                    # cria registro de notificação
                    notificacao = Notificacao(
                        usuario=usuario,
                        tabela=registro.TABELA,
                        chave=getattr(registro, "CHAVE", None),
                        acao=registro.ACAO,
                        descricao=registro.DESCRICAO,
                        data_hora=registro.DATA_HORA or datetime.utcnow()
                    )
                    db.add(notificacao)
                    db.commit()
                    db.refresh(notificacao)

                    # envia via WebSocket se estiver disponível
                    if WS_AVAILABLE:
                        asyncio.run_coroutine_threadsafe(manager.broadcast(_to_payload(notificacao)), loop)

                last_seen_id = registro.ID_AUD

        except Exception as e:
            print(f"[ERRO] Falha ao processar notificações: {e}")

        finally:
            db.close()

        time.sleep(interval_seconds)

if __name__ == "__main__":
    notification_loop()
