from fastapi import APIRouter , Depends , UploadFile , File , Form , HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import DOC_CUSTOM
from app.schemas import DocCustomCreate, DocCustom

router = APIRouter(prefix="/documentacao", tags=["Documentacao"])

"""uter.post("/", response_model=Documentacao)
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

    return {"message": "Documento apagado com sucesso"}"""

# Criar documentação
@router.post("/", response_model=DocCustom)
def criar_doc(dados: DocCustomCreate, db: Session = Depends(get_db)):
    doc = DOC_CUSTOM(**dados.dict())
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc

# Listar documentação de um registro
@router.get("/{tabela}/{id_registro}", response_model=List[DocCustom])
def listar_doc(tabela: str, id_registro: str, db: Session = Depends(get_db)):
    docs = (
        db.query(DOC_CUSTOM)
        .filter(
            DOC_CUSTOM.TABELA == tabela,
            DOC_CUSTOM.ID_REGISTRO == id_registro
        )
        .all()
    )
    return docs


# Deletar documentação
@router.delete("/{id}")
def deletar_doc_custom(id: str, db: Session = Depends(get_db)):
    doc = db.query(DOC_CUSTOM).filter(DOC_CUSTOM.ID == id).first()

    if not doc:
        raise HTTPException(status_code=404, detail="Documento não encontrado")

    db.delete(doc)
    db.commit()

    return {"message": "Documento removido com sucesso"}
