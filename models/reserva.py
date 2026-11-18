"""Modelo de reservas del sistema Software FJ (sin base de datos).

``Reserva`` representa el acuerdo entre un cliente y un servicio por una
duracion determinada, con maquina de estados (Pendiente -> Confirmada /
Cancelada). ``GestorReservas`` administra todas las reservas **en memoria**
mediante una lista: es el sustituto de la base de datos exigido por el
proyecto. Cada evento relevante se registra en el log del sistema.

Autor: Camilo (Reservas y Logging).
"""

from datetime import datetime
from enum import Enum
from itertools import count

from models.cliente import Cliente
from models.servicios import Servicio
from utils.excepciones import (
    ErrorDisponibilidad,
    ErrorEstadoReserva,
    ErrorReservaInvalida,
    ErrorValidacion,
)
from utils.logger import obtener_logger

logger = obtener_logger("software_fj.reservas")


class EstadoReserva(str, Enum):
    """Estados posibles de una reserva durante su ciclo de vida."""

    PENDIENTE = "Pendiente"
    CONFIRMADA = "Confirmada"
    CANCELADA = "Cancelada"


class Reserva:
    """Acuerdo entre un cliente y un servicio por un numero de horas.

    Attributes:
        _codigo: Codigo legible consecutivo con formato ``RES-0001``.
        _duracion_horas: Tiempo contratado (entre 1 hora y 720 horas).
        _estado: Estado actual dentro de la maquina de estados.
    """

    DURACION_MAXIMA_HORAS = 720
    _TRANSICIONES = {
        EstadoReserva.PENDIENTE: frozenset(
            {EstadoReserva.CONFIRMADA, EstadoReserva.CANCELADA}
        ),
        EstadoReserva.CONFIRMADA: frozenset({EstadoReserva.CANCELADA}),
        EstadoReserva.CANCELADA: frozenset(),
    }
    _secuencia: "count[int]" = count(1)

    def __init__(
        self, cliente: Cliente, servicio: Servicio, duracion_horas: float
    ) -> None:
        self._validar_tipos(cliente, servicio)
        self._validar_duracion(duracion_horas)
        self._cliente = cliente
        self._servicio = servicio
        self._duracion_horas = float(duracion_horas)
        self._codigo = f"RES-{next(Reserva._secuencia):04d}"
        self._estado = EstadoReserva.PENDIENTE
        self._fecha_creacion = datetime.now()
        self._fecha_confirmacion: datetime | None = None
        self._motivo_cancelacion: str | None = None
        logger.info("Reserva %s creada para %s (%s)", self._codigo, cliente.nombre_completo, servicio.codigo)

    @staticmethod
    def _validar_tipos(cliente: Cliente, servicio: Servicio) -> None:
        """Valida que los argumentos sean instancias de las clases correctas.

        Raises:
            ErrorValidacion: Si el cliente o el servicio no tienen el tipo esperado.
        """
        if not isinstance(cliente, Cliente):
            raise ErrorValidacion(
                "La reserva requiere una instancia valida de Cliente",
                detalle=f"tipo recibido: {type(cliente).__name__}",
            )
        if not isinstance(servicio, Servicio):
            raise ErrorValidacion(
                "La reserva requiere una instancia valida de Servicio",
                detalle=f"tipo recibido: {type(servicio).__name__}",
            )

    @staticmethod
    def _validar_duracion(duracion_horas: float) -> None:
        """Valida el rango de la duracion contratada.

        Raises:
            ErrorReservaInvalida: Si la duracion es invalida o excede el maximo.
        """
        try:
            duracion = float(duracion_horas)
        except (TypeError, ValueError) as original:
            raise ErrorReservaInvalida(
                "La duracion de la reserva debe ser un numero de horas",
                detalle=f"valor recibido: {duracion_horas!r}",
            ) from original
        if not 0 < duracion <= Reserva.DURACION_MAXIMA_HORAS:
            raise ErrorReservaInvalida(
                f"La duracion debe estar entre 1 hora y {Reserva.DURACION_MAXIMA_HORAS} horas",
                detalle=f"valor recibido: {duracion}",
            )

    @property
    def codigo(self) -> str:
        return self._codigo

    @property
    def cliente(self) -> Cliente:
        return self._cliente

    @property
    def servicio(self) -> Servicio:
        return self._servicio

    @property
    def duracion_horas(self) -> float:
        return self._duracion_horas

    @property
    def estado(self) -> EstadoReserva:
        return self._estado

    @property
    def motivo_cancelacion(self) -> str | None:
        return self._motivo_cancelacion

    @property
    def costo_estimado(self) -> float:
        """Costo polimorfico: delega el calculo al servicio contratado."""
        return self._servicio.calcular_costo(self._duracion_horas)

    @property
    def esta_activa(self) -> bool:
        """Indica si la reserva aun puede confirmarse o cancelarse."""
        return self._estado in (EstadoReserva.PENDIENTE, EstadoReserva.CONFIRMADA)

    def _validar_transicion(self, destino: EstadoReserva) -> None:
        """Verifica la maquina de estados a nivel interno.

        Raises:
            ErrorReservaInvalida: Si la transicion solicitada no esta permitida.
        """
        permitidos = Reserva._TRANSICIONES[self._estado]
        if destino not in permitidos:
            raise ErrorReservaInvalida(
                f"Transicion no permitida de '{self._estado.value}' a '{destino.value}'"
            )

    def confirmar(self) -> None:
        """Pasa la reserva de Pendiente a Confirmada.

        Raises:
            ErrorEstadoReserva: Si la reserva no esta pendiente (encadenada
                desde la validacion interna de transiciones).
        """
        try:
            self._validar_transicion(EstadoReserva.CONFIRMADA)
        except ErrorReservaInvalida as original:
            raise ErrorEstadoReserva(
                f"No se puede confirmar {self._codigo}: su estado actual es '{self._estado.value}'"
            ) from original
        self._estado = EstadoReserva.CONFIRMADA
        self._fecha_confirmacion = datetime.now()
        logger.info("Reserva %s confirmada", self._codigo)

    def cancelar(self, motivo: str = "Sin especificar") -> None:
        """Cancela la reserva registrando el motivo del cliente.

        Raises:
            ErrorValidacion: Si el motivo esta vacio.
            ErrorEstadoReserva: Si la reserva ya fue cancelada (encadenada
                desde la validacion interna de transiciones).
        """
        if not isinstance(motivo, str) or not motivo.strip():
            raise ErrorValidacion(
                "El motivo de cancelacion es obligatorio",
                detalle=f"valor recibido: {motivo!r}",
            )
        try:
            self._validar_transicion(EstadoReserva.CANCELADA)
        except ErrorReservaInvalida as original:
            raise ErrorEstadoReserva(
                f"No se puede cancelar {self._codigo}: su estado actual es '{self._estado.value}'"
            ) from original
        self._estado = EstadoReserva.CANCELADA
        self._motivo_cancelacion = motivo.strip()
        logger.info("Reserva %s cancelada | motivo: %s", self._codigo, self._motivo_cancelacion)

    def __str__(self) -> str:
        return (
            f"{self._codigo} | {self._cliente.nombre_completo} | "
            f"{self._servicio.codigo} | {self._duracion_horas:.0f}h | "
            f"{self._estado.value} | ${self.costo_estimado:,.2f} COP"
        )


