# --------------------------------------------
# Nombre: Laura Daniela Troncoso Rodríguez
# Curso: Programación (213023) - Fase 4
# Módulo: Ejecución principal y simulación de 11 operaciones (Software FJ)
# --------------------------------------------

from excepciones import (
    ErrorOperacionSistema,
    ErrorParametroServicio,
    ErrorReserva,
    ErrorSoftwareFJ,
    ErrorValidacionCliente,
    logger_fj,
)
from modelos import (
    AlquilerEquipo,
    AsesoriaEspecializada,
    Cliente,
    Reserva,
    ReservaSala,
    Servicio,
)


class GestorSoftwareFJ:
    """Administra clientes, servicios y reservas en listas internas (sin base de datos)."""

    def __init__(self):
        self.clientes: list[Cliente] = []
        self.servicios: list[Servicio] = []
        self.reservas: list[Reserva] = []

    def registrar_cliente(self, id_cliente: str, nombre: str, correo: str, telefono: str, es_vip: bool = False) -> Cliente:
        try:
            if any(c.identificador == id_cliente.strip().upper() for c in self.clientes):
                raise ErrorValidacionCliente(f"Ya existe un cliente con el ID '{id_cliente}'.")
            cliente = Cliente(id_cliente, nombre, correo, telefono, es_vip=es_vip)
        except ErrorValidacionCliente as exc:
            logger_fj.error("Error en registro de cliente: %s", exc)
            raise ErrorOperacionSistema("No fue posible completar el registro del cliente.") from exc
        except ValueError as exc:
            logger_fj.error("Error de formato en ID de cliente: %s", exc)
            raise ErrorOperacionSistema("Identificador de cliente inválido.") from exc
        else:
            self.clientes.append(cliente)
            logger_fj.info("Cliente registrado correctamente: %s", cliente.resumen())
            return cliente
        finally:
            logger_fj.info("Fin del intento de registro de cliente (ID: %s).", id_cliente)

    def registrar_servicio(self, servicio: Servicio) -> Servicio:
        try:
            if not isinstance(servicio, Servicio):
                raise ErrorParametroServicio("Solo se pueden registrar instancias válidas de Servicio.")
            if any(s.identificador == servicio.identificador for s in self.servicios):
                raise ErrorParametroServicio(f"El servicio '{servicio.identificador}' ya está registrado.")
        except ErrorParametroServicio as exc:
            logger_fj.error("Error al registrar servicio: %s", exc)
            raise ErrorOperacionSistema("Fallo al incorporar el servicio al catálogo.") from exc
        else:
            self.servicios.append(servicio)
            logger_fj.info("Servicio registrado: %s", servicio.resumen())
            return servicio
        finally:
            logger_fj.info("Verificación de catálogo de servicios finalizada.")

    def crear_y_confirmar_reserva(
        self,
        id_reserva: str,
        id_cliente: str,
        codigo_servicio: str,
        duracion: float,
        impuesto: float = 0.0,
        descuento: float = 0.0,
        confirmar_inmediato: bool = True,
        **kwargs_servicio,
    ) -> Reserva:
        try:
            cliente = next((c for c in self.clientes if c.identificador == id_cliente.strip().upper()), None)
            if cliente is None:
                raise ErrorReserva(f"Cliente con ID '{id_cliente}' no encontrado.")

            servicio = next((s for s in self.servicios if s.identificador == codigo_servicio.strip().upper()), None)
            if servicio is None:
                raise ErrorReserva(f"Servicio con código '{codigo_servicio}' no encontrado.")

            reserva = Reserva(
                id_reserva=id_reserva,
                cliente=cliente,
                servicio=servicio,
                duracion=duracion,
                impuesto=impuesto,
                descuento=descuento,
                **kwargs_servicio,
            )
            if confirmar_inmediato:
                reserva.confirmar()
        except (ErrorReserva, ErrorParametroServicio) as exc:
            logger_fj.error("Error procesando reserva '%s': %s", id_reserva, exc)
            raise ErrorOperacionSistema(f"No se pudo procesar la reserva '{id_reserva}'.") from exc
        else:
            self.reservas.append(reserva)
            logger_fj.info("Reserva almacenada en memoria: %s", reserva.resumen())
            return reserva
        finally:
            logger_fj.info("Ciclo de procesamiento de reserva '%s' concluido.", id_reserva)


