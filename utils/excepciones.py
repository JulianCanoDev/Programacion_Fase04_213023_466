"""Jerarquia de excepciones personalizadas del sistema Software FJ.

Toda la gestion de errores del sistema se apoya en esta jerarquia, lo que
permite capturar errores genericos (``ErrorSoftwareFJ``) o especificos
(``ErrorClienteInvalido``, ``ErrorDisponibilidad``, etc.) segun la necesidad,
y facilita el encadenamiento de excepciones (``raise ... from ...``).

Autor: John Arroyo (Servicios y Excepciones).
"""


class ErrorSoftwareFJ(Exception):
    """Raiz de la jerarquia de excepciones del sistema Software FJ.

    Attributes:
        detalle: Informacion tecnica adicional que ayuda a depurar la causa
            del error sin exponer datos sensibles al usuario final.
    """

    def __init__(self, mensaje: str, detalle: str | None = None) -> None:
        self.detalle = detalle
        super().__init__(mensaje)

    def __str__(self) -> str:
        texto = super().__str__()
        if self.detalle:
            return f"{texto} (detalle: {self.detalle})"
        return texto


class ErrorValidacion(ErrorSoftwareFJ):
    """Se produce cuando un dato no cumple las reglas de validacion del sistema."""


class ErrorClienteInvalido(ErrorValidacion):
    """Se produce cuando los datos de un cliente son invalidos o estan incompletos."""


class ErrorServicioInvalido(ErrorValidacion):
    """Se produce cuando un servicio recibe parametros invalidos."""


class ErrorReservaInvalida(ErrorSoftwareFJ):
    """Se produce cuando una reserva no puede crearse o encontrarse."""


class ErrorEstadoReserva(ErrorReservaInvalida):
    """Se produce cuando se intenta una transicion de estado no permitida."""


class ErrorDisponibilidad(ErrorReservaInvalida):
    """Se produce cuando un cliente supera el limite de reservas activas."""


class ErrorOperacion(ErrorSoftwareFJ):
    """Envuelve fallos inesperados para que la aplicacion no se detenga."""
