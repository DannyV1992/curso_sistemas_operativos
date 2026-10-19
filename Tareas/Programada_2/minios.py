#!/usr/bin/env python3
"""MiniOS: simulador de planificación de procesos (Tarea Programada 2).

Simula un computador con un único CPU y una cola de procesos listos. Soporta dos
políticas: FIFO (sin expropiación) y Round Robin (el proceso pierde el CPU al
agotar su quantum y vuelve al final de la cola).

Uso:
    python minios.py [--archivo procesos.csv] [--politica fifo|rr] [--quantum Q]
                     [--costo-cambio N] [--comparar] [--salida CARPETA]

Entrada:  CSV con columnas id,llegada,duracion
Salidas:  resultados.csv y eventos.txt (se sobrescriben en cada corrida) en la
          carpeta indicada con --salida (por defecto, la carpeta actual).
"""

import argparse
import csv
import re
import sys
from collections import deque
from dataclasses import dataclass
from pathlib import Path

# Los archivos por defecto se buscan junto al script, sin importar desde dónde se ejecute
CARPETA_BASE = Path(__file__).resolve().parent
COLUMNAS = ["id", "llegada", "duracion"]
COLUMNAS_RESULTADOS = ["id", "llegada", "duracion", "inicio", "fin",
                       "espera", "retorno", "respuesta", "expropiaciones"]

# Políticas y valores por defecto
FIFO = "fifo"
RR = "rr"
POLITICAS = (FIFO, RR)
POLITICA_DEFECTO = RR
QUANTUM_DEFECTO = 3
ARCHIVO_DEFECTO = "procesos.csv"

# Estados de un proceso
NUEVO = "Nuevo"
LISTO = "Listo"
EJECUTANDO = "Ejecutando"
TERMINADO = "Terminado"


@dataclass
class Proceso:
    id: str
    llegada: int
    duracion: int
    linea: int = 0  # línea del archivo de entrada (solo para mensajes de error)
    estado: str = NUEVO
    restante: int = 0
    inicio: int | None = None  # primera vez que obtiene el CPU
    fin: int | None = None
    espera: int | None = None
    retorno: int | None = None
    respuesta: int | None = None
    expropiaciones: int = 0  # veces que perdió el CPU sin haber terminado

    def __post_init__(self):
        self.restante = self.duracion


@dataclass
class Configuracion:
    archivo: Path
    politica: str
    quantum: int | None  # None cuando la política es FIFO
    costo_cambio: int
    comparar: bool
    salida: Path


@dataclass
class Simulacion:
    """Lo que devuelve una simulación además de los procesos actualizados."""
    eventos: list  # tuplas (tiempo, texto)
    tiempo_total: int
    tiempo_util: int  # unidades en que el CPU ejecutó procesos
    cambios_contexto: int
    tiempo_cambios: int  # unidades perdidas en cambios de contexto (solo con --costo-cambio)


# ---------------------------------------------------------------------------
# Lectura y validación de los datos
# ---------------------------------------------------------------------------

def _a_entero(texto, campo):
    """Convierte texto a entero. Devuelve (valor, mensaje_de_error)."""
    if texto == "":
        return None, f"el campo '{campo}' está vacío"
    if not re.fullmatch(r"-?[0-9]+", texto):
        return None, f"el valor de '{campo}' ('{texto}') no es un número entero"
    return int(texto), None


def leer_procesos(ruta):
    """Lee el CSV de procesos.

    Devuelve (procesos, errores) donde errores es una lista de (linea, mensaje).
    Línea 0 indica un error que afecta a todo el archivo.
    """
    ruta = Path(ruta)
    if not ruta.is_file():
        return [], [(0, f"el archivo '{ruta}' no existe")]

    try:
        with open(ruta, newline="", encoding="utf-8-sig") as f:
            lector = csv.reader(f)
            filas = [(lector.line_num, fila) for fila in lector]
    except (OSError, UnicodeDecodeError, csv.Error) as e:
        return [], [(0, f"no se pudo leer el archivo '{ruta}': {e}")]

    # Las líneas totalmente en blanco se ignoran
    filas = [(n, [c.strip() for c in fila]) for n, fila in filas if any(c.strip() for c in fila)]
    if not filas:
        return [], [(0, f"el archivo '{ruta}' está vacío")]

    numero, encabezado = filas[0]
    if [c.lower() for c in encabezado] != COLUMNAS:
        return [], [(numero, "encabezado inválido, se esperaba: " + ",".join(COLUMNAS))]
    if len(filas) == 1:
        return [], [(0, f"el archivo '{ruta}' no contiene procesos")]

    procesos, errores = [], []
    for numero, fila in filas[1:]:
        if len(fila) < len(COLUMNAS):
            errores.append((numero, f"fila incompleta ({len(fila)} de {len(COLUMNAS)} columnas)"))
            continue
        if len(fila) > len(COLUMNAS):
            errores.append((numero, f"la fila tiene demasiadas columnas ({len(fila)} en lugar de {len(COLUMNAS)})"))
            continue

        llegada, err_llegada = _a_entero(fila[1], "llegada")
        duracion, err_duracion = _a_entero(fila[2], "duracion")
        for err in (err_llegada, err_duracion):
            if err:
                errores.append((numero, err))
        if err_llegada or err_duracion:
            continue
        procesos.append(Proceso(fila[0], llegada, duracion, linea=numero))

    return procesos, errores


