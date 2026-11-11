# skill-menu-fiestas

🎄 Skill para tu IA favorita que te ayuda a elegir qué cocinar estas navidades, con las recetas en vídeo corto. La felicitación navideña de Crowd Digital.

> **Estado:** esqueleto y definiciones. Todavía no hay recetas ni código; cada carpeta tiene un `README.md` que define qué irá dentro.

## Qué es

Le cuentas a tu IA cuántos sois, qué días cocinas y qué os gusta, y te propone el menú de Nochebuena, Navidad, San Esteban, Nochevieja y la noche de Reyes. De cada plato te da la receta resumida y el enlace al vídeo corto (Instagram, YouTube o TikTok) donde su autor la explica.

No calcula cantidades ni hace la lista de la compra: te ayuda a decidir y te lleva al vídeo.

## Cómo encajan las piezas

```
 scraper/  ──►  recetas/raw/  ──►  recetas/recetas.tsv  ──►  skill/  ──►  tu IA
 (extensión)    (capturas)         (tabla revisada)          (instrucciones + catálogo)

                                   landing/ · newsletter/ · rrss/   ──►  promoción
```

1. Con la extensión de Chrome guardamos los vídeos cortos de recetas que nos gustan.
2. Cada captura se revisa y, si es una receta, pasa a la tabla.
3. A partir de la tabla se genera el catálogo que usa la skill.
4. La landing, el correo y las piezas de redes explican la skill y llevan a ella.

## Estructura

```
skill-menu-fiestas/
├── AGENTS.md          Instrucciones para agentes (Claude, Codex...)
├── CLAUDE.md          Enlace simbólico a AGENTS.md
├── skill/             La skill: instrucciones y catálogo para cualquier IA
├── recetas/           La tabla de recetas y las capturas en bruto
├── scraper/           Extensión de Chrome para capturar vídeos cortos
├── scripts/           Scripts para pasar las capturas a la tabla y generar el catálogo
├── landing/           Página para presentar la skill
├── newsletter/        Correo para clientes
└── rrss/              Vídeo y publicaciones para redes sociales
```

| Carpeta | Definición |
|---|---|
| [`skill/`](skill/README.md) | Qué hace la skill, cómo conversa y cómo se distribuye a cada IA |
| [`recetas/`](recetas/README.md) | Formato de la tabla y de las capturas en bruto |
| [`scraper/`](scraper/README.md) | Qué captura la extensión y cómo escribe en el repo |
| [`scripts/`](scripts/README.md) | Scripts previstos para procesar y generar |
| [`landing/`](landing/README.md) | Secciones y objetivo de la página |
| [`newsletter/`](newsletter/README.md) | Contenido del correo a clientes |
| [`rrss/`](rrss/README.md) | Piezas para redes sociales |

## Créditos

Las recetas son de sus autores. La skill solo las recomienda y enlaza al vídeo original, citando siempre a quien lo ha hecho.

Un proyecto de Crowd Digital.
