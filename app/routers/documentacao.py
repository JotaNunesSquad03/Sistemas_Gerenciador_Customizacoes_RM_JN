from fastapi import APIRouter , Depends , UploadFile , File , Form , HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import AUD_DOCUMENTACAO
from app.schemas import DocumentacaoCreate,Documentacao 

router = APIRouter(prefix="/documentacao", tags=["Documentacao"])

@router.post("/", response_model=Documentacao)
def criar_documentacao(dados:DocumentacaoCreate, db: Session = Depends(get_db)):
    doc =AUD_DOCUMENTACAO(**dados.dict())
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc

@router.get("/{tabela}/{id_registro}", response_model=list[Documentacao])
def listar_documentacao(tabela: str, id_registro: int, db: Session = Depends(get_db)):
    docs = (
        db.query(AUD_DOCUMENTACAO)
        .filter(
            AUD_DOCUMENTACAO.TABELA == tabela,
            AUD_DOCUMENTACAO.ID_REGISTRO == id_registro,
        )
        .all()
    )
    return docs


@router.delete("/{id}")
def deletar_documentacao(id: int, db: Session = Depends(get_db)):
    doc = db.query(AUD_DOCUMENTACAO).filter(AUD_DOCUMENTACAO.ID == id).first()

    if not doc:
        raise HTTPException(status_code=404, detail="Documento não encontrado")

    db.delete(doc)
    db.commit()

    return {"message": "Documento apagado com sucesso"}