from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app import schemas
from app.services import dependencias_service
from app.models import Dependencias, DependenciasRegistro, NvRisco

router = APIRouter(prefix="/dependencias", tags=["Dependencias"])

# ------------ DEPENDENCIAS ------------

@router.post("/", response_model=schemas.Dependencia)
def criar_dependencia(data: schemas.DependenciaCreate, db: Session = Depends(get_db)):
    return dependencias_service.create_dependencia(db, data)

@router.get("/", response_model=list[schemas.Dependencia])
def listar_dependencias(db: Session = Depends(get_db)):
    return dependencias_service.get_dependencias(db)


# ------------ DEPENDENCIAS_REGISTRO ------------

@router.post("/registro", response_model=schemas.DependenciaRegistro)
def criar_dependencia_registro(
    data: schemas.DependenciaRegistroCreate,
    db: Session = Depends(get_db)
):
    return dependencias_service.create_dependencia_registro(db, data)


@router.get("/registro/{tabela_origem}/{id_origem}", response_model=list[schemas.DependenciaRegistro])
def listar_dependencias_registro(
    tabela_origem: str,
    id_origem: int,
    db: Session = Depends(get_db)
):
    return dependencias_service.get_dependencias_registro(db, tabela_origem, id_origem)