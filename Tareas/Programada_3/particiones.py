#!/usr/bin/env python3
"""Simulador de memoria con particiones fijas (Tarea Programada 3).

Divide la memoria principal en particiones de tamaño fijo y asigna a cada una un
único proceso, usando First Fit (primer ajuste) o Best Fit (mejor ajuste). Los
procesos que no caben esperan en una cola y se revisan cada vez que se libera una
partición. El sobrante de una partición ocupada es fragmentación interna y no se
puede aprovechar.

Uso:
    python particiones.py

Todo se maneja desde un menú de consola. Para repetir una sesión sin escribir cada
opción se puede redirigir la entrada:
    python particiones.py < casos/escenario_1_ajuste_exacto.txt
"""

import sys
from collections import deque
from dataclasses import dataclass

# Estrategias de asignación
FIRST_FIT = "first"
BEST_FIT = "best"
NOMBRES_ESTRATEGIA = {
    FIRST_FIT: "First Fit (primer ajuste)",
    BEST_FIT: "Best Fit (mejor ajuste)",
}

# Estados de un proceso
ESPERANDO = "Esperando"
EN_MEMORIA = "En memoria"
FINALIZADO = "Finalizado"

# Un proceso mayor que la partición más grande nunca podrá asignarse. El enunciado
# pide rechazarlo (True). Con False se deja en la cola de espera indefinidamente.
RECHAZAR_SI_EXCEDE_MAXIMO = True


class ErrorSimulacion(Exception):
    """Error de validación o de uso; el mensaje se muestra tal cual al usuario."""


class SalirPrograma(Exception):
    """Se acabó la entrada (Ctrl+D / Ctrl+Z o fin del archivo redirigido)."""


@dataclass
class Particion:
    id: int
    tamano: int  # KB, fijo durante toda la simulación
    proceso_id: str | None = None
    usado: int = 0  # KB del proceso que la ocupa (0 si está libre)

    @property
    def libre(self):
        return self.proceso_id is None

    @property
    def sobrante(self):
        """Fragmentación interna si está ocupada; capacidad disponible si está libre."""
        return self.tamano - self.usado


@dataclass
class Proceso:
    id: str
    tamano: int  # KB
    estado: str = ESPERANDO
    particion: int | None = None  # id de la partición asignada


# ---------------------------------------------------------------------------
# Algoritmos de selección de partición (cada uno por separado)
# ---------------------------------------------------------------------------

def buscar_first_fit(particiones, tamano):
    """Primera partición libre, en el orden en que fueron definidas, donde quepa el proceso."""
    for particion in particiones:
        if particion.libre and particion.tamano >= tamano:
            return particion
    return None


def buscar_best_fit(particiones, tamano):
    """Partición libre más pequeña donde quepa el proceso; en empate, la de menor id."""
    elegida = None
    for particion in particiones:
        if not particion.libre or particion.tamano < tamano:
            continue
        if (elegida is None
                or (particion.tamano, particion.id) < (elegida.tamano, elegida.id)):
            elegida = particion
    return elegida


ALGORITMOS = {FIRST_FIT: buscar_first_fit, BEST_FIT: buscar_best_fit}


# ---------------------------------------------------------------------------
# Modelo: memoria, procesos y cola de espera
# ---------------------------------------------------------------------------

