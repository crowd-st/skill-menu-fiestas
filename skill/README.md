# skill/

La skill `menu-fiestas`: las instrucciones y el catálogo de recetas que una IA necesita para ayudarte a elegir qué cocinar en las fiestas.

## Qué hace

1. **Pregunta lo justo:** qué días cocinas, cuántos sois, si hay niños, restricciones (vegetariano, sin gluten, alergias), estilo (tradicional o con un giro), nivel de cocina y tiempo disponible.
2. **Propone un menú por día:** aperitivo, entrante, principal y postre, elegidos del catálogo.
3. **Equilibra el conjunto:** no repite ingrediente principal entre días, combina platos que se preparan con antelación con otros de última hora y ajusta la dificultad al nivel de quien cocina.
4. **Da la receta de cada plato:** descripción, ingredientes sin cantidades, pasos resumidos, autor y enlace al vídeo.
5. **Permite cambiar:** «cámbiame el principal de Nochevieja por algo de pescado» y vuelve a proponer.

## Qué no hace

- No calcula cantidades ni raciones.
- No hace la lista de la compra.
- No recomienda platos que no estén en el catálogo ni inventa enlaces. Si no hay nada que encaje, lo dice.

## Días que cubre

| Valor | Día |
|---|---|
| `nochebuena` | Cena del 24 de diciembre |
| `navidad` | Comida del 25 de diciembre |
| `san-esteban` | Comida del 26 de diciembre |
| `nochevieja` | Cena del 31 de diciembre |
| `reyes` | Noche del 5 de enero |

## Archivos

```
skill/
├── menu-fiestas/
│   ├── SKILL.md       Instrucciones, en formato de skill
│   └── catalogo.md    Catálogo compacto de recetas (generado, no se edita)
└── prompt.md          Instrucciones y catálogo en un solo archivo (generado)
```

`catalogo.md` y `prompt.md` los genera `scripts/generar.py` a partir de `recetas/recetas.tsv`. Todavía no existen.

## Cómo llega a cada IA

La skill tiene que funcionar en la IA que use cada persona (Claude, ChatGPT, Gemini, Copilot, DeepSeek...) y desde cualquier dispositivo. Hay tres vías, de más universal a más cómoda:

| Vía | Cómo | Dónde funciona |
|---|---|---|
| **Copiar y pegar** | La landing copia `prompt.md` al portapapeles y abre el chat | En todas |
| **Enlace** | Se le pide a la IA que lea la URL pública de `prompt.md` | En las que navegan |
| **Instalación nativa** | Se instala `menu-fiestas/` como skill, o se publica como GPT o Gem | Claude, y las que tengan formato propio |

Como la vía universal es pegar un prompt, el catálogo tiene que ser compacto: por eso las recetas van sin cantidades y con los pasos resumidos.

## Tono y firma

Cercano y práctico, como alguien que cocina bien y te echa una mano. La skill no se promociona: no menciona a Crowd Digital al recomendar. Si le preguntan quién la ha hecho, responde que las recetas las ha elegido con cariño todo el equipo de Crowd Digital, y nada más.

## Decisiones abiertas

- Tamaño máximo del catálogo para que quepa con holgura en un prompt en todas las IA.
- Si publicamos también un GPT y un Gem, o solo el prompt y la skill de Claude.
