"""Simulacion del sistema Software FJ (UNAD 213023_466 - Fase 4).

Ejecuta 19 operaciones completas: clientes validos e invalidos, servicios
correctos e incorrectos y reservas exitosas y fallidas. Toda la ejecucion se
protege con manejo avanzado de excepciones (``try/except``,
``try/except/else``, ``try/except/finally`` y encadenamiento con
``raise ... from ...``) para que ningun fallo detenga la aplicacion: la
simulacion permanece activa hasta el informe final.

Autor: Santiago (Simulacion).
"""

from models.cliente import Cliente
from models.reserva import GestorReservas
from models.servicios import ServicioConsultoria, ServicioEquipo, ServicioSala
from utils.excepciones import ErrorSoftwareFJ
from utils.logger import obtener_logger

logger = obtener_logger("software_fj.simulacion")


def formatear_peso(valor: float) -> str:
    """Da formato de moneda a un valor en pesos colombianos."""
    return f"${valor:,.2f} COP"


def ejecutar_operacion(numero: int, descripcion: str, accion) -> bool:
    """Ejecuta una operacion de forma segura y reporta el resultado.

    Demonstra los cuatro patrones de manejo de excepciones:
        - ``try/except``: captura errores de negocio del sistema.
        - ``except Exception``: captura fallos inesperados sin detener la app.
        - ``else``: se ejecuta solo cuando la operacion fue exitosa.
        - ``finally``: se ejecuta siempre, exista error o no.

    Returns:
        ``True`` si la operacion termino correctamente, ``False`` si fallo.
    """
    print(f"\n=== Operacion {numero:02d}: {descripcion} ===")
    logger.info("Operacion %02d iniciada: %s", numero, descripcion)
    try:
        accion()
    except ErrorSoftwareFJ as error:
        causa = (
            f" | Causa raiz: {type(error.__cause__).__name__}: {error.__cause__}"
            if error.__cause__
            else ""
        )
        print(f"[FALLO CONTROLADO] {error}{causa}")
        logger.exception("Operacion %02d fallo de forma controlada", numero)
        return False
    except Exception as error:  # noqa: BLE001 - la app nunca debe detenerse
        print(f"[FALLO INESPERADO CONTROLADO] {type(error).__name__}: {error}")
        logger.exception("Operacion %02d fallo inesperadamente", numero)
        return False
    else:
        print("[OK] Operacion completada sin errores")
        logger.info("Operacion %02d finalizada con exito", numero)
        return True
    finally:
        print(f"[FIN] La simulacion permanece activa tras la operacion {numero:02d}")


