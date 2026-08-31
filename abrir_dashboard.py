"""Gera o HTML único e abre no navegador padrão."""
from pathlib import Path
import os
import webbrowser

ROOT = Path(__file__).resolve().parent
DASH = ROOT / "dashboard"

css = (DASH / "styles.css").read_text(encoding="utf-8")
app = (DASH / "app.js").read_text(encoding="utf-8")
data = (DASH / "data.js").read_text(encoding="utf-8")
template = (DASH / "index.html").read_text(encoding="utf-8")

html = template
html = html.replace('<link rel="stylesheet" href="styles.css" />', f"<style>\n{css}\n</style>")
html = html.replace(
    '<script src="data.js"></script>\n  <script src="app.js"></script>',
    f"<script>\n{data}\n{app}\n</script>",
)

out = ROOT / "palmeiras_scores.html"
out.write_text(html, encoding="utf-8")
print(f"Arquivo: {out}")

uri = out.resolve().as_uri()
opened = webbrowser.open(uri)
print(f"Navegador: {uri} (open={opened})")
try:
    os.startfile(out)  # Windows: abre com o app padrão
    print("os.startfile ok")
except OSError as exc:
    print("os.startfile falhou:", exc)
