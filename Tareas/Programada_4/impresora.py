#!/usr/bin/env python3
"""Simulador de impresora 3D compartida (Tarea Programada 4).

Una única impresora 3D es solicitada por varios procesos. Al iniciar se elige cómo
actúa el sistema operativo cuando la impresora está ocupada:

    BLOQUEO  El proceso queda BLOQUEADO y su solicitud se rechaza. Nadie lo atiende
             automáticamente: debe volver a solicitar la impresora (reintento manual).
    COLA     El proceso pasa a ESPERANDO en una cola FIFO. Al liberarse la impresora
             se asigna automáticamente al primero de la cola.

La simulación es por eventos (sin hilos ni temporizadores): el usuario decide cuándo
llega una solicitud y cuándo termina un proceso de usar la impresora.

Uso:
    python impresora.py

Para repetir una sesión sin escribir cada opción se puede redirigir la entrada:
    python impresora.py < casos/ejemplo_seccion4_bloqueo.txt
"""

import sys
from collections import deque

# Modos de administración
BLOQUEO = "bloqueo"
COLA = "cola"
NOMBRES_MODO = {
    BLOQUEO: "BLOQUEO (sin cola)",
    COLA: "COLA DE ESPERA (FIFO)",
}

# Estados de un proceso
LISTO = "LISTO"
USANDO = "USANDO"
BLOQUEADO = "BLOQUEADO"
ESPERANDO = "ESPERANDO"

# Resultados de una solicitud
ASIGNADA = "ASIGNADA"
RESULTADO_BLOQUEADO = "BLOQUEADO"
EN_COLA = "EN COLA"


class ErrorSimulacion(Exception):
    """Operación inválida; el mensaje se muestra al usuario y el programa sigue."""


class SalirPrograma(Exception):
    """Se terminó la entrada (fin de archivo) o el usuario eligió salir."""


# ---------------------------------------------------------------------------
# Lógica de la simulación
# ---------------------------------------------------------------------------

class Simulador:
    def __init__(self, modo):
        self.modo = modo
        self.procesos = {}         # id -> estado; el orden del dict es el de creación
        self.usuario = None        # proceso que tiene la impresora (None = libre)
        self.cola = deque()        # ids en espera, en orden FIFO (solo en modo COLA)
        self.siguiente_numero = 1
        # Contadores del reto adicional
        self.solicitudes = 0       # solicitudes realizadas (incluye reintentos)
        self.no_inmediatas = 0     # solicitudes que no obtuvieron la impresora al instante
        self.asignaciones = 0      # veces que un proceso recibió la impresora

    # -- Consultas -----------------------------------------------------------

    @property
    def bloqueados(self):
        return [p for p, e in self.procesos.items() if e == BLOQUEADO]

    def resolver_id(self, texto):
        """Convierte lo escrito por el usuario ('P2', 'p2' o '2') en un id existente."""
        limpio = texto.strip().upper()
        if limpio.isdigit():
            limpio = f"P{int(limpio)}"
        if limpio not in self.procesos:
            raise ErrorSimulacion(f"El proceso '{texto.strip()}' no existe.")
        return limpio

    # -- Operaciones ---------------------------------------------------------

    def crear_proceso(self):
        pid = f"P{self.siguiente_numero}"
        self.siguiente_numero += 1
        self.procesos[pid] = LISTO
        return pid

    def solicitar(self, pid):
        """Solicitud de la impresora. Devuelve ASIGNADA, RESULTADO_BLOQUEADO o EN_COLA."""
        estado = self.procesos[pid]
        if estado == USANDO:
            raise ErrorSimulacion(f"{pid} ya está usando la impresora; no puede solicitarla de nuevo.")
        if estado == ESPERANDO:
            raise ErrorSimulacion(f"{pid} ya está en la cola de espera; no puede solicitarla de nuevo.")

        # Un reintento de un proceso BLOQUEADO es una solicitud nueva y cuenta como tal.
        self.solicitudes += 1
        if self.usuario is None:
            self._asignar(pid)
            return ASIGNADA

        self.no_inmediatas += 1
        if self.modo == COLA:
            self.procesos[pid] = ESPERANDO
            self.cola.append(pid)
            return EN_COLA
        self.procesos[pid] = BLOQUEADO
        return RESULTADO_BLOQUEADO

    def liberar(self):
        """Termina el uso de la impresora. Devuelve (proceso que terminó, proceso que la recibe o None)."""
        if self.usuario is None:
            raise ErrorSimulacion("La impresora ya está libre; no hay nada que liberar.")
        terminado = self.usuario
        self.procesos[terminado] = LISTO
        self.usuario = None
        siguiente = None
        if self.modo == COLA and self.cola:
            siguiente = self.cola.popleft()
            self._asignar(siguiente)
        return terminado, siguiente

    def _asignar(self, pid):
        self.usuario = pid
        self.procesos[pid] = USANDO
        self.asignaciones += 1


# ---------------------------------------------------------------------------
# Presentación
# ---------------------------------------------------------------------------

def formatear_cola(cola):
    return "[" + ", ".join(cola) + "]"


