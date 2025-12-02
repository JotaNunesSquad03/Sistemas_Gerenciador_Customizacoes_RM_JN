from sqlalchemy.orm import Session
from app import models, schemas

# ------------ DEPENDENCIAS ------------

def create_dependencia(db: Session, data: schemas.DependenciaCreate):
    dependencia = models.Dependencias(**data.dict())
    db.add(dependencia)
    db.commit()
    db.refresh(dependencia)
    return dependencia

def get_dependencias(db: Session):
    return db.query(models.Dependencias).all()


# ------------ DEPENDENCIAS_REGISTRO ------------

def create_dependencia_registro(db: Session, data: schemas.DependenciaRegistroCreate):
    registro = models.DependenciasRegistro(**data.dict())
    db.add(registro)
    db.commit()
    db.refresh(registro)
    return registro

def get_dependencias_registro(db: Session, tabela: str, id_origem: int):
    return (
        db.query(models.DependenciasRegistro)
        .filter(
            models.DependenciasRegistro.tabela_origem == tabela,
            models.DependenciasRegistro.id_origem == id_origem
        )
        .all()
    )