from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, PrimaryKeyConstraint
from datetime import datetime
from app.database import Base

class AUD_FV(Base):
    __tablename__ = "AUD_FV"
    CODCOLIGADA = Column(Integer, nullable=False)
    ID = Column(Integer, nullable=False)
    NOME = Column(String(255), nullable=True)
    DESCRICAO = Column(Text, nullable=True)
    IDCATEGORIA = Column(Integer, nullable=True)
    ATIVO = Column(Boolean, nullable=True)
    RECCREATEDBY = Column(String(100), nullable=True)
    RECCREATEDON = Column(DateTime, nullable=True)
    RECMODIFIEDBY = Column(String(100), nullable=True)
    RECMODIFIEDON = Column(DateTime, nullable=True)

    __table_args__ = (
        PrimaryKeyConstraint('CODCOLIGADA', 'ID'),
    )

class AUD_SQL(Base):
    __tablename__ = "AUD_SQL"

    CODCOLIGADA = Column(Integer, nullable=False)
    APLICACAO = Column(String(100), nullable=False)
    CODSENTENCA = Column(String(100), nullable=False)
    TITULO = Column(String(255), nullable=True)
    SENTENCA = Column(Text, nullable=True)
    TAMANHO = Column(Integer, nullable=True)
    RECCREATEDBY = Column(String(100), nullable=True)
    RECCREATEDON = Column(DateTime, nullable=True)
    RECMODIFIEDBY = Column(String(100), nullable=True)
    RECMODIFIEDON = Column(DateTime, nullable=True)

    __table_args__ = (
        PrimaryKeyConstraint("CODCOLIGADA", "APLICACAO", "CODSENTENCA"),
    )

class AUD_REPORT(Base):
    __tablename__ = "AUD_REPORT"

    CODCOLIGADA = Column(Integer, nullable=False)
    ID = Column(Integer, nullable=False)
    CODAPLICACAO = Column(String(100), nullable=False)
    CODIGO = Column(String(100), nullable=True)
    DESCRICAO = Column(String(255), nullable=True)
    RECCREATEDBY = Column(String(100), nullable=True)
    RECCREATEDON = Column(DateTime, nullable=True)
    USRULTALTERACAO = Column(String(100), nullable=True)
    DATAULTALTERACAO = Column(DateTime, nullable=True)

    __table_args__ = (
        PrimaryKeyConstraint("CODCOLIGADA", "ID"),
    )

class AUD_DEPENDENCIAS(Base):
    __tablename__ = "AUD_DEPENDENCIAS"

    ID = Column(Integer, primary_key=True, index=True, autoincrement=True)
    CODCOLIGADA = Column(Integer, nullable=False)
    TIPO_ORIGEM = Column(String(50), nullable=False)
    ID_ORIGEM = Column(String(100), nullable=False)
    TIPO_DESTINO = Column(String(50), nullable=False)
    ID_DESTINO = Column(String(100), nullable=False)
    RECCREATEDON = Column(DateTime, nullable=True)

class AUD_ALTERACAO(Base):
    __tablename__ = "AUD_ALTERACAO"

    ID_AUD = Column(Integer, primary_key=True, index=True, autoincrement=True)
    TABELA = Column(String(50), nullable=False)
    CHAVE = Column(String(200), nullable=False)
    ACAO = Column(String(20), nullable=False)
    USUARIO = Column(String(100), nullable=False)
    DATA_HORA = Column(DateTime, default=datetime.utcnow, nullable=False)
    DESCRICAO = Column(String(500), nullable=True)
    VALOR_ANTERIOR = Column(Text, nullable=True)
    VALOR_NOVO = Column(Text, nullable=True)


class AUD_CURSOR(Base):
    __tablename__ = "AUD_CURSOR"

    ID = Column(Integer, primary_key=True, index=True, autoincrement=True)
    LAST_CHECK = Column(DateTime, nullable=False)