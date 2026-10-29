from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from chatbot.api import router as chatbot_router
from avanzadas.api import router as stats_router
from clasificacion_service import (
    obtener_clasificacion_cacheada,
    ClasificacionNoDisponible,
)

app = FastAPI(
    title="Backend NBA",
    version="1.0.0"
)


# Permitir peticiones desde Laravel
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Chatbot
app.include_router(
    chatbot_router,
    prefix="/api/chatbot",
    tags=["Chatbot"]
)

# Estadísticas
app.include_router(
    stats_router,
    prefix="/api/stats",
    tags=["Stats"]
)

@app.get("/")
def home():
    return {
        "ok": True,
        "mensaje": "Backend NBA funcionando"
    }

@app.get("/api/stats/clasificacion")
def clasificacion():
    try:
        return obtener_clasificacion_cacheada()
    except ClasificacionNoDisponible:
        raise HTTPException(status_code=503, detail="No se pudo obtener la clasificación")