"""Jerarquia de servicios del sistema Software FJ.

``Servicio`` define el contrato abstracto (costo, descripcion y validacion de
parametros) y tres clases concretas lo especializan: salas, equipos de
computo y consultoria. Cada subclase **sobrescribe** los metodos abstractos
con su propia formula de costo, y la clase base implementa
**sobrecarga simulada** (Python no soporta sobrecarga real) mediante
parametros por defecto en los metodos de impuestos y descuentos.

Autor: John Arroyo (Servicios y Excepciones).
"""

import re
from abc import abstractmethod

from models.entidades import EntidadBase
from utils.excepciones import ErrorServicioInvalido


class Servicio(EntidadBase):
    """Contrato base de todos los servicios ofrecidos por la empresa.

    Attributes:
        _codigo: Codigo unico con formato ``AAA-999`` (3 letras, guion, 3 digitos).
        _precio_base: Precio de referencia por unidad de tiempo (COP, mayor que 0).
        _tarifa_iva: Tarifa de IVA en fraccion decimal (por defecto 19%).
    """

    PATRON_CODIGO = re.compile(r"^[A-Z]{3}-\d{3}$")
    IVA_POR_DEFECTO = 0.19

    def __init__(
        self,
        codigo: str,
        nombre: str,
        precio_base: float,
        tarifa_iva: float = IVA_POR_DEFECTO,
    ) -> None:
        super().__init__(nombre)
        self._validar_codigo(codigo)
        self._codigo = codigo.strip().upper()
        self._asignar_precio_base(precio_base)
        self._asignar_tarifa_iva(tarifa_iva)

    @classmethod
    def _validar_codigo(cls, codigo: str) -> None:
        """Valida el formato del codigo del servicio.

        Raises:
            ErrorServicioInvalido: Si el codigo no cumple el patron ``AAA-999``.
        """
        if not isinstance(codigo, str) or not cls.PATRON_CODIGO.match(codigo.strip().upper()):
            raise ErrorServicioInvalido(
                "El codigo del servicio debe tener el formato AAA-999",
                detalle=f"valor recibido: {codigo!r}",
            )

    def _asignar_precio_base(self, precio_base: float) -> None:
        """Convierte y valida el precio base (encadena la excepcion original).

        Raises:
            ErrorServicioInvalido: Si el precio no es numerico o no es positivo.
        """
        try:
            precio = float(precio_base)
        except (TypeError, ValueError) as original:
            raise ErrorServicioInvalido(
                "El precio base del servicio debe ser un valor numerico",
                detalle=f"valor recibido: {precio_base!r}",
            ) from original
        if precio <= 0:
            raise ErrorServicioInvalido(
                "El precio base del servicio debe ser mayor que cero",
                detalle=f"valor recibido: {precio}",
            )
        self._precio_base = precio

    def _asignar_tarifa_iva(self, tarifa_iva: float) -> None:
        """Valida que la tarifa de IVA este en un rango razonable (0 a 50%).

        Raises:
            ErrorServicioInvalido: Si la tarifa esta fuera del rango permitido.
        """
        try:
            tarifa = float(tarifa_iva)
        except (TypeError, ValueError) as original:
            raise ErrorServicioInvalido(
                "La tarifa de IVA debe ser un valor numerico",
                detalle=f"valor recibido: {tarifa_iva!r}",
            ) from original
        if not 0 <= tarifa <= 0.5:
            raise ErrorServicioInvalido(
                "La tarifa de IVA debe estar entre 0.0 (exento) y 0.5",
                detalle=f"valor recibido: {tarifa}",
            )
        self._tarifa_iva = tarifa

    @property
    def codigo(self) -> str:
        return self._codigo

    @property
    def precio_base(self) -> float:
        return self._precio_base

    @property
    def tarifa_iva(self) -> float:
        return self._tarifa_iva

    def calcular_impuesto(
        self, tarifa: float | None = None, costo: float | None = None
    ) -> float:
        """Sobrecarga simulada del calculo de impuestos.

        Formas de uso:
            - ``calcular_impuesto()``: IVA propio sobre el precio base.
            - ``calcular_impuesto(tarifa=0.05)``: tarifa personalizada.
            - ``calcular_impuesto(costo=100000)``: IVA propio sobre un monto dado.

        Raises:
            ErrorServicioInvalido: Si los argumentos son inconsistentes.
        """
        tarifa_efectiva = self._tarifa_iva if tarifa is None else tarifa
        base_imponible = self._precio_base if costo is None else costo
        if not isinstance(tarifa_efectiva, (int, float)) or not 0 <= tarifa_efectiva <= 0.5:
            raise ErrorServicioInvalido(
                "La tarifa de impuesto debe ser un numero entre 0.0 y 0.5",
                detalle=f"tarifa recibida: {tarifa!r}",
            )
        if not isinstance(base_imponible, (int, float)) or base_imponible < 0:
            raise ErrorServicioInvalido(
                "La base imponible debe ser un numero no negativo",
                detalle=f"costo recibido: {costo!r}",
            )
        return round(base_imponible * tarifa_efectiva, 2)

    def aplicar_descuento(
        self, porcentaje: float | None = None, monto: float | None = None
    ) -> float:
        """Sobrecarga simulada del descuento sobre el precio base.

        Formas de uso:
            - ``aplicar_descuento(porcentaje=10)``: 10% del precio base.
            - ``aplicar_descuento(monto=50000)``: descuento por monto fijo.

        Debe indicarse exactamente una de las dos formas.

        Raises:
            ErrorServicioInvalido: Si faltan o sobran argumentos.
        """
        if (porcentaje is None) == (monto is None):
            raise ErrorServicioInvalido(
                "Indique el descuento como 'porcentaje' o como 'monto', no ambos ni ninguno"
            )
        if porcentaje is not None:
            if not isinstance(porcentaje, (int, float)) or not 0 < porcentaje <= 100:
                raise ErrorServicioInvalido(
                    "El porcentaje de descuento debe estar entre 1 y 100",
                    detalle=f"valor recibido: {porcentaje!r}",
                )
            return round(self._precio_base * (porcentaje / 100), 2)
        if not isinstance(monto, (int, float)) or monto <= 0:
            raise ErrorServicioInvalido(
                "El monto de descuento debe ser un numero positivo",
                detalle=f"valor recibido: {monto!r}",
            )
        if monto >= self._precio_base:
            raise ErrorServicioInvalido(
                "El descuento no puede ser mayor o igual al precio base del servicio",
                detalle=f"monto: {monto} | precio base: {self._precio_base}",
            )
        return round(monto, 2)

    @abstractmethod
    def calcular_costo(self, duracion_horas: float = 1.0) -> float:
        """Costo total del servicio para una duracion dada (IVA incluido)."""

    @abstractmethod
    def _validar_parametros_especificos(self) -> None:
        """Valida los atributos propios de cada subclase (sobrescrito)."""

    def obtener_descripcion(self) -> str:
        """Descripcion generica; cada subclase la enriquece (sobrescritura)."""
        return f"[{self._codigo}] {self._nombre} | precio base: ${self._precio_base:,.2f} COP"