def construir_operaciones():
    """Prepara el gestor en memoria y las 19 operaciones de la simulacion."""
    gestor = GestorReservas()
    clientes: dict[str, Cliente] = {}
    servicios: dict[str, object] = {}
    reservas_creadas: list[str] = []

    def registrar_cliente_valido(nombre, apellido, documento, email, telefono):
        def accion():
            cliente = Cliente(nombre, apellido, documento, email, telefono)
            clientes[documento] = cliente
            print(f"Registrado: {cliente.obtener_descripcion()}")
            print(f"Ficha tecnica: {cliente!r}")

        return accion

    def registrar_cliente_invalido(**datos):
        def accion():
            Cliente(**datos)
            print("ADVERTENCIA: este cliente no deberia haberse registrado")

        return accion

    def crear_sala():
        def accion():
            sala = ServicioSala("SAL-001", "Sala Ejecutiva Norte", 45000, 12, True)
            servicios["sala"] = sala
            print(sala.obtener_descripcion())
            impuesto_normal = sala.calcular_impuesto()
            impuesto_tarifa = sala.calcular_impuesto(tarifa=0.05)
            impuesto_monto = sala.calcular_impuesto(costo=100000)
            print(
                f"Sobrecarga de impuestos -> por defecto: {formatear_peso(impuesto_normal)} "
                f"| tarifa 5%: {formatear_peso(impuesto_tarifa)} "
                f"| sobre 100000: {formatear_peso(impuesto_monto)}"
            )

        return accion

    def crear_equipo():
        def accion():
            equipo = ServicioEquipo("EQU-002", "Portatiles Alta Gama", 18000, 10)
            servicios["equipo"] = equipo
            print(equipo.obtener_descripcion())
            descuento_porcentaje = equipo.aplicar_descuento(porcentaje=10)
            descuento_monto = equipo.aplicar_descuento(monto=5000)
            print(
                f"Sobrecarga de descuentos -> 10%: {formatear_peso(descuento_porcentaje)} "
                f"| monto fijo 5000: {formatear_peso(descuento_monto)}"
            )

        return accion

    def crear_consultoria():
        def accion():
            consultoria = ServicioConsultoria(
                "CON-003", "Auditoria de Arquitectura", 90000, "SENIOR"
            )
            servicios["consultoria"] = consultoria
            print(consultoria.obtener_descripcion())

        return accion

    def crear_servicio_invalido(clase, **datos):
        def accion():
            clase(**datos)
            print("ADVERTENCIA: este servicio no deberia haberse creado")

        return accion

    def demostrar_polimorfismo():
        def accion():
            print("Un mismo mensaje, tres comportamientos distintos:\n")
            for servicio in servicios.values():
                print(f"- {servicio.obtener_descripcion()}")
                print(
                    f"  Costo por 6 horas: {formatear_peso(servicio.calcular_costo(6))}"
                )

        return accion

    def reserva_exitosa():
        def accion():
            reserva = gestor.crear(clientes["1007223344"], servicios["sala"], 4)
            reservas_creadas.append(reserva.codigo)
            print(f"Creada en estado pendiente: {reserva}")
            gestor.confirmar(reserva.codigo)
            print(f"Confirmada: {reserva}")

        return accion

    def reserva_duracion_invalida():
        def accion():
            gestor.crear(clientes["1007223344"], servicios["equipo"], -5)

        return accion

    def reserva_tipo_incorrecto():
        def accion():
            gestor.crear(servicios["sala"], servicios["equipo"], 3)

        return accion

    def exceder_disponibilidad():
        def accion():
            creadas = 0
            try:
                for _ in range(4):
                    gestor.crear(clientes["1029384756"], servicios["consultoria"], 2)
                    creadas += 1
            except ErrorSoftwareFJ as error:
                print(f"[RECHAZO] {error}")
                logger.warning("Disponibilidad agotada tras %d reservas", creadas)
            finally:
                print(f"Reservas activas creadas antes del rechazo: {creadas}")

        return accion

    def cancelar_y_repetir():
        def accion():
            codigo = reservas_creadas[0]
            cancelada = gestor.cancelar(codigo, "Cambio de agenda del cliente")
            print(f"Cancelada correctamente: {cancelada}")
            gestor.cancelar(codigo, "Segundo intento de cancelacion")

        return accion

    def confirmar_cancelada():
        def accion():
            gestor.confirmar(reservas_creadas[0])

        return accion

    def encadenar_excepciones():
        def accion():
            try:
                gestor.confirmar("RES-9999")
            except ErrorSoftwareFJ as original:
                raise ErrorSoftwareFJ(
                    "Fallo al confirmar la reserva, verifique el codigo"
                ) from original

        return accion

    def descuento_invalido():
        def accion():
            servicios["equipo"].aplicar_descuento(porcentaje=10, monto=5000)

        return accion

    def resistencia_final():
        def accion():
            gestor.crear(clientes["80123546"], servicios["sala"], 8)
            print("Sistema operativo tras 18 operaciones previas")

        return accion

    operaciones = [
        ("Registro de cliente valido (Julian Cano)", registrar_cliente_valido("Julian", "Cano", "1007223344", "julian.cano@softwarefj.com", "3104567890")),
        ("Registro de cliente valido (Valeria Gomez)", registrar_cliente_valido("Valeria", "Gomez", "1029384756", "valeria.gomez@softwarefj.com", "3119876543")),
        ("Registro de cliente valido (Andres Mendoza)", registrar_cliente_valido("Andres", "Mendoza", "80123546", "andres.mendoza@softwarefj.com", "3205558899")),
        ("Cliente invalido: correo mal formado", registrar_cliente_invalido(nombre="Pedro", apellido="Ruiz", documento="79855123", email="pedro.ruiz@correo", telefono="3123456789")),
        ("Cliente invalido: celular invalido", registrar_cliente_invalido(nombre="Laura", apellido="Perez", documento="52678901", email="laura.perez@softwarefj.com", telefono="12345")),
        ("Cliente invalido: documento con letras", registrar_cliente_invalido(nombre="Ana", apellido="Torres", documento="AB12345", email="ana.torres@softwarefj.com", telefono="3156789423")),
        ("Servicio correcto: Sala Ejecutiva con impuestos sobrecargados", crear_sala()),
        ("Servicio correcto: Equipos con descuentos sobrecargados", crear_equipo()),
        ("Servicio correcto: Consultoria SENIOR", crear_consultoria()),
        ("Servicio invalido: precio base negativo", crear_servicio_invalido(ServicioSala, codigo="SAL-004", nombre="Sala Fantasma", precio_base=-5000, capacidad=10)),
        ("Servicio invalido: codigo mal formado", crear_servicio_invalido(ServicioEquipo, codigo="equipos-9", nombre="Equipos Rotulados", precio_base=10000, unidades=5)),
        ("Polimorfismo: costo y descripcion de cada servicio", demostrar_polimorfismo()),
        ("Reserva exitosa: Julian contrata la sala y la confirma", reserva_exitosa()),
        ("Reserva fallida: duracion negativa", reserva_duracion_invalida()),
        ("Reserva fallida: tipo de argumento incorrecto", reserva_tipo_incorrecto()),
        ("Disponibilidad: Valeria supera el limite de reservas activas", exceder_disponibilidad()),
        ("Cancelacion y doble cancelacion de la misma reserva", cancelar_y_repetir()),
        ("Confirmacion de una reserva ya cancelada", confirmar_cancelada()),
        ("Encadenamiento de excepciones con codigo inexistente", encadenar_excepciones()),
        ("Descuento invalido: porcentaje y monto a la vez", descuento_invalido()),
        ("Resistencia: nueva reserva tras todos los fallos previos", resistencia_final()),
    ]
    return gestor, operaciones


