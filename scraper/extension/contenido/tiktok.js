// TikTok: tiktok.com/@<usuario>/video/<id>, y el feed (Para ti, Siguiendo...).
// TikTok marca sus elementos con data-e2e. El «me gusta» es:
//   - like-icon         en el feed
//   - browse-like-icon  en la página de un vídeo
// El botón 🎄 va encima del <button> que contiene el icono.

(() => {
  const { iniciar, texto } = window.MenuFiestas;

  const ID_VIDEO = /\/@([^/?#]+)\/video\/(\d{8,25})/;

  function contenedor(ancla) {
    return (
      ancla.closest("article") ||
      ancla.closest("[data-e2e='recommend-list-item-container']") ||
      ancla.closest("[class*='DivItemContainer']") ||
      document
    );
  }

  iniciar({
    plataforma: "tiktok",

    buscarAnclas() {
      const iconos = document.querySelectorAll(
        "[data-e2e='like-icon'], [data-e2e='browse-like-icon']",
      );
      const anclas = new Set();
      for (const icono of iconos) anclas.add(icono.closest("button") || icono.parentElement);
      return anclas;
    },

    leerVideo(ancla) {
      const caja = contenedor(ancla);

      // 1) En el feed: el enlace al vídeo que hay dentro de la tarjeta.
      // 2) En la página de un vídeo: la URL.
      let coincidencia = null;
      if (caja !== document) {
        for (const enlace of caja.querySelectorAll("a[href*='/video/']")) {
          coincidencia = enlace.href.match(ID_VIDEO);
          if (coincidencia) break;
        }
      }
      if (!coincidencia) coincidencia = location.href.match(ID_VIDEO);
      if (!coincidencia) return null;

      const [, usuario, id] = coincidencia;
      const descripcion = caja.querySelector(
        "[data-e2e='video-desc'], [data-e2e='browse-video-desc']",
      );
      return {
        id,
        url: `https://www.tiktok.com/@${usuario}/video/${id}`,
        autor: usuario,
        titulo: "",
        descripcion: texto(descripcion),
        fecha_publicacion: "",
      };
    },
  });
})();
