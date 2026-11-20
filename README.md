# Software FJ — Fase 4 (Prácticas Simuladas)

Sistema integral orientado a objetos en Python para la gestión de **clientes**, **servicios** (*ReservaSala*, *AlquilerEquipo*, *AsesoriaEspecializada*) y **reservas** para la empresa **Software FJ**, desarrollado sin base de datos (objetos y listas en memoria) con registro de eventos y errores en `software_fj.log`.

## Estructura del proyecto
- `excepciones.py`: excepciones personalizadas (`ErrorSoftwareFJ`, `ErrorValidacionCliente`, `ErrorParametroServicio`, `ErrorReserva`, `ErrorOperacionSistema`), encadenamiento de excepciones y configuración del registro en `software_fj.log`.
- `modelos.py`: clase abstracta `EntidadSistema`, `Cliente` con encapsulación y validaciones estrictas, clase abstracta `Servicio`, clases derivadas con polimorfismo y sobrecarga de métodos para el cálculo de costos (`calcular_costo`), y `Reserva` con confirmación, cancelación y bloques `try/except/else/finally`.
- `main.py`: clase `GestorSoftwareFJ` y ejecución de 11 operaciones simuladas (válidas e inválidas) manteniendo la estabilidad del sistema.

## Ejecución local
1. Asegúrate de tener `excepciones.py`, `modelos.py` y `main.py` en la misma carpeta.
2. Ejecuta:
   ```bash
   python main.py
