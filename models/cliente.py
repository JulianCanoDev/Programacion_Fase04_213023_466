"""Modelo Cliente del sistema Software FJ con validacion estricta.

Todos los atributos se administran mediante propiedades con validacion en los
*setters* (encapsulacion): ningun dato puede asignarse sin pasar por las
reglas del sistema. Los errores se reportan con la excepcion
``ErrorClienteInvalido``.

Autor: Leo Diaz (Modelos).
"""

import re

from models.entidades import EntidadBase
from utils.excepciones import ErrorClienteInvalido


class Cliente(EntidadBase):
    """Cliente de la empresa registrado en memoria.

    Attributes:
        _documento: Documento de identidad (6 a 10 digitos).
        _apellido: Apellido del cliente (solo letras y espacios).
        _email: Correo electronico valido.
        _telefono: Celular colombiano de 10 digitos que inicia en 3.
    """

    PATRON_TEXTO = re.compile(r"^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ\s]{2,40}$")
    PATRON_DOCUMENTO = re.compile(r"^\d{6,10}$")
    PATRON_EMAIL = re.compile(r"^[\w.+-]+@[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)+$")
    PATRON_TELEFONO = re.compile(r"^3\d{9}$")

    def __init__(
        self,
        nombre: str,
        apellido: str,
        documento: str,
        email: str,
        telefono: str,
    ) -> None:
        super().__init__(nombre)
        self.apellido = apellido
        self.documento = documento
        self.email = email
        self.telefono = telefono

    @staticmethod
    def _validar_cadena(campo: str, valor: str, patron: re.Pattern[str]) -> None:
        """Valida un campo de texto contra su patron correspondiente.

        Raises:
            ErrorClienteInvalido: Si el valor no coincide con el patron.
        """
        if not isinstance(valor, str) or not patron.match(valor.strip()):
            raise ErrorClienteInvalido(
                f"El campo '{campo}' no tiene un formato valido",
                detalle=f"patron esperado: {patron.pattern} | valor recibido: {valor!r}",
            )

    @property
    def apellido(self) -> str:
        return self._apellido

    @apellido.setter
    def apellido(self, valor: str) -> None:
        self._validar_cadena("apellido", valor, self.PATRON_TEXTO)
        self._apellido = valor.strip().title()

    @property
    def documento(self) -> str:
        return self._documento

    @documento.setter
    def documento(self, valor: str) -> None:
        texto = valor.strip() if isinstance(valor, str) else ""
        if not self.PATRON_DOCUMENTO.match(texto):
            raise ErrorClienteInvalido(
                "El documento debe contener entre 6 y 10 digitos numericos",
                detalle=f"valor recibido: {valor!r}",
            )
        self._documento = texto

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, valor: str) -> None:
        self._validar_cadena("email", valor, self.PATRON_EMAIL)
        self._email = valor.strip().lower()

    @property
    def telefono(self) -> str:
        return self._telefono

    @telefono.setter
    def telefono(self, valor: str) -> None:
        texto = str(valor).strip() if valor is not None else ""
        if not self.PATRON_TELEFONO.match(texto):
            raise ErrorClienteInvalido(
                "El telefono debe ser un celular de 10 digitos que inicie en 3",
                detalle=f"valor recibido: {valor!r}",
            )
        self._telefono = texto

    @property
    def nombre_completo(self) -> str:
        """Nombre completo del cliente en formato de presentacion."""
        return f"{self._nombre} {self._apellido}"

    def obtener_descripcion(self) -> str:
        """Implementacion polimorfica de la descripcion de la entidad."""
        return (
            f"Cliente {self._documento} | {self.nombre_completo} "
            f"| {self._email} | cel. {self._telefono}"
        )

    def __eq__(self, otro: object) -> bool:
        if not isinstance(otro, Cliente):
            return NotImplemented
        return self._documento == otro._documento

    def __hash__(self) -> int:
        return hash(self._documento)

    def __repr__(self) -> str:
        return (
            f"Cliente(nombre={self._nombre!r}, apellido={self._apellido!r}, "
            f"documento={self._documento!r}, email={self._email!r}, "
            f"telefono={self._telefono!r})"
        )
