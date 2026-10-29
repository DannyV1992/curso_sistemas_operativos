#!/bin/bash
# reporte_log.sh - Reporte resumen de un archivo de log
# Uso: ./reporte_log.sh [archivo] [umbral_errores]
# Firma: Daniel Vásquez González (DannyV1992) - Sistemas Operativos, LEAD University, III Cuat. 2026

ARCHIVO="${1:-app.log}"
UMBRAL="${2:-20}"

# TODO 1: validar que el archivo exista
if [ ! -f "$ARCHIVO" ]; then
    echo "Error: no existe el archivo '$ARCHIVO'" >&2
    exit 1
fi

mkdir -p reportes
SALIDA="reportes/reporte_$(date +%Y%m%d_%H%M%S).txt"
ERRORES=$(grep -c '\[ERROR\]' "$ARCHIVO")

{
    echo "===== REPORTE DE $ARCHIVO ====="
    echo "Generado: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "Total de líneas: $(wc -l < "$ARCHIVO")"
    echo

    # TODO 2: conteo por nivel con un for
    echo "--- Conteo por nivel ---"
    for NIVEL in DEBUG INFO WARN ERROR CRITICAL; do
        echo "$NIVEL: $(grep -c "\[$NIVEL\]" "$ARCHIVO")"
    done
    echo

    # TODO 3: top 5 servicios con errores
    echo "--- Top 5 servicios con errores ---"
    grep '\[ERROR\]' "$ARCHIVO" | awk '{print $4}' | sed 's/\[.*//' | sort | uniq -c | sort -rn | head -n 5
    echo

    # TODO 4: ranking de IPs con login fallido
    echo "--- IPs con Login fallido ---"
    grep 'Login fallido' "$ARCHIVO" | grep -oE '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+' | sort | uniq -c | sort -rn | head -n 5
    echo

    # TODO 5: últimos 5 CRITICAL
    echo "--- Últimos 5 CRITICAL ---"
    grep '\[CRITICAL\]' "$ARCHIVO" | tail -n 5
    echo

    # TODO 6: alerta por umbral
    if [ "$ERRORES" -ge "$UMBRAL" ]; then
        echo "ALERTA: $ERRORES errores (umbral: $UMBRAL)"
    else
        echo "OK: $ERRORES errores (umbral: $UMBRAL)"
    fi
} | tee "$SALIDA"

echo "Reporte guardado en $SALIDA"

if [ "$ERRORES" -ge "$UMBRAL" ]; then
    exit 2
fi
exit 0
