import discord
from fastapi import FastAPI, Request
import uvicorn
import asyncio
from uvicorn import Config, Server
from dotenv import load_dotenv
import os
from fastapi.responses import JSONResponse

load_dotenv()

# Configuración del bot de Discord
TOKEN_DISCORD = os.getenv("BOT_KEY")  # Asegúrate de usar tu token aquí
CHANNEL_ID = int(os.getenv("CHANNEL"))  # ID del canal de Discord donde se enviarán los mensajes

# Crear los Intents necesarios (especificando los eventos que deseas recibir)
intents = discord.Intents.default()
intents.messages = True  # Permitir recibir mensajes

# Crear el cliente de Discord con los Intents
client = discord.Client(intents=intents)

# Crear la aplicación FastAPI
app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Servicio activo y funcionando correctamente"}

@app.head("/")
async def head_root():
    return JSONResponse(content={}, status_code=200)

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
    await client.wait_until_ready()  # Asegurarse de que el bot esté conectado
    channel = client.get_channel(CHANNEL_ID)
    if channel:
        await channel.send(message)
    else:
        print(f"Error: No se encontró el canal con ID {CHANNEL_ID}")

# Iniciar el bot de Discord
@client.event
async def on_ready():
    print(f'Bot conectado como {client.user}')

# Bucle asincrónico para tareas repetitivas
async def keep_alive():
    while True:
        print("Bot sigue conectado")
        await asyncio.sleep(60)  # Espera 60 segundos de forma no bloqueante

# Ejecutar FastAPI y Discord al mismo tiempo
async def start():
    # Render asigna automáticamente el puerto a través de la variable de entorno PORT
    port = int(os.getenv("PORT", 8000))  # Por defecto, usa 8000 en local si PORT no está definido
    config = Config(app, host="0.0.0.0", port=port)  # Escucha en todas las interfaces
    server = Server(config)

    # Crear tareas para FastAPI, Discord y el bucle de keep_alive
    server_task = asyncio.create_task(server.serve())
    discord_task = asyncio.create_task(client.start(TOKEN_DISCORD))
    keep_alive_task = asyncio.create_task(keep_alive())

    # Ejecutar todas las tareas
    await asyncio.gather(server_task, discord_task, keep_alive_task)

if __name__ == "__main__":
    asyncio.run(start())
