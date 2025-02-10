#!/usr/bin/env python3
import asyncio
import websockets
import logging
import os
from dotenv import load_dotenv

# Configure logging to write in "server.log" in append mode
logging.basicConfig(
    level=logging.INFO,
    filename="server.log",
    filemode="a",
    format="%(asctime)s %(message)s"
)

# Get env variables
load_dotenv()
port = os.getenv("WS_PORT")
ip = os.getenv("WS_IP")

# Global dictionary of clients: websocket -> status ("active" or "inactive")
clients = {}


async def handler(websocket):
    logging.info(f"Client connected: {websocket.remote_address}")
    print(f"Client connected: {websocket.remote_address}")
    # Add the client with a default "inactive" status
    clients[websocket] = "inactive"
    try:
        async for message in websocket:
            # Log the received message in the log file
            logging.info(f"Message received from {websocket.remote_address}: {message}")

            # Mark the sender as "active"
            clients[websocket] = "active"

            # Broadcast the message to all clients with the "inactive" status
            broadcast_clients = [
                ws for ws, status in clients.items() if status == "inactive"
            ]
            if broadcast_clients:
                await asyncio.gather(*[ws.send(message) for ws in broadcast_clients])

            # Set the sender's status back to "inactive"
            clients[websocket] = "inactive"
    except websockets.ConnectionClosed:
        logging.info(f"Connection closed: {websocket.remote_address}")
        print(f"Connection closed: {websocket.remote_address}")
    finally:
        # Cleanup when the client disconnects
        del clients[websocket]
        logging.info(f"Client disconnected: {websocket.remote_address}")
        print(f"Client disconnected: {websocket.remote_address}")


async def main():


    async with websockets.serve(handler, ip, port):
        print(f"Server started at ws://{ip}:{port}")
        await asyncio.Future()  # Keeps the server running indefinitely


if __name__ == "__main__":
    asyncio.run(main())