class GestorReservas:
    """Repositorio en memoria de reservas (sustituye la base de datos).

    Mantiene todas las reservas en una lista de Python y expone operaciones
    de creacion, confirmacion, cancelacion y consulta. Aplica una regla de
    negocio: numero maximo de reservas activas por cliente.
    """

    LIMITE_ACTIVAS_POR_CLIENTE = 3

    def __init__(self) -> None:
        self._reservas: list[Reserva] = []

    def crear(self, cliente: Cliente, servicio: Servicio, duracion_horas: float) -> Reserva:
        """Crea una reserva pendiente tras validar disponibilidad del cliente.

        Raises:
            ErrorValidacion: Si los argumentos no tienen el tipo esperado.
            ErrorDisponibilidad: Si el cliente ya alcanzo el limite activo.
        """
        try:
            documento = cliente.documento
        except AttributeError as original:
            raise ErrorValidacion(
                "crear_reserva requiere una instancia de Cliente",
                detalle=f"tipo recibido: {type(cliente).__name__}",
            ) from original
        activas = [
            reserva
            for reserva in self._reservas
            if reserva.esta_activa and reserva.cliente.documento == documento
        ]
        if len(activas) >= self.LIMITE_ACTIVAS_POR_CLIENTE:
            raise ErrorDisponibilidad(
                f"El cliente {documento} ya tiene {len(activas)} reservas activas "
                f"(limite: {self.LIMITE_ACTIVAS_POR_CLIENTE})"
            )
        reserva = Reserva(cliente, servicio, duracion_horas)
        self._reservas.append(reserva)
        return reserva

    def _buscar(self, codigo: str) -> Reserva:
        """Localiza una reserva por su codigo.

        Raises:
            ErrorReservaInvalida: Si el codigo no existe en memoria.
        """
        for reserva in self._reservas:
            if reserva.codigo == codigo:
                return reserva
        raise ErrorReservaInvalida(f"No existe la reserva '{codigo}' en el sistema")

    def confirmar(self, codigo: str) -> Reserva:
        """Confirma una reserva existente por codigo."""
        reserva = self._buscar(codigo)
        reserva.confirmar()
        return reserva

    def cancelar(self, codigo: str, motivo: str) -> Reserva:
        """Cancela una reserva existente por codigo."""
        reserva = self._buscar(codigo)
        reserva.cancelar(motivo)
        return reserva

    def por_cliente(self, documento: str) -> list[Reserva]:
        """Copia de las reservas asociadas a un documento."""
        return [r for r in self._reservas if r.cliente.documento == documento]

    def activas(self) -> list[Reserva]:
        """Copia de las reservas pendientes o confirmadas."""
        return [r for r in self._reservas if r.esta_activa]

    def resumen(self) -> dict[str, int]:
        """Conteo de reservas por estado y total de ingresos confirmados."""
        conteo = {estado.value: 0 for estado in EstadoReserva}
        ingresos = 0.0
        for reserva in self._reservas:
            conteo[reserva.estado.value] += 1
            if reserva.estado is EstadoReserva.CONFIRMADA:
                ingresos += reserva.costo_estimado
        conteo["total"] = len(self._reservas)
        conteo["ingresos_confirmados"] = round(ingresos, 2)
        return conteo

    def __len__(self) -> int:
        return len(self._reservas)

    def __iter__(self):
        return iter(self._reservas)
