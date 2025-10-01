from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Notificacao
from app.schemas import NotificacaoOut

router = APIRouter(prefix="/notificacoes", tags=["Notificações"])

@router.get("/", response_model=List[NotificacaoOut])
def listar_notificacoes(usuario: str, db: Session = Depends(get_db)):
    return db.query(Notificacao).filter(Notificacao.usuario == usuario).order_by(Notificacao.data_hora.desc()).all()

@router.patch("/{notif_id}/ler")
def marcar_como_lida(notif_id: int, db: Session = Depends(get_db)):
    notif = db.query(Notificacao).filter(Notificacao.id == notif_id).first()
    if notif:
        notif.lida = True
        db.commit()
        return {"status": "ok"}
    return {"status": "not found"}
