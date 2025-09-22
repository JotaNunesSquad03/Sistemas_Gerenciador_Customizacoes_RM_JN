# test_audit.py
from app.database import SessionLocal
from app.services.audit import log_aud_alteracao

db = SessionLocal()

# Simula um CREATE em uma Fórmula Visual
log_aud_alteracao(
    db=db,
    tabela="AUD_FV",
    chave="1|1101",
    acao="CREATE",
    usuario="camyla",
    descricao="Simulação de criação de FV de teste",
    valor_novo={"descricao": "Minha FV exemplo", "codcoligada": 1}
)

# Simula um UPDATE em uma SQL
log_aud_alteracao(
    db=db,
    tabela="AUD_SQL",
    chave="1|2202",
    acao="UPDATE",
    usuario="tester",
    descricao="SQL alterada na simulação",
    valor_anterior={"consulta": "SELECT * FROM PRODUTOS"},
    valor_novo={"consulta": "SELECT * FROM PRODUTOS WHERE ATIVO=1"}
)

print("✅ Registros simulados inseridos em AUD_ALTERACAO")