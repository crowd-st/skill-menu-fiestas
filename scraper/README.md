# scraper/

Extensión de Chrome (también funciona en Brave) para capturar, desde la web, los vídeos cortos de recetas que queremos incluir en la skill. Es una herramienta interna: la usamos nosotros para llenar `recetas/raw/`.

## Qué hace

Encima del botón de «me gusta» de cada vídeo añade un botón 🎄 **Receta**:

- **Púlsalo** y el vídeo va a las recetas pendientes de procesar: se escribe `recetas/raw/<plataforma>/<id>.json` en la copia local del repo.
- **Queda pulsado** (verde) si el vídeo ya está guardado, también al volver a verlo otro día.
- **Púlsalo otra vez** para quitarlo, mientras no se haya procesado. Si ya está en la tabla o en descartados, no se puede quitar desde aquí.

El formato del JSON está definido en [`recetas/`](../recetas/README.md).

## Cómo funciona

Una extensión no puede escribir en una carpeta del disco, así que hay dos piezas:

```
 extensión (botón 🎄)  ──►  servidor.py en 127.0.0.1:4747  ──►  recetas/raw/<plataforma>/<id>.json
```

- **`servidor.py`**: un servidor mínimo, solo con la librería estándar de Python, que escucha únicamente en `127.0.0.1`. Valida la plataforma y el id, y solo acepta peticiones de la extensión: una web abierta en el navegador no puede leer ni escribir capturas.
- **`extension/`**: pinta el botón y le pasa al servidor los metadatos del vídeo que se está viendo.

## Puesta en marcha

1. Arranca el servidor desde la raíz del repo y déjalo abierto mientras capturas:

   ```bash
   uv run scraper/servidor.py
   ```

2. Instala la extensión, una sola vez:
   - Chrome: abre `chrome://extensions`. Brave: `brave://extensions`.
   - Activa el **Modo de desarrollador**.
   - **Cargar descomprimida** y elige la carpeta `scraper/extension/`.

3. Abre un short y pulsa 🎄. En el terminal del servidor sale cada receta guardada.

Si el servidor no está en marcha, el botón se ve apagado y al pulsarlo avisa de que hay que arrancarlo.

Después de cambiar el código de la extensión, pulsa el botón de recargar en la página de extensiones y recarga las pestañas abiertas.

## Páginas que reconoce

| Plataforma | Dónde sale el botón | Cómo encuentra el «me gusta» |
|---|---|---|
| YouTube | `youtube.com/shorts/<id>` | `<like-button-view-model>` dentro de la barra de acciones |
| TikTok | Feed y `tiktok.com/@<usuario>/video/<id>` | Atributos `data-e2e="like-icon"` y `browse-like-icon` |
| Instagram | Reels (`/reels/`, `/reel/<código>/`), publicaciones (`/p/<código>/`) y feed | `aria-label` del icono, en castellano, catalán e inglés |

Estas webs cambian a menudo su código. Si el botón deja de salir en una plataforma, el sitio que hay que tocar es su archivo en `extension/contenido/`.

## Qué captura

Solo metadatos públicos de la página que se está viendo: URL, autor, título y descripción, según lo que muestre cada plataforma. No descarga el vídeo, no lee la cuenta ni los guardados, y no envía nada fuera del ordenador.

La descripción no siempre está a la vista (en Instagram, por ejemplo, a menudo está recortada). No pasa nada: al procesar las capturas se completa lo que falte.

## Archivos

```
scraper/
├── servidor.py              Servidor local que escribe en recetas/raw/
└── extension/
    ├── manifest.json        Manifest V3
    ├── fondo.js             Habla con el servidor
    └── contenido/
        ├── comun.js         Botón, estado y guardado (común a las tres)
        ├── boton.css        Estilo del botón y del aviso
        ├── youtube.js       Dónde va el botón y qué se lee, en YouTube
        ├── instagram.js     Ídem, en Instagram
        └── tiktok.js        Ídem, en TikTok
```

No se publica en la Chrome Web Store.

## Decisiones abiertas

- Si el botón permite añadir una nota («para Nochevieja, como entrante»). El servidor ya acepta el campo `nota`.
- Arrancar el servidor automáticamente al iniciar sesión en el Mac, para no tener que acordarse.
