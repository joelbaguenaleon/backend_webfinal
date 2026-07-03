from pickletools import read_stringnl_noescape_pair
import pandas as pd
from nba_api.stats.endpoints import leaguedashplayerstats

def obtener_stats(season="2025-26"): #funcion para obtener los datos de los playoffs
    data = leaguedashplayerstats.LeagueDashPlayerStats(
        season=season,
        season_type_all_star="Playoffs",
        measure_type_detailed_defense="Advanced",
        per_mode_detailed="PerGame"
    )
    advanced = pd.DataFrame(data.get_data_frames()[0]) #dataframe donde guardar los datos de avanzadas

    advanced_columns = [
         "PLAYER_ID", "OFF_RATING", "DEF_RATING", "NET_RATING",
         "TS_PCT", "USG_PCT"
        ]
    #filtrar datos
    advanced = advanced[advanced_columns]
   
    basic = leaguedashplayerstats.LeagueDashPlayerStats(
        season=season,
        season_type_all_star="Playoffs",
        per_mode_detailed="PerGame",
        measure_type_detailed_defense="Base"
    )
    basic = pd.DataFrame(basic.get_data_frames()[0]) #datadrae para guardar estaditicas basicas

    basic_columns = [
        "PLAYER_ID", "PLAYER_NAME", "TEAM_ABBREVIATION", "GP", "MIN", "PTS", "REB", "AST",
        "STL", "BLK", "FG_PCT", "FG3_PCT", "FT_PCT"
    ]
    basic= basic[basic_columns]

    df = pd.merge( #combinar llamadas
        basic,
        advanced,
        on="PLAYER_ID",
        how="inner"
    )
    porcentajes = [ #pasar a porcentaje
            "FG_PCT",
            "FG3_PCT",
            "FT_PCT",
            "TS_PCT",
            "USG_PCT"
    ]
    for col in porcentajes:
            df[col] = (df[col] * 100).round(2)
    return df

def obtener_equipos(season="2025-26"): #obtener equipo
    df = obtener_stats(season)

    equipos = df[["TEAM_ABBREVIATION"]].drop_duplicates()
    equipos = equipos.sort_values(by="TEAM_ABBREVIATION")

    return equipos

def obtener_jugadores_por_equipo(equipo, season="2025-26"): #obtener jugadores
    df = obtener_stats(season)

    jugadores = df[df["TEAM_ABBREVIATION"] == equipo]

    jugadores = jugadores[
        [
            "PLAYER_ID",
            "PLAYER_NAME",
            "TEAM_ABBREVIATION"
        ]
    ]
    jugadores = jugadores.sort_values(by="PLAYER_NAME")

    return jugadores

def comparar_jugadores(jugador1_id, jugador2_id, season="2025-26"): #comparar 2 jugadores

    df = obtener_stats(season)

    jugador1 = df[df["Jugador_ID"] == jugador1_id]

    jugador2 = df[df["Jugador_ID"] == jugador2_id]

    return {
        "jugador1": jugador1.to_dict(orient="records")[0],
        "jugador2": jugador2.to_dict(orient="records")[0]
    }

