# /// script
# requires-python = ">=3.11"
# dependencies = ["yt-dlp[default]"]
# ///
"""
Recoge el texto que la extensión no ve y lo guarda en recetas/raw/extra/<plataforma>/<id>.json,
sin tocar la captura. No usa IA: solo recopila.

  - YouTube: descripción completa y subtítulos (del autor o automáticos, en el idioma original).

En Instagram y TikTok la extensión ya lee la descripción, que es donde suele estar la receta.

Uso:
    uv run scripts/completar.py                # las capturas pendientes sin texto extra
    uv run scripts/completar.py --limite 5
    uv run scripts/completar.py --id <id>      # una concreta (vuelve a recogerla)
    uv run scripts/completar.py --cookies      # usa la sesión de Brave si YouTube pide verificar
"""

import argparse
import html
import json
import re
import sys
import time
from datetime import datetime

from comun import EXTRA, capturas, enlaces_procesados

IDIOMAS = ["es", "ca", "en"]
MAX_SUBTITULOS = 15000


def log(texto: str) -> None:
    print(texto, file=sys.stderr, flush=True)


def vtt_a_texto(vtt: str) -> str:
    lineas = []
    for linea in vtt.splitlines():
        linea = linea.strip()
        if not linea or linea == "WEBVTT" or "-->" in linea or linea.isdigit() or linea.startswith(("Kind:", "Language:", "NOTE")):
            continue
        linea = html.unescape(re.sub(r"<[^>]+>", "", linea)).strip()
        if linea and (not lineas or lineas[-1] != linea):
            lineas.append(linea)
    return " ".join(lineas)


def youtube(id_: str, cookies: bool) -> dict:
    import yt_dlp

    opciones = {"skip_download": True, "quiet": True, "no_warnings": True, "ignore_no_formats_error": True}
    if cookies:
        opciones["cookiesfrombrowser"] = ("brave",)

    with yt_dlp.YoutubeDL(opciones) as ydl:
        info = ydl.extract_info(f"https://www.youtube.com/watch?v={id_}", download=False)
        resultado = {"descripcion": info.get("description") or "", "subtitulos": None}

        propios = info.get("subtitles") or {}
        automaticos = info.get("automatic_captions") or {}
        original = info.get("language") or ""
        candidatos = [("autor", propios, l) for l in [original, *IDIOMAS] if l and l in propios]
        candidatos += [("automaticos", automaticos, l) for l in automaticos if l.endswith("-orig")]
        candidatos += [("automaticos", automaticos, l) for l in [original, *IDIOMAS] if l and l in automaticos]

        for tipo, tabla, idioma in candidatos:
            vtt = next((f for f in tabla[idioma] if f.get("ext") == "vtt"), None)
            if not vtt:
                continue
            texto = vtt_a_texto(ydl.urlopen(vtt["url"]).read().decode("utf-8", "replace"))
            if texto:
                resultado["subtitulos"] = {"idioma": idioma, "tipo": tipo, "texto": texto[:MAX_SUBTITULOS]}
                break
    return resultado


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--limite", type=int)
    parser.add_argument("--id", help="recoger (otra vez) una captura concreta")
    parser.add_argument("--cookies", action="store_true", help="usar las cookies de Brave")
    args = parser.parse_args()

    hechos = enlaces_procesados()
    if args.id:
        lista = [c for c in capturas() if c["id"] == args.id]
    else:
        lista = [c for c in capturas() if c["plataforma"] == "youtube" and not c["extra"] and c["url"] not in hechos]
    if args.limite:
        lista = lista[: args.limite]
    if not lista:
        return log("Nada que completar.")

    errores = 0
    for n, captura in enumerate(lista, 1):
        if captura["plataforma"] != "youtube":
            log(f"[{n}/{len(lista)}] {captura['id']}: en {captura['plataforma']} no hay nada más que recoger")
            continue
        try:
            datos = youtube(captura["id"], args.cookies)
        except Exception as error:  # yt-dlp lanza muchos tipos distintos
            errores += 1
            log(f"[{n}/{len(lista)}] {captura['id']}: ERROR {str(error).splitlines()[0][:150]}")
            continue

        datos["obtenido_en"] = datetime.now().astimezone().isoformat(timespec="seconds")
        ruta = EXTRA / captura["plataforma"] / f"{captura['id']}.json"
        ruta.parent.mkdir(parents=True, exist_ok=True)
        ruta.write_text(json.dumps(datos, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        subs = datos["subtitulos"]
        log(f"[{n}/{len(lista)}] {captura['id']}: descripción {len(datos['descripcion'])} car., "
            + (f"subtítulos {subs['tipo']} ({subs['idioma']}) {len(subs['texto'])} car." if subs else "sin subtítulos"))
        time.sleep(1)

    if errores:
        log(f"{errores} con error. Si YouTube pide verificar que no eres un bot, vuelve a probar con --cookies.")


if __name__ == "__main__":
    main()
