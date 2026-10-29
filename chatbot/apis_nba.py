import time
import logging
from functools import wraps
from nba_api.stats.endpoints import (
    ScoreboardV2, TeamGameLog, PlayerCareerStats, LeagueStandings,
    CommonTeamRoster, CommonPlayerInfo,
)
from nba_api.stats.static import teams, players
from datetime import datetime
from zoneinfo import ZoneInfo

log = logging.getLogger(__name__)

TEMPORADA_ACTUAL = "2026-27"
TIMEOUT_API = 15  # segundos


def cache_ttl(segundos):
    """Cachea en memoria el resultado de una funcion durante `segundos`.
    No cachea resultados vacios/None (para no 'congelar' un fallo)."""
    def decorador(func):
        almacen = {}

        @wraps(func)
        def envoltura(*args):
            ahora = time.time()
            if args in almacen:
                valor, caduca = almacen[args]
                if ahora < caduca:
                    return valor
            valor = func(*args)
            if valor:
                almacen[args] = (valor, ahora + segundos)
            return valor
        return envoltura
    return decorador

def convertir_a_hora_espanola(texto_hora):  ##hora de españa
    try:
        texto_hora = texto_hora.strip().replace(" ET", "").replace("ET", "").strip()

        dt = datetime.strptime(texto_hora, "%I:%M %p")
        dt = dt.replace(
            year=datetime.now().year,
            month=datetime.now().month,
            day=datetime.now().day,
            tzinfo=ZoneInfo("America/New_York")
        )

        dt_es = dt.astimezone(ZoneInfo("Europe/Madrid"))
        return dt_es.strftime("%H:%M")
    except Exception:
        return texto_hora

def obtener_team_id_por_abreviatura(abreviatura):
    lista_equipos = teams.get_teams()

    for equipo in lista_equipos:
        if equipo["abbreviation"].lower() == abreviatura.lower():
            return equipo["id"]

    return None


def obtener_nombre_equipo_por_id(team_id):
    lista_equipos = teams.get_teams()

    for equipo in lista_equipos:
        if equipo["id"] == team_id:
            return equipo["full_name"]   
    return "Equipo desconocido"

##partidos del dia de hoy
@cache_ttl(60)
def obtener_partidos_hoy():
    fecha_hoy = datetime.now().strftime("%Y-%m-%d")
    marcador = ScoreboardV2(game_date=fecha_hoy, timeout=TIMEOUT_API)
    partidos = marcador.get_data_frames()[0]
    resultados = []

    for _, fila in partidos.iterrows():
        local = obtener_nombre_equipo_por_id(fila["HOME_TEAM_ID"])
        visitante = obtener_nombre_equipo_por_id(fila["VISITOR_TEAM_ID"])
        estado = str(fila["GAME_STATUS_TEXT"]).strip()

        hora_es = estado
        if "ET" in estado:
            hora_es = convertir_a_hora_espanola(estado)

        resultados.append({
            "game_id": fila["GAME_ID"],
            "local": local,
            "visitante": visitante,
            "hora": hora_es,
            "estado": estado
        })

    return resultados
##patidos de un equipo
@cache_ttl(300)
def obtener_ultimos_partidos_equipo(abreviatura, temporada=TEMPORADA_ACTUAL):
    team_id = obtener_team_id_por_abreviatura(abreviatura)

    if not team_id:
        return []

    logs = TeamGameLog(team_id=team_id, season=temporada, timeout=TIMEOUT_API)
    df = logs.get_data_frames()[0]

    resultados = []

    for _, fila in df.head(5).iterrows():
        resultados.append({
            "fecha": fila["GAME_DATE"],
            "matchup": fila["MATCHUP"],
            "resultado": fila["WL"],
            "puntos": fila["PTS"]
        })

    return resultados

#estadisticas de un jugador
def obtener_player_id_por_nombre(nombre_jugador):
    lista_jugadores = players.get_players()

    for jugador in lista_jugadores:
        nombre_completo = jugador["full_name"].lower()
        if nombre_jugador.lower() in nombre_completo:
            return jugador["id"], jugador["full_name"]

    return None, None


@cache_ttl(1800)
def obtener_estadisticas_jugador(nombre_jugador, temporada=TEMPORADA_ACTUAL):
    player_id, nombre_real = obtener_player_id_por_nombre(nombre_jugador)

    if not player_id:
        return None

    carrera = PlayerCareerStats(player_id=player_id, timeout=TIMEOUT_API)
    df = carrera.get_data_frames()[0]

    temporada_df = df[df["SEASON_ID"] == temporada]

    if temporada_df.empty:
        return None

    fila = temporada_df.iloc[0]

    partidos = int(fila["GP"])
    minutos = float(fila["MIN"])
    puntos = float(fila["PTS"])
    rebotes = float(fila["REB"])
    asistencias = float(fila["AST"])
    robos = float(fila["STL"])
    tapones = float(fila["BLK"])

    return {
        "jugador": nombre_real,
        "temporada": temporada,
        "partidos": partidos,
        "minutos_por_partido": round(minutos / partidos, 1) if partidos > 0 else 0,
        "puntos_por_partido": round(puntos / partidos, 1) if partidos > 0 else 0,
        "rebotes_por_partido": round(rebotes / partidos, 1) if partidos > 0 else 0,
        "asistencias_por_partido": round(asistencias / partidos, 1) if partidos > 0 else 0,
        "robos_por_partido": round(robos / partidos, 1) if partidos > 0 else 0,
        "tapones_por_partido": round(tapones / partidos, 1) if partidos > 0 else 0
    }

