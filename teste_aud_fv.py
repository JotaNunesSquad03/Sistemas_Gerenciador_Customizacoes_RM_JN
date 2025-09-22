# from app.models import AUD_FV, AUD_SQL, AUD_REPORT
# from app.database import SessionLocal

# session = SessionLocal()

# try:
#     registro = session.get(AUD_FV, {"CODCOLIGADA": 0, "ID": 14})
#     if registro:
#         print("Registro encontrado:", registro.NOME)
#     else:
#         print("Registro não encontrado")
# finally:
#     session.close()

# try:
#     registro = session.get(AUD_SQL, {"CODCOLIGADA": 0, "APLICACAO": "A", "CODSENTENCA": "CODE_A001"})
#     if registro:
#         print("Registro encontrado:", registro.TITULO)
#     else:
#         print("Registro não encontrado")
# finally:
#     session.close()

# try:
#     registro = session.get(AUD_REPORT, {"CODCOLIGADA": 0, "ID": 21})
#     if registro:
#         print("Registro encontrado:", registro.DESCRICAO)
#     else:
#         print("Registro não encontrado")
# finally:
#     session.close()