def ejecutar_simulacion_software_fj() -> None:
    """Ejecuta 11 operaciones completas (válidas e inválidas) demostrando estabilidad."""
    gestor = GestorSoftwareFJ()
    logger_fj.info("=== INICIO DE SIMULACIÓN SOFTWARE FJ (SIN BASE DE DATOS) ===")

    operaciones = [
        (
            "Op 1 - Registro cliente válido (Laura Troncoso)",
            lambda: gestor.registrar_cliente("CLI-01", "Laura Troncoso", "laura.fj@correo.com", "3105550101", es_vip=True),
        ),
        (
            "Op 2 - Registro cliente inválido (correo erróneo)",
            lambda: gestor.registrar_cliente("CLI-02", "Carlos Ruiz", "correo_sin_arroba", "3001112233"),
        ),
        (
            "Op 3 - Registro cliente válido (Camila Gómez)",
            lambda: gestor.registrar_cliente("CLI-03", "Camila Gómez", "camila.gomez@empresa.co", "3158889900"),
        ),
        (
            "Op 4 - Creación servicio válido (ReservaSala)",
            lambda: gestor.registrar_servicio(
                ReservaSala("SAL-101", "Sala de Conferencias Norte", tarifa_base=85000.0, capacidad_maxima=15)
            ),
        ),
        (
            "Op 5 - Creación servicio válido (AlquilerEquipo)",
            lambda: gestor.registrar_servicio(
                AlquilerEquipo("EQ-201", "Estación Workstation i7", tarifa_base=45000.0, unidades_disponibles=4)
            ),
        ),
        (
            "Op 6 - Creación servicio válido (AsesoriaEspecializada)",
            lambda: gestor.registrar_servicio(
                AsesoriaEspecializada("ASE-301", "Auditoría de Arquitectura", tarifa_base=120000.0, especialidad="Cloud & POO")
            ),
        ),
        (
            "Op 7 - Creación servicio inválido (tarifa negativa)",
            lambda: gestor.registrar_servicio(
                ReservaSala("SAL-999", "Sala Inválida", tarifa_base=-10000.0, capacidad_maxima=10)
            ),
        ),
        (
            "Op 8 - Reserva exitosa de sala con descuento e IVA",
            lambda: gestor.crear_y_confirmar_reserva(
                "RES-001", "CLI-01", "SAL-101", duracion=3.0, impuesto=0.19, descuento=10.0, asistentes=10
            ),
        ),
        (
            "Op 9 - Reserva exitosa de alquiler de equipos",
            lambda: gestor.crear_y_confirmar_reserva(
                "RES-002", "CLI-03", "EQ-201", duracion=2.0, impuesto=0.19, descuento=0.0, cantidad=2
            ),
        ),
        (
            "Op 10 - Reserva fallida (excede capacidad de sala)",
            lambda: gestor.crear_y_confirmar_reserva(
                "RES-003", "CLI-01", "SAL-101", duracion=2.0, asistentes=30
            ),
        ),
        (
            "Op 11 - Reserva fallida (cliente inexistente)",
            lambda: gestor.crear_y_confirmar_reserva("RES-004", "CLI-999", "ASE-301", duracion=1.5),
        ),
    ]

    for indice, (descripcion, accion) in enumerate(operaciones, start=1):
        print(f"\n--- {descripcion} ---")
        try:
            resultado = accion()
        except ErrorSoftwareFJ as exc:
            causa = f" | Causa raíz: {exc.__cause__}" if exc.__cause__ else ""
            print(f"[CONTROLADO] {exc}{causa}")
        else:
            print(f"[OK] {resultado.resumen()}")
        finally:
            print(f"[ESTADO] Operación #{indice} finalizada. Sistema activo.")

    if gestor.reservas:
        print("\n--- Operación extra: Cancelación controlada de reserva ---")
        try:
            mensaje_cancelacion = gestor.reservas[-1].cancelar("Reprogramación del cliente")
            print(f"[OK] {mensaje_cancelacion}")
        except ErrorReserva as exc:
            print(f"[CONTROLADO] {exc}")

    print("\n=== RESUMEN FINAL EN MEMORIA (SIN BASE DE DATOS) ===")
    print(f"Clientes registrados: {len(gestor.clientes)}")
    print(f"Servicios registrados: {len(gestor.servicios)}")
    print(f"Reservas registradas: {len(gestor.reservas)}")
    logger_fj.info("=== FIN DE SIMULACIÓN SOFTWARE FJ ===")


if __name__ == "__main__":
    ejecutar_simulacion_software_fj()
