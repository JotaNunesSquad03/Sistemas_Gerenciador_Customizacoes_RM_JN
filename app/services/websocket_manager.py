from fastapi import WebSocket
import asyncio

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """Aceita a conexão e adiciona na lista"""
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        """Remove da lista se a conexão cair"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        """
        Envia uma notificação para todos os clientes conectados
        """
        for connection in list(self.active_connections):  # copia para não quebrar no loop
            try:
                await connection.send_text(message)
            except:
                self.disconnect(connection)


# instância global para ser usada no projeto
manager = ConnectionManager()

# loop global do asyncio (usado em threads worker, ex: audit.py)
try:
    loop = asyncio.get_event_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)