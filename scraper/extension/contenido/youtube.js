// YouTube Shorts: youtube.com/shorts/<id>
// La barra de acciones es <reel-action-bar-view-model> y el «me gusta», <like-button-view-model>.
// YouTube reutiliza la misma barra al pasar de short, así que el id se lee de la URL.

(() => {
  const { iniciar, texto } = window.MenuFiestas;

  const idDeLaUrl = () => {
    const coincidencia = location.pathname.match(/^\/shorts\/([A-Za-z0-9_-]{11})/);
    return coincidencia ? coincidencia[1] : "";
  };

  iniciar({
    plataforma: "youtube",

    buscarAnclas() {
      if (!idDeLaUrl()) return [];
      return document.querySelectorAll("reel-action-bar-view-model > like-button-view-model");
    },

    leerVideo(ancla) {
      const id = idDeLaUrl();
      if (!id) return null;
      const video = ancla.closest("ytd-reel-video-renderer") || document;
      const canal = video.querySelector("yt-reel-channel-bar-view-model a[href^='/@']");
      return {
        id,
        url: `https://www.youtube.com/shorts/${id}`,
        autor: canal ? canal.getAttribute("href").split("/")[1] : "",
        titulo: texto(video.querySelector("yt-shorts-video-title-view-model")),
        descripcion: "",
        fecha_publicacion: "",
      };
    },
  });
})();
