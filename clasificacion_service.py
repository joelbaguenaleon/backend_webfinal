import time
from nba_api.stats.endpoints import LeagueStandings

_cache = {"datos": None, "ts": 0}
TTL = 600  # 10 minutos


class ClasificacionNoDisponible(Exception):
    pass


def obtener_clasificacion_liga():
    df = LeagueStandings(timeout=60).get_data_frames()[0]
    return [
        {
            "id": int(f["TeamID"]),
            "equipo": f["TeamName"],
            "ciudad": f["TeamCity"],
            "conferencia": f["Conference"],
            "posicion": int(f["PlayoffRank"]),
            "victorias": int(f["WINS"]),
            "derrotas": int(f["LOSSES"]),
            "pct": float(f["WinPCT"]),
            "ultimos10": f["L10"],
            "racha": f["strCurrentStreak"],
        }
        for _, f in df.iterrows()
    ]


def obtener_clasificacion_cacheada():
    ahora = time.time()
    if _cache["datos"] is None or ahora - _cache["ts"] > TTL:
        try:
            _cache["datos"] = obtener_clasificacion_liga()
            _cache["ts"] = ahora
        except Exception:
            if _cache["datos"] is None:
                raise ClasificacionNoDisponible()
            # si falla pero hay caché antigua, se sirve esa
    return _cache["datos"]