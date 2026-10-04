#!/usr/bin/env python3
"""MiniOS: simulador básico de procesos (Tarea Programada 1).

Simula un computador con un único CPU y una cola FIFO, sin interrupciones:
una vez que un proceso empieza a ejecutarse, continúa hasta terminar.

Uso:
    python minios.py        (abre un menú interactivo)

Entrada:  archivos CSV de la carpeta casos/ (columnas: id,llegada,duracion)
Salidas:  carpeta salida/, con <fecha_hora>_resultados_<caso>.csv,
          <fecha_hora>_eventos_<caso>.txt y <fecha_hora>_traza_<caso>.txt
          (la traza termina con el mismo resumen que se muestra en pantalla).
          Si los datos tienen errores solo se genera <fecha_hora>_errores_<caso>.txt
"""

import csv
import re
import sys
import unicodedata
from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

# Las carpetas se buscan junto al script, sin importar desde dónde se ejecute
CARPETA_BASE = Path(__file__).resolve().parent
CARPETA_CASOS = CARPETA_BASE / "casos"
CARPETA_SALIDA = CARPETA_BASE / "salida"
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


def formatear_errores(errores):
    """Devuelve el texto de los errores, igual para la pantalla y para el archivo."""
    lineas = ["No se puede ejecutar la simulación. Se encontraron errores en los datos:"]
    for linea, mensaje in sorted(errores, key=lambda e: e[0]):
        prefijo = f"  Línea {linea}: " if linea else "  "
        lineas.append(prefijo + mensaje)
    return "\n".join(lineas)


def mostrar_errores(errores):
    print(formatear_errores(errores), file=sys.stderr)


def guardar_errores(errores, nombre_caso, ruta):
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(f"Archivo: {nombre_caso}\n{formatear_errores(errores)}\n")


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


def formatear_resumen(procesos, metricas):
    """Devuelve el texto del resumen, igual para la pantalla y para el archivo."""
    linea = "=" * 40
    ancho = max(len("Proceso"), *(len(p.id) for p in procesos))
    mayor, ids_mayor = metricas["mayor_espera"]
    menor, ids_menor = metricas["menor_espera"]

    lineas = [linea, "  RESULTADO MINIOS", linea, ""]
    lineas.append(f"{'Proceso':<{ancho}}  {'Llegada':>7}  {'Inicio':>6}  {'Fin':>5}  {'Espera':>6}  {'Retorno':>7}")
    for p in procesos:
        lineas.append(f"{p.id:<{ancho}}  {p.llegada:>7}  {p.inicio:>6}  {p.fin:>5}  {p.espera:>6}  {p.retorno:>7}")
    lineas += [
        "",
        f"Procesos ejecutados: {metricas['cantidad']}",
        f"Tiempo total: {metricas['tiempo_total']}",
        f"Espera promedio: {metricas['espera_promedio']:.2f}",
        f"Retorno promedio: {metricas['retorno_promedio']:.2f}",
        f"Mayor tiempo de espera: {', '.join(ids_mayor)} ({mayor})",
        f"Menor tiempo de espera: {', '.join(ids_menor)} ({menor})",
        f"Utilización del CPU: {metricas['utilizacion_cpu']:.2f}%",
    ]
    return "\n".join(lineas)


def mostrar_resumen(procesos, metricas):
    print(formatear_resumen(procesos, metricas))


def sin_tildes(texto):
    return "".join(c for c in unicodedata.normalize("NFD", texto) if unicodedata.category(c) != "Mn")


def guardar_traza(eventos, traza, resumen, ruta):
    """Guarda la simulación instante por instante (eventos + estado del CPU y la cola)
    seguida del resumen final. Todo el archivo va sin tildes."""
    por_tiempo = defaultdict(list)
    for t, texto in eventos:
        por_tiempo[t].append(texto)
    estado = dict(traza)
    with open(ruta, "w", encoding="utf-8") as f:
        f.write("--- Traza de la simulacion ---\n")
        for t in sorted(set(por_tiempo) | set(estado)):
            for texto in por_tiempo.get(t, []):
                f.write(sin_tildes(f"[{t}] {texto}") + "\n")
            if t in estado:
                f.write(sin_tildes(f"[{t}]   {estado[t]}") + "\n")
        f.write("\n" + sin_tildes(resumen) + "\n")


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
# Ejecución de un caso
# ---------------------------------------------------------------------------

