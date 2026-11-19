# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
Genera el catálogo de la skill a partir de recetas/recetas.tsv:

  skill/menu-fiestas/catalogo.md   el catálogo, junto al SKILL.md (skill de Claude)
  skill/prompt.md                  instrucciones y catálogo en un solo archivo, para
                                   pegarlo en cualquier IA

Uso:
    uv run scripts/generar.py
    uv run scripts/generar.py --comprobar   # falla si los archivos no están al día
"""

import argparse
import re
import sys

from comun import RAIZ, TABLA, leer_tsv

SKILL = RAIZ / "skill" / "menu-fiestas" / "SKILL.md"
CATALOGO = RAIZ / "skill" / "menu-fiestas" / "catalogo.md"
PROMPT = RAIZ / "skill" / "prompt.md"

SECCIONES = [
    ("aperitivo", "Aperitivos"),
    ("entrante", "Entrantes"),
    ("sopa", "Sopas"),
    ("principal", "Principales"),
    ("guarnicion", "Guarniciones"),
    ("postre", "Postres"),
    ("dulce", "Dulces navideños"),
    ("bebida", "Bebidas"),
]
DIAS = {
    "nochebuena": "Nochebuena",
    "navidad": "Navidad",
    "san-esteban": "San Esteban",
    "nochevieja": "Nochevieja",
    "reyes": "Reyes",
}
SI_NO = {"si": "sí", "no": "no", "adaptable": "adaptable", "": "sin confirmar"}
DIFICULTAD = {"facil": "fácil", "media": "media", "dificil": "difícil"}
COCINA = {"espanola": "española", "madrilena": "madrileña"}
PLATAFORMA = {"youtube": "YouTube", "instagram": "Instagram", "tiktok": "TikTok"}


def lista(valor: str) -> list[str]:
    return [v.strip() for v in valor.split(";") if v.strip()]


def autor(fila: dict) -> str:
    nombre = fila["autor"]
    return nombre if nombre.startswith("@") else f"@{nombre}"


def ficha(fila: dict) -> str:
    datos = [
        f"días: {', '.join(DIAS[d] for d in lista(fila['fiestas']))}",
        f"estilo: {fila['estilo']}",
    ]
    if fila["cocina"]:
        datos.append(f"cocina: {COCINA.get(fila['cocina'], fila['cocina'])}")
    if fila["dificultad"]:
        datos.append(f"dificultad: {DIFICULTAD[fila['dificultad']]}")
    if fila["tiempo_min"]:
        datos.append(f"tiempo: {fila['tiempo_min']} min")
    if fila["se_prepara_antes"] == "si":
        datos.append("se prepara antes")
    dietas = [
        f"vegetariana: {SI_NO[fila['vegetariana']]}",
        f"vegana: {SI_NO[fila['vegana']]}",
        f"sin gluten: {SI_NO[fila['sin_gluten']]}",
    ]

    lineas = [
        f"#### {fila['nombre']}",
        " · ".join(datos),
        " · ".join(dietas),
    ]
    if fila["etiquetas"]:
        lineas.append(f"etiquetas: {', '.join(lista(fila['etiquetas']))}")
    lineas.append(fila["descripcion"])
    if fila["ingredientes"]:
        lineas.append(f"Ingredientes: {', '.join(lista(fila['ingredientes']))}.")
    pasos = lista(fila["pasos"])
    if pasos:
        lineas.append("Pasos: " + " ".join(f"{n}) {p.rstrip('.')}." for n, p in enumerate(pasos, 1)))
    lineas.append(f"Vídeo: {fila['enlace']} ({autor(fila)} en {PLATAFORMA[fila['plataforma']]})")
    return "\n".join(lineas)


def catalogo(filas: list[dict]) -> str:
    partes = [
        "# Catálogo de recetas",
        "",
        f"{len(filas)} recetas en vídeo corto, elegidas para las fiestas de Navidad. "
        "Cada una tiene los días en los que encaja, el estilo, las dietas y el enlace al vídeo de su autor. "
        "Este archivo se genera con `scripts/generar.py`: no se edita a mano.",
    ]
    for plato, titulo in SECCIONES:
        grupo = sorted((f for f in filas if f["plato"] == plato), key=lambda f: f["nombre"])
        if not grupo:
            continue
        partes += ["", f"## {titulo}", ""]
        partes.append("\n\n".join(ficha(f) for f in grupo))
    return "\n".join(partes) + "\n"


def prompt(instrucciones: str, texto_catalogo: str) -> str:
    cuerpo = re.sub(r"\A---\n.*?\n---\n", "", instrucciones, flags=re.S).strip()
    cuerpo = cuerpo.replace(
        "El catálogo está en `catalogo.md`.",
        "El catálogo está al final de este mensaje.",
    )
    return (
        "<!-- Prompt para pegar en cualquier IA. Se genera con scripts/generar.py: no se edita a mano. -->\n\n"
        f"{cuerpo}\n\n---\n\n{texto_catalogo.replace('# Catálogo de recetas', '# Catálogo', 1)}\n"
        "---\n\nEmpieza ahora: saluda en una línea y haz la primera pregunta.\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--comprobar", action="store_true", help="no escribe; falla si no están al día")
    args = parser.parse_args()

    _, filas = leer_tsv(TABLA)
    texto_catalogo = catalogo(filas)
    texto_prompt = prompt(SKILL.read_text(encoding="utf-8"), texto_catalogo)

    salidas = {CATALOGO: texto_catalogo, PROMPT: texto_prompt}
    if args.comprobar:
        viejos = [r for r, t in salidas.items() if not r.exists() or r.read_text(encoding="utf-8") != t]
        if viejos:
            sys.exit("No están al día: " + ", ".join(str(r.relative_to(RAIZ)) for r in viejos))
        print("Catálogo y prompt al día.")
        return

    for ruta, texto in salidas.items():
        ruta.write_text(texto, encoding="utf-8")
        print(f"{ruta.relative_to(RAIZ)}: {len(texto):,} caracteres (~{len(texto) // 4:,} tokens)", file=sys.stderr)
    print(f"{len(filas)} recetas.", file=sys.stderr)


if __name__ == "__main__":
    main()
