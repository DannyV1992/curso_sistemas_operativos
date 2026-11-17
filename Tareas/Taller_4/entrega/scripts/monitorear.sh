#!/bin/bash
# monitorear.sh - Registra el estado de memoria de la máquina mientras corre un análisis
# Uso: ./monitorear.sh NOMBRE [INTERVALO_segundos]     (se detiene con Ctrl+C o kill)
#   ej: ./monitorear.sh prueba 1
# Genera resultados/NOMBRE/ con un archivo por comando, cada muestra con su hora:
#   vmstat.txt  (vmstat -w -t)         memoria virtual, swap in/out, CPU
#   free.txt    (free -m)              RAM y swap usados (en MiB para poder procesarlo)
#   psi.txt     (/proc/pressure/memory) presión de memoria (PSI)
#   top.txt     (top -b -n 1)          procesos que más memoria usan
# Firma: Daniel Vásquez González (DannyV1992) - Sistemas Operativos, LEAD University, III Cuat. 2026

NOMBRE="${1:?Uso: $0 NOMBRE [INTERVALO_segundos]}"
INTERVALO="${2:-1}"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DIR="$SCRIPT_DIR/resultados/$NOMBRE"
mkdir -p "$DIR"

if [ ! -r /proc/pressure/memory ]; then
    echo "Aviso: /proc/pressure/memory no existe en este kernel; psi.txt quedará vacío." >&2
fi

# vmstat imprime por su cuenta cada INTERVALO s; -t agrega la hora a cada línea
vmstat -w -t "$INTERVALO" > "$DIR/vmstat.txt" &
VMSTAT_PID=$!
trap 'kill "$VMSTAT_PID" 2>/dev/null; exit 0' INT TERM EXIT

echo "Monitoreando en $DIR cada ${INTERVALO}s (Ctrl+C para detener)"

while true; do
    TS="$(date '+%Y-%m-%d %H:%M:%S')"
    { echo "### $TS"; free -m; }                              >> "$DIR/free.txt"
    { echo "### $TS"; cat /proc/pressure/memory 2>/dev/null; } >> "$DIR/psi.txt"
    { echo "### $TS"; top -b -n 1 -o %MEM | head -n 15; }     >> "$DIR/top.txt"
    sleep "$INTERVALO"
done
