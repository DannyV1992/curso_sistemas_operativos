#!/bin/bash
# correr_corrida.sh - Una corrida del Laboratorio 4: monitoreo + analizar_datos.py
# Uso: ./correr_corrida.sh ARCHIVO MODO [opciones de analizar_datos.py]
#   ej: ./correr_corrida.sh ventas_20gb.csv chunks --chunk-size 100000
#       ./correr_corrida.sh ventas_20gb.csv full --force
# Cada corrida crea resultados/<archivo>_<modo>_<fecha>/ con la salida del monitoreo,
# la salida del análisis (analisis.txt) y marcas.txt (hora de inicio/fin y código de salida).
# Firma: Daniel Vásquez González (DannyV1992) - Sistemas Operativos, LEAD University, III Cuat. 2026

ARCHIVO="${1:?Uso: $0 ARCHIVO full|chunks [opciones de analizar_datos.py]}"
MODO="${2:?Uso: $0 ARCHIVO full|chunks [opciones de analizar_datos.py]}"
shift 2

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
NOMBRE="$(basename "$ARCHIVO" .csv)_${MODO}_$(date +%Y%m%d_%H%M%S)"
DIR="$SCRIPT_DIR/resultados/$NOMBRE"
mkdir -p "$DIR"

if [ ! -f "$ARCHIVO" ]; then
    echo "Error: no existe el archivo '$ARCHIVO'" >&2
    exit 1
fi

# Vaciar la caché de archivos para que cada corrida parta de las mismas condiciones
sync
echo 3 | sudo tee /proc/sys/vm/drop_caches > /dev/null

"$SCRIPT_DIR/monitorear.sh" "$NOMBRE" 1 > /dev/null 2>&1 &
MON_PID=$!
trap 'kill "$MON_PID" 2>/dev/null' EXIT

echo "Corrida: $NOMBRE"
echo "Monitoreo iniciado; esperando 10 s antes del análisis..."
sleep 10

echo "inicio_analisis $(date '+%Y-%m-%d %H:%M:%S')" >> "$DIR/marcas.txt"
python3 "$SCRIPT_DIR/analizar_datos.py" --input "$ARCHIVO" --mode "$MODO" "$@" 2>&1 | tee "$DIR/analisis.txt"
CODIGO=${PIPESTATUS[0]}
echo "fin_analisis $(date '+%Y-%m-%d %H:%M:%S')" >> "$DIR/marcas.txt"
echo "codigo_salida $CODIGO" >> "$DIR/marcas.txt"   # 137 = el SO mató el proceso (OOM killer)

echo "Análisis terminado (código $CODIGO); 10 s más de monitoreo..."
sleep 10

kill "$MON_PID" 2>/dev/null
wait "$MON_PID" 2>/dev/null
echo "Resultados en $DIR"
exit "$CODIGO"
