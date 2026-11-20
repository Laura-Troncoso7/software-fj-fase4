# --------------------------------------------
# Nombre: Laura Daniela Troncoso Rodríguez
# Curso: Programación (213023) - Fase 4
# Módulo: Modelos orientados a objetos (Software FJ)
# --------------------------------------------

from abc import ABC, abstractmethod
import re
from excepciones import (
    ErrorParametroServicio,
    ErrorReserva,
    ErrorValidacionCliente,
    logger_fj,
)


class EntidadSistema(ABC):
    """Clase abstracta base que representa entidades generales de Software FJ."""

    def __init__(self, identificador: str):
        if not isinstance(identificador, str) or not identificador.strip():
            raise ValueError("El identificador de la entidad debe ser un texto no vacío.")
        self._identificador = identificador.strip().upper()

    @property
    def identificador(self) -> str:
        """Retorna el identificador único de la entidad."""
        return self._identificador

    @abstractmethod
    def resumen(self) -> str:
        """Devuelve una representación resumida de la entidad."""


class Cliente(EntidadSistema):
    """Representa un cliente con encapsulación de datos personales y validaciones estrictas."""

    def __init__(self, id_cliente: str, nombre: str, correo: str, telefono: str, es_vip: bool = False):
        super().__init__(id_cliente)
        self.nombre = nombre
        self.correo = correo
        self.telefono = telefono
        self._es_vip = bool(es_vip)

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str):
        if not isinstance(valor, str) or len(valor.strip()) < 3:
            raise ErrorValidacionCliente("El nombre del cliente debe tener al menos 3 caracteres.")
        self._nombre = valor.strip()

    @property
    def correo(self) -> str:
        return self._correo

    @correo.setter
    def correo(self, valor: str):
        patron = r"^[\w\.-]+@[\w\.-]+\.\w{2,}$"
        if not isinstance(valor, str) or not re.match(patron, valor.strip()):
            raise ErrorValidacionCliente(f"Correo electrónico inválido: '{valor}'.")
        self._correo = valor.strip().lower()

    @property
    def telefono(self) -> str:
        return self._telefono

    @telefono.setter
    def telefono(self, valor: str):
        digitos = re.sub(r"\D", "", str(valor))
        if len(digitos) < 7:
            raise ErrorValidacionCliente(f"Teléfono inválido: '{valor}'. Debe tener al menos 7 dígitos.")
        self._telefono = digitos

    @property
    def es_vip(self) -> bool:
        return self._es_vip

    def resumen(self) -> str:
        vip_tag = "VIP" if self._es_vip else "Estándar"
        return f"Cliente [{self._identificador}] {self._nombre} ({vip_tag}) - {self._correo}"


class Servicio(EntidadSistema, ABC):
    """Clase abstracta para los servicios ofrecidos por Software FJ."""

    def __init__(self, codigo_servicio: str, nombre: str, tarifa_base: float, disponible: bool = True):
        super().__init__(codigo_servicio)
        if not isinstance(nombre, str) or not nombre.strip():
            raise ErrorParametroServicio("El nombre del servicio es obligatorio.")
        try:
            tarifa = float(tarifa_base)
        except (TypeError, ValueError) as exc:
            raise ErrorParametroServicio("La tarifa base debe ser un valor numérico.") from exc

        if tarifa <= 0:
            raise ErrorParametroServicio("La tarifa base debe ser mayor que cero.")

        self._nombre = nombre.strip()
        self._tarifa_base = tarifa
        self._disponible = bool(disponible)

    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def tarifa_base(self) -> float:
        return self._tarifa_base

    @property
    def disponible(self) -> bool:
        return self._disponible

    def cambiar_disponibilidad(self, estado: bool):
        self._disponible = bool(estado)

    @abstractmethod
    def validar_parametros(self, duracion: float, **kwargs) -> None:
        """Valida duración y parámetros específicos de cada tipo de servicio."""

    @abstractmethod
    def describir_servicio(self) -> str:
        """Retorna una descripción detallada del servicio especializado."""

    @abstractmethod
    def _calcular_subtotal_base(self, duracion: float, **kwargs) -> float:
        """Calcula el subtotal según la lógica particular de cada servicio."""

    def calcular_costo(
        self,
        duracion: float = 1.0,
        impuesto: float = 0.0,
        descuento: float = 0.0,
        **kwargs,
    ) -> float:
        """Sobrecarga de método mediante parámetros opcionales y **kwargs."""
        self.validar_parametros(duracion, **kwargs)

        if not (0.0 <= impuesto <= 1.0):
            raise ErrorParametroServicio("El impuesto debe estar expresado entre 0.0 y 1.0 (ej. 0.19).")
        if not (0.0 <= descuento < 100.0):
            raise ErrorParametroServicio("El descuento debe estar entre 0% y menos del 100%.")

        subtotal = self._calcular_subtotal_base(duracion, **kwargs)
        if subtotal <= 0:
            raise ErrorParametroServicio("Cálculo inconsistente: el subtotal resultante no es válido.")

        con_descuento = subtotal * (1.0 - (descuento / 100.0))
        total_final = con_descuento * (1.0 + impuesto)
        return round(max(0.0, total_final), 2)

    def resumen(self) -> str:
        estado = "Disponible" if self._disponible else "No disponible"
        return f"Servicio [{self._identificador}] {self._nombre} | Base: ${self._tarifa_base:,.2f} | {estado}"


