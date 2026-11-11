// Habla con el servidor local (scraper/servidor.py).
// Las páginas no pueden llamar a 127.0.0.1 por su cuenta; el fondo de la extensión sí,
// gracias a host_permissions.

const SERVIDOR = "http://127.0.0.1:4747";

async function llamar({ metodo, plataforma, id, datos }) {
  const opciones = { method: metodo, headers: {} };
  if (datos) {
    opciones.headers["Content-Type"] = "application/json";
    opciones.body = JSON.stringify(datos);
  }
  try {
    const respuesta = await fetch(`${SERVIDOR}/capturas/${plataforma}/${encodeURIComponent(id)}`, opciones);
    const cuerpo = await respuesta.json().catch(() => ({}));
    if (!respuesta.ok) return { error: cuerpo.error || `error ${respuesta.status}` };
    return cuerpo;
  } catch {
    return { error: "sin-servidor" };
  }
}

chrome.runtime.onMessage.addListener((mensaje, _remitente, responder) => {
  llamar(mensaje).then(responder);
  return true; // respuesta asíncrona
});