class Simulador:
    def __init__(self):
        self.reiniciar()

    def reiniciar(self):
        self.particiones: list[Particion] = []
        self.estrategia: str | None = None
        self.activos: dict[str, Proceso] = {}  # esperando o en memoria
        self.finalizados: list[Proceso] = []
        self.cola: deque[str] = deque()  # ids de procesos esperando, en orden de llegada

    @property
    def hay_procesos(self):
        return bool(self.activos)

    @property
    def listo(self):
        return bool(self.particiones) and self.estrategia is not None

    def configurar_particiones(self, definiciones):
        """definiciones: lista de (id, tamaño) en el orden en que se definen."""
        if self.hay_procesos:
            raise ErrorSimulacion("Hay procesos en el sistema. Reinicie la simulación "
                                  "(opción 8) para cambiar las particiones.")
        if not definiciones:
            raise ErrorSimulacion("Debe haber al menos una partición.")
        ids = [id_ for id_, _ in definiciones]
        if len(set(ids)) != len(ids):
            raise ErrorSimulacion("Los identificadores de partición deben ser únicos.")
        if any(id_ <= 0 or tamano <= 0 for id_, tamano in definiciones):
            raise ErrorSimulacion("Identificadores y tamaños deben ser mayores que cero.")
        self.particiones = [Particion(id_, tamano) for id_, tamano in definiciones]

    def seleccionar_estrategia(self, estrategia):
        if self.hay_procesos:
            raise ErrorSimulacion("Hay procesos en el sistema. Reinicie la simulación "
                                  "(opción 8) para cambiar la estrategia.")
        if estrategia not in ALGORITMOS:
            raise ErrorSimulacion("Estrategia desconocida.")
        self.estrategia = estrategia

    def registrar_proceso(self, id_, tamano):
        """Registra un proceso y trata de asignarlo; si no cabe en ninguna partición
        libre queda esperando. Devuelve el Proceso."""
        if not self.listo:
            raise ErrorSimulacion("Primero configure las particiones (opción 1) y "
                                  "seleccione la estrategia (opción 2).")
        if not id_:
            raise ErrorSimulacion("El identificador del proceso no puede estar vacío.")
        if tamano <= 0:
            raise ErrorSimulacion("El tamaño del proceso debe ser mayor que cero.")
        if id_ in self.activos:
            raise ErrorSimulacion(f"Ya existe un proceso activo con el identificador '{id_}'.")
        mayor = max(p.tamano for p in self.particiones)
        if tamano > mayor and RECHAZAR_SI_EXCEDE_MAXIMO:
            raise ErrorSimulacion(f"'{id_}' requiere {tamano} KB y la partición más grande "
                                  f"es de {mayor} KB: proceso rechazado por imposibilidad "
                                  "de asignación.")
        proceso = Proceso(id_, tamano)
        self.activos[id_] = proceso
        if not self._intentar_asignar(proceso):
            self.cola.append(id_)
        return proceso

    def finalizar_proceso(self, id_):
        """Libera la partición del proceso y revisa la cola. Devuelve la partición
        liberada y la lista de procesos que pasaron de la cola a memoria."""
        proceso = self.activos.get(id_)
        if proceso is None:
            if any(p.id == id_ for p in self.finalizados):
                raise ErrorSimulacion(f"El proceso '{id_}' ya había finalizado.")
            raise ErrorSimulacion(f"El proceso '{id_}' no existe.")
        if proceso.estado != EN_MEMORIA:
            raise ErrorSimulacion(f"El proceso '{id_}' está en la cola de espera, no en memoria.")
        particion = next(p for p in self.particiones if p.id == proceso.particion)
        particion.proceso_id = None
        particion.usado = 0
        proceso.estado = FINALIZADO
        del self.activos[id_]
        self.finalizados.append(proceso)
        return particion, self._revisar_cola()

    def _intentar_asignar(self, proceso):
        particion = ALGORITMOS[self.estrategia](self.particiones, proceso.tamano)
        if particion is None:
            return False
        particion.proceso_id = proceso.id
        particion.usado = proceso.tamano
        proceso.estado = EN_MEMORIA
        proceso.particion = particion.id
        return True

    def _revisar_cola(self):
        """Recorre la cola en orden de llegada. El que no cabe sigue esperando, pero se
        siguen revisando los demás para aprovechar otras particiones libres."""
        asignados = []
        for id_ in list(self.cola):
            proceso = self.activos[id_]
            if self._intentar_asignar(proceso):
                self.cola.remove(id_)
                asignados.append(proceso)
        return asignados

    def estadisticas(self):
        total = sum(p.tamano for p in self.particiones)
        ocupadas = [p for p in self.particiones if not p.libre]
        utilizada = sum(p.usado for p in ocupadas)
        libre = sum(p.tamano for p in self.particiones if p.libre)
        fragmentacion = sum(p.sobrante for p in ocupadas)
        return {
            "total": total,
            "utilizada": utilizada,
            "libre": libre,
            "fragmentacion": fragmentacion,
            "utilizacion": utilizada / total * 100 if total else 0.0,
            "en_espera": len(self.cola),
            "en_memoria": len(ocupadas),
            "finalizados": len(self.finalizados),
        }


# ---------------------------------------------------------------------------
# Presentación
# ---------------------------------------------------------------------------

def tabla(encabezados, filas, derecha=()):
    """Texto de una tabla simple; las columnas en 'derecha' (índices) van alineadas a la derecha."""
    anchos = [max(len(str(fila[i])) for fila in [encabezados] + filas)
              for i in range(len(encabezados))]

    def linea(fila):
        celdas = [str(v).rjust(anchos[i]) if i in derecha else str(v).ljust(anchos[i])
                  for i, v in enumerate(fila)]
        return "  ".join(celdas).rstrip()

    return "\n".join([linea(encabezados), "  ".join("-" * a for a in anchos)]
                     + [linea(f) for f in filas])