class ReservaSala(Servicio):
    """Servicio especializado para reserva de salas de reuniones o capacitación."""

    def __init__(self, codigo_servicio: str, nombre: str, tarifa_base: float, capacidad_maxima: int, disponible: bool = True):
        super().__init__(codigo_servicio, nombre, tarifa_base, disponible)
        if not isinstance(capacidad_maxima, int) or capacidad_maxima <= 0:
            raise ErrorParametroServicio("La capacidad máxima de la sala debe ser un entero positivo.")
        self._capacidad_maxima = capacidad_maxima

    def validar_parametros(self, duracion: float, **kwargs) -> None:
        if duracion is None or float(duracion) <= 0:
            raise ErrorParametroServicio("La duración en horas para reservar una sala debe ser mayor que 0.")
        asistentes = kwargs.get("asistentes")
        if asistentes is not None:
            if not isinstance(asistentes, int) or asistentes <= 0:
                raise ErrorParametroServicio("El número de asistentes debe ser un entero positivo.")
            if asistentes > self._capacidad_maxima:
                raise ErrorParametroServicio(
                    f"Los asistentes ({asistentes}) superan la capacidad máxima ({self._capacidad_maxima})."
                )

    def describir_servicio(self) -> str:
        return f"[Sala] {self._nombre} (Capacidad máx: {self._capacidad_maxima} personas, Tarifa/hora: ${self._tarifa_base:,.2f})"

    def _calcular_subtotal_base(self, duracion: float, **kwargs) -> float:
        return self._tarifa_base * float(duracion)


class AlquilerEquipo(Servicio):
    """Servicio especializado para alquiler de equipos tecnológicos."""

    def __init__(self, codigo_servicio: str, nombre: str, tarifa_base: float, unidades_disponibles: int, disponible: bool = True):
        super().__init__(codigo_servicio, nombre, tarifa_base, disponible)
        if not isinstance(unidades_disponibles, int) or unidades_disponibles < 0:
            raise ErrorParametroServicio("Las unidades disponibles deben ser un entero mayor o igual a 0.")
        self._unidades_disponibles = unidades_disponibles
        if self._unidades_disponibles == 0:
            self._disponible = False

    def validar_parametros(self, duracion: float, **kwargs) -> None:
        if duracion is None or float(duracion) <= 0:
            raise ErrorParametroServicio("El tiempo de alquiler (días/horas) debe ser mayor que 0.")
        cantidad = kwargs.get("cantidad", 1)
        if not isinstance(cantidad, int) or cantidad <= 0:
            raise ErrorParametroServicio("La cantidad de equipos a alquilar debe ser un entero positivo.")
        if cantidad > self._unidades_disponibles:
            raise ErrorParametroServicio(
                f"Cantidad solicitada ({cantidad}) excede el inventario ({self._unidades_disponibles})."
            )

    def describir_servicio(self) -> str:
        return (
            f"[Equipo] {self._nombre} (Stock: {self._unidades_disponibles} und., "
            f"Tarifa base: ${self._tarifa_base:,.2f})"
        )

    def _calcular_subtotal_base(self, duracion: float, **kwargs) -> float:
        cantidad = kwargs.get("cantidad", 1)
        return self._tarifa_base * float(duracion) * cantidad


