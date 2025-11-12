from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, PrimaryKeyConstraint, ForeignKey
from datetime import datetime
from app.database import Base

class AUD_FV(Base):
    __tablename__ = "AUD_FV"
    CODCOLIGADA = Column(Integer, nullable=True)
    ID = Column(Integer, primary_key=True, autoincrement=True) 
    NOME = Column(String(255), nullable=True)
    DESCRICAO = Column(Text, nullable=True)
    IDCATEGORIA = Column(Integer, nullable=True)
    ATIVO = Column(Boolean, nullable=True)
    RECCREATEDBY = Column(String(100), nullable=True)
    RECCREATEDON = Column(DateTime, nullable=True)
    RECMODIFIEDBY = Column(String(100), nullable=True)
    RECMODIFIEDON = Column(DateTime, nullable=True)

    __table_args__ = (
        PrimaryKeyConstraint('ID'),
    )

class AUD_SQL(Base):
    __tablename__ = "AUD_SQL"
    
    CODSENTENCA = Column(String(100), primary_key=True)  # vira o ID

    CODCOLIGADA = Column(Integer, nullable=True)
    APLICACAO = Column(String(100), nullable=True)
    TITULO = Column(String(255), nullable=True)
    SENTENCA = Column(Text, nullable=True)
    TAMANHO = Column(Integer, nullable=True)
    RECCREATEDBY = Column(String(100), nullable=True)
    RECCREATEDON = Column(DateTime, nullable=True)
    RECMODIFIEDBY = Column(String(100), nullable=True)
    RECMODIFIEDON = Column(DateTime, nullable=True)

class AUD_REPORT(Base):
    __tablename__ = "AUD_REPORT"

    CODCOLIGADA = Column(Integer, nullable=True)
    ID = Column(Integer, primary_key=True, autoincrement=True) 
    CODAPLICACAO = Column(String(100), nullable=True)
    CODIGO = Column(String(100), nullable=True)
    DESCRICAO = Column(String(255), nullable=True)
    RECCREATEDBY = Column(String(100), nullable=True)
    RECCREATEDON = Column(DateTime, nullable=True)
    USRULTALTERACAO = Column(String(100), nullable=True)
    DATAULTALTERACAO = Column(DateTime, nullable=True)
    LIDA = Column(Boolean, default=False, nullable=True)

    __table_args__ = (
        PrimaryKeyConstraint("ID"),
    )
