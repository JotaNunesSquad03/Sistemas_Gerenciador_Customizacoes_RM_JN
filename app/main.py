from fastapi import FastAPI, WebSocket
from app.routers import auditoria, fv, sql, report, dependencias, dashboard, docs
from app.services.websocket_manager import manager
from app.services.notification_service import notification_loop
from app.services.monitor_espelhos import monitor_espelhos  # <<< importe aqui
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
app.include_router(dependencias.router) # /dependencias
app.include_router(dashboard.router)    # /dashboard
app.include_router(auditoria.router)    # /auditoria
app.include_router(docs.router)         # /docs

@app.get("/")
def root():
    return {
        "message": "Sistema de Gerenciamento de Customizações ERP RM TOTVS",
        "version": "1.0.0",
        "endpoints": {
            "fv": "/fv - Fórmulas Visuais",
            "sql": "/sql - Consultas SQL",
            "report": "/report - Relatórios",
            "dependencias": "/dependencias - Dependências",
            "dashboard": "/dashboard - Estatísticas gerais",
            "auditoria": "/auditoria - Auditoria e histórico de alterações",
            "ws_notificacoes": "/ws/notificacoes - WebSocket para notificações em tempo real"
        }
    }

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "API funcionando normalmente"}

# WebSocket
@app.websocket("/ws/notificacoes")
async def websocket_notificacoes(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Mantém a conexão viva; ignore o conteúdo
            await websocket.receive_text()
    except Exception:
        manager.disconnect(websocket)

# Startup: inicia os dois workers
@app.on_event("startup")
def start_background_workers():
    t_notify = threading.Thread(target=notification_loop, kwargs={"interval_seconds": 5}, daemon=True)
    t_notify.start()

    t_monitor = threading.Thread(target=monitor_espelhos, kwargs={"interval_seconds": 30}, daemon=True)
    t_monitor.start()