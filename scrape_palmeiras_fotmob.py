# -*- coding: utf-8 -*-
"""Coleta estatisticas Opta (FotMob) dos ultimos 5 jogos do Palmeiras no Brasileirao."""
from __future__ import annotations

import time
from pathlib import Path

import pandas as pd
import requests

PALMEIRAS_TEAM_ID = 10283

MATCHES = [
    {
        "id": 5103572,
        "data": "2026-07-29",
        "adversario": "Vitória",
        "local": "Fora",
        "resultado": "4-0",
        "nivel": 3,
    },
    {
        "id": 5103577,
        "data": "2026-08-09",
        "adversario": "Internacional",
        "local": "Casa",
        "resultado": "0-0",
        "nivel": 2,
    },
    {
        "id": 5103584,
        "data": "2026-08-15",
        "adversario": "Fluminense",
        "local": "Fora",
        "resultado": "2-3",
        "nivel": 5,
    },
    {
        "id": 5103597,
        "data": "2026-08-23",
        "adversario": "Vasco da Gama",
        "local": "Casa",
        "resultado": "4-1",
        "nivel": 2,
    },
    {
        "id": 5103608,
        "data": "2026-08-30",
        "adversario": "Mirassol",
        "local": "Fora",
        "resultado": "1-1",
        "nivel": 2,
    },
]

COLUNAS_DADOS_BRUTOS = [
    "Jogador",
    "Posição",
    "Nível do jogo",
    "Minutos jogados",
    "Golos",
    "xG",
    "Assistências",
    "xA",
    "Remates",
    "Remates no alvo",
    "Passes",
    "Passes certos",
    "Cruzamentos",
    "Cruzamentos certos",
    "Dribles",
    "Dribles certos",
    "Duelos",
    "Duelos certos",
    "Perdas (total)",
    "Recuperações (total)",
    "Toques na área",
    "Cartões amarelos",
    "Cartões vermelhos",
    "Duelos defensivos",
    "Duelos ofensivos",
    "Duelos aéreos",
    "Remates bloqueados",
    "Interceções",
    "Alívios (Clearances)",
    "Faltas cometidas",
    "Faltas sofridas",
    "Passes decisivos",
    "Segunda assistência",
    "Terceira assistência",
    "Shot assists",
]

POSICAO_POR_JOGADOR = {
    "Carlos Miguel": "Goleiro",
    "Marcelo Lomba": "Goleiro",
    "Gustavo Gómez": "Zagueiro",
    "Murilo Cerqueira": "Zagueiro",
    "Murilo": "Zagueiro",
    "Alexander Barboza": "Zagueiro",
    "Bruno Fuchs": "Zagueiro",
    "Luis Benedetti": "Zagueiro",
    "Agustín Giay": "Lateral Direito",
    "Khellven": "Lateral Direito",
    "Joaquín Piquerez": "Lateral Esquerdo",
    "Arthur": "Lateral Esquerdo",
    "Jefté": "Lateral Esquerdo",
    "Marlon Freitas": "Volante",
    "Emiliano Martínez": "Volante",
    "Lucas Evangelista": "Volante",
    "Andreas Pereira": "Meia",
    "Mauricio": "Meia",
    "Allan": "Meia",
    "Luis Pacheco": "Meia",
    "Larson": "Meia",
    "Jhon Arias": "Extremo",
    "Felipe Anderson": "Extremo",
    "Ramón Sosa": "Extremo",
    "Flaco López": "Centroavante",
    "José Manuel López": "Centroavante",
    "Vitor Roque": "Centroavante",
    "Paulinho": "Centroavante",
    "Luighi": "Centroavante",
    "Heittor Vinicius": "Centroavante",
    "Heittor": "Centroavante",
    "Riquelme Fillipi": "Extremo",
}

USUAL_POS = {0: "Goleiro", 1: "Zagueiro", 2: "Meia", 3: "Centroavante"}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Accept": "application/json",
}