def validar_procesos(procesos):
    """Valida las reglas de negocio. Devuelve una lista de (linea, mensaje)."""
    errores = []
    vistos = {}
    for p in procesos:
        if p.id == "":
            errores.append((p.linea, "el identificador está vacío"))
        elif p.id in vistos:
            errores.append((p.linea, f"el identificador '{p.id}' está duplicado (ya aparece en la línea {vistos[p.id]})"))
        else:
            vistos[p.id] = p.linea
        if p.llegada < 0:
            errores.append((p.linea, f"el tiempo de llegada no puede ser negativo ({p.llegada})"))
        if p.duracion <= 0:
            errores.append((p.linea, f"la duración debe ser mayor que cero ({p.duracion})"))
    return errores


def formatear_errores(errores):
    """Devuelve el texto de los errores de datos."""
    lineas = ["No se puede ejecutar la simulación. Se encontraron errores en los datos:"]
    for linea, mensaje in sorted(errores, key=lambda e: e[0]):
        prefijo = f"  Línea {linea}: " if linea else "  "
        lineas.append(prefijo + mensaje)
    return "\n".join(lineas)


def copiar_procesos(procesos):
    """Copia limpia (sin estado de simulación) para correr otra política sobre los mismos datos."""
    return [Proceso(p.id, p.llegada, p.duracion, linea=p.linea) for p in procesos]


# ---------------------------------------------------------------------------
# Parámetros de la línea de comandos
# ---------------------------------------------------------------------------

class _Parser(argparse.ArgumentParser):
    """ArgumentParser que reporta sus errores en español y termina con código 2."""

    def error(self, message):
        self.print_usage(sys.stderr)
        print(f"Error en los parámetros: {message}", file=sys.stderr)
        sys.exit(2)


def _crear_parser():
    parser = _Parser(
        prog="minios.py",
        allow_abbrev=False,
        description="MiniOS: simulador de planificación de procesos (FIFO y Round Robin).",
    )
    parser.add_argument("--archivo", default=None,
                        help=f"ruta del CSV con los procesos (por defecto {ARCHIVO_DEFECTO})")
    parser.add_argument("--politica", default=POLITICA_DEFECTO,
                        help=f"política de planificación: fifo o rr (por defecto {POLITICA_DEFECTO})")
    parser.add_argument("--quantum", default=None,
                        help=f"entero mayor que cero; solo se usa con rr (por defecto {QUANTUM_DEFECTO})")
    parser.add_argument("--costo-cambio", default="0", dest="costo_cambio",
                        help="[extra] unidades de tiempo que consume cada cambio de contexto (por defecto 0)")
    parser.add_argument("--comparar", action="store_true",
                        help="[extra] ejecuta FIFO y Round Robin sobre el mismo archivo y los muestra lado a lado")
    parser.add_argument("--salida", default=".",
                        help="carpeta donde se escriben resultados.csv y eventos.txt (por defecto la actual)")
    return parser


def resolver_archivo(texto):
    """Busca el archivo en la carpeta actual, junto al script y en casos/ (en ese orden).

    La extensión .csv es opcional: 'cpu_ocioso' equivale a 'cpu_ocioso.csv'.
    """
    ruta = Path(texto)
    candidatas = [ruta]
    if ruta.suffix.lower() != ".csv":
        candidatas.append(ruta.with_name(ruta.name + ".csv"))
    for candidata in candidatas:
        if candidata.is_file():
            return candidata
        if not candidata.is_absolute():
            for base in (CARPETA_BASE, CARPETA_BASE / "casos"):
                if (base / candidata).is_file():
                    return base / candidata
    return ruta  # leer_procesos informará que no existe


