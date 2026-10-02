#!/usr/bin/env python3
"""MiniOS: simulador básico de procesos (Tarea Programada 1).

Simula un computador con un único CPU y una cola FIFO, sin interrupciones:
una vez que un proceso empieza a ejecutarse, continúa hasta terminar.

Uso:
    python minios.py [archivo.csv] [--salida DIRECTORIO] [-v]

Entrada:  procesos.csv (columnas: id,llegada,duracion)
Salidas:  resultados.csv y eventos.txt
"""

import argparse
import csv
import re
import sys
import unicodedata
from collections import defaultdict, deque
from dataclasses import dataclass
from pathlib import Path

ARCHIVO_ENTRADA = "procesos.csv"
ARCHIVO_RESULTADOS = "resultados.csv"
ARCHIVO_EVENTOS = "eventos.txt"
COLUMNAS = ["id", "llegada", "duracion"]

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
    inicio: int | None = None
    fin: int | None = None
    espera: int | None = None
    retorno: int | None = None

    def __post_init__(self):
        self.restante = self.duracion


# ---------------------------------------------------------------------------
# Lectura y validación
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


def mostrar_errores(errores):
    print("No se puede ejecutar la simulación. Se encontraron errores en los datos:", file=sys.stderr)
    for linea, mensaje in sorted(errores, key=lambda e: e[0]):
        prefijo = f"  Línea {linea}: " if linea else "  "
        print(prefijo + mensaje, file=sys.stderr)


# ---------------------------------------------------------------------------
# Simulación
# ---------------------------------------------------------------------------

def _iniciar(proceso, t, eventos):
    proceso.estado = EJECUTANDO
    proceso.inicio = t
    eventos.append((t, f"{proceso.id} inicia ejecución"))


def simular(procesos):
    """Simula el CPU unidad de tiempo por unidad de tiempo con una cola FIFO.

    Actualiza los procesos (estado, inicio, fin) y devuelve (eventos, traza),
    listas de tuplas (tiempo, texto).

    Orden de las acciones en cada instante t:
      1. Si el proceso actual ya consumió toda su duración, termina en t.
      2. Si el CPU quedó libre, entra el primero de la cola.
      3. Llegan los procesos de ese instante (en el orden del archivo): si el
         CPU está libre arrancan de inmediato, si no entran a la cola.
      4. El proceso que esté en el CPU consume una unidad de tiempo.
    """
    llegadas = defaultdict(list)
    for p in procesos:
        llegadas[p.llegada].append(p)

    cola = deque()
    actual = None
    terminados = 0
    eventos, traza = [], []
    t = 0

    while True:
        if actual is not None and actual.restante == 0:
            actual.estado = TERMINADO
            actual.fin = t
            eventos.append((t, f"{actual.id} termina"))
            terminados += 1
            actual = None
        if terminados == len(procesos):
            break

        if actual is None and cola:
            actual = cola.popleft()
            _iniciar(actual, t, eventos)

        for p in llegadas.get(t, []):
            p.estado = LISTO
            eventos.append((t, f"{p.id} llega al sistema"))
            if actual is None:
                actual = p
                _iniciar(p, t, eventos)
            else:
                cola.append(p)
                eventos.append((t, f"{p.id} entra a la cola"))

        cpu = f"{actual.id} (restante {actual.restante})" if actual else "libre"
        espera = ", ".join(p.id for p in cola) or "vacía"
        traza.append((t, f"CPU: {cpu} | Cola: {espera}"))

        if actual is not None:
            actual.restante -= 1
        t += 1

    return eventos, traza


# ---------------------------------------------------------------------------
# Métricas y salidas
# ---------------------------------------------------------------------------

def calcular_metricas(procesos):
    """Calcula espera y retorno de cada proceso y devuelve las métricas globales."""
    for p in procesos:
        p.retorno = p.fin - p.llegada
        p.espera = p.inicio - p.llegada

    n = len(procesos)
    tiempo_total = max(p.fin for p in procesos)
    mayor = max(p.espera for p in procesos)
    menor = min(p.espera for p in procesos)
    return {
        "cantidad": n,
        "tiempo_total": tiempo_total,
        "espera_promedio": sum(p.espera for p in procesos) / n,
        "retorno_promedio": sum(p.retorno for p in procesos) / n,
        "mayor_espera": (mayor, [p.id for p in procesos if p.espera == mayor]),
        "menor_espera": (menor, [p.id for p in procesos if p.espera == menor]),
        "utilizacion_cpu": sum(p.duracion for p in procesos) / tiempo_total * 100,
    }


