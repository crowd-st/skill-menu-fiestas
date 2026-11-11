// Lógica común a las tres plataformas: pinta el botón 🎄 encima de cada «me gusta»,
// sabe si el vídeo ya está guardado y lo guarda o lo quita al pulsarlo.
//
// Cada plataforma (youtube.js, instagram.js, tiktok.js) llama a
// MenuFiestas.iniciar({ plataforma, buscarAnclas, leerVideo }):
//   buscarAnclas()   -> elementos «me gusta» encima de los que va el botón
//   leerVideo(ancla) -> { id, url, autor, titulo, descripcion, fecha_publicacion } o null

(() => {
  const CLASE = "menu-fiestas-boton";
  const INTERVALO_MS = 800;
  const AYUDA_SERVIDOR = "Arranca el servidor: uv run scraper/servidor.py";

  const estados = new Map(); // "plataforma/id" -> { guardada, procesada }

  function enviar(mensaje) {
    return new Promise((resolver) => {
      try {
        chrome.runtime.sendMessage(mensaje, (respuesta) => {
          resolver(chrome.runtime.lastError ? { error: "extension-recargada" } : respuesta);
        });
      } catch {
        resolver({ error: "extension-recargada" });
      }
    });
  }

  function aviso(texto) {
    let caja = document.querySelector(".menu-fiestas-aviso");
    if (!caja) {
      caja = document.createElement("div");
      caja.className = "menu-fiestas-aviso";
      document.body.appendChild(caja);
    }
    caja.textContent = texto;
    caja.classList.add("visible");
    clearTimeout(caja._temporizador);
    caja._temporizador = setTimeout(() => caja.classList.remove("visible"), 3500);
  }

  function pintar(boton, estado) {
    const guardada = Boolean(estado && estado.guardada);
    const procesada = Boolean(estado && estado.procesada);
    boton.classList.toggle("guardada", guardada || procesada);
    boton.classList.toggle("sin-servidor", Boolean(estado && estado.error === "sin-servidor"));
    boton.setAttribute("aria-pressed", String(guardada || procesada));
    boton.title = procesada
      ? "Ya está en la lista de recetas"
      : guardada
        ? "Guardada para procesar · pulsa para quitarla"
        : "Guardar receta para el menú de fiestas";
  }

  function crearBoton() {
    const boton = document.createElement("button");
    boton.type = "button";
    boton.className = CLASE;
    // Sin innerHTML: YouTube exige Trusted Types y lo bloquearía.
    const icono = document.createElement("span");
    icono.className = "icono";
    icono.setAttribute("aria-hidden", "true");
    icono.textContent = "🎄";
    const etiqueta = document.createElement("span");
    etiqueta.className = "texto";
    etiqueta.textContent = "Receta";
    boton.append(icono, etiqueta);
    boton.setAttribute("aria-label", "Guardar receta para el menú de fiestas");
    return boton;
  }

  function iniciar({ plataforma, buscarAnclas, leerVideo }) {
    const clave = (id) => `${plataforma}/${id}`;

    async function consultar(boton, id) {
      const estado = await enviar({ metodo: "GET", plataforma, id });
      if (!estado.error) estados.set(clave(id), estado);
      if (boton.dataset.id === id) pintar(boton, estado);
    }

    async function alPulsar(evento, boton, ancla) {
      evento.preventDefault();
      evento.stopPropagation();
      const video = leerVideo(ancla);
      if (!video || !video.id) return aviso("No encuentro el vídeo en esta página");

      const actual = estados.get(clave(video.id));
      if (actual && actual.procesada) return aviso("Esta receta ya está en la lista");

      boton.disabled = true;
      const quitar = Boolean(actual && actual.guardada);
      const { id, ...datos } = video;
      const estado = await enviar(
        quitar ? { metodo: "DELETE", plataforma, id } : { metodo: "PUT", plataforma, id, datos },
      );
      boton.disabled = false;

      if (estado.error === "sin-servidor") return pintar(boton, estado), aviso(AYUDA_SERVIDOR);
      if (estado.error === "extension-recargada") return aviso("Recarga la página: la extensión se ha actualizado");
      if (estado.error) return aviso(`No se ha podido guardar: ${estado.error}`);

      estados.set(clave(id), estado);
      pintar(boton, estado);
      aviso(quitar ? "Quitada de las recetas pendientes" : "🎄 Guardada en las recetas pendientes");
    }

    function revisar() {
      for (const ancla of buscarAnclas()) {
        if (!ancla || !ancla.parentElement) continue;

        let boton = ancla.previousElementSibling;
        if (!boton || !boton.classList.contains(CLASE)) {
          boton = crearBoton();
          boton.classList.add(plataforma);
          boton.addEventListener("click", (evento) => alPulsar(evento, boton, ancla));
          ancla.parentElement.insertBefore(boton, ancla);
        }

        // Las plataformas reutilizan los mismos elementos al pasar de vídeo:
        // si el vídeo ha cambiado, se vuelve a consultar su estado.
        const video = leerVideo(ancla);
        const id = video && video.id ? video.id : "";
        if (boton.dataset.id !== id) {
          boton.dataset.id = id;
          pintar(boton, estados.get(clave(id)));
          if (id) consultar(boton, id);
        }
      }
    }

    setInterval(revisar, INTERVALO_MS);
    revisar();

    // Al volver a la pestaña, refresca el estado por si se ha procesado algo mientras tanto.
    document.addEventListener("visibilitychange", () => {
      if (document.visibilityState !== "visible") return;
      for (const boton of document.querySelectorAll(`.${CLASE}`)) {
        if (boton.dataset.id) consultar(boton, boton.dataset.id);
      }
    });
  }

  // Utilidades para los lectores de cada plataforma.
  const texto = (elemento) => (elemento ? elemento.textContent.replace(/\s+/g, " ").trim() : "");

  window.MenuFiestas = { iniciar, texto };
})();