def fetch_match(match_id: int) -> dict:
    url = f"https://www.fotmob.com/api/data/matchDetails?matchId={match_id}"
    r = requests.get(url, headers=HEADERS, timeout=40)
    r.raise_for_status()
    return r.json()


def flatten_stats(player: dict) -> dict:
    out = {}
    for grp in player.get("stats") or []:
        for _label, obj in (grp.get("stats") or {}).items():
            key = obj.get("key") or _label
            out[key] = obj.get("stat") or {}
    return out


def val(flat: dict, key: str, default: float | int = 0):
    st = flat.get(key) or {}
    if "value" not in st or st.get("value") is None:
        return default
    n = st["value"]
    if isinstance(n, float) and n.is_integer():
        return int(n)
    return n


def frac(flat: dict, key: str) -> tuple[int, int]:
    st = flat.get(key) or {}
    won = st.get("value")
    total = st.get("total")
    won_n = 0 if won is None else int(won)
    if total is None:
        total_n = won_n
    else:
        total_n = int(total)
    return won_n, total_n


def mapear_posicao(nome: str, usual: int | None) -> str:
    if nome in POSICAO_POR_JOGADOR:
        return POSICAO_POR_JOGADOR[nome]
    for chave, pos in POSICAO_POR_JOGADOR.items():
        if chave.lower() in nome.lower() or nome.lower() in chave.lower():
            return pos
    if nome.startswith("José Manuel") or "López" in nome:
        return "Centroavante"
    return USUAL_POS.get(usual if usual is not None else -1, "Meia")


def cartoes_do_jogo(md: dict, player_id: int) -> tuple[int, int]:
    amarelos = 0
    vermelhos = 0
    eventos = (((md.get("content") or {}).get("matchFacts") or {}).get("events") or {}).get("events") or []
    for e in eventos:
        if e.get("type") != "Card" or e.get("playerId") != player_id:
            continue
        tipo = (e.get("card") or "").lower()
        if tipo == "yellow":
            amarelos += 1
        elif tipo == "yellowred":
            amarelos += 1
            vermelhos += 1
        elif tipo == "red":
            vermelhos += 1
    return amarelos, vermelhos


def montar_linha(jogo: dict, player: dict, md: dict) -> dict | None:
    flat = flatten_stats(player)
    minutos = val(flat, "minutes_played", 0)
    if not minutos:
        return None

    passes_certos, passes = frac(flat, "accurate_passes")
    cruz_certos, cruzamentos = frac(flat, "accurate_crosses")
    dribles_certos, dribles = frac(flat, "dribbles_succeeded")
    aereos_certos, aereos = frac(flat, "aerials_won")
    solo_certos, solo = frac(flat, "ground_duels_won")

    duelos_certos = val(flat, "duel_won", None)
    duelos_perdidos = val(flat, "duel_lost", None)
    if duelos_certos is None:
        duelos_certos = aereos_certos + solo_certos
    if duelos_perdidos is None:
        duelos_perdidos = max(aereos - aereos_certos, 0) + max(solo - solo_certos, 0)
    duelos = int(duelos_certos) + int(duelos_perdidos)

    perdas = (
        val(flat, "dispossessed", 0)
        + max(passes - passes_certos, 0)
        + max(dribles - dribles_certos, 0)
    )

    amarelos, vermelhos = cartoes_do_jogo(md, int(player["id"]))
    chances = val(flat, "chances_created", 0)

    nome = player["name"]
    return {
        "Data": jogo["data"],
        "Adversário": jogo["adversario"],
        "Local": jogo["local"],
        "Resultado": jogo["resultado"],
        "Jogador": nome,
        "Posição": mapear_posicao(nome, player.get("usualPosition")),
        "Nível do jogo": jogo["nivel"],
        "Minutos jogados": minutos,
        "Golos": val(flat, "goals", 0),
        "xG": round(float(val(flat, "expected_goals", 0) or 0), 2),
        "Assistências": val(flat, "assists", 0),
        "xA": round(float(val(flat, "expected_assists", 0) or 0), 2),
        "Remates": val(flat, "total_shots", 0),
        "Remates no alvo": val(flat, "ShotsOnTarget", 0),
        "Passes": passes,
        "Passes certos": passes_certos,
        "Cruzamentos": cruzamentos,
        "Cruzamentos certos": cruz_certos,
        "Dribles": dribles,
        "Dribles certos": dribles_certos,
        "Duelos": duelos,
        "Duelos certos": int(duelos_certos),
        "Perdas (total)": perdas,
        "Recuperações (total)": val(flat, "recoveries", 0),
        "Toques na área": val(flat, "touches_opp_box", 0),
        "Cartões amarelos": amarelos,
        "Cartões vermelhos": vermelhos,
        "Duelos defensivos": val(flat, "matchstats.headers.tackles", 0),
        "Duelos ofensivos": dribles,
        "Duelos aéreos": aereos,
        "Remates bloqueados": val(flat, "shot_blocks", 0),
        "Interceções": val(flat, "interceptions", 0),
        "Alívios (Clearances)": val(flat, "clearances", 0),
        "Faltas cometidas": val(flat, "fouls", 0),
        "Faltas sofridas": val(flat, "was_fouled", 0),
        "Passes decisivos": chances,
        "Segunda assistência": 0,
        "Terceira assistência": 0,
        "Shot assists": chances,
        "Fonte": "FotMob / Opta",
        "URL": f"https://www.fotmob.com/matches/{jogo['id']}",
    }


