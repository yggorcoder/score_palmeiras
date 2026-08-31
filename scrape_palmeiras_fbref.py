# -*- coding: utf-8 -*-
"""Extrai estatisticas dos ultimos 5 jogos do Palmeiras no Brasileirao (FBref)."""
from __future__ import annotations

from io import StringIO
from pathlib import Path

import pandas as pd
from lxml import html as lxml_html

MATCHES = [
    {
        "arquivo": "vitoria.html",
        "data": "2026-07-29",
        "adversario": "Vitória",
        "local": "Fora",
        "resultado": "4-0",
        "nivel": 3,
        "url": "https://fbref.com/en/matches/c00556ef/Vitoria-Palmeiras-July-29-2026-Serie-A",
        "completo": True,
    },
    {
        "arquivo": "internacional.html",
        "data": "2026-08-09",
        "adversario": "Internacional",
        "local": "Casa",
        "resultado": "0-0",
        "nivel": 2,
        "url": "https://fbref.com/en/matches/0b682d4e/Palmeiras-Internacional-August-9-2026-Serie-A",
        "completo": True,
    },
    {
        "arquivo": "fluminense.html",
        "data": "2026-08-15",
        "adversario": "Fluminense",
        "local": "Fora",
        "resultado": "2-3",
        "nivel": 5,
        "url": "https://fbref.com/en/matches/83f2942f/Fluminense-Palmeiras-August-15-2026-Serie-A",
        "completo": True,
    },
    {
        "arquivo": "vasco.html",
        "data": "2026-08-23",
        "adversario": "Vasco da Gama",
        "local": "Casa",
        "resultado": "4-1",
        "nivel": 2,
        "url": "https://fbref.com/en/matches/d441eb53/Palmeiras-Vasco-da-Gama-August-23-2026-Serie-A",
        "completo": True,
    },
    {
        "arquivo": "mirassol.html",
        "data": "2026-08-30",
        "adversario": "Mirassol",
        "local": "Fora",
        "resultado": "1-1",
        "nivel": 2,
        "url": "https://fbref.com/en/matches/00202f2b/Mirassol-Palmeiras-August-30-2026-Serie-A",
        "completo": False,
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
    "Vitor Roque": "Centroavante",
    "Paulinho": "Centroavante",
    "Luighi": "Centroavante",
    "Heittor Vinicius": "Centroavante",
    "Heittor": "Centroavante",
    "Riquelme Fillipi": "Extremo",
}

POSICAO_FBREF = {
    "GK": "Goleiro",
    "CB": "Zagueiro",
    "LB": "Lateral Esquerdo",
    "LWB": "Lateral Esquerdo",
    "RB": "Lateral Direito",
    "RWB": "Lateral Direito",
    "WB": "Lateral Direito",
    "DM": "Volante",
    "CM": "Meia",
    "MF": "Meia",
    "AM": "Meia",
    "LM": "Extremo",
    "RM": "Extremo",
    "WM": "Extremo",
    "LW": "Extremo",
    "RW": "Extremo",
    "FW": "Centroavante",
    "ST": "Centroavante",
}

FBREF_DISPONIVEL = {
    "Jogador": "Nome do jogador no FBref",
    "Posição": "Mapeada a partir da posição tática do FBref + elenco Palmeiras",
    "Nível do jogo": "Escala 1-5 segundo a força do adversário na tabela (não existe no FBref)",
    "Minutos jogados": "Min",
    "Golos": "Gls",
    "Assistências": "Ast",
    "Remates": "Sh",
    "Remates no alvo": "SoT",
    "Cruzamentos": "Crs (tentados)",
    "Cartões amarelos": "CrdY",
    "Cartões vermelhos": "CrdR",
    "Interceções": "Int",
    "Faltas cometidas": "Fls",
    "Faltas sofridas": "Fld",
}

FBREF_INDISPONIVEL = [
    "xG",
    "xA",
    "Passes",
    "Passes certos",
    "Cruzamentos certos",
    "Dribles",
    "Dribles certos",
    "Duelos",
    "Duelos certos",
    "Perdas (total)",
    "Recuperações (total)",
    "Toques na área",
    "Duelos defensivos",
    "Duelos ofensivos",
    "Duelos aéreos",
    "Remates bloqueados",
    "Alívios (Clearances)",
    "Passes decisivos",
    "Segunda assistência",
    "Terceira assistência",
    "Shot assists",
]


def flatten_cols(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [c[1] if isinstance(c, tuple) else c for c in df.columns]
    return df


def mapear_posicao(jogador: str, pos_fbref: str) -> str:
    if jogador in POSICAO_POR_JOGADOR:
        return POSICAO_POR_JOGADOR[jogador]
    primeira = str(pos_fbref).split(",")[0].strip().upper()
    return POSICAO_FBREF.get(primeira, str(pos_fbref))


def num(valor) -> float | int:
    if pd.isna(valor) or valor == "":
        return 0
    try:
        n = float(valor)
    except (TypeError, ValueError):
        return 0
    if n.is_integer():
        return int(n)
    return n


def texto_celula(td) -> str:
    links = td.xpath(".//a/text()")
    if links:
        return links[0].strip()
    return "".join(td.xpath(".//text()")).strip()


def extrair_tabela_id(html: str, table_id: str) -> pd.DataFrame:
    tree = lxml_html.fromstring(html)
    tabelas = tree.xpath(f'//table[@id="{table_id}"]')
    if not tabelas:
        return pd.DataFrame()
    tabela = tabelas[0]
    linhas = []
    for tr in tabela.xpath(".//tbody/tr"):
        if tr.get("class") and "spacer" in (tr.get("class") or ""):
            continue
        row = {}
        for cell in tr.xpath("./th|./td"):
            stat = cell.get("data-stat")
            if not stat:
                continue
            row[stat] = texto_celula(cell)
        nome = row.get("player", "")
        if not nome or "Players" in nome:
            continue
        linhas.append(row)
    if not linhas:
        return pd.DataFrame()
    df = pd.DataFrame(linhas)
    rename = {
        "player": "Player",
        "position": "Pos",
        "minutes": "Min",
        "goals": "Gls",
        "assists": "Ast",
        "shots": "Sh",
        "shots_on_target": "SoT",
        "cards_yellow": "CrdY",
        "cards_red": "CrdR",
        "crosses": "Crs",
        "interceptions": "Int",
        "fouls": "Fls",
        "fouled": "Fld",
    }
    df = df.rename(columns=rename)
    return df


def extrair_palmeiras(html: str) -> pd.DataFrame:
    df = extrair_tabela_id(html, "stats_abdce579_summary")
    if not df.empty:
        return df
    tables = pd.read_html(StringIO(html))
    candidatas = []
    for t in tables:
        flat = flatten_cols(t)
        if "Player" not in flat.columns or "Min" not in flat.columns:
            continue
        if "Gls" not in flat.columns:
            continue
        blob = " ".join(flat["Player"].astype(str).tolist())
        if "Carlos Miguel" in blob and "Marlon Freitas" in blob:
            return flat
        if "Players" in blob or len(flat) >= 11:
            candidatas.append(flat)
    return candidatas[-1] if candidatas else pd.DataFrame()


def linha_padrao(jogo: dict, row: pd.Series) -> dict:
    jogador = str(row["Player"]).strip()
    pos_fb = str(row.get("Pos", "")).strip()
    dados = {c: None for c in COLUNAS_DADOS_BRUTOS}
    dados.update(
        {
            "Data": jogo["data"],
            "Adversário": jogo["adversario"],
            "Local": jogo["local"],
            "Resultado": jogo["resultado"],
            "Jogador": jogador,
            "Posição": mapear_posicao(jogador, pos_fb),
            "Posição FBref": pos_fb,
            "Nível do jogo": jogo["nivel"],
            "Minutos jogados": num(row.get("Min")),
            "Golos": num(row.get("Gls")),
            "Assistências": num(row.get("Ast")),
            "Remates": num(row.get("Sh")),
            "Remates no alvo": num(row.get("SoT")),
            "Cruzamentos": num(row.get("Crs")),
            "Cartões amarelos": num(row.get("CrdY")),
            "Cartões vermelhos": num(row.get("CrdR")),
            "Interceções": num(row.get("Int")),
            "Faltas cometidas": num(row.get("Fls")),
            "Faltas sofridas": num(row.get("Fld")),
            "Fonte": "FBref match report",
            "URL FBref": jogo["url"],
        }
    )
    return dados


def main() -> None:
    pasta = Path(r"C:\dev\players_scores\_fbref_matches")
    linhas = []
    jogos_ok = []
    jogos_incompletos = []

    for jogo in MATCHES:
        html_path = pasta / jogo["arquivo"]
        alt = pasta / "mirassol_save.html"
        if jogo["arquivo"] == "mirassol.html" and alt.exists() and alt.stat().st_size > 180000:
            html_path = alt
            jogo = dict(jogo)
            jogo["completo"] = True
        html = html_path.read_text(encoding="utf-8")
        df = extrair_palmeiras(html)
        if df.empty:
            jogos_incompletos.append(jogo["adversario"])
            continue
        df = df[~df["Player"].astype(str).str.contains("Players", na=False)].copy()
        df = df[df["Min"].notna()].copy()
        if len(df) < 8:
            jogos_incompletos.append(jogo["adversario"])
            continue
        for _, row in df.iterrows():
            linhas.append(linha_padrao(jogo, row))
        jogos_ok.append(f"{jogo['data']} {jogo['adversario']} {jogo['resultado']} ({len(df)} jogadores)")

    colunas_saida = [
        "Data",
        "Adversário",
        "Local",
        "Resultado",
        "Posição FBref",
        "Fonte",
        "URL FBref",
    ] + COLUNAS_DADOS_BRUTOS

    out = pd.DataFrame(linhas)
    for c in colunas_saida:
        if c not in out.columns:
            out[c] = None
    out = out[colunas_saida]
    out = out.sort_values(["Data", "Minutos jogados", "Jogador"], ascending=[True, False, True]).reset_index(drop=True)

    mapa_rows = []
    for col in COLUNAS_DADOS_BRUTOS:
        if col in FBREF_DISPONIVEL:
            mapa_rows.append({"Coluna dados_brutos": col, "No FBref (Brasileirão)": "Sim", "Origem / observação": FBREF_DISPONIVEL[col]})
        elif col in FBREF_INDISPONIVEL:
            mapa_rows.append({"Coluna dados_brutos": col, "No FBref (Brasileirão)": "Não", "Origem / observação": "FBref não publica esta métrica nos relatórios da Série A (cobertura básica, sem Opta avançado)"})
        else:
            mapa_rows.append({"Coluna dados_brutos": col, "No FBref (Brasileirão)": "", "Origem / observação": ""})
    mapa = pd.DataFrame(mapa_rows)

    jogos_df = pd.DataFrame(
        [
            {
                "Data": j["data"],
                "Adversário": j["adversario"],
                "Local": j["local"],
                "Resultado Palmeiras": j["resultado"],
                "Nível do jogo": j["nivel"],
                "URL FBref": j["url"],
                "Status coleta": "Coletado" if j["adversario"] not in jogos_incompletos else "Relatório ainda não estava no arquivo (jogo muito recente)",
            }
            for j in MATCHES
        ]
    )

    saida = Path(r"C:\dev\players_scores\palmeiras_ultimos_5_jogos_brasileirao.xlsx")
    with pd.ExcelWriter(saida, engine="openpyxl") as writer:
        out.to_excel(writer, sheet_name="dados_brutos", index=False)
        jogos_df.to_excel(writer, sheet_name="jogos", index=False)
        mapa.to_excel(writer, sheet_name="mapeamento_fbref", index=False)

        ws = writer.sheets["dados_brutos"]
        for col in ws.columns:
            letra = col[0].column_letter
            largura = min(max((len(str(c.value)) if c.value else 0) for c in col) + 2, 42)
            ws.column_dimensions[letra].width = largura
        for sheet in ("jogos", "mapeamento_fbref"):
            ws2 = writer.sheets[sheet]
            for col in ws2.columns:
                letra = col[0].column_letter
                largura = min(max((len(str(c.value)) if c.value else 0) for c in col) + 2, 80)
                ws2.column_dimensions[letra].width = largura

    print("Arquivo:", saida)
    print("Linhas:", len(out))
    print("Jogos ok:")
    for item in jogos_ok:
        print(" -", item)
    print("Jogos incompletos:", jogos_incompletos)
    print("Jogadores únicos:", out["Jogador"].nunique())


if __name__ == "__main__":
    main()