def leer_parametros(argv=None):
    """Interpreta y valida los parámetros. Devuelve (Configuracion, errores)."""
    args = _crear_parser().parse_args(argv)
    errores = []

    politica = args.politica.strip().lower()
    if politica not in POLITICAS:
        errores.append(f"política desconocida '{args.politica}': use 'fifo' o 'rr'")

    # El quantum solo importa con Round Robin (o al comparar); con fifo se ignora
    usa_quantum = politica == RR or args.comparar
    quantum = QUANTUM_DEFECTO
    if usa_quantum and args.quantum is not None:
        quantum, err = _a_entero(args.quantum.strip(), "quantum")
        if err:
            errores.append(f"quantum inválido: {err}")
        elif quantum <= 0:
            errores.append(f"el quantum debe ser un entero mayor que cero (se recibió {quantum})")

    costo, err = _a_entero(args.costo_cambio.strip(), "costo-cambio")
    if err:
        errores.append(f"costo de cambio inválido: {err}")
    elif costo < 0:
        errores.append(f"el costo de cambio de contexto no puede ser negativo (se recibió {costo})")

    if errores:
        return None, errores
    return Configuracion(
        archivo=resolver_archivo(args.archivo or ARCHIVO_DEFECTO),
        politica=politica,
        quantum=quantum if usa_quantum else None,
        costo_cambio=costo,
        comparar=args.comparar,
        salida=Path(args.salida),
    ), []


def formatear_errores_parametros(errores):
    lineas = ["No se puede ejecutar la simulación. Parámetros inválidos:"]
    lineas += [f"  {e}" for e in errores]
    return "\n".join(lineas)


# ---------------------------------------------------------------------------
# Simulación
# ---------------------------------------------------------------------------

