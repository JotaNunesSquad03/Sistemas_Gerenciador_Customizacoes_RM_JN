from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Importar modelos e schemas
from app.models import Base, AUD_FV, AUD_SQL, AUD_REPORT, AUD_DEPENDENCIAS
from app.schemas import FVCreate, SQLCreate, ReportCreate, DependenciaCreate

# Criar engine SQLite em memória
engine = create_engine("sqlite:///:memory:", echo=True)
SessionLocal = sessionmaker(bind=engine)
Base.metadata.create_all(engine)  # cria todas as tabelas

# Criar uma sessão
session = SessionLocal()

try:
    # -----------------------------
    # Teste AUD_FV
    # -----------------------------
    fv_data = FVCreate(
        CODCOLIGADA=0,
        ID=1,
        NOME="Email",
        DESCRICAO="Email",
        IDCATEGORIA=4,
        ATIVO=False,
        RECCREATEDBY="deivide.nascimento"
    )
    fv = AUD_FV(**fv_data.model_dump())
    session.add(fv)

    # -----------------------------
    # Teste AUD_SQL
    # -----------------------------
    sql_data = SQLCreate(
        CODCOLIGADA=0,
        APLICACAO="CODEF001.0005",
        CODSENTENCA="RETORNA DADOS DA FILIAL POR DOCUMENTO",
        TITULO="Retorna dados",
        SENTENCA="SELECT * FROM FLAN",
        TAMANHO=1211,
        RECCREATEDBY="wffluig"
    )
    sql = AUD_SQL(**sql_data.model_dump())
    session.add(sql)

    # -----------------------------
    # Teste AUD_REPORT
    # -----------------------------
    report_data = ReportCreate(
        CODCOLIGADA=0,
        ID=10,
        CODAPLICACAO="M",
        CODIGO="SAGRA1",
        DESCRICAO="Relatório de Produtividade",
        RECCREATEDBY="mestre"
    )
    report = AUD_REPORT(**report_data.model_dump())
    session.add(report)

    # -----------------------------
    # Teste AUD_DEPENDENCIAS
    # -----------------------------
    dep_data = DependenciaCreate(
        CODCOLIGADA=0,
        TIPO_ORIGEM="FV",
        ID_ORIGEM="1",
        TIPO_DESTINO="SQL",
        ID_DESTINO="RETORNA DADOS DA FILIAL POR DOCUMENTO",
        RECCREATEDON=datetime.now()
    )
    dependencia = AUD_DEPENDENCIAS(**dep_data.model_dump())
    session.add(dependencia)

    # Commit das alterações
    session.commit()

    # -----------------------------
    # Consulta de teste
    # -----------------------------
    fv_test = session.query(AUD_FV).first()
    print("AUD_FV inserido:", fv_test.NOME)

    sql_test = session.query(AUD_SQL).first()
    print("AUD_SQL inserido:", sql_test.TITULO)

    report_test = session.query(AUD_REPORT).first()
    print("AUD_REPORT inserido:", report_test.DESCRICAO)

    dep_test = session.query(AUD_DEPENDENCIAS).first()
    print("AUD_DEPENDENCIAS inserido:", dep_test.TIPO_ORIGEM, "->", dep_test.TIPO_DESTINO)

finally:
    session.close()
