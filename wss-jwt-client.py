#!/usr/bin/env python3
import asyncio
import websockets
import json
import threading
import ssl
import jwt
import os
from dotenv import load_dotenv
import uuid

# Create UUID for this client
user_id = str(uuid.uuid4())

# Get env variables
load_dotenv()

secret = os.getenv("SECRET_KEY")

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# Generate JWT token
def generate_token(user_id):
    """Génère un token JWT avec un payload simple."""
    payload = {"user_id": user_id}
    return jwt.encode(payload, secret, algorithm="HS256")


async def handle_messages(websocket):
    """
    Écoute en continu les messages reçus depuis le serveur et les affiche immédiatement.
    """
    async for message in websocket:
        try:
            data = json.loads(message)
        except json.JSONDecodeError:
            print("Message reçu n'est pas un JSON valide.")
            continue

        if data.get("type") == "speech":
            print(f"\nText received: {data.get('text')}")
            # Réafficher l'invite pour être certain que l'utilisateur peut continuer à saisir
            print("Enter your message: ", end="", flush=True)


async def send_status(websocket, status):
    """
    Envoie un message de type "status" pour indiquer l'état du client.
    """
    message = json.dumps({"type": "status", "status": status})
    await websocket.send(message)


async def send_text(websocket, text):
    """
    Envoie un message de type "speech" contenant le texte saisi.
    """
    message = json.dumps({
        "type": "speech",
        "text": text,
        "from": str(websocket.remote_address)
    })
    print("Message envoyé")
    print(message)
    await websocket.send(message)


async def send_inactive_delay(websocket):
    """
    Attend un court délai puis met le statut du client à "inactive".
    """
    await asyncio.sleep(0.1)
    await send_status(websocket, "inactive")

async def send_authentication(websocket, token):
    """Envoie le message d'authentification avec le token JWT."""
    auth_message = json.dumps({"type": "auth", "token": token})
    await websocket.send(auth_message)


def input_thread(websocket, loop):
    """
    Fonction exécutée dans un thread séparé pour la saisie utilisateur.
    Pour chaque message saisi, on programme dans la loop les coroutines correspondantes.
    """
    while True:
        try:
            text = input("Enter your message: ").strip()
        except EOFError:
            break

        if text == "":
            continue  # Ignorer les saisies vides

        # Planifier l'envoi des messages dans la boucle asynchrone via run_coroutine_threadsafe
        asyncio.run_coroutine_threadsafe(send_status(websocket, "active"), loop)
        asyncio.run_coroutine_threadsafe(send_text(websocket, text), loop)
        asyncio.run_coroutine_threadsafe(send_inactive_delay(websocket), loop)


async def start_client():
    """
    Se connecte au serveur et démarre les tâches d'affichage des messages reçus
    et de saisie utilisateur via un thread.
    """
    websocket_url = "wss://172.20.10.2:8765"  # Vérifiez que l'URL et le port sont corrects
    async with websockets.connect(websocket_url, ssl=ssl_context) as websocket:
        print("WebSocket connection established.")

        # Générer et envoyer le token JWT (exemple avec user_id=1)
        token = generate_token(user_id)
        await send_authentication(websocket, token)

        # Obtenir la boucle asynchrone en cours
        loop = asyncio.get_running_loop()
        # Démarrer le thread pour la saisie utilisateur
        thread = threading.Thread(target=input_thread, args=(websocket, loop), daemon=True)
        thread.start()

        try:
            await handle_messages(websocket)
        except websockets.ConnectionClosed as e:
            print(f"Connection closed: {e}")


if __name__ == "__main__":
    asyncio.run(start_client())
