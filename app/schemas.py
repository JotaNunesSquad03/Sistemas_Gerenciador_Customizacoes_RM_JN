from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# -----------------------------
# Schemas para AUD_FV
# -----------------------------
class FVBase(BaseModel):
    CODCOLIGADA: int
    NOME: Optional[str] = None
    DESCRICAO: Optional[str] = None
    IDCATEGORIA: Optional[int] = None
    ATIVO: Optional[bool] = None

class FVRead(FVBase):
    ID: int
    RECCREATEDBY: Optional[str]
    RECCREATEDON: Optional[datetime]
    RECMODIFIEDBY: Optional[str]
    RECMODIFIEDON: Optional[datetime]

    class Config:
        orm_mode = True

# -----------------------------
# Schemas para AUD_SQL
# -----------------------------
class SQLBase(BaseModel):
    CODCOLIGADA: int
    APLICACAO: str
    CODSENTENCA: str
    TITULO: Optional[str] = None
    SENTENCA: Optional[str] = None
    TAMANHO: Optional[int] = None

class SQLRead(SQLBase):
    RECCREATEDBY: Optional[str]
    RECCREATEDON: Optional[datetime]
    RECMODIFIEDBY: Optional[str]
    RECMODIFIEDON: Optional[datetime]

    class Config:
        orm_mode = True

# -----------------------------
# Schemas para AUD_REPORT
# -----------------------------
class ReportBase(BaseModel):
    CODCOLIGADA: int
    CODAPLICACAO: str
    CODIGO: Optional[str] = None
    DESCRICAO: Optional[str] = None

class ReportRead(ReportBase):
    ID: int
    RECCREATEDBY: Optional[str]
    RECCREATEDON: Optional[datetime]
    USRULTALTERACAO: Optional[str]
    DATAULTALTERACAO: Optional[datetime]
    LIDA: Optional[bool] = False

    class Config:
        orm_mode = True

# -----------------------------
# Schemas para DEPENDENCIAS
# -----------------------------

class DependenciaBase(BaseModel):
    descricao:str
    nv_risco:int

class DependenciaCreate(DependenciaBase):
    pass

class Dependencia(DependenciaBase):
    id: int 

    class Config:
        orm_mode = True

# -----------------------------
# Schemas para DEPENDENCIAS_REGISTRO
# -----------------------------

class DependenciaRegistroBase(BaseModel):
    tabela_origem: str
    id_origem: int
    id_dependencia: int
    is_principal: bool

class DependenciaRegistroCreate(DependenciaRegistroBase):
    pass

class DependenciaRegistro(DependenciaRegistroBase):
    id: int 

    class Config:
        orm_mode = True

# -----------------------------
# Schemas para AUD_USUARIO
# -----------------------------

class UsuarioCreate(BaseModel):
    nome: str
    email: EmailStr
    senha: str
    funcao: str

class UsuarioOut(BaseModel):
    id: int
    nome: str
    email: EmailStr
    funcao: str

    class Config:
        orm_mode = True

# -----------------------------
# Schemas para Autenticação 
# -----------------------------

class Token(BaseModel):
    access_token: str
    token_type: str

    class Config:
        orm_mode = True

# -----------------------------
# Schemas para Documentação 
# -----------------------------

class DocCustomBase(BaseModel):
    TABELA: str
    ID_REGISTRO: str
    DESCRICAO: Optional[str] = None
    FUNCIONALIDADES: Optional[str] = None
    CONFIGURACOES: Optional[str] = None
    OBSERVACAO: Optional[str] = None

class DocCustomCreate(DocCustomBase):
    pass  

class DocCustom(DocCustomBase):
    ID: int
    RECCREATEDON: datetime
    RECMODIFIEDON: Optional[datetime] = None

    class Config:
        from_attributes = True