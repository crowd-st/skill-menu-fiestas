# recetas/

La lista de recetas: las capturas en bruto que llegan de la extensión y la tabla revisada de la que sale el catálogo de la skill.

```
recetas/
├── recetas.tsv            La tabla de recetas (fuente de verdad)
└── raw/                   Capturas en bruto, una por vídeo
    ├── descartados.tsv    Capturas revisadas que no son recetas
    ├── instagram/         Un JSON por reel
    ├── youtube/           Un JSON por short
    ├── tiktok/            Un JSON por vídeo
    └── extra/             Texto extra de cada vídeo (descripción completa, subtítulos)
```

## La tabla: `recetas.tsv`

La tabla existe para montar menús de Navidad: cada columna es una pista que la skill usa para decidir qué plato va en qué día, en qué lugar del menú y para quién.

Una receta por línea, columnas separadas por tabulador. Dentro de una celda, las listas se separan con `;`. Ninguna celda lleva tabuladores ni saltos de línea.

| Columna | Valores |
|---|---|
| `id` | identificador corto en minúsculas con guiones, p. ej. `pularda-rellena` |
| `nombre` | nombre del plato |
| `plato` | lugar en el menú: `aperitivo`, `entrante`, `sopa`, `principal`, `guarnicion`, `postre`, `dulce` o `bebida` |
| `fiestas` | días en los que encaja, separados por `;`: `nochebuena`, `navidad`, `san-esteban`, `nochevieja`, `reyes` |
| `estilo` | `tradicional` (el plato de siempre) o `moderno` (una versión nueva, una fusión o un plato que no es típico de estas fechas) |
| `cocina` | origen: `catalana`, `vasca`, `andaluza`, `gallega`, `madrilena`, `espanola`, `italiana`, `francesa`, `internacional`... |
| `descripcion` | una frase que explica qué es el plato y por qué apetece en estas fechas |
| `ingredientes` | ingredientes principales separados por `;`, **sin cantidades** |
| `pasos` | pasos resumidos, separados por `;` |
| `enlace` | URL del vídeo original |
| `plataforma` | `instagram`, `youtube` o `tiktok` |
| `autor` | usuario o canal que ha publicado el vídeo |
| `dificultad` | `facil`, `media` o `dificil` |
| `tiempo_min` | tiempo total aproximado en minutos, si sale en la fuente |
| `se_prepara_antes` | `si` si se puede dejar hecho el día anterior (o buena parte), `no` si es de última hora |
| `vegetariana` | `si`, `no` o `adaptable` |
| `vegana` | `si`, `no` o `adaptable` |
| `sin_gluten` | `si`, `no` o `adaptable` |
| `etiquetas` | otros filtros separados por `;` (ver abajo) |

### Qué día va cada plato (`fiestas`)

Un plato puede ir en varios días. Criterios:

| Día | Qué encaja |
|---|---|
| `nochebuena` | Cena del 24: pescado y marisco, sopas y cremas, platos lucidos pero que se pueden adelantar. Bacalao, besugo, langostinos. |
| `navidad` | Comida del 25: el plato grande del año. Escudella o sopa de galets, carn d'olla, cocido, asados (pularda, capón, cordero, pavo), rellenos. |
| `san-esteban` | Comida del 26: aprovechamiento de lo del día anterior. Canelones, croquetas, ropa vieja. |
| `nochevieja` | Cena del 31: picoteo y platos vistosos. Canapés, marisco, entrantes fríos, un principal elegante. |
| `reyes` | Noche del 5 y mañana del 6: roscón, chocolate y una cena sencilla. |

Los dulces navideños (turrones, polvorones, mazapanes) van en todos los días en los que se suelen poner: casi siempre `nochebuena; navidad; nochevieja`.

### Etiquetas

| Grupo | Etiquetas |
|---|---|
| Ingrediente principal | `carne`, `ave`, `cerdo`, `cordero`, `ternera`, `caza`, `pescado`, `marisco`, `verdura`, `pasta`, `arroz`, `queso`, `chocolate` |
| Cocción | `horno`, `sin-horno`, `olla`, `fritura`, `sin-coccion` |
| Ocasión | `para-muchos`, `aprovechamiento`, `economico`, `rapido`, `ligero`, `lucido`, `ninos` |
| Estado | `incompleta`: solo tenemos el nombre y el enlace, el detalle está en el vídeo |

### Reglas

- Todo en castellano, venga el vídeo en el idioma que venga.
- Si un dato no sale en la fuente, la celda se queda vacía. No se inventan tiempos ni ingredientes.
- `vegetariana`, `vegana` y `sin_gluten` solo se marcan `si` cuando los ingredientes lo dejan claro. Ante cualquier duda (caldos, salsas comerciales, embutidos), celda vacía. `adaptable` es para platos que lo son cambiando un ingrediente evidente.
- `fiestas`, `plato` y `estilo` son los que más pesan al montar el menú: no se dejan vacíos.

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
  "fecha_publicacion": "",
  "nota": "",
  "capturado_en": "2026-11-11T16:20:00+01:00"
}
```

Las capturas no se editan a mano.

## El texto extra: `raw/extra/<plataforma>/<id>.json`

La extensión no siempre ve la receta: en YouTube solo lee el título. `scripts/completar.py` recoge la descripción completa y los subtítulos del vídeo y los guarda aquí, sin tocar la captura.

## Descartados: `raw/descartados.tsv`

Las capturas revisadas que no son recetas se apuntan aquí, con `enlace` y `motivo`, para que no vuelvan a salir como pendientes.

## De la captura a la tabla

1. La extensión escribe la captura en `raw/<plataforma>/`.
2. `completar.py` recoge el texto que falte en `raw/extra/`.
3. `pendientes.py` lista las capturas que no están ni en la tabla ni en descartados, con todo su texto.
4. Cada una se clasifica: si es una receta, pasa a `recetas.tsv` con `agregar.py`; si no, a `descartados.tsv`.
5. Se regenera el catálogo de la skill.

Los scripts están en [`scripts/`](../scripts/README.md).