def mostrar_resumen(procesos, metricas):
    linea = "=" * 40
    print(linea)
    print("  RESULTADO MINIOS")
    print(linea)
    print()

    ancho = max(len("Proceso"), *(len(p.id) for p in procesos))
    print(f"{'Proceso':<{ancho}}  {'Llegada':>7}  {'Inicio':>6}  {'Fin':>5}  {'Espera':>6}  {'Retorno':>7}")
    for p in procesos:
        print(f"{p.id:<{ancho}}  {p.llegada:>7}  {p.inicio:>6}  {p.fin:>5}  {p.espera:>6}  {p.retorno:>7}")

    mayor, ids_mayor = metricas["mayor_espera"]
    menor, ids_menor = metricas["menor_espera"]
    print()
    print(f"Procesos ejecutados: {metricas['cantidad']}")
    print(f"Tiempo total: {metricas['tiempo_total']}")
    print(f"Espera promedio: {metricas['espera_promedio']:.2f}")
    print(f"Retorno promedio: {metricas['retorno_promedio']:.2f}")
    print(f"Mayor tiempo de espera: {', '.join(ids_mayor)} ({mayor})")
    print(f"Menor tiempo de espera: {', '.join(ids_menor)} ({menor})")
    print(f"Utilización del CPU: {metricas['utilizacion_cpu']:.2f}%")


def sin_tildes(texto):
    return "".join(c for c in unicodedata.normalize("NFD", texto) if unicodedata.category(c) != "Mn")


def mostrar_traza(eventos, traza):
    """Imprime la simulación instante por instante, sin tildes (opción -v)."""
    por_tiempo = defaultdict(list)
    for t, texto in eventos:
        por_tiempo[t].append(texto)
    estado = dict(traza)
    print("--- Simulacion ---")
    for t in sorted(set(por_tiempo) | set(estado)):
        for texto in por_tiempo.get(t, []):
            print(sin_tildes(f"[{t}] {texto}"))
        if t in estado:
            print(sin_tildes(f"[{t}]   {estado[t]}"))
    print()


def guardar_resultados(procesos, ruta):
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        escritor = csv.writer(f, lineterminator="\n")
        escritor.writerow(["id", "llegada", "duracion", "inicio", "fin", "espera", "retorno"])
        for p in procesos:
            escritor.writerow([p.id, p.llegada, p.duracion, p.inicio, p.fin, p.espera, p.retorno])


def guardar_eventos(eventos, ruta):
    with open(ruta, "w", encoding="utf-8") as f:
        for t, texto in eventos:
            f.write(f"[{t}] {texto}\n")


# ---------------------------------------------------------------------------
# Programa principal
# ---------------------------------------------------------------------------


def main(argv=None):
    parser = argparse.ArgumentParser(description="MiniOS: simulador básico de procesos (CPU único, cola FIFO).")
    parser.add_argument("archivo", nargs="?", default=ARCHIVO_ENTRADA,
                        help=f"CSV de entrada (por defecto {ARCHIVO_ENTRADA})")
    parser.add_argument("--salida", default=".",
                        help="directorio donde se escriben resultados.csv y eventos.txt (por defecto el actual)")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="muestra la simulación instante por instante")
    args = parser.parse_args(argv)

    procesos, errores = leer_procesos(args.archivo)
    errores += validar_procesos(procesos)
    if errores:
        mostrar_errores(errores)
        return 1

    eventos, traza = simular(procesos)
    metricas = calcular_metricas(procesos)

    if args.verbose:
        mostrar_traza(eventos, traza)
    mostrar_resumen(procesos, metricas)

    salida = Path(args.salida)
    try:
        salida.mkdir(parents=True, exist_ok=True)
        guardar_resultados(procesos, salida / ARCHIVO_RESULTADOS)
        guardar_eventos(eventos, salida / ARCHIVO_EVENTOS)
    except OSError as e:
        print(f"Error al guardar los archivos de salida: {e}", file=sys.stderr)
        return 1
    print(f"\nArchivos generados: {salida / ARCHIVO_RESULTADOS}, {salida / ARCHIVO_EVENTOS}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
