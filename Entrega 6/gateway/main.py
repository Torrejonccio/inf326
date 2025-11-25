import httpx
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GATEWAY")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

URL_USERS_BASE = "https://users.inf326.nursoft.dev"
URL_CHANNELS_BASE = "https://channel-api.inf326.nur.dev"

class LoginRequest(BaseModel):
    username_or_email: str
    password: str

class RegisterRequest(BaseModel):
    email: str
    username: str
    password: str

class CreateChannelRequest(BaseModel):
    name: str
    owner_id: str
    channel_type: Optional[str] = "public"

class UpdateChannelRequest(BaseModel):
    name: str
    status: Optional[str] = None

class ChatRequest(BaseModel):
    text: str

@app.post("/proxy/auth/login")
async def login(data: LoginRequest):
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{URL_USERS_BASE}/v1/auth/login", json=data.dict())
        if resp.status_code >= 400: raise HTTPException(status_code=resp.status_code, detail="Error Auth")
        return resp.json()

@app.post("/proxy/auth/register")
async def register(data: RegisterRequest):
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{URL_USERS_BASE}/v1/users/register", json=data.dict())
        if resp.status_code >= 400: raise HTTPException(status_code=resp.status_code, detail="Error Registro")
        return resp.json()


@app.get("/proxy/channels")
async def list_channels():
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f"{URL_CHANNELS_BASE}/v1/channels/", timeout=5)
            if resp.status_code == 200:
                return resp.json()
        except: pass
    return []

@app.get("/proxy/channels/owner/{owner_id}")
async def list_my_channels(owner_id: str):
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f"{URL_CHANNELS_BASE}/v1/members/owner/{owner_id}", timeout=5)
            if resp.status_code == 200:
                return resp.json()
        except: pass
    return []

@app.post("/proxy/channels")
async def create_channel(data: CreateChannelRequest):
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{URL_CHANNELS_BASE}/v1/channels/", json=data.dict())
        if resp.status_code >= 400: raise HTTPException(status_code=resp.status_code, detail=resp.text)
        return resp.json()

@app.get("/proxy/channels/{channel_id}")
async def get_channel_details(channel_id: str):
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{URL_CHANNELS_BASE}/v1/channels/{channel_id}")
        return resp.json() if resp.status_code == 200 else {}

@app.put("/proxy/channels/{channel_id}")
async def update_channel(channel_id: str, data: UpdateChannelRequest):
    async with httpx.AsyncClient() as client:
        resp = await client.put(f"{URL_CHANNELS_BASE}/v1/channels/{channel_id}", json=data.dict())
        if resp.status_code >= 400: raise HTTPException(status_code=resp.status_code, detail="Error update")
        return resp.json()

@app.delete("/proxy/channels/{channel_id}")
async def delete_channel(channel_id: str):
    async with httpx.AsyncClient() as client:
        resp = await client.delete(f"{URL_CHANNELS_BASE}/v1/channels/{channel_id}")
        if resp.status_code >= 400: raise HTTPException(status_code=resp.status_code, detail="Error delete")
        return {"status": "deleted"}

@app.post("/proxy/channels/{channel_id}/reactivate")
async def reactivate_channel(channel_id: str):
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{URL_CHANNELS_BASE}/v1/channels/{channel_id}/reactivate")
        return resp.json()

@app.post("/api/chat")
async def chat(msg: ChatRequest):
    text = msg.text.lower()
    bot_resp = "No entiendo. Prueba 'hola'."
    if "hola" in text: bot_resp = "¡Hola! Soy el Chatbot Académico G9."
    elif "fecha" in text: bot_resp = "El certamen es el 25 de Noviembre."
    return {"content": bot_resp, "author": "Bot G9"}