def main() -> int:
    """Ejecuta la simulacion completa y presenta el informe final."""
    logger.info("Iniciando simulacion del sistema Software FJ")
    print("=" * 72)
    print(" Bienvenido a Software FJ - Sistema de Reservas (UNAD 213023_466)")
    print(" Datos 100% en memoria | Log de eventos y errores: logs/software_fj.log")
    print("=" * 72)

    gestor, operaciones = construir_operaciones()
    resultados = [
        ejecutar_operacion(numero, descripcion, accion)
        for numero, (descripcion, accion) in enumerate(operaciones, start=1)
    ]

    exitosas = sum(resultados)
    fallidas = len(resultados) - exitosas
    resumen = gestor.resumen()

    print("\n" + "=" * 72)
    print(" INFORME FINAL DE LA SIMULACION")
    print("=" * 72)
    print(f" Operaciones ejecutadas : {len(resultados)}")
    print(f" Exitosas               : {exitosas}")
    print(f" Fallidas (controladas) : {fallidas}")
    print(f" Cierres inesperados    : 0 (la aplicacion permanecio activa)")
    print(f" Reservas en memoria    : {resumen}")
    for reserva in gestor:
        print(f"   - {reserva}")
    print("=" * 72)

    logger.info(
        "Simulacion finalizada | exitosas=%d fallidas=%d reservas=%d",
        exitosas,
        fallidas,
        resumen["total"],
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