class AsesoriaEspecializada(Servicio):
    """Servicio especializado para consultoría y asesoría técnica."""

    def __init__(self, codigo_servicio: str, nombre: str, tarifa_base: float, especialidad: str, disponible: bool = True):
        super().__init__(codigo_servicio, nombre, tarifa_base, disponible)
        if not isinstance(especialidad, str) or not especialidad.strip():
            raise ErrorParametroServicio("La especialidad de la asesoría no puede estar vacía.")
        self._especialidad = especialidad.strip()

    def validar_parametros(self, duracion: float, **kwargs) -> None:
        if duracion is None or float(duracion) < 0.5:
            raise ErrorParametroServicio("La asesoría especializada requiere al menos 0.5 horas de duración.")

    def describir_servicio(self) -> str:
        return f"[Asesoría - {self._especialidad}] {self._nombre} (Tarifa/hora: ${self._tarifa_base:,.2f})"

    def _calcular_subtotal_base(self, duracion: float, **kwargs) -> float:
        recargo_urgencia = 1.25 if kwargs.get("urgente", False) else 1.0
        return self._tarifa_base * float(duracion) * recargo_urgencia


class Reserva(EntidadSistema):
    """Integra cliente, servicio, duración y estado, gestionando confirmación y cancelación."""

    ESTADOS_VALIDOS = {"PENDIENTE", "CONFIRMADA", "CANCELADA"}

    def __init__(
        self,
        id_reserva: str,
        cliente: Cliente,
        servicio: Servicio,
        duracion: float,
        impuesto: float = 0.0,
        descuento: float = 0.0,
        **kwargs_servicio,
    ):
        super().__init__(id_reserva)
        if not isinstance(cliente, Cliente):
            raise ErrorReserva("Debe asociarse un objeto Cliente válido a la reserva.")
        if not isinstance(servicio, Servicio):
            raise ErrorReserva("Debe asociarse un objeto Servicio válido a la reserva.")
        if not servicio.disponible:
            raise ErrorReserva(f"El servicio '{servicio.nombre}' no está disponible para reservar.")

        self._cliente = cliente
        self._servicio = servicio
        self._duracion = duracion
        self._kwargs_servicio = kwargs_servicio
        self._estado = "PENDIENTE"
        self._costo_total = servicio.calcular_costo(
            duracion=duracion,
            impuesto=impuesto,
            descuento=descuento,
            **kwargs_servicio,
        )

    @property
    def estado(self) -> str:
        return self._estado

    @property
    def costo_total(self) -> float:
        return self._costo_total

    def confirmar(self) -> str:
        """Confirma la reserva aplicando bloques try/except/else/finally."""
        try:
            if self._estado == "CANCELADA":
                raise ErrorReserva(f"No se puede confirmar la reserva {self._identificador} porque está CANCELADA.")
            if not self._servicio.disponible:
                raise ErrorReserva(f"El servicio '{self._servicio.nombre}' dejó de estar disponible.")
            self._servicio.validar_parametros(self._duracion, **self._kwargs_servicio)
        except ErrorReserva as exc:
            logger_fj.error("Fallo al confirmar reserva %s: %s", self._identificador, exc)
            raise
        else:
            self._estado = "CONFIRMADA"
            mensaje = f"Reserva {self._identificador} CONFIRMADA para {self._cliente.nombre} (${self._costo_total:,.2f})."
            logger_fj.info(mensaje)
            return mensaje
        finally:
            logger_fj.info("Auditoría de confirmación ejecutada para reserva %s [Estado actual: %s].", self._identificador, self._estado)

    def cancelar(self, motivo: str = "Cancelación solicitada") -> str:
        """Cancela la reserva si su estado actual lo permite."""
        if self._estado == "CANCELADA":
            raise ErrorReserva(f"La reserva {self._identificador} ya se encuentra CANCELADA.")
        self._estado = "CANCELADA"
        mensaje = f"Reserva {self._identificador} CANCELADA ({motivo})."
        logger_fj.warning(mensaje)
        return mensaje

    def resumen(self) -> str:
        return (
            f"Reserva [{self._identificador}] | Estado: {self._estado} | "
            f"{self._cliente.nombre} -> {self._servicio.nombre} | Total: ${self._costo_total:,.2f}"
        )
