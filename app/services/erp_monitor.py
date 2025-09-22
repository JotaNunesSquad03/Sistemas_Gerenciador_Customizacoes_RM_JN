# app/services/erp_monitor.py
import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database import SessionLocal, engine  # usa o mesmo banco já configurado
from app.services.audit import log_aud_alteracao
from app import models

logging.basicConfig(level=logging.INFO)

TABLE_MAPPING = {
    'TSQL': 'AUD_SQL',
    'TFV': 'AUD_FV',
    'TREPORT': 'AUD_REPORT',
}

ACTION_MAPPING = {
    'INCLUSAO': 'CREATE',
    'ALTERACAO': 'UPDATE',
    'EXCLUSAO': 'DELETE',
}


class ERPMonitor:
    def __init__(self):
        self.erp_engine = engine

    def _get_last_check(self, db: Session):
        cursor = db.query(models.AUD_CURSOR).order_by(models.AUD_CURSOR.ID.desc()).first()
        if cursor:
            return cursor.LAST_CHECK
        else:
            initial_time = datetime.utcnow() - timedelta(days=30)
            new_cursor = models.AUD_CURSOR(LAST_CHECK=initial_time)
            db.add(new_cursor)
            db.commit()
            return initial_time

    def _update_cursor(self, db: Session, new_time: datetime):
        new_cursor = models.AUD_CURSOR(LAST_CHECK=new_time)
        db.add(new_cursor)
        db.commit()

    def check_for_changes(self, db: Session):
        try:
            last_check = self._get_last_check(db)

            query = text("""
                SELECT 
                    DATA_HORA,
                    TABELA,
                    CHAVE,
                    ACAO,
                    USUARIO,
                    DESCRICAO
                FROM AUD_ALTERACAO
                WHERE DATA_HORA > :last_check
                  AND TABELA IN ('TSQL', 'TFV', 'TREPORT')
                ORDER BY DATA_HORA ASC
            """)

            with self.erp_engine.connect() as conn:
                result = conn.execute(query, {"last_check": last_check})
                rows = result.fetchall()

            count = 0
            last_processed_time = last_check
            for row in rows:
                change = row._mapping
                if self._process_change(db, change):
                    count += 1
                    last_processed_time = change['DATA_HORA']

            if count > 0:
                self._update_cursor(db, last_processed_time)

            logging.info(f"Processadas {count} mudanças desde {last_check}")

        except Exception as e:
            logging.exception(f"Erro ao monitorar alterações: {e}")

    def _process_change(self, db: Session, change_map) -> bool:
        try:
            tabela_erp = change_map['TABELA']
            acao_erp = change_map['ACAO']

            tabela_sistema = TABLE_MAPPING.get(tabela_erp)
            if not tabela_sistema:
                return False

            acao_sistema = ACTION_MAPPING.get(acao_erp, acao_erp)
            chave = change_map['CHAVE']
            usuario = change_map.get('USUARIO') or 'ERP'
            descricao = change_map.get('DESCRICAO') or 'Sem descrição'

            log_aud_alteracao(
                db=db,
                tabela=tabela_sistema,
                chave=chave,
                acao=acao_sistema,
                usuario=usuario,
                descricao=f"Alteração detectada: {descricao}",
            )

            logging.info(f"[NOTIFY] {acao_sistema} em {tabela_sistema} | {chave}")
            return True

        except Exception as e:
            logging.exception(f"Erro ao processar mudança {change_map.get('CHAVE')}: {e}")
            return False


def monitor_changes():
    monitor = ERPMonitor()
    db = SessionLocal()
    try:
        monitor.check_for_changes(db)
    finally:
        db.close()


if __name__ == "__main__":
    monitor_changes()