class ServicioSala(Servicio):
    """Alquiler de salas de reuniones/eventos por hora.

    Sobreprecio del 10% si incluye proyector y 5% adicional para salas de
    50 o mas personas.

    Attributes:
        _capacidad: Aforo de la sala (entre 2 y 500 personas).
        _incluye_proyector: Indica si la sala cuenta con proyector.
    """

    RECARGO_PROYECTOR = 0.10
    RECARGO_AFORO = 0.05
    UMBRAL_AFORO_GRANDE = 50

    def __init__(
        self,
        codigo: str,
        nombre: str,
        precio_base: float,
        capacidad: int,
        incluye_proyector: bool = False,
        tarifa_iva: float = Servicio.IVA_POR_DEFECTO,
    ) -> None:
        super().__init__(codigo, nombre, precio_base, tarifa_iva)
        self._capacidad = capacidad
        self._incluye_proyector = incluye_proyector
        self._validar_parametros_especificos()

    def _validar_parametros_especificos(self) -> None:
        """Valida el aforo y la bandera de proyector (metodo sobrescrito)."""
        try:
            capacidad_valida = int(self._capacidad)
        except (TypeError, ValueError) as original:
            raise ErrorServicioInvalido(
                "La capacidad de la sala debe ser un numero entero",
                detalle=f"valor recibido: {self._capacidad!r}",
            ) from original
        if not 2 <= capacidad_valida <= 500:
            raise ErrorServicioInvalido(
                "La capacidad de la sala debe estar entre 2 y 500 personas",
                detalle=f"valor recibido: {capacidad_valida}",
            )
        if not isinstance(self._incluye_proyector, bool):
            raise ErrorServicioInvalido(
                "incluye_proyector debe ser verdadero o falso",
                detalle=f"valor recibido: {self._incluye_proyector!r}",
            )
        self._capacidad = capacidad_valida

    @property
    def capacidad(self) -> int:
        return self._capacidad

    @property
    def incluye_proyector(self) -> bool:
        return self._incluye_proyector

    def calcular_costo(self, duracion_horas: float = 1.0) -> float:
        """Sobrescribe la formula: precio x horas + recargos + IVA."""
        if not isinstance(duracion_horas, (int, float)) or duracion_horas <= 0:
            raise ErrorServicioInvalido(
                "La duracion del servicio debe ser un numero positivo de horas",
                detalle=f"valor recibido: {duracion_horas!r}",
            )
        subtotal = self._precio_base * duracion_horas
        if self._incluye_proyector:
            subtotal *= 1 + self.RECARGO_PROYECTOR
        if self._capacidad >= self.UMBRAL_AFORO_GRANDE:
            subtotal *= 1 + self.RECARGO_AFORO
        return round(subtotal * (1 + self._tarifa_iva), 2)

    def obtener_descripcion(self) -> str:
        """Enriquece la descripcion base con los detalles de la sala."""
        base = super().obtener_descripcion()
        proyector = "con proyector" if self._incluye_proyector else "sin proyector"
        return f"{base} | Sala para {self._capacidad} personas, {proyector}"


