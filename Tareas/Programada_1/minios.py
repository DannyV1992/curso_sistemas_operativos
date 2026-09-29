"""MiniOS: simulador básico de procesos con planificación FIFO (no apropiativa).

Uso:
    python minios.py [ruta_al_csv]

Si no se indica ruta, se usa por defecto "procesos.csv" en el directorio actual.
Genera "resultados.csv" y "eventos.txt" en el directorio actual.
"""

import csv
import statistics
import sys
from dataclasses import dataclass
from pathlib import Path

ENCABEZADO_ESPERADO = ["id", "llegada", "duracion"]


@dataclass
class Proceso:
    id: str
    llegada: int
    duracion: int
    inicio: int = None
    fin: int = None
    espera: int = None
    retorno: int = None


def leer_procesos(ruta):
    """Lee el archivo CSV de procesos y devuelve las filas crudas (sin validar).

    Lanza FileNotFoundError si el archivo no existe.
    Lanza ValueError si el archivo está vacío o solo tiene encabezado.
    """
    path = Path(ruta)
    if not path.exists():
        raise FileNotFoundError(f"el archivo '{ruta}' no existe.")

    with path.open(newline="", encoding="utf-8") as f:
        filas = [fila for fila in csv.reader(f) if fila]

    if not filas:
        raise ValueError(f"el archivo '{ruta}' está vacío.")

    if [campo.strip().lower() for campo in filas[0]] == ENCABEZADO_ESPERADO:
        filas = filas[1:]

    if not filas:
        raise ValueError(f"el archivo '{ruta}' no contiene procesos (solo encabezado).")

    return filas


def validar_procesos(filas):
    """Valida las filas crudas leídas del archivo de procesos.

    Devuelve una tupla (procesos_validos, errores), donde procesos_validos
    es una lista de objetos Proceso y errores es una lista de mensajes
    comprensibles describiendo cada problema encontrado.
    """
    procesos = []
    errores = []
    ids_vistos = set()

    for numero_linea, fila in enumerate(filas, start=1):
        if len(fila) != 3:
            errores.append(
                f"Línea {numero_linea}: fila incompleta {fila}; "
                "se esperaban 3 columnas (id,llegada,duracion)."
            )
            continue

        id_proceso, texto_llegada, texto_duracion = (campo.strip() for campo in fila)

        if not id_proceso:
            errores.append(f"Línea {numero_linea}: el identificador está vacío.")
            continue

        if id_proceso in ids_vistos:
            errores.append(
                f"Línea {numero_linea}: el identificador '{id_proceso}' está duplicado."
            )
            continue

        try:
            llegada = int(texto_llegada)
        except ValueError:
            errores.append(
                f"Línea {numero_linea}: el tiempo de llegada '{texto_llegada}' de "
                f"'{id_proceso}' no es un número entero."
            )
            continue

        try:
            duracion = int(texto_duracion)
        except ValueError:
            errores.append(
                f"Línea {numero_linea}: la duración '{texto_duracion}' de "
                f"'{id_proceso}' no es un número entero."
            )
            continue

        if llegada < 0:
            errores.append(
                f"Línea {numero_linea}: '{id_proceso}' tiene un tiempo de llegada "
                f"negativo ({llegada})."
            )
            continue

        if duracion <= 0:
            errores.append(
                f"Línea {numero_linea}: '{id_proceso}' tiene una duración inválida "
                f"({duracion}); debe ser mayor que cero."
            )
            continue

        ids_vistos.add(id_proceso)
        procesos.append(Proceso(id=id_proceso, llegada=llegada, duracion=duracion))

    return procesos, errores


def simular(procesos):
    """Ejecuta la simulación FIFO no apropiativa sobre la lista de procesos.

    Devuelve (procesos_en_orden_de_ejecucion, eventos), donde cada proceso
    queda con sus tiempos de inicio/fin/espera/retorno calculados, y eventos
    es la lista de (tiempo, prioridad, texto) ya ordenada cronológicamente.
    """
    # Orden de llegada a la cola: por tiempo de llegada y, en caso de
    # empate, por el orden en que aparecen en el archivo de entrada.
    orden_llegada = sorted(enumerate(procesos), key=lambda par: (par[1].llegada, par[0]))

    reloj = 0
    eventos = []

    for _, proceso in orden_llegada:
        if reloj < proceso.llegada:
            reloj = proceso.llegada

        proceso.inicio = reloj
        proceso.fin = reloj + proceso.duracion
        proceso.espera = proceso.inicio - proceso.llegada
        proceso.retorno = proceso.fin - proceso.llegada

        reloj = proceso.fin

        eventos.append((proceso.llegada, 0, f"[{proceso.llegada}] {proceso.id} llega al sistema"))
        if proceso.inicio == proceso.llegada:
            eventos.append((proceso.llegada, 1, f"[{proceso.llegada}] {proceso.id} inicia ejecución"))
        else:
            eventos.append((proceso.llegada, 1, f"[{proceso.llegada}] {proceso.id} entra a la cola"))
            eventos.append((proceso.inicio, 3, f"[{proceso.inicio}] {proceso.id} inicia ejecución"))
        eventos.append((proceso.fin, 2, f"[{proceso.fin}] {proceso.id} termina"))

    eventos.sort(key=lambda evento: (evento[0], evento[1]))
    procesos_ejecutados = [proceso for _, proceso in orden_llegada]

    return procesos_ejecutados, eventos