class Simulador:
    """Motor de la simulación: un CPU, una cola de listos y un reloj entero.

    quantum=None equivale a FIFO (el proceso conserva el CPU hasta terminar).
    El reloj salta de evento en evento (llegada, fin del quantum, fin del proceso o
    fin de un cambio de contexto), lo que da el mismo resultado que avanzar de a una
    unidad pero permite simular duraciones muy grandes.

    En cada instante t las acciones ocurren en este orden:
      0. Si terminó un cambio de contexto (--costo-cambio), el proceso empieza a ejecutar.
      1. Si el proceso actual ya consumió su duración, termina en t.
      2. Si el CPU quedó libre, entra el primero de la cola.
      3. Llegan los procesos de t (en el orden del archivo): con el CPU libre arrancan
         de inmediato; si no, entran al final de la cola.
      4. Si el actual agotó su quantum: con cola no vacía es expropiado y entra al final
         (después de los que acaban de llegar); con cola vacía sigue con un nuevo quantum.
      5. Si el CPU quedó libre, entra el primero de la cola.
      6. El reloj avanza hasta el próximo evento.
    """

    def __init__(self, procesos, quantum=None, costo_cambio=0):
        self.procesos = procesos
        self.quantum = quantum
        self.costo = costo_cambio
        # sorted es estable: los que llegan en el mismo instante conservan el orden del archivo
        self.llegadas = sorted(procesos, key=lambda p: p.llegada)
        self.siguiente = 0  # índice de la próxima llegada
        self.cola = deque()
        self.actual = None
        self.usado = 0  # unidades consecutivas usadas del quantum vigente
        self.cambiando = 0  # unidades que faltan del cambio de contexto en curso
        self.ultimo = None  # último proceso al que se le asignó el CPU
        self.terminados = 0
        self.t = 0
        self.eventos = []
        self.tiempo_util = 0
        self.cambios_contexto = 0
        self.tiempo_cambios = 0

    def _registrar(self, texto):
        self.eventos.append((self.t, texto))

    def _proxima_llegada(self):
        if self.siguiente < len(self.llegadas):
            return self.llegadas[self.siguiente].llegada
        return None

    def _terminar(self):
        p = self.actual
        p.estado = TERMINADO
        p.fin = self.t
        self._registrar(f"{p.id} termina")
        self.terminados += 1
        self.actual = None

    def _despachar(self, p):
        """Asigna el CPU a p. Un cambio de contexto es asignarlo a un proceso distinto del último."""
        self.actual = p
        self.usado = 0
        if self.ultimo is not None and self.ultimo is not p:
            self.cambios_contexto += 1
            if self.costo > 0:
                self.cambiando = self.costo
                self.tiempo_cambios += self.costo
                self._registrar(f"cambio de contexto {self.ultimo.id} -> {p.id} (costo={self.costo})")
                self.ultimo = p
                return
        self.ultimo = p
        self._comenzar()

    def _comenzar(self):
        p = self.actual
        p.estado = EJECUTANDO
        if p.inicio is None:
            p.inicio = self.t
            self._registrar(f"{p.id} inicia ejecución")
        else:
            self._registrar(f"{p.id} retoma ejecución")

    def _despachar_siguiente(self):
        if self.actual is None and self.cola:
            self._despachar(self.cola.popleft())

    def _procesar_llegadas(self):
        while self._proxima_llegada() == self.t:
            p = self.llegadas[self.siguiente]
            self.siguiente += 1
            p.estado = LISTO
            self._registrar(f"{p.id} llega al sistema")
            if self.actual is None:
                self._despachar(p)  # el CPU estaba libre y la cola vacía
            else:
                self.cola.append(p)
                self._registrar(f"{p.id} entra a la cola")

    def _verificar_quantum(self):
        p = self.actual
        if self.quantum is None or p is None or self.cambiando or self.usado < self.quantum:
            return
        self._registrar(f"{p.id} agota su quantum (restante={p.restante})")
        if self.cola:
            p.estado = LISTO
            p.expropiaciones += 1
            self.cola.append(p)
            self._registrar(f"{p.id} vuelve a la cola")
            self.actual = None
        else:
            self.usado = 0  # cola vacía: sigue con un nuevo quantum, sin expropiación
            self._registrar(f"{p.id} continúa con un nuevo quantum (la cola está vacía)")

    def _avanzar(self):
        proxima = self._proxima_llegada()
        if self.actual is None:
            # Nadie en el CPU ni en la cola: solo puede faltar que lleguen procesos
            self._registrar("CPU ocioso (no hay procesos listos)")
            self.t = proxima
            return
        if self.cambiando:
            paso = self.cambiando
        else:
            paso = self.actual.restante
            if self.quantum is not None:
                paso = min(paso, self.quantum - self.usado)
        if proxima is not None:
            paso = min(paso, proxima - self.t)

        if self.cambiando:
            self.cambiando -= paso
        else:
            self.actual.restante -= paso
            self.usado += paso
            self.tiempo_util += paso
        self.t += paso

    def ejecutar(self):
        while True:
            if self.actual is not None and not self.cambiando and self.actual.estado == LISTO:
                self._comenzar()  # terminó el cambio de contexto
            if self.actual is not None and not self.cambiando and self.actual.restante == 0:
                self._terminar()
            if self.terminados == len(self.procesos):
                break
            self._despachar_siguiente()
            self._procesar_llegadas()
            self._verificar_quantum()
            self._despachar_siguiente()
            self._avanzar()
        return Simulacion(self.eventos, self.t, self.tiempo_util, self.cambios_contexto, self.tiempo_cambios)


def simular_fifo(procesos, costo_cambio=0):
    """FIFO: el proceso que obtiene el CPU lo conserva hasta terminar."""
    return Simulador(procesos, quantum=None, costo_cambio=costo_cambio).ejecutar()


def simular_round_robin(procesos, quantum, costo_cambio=0):
    """Round Robin: máximo `quantum` unidades consecutivas de CPU por turno."""
    return Simulador(procesos, quantum=quantum, costo_cambio=costo_cambio).ejecutar()


# ---------------------------------------------------------------------------
# Métricas
# ---------------------------------------------------------------------------

def calcular_metricas(procesos, simulacion, politica, quantum, costo_cambio=0):
    """Calcula las métricas de cada proceso (válido para ambas políticas) y las globales."""
    for p in procesos:
        p.retorno = p.fin - p.llegada
        p.espera = p.retorno - p.duracion  # tiempo total en la cola de listos, sumando todas las esperas
        p.respuesta = p.inicio - p.llegada

    n = len(procesos)
    tiempo_total = max(p.fin for p in procesos)
    # En un empate, max/min devuelven el primero en el orden del archivo
    mayor = max(procesos, key=lambda p: p.espera)
    menor = min(procesos, key=lambda p: p.espera)
    return {
        "politica": politica,
        "quantum": quantum,
        "costo_cambio": costo_cambio,
        "cantidad": n,
        "tiempo_total": tiempo_total,
        "espera_promedio": sum(p.espera for p in procesos) / n,
        "retorno_promedio": sum(p.retorno for p in procesos) / n,
        "respuesta_promedio": sum(p.respuesta for p in procesos) / n,
        "mayor_espera": (mayor.id, mayor.espera),
        "menor_espera": (menor.id, menor.espera),
        "utilizacion_cpu": simulacion.tiempo_util / tiempo_total * 100,
        "cambios_contexto": simulacion.cambios_contexto,
        "tiempo_cambios": simulacion.tiempo_cambios,
    }


