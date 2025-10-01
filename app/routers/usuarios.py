from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext

from app.database import get_db
from app import models, schemas

# ----------------------------
# Configurações de segurança
# ----------------------------
SECRET_KEY = "sua_chave_secreta_muito_forte"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def criar_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def hash_senha(senha: str) -> str:
    # bcrypt não suporta mais de 72 bytes
    senha_truncada = senha[:72]
    return pwd_context.hash(senha_truncada)

def verificar_senha(senha: str, senha_hash: str) -> bool:
    senha_truncada = senha[:72]
    return pwd_context.verify(senha_truncada, senha_hash)

# ----------------------------
# Router
# ----------------------------
router = APIRouter(prefix="/usuarios", tags=["Usuários"])

@router.post("/register", response_model=schemas.UsuarioOut)
def registrar_usuario(usuario: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    db_usuario = db.query(models.Usuario).filter(models.Usuario.email == usuario.email).first()
    if db_usuario:
        raise HTTPException(status_code=400, detail="Email já cadastrado")

    senha_hash = hash_senha(usuario.senha)
    novo_usuario = models.Usuario(
        nome=usuario.nome,
        email=usuario.email,
        senha_hash=senha_hash,
        funcao=usuario.funcao
    )
    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)
    return novo_usuario

@router.post("/login", response_model=schemas.Token)
def login(form_data: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(models.Usuario.email == form_data.email).first()
    if not usuario or not verificar_senha(form_data.senha, usuario.senha_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email ou senha incorretos")

    token = criar_token({"sub": usuario.email, "funcao": usuario.funcao})
    return {"access_token": token, "token_type": "bearer"}
