"""Exporta JSON/JS do ranking e dos jogos para o dashboard HTML."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "dashboard" / "data.js"

PESOS_OFENSIVOS = {
    "Zagueiro": {
        "Golos": 0.07, "xG": 0.05, "Assistências": 0.05, "xA": 0.04,
        "Remates": 0.03, "Remates no alvo": 0.04,
        "Passes": 0.10, "Passes certos": 0.15,
        "Cruzamentos": 0.01, "Cruzamentos certos": 0.02,
        "Dribles": 0.02, "Dribles certos": 0.03,
        "Duelos ofensivos": 0.05, "Toques na área": 0.04, "Faltas sofridas": 0.03,
        "Passes decisivos": 0.08, "Segunda assistência": 0.06,
        "Terceira assistência": 0.07, "Shot assists": 0.06,
    },
    "Lateral Direito": {
        "Golos": 0.05, "xG": 0.04, "Assistências": 0.10, "xA": 0.08,
        "Remates": 0.03, "Remates no alvo": 0.03,
        "Passes": 0.05, "Passes certos": 0.07,
        "Cruzamentos": 0.07, "Cruzamentos certos": 0.10,
        "Dribles": 0.03, "Dribles certos": 0.05,
        "Duelos ofensivos": 0.04, "Toques na área": 0.03, "Faltas sofridas": 0.03,
        "Passes decisivos": 0.09, "Segunda assistência": 0.05,
        "Terceira assistência": 0.02, "Shot assists": 0.04,
    },
    "Lateral Esquerdo": {
        "Golos": 0.05, "xG": 0.04, "Assistências": 0.10, "xA": 0.08,
        "Remates": 0.03, "Remates no alvo": 0.03,
        "Passes": 0.05, "Passes certos": 0.07,
        "Cruzamentos": 0.07, "Cruzamentos certos": 0.10,
        "Dribles": 0.03, "Dribles certos": 0.05,
        "Duelos ofensivos": 0.04, "Toques na área": 0.03, "Faltas sofridas": 0.03,
        "Passes decisivos": 0.09, "Segunda assistência": 0.05,
        "Terceira assistência": 0.02, "Shot assists": 0.04,
    },
    "Volante": {
        "Golos": 0.04, "xG": 0.03, "Assistências": 0.07, "xA": 0.06,
        "Remates": 0.03, "Remates no alvo": 0.03,
        "Passes": 0.08, "Passes certos": 0.12,
        "Cruzamentos": 0.02, "Cruzamentos certos": 0.02,
        "Dribles": 0.02, "Dribles certos": 0.04,
        "Duelos ofensivos": 0.04, "Toques na área": 0.03, "Faltas sofridas": 0.04,
        "Passes decisivos": 0.11, "Segunda assistência": 0.10,
        "Terceira assistência": 0.06, "Shot assists": 0.06,
    },
    "Meia": {
        "Golos": 0.08, "xG": 0.06, "Assistências": 0.11, "xA": 0.09,
        "Remates": 0.04, "Remates no alvo": 0.05,
        "Passes": 0.05, "Passes certos": 0.07,
        "Cruzamentos": 0.02, "Cruzamentos certos": 0.03,
        "Dribles": 0.04, "Dribles certos": 0.06,
        "Duelos ofensivos": 0.04, "Toques na área": 0.04, "Faltas sofridas": 0.04,
        "Passes decisivos": 0.11, "Segunda assistência": 0.05,
        "Terceira assistência": 0.02, "Shot assists": 0.03,
    },
    "Extremo": {
        "Golos": 0.11, "xG": 0.08, "Assistências": 0.09, "xA": 0.07,
        "Remates": 0.05, "Remates no alvo": 0.06,
        "Passes": 0.02, "Passes certos": 0.03,
        "Cruzamentos": 0.04, "Cruzamentos certos": 0.06,
        "Dribles": 0.05, "Dribles certos": 0.08,
        "Duelos ofensivos": 0.05, "Toques na área": 0.06, "Faltas sofridas": 0.04,
        "Passes decisivos": 0.06, "Segunda assistência": 0.02,
        "Terceira assistência": 0.01, "Shot assists": 0.02,
    },
    "Centroavante": {
        "Golos": 0.16, "xG": 0.12, "Assistências": 0.06, "xA": 0.05,
        "Remates": 0.06, "Remates no alvo": 0.08,
        "Passes": 0.02, "Passes certos": 0.04,
        "Cruzamentos": 0.01, "Cruzamentos certos": 0.02,
        "Dribles": 0.02, "Dribles certos": 0.04,
        "Duelos ofensivos": 0.05, "Toques na área": 0.10, "Faltas sofridas": 0.05,
        "Passes decisivos": 0.05, "Segunda assistência": 0.02,
        "Terceira assistência": 0.01, "Shot assists": 0.04,
    },
}

PESOS_DEFENSIVOS = {
    "Zagueiro": {
        "Recuperações (total)": 0.18, "Duelos defensivos": 0.14,
        "Duelos": 0.06, "Duelos certos": 0.10,
        "Interceções": 0.14, "Alívios (Clearances)": 0.13,
        "Remates bloqueados": 0.13, "Duelos aéreos": 0.12,
        "Perdas (total)": -0.05, "Faltas cometidas": -0.04,
        "Cartões amarelos": -0.06, "Cartões vermelhos": -0.15,
    },
    "Lateral Direito": {
        "Recuperações (total)": 0.18, "Duelos defensivos": 0.15,
        "Duelos": 0.07, "Duelos certos": 0.11,
        "Interceções": 0.15, "Alívios (Clearances)": 0.11,
        "Remates bloqueados": 0.11, "Duelos aéreos": 0.12,
        "Perdas (total)": -0.05, "Faltas cometidas": -0.04,
        "Cartões amarelos": -0.06, "Cartões vermelhos": -0.15,
    },
    "Lateral Esquerdo": {
        "Recuperações (total)": 0.18, "Duelos defensivos": 0.15,
        "Duelos": 0.07, "Duelos certos": 0.11,
        "Interceções": 0.15, "Alívios (Clearances)": 0.11,
        "Remates bloqueados": 0.11, "Duelos aéreos": 0.12,
        "Perdas (total)": -0.05, "Faltas cometidas": -0.04,
        "Cartões amarelos": -0.06, "Cartões vermelhos": -0.15,
    },
    "Volante": {
        "Recuperações (total)": 0.18, "Duelos defensivos": 0.16,
        "Duelos": 0.08, "Duelos certos": 0.12,
        "Interceções": 0.16, "Alívios (Clearances)": 0.08,
        "Remates bloqueados": 0.11, "Duelos aéreos": 0.11,
        "Perdas (total)": -0.06, "Faltas cometidas": -0.05,
        "Cartões amarelos": -0.06, "Cartões vermelhos": -0.15,
    },
    "Meia": {
        "Recuperações (total)": 0.19, "Duelos defensivos": 0.15,
        "Duelos": 0.09, "Duelos certos": 0.13,
        "Interceções": 0.15, "Alívios (Clearances)": 0.06,
        "Remates bloqueados": 0.10, "Duelos aéreos": 0.11,
        "Perdas (total)": -0.06, "Faltas cometidas": -0.05,
        "Cartões amarelos": -0.06, "Cartões vermelhos": -0.15,
    },
    "Extremo": {
        "Recuperações (total)": 0.20, "Duelos defensivos": 0.17,
        "Duelos": 0.10, "Duelos certos": 0.14,
        "Interceções": 0.15, "Alívios (Clearances)": 0.04,
        "Remates bloqueados": 0.10, "Duelos aéreos": 0.10,
        "Perdas (total)": -0.06, "Faltas cometidas": -0.05,
        "Cartões amarelos": -0.06, "Cartões vermelhos": -0.15,
    },
    "Centroavante": {
        "Recuperações (total)": 0.20, "Duelos defensivos": 0.17,
        "Duelos": 0.11, "Duelos certos": 0.15,
        "Interceções": 0.13, "Alívios (Clearances)": 0.04,
        "Remates bloqueados": 0.08, "Duelos aéreos": 0.12,
        "Perdas (total)": -0.06, "Faltas cometidas": -0.05,
        "Cartões amarelos": -0.06, "Cartões vermelhos": -0.15,
    },
}

STAT_KEYS = [
    "Golos", "xG", "Assistências", "xA",
    "Remates", "Remates no alvo",
    "Passes", "Passes certos",
    "Cruzamentos", "Cruzamentos certos",
    "Dribles", "Dribles certos",
    "Duelos", "Duelos certos",
    "Perdas (total)", "Recuperações (total)",
    "Toques na área",
    "Cartões amarelos", "Cartões vermelhos",
    "Duelos defensivos", "Duelos ofensivos", "Duelos aéreos",
    "Remates bloqueados", "Interceções", "Alívios (Clearances)",
    "Faltas cometidas", "Faltas sofridas",
    "Passes decisivos", "Segunda assistência", "Terceira assistência",
    "Shot assists",
]


def _num(value) -> float:
    if pd.isna(value):
        return 0.0
    return float(value)


def score_bruto(row: pd.Series, pesos: dict) -> float | None:
    posicao = row["Posição"]
    if posicao not in pesos:
        return None
    total = 0.0
    for variavel, peso in pesos[posicao].items():
        total += _num(row.get(variavel, 0)) * peso
    return total


def round_or_none(value, digits=3):
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    return round(float(value), digits)


def main() -> None:
    ranking = pd.read_excel(ROOT / "resultado_scores_palmeiras.xlsx", sheet_name="Ranking")
    base = pd.read_excel(ROOT / "resultado_scores_palmeiras.xlsx", sheet_name="Base_com_Scores")
    brutos = pd.read_excel(ROOT / "palmeiras_ultimos_5_jogos_brasileirao.xlsx", sheet_name="dados_brutos")
    jogos_df = pd.read_excel(ROOT / "palmeiras_ultimos_5_jogos_brasileirao.xlsx", sheet_name="jogos")

    merged = ranking.merge(
        base,
        on=["Jogador", "Posição"],
        how="left",
        suffixes=("", "_base"),
    )

    players = []
    for _, row in merged.iterrows():
        stats = {k: round_or_none(row.get(k), 3 if k in {"xG", "xA"} else 2) for k in STAT_KEYS}
        players.append({
            "jogador": row["Jogador"],
            "posicao": row["Posição"],
            "minutos": int(round(_num(row["Minutos jogados"]))),
            "nivel": round_or_none(row["Nível do jogo"], 2),
            "jogos": int((brutos["Jogador"] == row["Jogador"]).sum()),
            "notaOfensiva": round_or_none(row["Nota_Ofensiva_0_5"], 2),
            "notaDefensiva": round_or_none(row["Nota_Defensiva_0_5"], 2),
            "rankOfensivo": int(row["Rank_Ofensivo"]),
            "rankDefensivo": int(row["Rank_Defensivo"]),
            "scoreFinal": round_or_none(row["Score_Final"], 2),
            "scoreOfBruto": round_or_none(row["Score_Of_Bruto"], 2),
            "scoreDefBruto": round_or_none(row["Score_Def_Bruto"], 2),
            **stats,
        })

    jogos = []
    for i, row in jogos_df.iterrows():
        data = pd.to_datetime(row["Data"]).strftime("%Y-%m-%d")
        adversario = str(row["Adversário"])
        jogos.append({
            "id": data,
            "data": data,
            "adversario": adversario,
            "local": str(row["Local"]),
            "resultado": str(row["Resultado Palmeiras"]),
            "nivel": int(row["Nível do jogo"]),
        })

    performances = []
    linhas = brutos[brutos["Posição"] != "Goleiro"].copy()
    linhas["scoreOfBruto"] = linhas.apply(lambda r: score_bruto(r, PESOS_OFENSIVOS), axis=1)
    linhas["scoreDefBruto"] = linhas.apply(lambda r: score_bruto(r, PESOS_DEFENSIVOS), axis=1)
    linhas["minutosAjustados"] = linhas["Minutos jogados"].clip(lower=20)
    linhas["scoreOfAjustado"] = (
        linhas["scoreOfBruto"] * linhas["Nível do jogo"] / linhas["minutosAjustados"]
    )
    linhas["scoreDefAjustado"] = (
        linhas["scoreDefBruto"] * linhas["Nível do jogo"] / linhas["minutosAjustados"]
    )

    for _, row in linhas.iterrows():
        data = pd.to_datetime(row["Data"]).strftime("%Y-%m-%d")
        stats = {k: round_or_none(row.get(k), 3 if k in {"xG", "xA"} else 2) for k in STAT_KEYS}
        of_aj = _num(row["scoreOfAjustado"])
        def_aj = _num(row["scoreDefAjustado"])
        performances.append({
            "jogador": row["Jogador"],
            "posicao": row["Posição"],
            "data": data,
            "adversario": str(row["Adversário"]),
            "local": str(row["Local"]),
            "resultado": str(row["Resultado"]),
            "nivel": int(row["Nível do jogo"]),
            "minutos": int(round(_num(row["Minutos jogados"]))),
            "scoreOfAjustado": round(of_aj, 4),
            "scoreDefAjustado": round(def_aj, 4),
            "scoreAjustado": round((of_aj + def_aj) / 2, 4),
            **stats,
        })

    payload = {
        "meta": {
            "time": "Palmeiras",
            "competicao": "Brasileirão 2026",
            "janela": "Últimos 5 jogos",
            "fonte": "FotMob / Opta · modelo Score CIGA",
            "escala": "Notas 0–5 normalizadas contra o elenco (sem goleiros)",
        },
        "jogos": jogos,
        "players": players,
        "performances": performances,
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    js = "window.DASHBOARD_DATA = " + json.dumps(payload, ensure_ascii=False, indent=2) + ";\n"
    OUT.write_text(js, encoding="utf-8")
    print(f"Escrito {OUT} ({len(players)} jogadores, {len(performances)} atuações)")


if __name__ == "__main__":
    main()
