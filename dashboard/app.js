const DATA = window.DASHBOARD_DATA;

const POSICOES = [
  "Zagueiro",
  "Lateral Direito",
  "Lateral Esquerdo",
  "Volante",
  "Meia",
  "Extremo",
  "Centroavante",
];

const POS_ABBR = {
  Zagueiro: "ZAG",
  "Lateral Direito": "LD",
  "Lateral Esquerdo": "LE",
  Volante: "VOL",
  Meia: "MEI",
  Extremo: "EXT",
  Centroavante: "CA",
};

const POS_COLOR = {
  Zagueiro: "#7aa2c4",
  "Lateral Direito": "#3db8a0",
  "Lateral Esquerdo": "#2a8f7c",
  Volante: "#3dce73",
  Meia: "#d4b45a",
  Extremo: "#e08a3c",
  Centroavante: "#d45b5b",
};

const METRIC_LABEL = {
  scoreFinal: "Score final",
  notaOfensiva: "Nota ofensiva",
  notaDefensiva: "Nota defensiva",
};

const state = {
  search: "",
  posicoes: new Set(),
  jogo: "all",
  minMinutos: 0,
  sort: "scoreFinal",
  metric: "scoreFinal",
  selected: null,
};

const els = {
  metaLine: document.getElementById("metaLine"),
  matchStrip: document.getElementById("matchStrip"),
  posChips: document.getElementById("posChips"),
  searchInput: document.getElementById("searchInput"),
  minRange: document.getElementById("minRange"),
  minLabel: document.getElementById("minLabel"),
  sortSelect: document.getElementById("sortSelect"),
  metricSelect: document.getElementById("metricSelect"),
  resetBtn: document.getElementById("resetBtn"),
  kpis: document.getElementById("kpis"),
  bars: document.getElementById("bars"),
  barTitle: document.getElementById("barTitle"),
  scatter: document.getElementById("scatter"),
  legend: document.getElementById("legend"),
  tbody: document.getElementById("tbody"),
  tableHint: document.getElementById("tableHint"),
  drawer: document.getElementById("drawer"),
  drawerName: document.getElementById("drawerName"),
  drawerPos: document.getElementById("drawerPos"),
  drawerScore: document.getElementById("drawerScore"),
  drawerMeters: document.getElementById("drawerMeters"),
  drawerStats: document.getElementById("drawerStats"),
  drawerGames: document.getElementById("drawerGames"),
  tooltip: document.getElementById("tooltip"),
};

function fmt(n, digits = 2) {
  if (n == null || Number.isNaN(n)) return "—";
  return Number(n).toLocaleString("pt-BR", {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  });
}

function fmtInt(n) {
  return Math.round(n || 0).toString();
}

function scoreColor(v) {
  if (v >= 3.5) return "var(--green-bright)";
  if (v >= 2) return "var(--gold)";
  return "var(--danger)";
}

function normalize05(values) {
  const min = Math.min(...values);
  const max = Math.max(...values);
  if (max === min) return values.map(() => 2.5);
  return values.map((v) => (5 * (v - min)) / (max - min));
}

function dateLabel(iso) {
  const [y, m, d] = iso.split("-");
  return `${d}/${m}`;
}

