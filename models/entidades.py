"""Clase abstracta base para todas las entidades del sistema Software FJ.

Centraliza el identificador consecutivo, el nombre comercial y la fecha de
registro comunes a clientes y servicios. Al ser abstracta, no puede
instanciarse directamente: obliga a cada entidad concreta a implementar
``obtener_descripcion`` (polimorfismo).

Autor: Leo Diaz (Modelos).
"""

from abc import ABC, abstractmethod
from datetime import datetime
from itertools import count

from utils.excepciones import ErrorValidacion


class EntidadBase(ABC):
    """Contrato comun para las entidades del sistema.

    Attributes:
        _id: Identificador consecutivo unico generado en memoria.
        _nombre: Nombre visible de la entidad (sin espacios sobrantes).
        _fecha_registro: Marca temporal de creacion de la entidad.
    """

    _secuencia: "count[int]" = count(1)

    def __init__(self, nombre: str) -> None:
        self._validar_nombre(nombre)
        self._id: int = next(EntidadBase._secuencia)
        self._nombre: str = nombre.strip()
        self._fecha_registro: datetime = datetime.now()

    @staticmethod
    def _validar_nombre(nombre: str) -> None:
        """Garantiza que el nombre sea texto con contenido real.

        Raises:
            ErrorValidacion: Si el nombre no es una cadena o esta vacio.
        """
        if not isinstance(nombre, str) or not nombre.strip():
            raise ErrorValidacion(
                "El nombre de la entidad es obligatorio y debe ser texto no vacio",
                detalle=f"valor recibido: {nombre!r}",
            )

    @property
    def id(self) -> int:
        """Identificador unico de la entidad (solo lectura)."""
        return self._id

    @property
    def nombre(self) -> str:
        """Nombre visible de la entidad."""
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        self._validar_nombre(valor)
        self._nombre = valor.strip()

    @property
    def fecha_registro(self) -> datetime:
        """Fecha y hora de creacion de la entidad (solo lectura)."""
        return self._fecha_registro

    @abstractmethod
    def obtener_descripcion(self) -> str:
        """Representacion legible de la entidad para el usuario final."""

    def __str__(self) -> str:
        return f"{type(self).__name__}#{self._id}({self._nombre})"