def formatear_particiones(sim):
    filas = []
    for p in sim.particiones:
        filas.append([p.id, f"{p.tamano} KB", "Libre" if p.libre else "Ocupada",
                      p.proceso_id or "—", f"{p.sobrante} KB"])
    return tabla(["Partición", "Tamaño", "Estado", "Proceso", "Memoria no utilizada"],
                 filas, derecha=(0, 1, 4))


def formatear_cola(sim):
    if not sim.cola:
        return "La cola de espera está vacía."
    filas = [[posicion, id_, f"{sim.activos[id_].tamano} KB"]
             for posicion, id_ in enumerate(sim.cola, start=1)]
    return tabla(["Orden", "Proceso", "Tamaño"], filas, derecha=(0, 2))


def formatear_estadisticas(sim):
    e = sim.estadisticas()
    ancho = len(str(e["total"])) + 3
    filas = [
        ("Memoria total", f"{e['total']} KB"),
        ("Memoria utilizada por procesos", f"{e['utilizada']} KB"),
        ("Memoria libre", f"{e['libre']} KB"),
        ("Fragmentación interna", f"{e['fragmentacion']} KB"),
        ("Utilización efectiva", f"{e['utilizacion']:.2f} %"),
        ("Procesos en espera", e["en_espera"]),
        ("Procesos en memoria", e["en_memoria"]),
        ("Procesos finalizados", e["finalizados"]),
    ]
    etiqueta = max(len(f[0]) for f in filas)
    lineas = [f"{nombre.ljust(etiqueta)} : {str(valor).rjust(ancho)}" for nombre, valor in filas]
    suma = e["utilizada"] + e["fragmentacion"] + e["libre"]
    verificacion = "OK" if suma == e["total"] else "ERROR"
    lineas.append(f"Verificación: {e['total']} = {e['utilizada']} + {e['fragmentacion']} "
                  f"+ {e['libre']} -> {verificacion}")
    return "\n".join(lineas)


def mostrar_estado(sim):
    print(formatear_particiones(sim))
    if sim.cola:
        print("En espera: " + ", ".join(f"{i} ({sim.activos[i].tamano} KB)" for i in sim.cola))


def mostrar_menu(sim):
    estrategia = NOMBRES_ESTRATEGIA.get(sim.estrategia, "sin seleccionar")
    particiones = f"{len(sim.particiones)} configuradas" if sim.particiones else "sin configurar"
    print("\n" + "=" * 52)
    print("SIMULADOR DE PARTICIONES FIJAS")
    print(f"Particiones: {particiones} | Estrategia: {estrategia}")
    print("=" * 52)
    print("1. Configurar las particiones de memoria")
    print("2. Seleccionar estrategia de asignación")
    print("3. Crear un proceso e intentar asignarlo")
    print("4. Finalizar un proceso en memoria")
    print("5. Consultar el estado de las particiones")
    print("6. Consultar la cola de espera")
    print("7. Mostrar estadísticas de utilización")
    print("8. Reiniciar la simulación")
    print("9. Salir")


# ---------------------------------------------------------------------------
# Entrada de datos
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


def leer_entero_positivo(mensaje):
    """Pide un entero mayor que cero hasta que el usuario escriba uno válido."""
    while True:
        texto = leer(mensaje)
        try:
            valor = int(texto)
        except ValueError:
            print(f"Error: '{texto}' no es un número entero.")
            continue
        if valor <= 0:
            print("Error: el valor debe ser mayor que cero.")
            continue
        return valor


# ---------------------------------------------------------------------------
# Opciones del menú
# ---------------------------------------------------------------------------

def opcion_configurar(sim):
    if sim.hay_procesos:
        raise ErrorSimulacion("Hay procesos en el sistema. Reinicie la simulación "
                              "(opción 8) para cambiar las particiones.")
    cantidad = leer_entero_positivo("Cantidad de particiones: ")
    definiciones = []
    for numero in range(1, cantidad + 1):
        while True:
            id_ = leer_entero_positivo(f"ID de la partición #{numero}: ")
            if any(id_ == existente for existente, _ in definiciones):
                print(f"Error: el identificador {id_} ya está en uso.")
                continue
            break
        tamano = leer_entero_positivo(f"Tamaño de la partición {id_} (KB): ")
        definiciones.append((id_, tamano))
    sim.configurar_particiones(definiciones)
    total = sum(t for _, t in definiciones)
    print(f"\nMemoria configurada: {cantidad} particiones, {total} KB en total.")
    print(formatear_particiones(sim))


