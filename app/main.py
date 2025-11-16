from fastapi import FastAPI, WebSocket
from app.routers import auditoria, fv, sql, report, dashboard
from fastapi.middleware.cors import CORSMiddleware
import threading

app = FastAPI(
    title="Sistema de Gerenciamento de Customizações ERP RM TOTVS",
    description="API para gerenciar fórmulas visuais, consultas SQL, relatórios e dependências",
    version="1.0.0"
)

# Routers
app.include_router(fv.router)           # /fv
app.include_router(sql.router)          # /sql
app.include_router(report.router)       # /report
app.include_router(dashboard.router)    # /dashboard
app.include_router(auditoria.router)    # /auditoria

@app.get("/")
def root():
    return {
        "message": "Sistema de Gerenciamento de Customizações ERP RM TOTVS",
        "version": "1.0.0",
        "endpoints": {
            "fv": "/fv - Fórmulas Visuais",
            "sql": "/sql - Consultas SQL",
            "report": "/report - Relatórios",
            "dashboard": "/dashboard - Estatísticas gerais",
            "auditoria": "/auditoria - Auditoria e histórico de alterações",
            "ws_notificacoes": "/ws/notificacoes - WebSocket para notificações em tempo real"
        }
    }
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173","https://sistema-de-gerenciamento-jota-nunes.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "API funcionando normalmente"}

