# scripts/

Scripts para pasar las capturas a la tabla y generar el catálogo de la skill. Se ejecutan con [uv](https://docs.astral.sh/uv/) desde la raíz del repo y declaran sus dependencias en el propio archivo.

| Script | Qué hace |
|---|---|
| `completar.py` | Recoge la descripción completa y los subtítulos de los vídeos de YouTube en `recetas/raw/extra/` |
| `pendientes.py` | Lista las capturas que no están ni en la tabla ni en descartados, con todo su texto |
| `agregar.py` | Añade recetas y descartados a partir de un lote, validando columnas y valores permitidos |
| `generar.py` | *(pendiente)* Genera `skill/menu-fiestas/catalogo.md` y `skill/prompt.md` a partir de la tabla |

`comun.py` tiene las rutas y utilidades que comparten.

## Procesar las capturas

```bash
uv run scripts/completar.py                     # texto extra de los vídeos de YouTube
uv run scripts/pendientes.py --contar           # cuántas quedan
uv run scripts/pendientes.py --limite 15        # las 15 primeras, en JSON Lines
uv run scripts/agregar.py lote.jsonl --prueba   # valida un lote
uv run scripts/agregar.py lote.jsonl            # lo añade a la tabla
```

Cada captura se lee y se clasifica:

- **Es una receta que encaja en Navidad**: una línea `"tipo": "receta"` con todas las columnas de la tabla. Los criterios de cada columna (qué día, qué plato, estilo, dietas, etiquetas) están en [`recetas/README.md`](../recetas/README.md).
- **No lo es** (no es una receta, es de verano, el propio autor no la recomienda...): una línea `"tipo": "descartado"` con el `motivo`.

El formato exacto del lote está en la cabecera de `agregar.py`. Si hay un solo error, no escribe nada.

La tabla se escribe siempre con `agregar.py`, nunca a mano.
