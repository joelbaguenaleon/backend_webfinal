from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from .motor import procesar_pregunta

router = APIRouter()

class PreguntaRequest(BaseModel):
    texto: str

@router.post("/preguntar")
def preguntar(data: PreguntaRequest):
    texto = data.texto.strip()

    if not texto:
        raise HTTPException(status_code=400, detail="La pregunta no puede estar vacía")

    respuesta = procesar_pregunta(texto)

    return {
        "ok": True,
        "pregunta": texto,
        "respuesta": respuesta
    }
