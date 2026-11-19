# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
Añade recetas a recetas/recetas.tsv y descartes a recetas/raw/descartados.tsv a partir
de un lote en JSON Lines, validándolo todo antes. Si hay algún error, no escribe nada.

Uso:
    uv run scripts/agregar.py lote.jsonl --prueba   # solo valida
    uv run scripts/agregar.py lote.jsonl            # valida y escribe
    cat lote.jsonl | uv run scripts/agregar.py -

Una receta por línea:

    {"tipo": "receta", "enlace": "...", "plataforma": "youtube", "autor": "@canal",
     "nombre": "Pularda rellena", "plato": "principal", "fiestas": ["navidad"],
     "estilo": "tradicional", "cocina": "catalana",
     "descripcion": "El asado de Navidad de toda la vida, relleno de frutos secos.",
     "ingredientes": ["pularda", "ciruelas pasas", "piñones", "manzana"],
     "pasos": ["Rellenar la pularda", "Asar al horno regándola con su jugo"],
     "dificultad": "media", "tiempo_min": 180, "se_prepara_antes": "si",
     "vegetariana": "no", "vegana": "no", "sin_gluten": "",
     "etiquetas": ["ave", "horno", "lucido", "para-muchos"]}

    {"tipo": "descartado", "enlace": "...", "motivo": "no es una receta"}

