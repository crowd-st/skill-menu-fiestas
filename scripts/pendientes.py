# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
Lista las capturas que todavía no se han procesado (no están en recetas.tsv ni en
descartados.tsv), en JSON Lines: una por línea, con todo el texto disponible.

Uso:
    uv run scripts/pendientes.py                   # todas
    uv run scripts/pendientes.py --contar          # solo cuántas hay por plataforma
    uv run scripts/pendientes.py --plataforma youtube
    uv run scripts/pendientes.py --limite 10 --desde 10

Cada línea tiene:
    enlace, plataforma, autor   lo que va a esas columnas de la tabla
    sin_extra                   true si falta pasar completar.py (en YouTube solo hay el título)
    texto                       título, descripción, nota y subtítulos, para sacar la receta
"""

import argparse
import json
import sys
from collections import Counter

from comun import PLATAFORMAS, capturas, enlaces_procesados


def texto_de(captura: dict) -> str:
    extra = captura["extra"]
    partes = [
        ("Título", captura.get("titulo")),
        ("Descripción", extra.get("descripcion") or captura.get("descripcion")),
        ("Nota", captura.get("nota")),
        ("Subtítulos", (extra.get("subtitulos") or {}).get("texto")),
    ]
    return "\n\n".join(f"{nombre}: {valor.strip()}" for nombre, valor in partes if valor and valor.strip())


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--plataforma", choices=PLATAFORMAS)
    parser.add_argument("--contar", action="store_true", help="solo el recuento por plataforma")
    parser.add_argument("--limite", type=int)
    parser.add_argument("--desde", type=int, default=0)
    args = parser.parse_args()

    hechos = enlaces_procesados()
    pendientes = [
        c for c in capturas()
        if c["url"] not in hechos and (not args.plataforma or c["plataforma"] == args.plataforma)
    ]

    if args.contar:
        recuento = Counter(c["plataforma"] for c in pendientes)
        for plataforma in PLATAFORMAS:
            if recuento[plataforma]:
                sin_extra = sum(1 for c in pendientes if c["plataforma"] == plataforma and not c["extra"])
                print(f"{plataforma}\t{recuento[plataforma]}" + (f"\t({sin_extra} sin completar)" if sin_extra else ""))
        print(f"total\t{len(pendientes)}")
        return

    seleccion = pendientes[args.desde:]
    if args.limite:
        seleccion = seleccion[: args.limite]
    for c in seleccion:
        print(json.dumps({
            "enlace": c["url"],
            "plataforma": c["plataforma"],
            "autor": c.get("autor", ""),
            "sin_extra": not c["extra"],
            "texto": texto_de(c),
        }, ensure_ascii=False))
    print(f"{len(seleccion)} de {len(pendientes)} pendientes", file=sys.stderr)


if __name__ == "__main__":
    main()