function escapeXml(text) {
  return String(text)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function dayKey(value) {
  return String(value || "").slice(0, 10);
}

function shortName(full, allNames) {
  const parts = full.trim().split(/\s+/);
  const last = parts[parts.length - 1];
  const clashes = allNames.filter((n) => n.trim().split(/\s+/).pop() === last).length > 1;
  if (clashes && parts.length > 1) return `${parts[0]} ${last}`;
  return last;
}

function resultClass(resultado) {
  const [a, b] = resultado.split("-").map(Number);
  if (a > b) return "W";
  if (a < b) return "L";
  return "D";
}

function matchRows() {
  if (state.jogo === "all") {
    return DATA.players.map((p) => ({ ...p, origem: "periodo" }));
  }

  const games = DATA.performances.filter((p) => dayKey(p.data) === dayKey(state.jogo));
  const ofN = normalize05(games.map((p) => p.scoreOfAjustado));
  const defN = normalize05(games.map((p) => p.scoreDefAjustado));

  return games.map((p, i) => ({
    ...p,
    notaOfensiva: Math.round(ofN[i] * 100) / 100,
    notaDefensiva: Math.round(defN[i] * 100) / 100,
    scoreFinal: Math.round(((ofN[i] + defN[i]) / 2) * 100) / 100,
    jogos: 1,
    origem: "jogo",
  }));
}

function filteredRows() {
  const q = state.search.trim().toLowerCase();
  let rows = matchRows().filter((p) => {
    if (state.posicoes.size && !state.posicoes.has(p.posicao)) return false;
    if (p.minutos < state.minMinutos) return false;
    if (q && !p.jogador.toLowerCase().includes(q)) return false;
    return true;
  });

  const key = state.sort;
  rows.sort((a, b) => {
    if (key === "jogador") return a.jogador.localeCompare(b.jogador, "pt-BR");
    return (b[key] ?? 0) - (a[key] ?? 0);
  });
  return rows;
}

function renderMatches() {
  const all = `<button type="button" class="match ${state.jogo === "all" ? "active" : ""}" data-jogo="all">
    <strong>5 jogos</strong><span>período</span>
  </button>`;

  const items = DATA.jogos.map((j) => {
    const active = dayKey(state.jogo) === dayKey(j.id) ? "active" : "";
    const tag = resultClass(j.resultado);
    return `<button type="button" class="match ${active}" data-jogo="${j.id}" data-result="${tag}">
      <strong>${j.resultado}</strong>
      <span>${dateLabel(j.data)} ${j.adversario}</span>
      <span class="lvl">${j.local} · nv ${j.nivel}</span>
    </button>`;
  }).join("");

  els.matchStrip.innerHTML = all + items;
}

function renderChips() {
  els.posChips.innerHTML = POSICOES.map((pos) => {
    const on = state.posicoes.has(pos) ? "active" : "";
    return `<button type="button" class="chip ${on}" data-pos="${pos}">${POS_ABBR[pos]}</button>`;
  }).join("");
}

function renderKpis(rows) {
  if (!rows.length) {
    els.kpis.innerHTML = `<div class="kpi"><p>Sem atletas</p><strong>0</strong></div>`;
    return;
  }
  const best = [...rows].sort((a, b) => b.scoreFinal - a.scoreFinal)[0];
  const avg = rows.reduce((s, r) => s + r.scoreFinal, 0) / rows.length;
  const gols = rows.reduce((s, r) => s + (r.Golos || 0), 0);
  const mins = rows.reduce((s, r) => s + r.minutos, 0);

  els.kpis.innerHTML = `
    <div class="kpi"><p>Melhor score</p><strong>${fmt(best.scoreFinal)}</strong><em>${best.jogador}</em></div>
    <div class="kpi"><p>Média do recorte</p><strong>${fmt(avg)}</strong><em>${rows.length} atletas</em></div>
    <div class="kpi"><p>Gols</p><strong>${fmtInt(gols)}</strong><em>${fmtInt(rows.reduce((s, r) => s + (r.Assistências || 0), 0))} assistências</em></div>
    <div class="kpi"><p>Minutos</p><strong>${fmtInt(mins)}</strong><em>${state.jogo === "all" ? "soma do período" : "neste jogo"}</em></div>
  `;
}

function renderBars(rows) {
  const metric = state.metric;
  els.barTitle.textContent = `Ranking por ${METRIC_LABEL[metric].toLowerCase()}`;
  const ordered = [...rows].sort((a, b) => (b[metric] ?? 0) - (a[metric] ?? 0));

  if (!ordered.length) {
    els.bars.innerHTML = `<p class="empty">Nenhum jogador neste recorte.</p>`;
    return;
  }

  els.bars.innerHTML = ordered.map((p, i) => {
    const v = p[metric] ?? 0;
    const pct = Math.max(4, (v / 5) * 100);
    const color = POS_COLOR[p.posicao];
    return `<div class="bar-row" data-player="${p.jogador}">
      <span class="rk">${i + 1}</span>
      <span class="nm">${p.jogador}<small>${POS_ABBR[p.posicao]} · ${p.minutos}'</small></span>
      <div class="track"><div class="fill" style="width:${pct}%;background:${color}"></div></div>
      <span class="val">${fmt(v)}</span>
    </div>`;
  }).join("");
}

function renderScatter(rows) {
  const w = 560;
  const h = 380;
  const pad = { l: 40, r: 78, t: 22, b: 40 };
  const x0 = pad.l;
  const y0 = h - pad.b;
  const x1 = w - pad.r;
  const y1 = pad.t;
  const names = rows.map((r) => r.jogador);

  els.scatter.setAttribute("viewBox", `0 0 ${w} ${h}`);

  const sx = (v) => x0 + (v / 5) * (x1 - x0);
  const sy = (v) => y0 - (v / 5) * (y0 - y1);

  const ticks = [0, 1, 2, 3, 4, 5];
  const grid = ticks.map((t) => {
    const x = sx(t);
    const y = sy(t);
    return `
      <line x1="${x}" y1="${y1}" x2="${x}" y2="${y0}" stroke="#1a3d2a" />
      <line x1="${x0}" y1="${y}" x2="${x1}" y2="${y}" stroke="#1a3d2a" />
      <text class="axis-label" x="${x}" y="${y0 + 16}" text-anchor="middle">${t}</text>
      <text class="axis-label" x="${x0 - 8}" y="${y + 4}" text-anchor="end">${t}</text>
    `;
  }).join("");

  const points = rows.map((p) => {
    const x = sx(p.notaOfensiva);
    const y = sy(p.notaDefensiva);
    const right = x < x0 + (x1 - x0) * 0.72;
    return {
      p,
      x,
      y,
      label: shortName(p.jogador, names),
      anchor: right ? "start" : "end",
      lx: right ? x + 10 : x - 10,
      ly: y + 3,
    };
  }).sort((a, b) => a.ly - b.ly);

  for (let i = 1; i < points.length; i++) {
    const gap = points[i].ly - points[i - 1].ly;
    const closeX = Math.abs(points[i].x - points[i - 1].x) < 90;
    if (closeX && gap < 12) points[i].ly = points[i - 1].ly + 12;
  }

  const dots = points.map(({ p, x, y, label, anchor, lx, ly }) => `
    <g class="dot-hit" data-player="${escapeXml(p.jogador)}"
       data-tip="${escapeXml(p.jogador)} · OF ${fmt(p.notaOfensiva)} · DEF ${fmt(p.notaDefensiva)}">
      <circle class="dot" cx="${x}" cy="${y}" r="6.5" fill="${POS_COLOR[p.posicao]}" />
      <text class="dot-label" x="${lx}" y="${ly}" text-anchor="${anchor}">${escapeXml(label)}</text>
    </g>
  `).join("");

  els.scatter.innerHTML = `
    ${grid}
    <line x1="${x0}" y1="${y0}" x2="${x1}" y2="${y0}" stroke="#8aa893" />
    <line x1="${x0}" y1="${y0}" x2="${x0}" y2="${y1}" stroke="#8aa893" />
    <text class="axis-label" x="${(x0 + x1) / 2}" y="${h - 6}" text-anchor="middle">Nota ofensiva</text>
    <text class="axis-label" x="12" y="${(y0 + y1) / 2}" transform="rotate(-90 12 ${(y0 + y1) / 2})" text-anchor="middle">Nota defensiva</text>
    ${dots}
  `;

  const used = [...new Set(rows.map((r) => r.posicao))];
  els.legend.innerHTML = used.map((pos) =>
    `<span><i style="background:${POS_COLOR[pos]}"></i>${POS_ABBR[pos]}</span>`
  ).join("");
}

function renderTable(rows) {
  els.tableHint.textContent = state.jogo === "all"
    ? "Notas do período de 5 jogos, normalizadas contra o elenco"
    : "Notas deste jogo, normalizadas entre os atletas da partida";

  els.tbody.innerHTML = rows.map((p, i) => `
    <tr data-player="${p.jogador}">
      <td class="num">${i + 1}</td>
      <td>
        <span class="player-cell">${p.jogador}
          <small>${p.posicao}</small>
        </span>
      </td>
      <td class="pos-tag">${POS_ABBR[p.posicao]}</td>
      <td class="num">${fmtInt(p.minutos)}</td>
      <td class="num">${fmtInt(p.Golos)}</td>
      <td class="num">${fmtInt(p.Assistências)}</td>
      <td class="num">${fmt(p.notaOfensiva)}</td>
      <td class="num">${fmt(p.notaDefensiva)}</td>
      <td class="num">
        <span class="score-pill" style="color:${scoreColor(p.scoreFinal)}">${fmt(p.scoreFinal)}</span>
      </td>
    </tr>
  `).join("") || `<tr><td colspan="9" class="empty">Nenhum jogador neste recorte.</td></tr>`;
}

function playerRecord(name) {
  return DATA.players.find((p) => p.jogador === name);
}

function openDrawer(name) {
  const period = playerRecord(name);
  const games = DATA.performances
    .filter((p) => p.jogador === name)
    .sort((a, b) => a.data.localeCompare(b.data));
  const current = filteredRows().find((p) => p.jogador === name) || period;
  if (!current && !period) return;

  const p = period || current;
  state.selected = name;
  els.drawer.hidden = false;
  els.drawerPos.textContent = `${p.posicao} · ${p.jogos} jogos · ${p.minutos} min no período`;
  els.drawerName.textContent = p.jogador;
  els.drawerScore.textContent = fmt(p.scoreFinal);

  els.drawerMeters.innerHTML = `
    <div>
      <div class="meter-label"><span>Ofensivo</span><span>${fmt(p.notaOfensiva)}</span></div>
      <div class="meter-bar"><span style="width:${(p.notaOfensiva / 5) * 100}%;background:${POS_COLOR[p.posicao]}"></span></div>
    </div>
    <div>
      <div class="meter-label"><span>Defensivo</span><span>${fmt(p.notaDefensiva)}</span></div>
      <div class="meter-bar"><span style="width:${(p.notaDefensiva / 5) * 100}%;background:${POS_COLOR[p.posicao]}"></span></div>
    </div>
  `;

  const pctPass = p.Passes ? (p["Passes certos"] / p.Passes) * 100 : 0;
  const stats = [
    ["Gols", fmtInt(p.Golos)],
    ["xG", fmt(p.xG, 2)],
    ["Assistências", fmtInt(p.Assistências)],
    ["xA", fmt(p.xA, 2)],
    ["Remates", fmtInt(p.Remates)],
    ["Toques na área", fmtInt(p["Toques na área"])],
    ["Passes certos", `${fmt(pctPass, 0)}%`],
    ["Passes decisivos", fmtInt(p["Passes decisivos"])],
    ["Recuperações", fmtInt(p["Recuperações (total)"])],
    ["Interceções", fmtInt(p.Interceções)],
    ["Duelos certos", fmtInt(p["Duelos certos"])],
    ["Cartões", `${fmtInt(p["Cartões amarelos"])} / ${fmtInt(p["Cartões vermelhos"])}`],
  ];

  els.drawerStats.innerHTML = stats.map(([k, v]) =>
    `<div class="stat"><b>${v}</b><span>${k}</span></div>`
  ).join("");

  els.drawerGames.innerHTML = games.map((g) => `
    <div class="game">
      <div>
        <div>${dateLabel(g.data)} ${g.adversario} (${g.local})</div>
        <small style="color:var(--muted)">${g.minutos}' · ${g.Golos}G ${g.Assistências}A · ${g.resultado}</small>
      </div>
      <span>OF ${fmt(g.scoreOfAjustado, 3)}</span>
      <b>${fmt((g.scoreOfAjustado + g.scoreDefAjustado) / 2, 3)}</b>
    </div>
  `).join("") || "<p class='empty'>Sem atuações.</p>";
}

function closeDrawer() {
  state.selected = null;
  els.drawer.hidden = true;
}

function setMinutos(value) {
  state.minMinutos = Number(value) || 0;
  els.minRange.value = String(state.minMinutos);
  els.minLabel.textContent = String(state.minMinutos);
}

function applyJogo(id) {
  state.jogo = id || "all";
  if (state.jogo !== "all" && state.minMinutos > 90) {
    setMinutos(0);
  }
  const rows = filteredRows();
  if (!rows.length && state.minMinutos > 0) {
    setMinutos(0);
  }
  render();
}

function render() {
  els.metaLine.textContent = `${DATA.meta.janela} · ${DATA.meta.fonte}`;
  renderMatches();
  renderChips();
  const rows = filteredRows();
  renderKpis(rows);
  renderBars(rows);
  renderScatter(rows);
  renderTable(rows);
}

function bind() {
  els.searchInput.addEventListener("input", (e) => {
    state.search = e.target.value;
    render();
  });

  els.minRange.addEventListener("input", (e) => {
    setMinutos(e.target.value);
    render();
  });

  els.sortSelect.addEventListener("change", (e) => {
    state.sort = e.target.value;
    render();
  });

  els.metricSelect.addEventListener("change", (e) => {
    state.metric = e.target.value;
    render();
  });

  els.resetBtn.addEventListener("click", () => {
    state.search = "";
    state.posicoes.clear();
    state.jogo = "all";
    setMinutos(0);
    state.sort = "scoreFinal";
    state.metric = "scoreFinal";
    els.searchInput.value = "";
    els.sortSelect.value = "scoreFinal";
    els.metricSelect.value = "scoreFinal";
    closeDrawer();
    render();
  });

  document.addEventListener("click", (e) => {
    const matchBtn = e.target.closest("[data-jogo]");
    if (matchBtn && els.matchStrip.contains(matchBtn)) {
      e.preventDefault();
      e.stopPropagation();
      applyJogo(matchBtn.getAttribute("data-jogo"));
      return;
    }

    const posBtn = e.target.closest("[data-pos]");
    if (posBtn && els.posChips.contains(posBtn)) {
      e.preventDefault();
      const pos = posBtn.getAttribute("data-pos");
      if (state.posicoes.has(pos)) state.posicoes.delete(pos);
      else state.posicoes.add(pos);
      render();
      return;
    }

    if (e.target.closest("[data-close]")) return;
    const hit = e.target.closest("[data-player]");
    if (hit) openDrawer(hit.getAttribute("data-player"));
  });

  els.drawer.addEventListener("click", (e) => {
    if (e.target.closest("[data-close]")) closeDrawer();
  });

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") closeDrawer();
  });

  els.scatter.addEventListener("pointermove", (e) => {
    const dot = e.target.closest("[data-tip]");
    if (!dot) {
      els.tooltip.hidden = true;
      return;
    }
    els.tooltip.hidden = false;
    els.tooltip.textContent = dot.dataset.tip;
    els.tooltip.style.left = `${e.clientX + 12}px`;
    els.tooltip.style.top = `${e.clientY + 12}px`;
  });

  els.scatter.addEventListener("pointerleave", () => {
    els.tooltip.hidden = true;
  });

  document.querySelectorAll("th[data-sort]").forEach((th) => {
    th.style.cursor = "pointer";
    th.addEventListener("click", () => {
      state.sort = th.dataset.sort;
      els.sortSelect.value = state.sort;
      render();
    });
  });
}

function boot() {
  if (!window.DASHBOARD_DATA) {
    document.body.insertAdjacentHTML(
      "afterbegin",
      '<p class="empty">Não foi possível carregar os dados do dashboard.</p>'
    );
    return;
  }
  bind();
  render();
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", boot);
} else {
  boot();
}
