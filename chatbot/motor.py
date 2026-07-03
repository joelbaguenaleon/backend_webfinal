from .consultas import cargar_equipos, cargar_jugadores
from .interacciones_basicas import detectar_interaccion_basica
from .intenciones import (
    detectar_equipo,
    detectar_jugador,
    detectar_intencion
)
from .respuestas import (
    responder_jugadores_equipo,
    responder_equipo_jugador,
    responder_info_jugador,
    responder_info_equipo,
    responder_partidos_hoy,
    responder_ultimos_partidos_equipo,
    responder_estadisticas_jugador,
    responder_clasificacion,
    responder_desconocido
)

equipos_cache = cargar_equipos()
jugadores_cache = cargar_jugadores()


def procesar_pregunta(pregunta: str) -> str:
    respuesta_basica = detectar_interaccion_basica(pregunta)

    if respuesta_basica:
        return respuesta_basica

    texto = pregunta.lower().strip()

    equipo = detectar_equipo(texto, equipos_cache)
    jugador = detectar_jugador(texto, jugadores_cache)
    intencion = detectar_intencion(texto, equipo, jugador)

    if intencion == "jugadores_equipo":
        return responder_jugadores_equipo(equipo)

    if intencion == "equipo_jugador":
        return responder_equipo_jugador(pregunta, jugador)

    if intencion == "info_jugador":
        return responder_info_jugador(pregunta, jugador)

    if intencion == "info_equipo":
        return responder_info_equipo(pregunta, equipo)

    if intencion == "partidos_hoy":
        return responder_partidos_hoy(pregunta)

    if intencion == "ultimos_partidos_equipo":
        return responder_ultimos_partidos_equipo(pregunta, equipo)

    if intencion == "estadisticas_jugador":
        return responder_estadisticas_jugador(pregunta, jugador)

    if intencion == "clasificacion":
        return responder_clasificacion(pregunta)

    return responder_desconocido(pregunta)