def main() -> None:
    linhas = []
    resumo = []
    for i, jogo in enumerate(MATCHES):
        md = fetch_match(jogo["id"])
        players = ((md.get("content") or {}).get("playerStats") or {})
        n = 0
        gols = 0
        for p in players.values():
            if p.get("teamId") != PALMEIRAS_TEAM_ID:
                continue
            row = montar_linha(jogo, p, md)
            if row is None:
                continue
            linhas.append(row)
            n += 1
            gols += row["Golos"]
        resumo.append(
            {
                "Data": jogo["data"],
                "Adversário": jogo["adversario"],
                "Local": jogo["local"],
                "Resultado Palmeiras": jogo["resultado"],
                "Nível do jogo": jogo["nivel"],
                "Jogadores coletados": n,
                "Golos (jogadores)": gols,
                "URL FotMob": f"https://www.fotmob.com/api/data/matchDetails?matchId={jogo['id']}",
            }
        )
        print(f"{jogo['data']} {jogo['adversario']}: {n} jogadores, {gols} gols")
        if i < len(MATCHES) - 1:
            time.sleep(1.2)

    extra = ["Data", "Adversário", "Local", "Resultado", "Fonte", "URL"]
    out = pd.DataFrame(linhas)
    out = out[extra + COLUNAS_DADOS_BRUTOS]
    out = out.sort_values(
        ["Data", "Minutos jogados", "Jogador"], ascending=[True, False, True]
    ).reset_index(drop=True)

    mapa = pd.DataFrame(
        [
            {"Coluna dados_brutos": "Jogador", "Fonte Opta/FotMob": "name"},
            {"Coluna dados_brutos": "Posição", "Fonte Opta/FotMob": "elenco Palmeiras + usualPosition"},
            {"Coluna dados_brutos": "Nível do jogo", "Fonte Opta/FotMob": "escala 1-5 da força do adversário (não vem da Opta)"},
            {"Coluna dados_brutos": "Minutos jogados", "Fonte Opta/FotMob": "minutes_played"},
            {"Coluna dados_brutos": "Golos", "Fonte Opta/FotMob": "goals"},
            {"Coluna dados_brutos": "xG", "Fonte Opta/FotMob": "expected_goals"},
            {"Coluna dados_brutos": "Assistências", "Fonte Opta/FotMob": "assists"},
            {"Coluna dados_brutos": "xA", "Fonte Opta/FotMob": "expected_assists"},
            {"Coluna dados_brutos": "Remates", "Fonte Opta/FotMob": "total_shots"},
            {"Coluna dados_brutos": "Remates no alvo", "Fonte Opta/FotMob": "shots_on_target"},
            {"Coluna dados_brutos": "Passes", "Fonte Opta/FotMob": "accurate_passes.total"},
            {"Coluna dados_brutos": "Passes certos", "Fonte Opta/FotMob": "accurate_passes.value"},
            {"Coluna dados_brutos": "Cruzamentos", "Fonte Opta/FotMob": "accurate_crosses.total"},
            {"Coluna dados_brutos": "Cruzamentos certos", "Fonte Opta/FotMob": "accurate_crosses.value"},
            {"Coluna dados_brutos": "Dribles", "Fonte Opta/FotMob": "dribbles_succeeded.total"},
            {"Coluna dados_brutos": "Dribles certos", "Fonte Opta/FotMob": "dribbles_succeeded.value"},
            {"Coluna dados_brutos": "Duelos", "Fonte Opta/FotMob": "duel_won + duel_lost"},
            {"Coluna dados_brutos": "Duelos certos", "Fonte Opta/FotMob": "duel_won"},
            {"Coluna dados_brutos": "Perdas (total)", "Fonte Opta/FotMob": "dispossessed + passes errados + dribles falhos"},
            {"Coluna dados_brutos": "Recuperações (total)", "Fonte Opta/FotMob": "recoveries"},
            {"Coluna dados_brutos": "Toques na área", "Fonte Opta/FotMob": "touches_opp_box"},
            {"Coluna dados_brutos": "Cartões amarelos", "Fonte Opta/FotMob": "eventos Card Yellow / YellowRed"},
            {"Coluna dados_brutos": "Cartões vermelhos", "Fonte Opta/FotMob": "eventos Card Red / YellowRed"},
            {"Coluna dados_brutos": "Duelos defensivos", "Fonte Opta/FotMob": "tackles (proxy Opta; Wyscout separa duelo defensivo)"},
            {"Coluna dados_brutos": "Duelos ofensivos", "Fonte Opta/FotMob": "dribles tentados (proxy Opta)"},
            {"Coluna dados_brutos": "Duelos aéreos", "Fonte Opta/FotMob": "aerials_won.total"},
            {"Coluna dados_brutos": "Remates bloqueados", "Fonte Opta/FotMob": "shot_blocks"},
            {"Coluna dados_brutos": "Interceções", "Fonte Opta/FotMob": "interceptions"},
            {"Coluna dados_brutos": "Alívios (Clearances)", "Fonte Opta/FotMob": "clearances"},
            {"Coluna dados_brutos": "Faltas cometidas", "Fonte Opta/FotMob": "fouls"},
            {"Coluna dados_brutos": "Faltas sofridas", "Fonte Opta/FotMob": "was_fouled"},
            {"Coluna dados_brutos": "Passes decisivos", "Fonte Opta/FotMob": "chances_created"},
            {"Coluna dados_brutos": "Segunda assistência", "Fonte Opta/FotMob": "não publicado na Opta/FotMob — preenchido com 0"},
            {"Coluna dados_brutos": "Terceira assistência", "Fonte Opta/FotMob": "não publicado na Opta/FotMob — preenchido com 0"},
            {"Coluna dados_brutos": "Shot assists", "Fonte Opta/FotMob": "chances_created"},
        ]
    )

    saida = Path(r"C:\dev\players_scores\palmeiras_ultimos_5_jogos_brasileirao.xlsx")
    with pd.ExcelWriter(saida, engine="openpyxl") as writer:
        out.to_excel(writer, sheet_name="dados_brutos", index=False)
        pd.DataFrame(resumo).to_excel(writer, sheet_name="jogos", index=False)
        mapa.to_excel(writer, sheet_name="mapeamento", index=False)
        for sheet in writer.sheets:
            ws = writer.sheets[sheet]
            for col in ws.columns:
                letra = col[0].column_letter
                largura = min(max((len(str(c.value)) if c.value else 0) for c in col) + 2, 70)
                ws.column_dimensions[letra].width = largura

    print("Arquivo:", saida)
    print("Linhas:", len(out), "jogadores únicos:", out["Jogador"].nunique())


if __name__ == "__main__":
    main()
