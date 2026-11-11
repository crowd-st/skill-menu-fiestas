# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Servidor local que recibe las capturas de la extensión y las guarda en el repo.

Escucha solo en 127.0.0.1 y escribe en recetas/raw/<plataforma>/<id>.json.

    uv run scraper/servidor.py               # puerto 4747
    uv run scraper/servidor.py --puerto 5000

API (la usa la extensión):

    GET    /estado                        -> {"ok": true}
    GET    /capturas/<plataforma>/<id>    -> {"guardada": bool, "procesada": bool}
    PUT    /capturas/<plataforma>/<id>    -> guarda la captura (cuerpo JSON)
    DELETE /capturas/<plataforma>/<id>    -> la borra, si todavía no se ha procesado
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
RAW = RAIZ / "recetas" / "raw"
TABLAS_PROCESADAS = [RAIZ / "recetas" / "recetas.tsv", RAW / "descartados.tsv"]

PLATAFORMAS = {"instagram", "youtube", "tiktok"}
ID_VALIDO = re.compile(r"^[A-Za-z0-9_-]{5,40}$")
RUTA = re.compile(r"^/capturas/([a-z]+)/([^/]+)$")
CAMPOS = ["url", "autor", "titulo", "descripcion", "fecha_publicacion", "nota"]
MAX_TEXTO = 5000


def archivo(plataforma: str, id_: str) -> Path:
    return RAW / plataforma / f"{id_}.json"


def procesada(id_: str) -> bool:
    """Una captura está procesada si su id sale en la tabla o en descartados."""
    for tabla in TABLAS_PROCESADAS:
        if tabla.exists() and id_ in tabla.read_text(encoding="utf-8"):
            return True
    return False


def limpiar(valor: object) -> str:
    if not isinstance(valor, str):
        return ""
    return valor.strip()[:MAX_TEXTO]


def ahora() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


class Manejador(BaseHTTPRequestHandler):
    server_version = "menu-fiestas"

    # --- respuestas -------------------------------------------------------

    def responder(self, codigo: int, datos: dict) -> None:
        cuerpo = json.dumps(datos, ensure_ascii=False).encode("utf-8")
        self.send_response(codigo)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(cuerpo)))
        self.end_headers()
        self.wfile.write(cuerpo)

    def log_message(self, formato: str, *args: object) -> None:  # silencia el log por petición
        pass

    # --- seguridad --------------------------------------------------------

    def origen_permitido(self) -> bool:
        """Solo la extensión (o una petición local sin Origin, como curl).

        Una web abierta en el navegador siempre manda su Origin http(s)://,
        así que no puede leer ni escribir capturas.
        """
        origen = self.headers.get("Origin", "")
        return origen == "" or origen.startswith(("chrome-extension://", "moz-extension://"))

    def destino(self) -> tuple[str, str] | None:
        coincidencia = RUTA.match(self.path.split("?", 1)[0])
        if not coincidencia:
            return None
        plataforma, id_ = coincidencia.groups()
        if plataforma not in PLATAFORMAS or not ID_VALIDO.match(id_):
            return None
        return plataforma, id_

    # --- métodos ----------------------------------------------------------

    def do_GET(self) -> None:
        if not self.origen_permitido():
            return self.responder(403, {"error": "origen no permitido"})
        if self.path == "/estado":
            return self.responder(200, {"ok": True})
        destino = self.destino()
        if not destino:
            return self.responder(404, {"error": "ruta no válida"})
        plataforma, id_ = destino
        self.responder(200, {"guardada": archivo(plataforma, id_).exists(), "procesada": procesada(id_)})

    def do_PUT(self) -> None:
        if not self.origen_permitido():
            return self.responder(403, {"error": "origen no permitido"})
        if not self.headers.get("Content-Type", "").startswith("application/json"):
            return self.responder(415, {"error": "se espera JSON"})
        destino = self.destino()
        if not destino:
            return self.responder(404, {"error": "ruta no válida"})
        plataforma, id_ = destino

        try:
            longitud = int(self.headers.get("Content-Length", "0"))
            if longitud > 100_000:
                return self.responder(413, {"error": "demasiado grande"})
            datos = json.loads(self.rfile.read(longitud) or b"{}")
            if not isinstance(datos, dict):
                raise ValueError
        except ValueError:
            return self.responder(400, {"error": "JSON no válido"})

        ruta = archivo(plataforma, id_)
        anterior = json.loads(ruta.read_text(encoding="utf-8")) if ruta.exists() else {}

        captura = {"id": id_, "plataforma": plataforma}
        for campo in CAMPOS:
            # Al volver a capturar, un campo vacío no borra lo que ya había.
            captura[campo] = limpiar(datos.get(campo)) or anterior.get(campo, "")
        captura["capturado_en"] = anterior.get("capturado_en") or ahora()

        ruta.parent.mkdir(parents=True, exist_ok=True)
        temporal = ruta.with_suffix(".tmp")
        temporal.write_text(json.dumps(captura, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        os.replace(temporal, ruta)

        print(f"🎄 guardada  {plataforma}/{id_}  {captura['autor'] or ''}  {captura['titulo'][:60]}", flush=True)
        self.responder(200, {"guardada": True, "procesada": procesada(id_)})

    def do_DELETE(self) -> None:
        if not self.origen_permitido():
            return self.responder(403, {"error": "origen no permitido"})
        destino = self.destino()
        if not destino:
            return self.responder(404, {"error": "ruta no válida"})
        plataforma, id_ = destino
        if procesada(id_):
            return self.responder(409, {"error": "ya está procesada; se quita desde la tabla"})
        ruta = archivo(plataforma, id_)
        if ruta.exists():
            ruta.unlink()
            print(f"   quitada   {plataforma}/{id_}", flush=True)
        self.responder(200, {"guardada": False, "procesada": False})


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--puerto", type=int, default=4747)
    args = parser.parse_args()

    servidor = ThreadingHTTPServer(("127.0.0.1", args.puerto), Manejador)
    print(f"Guardando capturas en {RAW.relative_to(RAIZ)}/ · http://127.0.0.1:{args.puerto} · Ctrl+C para parar", flush=True)
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print()
    finally:
        servidor.server_close()


if __name__ == "__main__":
    sys.exit(main())