#clasificacion de la liga
@cache_ttl(600)
def obtener_clasificacion_liga():
    standings = LeagueStandings(timeout=TIMEOUT_API)
    df = standings.get_data_frames()[0]

    resultados = []

    for _, fila in df.iterrows():
        resultados.append({
            "equipo": fila["TeamName"],
            "conferencia": fila["Conference"],
            "victorias": int(fila["WINS"]),
            "derrotas": int(fila["LOSSES"]),
            "pct": fila["WinPCT"]
        })

    return resultados



# ======================================================================
# Sustitutos de consultas.py (antes SQLite). Mismas firmas y formatos.
# ======================================================================

def cargar_equipos():
    """[(nombre, abreviatura)] - datos estaticos del paquete, sin red."""
    return [(e["full_name"], e["abbreviation"]) for e in teams.get_teams()]


def cargar_jugadores():
    """[nombre] de jugadores activos - datos estaticos del paquete, sin red."""
    return [j["full_name"] for j in players.get_players() if j["is_active"]]


def _equipo_por_nombre(nombre_equipo):
    for e in teams.get_teams():
        if e["full_name"].lower() == nombre_equipo.lower():
            return e
    return None


def _jugador_por_nombre_exacto(nombre_jugador):
    for j in players.get_players():
        if j["full_name"].lower() == nombre_jugador.lower() and j["is_active"]:
            return j
    return None


@cache_ttl(3600)
def obtener_jugadores_equipo(nombre_equipo):
    """[(nombre, posicion, dorsal)] ordenado por nombre."""
    equipo = _equipo_por_nombre(nombre_equipo)
    if not equipo:
        return []
    try:
        df = CommonTeamRoster(
            team_id=equipo["id"], season=TEMPORADA_ACTUAL, timeout=TIMEOUT_API
        ).get_data_frames()[0]
    except Exception:
        log.exception("Fallo CommonTeamRoster")
        return []
    datos = [(f["PLAYER"], f["POSITION"], f["NUM"]) for _, f in df.iterrows()]
    return sorted(datos, key=lambda t: t[0])


@cache_ttl(3600)
def _info_jugador_api(nombre_jugador):
    """Fila de CommonPlayerInfo como dict, o None."""
    jugador = _jugador_por_nombre_exacto(nombre_jugador)
    if not jugador:
        return None
    try:
        df = CommonPlayerInfo(
            player_id=jugador["id"], timeout=TIMEOUT_API
        ).get_data_frames()[0]
    except Exception:
        log.exception("Fallo CommonPlayerInfo")
        return None
    if df.empty:
        return None
    fila = df.iloc[0]
    team_id = int(fila["TEAM_ID"]) if fila["TEAM_ID"] else 0
    return {
        "nombre": fila["DISPLAY_FIRST_LAST"],
        "posicion": fila["POSITION"],
        "dorsal": fila["JERSEY"],
        "equipo": obtener_nombre_equipo_por_id(team_id) if team_id else "Sin equipo",
    }


def obtener_equipo_jugador(nombre_jugador):
    """(nombre, equipo) o None."""
    info = _info_jugador_api(nombre_jugador)
    if info:
        return info["nombre"], info["equipo"]
    return None


def obtener_info_jugador(nombre_jugador):
    """(nombre, posicion, dorsal, equipo) o None."""
    info = _info_jugador_api(nombre_jugador)
    if info:
        return info["nombre"], info["posicion"], info["dorsal"], info["equipo"]
    return None


@cache_ttl(86400)
def _conferencia_division():
    """{team_id: (conferencia, division)} desde la clasificacion."""
    try:
        df = LeagueStandings(timeout=TIMEOUT_API).get_data_frames()[0]
    except Exception:
        log.exception("Fallo LeagueStandings")
        return {}
    return {int(f["TeamID"]): (f["Conference"], f["Division"]) for _, f in df.iterrows()}


def obtener_info_equipo(nombre_equipo):
    """(nombre, ciudad, conferencia, division, abreviatura) o None."""
    equipo = _equipo_por_nombre(nombre_equipo)
    if not equipo:
        return None
    conferencia, division = _conferencia_division().get(equipo["id"], (None, None))
    return (equipo["full_name"], equipo["city"], conferencia, division, equipo["abbreviation"])