def calcular_metricas(procesos):
    """Calcula las métricas globales de la simulación."""
    esperas = [proceso.espera for proceso in procesos]
    retornos = [proceso.retorno for proceso in procesos]

    return {
        "cantidad": len(procesos),
        "tiempo_total": max(proceso.fin for proceso in procesos),
        "espera_promedio": statistics.mean(esperas),
        "retorno_promedio": statistics.mean(retornos),
        "mayor_espera": max(procesos, key=lambda proceso: proceso.espera),
        "menor_espera": min(procesos, key=lambda proceso: proceso.espera),
    }


def guardar_resultados(procesos, ruta="resultados.csv"):
    """Genera el archivo resultados.csv con el detalle de cada proceso."""
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        escritor = csv.writer(f)
        escritor.writerow(["id", "llegada", "duracion", "inicio", "fin", "espera", "retorno"])
        for proceso in procesos:
            escritor.writerow(
                [
                    proceso.id,
                    proceso.llegada,
                    proceso.duracion,
                    proceso.inicio,
                    proceso.fin,
                    proceso.espera,
                    proceso.retorno,
                ]
            )


def guardar_eventos(eventos, ruta="eventos.txt"):
    """Genera el archivo eventos.txt con el registro cronológico de la simulación."""
    with open(ruta, "w", encoding="utf-8") as f:
        for _, _, texto in eventos:
            f.write(texto + "\n")


def mostrar_resumen(procesos, metricas):
    """Muestra en pantalla un resumen ordenado de la simulación."""
    print("=" * 45)
    print(" RESULTADO MINIOS")
    print("=" * 45)
    print()
    print(f"{'Proceso':<10}{'Llegada':>8}{'Inicio':>8}{'Fin':>8}{'Espera':>8}{'Retorno':>9}")
    for proceso in procesos:
        print(
            f"{proceso.id:<10}{proceso.llegada:>8}{proceso.inicio:>8}{proceso.fin:>8}"
            f"{proceso.espera:>8}{proceso.retorno:>9}"
        )
    print()
    print(f"Procesos ejecutados: {metricas['cantidad']}")
    print(f"Tiempo total: {metricas['tiempo_total']}")
    print(f"Espera promedio: {metricas['espera_promedio']:.2f}")
    print(f"Retorno promedio: {metricas['retorno_promedio']:.2f}")
    print(
        f"Proceso con mayor tiempo de espera: {metricas['mayor_espera'].id} "
        f"({metricas['mayor_espera'].espera})"
    )
    print(
        f"Proceso con menor tiempo de espera: {metricas['menor_espera'].id} "
        f"({metricas['menor_espera'].espera})"
    )


def main():
    # Evita que las tildes se muestren mal en consolas de Windows que no
    # usan UTF-8 por defecto (p. ej. cmd.exe).
    for flujo in (sys.stdout, sys.stderr):
        if hasattr(flujo, "reconfigure"):
            flujo.reconfigure(encoding="utf-8")

    ruta_entrada = sys.argv[1] if len(sys.argv) > 1 else "procesos.csv"

    try:
        filas = leer_procesos(ruta_entrada)
    except (FileNotFoundError, ValueError) as error:
        print(f"Error: {error}")
        sys.exit(1)

    procesos, errores = validar_procesos(filas)

    if errores:
        print("Se encontraron errores en el archivo de procesos:")
        for error in errores:
            print(f"  - {error}")
        print()

    if not procesos:
        print("No hay procesos válidos para simular. Se detiene la ejecución.")
        sys.exit(1)

    if errores:
        print(f"Se continuará la simulación únicamente con los {len(procesos)} procesos válidos.\n")

    procesos_ejecutados, eventos = simular(procesos)
    metricas = calcular_metricas(procesos_ejecutados)

    guardar_resultados(procesos_ejecutados)
    guardar_eventos(eventos)
    mostrar_resumen(procesos_ejecutados, metricas)


if __name__ == "__main__":
    main()
