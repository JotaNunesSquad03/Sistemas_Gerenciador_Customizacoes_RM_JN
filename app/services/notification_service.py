import time
import json
import asyncio
from datetime import datetime
from app.database import SessionLocal
from app.models import AUD_FV, AUD_SQL, AUD_REPORT, DEPENDENCIA
from app.services.websocket_manager import manager, loop  # loop global thread-safe

WS_AVAILABLE = True  # ativa envio via WebSocket

# ---------------------------
# Helpers
# ---------------------------

def _get_last_seen_id(db, model):
    """Busca o maior ID existente do modelo para iniciar a leitura."""
    last = db.query(model).order_by(model.ID.desc()).first()
    return last.ID if last else 0

def _get_usuarios_dependentes(db, tabela, id_item):
    """
    Retorna lista de "usuários" dependentes da alteração de um item.
    Como não há campo de usuário, retornamos representações dos IDs relacionados.
    """
    usuarios = set()

    if tabela == "AUD_FV":
        dependencias = db.query(DEPENDENCIA).filter(DEPENDENCIA.ID_FV == id_item).all()
    elif tabela == "AUD_SQL":
        dependencias = db.query(DEPENDENCIA).filter(DEPENDENCIA.ID_SQL == id_item).all()
    elif tabela == "AUD_REPORT":
        dependencias = db.query(DEPENDENCIA).filter(DEPENDENCIA.ID_REPORT == id_item).all()
    else:
        dependencias = []

    for dep in dependencias:
        usuarios.add(f"SQL:{dep.ID_SQL}-FV:{dep.ID_FV}-REPORT:{dep.ID_REPORT}")

    return list(usuarios)

def _to_payload(notificacao):
    """Transforma a notificação em JSON para WebSocket."""
    return json.dumps(
        {
            "id": notificacao["id"],
            "usuario": notificacao["usuario"],
            "tabela": notificacao["tabela"],
            "acao": notificacao["acao"],
            "descricao": notificacao["descricao"],
            "data_hora": notificacao["data_hora"].isoformat(),
            "lida": notificacao.get("lida", False)
        },
        ensure_ascii=False
    )

# ---------------------------
# Loop de notificações
# ---------------------------

def notification_loop(interval_seconds=5):
    """Loop que verifica alterações nos modelos e cria notificações para o front."""
    with SessionLocal() as db:
        last_ids = {
            "AUD_FV": _get_last_seen_id(db, AUD_FV),
            "AUD_SQL": _get_last_seen_id(db, AUD_SQL),
            "AUD_REPORT": _get_last_seen_id(db, AUD_REPORT)
        }

    while True:
        with SessionLocal() as db:
            try:
                modelos = [("AUD_FV", AUD_FV), ("AUD_SQL", AUD_SQL), ("AUD_REPORT", AUD_REPORT)]
                for nome_tabela, modelo in modelos:
                    novos = db.query(modelo).filter(modelo.ID > last_ids[nome_tabela]).order_by(modelo.ID.asc()).all()

                    for registro in novos:
                        usuarios = _get_usuarios_dependentes(db, nome_tabela, getattr(registro, "ID", None))

                        for usuario in usuarios:
                            notificacao = {
                                "id": f"{nome_tabela}_{getattr(registro, 'ID', None)}_{usuario}",
                                "usuario": usuario,
                                "tabela": nome_tabela,
                                "acao": "CREATE/UPDATE",
                                "descricao": getattr(registro, "DESCRICAO", "") or getattr(registro, "TITULO", ""),
                                "data_hora": datetime.utcnow(),
                                "lida": False  # sempre inicia como não lida
                            }

                            if WS_AVAILABLE:
                                asyncio.run_coroutine_threadsafe(manager.broadcast(_to_payload(notificacao)), loop)

                        # Atualiza o último ID processado
                        last_ids[nome_tabela] = getattr(registro, "ID", 0)

            except Exception as e:
                print(f"[ERRO] Falha no monitor de espelhos: {e}")

        time.sleep(interval_seconds)


if __name__ == "__main__":
    notification_loop()










