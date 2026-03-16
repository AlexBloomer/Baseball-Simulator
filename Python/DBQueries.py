import sqlite3
import pandas as pd

conn = sqlite3.connect("lahman_lab7.sqlite", check_same_thread=False)

DEFAULT_YEAR = 2021

def get_hitters(teamID, year=DEFAULT_YEAR):
    return pd.read_sql_query("""
        SELECT
            b.playerID,
            COALESCE(p.nameFirst,'') || ' ' || COALESCE(p.nameLast,'') AS Player,
            b.teamID AS Team,
            f.POS,
            b.G, b.AB, b.R, b.H, b.H2B, b.H3B, b.HR,
            b.RBI, b.SB, b.CS, b.BB, b.SO, b.IBB,
            b.HBP, b.SH, b.SF, b.GIDP,
            printf('%.3f', CAST(b.H AS FLOAT) / NULLIF(b.AB, 0)) AS BA
        FROM Batting b
        JOIN People p ON p.playerID = b.playerID
        JOIN (
            SELECT playerID, yearID, teamID, POS, MAX(G) AS maxG
            FROM Fielding
            GROUP BY playerID, yearID, teamID
        ) f
            ON f.playerID = b.playerID
            AND f.yearID = b.yearID
            AND f.teamID = b.teamID
        WHERE b.teamID = ? AND b.yearID = ? AND b.AB > 0
        ORDER BY b.G DESC
    """, conn, params=(teamID, year))

def get_pitchers(teamID, year=DEFAULT_YEAR):
    return pd.read_sql_query("""
        SELECT
            pt.playerID,
            pe.nameFirst || ' ' || pe.nameLast AS Player,
            pt.teamID AS Team,
            pt.lgID,
            pt.W, pt.L, pt.G, pt.GS, pt.GF, pt.CG, pt.SHO, pt.SV,
            pt.IPouts, pt.BFP AS BF, pt.H, pt.R, pt.ER, pt.HR,
            pt.BB, pt.IBB, pt.SO, pt.WP, pt.HBP, pt.BK,
            pt.SH, pt.SF, pt.GIDP, pt.ERA, round(pt.BAOpp,3)
        FROM Pitching pt
        JOIN People pe ON pe.playerID = pt.playerID
        WHERE pt.teamID = ? AND pt.yearID = ? AND pt.BFP > 120
    """, conn, params=(teamID, year))

def get_teams(year=DEFAULT_YEAR):
    return pd.read_sql_query("""
        Select
            t.teamID,
            t.name
            from Teams t join Batting b on b.teamID = t.teamID and b.yearID = t.yearID
            where t.yearID = ? and name is not null
            group by t.teamID, t.name
            having Count(playerID) > 0
    """,conn, params=(year,)).fillna('').to_dict(orient='records')

def get_years():
    return pd.read_sql_query("""
        Select
            distinct yearId
            from Batting
    """,conn)
