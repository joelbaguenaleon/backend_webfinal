from .consultas import (
    obtener_jugadores_equipo,
    obtener_equipo_jugador,
    obtener_info_jugador,
    obtener_info_equipo,
)

from .alias import (
    traducir_posicion,
    traducir_conferencia,
    traducir_division,
    normalizar_abreviatura_equipo,
)

from .apis_nba import (
    obtener_partidos_hoy,
    obtener_ultimos_partidos_equipo,
    obtener_estadisticas_jugador,
    obtener_clasificacion_liga,
)


def responder_jugadores_equipo(equipo):
    datos = obtener_jugadores_equipo(equipo)

    if not datos:
        return "No encontré jugadores para ese equipo."

    respuesta = f"Jugadores de {equipo}:\n\n"

    for nombre, posicion, dorsal in datos:
        respuesta += f"- {nombre} ({traducir_posicion(posicion)}, dorsal {dorsal})\n"

    return respuesta


def responder_equipo_jugador(pregunta, jugador):
    dato = obtener_equipo_jugador(jugador)

    if not dato:
        return "No encontré ese jugador."

    nombre, equipo = dato
    return f"{nombre} juega en {equipo}."


def responder_info_jugador(pregunta, jugador):
    dato = obtener_info_jugador(jugador)

    if not dato:
        return "No encontré información de ese jugador."

    nombre, posicion, dorsal, equipo = dato

    return (
        f"{nombre} juega en {equipo}, "
        f"su posición es {traducir_posicion(posicion)} "
        f"y lleva el dorsal {dorsal}."
    )


def responder_info_equipo(pregunta, equipo):
    dato = obtener_info_equipo(equipo)

    if not dato:
        return "No encontré ese equipo."

    nombre, ciudad, conferencia, division, abreviatura = dato

    return (
        f"{nombre} ({abreviatura}) es un equipo de {ciudad}, "
        f"pertenece a la conferencia {traducir_conferencia(conferencia)}, "
        f"división {traducir_division(division)}."
    )


def responder_partidos_hoy(pregunta):
    datos = obtener_partidos_hoy()

    if not datos:
        return "No encontré partidos para hoy."

    respuesta = f"Hoy hay {len(datos)} partidos NBA:\n\n"

    for i, partido in enumerate(datos, 1):
        hora = partido.get("hora_es", partido.get("hora", partido.get("estado", "Sin hora")))
        respuesta += f"{i}. {partido['visitante']} vs {partido['local']} | {hora}\n"

    return respuesta


def responder_ultimos_partidos_equipo(pregunta, equipo):
    abreviatura = normalizar_abreviatura_equipo(equipo)
    datos = obtener_ultimos_partidos_equipo(abreviatura)

    if not datos:
        return "No encontré últimos partidos para ese equipo."

    respuesta = f"Últimos partidos de {equipo}:\n\n"

    for partido in datos:
        respuesta += (
            f"- {partido['fecha']} | "
            f"{partido['matchup']} | "
            f"{partido['resultado']}\n"
        )

    return respuesta


def responder_estadisticas_jugador(pregunta, jugador):
    datos = obtener_estadisticas_jugador(jugador)

    if not datos:
        return "No encontré estadísticas de ese jugador en esta temporada."

    return (
        f"Estadísticas de {datos['jugador']} en la temporada {datos['temporada']}:\n\n"
        f"- Partidos: {datos['partidos']}\n"
        f"- Minutos por partido: {datos['minutos_por_partido']}\n"
        f"- Puntos por partido: {datos['puntos_por_partido']}\n"
        f"- Rebotes por partido: {datos['rebotes_por_partido']}\n"
        f"- Asistencias por partido: {datos['asistencias_por_partido']}\n"
        f"- Robos por partido: {datos['robos_por_partido']}\n"
        f"- Tapones por partido: {datos['tapones_por_partido']}"
    )


def responder_clasificacion(pregunta):
    datos = obtener_clasificacion_liga()

    if not datos:
        return "No pude obtener la clasificación de la liga."

    este = [e for e in datos if e["conferencia"] == "East"]
    oeste = [e for e in datos if e["conferencia"] == "West"]

    respuesta = "Clasificación NBA\n\n"

    respuesta += "Conferencia Este:\n"
    for i, equipo in enumerate(este, 1):
        respuesta += f"{i}. {equipo['equipo']} ({equipo['victorias']}-{equipo['derrotas']})\n"

    respuesta += "\nConferencia Oeste:\n"
    for i, equipo in enumerate(oeste, 1):
        respuesta += f"{i}. {equipo['equipo']} ({equipo['victorias']}-{equipo['derrotas']})\n"

    return respuesta


def responder_desconocido(pregunta):
    return (
        "No entendí la pregunta. "
        "Prueba con algo como 'jugadores de Lakers', "
        "'qué dorsal tiene Tatum', 'partidos de hoy', "
        "'estadísticas de Durant' o 'clasificación NBA'."
    )
    

