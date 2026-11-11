# recetas/

La lista de recetas: las capturas en bruto que llegan de la extensión y la tabla revisada de la que sale el catálogo de la skill.

```
recetas/
├── recetas.tsv            La tabla de recetas (fuente de verdad)
└── raw/                   Capturas en bruto, una por vídeo
    ├── descartados.tsv    Capturas revisadas que no son recetas
    ├── instagram/         Un JSON por reel
    ├── youtube/           Un JSON por short
    └── tiktok/            Un JSON por vídeo
```

## La tabla: `recetas.tsv`

Una receta por línea, columnas separadas por tabulador. Dentro de una celda, las listas se separan con `;`. Ninguna celda lleva tabuladores ni saltos de línea.

| Columna | Valores |
|---|---|
| `id` | identificador corto en minúsculas con guiones, p. ej. `cordero-asado-al-horno` |
| `nombre` | nombre del plato |
| `plato` | `aperitivo`, `entrante`, `principal`, `guarnicion`, `postre` o `bebida` |
| `fiestas` | días en los que encaja, separados por `;`: `nochebuena`, `navidad`, `san-esteban`, `nochevieja`, `reyes` |
| `descripcion` | una frase que explica qué es el plato |
| `ingredientes` | lista separada por `;`, **sin cantidades** |
| `pasos` | pasos resumidos, separados por `;` |
| `enlace` | URL del vídeo original |
| `plataforma` | `instagram`, `youtube` o `tiktok` |
| `autor` | usuario o canal que ha publicado el vídeo |
| `dificultad` | `facil`, `media` o `dificil` |
| `tiempo_min` | tiempo total aproximado en minutos |
| `se_prepara_antes` | `si` o `no`: si se puede dejar hecho el día anterior |
| `vegetariana` | `si`, `no` o `adaptable` |
| `sin_gluten` | `si`, `no` o `adaptable` |
| `etiquetas` | otros filtros separados por `;`: `tradicional`, `marisco`, `pescado`, `carne`, `horno`, `sin-horno`, `ninos`, `economico`, `aprovechamiento`, `vegana`, `incompleta`... |

Reglas:

- Todo en castellano, venga el vídeo en el idioma que venga.
- Si un dato no sale en la fuente, la celda se queda vacía. No se inventan tiempos ni ingredientes.
- `vegetariana` y `sin_gluten` solo se marcan `si` cuando la fuente lo deja claro.
- `incompleta` marca las recetas de las que solo tenemos el nombre y el enlace, porque el detalle está en el vídeo.

## Las capturas: `raw/<plataforma>/<id>.json`

Un archivo por vídeo, escrito por la extensión. El nombre es el identificador del vídeo en su plataforma, así un mismo vídeo no se captura dos veces.

```json
{
  "id": "DAbC123xYz",
  "plataforma": "instagram",
  "url": "https://www.instagram.com/reel/DAbC123xYz/",
  "autor": "usuario",
  "titulo": "",
  "descripcion": "Texto que acompaña al vídeo",
  "fecha_publicacion": "2026-11-02",
  "capturado_en": "2026-11-11T16:20:00+01:00",
  "nota": "Para Nochevieja, como entrante"
}
```

| Campo | Contenido |
|---|---|
| `id` | identificador del vídeo en la plataforma |
| `plataforma` | `instagram`, `youtube` o `tiktok` |
| `url` | URL canónica del vídeo, sin parámetros de seguimiento |
| `autor` | usuario o canal |
| `titulo` | título, si la plataforma lo tiene |
| `descripcion` | texto que acompaña al vídeo |
| `fecha_publicacion` | fecha del vídeo, si se puede leer |
| `capturado_en` | cuándo se ha capturado |
| `nota` | comentario opcional de quien lo captura |

Las capturas no se editan a mano.

## Descartados: `raw/descartados.tsv`

Las capturas revisadas que no son recetas se apuntan aquí, con `enlace` y `motivo`, para que no vuelvan a salir como pendientes.

## De la captura a la tabla

1. La extensión escribe la captura en `raw/<plataforma>/`.
2. Se listan las capturas pendientes: las que no están ni en la tabla ni en descartados.
3. Cada una se clasifica: si es una receta, pasa a `recetas.tsv`; si no, a `descartados.tsv`.
4. Las `incompleta` se completan con lo que se dice en el vídeo.
5. Se regenera el catálogo de la skill.

Los scripts de cada paso están definidos en [`scripts/`](../scripts/README.md).
