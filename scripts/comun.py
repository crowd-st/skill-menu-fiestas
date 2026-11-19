"""Rutas y utilidades compartidas por los scripts."""

from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
TABLA = RAIZ / "recetas" / "recetas.tsv"
RAW = RAIZ / "recetas" / "raw"
EXTRA = RAW / "extra"
DESCARTADOS = RAW / "descartados.tsv"
PLATAFORMAS = ("youtube", "instagram", "tiktok")


def sin_acentos(texto: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", texto) if not unicodedata.combining(c))


def limpiar(valor) -> str:
    if valor is None:
        return ""
    texto = re.sub(r"[\t\r\n]+", " ", str(valor))
    return re.sub(r" {2,}", " ", texto).strip()


def controlado(valor: str) -> str:
    """Valores controlados: minúsculas, sin acentos, sin ñ."""
    return sin_acentos(valor).lower().strip()


def slug(texto: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", controlado(texto)).strip("-")
    return s[:60].rstrip("-") or "receta"


def leer_tsv(ruta: Path) -> tuple[list[str], list[dict]]:
    lineas = ruta.read_text(encoding="utf-8").splitlines()
    cabecera = lineas[0].split("\t")
    filas = [dict(zip(cabecera, l.split("\t"))) for l in lineas[1:] if l.strip()]
    return cabecera, filas


def anadir_filas(ruta: Path, cabecera: list[str], filas: list[dict]) -> None:
    texto = ruta.read_text(encoding="utf-8")
    if texto and not texto.endswith("\n"):
        texto += "\n"
    texto += "".join("\t".join(f.get(c, "") for c in cabecera) + "\n" for f in filas)
    ruta.write_text(texto, encoding="utf-8")


def enlaces_procesados() -> set[str]:
    """Enlaces que ya están en la tabla o en descartados."""
    hechos = set()
    for ruta, columna in ((TABLA, "enlace"), (DESCARTADOS, "enlace")):
        if ruta.exists():
            hechos |= {f[columna].strip() for f in leer_tsv(ruta)[1] if f.get(columna)}
    return hechos


def capturas():
    """Todas las capturas, de todas las plataformas, con su texto extra si lo hay."""
    for plataforma in PLATAFORMAS:
        for ruta in sorted((RAW / plataforma).glob("*.json")):
            captura = json.loads(ruta.read_text(encoding="utf-8"))
            extra_ruta = EXTRA / plataforma / ruta.name
            captura["extra"] = json.loads(extra_ruta.read_text(encoding="utf-8")) if extra_ruta.exists() else {}
            yield captura
