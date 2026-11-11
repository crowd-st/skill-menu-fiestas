# scraper/

Extensión de Chrome para capturar, desde la web, los vídeos cortos de recetas que queremos incluir en la skill. Es una herramienta interna: la usamos nosotros para llenar `recetas/raw/`.

## Qué hace

1. Estás viendo un reel de Instagram, un short de YouTube o un vídeo de TikTok.
2. Pulsas el botón de la extensión y, si quieres, añades una nota («para Nochevieja, como entrante»).
3. La extensión lee los metadatos del vídeo y escribe un JSON en `recetas/raw/<plataforma>/<id>.json`, en la copia local del repo.

El formato del JSON está definido en [`recetas/`](../recetas/README.md).

## Páginas que reconoce

| Plataforma | URL |
|---|---|
| Instagram | `instagram.com/reel/<id>/` y `instagram.com/p/<id>/` |
| YouTube | `youtube.com/shorts/<id>` |
| TikTok | `tiktok.com/@<usuario>/video/<id>` |

## Qué captura

Solo metadatos públicos de la página que se está viendo: URL, autor, título, descripción y fecha. No descarga el vídeo, no lee la cuenta ni los guardados, y no envía nada a ningún servidor.

## Cómo escribe en el repo

Una extensión no puede escribir en una carpeta cualquiera del disco. Propuesta: la primera vez se elige la carpeta `recetas/raw/` del repo local desde la página de opciones (File System Access API) y la extensión recuerda el permiso. A partir de ahí escribe directamente los archivos.

Si un vídeo ya está capturado, avisa y no lo duplica.

## Piezas previstas

```
scraper/
├── manifest.json      Manifest V3
├── popup/             Botón de captura y campo de nota
├── opciones/          Elegir la carpeta del repo
├── contenido/         Un lector de metadatos por plataforma
└── fondo/             Escritura de archivos
```

Se instala en modo desarrollador («Cargar descomprimida»). No se publica en la Chrome Web Store.

## Decisiones abiertas

- Confirmar que la File System Access API mantiene el permiso entre sesiones; si no, la alternativa es descargar el JSON y moverlo con un script.
- Captura de uno en uno, o también en lote desde una página de guardados o una lista.
- Si la nota es texto libre o lleva campos fijos (día, tipo de plato).
