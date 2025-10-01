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

    class Config:
        orm_mode = True

# -----------------------------
# Schemas para AUD_DEPENDENCIAS
# -----------------------------
class DependenciaBase(BaseModel):
    CODCOLIGADA: int
    TIPO_ORIGEM: str
    ID_ORIGEM: str
    TIPO_DESTINO: str
    ID_DESTINO: str

class DependenciaCreate(DependenciaBase):
    RECCREATEDON: Optional[datetime] = None

class DependenciaUpdate(BaseModel):
    TIPO_ORIGEM: Optional[str] = None
    ID_ORIGEM: Optional[str] = None
    TIPO_DESTINO: Optional[str] = None
    ID_DESTINO: Optional[str] = None

class DependenciaRead(DependenciaBase):
    ID: int
    RECCREATEDON: Optional[datetime]

    class Config:
        orm_mode = True


# -----------------------------
# Schema para AUD_ALTERACAO (leitura)
# -----------------------------

class AudAlteracaoRead(BaseModel):
    ID_AUD: int
    TABELA: str
    CHAVE: str
    ACAO: str
    USUARIO: str
    DATA_HORA: datetime
    DESCRICAO: Optional[str] = None
    VALOR_ANTERIOR: Optional[str] = None
    VALOR_NOVO: Optional[str] = None

    class Config:
        from_attributes = True

# -----------------------------
# Schemas para AUD_DOCS
# -----------------------------
class DocBase(BaseModel):
    CHAVE: str
    TITULO: str
    AUTOR: str
    CONTEUDO: str  # Markdown
    TAGS: Optional[str] = None

class DocCreate(DocBase):
    pass

class DocUpdate(BaseModel):
    TITULO: Optional[str] = None
    CONTEUDO: Optional[str] = None
    TAGS: Optional[str] = None

class DocRead(DocBase):
    ID_DOC: int
    DATA_CRIACAO: datetime
    DATA_ATUALIZACAO: datetime

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

class Token(BaseModel):
    access_token: str
    token_type: str

class NotificacaoOut(BaseModel):
    id: int
    id_alteracao: int
    usuario: str
    mensagem: str
    data_hora: datetime
    lida: bool

    class Config:
        orm_mode = True