def ejecutar_politica(procesos, politica, quantum, costo_cambio=0):
    """Simula `procesos` con la política dada. Devuelve (procesos, simulacion, metricas)."""
    procesos = copiar_procesos(procesos)
    if politica == FIFO:
        simulacion = simular_fifo(procesos, costo_cambio)
        quantum = None
    else:
        simulacion = simular_round_robin(procesos, quantum, costo_cambio)
    return procesos, simulacion, calcular_metricas(procesos, simulacion, politica, quantum, costo_cambio)


# ---------------------------------------------------------------------------
# Salidas
# ---------------------------------------------------------------------------

def nombre_politica(politica, quantum):
    return "FIFO" if politica == FIFO else f"Round Robin (quantum = {quantum})"


def formatear_resumen(procesos, metricas):
    """Devuelve el texto del resumen que se muestra en pantalla."""
    linea = "=" * 31
    ancho = max(len("Proceso"), *(len(p.id) for p in procesos))
    id_mayor, mayor = metricas["mayor_espera"]
    id_menor, menor = metricas["menor_espera"]

    lineas = [linea, "RESULTADO MINIOS", f"Política: {nombre_politica(metricas['politica'], metricas['quantum'])}"]
    if metricas["costo_cambio"] > 0:
        lineas.append(f"Costo por cambio de contexto: {metricas['costo_cambio']}")
    lineas += [linea,
               f"{'Proceso':<{ancho}}  {'Llegada':>7}  {'Inicio':>6}  {'Fin':>5}  {'Espera':>6}  {'Retorno':>7}  {'Respuesta':>9}"]
    for p in procesos:
        lineas.append(f"{p.id:<{ancho}}  {p.llegada:>7}  {p.inicio:>6}  {p.fin:>5}  "
                      f"{p.espera:>6}  {p.retorno:>7}  {p.respuesta:>9}")
    lineas += [
        f"Procesos ejecutados: {metricas['cantidad']}",
        f"Tiempo total: {metricas['tiempo_total']}",
        f"Espera promedio: {metricas['espera_promedio']:.2f}",
        f"Retorno promedio: {metricas['retorno_promedio']:.2f}",
        f"Respuesta promedio: {metricas['respuesta_promedio']:.2f}",
        f"Mayor espera: {id_mayor} ({mayor})",
        f"Menor espera: {id_menor} ({menor})",
        f"Utilización del CPU: {metricas['utilizacion_cpu']:.1f}%",
        f"Cambios de contexto: {metricas['cambios_contexto']}",
    ]
    if metricas["costo_cambio"] > 0:
        lineas.append(f"Tiempo perdido en cambios de contexto: {metricas['tiempo_cambios']}")
    return "\n".join(lineas)


def mostrar_resumen(procesos, metricas):
    print(formatear_resumen(procesos, metricas))


