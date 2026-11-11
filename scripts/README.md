# scripts/

Scripts para pasar las capturas a la tabla y generar el catálogo de la skill. Todavía no hay ninguno: esta es la lista prevista.

| Script | Qué hace |
|---|---|
| `pendientes.py` | Lista las capturas de `recetas/raw/` que no están ni en la tabla ni en descartados |
| `agregar.py` | Añade recetas y descartados a partir de un lote, validando campos y valores permitidos |
| `actualizar.py` | Modifica recetas existentes por su `id`, con la misma validación |
| `completar.py` | Recoge texto extra (subtítulos, comentarios del autor) para las recetas `incompleta` |
| `generar.py` | Genera `skill/menu-fiestas/catalogo.md` y `skill/prompt.md` a partir de `recetas/recetas.tsv` |

Criterios:

- Se ejecutan con [uv](https://docs.astral.sh/uv/) (`uv run scripts/<script>.py`) y declaran sus dependencias en el propio archivo.
- `agregar.py` y `actualizar.py` no escriben nada si hay algún error, y aceptan `--dry-run`.
- La tabla se escribe siempre a través de ellos, nunca a mano.
- `generar.py` es el único que escribe en `skill/`.
