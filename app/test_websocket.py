import asyncio
import websockets

async def test_websocket():
    uri = "ws://localhost:8000/chat/1/2"  # Replace with correct sender_id and receiver_id
    async with websockets.connect(uri) as websocket:
        await websocket.send("Hello from Python WebSocket client!")
        response = await websocket.recv()
        print(f"Received: {response}")

asyncio.run(test_websocket())
