# skill-menu-fiestas — instrucciones para agentes

Proyecto de Crowd Digital: la felicitación navideña es una skill pública que ayuda a elegir qué cocinar en las fiestas, con enlaces a recetas en vídeo corto.

**El repo es público.** Todo lo que se escribe aquí lo puede leer cualquiera.

## Idioma

Todo el contenido del repo va en **castellano**: documentación, skill, recetas, textos de la landing, del correo y de redes. Los nombres de carpetas, archivos, columnas y valores controlados van en minúsculas, sin acentos ni `ñ`.

## Tono: Crowd Digital, en segundo plano

Esto es un regalo, no un anuncio. La protagonista es la skill y lo que resuelve; Crowd Digital solo firma.

- **Una sola firma, discreta.** En la landing y en el correo es, literalmente, «Cocinado con amor por Crowd Digital»: una línea pequeña al pie. En el resto de piezas, si hace falta decir algo, que las recetas las ha elegido con cariño todo el equipo.
- **Nada comercial:** ni servicios, ni casos, ni «contáctanos», ni logotipo grande, ni el nombre en titulares o botones.
- **La skill no se promociona.** No menciona a Crowd Digital al recomendar; solo lo dice si le preguntan quién la ha hecho.
- En caso de duda, menos marca.

## Piezas

Cada carpeta tiene un `README.md` con su definición. Léelo antes de trabajar en ella.

- `skill/`: la skill (instrucciones y catálogo).
- `recetas/`: `recetas.tsv` es la fuente de verdad; `raw/` son las capturas en bruto.
- `scraper/`: extensión de Chrome que captura vídeos cortos y escribe en `recetas/raw/`.
- `scripts/`: scripts para pasar capturas a la tabla y generar el catálogo de la skill.
- `landing/`, `newsletter/`, `rrss/`: piezas de promoción.

## Reglas de las recetas

- **Solo recetas de cocina.** Una captura entra en la tabla si explica cómo preparar un plato, una bebida o un dulce. Restaurantes, productos, humor, sorteos y recopilatorios sin receta se descartan y se apuntan en `recetas/raw/descartados.tsv`.
- **Sin cantidades ni lista de la compra.** Los ingredientes se listan sin medidas y los pasos se resumen. Quien quiera el detalle va al vídeo.
- **Nunca inventes un enlace ni una receta.** Todo plato de la tabla viene de una captura real y lleva el enlace al vídeo original.
- **Cita siempre al autor** del vídeo (`autor`).
- **Restricciones alimentarias con cautela.** `vegetariana` y `sin_gluten` solo se marcan `si` cuando la fuente lo deja claro. En caso de duda, celda vacía.
- Las capturas en bruto (`recetas/raw/<plataforma>/`) no se editan a mano.
- Cuando existan los scripts, la tabla se escribe siempre a través de ellos, no a mano.

## Privacidad

- Nada de datos de clientes en el repo: la lista de destinatarios del correo, nombres o estadísticas de envío se quedan fuera.
- Nada de sesiones, cookies, tokens ni credenciales. Si alguna pieza las necesita, van en `.sessions/`, que git ignora.
- La extensión solo guarda metadatos públicos del vídeo que se está viendo. No descarga vídeos.

## Commits

No hagas commit ni push si no te lo piden.
