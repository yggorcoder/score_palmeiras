# Score Palmeiras

**Do dado bruto à reunião da comissão técnica.**  
Modelo de desempenho por posição + dashboard interativo, aplicado aos últimos jogos do Palmeiras no Brasileirão.

> Destinado a analistas de desempenho, scouting, coordenação técnica e RH de clubes que avaliam profissionais capazes de transformar estatística em decisão.

**[Abrir o dashboard](https://yggorcoder.github.io/score_palmeiras/)** · [Repositório](https://github.com/yggorcoder/score_palmeiras)

---

## O problema que um clube vive toda semana

Gols e notas de imprensa não respondem às perguntas da diretoria:

- Quem entregou para a **função tática**, não só para o placar?
- O reserva de 20 minutos inflou a média — ou o titular de 400 minutos sustentou o bloco?
- O meia que fez 4 gols realmente **ganhou o meio**, ou só finalizou?
- Como comparar um zagueiro construtor com um centroavante de área **sem misturar os papéis**?

Este projeto responde a isso com um pipeline reproduzível: coleta das partidas, score ofensivo e defensivo ponderado por posição, ajuste por minutos e nível do adversário, e um frontend para a comissão filtrar, clicar e discutir.

Estudo de caso: **Palmeiras, Brasileirão 2026, últimos 5 jogos** (Vitória, Internacional, Fluminense, Vasco e Mirassol).

---

## O que o RH encontra aqui

Não é um notebook solto. É o recorte de um profissional que consegue atravessar o clube:

| Entrega | O que demonstra |
|---|---|
| Coleta das 5 partidas (FotMob / Opta) | Sai do Excel manual; monta base jogador × jogo |
| Pesos ofensivos e defensivos **por posição** | Fala a língua da comissão (volante ≠ extremo) |
| Score 0–5 + ranking | Traduz métrica em linguagem de reunião |
| Dashboard com filtros (jogo, posição, minutos) | Produto que o diretor abre no navegador |
| Limitações documentadas | Madureza analítica: sabe o que o modelo *não* mede |

Stack: Python, pandas, openpyxl, HTML/CSS/JavaScript. Sem framework pesado — o dashboard abre localmente ou pelo GitHub Pages.

---

## Como a comissão usa o dashboard

1. **Filtro de minutos** — decisão de titularidade só com amostra (ex.: ≥ 150').
2. **Filtro de posição** — compara lateral com lateral, não com centroavante.
3. **Jogo a jogo** — o Fluminense (nível 5, única derrota do recorte) vira o stress test.
4. **Gráfico ofensivo × defensivo** — perfil tático, com nome em cada atleta.
5. **Ficha do jogador** — gols, xG, duelos, recuperações e a linha dos 5 jogos.

No recorte do Palmeiras, o modelo deixa explícito um ponto típico de reunião: o artilheiro do período não é automaticamente o melhor score de meio-campo. Gols continuam valendo no campo; a nota descreve **volume útil para a função**.

---

## Como o score é calculado

Cada linha da base é um **jogador em um jogo**. O notebook agrega o período e aplica o modelo **Score CIGA**:

1. **Score bruto** — cada métrica × peso da posição (zagueiro, lateral, volante, meia, extremo, centroavante). Goleiro fica fora da escala: não há pesos para a posição.
2. **Score ajustado** — multiplica pelo nível do adversário (1–5) e divide pelos minutos. Minutos abaixo de 20 viram 20 no denominador, para o reserva de 3 minutos não explodir a nota.
3. **Nota 0–5** — min–máx contra o elenco de campo. Cinco é o teto *deste* grupo *neste* bloco, não uma nota de mercado.
4. **Ranking** — geral e por posição (ofensivo / defensivo / score final).

### Leitura honesta (importante para quem decide)

A nota 0–5 **não é calculada dentro da posição**. Volume de passe de zagueiro e volume de duelo de atacante competem na mesma régua. Por isso, no gráfico geral, zagueiros tendem a aparecer mais “ofensivos” e atacantes mais “defensivos”. **Isso é efeito de escala, não diagnóstico tático.** A comparação justa está no filtro por posição e no rank dentro da função.

---

## Como rodar

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
pip install -r requirements.txt
```

**Dashboard (sem instalar nada além do navegador)**  
Abra `palmeiras_scores.html` ou sirva a pasta:

```bash
python -m http.server 5500 --bind 127.0.0.1
```

Depois: [http://127.0.0.1:5500/dashboard/](http://127.0.0.1:5500/dashboard/)

**Recalcular scores**  
Execute `Curso_Imersao_Scores.ipynb` (lê `palmeiras_ultimos_5_jogos_brasileirao.xlsx` e gera `resultado_scores_palmeiras.xlsx`).

**Atualizar o dashboard**

```bash
python export_dashboard.py
python abrir_dashboard.py
```

**Nova coleta de jogos** (opcional): `scrape_palmeiras_fotmob.py`.

---

## Estrutura

```
Curso_Imersao_Scores.ipynb      # modelo e exportação do ranking
palmeiras_ultimos_5_jogos_brasileirao.xlsx
resultado_scores_palmeiras.xlsx
dashboard/                      # frontend interativo
palmeiras_scores.html           # versão única, abre com dois cliques
export_dashboard.py
scrape_palmeiras_fotmob.py
```

---

## Para quem contrata análise de desempenho

O perfil que este repositório ilustra:

- **Traduz o jogo em modelo**, com pesos que mudam com a função em campo.
- **Fecha o ciclo** até um artefato que a diretoria consegue usar (filtro, gráfico, ficha).
- **Documenta o viés** em vez de esconder (normalização entre posições, piso de minutos, amostra curta).
- **Trabalha com janela real de campeonato**, não com dataset didático genérico.

Janela pequena (5 jogos) é escolha consciente: é o recorte que um clube pede na semana. O código está pronto para o próximo bloco de partidas.

---

## Autor

**Yggor Ramos**  
Análise de desempenho · dados aplicados ao futebol  

[github.com/yggorcoder](https://github.com/yggorcoder) · [github.com/yggorcoder/score_palmeiras](https://github.com/yggorcoder/score_palmeiras)
