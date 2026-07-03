from .alias import obtener_alias_equipos  
##logica del chat para entender mensajes##
def detectar_equipo(pregunta, equipos):
    texto = pregunta.lower().strip()
    alias_equipos = obtener_alias_equipos()

    for alias in sorted(alias_equipos.keys(), key=len, reverse=True):
        if alias in texto:
            return alias_equipos[alias]

    for nombre, abreviatura in equipos:
        if nombre.lower() in texto or abreviatura.lower() in texto:
            return nombre

    return None


def detectar_jugador(pregunta, jugadores):
    texto = pregunta.lower().strip()

    for jugador in jugadores:
        if jugador.lower() in texto:
            return jugador

    coincidencias = []

    for jugador in jugadores:
        partes = jugador.lower().split()
        for parte in partes:
            if len(parte) > 2 and parte in texto:
                coincidencias.append(jugador)
                break

    if len(coincidencias) == 1:
        return coincidencias[0]

    return None


def detectar_intencion(texto, equipo_detectado, jugador_detectado):
    if equipo_detectado and ("jugadores" in texto or "plantilla" in texto):
        return "jugadores_equipo"

    elif jugador_detectado and ("equipo" in texto or "juega" in texto):
        return "equipo_jugador"

    elif equipo_detectado and (
        "información" in texto or
        "informacion" in texto or
        "info" in texto
    ):
        return "info_equipo"

    elif "partidos de hoy" in texto or "que partidos hay hoy" in texto or "quien juega hoy" in texto:
        return "partidos_hoy"

    elif equipo_detectado and ("últimos partidos" in texto or "ultimos partidos" in texto or "ultimos" in texto):
        return "ultimos_partidos_equipo"

    elif jugador_detectado and (
        "posición" in texto or
        "posicion" in texto or
        "dorsal" in texto or
        "info" in texto
    ):
        return "info_jugador"

    elif jugador_detectado and (
        "estadisticas" in texto or
        "estadísticas" in texto or
        "temporada" in texto
    ):
        return "estadisticas_jugador"

    elif (
        "clasificacion" in texto or
        "clasificación" in texto or
        "tabla" in texto or
        "posiciones" in texto
    ):
        return "clasificacion"

    return "desconocida"
