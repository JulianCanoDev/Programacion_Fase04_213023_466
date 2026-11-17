"""Configuracion central de logging (eventos y errores) de Software FJ.

    Unico punto de entrada/salida de archivos permitido por el proyecto: todos los
eventos y errores de la aplicacion se escriben en ``logs/software_fj.log``
(con trazabilidad completa de excepciones). La consola se mantiene limpia:
solo mostraria mensajes criticos que amenazan la continuidad del proceso.

Autor: Camilo (Reservas y Logging).
"""

import logging
import sys
from pathlib import Path

NOMBRE_RAIZ = "software_fj"
DIRECTORIO_LOGS = Path(__file__).resolve().parent.parent / "logs"
ARCHIVO_LOG = DIRECTORIO_LOGS / "software_fj.log"
FORMATO_LOG = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"


def obtener_logger(nombre: str = NOMBRE_RAIZ) -> logging.Logger:
    """Devuelve el logger del sistema, configurandolo una sola vez.

    Los modulos pueden solicitar loggers hijos (por ejemplo
    ``obtener_logger("software_fj.reservas")``): la primera llamada garantiza
    la configuracion del logger raiz y los hijos propagan sus mensajes hacia
    el, sin crear handlers duplicados.

    Args:
        nombre: Nombre del logger; por defecto el logger raiz del sistema.

    Returns:
        Logger listo para emitir eventos a archivo y consola.
    """
    raiz = logging.getLogger(NOMBRE_RAIZ)
    if not raiz.handlers:
        raiz.setLevel(logging.INFO)
        raiz.propagate = False

        DIRECTORIO_LOGS.mkdir(parents=True, exist_ok=True)

        archivo = logging.FileHandler(ARCHIVO_LOG, encoding="utf-8")
        archivo.setLevel(logging.INFO)
        archivo.setFormatter(logging.Formatter(FORMATO_LOG))
        raiz.addHandler(archivo)

        consola = logging.StreamHandler(sys.stdout)
        consola.setLevel(logging.CRITICAL)
        consola.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
        raiz.addHandler(consola)

    return logging.getLogger(nombre)
