import discord
from fastapi import FastAPI, Request
import uvicorn
import asyncio
from uvicorn import Config, Server
from dotenv import load_dotenv
import os

load_dotenv()
# Configuración del bot de Discord
TOKEN_DISCORD = os.getenv("BOT_KEY")  # Asegúrate de usar tu token aquí
CHANNEL_ID = os.getenv("CHANNEL")  # ID del canal de Discord donde se enviarán los mensajes

# Crear los Intents necesarios (especificando los eventos que deseas recibir)
intents = discord.Intents.default()
intents.messages = True  # Permitir recibir mensajes

# Crear el cliente de Discord con los Intents
client = discord.Client(intents=intents)

# Crear la aplicación FastAPI
app = FastAPI()


@app.post("/webhook")
async def github_webhook(request: Request):
    payload = await request.json()

    if "commits" in payload:
        for commit in payload["commits"]:
            commit_message = commit["message"]
            author_name = commit["author"]["name"]

            # Crear el mensaje que quieres enviar al canal de Discord
            discord_message = f"Nuevo commit por {author_name}: {commit_message}"
            print(discord_message)
            # Enviar el mensaje a Discord
            await send_message_to_discord(discord_message)

    return {"status": "ok"}


# Función para enviar un mensaje a Discord
async def send_message_to_discord(message: str):
    channel = client.get_channel(CHANNEL_ID)
    if channel:
        await channel.send(message)


# Iniciar el bot de Discord
@client.event
async def on_ready():
    print(f'Bot conectado como {client.user}')


# Ejecutar FastAPI y Discord al mismo tiempo
async def start():
    # Configurar el servidor de uvicorn
    port = int(os.getenv("PORT", 8000))
    config = Config(app, host="0.0.0.0", port=port)
    server = Server(config)

    # Ejecutar FastAPI
    loop = asyncio.get_event_loop()

    # Iniciar el servidor de FastAPI
    server_task = loop.create_task(server.serve())

    # Ejecutar el bot de Discord
    await client.start(TOKEN_DISCORD)  # Iniciar el bot de discord

    # Esperar a que ambos servidores terminen (aunque nunca deberían terminar)
    await server_task


if __name__ == "__main__":
    asyncio.run(start())