from fastapi import FastAPI
from app.routers import auditoria, fv, sql, report, dependencias, dashboard
from fastapi import WebSocket
from app.services.websocket_manager import manager

app = FastAPI(
    title="Sistema de Gerenciamento de Customizações ERP RM TOTVS",
    description="API para gerenciar fórmulas visuais, consultas SQL, relatórios e dependências",
    version="1.0.0"
)

# Registrar todos os routers
app.include_router(fv.router)           # /fv
app.include_router(sql.router)          # /sql  
app.include_router(report.router)       # /report
app.include_router(dependencias.router) # /dependencias
app.include_router(dashboard.router)    # /dashboard
app.include_router(auditoria.router)   # /auditoria 

@app.get("/")
def root():
    return {
        "message": "Sistema de Gerenciamento de Customizações ERP RM TOTVS",
        "version": "1.0.0",
        "endpoints": {
            "fv": "/fv - Fórmulas Visuais",
            "sql": "/sql - Consultas SQL", 
            "report": "/report - Relatórios",
            "dependencias": "/dependencias - Dependências entre objetos",
            "dashboard": "/dashboard - Estatísticas gerais",
            "aud": "/aud - Auditoria e histórico de alterações"
        }
    }

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "API funcionando normalmente"}


@app.websocket("/ws/notificacoes")
async def websocket_notificacoes(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Mantém conexão aberta
            await websocket.receive_text()
    except:
        manager.disconnect(websocket)