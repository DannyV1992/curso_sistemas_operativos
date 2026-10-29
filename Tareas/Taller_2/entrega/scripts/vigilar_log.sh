#!/bin/bash
# vigilar_log.sh - Vigila un log en vivo durante N segundos y guarda las líneas que coinciden
# Uso: ./vigilar_log.sh [archivo] [segundos] [patron]
# Firma: Daniel Vásquez González (DannyV1992) - Sistemas Operativos, LEAD University, III Cuat. 2026

ARCHIVO="${1:-app.log}"
SEGUNDOS="${2:-30}"
PATRON="${3:-ERROR|CRITICAL}"

if [ ! -f "$ARCHIVO" ]; then
    echo "Error: no existe el archivo '$ARCHIVO'" >&2
    exit 1
fi

mkdir -p capturas
SALIDA="capturas/captura_$(date +%Y%m%d_%H%M%S).txt"

echo "Vigilando '$ARCHIVO' durante $SEGUNDOS s con el patrón '$PATRON'..."

# tail -F sigue el archivo aunque se rote; --line-buffered evita que grep retenga las líneas
tail -n 0 -F "$ARCHIVO" 2>/dev/null | grep --line-buffered -E "$PATRON" | tee "$SALIDA" &
PID=$!

sleep "$SEGUNDOS"

kill "$PID" 2>/dev/null
pkill -P $$ tail 2>/dev/null
wait 2>/dev/null

echo
echo "Vigilancia terminada. Líneas capturadas: $(wc -l < "$SALIDA")"
echo "Captura guardada en $SALIDA"