def opcion_estrategia(sim):
    if sim.hay_procesos:
        raise ErrorSimulacion("Hay procesos en el sistema. Reinicie la simulación "
                              "(opción 8) para cambiar la estrategia.")
    print("1. First Fit (primer ajuste)")
    print("2. Best Fit (mejor ajuste)")
    eleccion = leer("Estrategia: ")
    estrategias = {"1": FIRST_FIT, "2": BEST_FIT}
    if eleccion not in estrategias:
        raise ErrorSimulacion(f"'{eleccion}' no es una estrategia válida (1 o 2).")
    sim.seleccionar_estrategia(estrategias[eleccion])
    print(f"Estrategia seleccionada: {NOMBRES_ESTRATEGIA[sim.estrategia]}.")


def opcion_crear_proceso(sim):
    if not sim.listo:
        raise ErrorSimulacion("Primero configure las particiones (opción 1) y "
                              "seleccione la estrategia (opción 2).")
    id_ = leer("ID del proceso: ")
    tamano = leer_entero_positivo("Tamaño del proceso (KB): ")
    proceso = sim.registrar_proceso(id_, tamano)
    if proceso.estado == EN_MEMORIA:
        particion = next(p for p in sim.particiones if p.id == proceso.particion)
        print(f"\n{proceso.id} ({proceso.tamano} KB) asignado a la partición "
              f"{particion.id} ({particion.tamano} KB). "
              f"Fragmentación interna: {particion.sobrante} KB.")
    else:
        libre = sim.estadisticas()["libre"]
        print(f"\nNo hay una partición libre donde quepan {proceso.tamano} KB: "
              f"{proceso.id} pasa a la cola de espera.")
        if libre >= proceso.tamano:
            print(f"Hay {libre} KB libres en total, pero ninguna partición libre alcanza "
                  "por sí sola (los procesos no se pueden repartir entre particiones).")
    mostrar_estado(sim)


def opcion_finalizar(sim):
    if not sim.particiones:
        raise ErrorSimulacion("Aún no hay particiones configuradas.")
    id_ = leer("ID del proceso que terminó: ")
    particion, asignados = sim.finalizar_proceso(id_)
    print(f"\n{id_} finalizó y la partición {particion.id} ({particion.tamano} KB) quedó libre.")
    for proceso in asignados:
        destino = next(p for p in sim.particiones if p.id == proceso.particion)
        print(f"{proceso.id} ({proceso.tamano} KB) sale de la cola y entra a la partición "
              f"{destino.id} ({destino.tamano} KB). Fragmentación interna: {destino.sobrante} KB.")
    mostrar_estado(sim)


def opcion_estado(sim):
    if not sim.particiones:
        raise ErrorSimulacion("Aún no hay particiones configuradas.")
    mostrar_estado(sim)


def opcion_cola(sim):
    if not sim.particiones:
        raise ErrorSimulacion("Aún no hay particiones configuradas.")
    print(formatear_cola(sim))


def opcion_estadisticas(sim):
    if not sim.particiones:
        raise ErrorSimulacion("Aún no hay particiones configuradas.")
    print(formatear_estadisticas(sim))


def opcion_reiniciar(sim):
    if leer("Se borrarán las particiones, la estrategia y los procesos. ¿Continuar? (s/n): ").lower() == "s":
        sim.reiniciar()
        print("Simulación reiniciada.")
    else:
        print("No se reinició la simulación.")


def main():
    for flujo in (sys.stdin, sys.stdout):
        try:
            flujo.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass
    sim = Simulador()
    opciones = {
        "1": opcion_configurar,
        "2": opcion_estrategia,
        "3": opcion_crear_proceso,
        "4": opcion_finalizar,
        "5": opcion_estado,
        "6": opcion_cola,
        "7": opcion_estadisticas,
        "8": opcion_reiniciar,
    }
    try:
        while True:
            mostrar_menu(sim)
            eleccion = leer("Opción: ")
            if eleccion == "9":
                print("Fin de la simulación.")
                return 0
            accion = opciones.get(eleccion)
            if accion is None:
                print(f"Error: '{eleccion}' no es una opción del menú (1 a 9).")
                continue
            try:
                accion(sim)
            except ErrorSimulacion as error:
                print(f"Error: {error}")
    except SalirPrograma:
        print("Fin de la entrada. Saliendo del programa.")
        return 0
    except KeyboardInterrupt:
        print("\nPrograma interrumpido.")
        return 130


if __name__ == "__main__":
    sys.exit(main())