def ejecutar_caso(ruta):
    """Lee, valida, simula y guarda un caso. Devuelve True si terminó bien.

    Si los datos tienen errores no se simula: se muestran en pantalla y se
    guardan en un archivo de errores.
    """
    # El timestamp va primero para que los archivos queden ordenados por ejecución:
    # 20261004_153012_resultados_caso1.csv
    marca = datetime.now().strftime("%Y%m%d_%H%M%S")

    procesos, errores = leer_procesos(ruta)
    errores += validar_procesos(procesos)
    if errores:
        mostrar_errores(errores)
        ruta_errores = CARPETA_SALIDA / f"{marca}_errores_{ruta.stem}.txt"
        try:
            CARPETA_SALIDA.mkdir(exist_ok=True)
            guardar_errores(errores, ruta.name, ruta_errores)
        except OSError as e:
            print(f"Error al guardar el archivo de errores: {e}", file=sys.stderr)
            return False
        print(f"\nArchivo generado en {CARPETA_SALIDA.name}/:\n  {ruta_errores.name}")
        return False

    eventos, traza = simular(procesos)
    metricas = calcular_metricas(procesos)

    mostrar_resumen(procesos, metricas)

    ruta_resultados = CARPETA_SALIDA / f"{marca}_resultados_{ruta.stem}.csv"
    ruta_eventos = CARPETA_SALIDA / f"{marca}_eventos_{ruta.stem}.txt"
    ruta_traza = CARPETA_SALIDA / f"{marca}_traza_{ruta.stem}.txt"
    try:
        CARPETA_SALIDA.mkdir(exist_ok=True)
        guardar_resultados(procesos, ruta_resultados)
        guardar_eventos(eventos, ruta_eventos)
        guardar_traza(eventos, traza, formatear_resumen(procesos, metricas), ruta_traza)
    except OSError as e:
        print(f"Error al guardar los archivos de salida: {e}", file=sys.stderr)
        return False
    print(f"\nArchivos generados en {CARPETA_SALIDA.name}/:")
    for destino in (ruta_resultados, ruta_eventos, ruta_traza):
        print(f"  {destino.name}")
    return True


# ---------------------------------------------------------------------------
# Menú interactivo
# ---------------------------------------------------------------------------

def listar_casos():
    """Devuelve los archivos CSV de la carpeta de casos, ordenados por nombre."""
    if not CARPETA_CASOS.is_dir():
        return []
    return sorted(CARPETA_CASOS.glob("*.csv"), key=lambda r: r.name.lower())


def mostrar_casos(casos):
    print(f"\nCasos disponibles en {CARPETA_CASOS.name}/:")
    for i, caso in enumerate(casos, 1):
        print(f"  {i}. {caso.name}")


def elegir_caso(casos):
    """Pide el nombre (o número) del archivo. Devuelve la ruta o None si no es válido."""
    mostrar_casos(casos)
    texto = input("\nNombre del archivo o número (Enter para cancelar): ").strip()
    if not texto:
        return None

    if texto.isdigit():
        indice = int(texto)
        if 1 <= indice <= len(casos):
            return casos[indice - 1]
        print(f"No hay un caso con el número {indice}.")
        return None

    if Path(texto).name != texto:
        print("Escriba solo el nombre del archivo, sin carpetas.")
        return None
    if not texto.lower().endswith(".csv"):
        texto += ".csv"
    ruta = CARPETA_CASOS / texto
    if not ruta.is_file():
        print(f"El archivo '{texto}' no existe en {CARPETA_CASOS.name}/.")
        return None
    return ruta


def mostrar_menu():
    print()
    print("=" * 40)
    print("  MINIOS - Simulador de procesos")
    print("=" * 40)
    print("  1. Ejecutar un caso")
    print("  2. Ver casos disponibles")
    print("  0. Salir")


def menu():
    while True:
        mostrar_menu()
        try:
            opcion = input("\nOpción: ").strip()
            casos = listar_casos()

            if opcion == "0":
                print("Hasta luego.")
                return
            if opcion not in ("1", "2"):
                print("Opción no válida. Escriba 1, 2 o 0.")
                continue
            if not casos:
                print(f"No hay archivos .csv en {CARPETA_CASOS}.")
                continue

            if opcion == "2":
                mostrar_casos(casos)
                continue

            ruta = elegir_caso(casos)
            if ruta is not None:
                print(f"\nEjecutando {ruta.name}...\n")
                ejecutar_caso(ruta)
        except (EOFError, KeyboardInterrupt):
            print("\nHasta luego.")
            return


if __name__ == "__main__":
    menu()
