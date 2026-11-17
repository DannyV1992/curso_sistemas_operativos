#!/usr/bin/env python3
"""Generador de CSV de ventas sintéticas para un laboratorio de memoria virtual.

No necesita cargar el dataset completo en RAM: escribe en bloques (~4 MiB).
El contenido sintético se recicla dentro de intervalos y se renueva
periódicamente para acelerar la creación de archivos muy grandes.

Ejemplos:
  python3 generar_dataset.py --demo-mb 200 --output ventas_demo.csv
  python3 generar_dataset.py --size-gb 20 --output ventas_20gb.csv
  python3 generar_dataset.py --size-gb 50 --output ventas_50gb.csv

'GB' corresponde a 1,000,000,000 bytes; 'MB' a 1,000,000 bytes.
"""

import argparse
import os
from pathlib import Path
import random
import shutil
import sys
import time

HEADER = b"fecha,region,categoria,cliente_id,unidades,precio_unitario\n"
REGIONES = ("Central", "Norte", "Pacifico", "Caribe", "Sur", "Occidente")
CATEGORIAS = ("Electronica", "Hogar", "Alimentos", "Deportes", "Libros", "Salud", "Servicios")
# 2023-01-01 a 2026-12-31, precalculadas para evitar operaciones caras por fila.
from datetime import date, timedelta
FECHAS = tuple((date(2023, 1, 1) + timedelta(days=i)).isoformat() for i in range(1461))
PRECIOS = tuple(f"{p / 100:.2f}" for p in range(250, 120000, 125))


def crear_bloque(aleatorio: random.Random, minimo_bytes: int) -> bytes:
    """Crea un conjunto de filas CSV enteras que puede reutilizarse."""
    partes = []
    total = 0
    while total < minimo_bytes:
        fila = (
            f"{aleatorio.choice(FECHAS)},{aleatorio.choice(REGIONES)},"
            f"{aleatorio.choice(CATEGORIAS)},{aleatorio.randrange(10000, 999999)},"
            f"{aleatorio.randrange(1, 51)},{aleatorio.choice(PRECIOS)}\n"
        ).encode("ascii")
        partes.append(fila)
        total += len(fila)
    return b"".join(partes)


def entero_positivo(valor: str) -> int:
    numero = int(valor)
    if numero < 1:
        raise argparse.ArgumentTypeError("Debe ser un entero positivo")
    return numero


def main() -> int:
    parser = argparse.ArgumentParser(description="Genera un CSV de ventas sintéticas sin consumir RAM proporcional al archivo.")
    tamano = parser.add_mutually_exclusive_group(required=True)
    tamano.add_argument("--size-gb", type=entero_positivo, metavar="1..50",
                        help="Tamaño de salida en GB decimales (entre 1 y 50; el original exigía 20..50)")
    tamano.add_argument("--demo-mb", type=entero_positivo, metavar="MB",
                        help="Modo de prueba pequeña (entre 1 y 1024 MB)")
    parser.add_argument("--output", type=Path, required=True, help="Ruta de destino del CSV")
    parser.add_argument("--seed", type=int, default=42, help="Semilla aleatoria reproducible (default: 42)")
    parser.add_argument("--block-mib", type=entero_positivo, default=4, help="RAM por bloque (1 a 16 MiB; default: 4)")
    args = parser.parse_args()

    if args.size_gb is not None and not (1 <= args.size_gb <= 50):
        parser.error("--size-gb debe estar entre 1 y 50 GB")
    if args.demo_mb is not None and not (1 <= args.demo_mb <= 1024):
        parser.error("--demo-mb debe estar entre 1 y 1024 MB")
    if not (1 <= args.block_mib <= 16):
        parser.error("--block-mib debe estar entre 1 y 16")

    meta = args.size_gb * 1_000_000_000 if args.size_gb is not None else args.demo_mb * 1_000_000
    salida = args.output.expanduser().resolve()
    salida.parent.mkdir(parents=True, exist_ok=True)
    if salida.exists():
        parser.error(f"El archivo ya existe, no se sobrescribirá: {salida}")
    reserva = max(1_000_000_000, meta // 20)  # Deja al menos 1 GB o 5% libre.
    libre = shutil.disk_usage(salida.parent).free
    if libre < meta + reserva:
        parser.error(
            f"Espacio libre insuficiente: {libre / 1e9:.2f} GB; "
            f"se requieren {((meta + reserva) / 1e9):.2f} GB "
            "incluyendo margen de seguridad."
        )

    rng = random.Random(args.seed)
    tam_bloque = args.block_mib * 1024 * 1024
    regenerar_cada = max(1, (128 * 1024 * 1024) // tam_bloque)
    t0 = time.perf_counter()
    escritos = 0
    ultimo_reporte = 0
    try:
        # x/b: evita destruir datos preexistentes.
        with salida.open("xb", buffering=1024 * 1024) as archivo:
            archivo.write(HEADER)
            escritos = len(HEADER)
            bloque = b""
            contador_bloques = 0
            while escritos < meta:
                if contador_bloques % regenerar_cada == 0:
                    bloque = crear_bloque(rng, tam_bloque)
                faltantes = meta - escritos
                if len(bloque) <= faltantes:
                    porcion = bloque
                else:
                    # Cortar solo entre filas completas, no dentro de una fila CSV.
                    hasta = bloque.rfind(b"\n", 0, faltantes)
                    porcion = bloque[:hasta + 1] if hasta >= 0 else b""
                if not porcion:
                    break  # Se queda a menos de una fila del tamaño solicitado.
                archivo.write(porcion)
                escritos += len(porcion)
                contador_bloques += 1
                avance_gb = escritos // 1_000_000_000
                if avance_gb > ultimo_reporte:
                    ultimo_reporte = avance_gb
                    print(f"Progreso: {escritos / 1e9:.2f} / {meta / 1e9:.2f} GB", flush=True)
    except (KeyboardInterrupt, OSError) as e:
        try:
            salida.unlink(missing_ok=True)  # Evita dejar un CSV parcial de decenas de GB.
        except OSError:
            pass
        print(f"Generación interrumpida o fallida: {e}. Se intentó eliminar el archivo parcial.", file=sys.stderr)
        return 1

    duracion = time.perf_counter() - t0
    tamano_final = salida.stat().st_size
    print(f"Archivo: {salida}\nTamaño: {tamano_final:,} bytes ({tamano_final / 1e9:.3f} GB)"
          f"\nTiempo: {duracion:.1f} s\nNota: el generador reutiliza bloques de filas y "
          "los renueva cada ~128 MiB para acelerar la escritura.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
