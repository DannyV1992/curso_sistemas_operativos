#!/usr/bin/env python3
"""Misma consulta en Pandas: carga completa vs. procesamiento por bloques.

Requisito: pip install pandas
Ejemplos:
  python3 analizar_datos.py --input ventas_demo.csv --mode full
  python3 analizar_datos.py --input ventas_20gb.csv --mode chunks --chunk-size 100000

Para archivos mayores que la RAM, el modo full puede agotar la memoria y el SO
puede terminar el proceso. El programa requiere --force cuando la estimación
indica riesgo. Usar --force exclusivamente en un entorno de pruebas aislado.
"""

import argparse
from pathlib import Path
import os
import resource  # Linux: ru_maxrss se expresa en KiB.
import sys
import time


def memoria_disponible_aprox() -> int | None:
    """Estimación conservadora del espacio disponible, incluidos cgroups v2."""
    valores = []
    try:
        with open("/proc/meminfo", encoding="ascii") as f:
            for linea in f:
                if linea.startswith("MemAvailable:"):
                    valores.append(int(linea.split()[1]) * 1024)
                    break
    except (OSError, ValueError):
        pass
    try:
        base = Path("/sys/fs/cgroup")
        limite = (base / "memory.max").read_text().strip()
        if limite != "max":
            actual = int((base / "memory.current").read_text().strip())
            valores.append(max(0, int(limite) - actual))
    except (OSError, ValueError):
        pass
    return min(valores) if valores else None


def consulta(df):
    df = df.loc[df["unidades"] >= 10]
    # El importe se calcula tras filtrar; mismas reglas para ambos modos.
    df = df.assign(importe=df["unidades"] * df["precio_unitario"])
    return df.groupby(["region", "categoria"])["importe"].sum()


def main() -> int:
    parser = argparse.ArgumentParser(description="Compara el uso de RAM en dos formas de analizar el mismo CSV.")
    parser.add_argument("--input", type=Path, required=True, help="CSV creado por generar_dataset.py")
    parser.add_argument("--mode", choices=("full", "chunks"), required=True)
    parser.add_argument("--chunk-size", type=int, default=100_000, help="Filas por bloque en modo chunks")
    parser.add_argument("--limit-rows", type=int, default=0, help="Solo leer N filas (0 = todas)")
    parser.add_argument("--force", action="store_true", help="Permite ejecutar full a pesar de riesgo de falta de RAM")
    args = parser.parse_args()
    if args.chunk_size < 1 or args.limit_rows < 0:
        parser.error("--chunk-size >= 1 y --limit-rows >= 0")
    if not args.input.is_file():
        parser.error(f"No existe el CSV: {args.input}")
    try:
        import pandas as pd
    except ImportError:
        parser.error("No está instalado pandas. Ejecutar: python3 -m pip install pandas")

    bytes_csv = args.input.stat().st_size
    disponible = memoria_disponible_aprox()
    if args.mode == "full" and args.limit_rows == 0 and not args.force:
        # Un CSV suele ocupar mucha más RAM al cargarse como un DataFrame.
        if disponible is not None and bytes_csv > disponible * 0.35:
            parser.error(
                f"Riesgo de agotar la RAM: CSV={bytes_csv / 1e9:.2f} GB, "
                f"memoria disponible aprox.={disponible / 1e9:.2f} GB. "
                "Pruebe --mode chunks, --limit-rows o use --force en una VM aislada."
            )
        if disponible is None and bytes_csv > 1_000_000_000:
            parser.error("No se pudo estimar la RAM disponible. Use --force solo en una VM aislada.")

    inicio = time.perf_counter()
    print(f"PID={os.getpid()}, modo={args.mode}, archivo={args.input}, "
          f"filas_limitadas={args.limit_rows or 'todas'}", flush=True)
    filas = 0
    if args.mode == "full":
        tabla = pd.read_csv(args.input, nrows=args.limit_rows if args.limit_rows else None)
        filas = len(tabla)
        memoria_tabla_mib = tabla.memory_usage(deep=True).sum() / (1024 * 1024)
        print(f"DataFrame completo antes del filtro: {memoria_tabla_mib:.1f} MiB (memoria estimada)", flush=True)
        resultado = consulta(tabla)
    else:
        acumulado = None
        iterador = pd.read_csv(args.input, chunksize=args.chunk_size,
                               nrows=args.limit_rows if args.limit_rows else None)
        for fragmento in iterador:
            filas += len(fragmento)
            parcial = consulta(fragmento)
            acumulado = parcial if acumulado is None else acumulado.add(parcial, fill_value=0)
        if acumulado is None:
            print("CSV vacío.")
            return 1
        resultado = acumulado

    resultado = resultado.sort_values(ascending=False)
    duracion = time.perf_counter() - inicio
    max_rss_mib = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
    print("\nTop 10 por region y categoria (importe acumulado):")
    print(resultado.head(10).to_string())
    print(f"\nFilas procesadas: {filas:,}\nDuración: {duracion:.2f} s"
          f"\nRSS máximo del proceso: {max_rss_mib:.1f} MiB")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except MemoryError:
        print("Memoria insuficiente: Python recibió MemoryError.", file=sys.stderr)
        raise SystemExit(2)
