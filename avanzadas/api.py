from fastapi import APIRouter
from . import avanzadas_playoffs as playoffs
from . import avanzadas_regular as regular

router = APIRouter()


def seleccionar_modulo(season_type: str):
    if season_type == "Regular Season":
        return regular
    return playoffs


@router.get("/teams")
def teams(season: str = "2025-26", season_type: str = "Playoffs"):
    modulo = seleccionar_modulo(season_type)
    df = modulo.obtener_equipos(season)
    return df.to_dict(orient="records")


@router.get("/players")
def players(equipo: str, season: str = "2025-26", season_type: str = "Playoffs"):
    modulo = seleccionar_modulo(season_type)
    df = modulo.obtener_jugadores_por_equipo(equipo, season)
    return df.to_dict(orient="records")


@router.get("/player/stats")
def player_stats(player_id: int, season: str = "2025-26", season_type: str = "Playoffs"):
    modulo = seleccionar_modulo(season_type)
    df = modulo.obtener_stats(season)
    jugador = df[df["PLAYER_ID"] == player_id]
    return jugador.to_dict(orient="records")[0]


@router.get("/players/advanced")
def players_advanced(season: str = "2025-26", season_type: str = "Playoffs"):
    modulo = seleccionar_modulo(season_type)
    df = modulo.obtener_stats(season)
    return df.to_dict(orient="records")


@router.get("/compare/players")
def compare_players(jugador1_id: int, jugador2_id: int, season: str = "2025-26", season_type: str = "Playoffs"):
    modulo = seleccionar_modulo(season_type)
    return modulo.comparar_jugadores(jugador1_id, jugador2_id, season)