def formatear_estado(sim):
    lineas = ["", "--- ESTADO DEL SISTEMA ---", f"Modo        : {NOMBRES_MODO[sim.modo]}"]
    if sim.usuario is None:
        lineas.append("Impresora   : LIBRE")
    else:
        lineas.append(f"Impresora   : OCUPADA por {sim.usuario}")
    if sim.modo == COLA:
        lineas.append(f"Cola (FIFO) : {formatear_cola(sim.cola) if sim.cola else 'vacía'}")
    else:
        lineas.append(f"Bloqueados  : {', '.join(sim.bloqueados) if sim.bloqueados else 'ninguno'}")

    if sim.procesos:
        lineas.append("")
        lineas.append("Proceso  Estado")
        lineas.append("-------  ---------")
        for pid, estado in sim.procesos.items():
            lineas.append(f"{pid:<7}  {estado}")
    else:
        lineas.append("Procesos    : ninguno creado todavía")

    # Lo interesante del modo BLOQUEO: el dispositivo libre con procesos que lo necesitan.
    if sim.usuario is None and sim.bloqueados:
        lineas.append("")
        lineas.append("Aviso: la impresora está LIBRE pero hay procesos BLOQUEADOS que la necesitan "
                      f"({', '.join(sim.bloqueados)}). Nadie la asigna: deben reintentar la solicitud.")
    return "\n".join(lineas)


def formatear_estadisticas(sim):
    return "\n".join([
        "",
        "--- ESTADÍSTICAS ---",
        f"Solicitudes realizadas                          : {sim.solicitudes}",
        f"Solicitudes sin impresora inmediata             : {sim.no_inmediatas}",
        f"Asignaciones exitosas de la impresora           : {sim.asignaciones}",
    ])


def mostrar_menu(sim):
    print()
    print("=" * 44)
    print(f"IMPRESORA 3D | Modo: {NOMBRES_MODO[sim.modo]}")
    print("=" * 44)
    print("1. Crear un proceso")
    print("2. Solicitar impresora")
    print("3. Liberar impresora")
    print("4. Mostrar estado del sistema")
    print("5. Salir")


# ---------------------------------------------------------------------------
# Entrada
# ---------------------------------------------------------------------------

def leer(mensaje):
    try:
        valor = input(mensaje)
    except EOFError:
        print()
        raise SalirPrograma
    if not sys.stdin.isatty():
        print(valor)  # al redirigir la entrada se repite lo leído para que la traza se entienda
    return valor.strip()


def elegir_modo():
    print("=== SIMULADOR DE IMPRESORA 3D ===")
    print()
    print("Seleccione el modo de administración:")
    print()
    print("1. BLOQUEO (sin cola)")
    print("2. COLA DE ESPERA (FIFO)")
    print()
    while True:
        opcion = leer("Seleccione una opción: ")
        if opcion == "1":
            return BLOQUEO
        if opcion == "2":
            return COLA
        print(f"Error: '{opcion}' no es una opción válida. Escriba 1 o 2.")


# ---------------------------------------------------------------------------
# Opciones del menú
# ---------------------------------------------------------------------------

def opcion_crear(sim):
    pid = sim.crear_proceso()
    print(f"Proceso {pid} creado (estado {LISTO}).")


def opcion_solicitar(sim):
    if not sim.procesos:
        raise ErrorSimulacion("No hay procesos. Cree uno con la opción 1.")
    pid = sim.resolver_id(leer("Proceso que solicita la impresora (ej. P1): "))
    reintento = sim.procesos[pid] == BLOQUEADO
    resultado = sim.solicitar(pid)
    if reintento:
        print(f"{pid} reintenta -> {resultado}")
    else:
        print(f"{pid} solicita impresora -> {resultado}")
    if resultado == EN_COLA:
        print(f"Cola: {formatear_cola(sim.cola)}")
    elif resultado == RESULTADO_BLOQUEADO:
        print(f"{pid} queda BLOQUEADO; deberá volver a solicitar la impresora.")


def opcion_liberar(sim):
    terminado, siguiente = sim.liberar()
    print(f"{terminado} libera impresora.")
    if siguiente is not None:
        print(f"{siguiente} recibe impresora automáticamente.")
        print(f"Cola: {formatear_cola(sim.cola)}" if sim.cola else "Cola: vacía")
    else:
        print("Impresora: LIBRE")
        if sim.bloqueados:
            if len(sim.bloqueados) == 1:
                print(f"{sim.bloqueados[0]} continúa BLOQUEADO.")
            else:
                print(f"{' y '.join(sim.bloqueados)} continúan BLOQUEADOS.")


def cierre(sim):
    """Resultados finales: contadores y procesos que quedaron sin atender."""
    print(formatear_estadisticas(sim))
    pendientes = sim.bloqueados + list(sim.cola)
    if pendientes:
        estados = ", ".join(f"{p} ({sim.procesos[p]})" for p in pendientes)
        print()
        print(f"Procesos que terminaron la simulación sin obtener la impresora: {estados}")
    if sim.usuario is not None:
        print(f"{sim.usuario} seguía usando la impresora al salir.")
    print()
    print("Fin de la simulación.")


ACCIONES = {
    "1": opcion_crear,
    "2": opcion_solicitar,
    "3": opcion_liberar,
}


def main():
    if not sys.stdout.isatty():
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except (AttributeError, OSError):
            pass
    sim = None
    try:
        sim = Simulador(elegir_modo())
        print(f"\nModo seleccionado: {NOMBRES_MODO[sim.modo]}. No se puede cambiar durante la simulación.")
        while True:
            mostrar_menu(sim)
            opcion = leer("Opción: ")
            if opcion == "5":
                break
            if opcion == "4":
                print(formatear_estado(sim))
                continue
            accion = ACCIONES.get(opcion)
            if accion is None:
                print(f"Error: '{opcion}' no es una opción válida. Elija un número del 1 al 5.")
                continue
            try:
                accion(sim)
            except ErrorSimulacion as error:
                print(f"Error: {error}")
    except SalirPrograma:
        pass
    if sim is not None:
        cierre(sim)


if __name__ == "__main__":
    main()
