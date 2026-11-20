# --------------------------------------------
# Nombre: Laura Daniela Troncoso Rodríguez
# Curso: Programación (213023) - Fase 4
# Módulo: Excepciones personalizadas y sistema de logs (Software FJ)
# --------------------------------------------

import logging
from datetime import datetime


def configurar_logger(archivo_log: str = "software_fj.log") -> logging.Logger:
    """Configura y devuelve el logger del sistema sin usar base de datos."""
    logger = logging.getLogger("SoftwareFJLogger")
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        formato = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

        manejador_archivo = logging.FileHandler(archivo_log, mode="a", encoding="utf-8")
        manejador_archivo.setFormatter(formato)
        logger.addHandler(manejador_archivo)

        manejador_consola = logging.StreamHandler()
        manejador_consola.setFormatter(formato)
        logger.addHandler(manejador_consola)

    return logger


logger_fj = configurar_logger()


class ErrorSoftwareFJ(Exception):
    """Excepción base personalizada para el sistema integral de Software FJ."""

    def __init__(self, mensaje: str, codigo_error: str = "ERR_GENERAL"):
        self.codigo_error = codigo_error
        self.timestamp = datetime.now().isoformat()
        super().__init__(f"[{codigo_error}] {mensaje}")


class ErrorValidacionCliente(ErrorSoftwareFJ):
    """Error lanzado cuando los datos o parámetros de un cliente son inválidos."""

    def __init__(self, mensaje: str):
        super().__init__(mensaje, codigo_error="ERR_CLIENTE")


class ErrorParametroServicio(ErrorSoftwareFJ):
    """Error lanzado ante parámetros faltantes, inválidos o cálculos inconsistentes en servicios."""

    def __init__(self, mensaje: str):
        super().__init__(mensaje, codigo_error="ERR_SERVICIO")


class ErrorReserva(ErrorSoftwareFJ):
    """Error lanzado ante reservas inválidas, falta de disponibilidad o transiciones no permitidas."""

    def __init__(self, mensaje: str):
        super().__init__(mensaje, codigo_error="ERR_RESERVA")


class ErrorOperacionSistema(ErrorSoftwareFJ):
    """Error de alto nivel encadenado cuando falla una operación del gestor."""

    def __init__(self, mensaje: str):
        super().__init__(mensaje, codigo_error="ERR_OPERACION")
