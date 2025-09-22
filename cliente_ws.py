import asyncio
import websockets

async def listen():
    uri = "ws://127.0.0.1:8000/ws/notificacoes"
    async with websockets.connect(uri) as websocket:
        print("✅ Conectado ao servidor WebSocket")
        while True:
            msg = await websocket.recv()
            print("🔔 Notificação recebida:", msg)

if __name__ == "__main__":
    asyncio.run(listen())