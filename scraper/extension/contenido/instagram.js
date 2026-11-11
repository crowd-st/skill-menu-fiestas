// Instagram: reels (instagram.com/reels/<código>/, /reel/<código>/) y publicaciones (/p/<código>/).
// Instagram no tiene atributos estables, así que el «me gusta» se busca por el aria-label
// de su icono, en los idiomas habituales. Si tu Instagram está en otro idioma, añádelo aquí.

(() => {
  const { iniciar, texto } = window.MenuFiestas;

  const ETIQUETAS_ME_GUSTA = new Set([
    // castellano
    "Me gusta", "Ya no me gusta",
    // catalán
    "M'agrada", "M’agrada", "Ja no m'agrada", "Ja no m’agrada",
    // inglés
    "Like", "Unlike",
  ]);

  const CODIGO = /\/(?:reels?|p)\/([A-Za-z0-9_-]{5,40})/;

  function botonDe(icono) {
    return icono.closest("[role='button'], button") || icono.parentElement;
  }

  // Sube desde el «me gusta» hasta el bloque que contiene un solo vídeo.
  function contenedor(ancla) {
    return ancla.closest("article") || ancla.closest("section") || ancla.parentElement;
  }

  iniciar({
    plataforma: "instagram",

    buscarAnclas() {
      const anclas = new Set();
      for (const icono of document.querySelectorAll("svg[aria-label]")) {
        if (!ETIQUETAS_ME_GUSTA.has(icono.getAttribute("aria-label"))) continue;
        // Los «me gusta» pequeños de los comentarios no llevan botón 🎄.
        if (icono.getBoundingClientRect().width < 20) continue;
        const boton = botonDe(icono);
        // En los reels, el «me gusta» va en un bloque junto a su contador:
        // si es así, el 🎄 va encima del bloque y no entre el icono y el número.
        const padre = boton.parentElement;
        const conContador =
          padre && padre.childElementCount <= 2 && padre.querySelectorAll("svg[aria-label]").length === 1;
        anclas.add(conContador ? padre : boton);
      }
      return anclas;
    },

    leerVideo(ancla) {
      const caja = contenedor(ancla);

      // En la página de un reel o una publicación, la URL manda.
      // En el feed, el enlace a la publicación que hay dentro del artículo.
      let coincidencia = location.pathname.match(CODIGO);
      const article = ancla.closest("article");
      if (article) {
        for (const enlace of article.querySelectorAll("a[href*='/p/'], a[href*='/reel/']")) {
          const encontrada = enlace.getAttribute("href").match(CODIGO);
          if (encontrada) {
            coincidencia = encontrada;
            break;
          }
        }
      }
      if (!coincidencia) return null;
      const codigo = coincidencia[1];

      // El autor es el primer enlace a un perfil (/<usuario>/) del bloque.
      let autor = "";
      for (const enlace of caja.querySelectorAll("a[href^='/']")) {
        const perfil = enlace.getAttribute("href").match(/^\/([A-Za-z0-9._]{1,30})\/?$/);
        if (perfil && !["explore", "reels", "direct", "accounts"].includes(perfil[1])) {
          autor = perfil[1];
          break;
        }
      }

      // La descripción del reel, si está a la vista (el texto más largo del bloque).
      let descripcion = "";
      for (const parrafo of caja.querySelectorAll("h1, span[dir='auto']")) {
        const contenido = texto(parrafo);
        if (contenido.length > descripcion.length) descripcion = contenido;
      }

      return {
        id: codigo,
        url: `https://www.instagram.com/reel/${codigo}/`,
        autor,
        titulo: "",
        descripcion,
        fecha_publicacion: "",
      };
    },
  });
})();
