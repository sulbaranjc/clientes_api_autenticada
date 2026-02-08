# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import clientes, auth

app = FastAPI(
    title="API de Clientes",
    version="1.0.0"
)

# CORS (pensando en React)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # en producción se ajusta
    allow_credentials=False,  # False para permitir * en origins
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(clientes.router)
app.include_router(auth.router)


@app.get("/")
def root():
    return {
        "mensaje": "API de Clientes con autenticación JWT activa 🚀 by JC"
    }