def formatear_comparacion(archivo, quantum, resultado_fifo, resultado_rr):
    """Texto con FIFO y Round Robin lado a lado, por proceso y en métricas globales."""
    procs_f, m_f = resultado_fifo
    procs_r, m_r = resultado_rr
    ancho = max(len("Proceso"), *(len(p.id) for p in procs_f))
    etiqueta_rr = f"RR (q={quantum})"
    linea = "=" * 66

    lineas = [linea, "COMPARACIÓN FIFO vs ROUND ROBIN", f"Archivo: {archivo.name} | quantum = {quantum}", linea,
              f"{'':<{ancho}}  {'':>7}  {'':>8}  {'--- FIFO ---':^22}  {'--- ' + etiqueta_rr + ' ---':^22}",
              f"{'Proceso':<{ancho}}  {'Llegada':>7}  {'Duración':>8}  "
              f"{'Esp':>6}{'Ret':>8}{'Resp':>8}  {'Esp':>6}{'Ret':>8}{'Resp':>8}"]
    for pf, pr in zip(procs_f, procs_r):
        lineas.append(f"{pf.id:<{ancho}}  {pf.llegada:>7}  {pf.duracion:>8}  "
                      f"{pf.espera:>6}{pf.retorno:>8}{pf.respuesta:>8}  "
                      f"{pr.espera:>6}{pr.retorno:>8}{pr.respuesta:>8}")
    lineas += ["", f"{'Métrica global':<28}{'FIFO':>12}{etiqueta_rr:>14}"]
    filas = [
        ("Tiempo total", "tiempo_total", "{:d}"),
        ("Espera promedio", "espera_promedio", "{:.2f}"),
        ("Retorno promedio", "retorno_promedio", "{:.2f}"),
        ("Respuesta promedio", "respuesta_promedio", "{:.2f}"),
        ("Utilización del CPU (%)", "utilizacion_cpu", "{:.1f}"),
        ("Cambios de contexto", "cambios_contexto", "{:d}"),
    ]
    for nombre, clave, formato in filas:
        lineas.append(f"{nombre:<28}{formato.format(m_f[clave]):>12}{formato.format(m_r[clave]):>14}")
    lineas.append(f"{'Mayor espera':<28}{'%s (%d)' % m_f['mayor_espera']:>12}{'%s (%d)' % m_r['mayor_espera']:>14}")
    lineas.append(f"{'Menor espera':<28}{'%s (%d)' % m_f['menor_espera']:>12}{'%s (%d)' % m_r['menor_espera']:>14}")
    return "\n".join(lineas)


def guardar_resultados(procesos, ruta):
    """Una fila por proceso, en el orden del archivo de entrada."""
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        escritor = csv.writer(f, lineterminator="\n")
        escritor.writerow(COLUMNAS_RESULTADOS)
        for p in procesos:
            escritor.writerow([p.id, p.llegada, p.duracion, p.inicio, p.fin,
                               p.espera, p.retorno, p.respuesta, p.expropiaciones])


def guardar_eventos(eventos, ruta):
    with open(ruta, "w", encoding="utf-8") as f:
        for t, texto in eventos:
            f.write(f"[{t}] {texto}\n")


# ---------------------------------------------------------------------------
# Programa principal
# ---------------------------------------------------------------------------

def cargar_procesos(ruta):
    """Lee y valida el archivo. Devuelve (procesos, errores)."""
    procesos, errores = leer_procesos(ruta)
    errores += validar_procesos(procesos)
    return procesos, errores


def ejecutar_simple(config, procesos):
    """Una política: muestra el resumen y escribe resultados.csv y eventos.txt."""
    procesos, simulacion, metricas = ejecutar_politica(procesos, config.politica, config.quantum, config.costo_cambio)
    mostrar_resumen(procesos, metricas)

    ruta_resultados = config.salida / "resultados.csv"
    ruta_eventos = config.salida / "eventos.txt"
    try:
        config.salida.mkdir(parents=True, exist_ok=True)
        guardar_resultados(procesos, ruta_resultados)
        guardar_eventos(simulacion.eventos, ruta_eventos)
    except OSError as e:
        print(f"Error al guardar los archivos de salida: {e}", file=sys.stderr)
        return 1
    print(f"\nArchivos generados: {ruta_resultados}, {ruta_eventos}")
    return 0


def ejecutar_comparacion(config, procesos):
    """--comparar: FIFO y Round Robin sobre los mismos datos, lado a lado (no escribe archivos)."""
    procs_fifo, _, m_fifo = ejecutar_politica(procesos, FIFO, None, config.costo_cambio)
    procs_rr, _, m_rr = ejecutar_politica(procesos, RR, config.quantum, config.costo_cambio)
    print(formatear_comparacion(config.archivo, config.quantum, (procs_fifo, m_fifo), (procs_rr, m_rr)))
    return 0


def main(argv=None):
    """Devuelve el código de salida: 0 correcto, 1 errores en los datos, 2 parámetros inválidos."""
    config, errores = leer_parametros(argv)
    if errores:
        print(formatear_errores_parametros(errores), file=sys.stderr)
        return 2

    procesos, errores = cargar_procesos(config.archivo)
    if errores:
        print(formatear_errores(errores), file=sys.stderr)
        return 1

    if config.comparar:
        return ejecutar_comparacion(config, procesos)
    return ejecutar_simple(config, procesos)


if __name__ == "__main__":
    sys.exit(main())