- Obligatorios en las recetas: enlace, plataforma, autor, nombre, plato, fiestas, estilo.
- ingredientes, pasos, fiestas y etiquetas pueden ser listas o texto separado por ";".
- El id se genera a partir del nombre si no viene; si se repite, se añade -2, -3...
- Los valores controlados pasan a minúsculas y sin acentos.
- Los enlaces que ya están en la tabla o en descartados se saltan con un aviso.
"""

import argparse
import json
import re
import sys
from pathlib import Path

from comun import DESCARTADOS, TABLA, anadir_filas, controlado, leer_tsv, limpiar, slug

LISTAS = {"ingredientes", "pasos", "fiestas", "etiquetas"}
CONTROLADOS = {"plato", "estilo", "cocina", "plataforma", "dificultad", "se_prepara_antes",
               "vegetariana", "vegana", "sin_gluten", "fiestas", "etiquetas"}
OBLIGATORIOS = ("enlace", "plataforma", "autor", "nombre", "plato", "fiestas", "estilo")
SI_NO = {"", "si", "no", "adaptable"}
PERMITIDOS = {
    "plato": {"aperitivo", "entrante", "sopa", "principal", "guarnicion", "postre", "dulce", "bebida"},
    "estilo": {"tradicional", "moderno"},
    "plataforma": {"youtube", "instagram", "tiktok"},
    "dificultad": {"", "facil", "media", "dificil"},
    "se_prepara_antes": {"", "si", "no"},
    "vegetariana": SI_NO,
    "vegana": SI_NO,
    "sin_gluten": SI_NO,
}
FIESTAS = {"nochebuena", "navidad", "san-esteban", "nochevieja", "reyes"}
ETIQUETAS = {
    "carne", "ave", "cerdo", "cordero", "ternera", "caza", "pescado", "marisco", "verdura", "pasta",
    "arroz", "queso", "chocolate",
    "horno", "sin-horno", "olla", "fritura", "sin-coccion",
    "para-muchos", "aprovechamiento", "economico", "rapido", "ligero", "lucido", "ninos",
    "incompleta",
}


def construir(item: dict, cabecera: list[str], ids: set[str]) -> tuple[dict, list[str]]:
    errores = []
    desconocidos = set(item) - set(cabecera) - {"tipo"}
    if desconocidos:
        errores.append(f"campos desconocidos: {', '.join(sorted(desconocidos))}")

    fila = {}
    for columna in cabecera:
        valor = item.get(columna)
        if columna in LISTAS:
            partes = valor if isinstance(valor, list) else str(valor or "").split(";")
            partes = [limpiar(p).replace(";", ",") for p in partes]
            if columna in CONTROLADOS:
                partes = [controlado(p).replace(" ", "-") for p in partes]
            fila[columna] = "; ".join(p for p in partes if p)
        else:
            fila[columna] = limpiar(valor)
            if columna in CONTROLADOS:
                fila[columna] = controlado(fila[columna])

    for columna in OBLIGATORIOS:
        if not fila[columna]:
            errores.append(f"falta {columna}")
    for columna, permitidos in PERMITIDOS.items():
        if fila[columna] not in permitidos and not (columna in OBLIGATORIOS and not fila[columna]):
            errores.append(f"{columna}={fila[columna]!r} no vale ({', '.join(sorted(p for p in permitidos if p))})")
    for columna, permitidos in (("fiestas", FIESTAS), ("etiquetas", ETIQUETAS)):
        malas = [v for v in fila[columna].split("; ") if v and v not in permitidos]
        if malas:
            errores.append(f"{columna}: {', '.join(malas)} no vale ({', '.join(sorted(permitidos))})")
    if fila["tiempo_min"] and not fila["tiempo_min"].isdigit():
        errores.append(f"tiempo_min={fila['tiempo_min']!r} tiene que ser un número de minutos")
    if fila["vegana"] == "si" and fila["vegetariana"] not in ("si", ""):
        errores.append("vegana=si pero vegetariana no es si")
    if not re.match(r"^https://", fila["enlace"]):
        errores.append(f"enlace={fila['enlace']!r} no es una URL")

    base = slug(fila["id"] or fila["nombre"])
    id_, n = base, 2
    while id_ in ids:
        id_, n = f"{base}-{n}", n + 1
    fila["id"] = id_
    return fila, errores


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("lote", help="archivo JSON Lines, o - para la entrada estándar")
    parser.add_argument("--prueba", action="store_true", help="solo validar, sin escribir")
    args = parser.parse_args()

    texto = sys.stdin.read() if args.lote == "-" else Path(args.lote).read_text(encoding="utf-8")
    cabecera, existentes = leer_tsv(TABLA)
    cabecera_d, descartes = leer_tsv(DESCARTADOS)
    hechos = {f["enlace"] for f in existentes} | {f["enlace"] for f in descartes}
    ids = {f["id"] for f in existentes}

    recetas, descartados, errores, saltados = [], [], [], 0
    for n, linea in enumerate(texto.splitlines(), 1):
        if not linea.strip():
            continue
        try:
            item = json.loads(linea)
        except json.JSONDecodeError as error:
            errores.append(f"línea {n}: JSON no válido ({error})")
            continue

        enlace = limpiar(item.get("enlace"))
        if enlace in hechos:
            saltados += 1
            print(f"línea {n}: {enlace} ya procesado, se salta", file=sys.stderr)
            continue

        if item.get("tipo") == "receta":
            fila, errs = construir(item, cabecera, ids)
            errores += [f"línea {n} ({fila.get('nombre') or enlace}): {e}" for e in errs]
            if not errs:
                recetas.append(fila)
                ids.add(fila["id"])
                hechos.add(enlace)
        elif item.get("tipo") == "descartado":
            motivo = limpiar(item.get("motivo"))
            if not enlace or not motivo:
                errores.append(f"línea {n}: un descartado necesita enlace y motivo")
                continue
            descartados.append({"enlace": enlace, "motivo": motivo})
            hechos.add(enlace)
        else:
            errores.append(f'línea {n}: tipo tiene que ser "receta" o "descartado"')

    if errores:
        print("Errores (no se ha escrito nada):", file=sys.stderr)
        for error in errores:
            print(f"  {error}", file=sys.stderr)
        sys.exit(1)

    resumen = f"{len(recetas)} recetas, {len(descartados)} descartados" + (f", {saltados} ya procesados" if saltados else "")
    if args.prueba:
        print(f"Validación correcta: {resumen}. No se ha escrito nada (--prueba).", file=sys.stderr)
        return
    if recetas:
        anadir_filas(TABLA, cabecera, recetas)
    if descartados:
        anadir_filas(DESCARTADOS, cabecera_d, descartados)
    print(f"Añadido: {resumen}.", file=sys.stderr)
    for fila in recetas:
        print(f"  + {fila['id']}: {fila['nombre']}", file=sys.stderr)


if __name__ == "__main__":
    main()