class ServicioEquipo(Servicio):
    """Alquiler de equipos de computo por hora y por unidad.

    Aplica descuento por jornada completa (8 horas o mas) del 10% antes
    de calcular el IVA.

    Attributes:
        _unidades: Cantidad de equipos a alquilar (entre 1 y 100).
    """

    DESCUENTO_JORNADA = 0.10
    HORAS_JORNADA = 8

    def __init__(
        self,
        codigo: str,
        nombre: str,
        precio_base: float,
        unidades: int,
        tarifa_iva: float = Servicio.IVA_POR_DEFECTO,
    ) -> None:
        super().__init__(codigo, nombre, precio_base, tarifa_iva)
        self._unidades = unidades
        self._validar_parametros_especificos()

    def _validar_parametros_especificos(self) -> None:
        """Valida la cantidad de unidades del alquiler (metodo sobrescrito)."""
        try:
            unidades_validas = int(self._unidades)
        except (TypeError, ValueError) as original:
            raise ErrorServicioInvalido(
                "La cantidad de equipos debe ser un numero entero",
                detalle=f"valor recibido: {self._unidades!r}",
            ) from original
        if not 1 <= unidades_validas <= 100:
            raise ErrorServicioInvalido(
                "La cantidad de equipos debe estar entre 1 y 100",
                detalle=f"valor recibido: {unidades_validas}",
            )
        self._unidades = unidades_validas

    @property
    def unidades(self) -> int:
        return self._unidades

    def calcular_costo(self, duracion_horas: float = 1.0) -> float:
        """Sobrescribe la formula: precio x unidades x horas - jornada + IVA."""
        if not isinstance(duracion_horas, (int, float)) or duracion_horas <= 0:
            raise ErrorServicioInvalido(
                "La duracion del servicio debe ser un numero positivo de horas",
                detalle=f"valor recibido: {duracion_horas!r}",
            )
        subtotal = self._precio_base * self._unidades * duracion_horas
        if duracion_horas >= self.HORAS_JORNADA:
            subtotal *= 1 - self.DESCUENTO_JORNADA
        return round(subtotal * (1 + self._tarifa_iva), 2)

    def obtener_descripcion(self) -> str:
        """Enriquece la descripcion base con los detalles del equipo."""
        base = super().obtener_descripcion()
        return f"{base} | {self._unidades} equipo(s) por hora, jornada 8h con 10% de descuento"


class ServicioConsultoria(Servicio):
    """Consultoria tecnologica por hora segun nivel del consultor.

    La consultoria se encuentra exenta de IVA (tarifa 0 por contrato) y aplica
    5% de descuento en sesiones de 10 horas o mas.

    Attributes:
        _nivel_experiencia: Nivel del consultor (JUNIOR, SENIOR o EXPERTO).
    """

    NIVELES_EXPERIENCIA = {"JUNIOR": 1.0, "SENIOR": 1.5, "EXPERTO": 2.0}
    DESCUENTO_SESION_LARGA = 0.05
    HORAS_SESION_LARGA = 10

    def __init__(
        self,
        codigo: str,
        nombre: str,
        precio_base: float,
        nivel_experiencia: str = "JUNIOR",
    ) -> None:
        super().__init__(codigo, nombre, precio_base, tarifa_iva=0.0)
        self._nivel_experiencia = nivel_experiencia
        self._validar_parametros_especificos()

    def _validar_parametros_especificos(self) -> None:
        """Valida el nivel de experiencia del consultor (metodo sobrescrito)."""
        nivel = (
            self._nivel_experiencia.strip().upper()
            if isinstance(self._nivel_experiencia, str)
            else ""
        )
        if nivel not in self.NIVELES_EXPERIENCIA:
            raise ErrorServicioInvalido(
                "El nivel de experiencia debe ser JUNIOR, SENIOR o EXPERTO",
                detalle=f"valor recibido: {self._nivel_experiencia!r}",
            )
        self._nivel_experiencia = nivel

    @property
    def nivel_experiencia(self) -> str:
        return self._nivel_experiencia

    def calcular_costo(self, duracion_horas: float = 1.0) -> float:
        """Sobrescribe la formula: tarifa x horas x nivel, exenta de IVA."""
        if not isinstance(duracion_horas, (int, float)) or duracion_horas <= 0:
            raise ErrorServicioInvalido(
                "La duracion de la consultoria debe ser un numero positivo de horas",
                detalle=f"valor recibido: {duracion_horas!r}",
            )
        multiplicador = self.NIVELES_EXPERIENCIA[self._nivel_experiencia]
        subtotal = self._precio_base * duracion_horas * multiplicador
        if duracion_horas >= self.HORAS_SESION_LARGA:
            subtotal *= 1 - self.DESCUENTO_SESION_LARGA
        return round(subtotal, 2)

    def obtener_descripcion(self) -> str:
        """Enriquece la descripcion base con los detalles de la consultoria."""
        base = super().obtener_descripcion()
        return f"{base} | Consultoria nivel {self._nivel_experiencia}, exenta de IVA"
