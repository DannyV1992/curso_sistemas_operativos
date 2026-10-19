#!/usr/bin/env python3
"""
simulador_log.py - Genera un archivo .log "vivo" para practicar tail, grep, awk, etc.

Funciona en Linux, macOS y Windows 10/11 (solo requiere Python 3.8+, sin librerías externas).

Ejemplos:
  python3 simulador_log.py                         # escribe 2 líneas/seg en app.log sin parar (Ctrl+C para salir)
  python3 simulador_log.py --lineas 500            # genera 500 líneas de golpe y termina (modo lote)
  python3 simulador_log.py --tasa 10 --duracion 60 # 10 líneas/seg durante 60 segundos
  python3 simulador_log.py --formato web           # formato tipo access.log de Apache/Nginx
  python3 simulador_log.py --rafagas               # alterna periodos tranquilos con ráfagas de errores
  python3 simulador_log.py --rotar 200             # rota el archivo cada 200 líneas (app.log -> app.log.1)
  python3 simulador_log.py --semilla 42            # salida reproducible (útil para clases)
"""

import argparse
import os
import random
import sys
import time
from datetime import datetime, timedelta

SERVICIOS = ["auth", "pagos", "inventario", "api-gateway", "correo", "reportes"]
USUARIOS = ["ana", "bruno", "carla", "diego", "elena", "fabian", "gaby", "hugo", "admin", "root"]
IPS = ["192.168.1.10", "192.168.1.22", "10.0.0.5", "10.0.0.17", "172.16.4.2",
       "201.204.33.8", "186.15.70.120", "45.33.12.9"]  # las tres últimas: IPs externas "sospechosas"
RUTAS = ["/", "/login", "/logout", "/api/productos", "/api/pagos", "/api/usuarios/42",
         "/admin", "/static/app.js", "/static/logo.png", "/reportes/mensual"]
METODOS = ["GET", "GET", "GET", "POST", "PUT", "DELETE"]
AGENTES = ["Mozilla/5.0 (Windows NT 10.0)", "Mozilla/5.0 (Macintosh)", "curl/8.4.0",
           "python-requests/2.31", "Mozilla/5.0 (X11; Linux x86_64)"]

MENSAJES = {
    "DEBUG": ["Consulta SQL ejecutada en {ms} ms", "Cache hit para clave user:{n}",
              "Payload recibido de {b} bytes"],
    "INFO": ["Usuario {u} inició sesión desde {ip}", "Usuario {u} cerró sesión",
             "Pedido #{n} creado correctamente", "Reporte mensual generado en {ms} ms",
             "Correo enviado a {u}@ejemplo.com", "Health check OK"],
    "WARN": ["Tiempo de respuesta alto: {ms} ms en {ruta}", "Uso de memoria al {p}%",
             "Reintento {r}/3 conectando a la base de datos", "Token próximo a expirar para {u}"],
    "ERROR": ["Login fallido para usuario {u} desde {ipx}", "Login fallido para usuario {u} desde {ipx}", "Timeout conectando a db-primaria:5432",
              "Pago #{n} rechazado: fondos insuficientes", "NullPointerException en {serv}.procesar()",
              "Disco /var al {p}% de capacidad"],
    "CRITICAL": ["Servicio {serv} no responde", "Base de datos fuera de línea",
                 "Intentos de acceso masivos detectados desde {ipx}"],
}

PESOS_NORMAL = {"DEBUG": 15, "INFO": 60, "WARN": 15, "ERROR": 8, "CRITICAL": 2}
PESOS_RAFAGA = {"DEBUG": 5, "INFO": 15, "WARN": 25, "ERROR": 45, "CRITICAL": 10}


def rellenar(plantilla):
    return plantilla.format(
        ms=random.randint(5, 4000), n=random.randint(1000, 9999), b=random.randint(100, 90000),
        u=random.choice(USUARIOS), ip=random.choice(IPS),
        ruta=random.choice(RUTAS),
        ipx=random.choice(IPS[-3:] * 4 + IPS),  # los ataques vienen más de IPs externas
        p=random.randint(70, 99), r=random.randint(1, 3), serv=random.choice(SERVICIOS))


def linea_app(ts, pesos):
    nivel = random.choices(list(pesos), weights=list(pesos.values()))[0]
    serv = random.choice(SERVICIOS)
    pid = random.randint(1000, 9999)
    msg = rellenar(random.choice(MENSAJES[nivel]))
    return f"{ts:%Y-%m-%d %H:%M:%S} [{nivel}] {serv}[{pid}]: {msg}"


def linea_web(ts, pesos):
    # Mapea "gravedad" a códigos HTTP
    nivel = random.choices(list(pesos), weights=list(pesos.values()))[0]
    codigo = {"DEBUG": 304, "INFO": random.choice([200, 200, 201]),
              "WARN": random.choice([301, 404]), "ERROR": random.choice([401, 403, 500]),
              "CRITICAL": random.choice([502, 503])}[nivel]
    ip, metodo, ruta = random.choice(IPS), random.choice(METODOS), random.choice(RUTAS)
    tam = random.randint(200, 50000) if codigo < 400 else random.randint(0, 500)
    fecha = ts.strftime("%d/%b/%Y:%H:%M:%S -0600")
    return f'{ip} - - [{fecha}] "{metodo} {ruta} HTTP/1.1" {codigo} {tam} "-" "{random.choice(AGENTES)}"'


def rotar(ruta):
    """Rotación simple: app.log -> app.log.1 (se pisa el anterior)."""
    viejo = ruta + ".1"
    if os.path.exists(viejo):
        os.remove(viejo)
    os.replace(ruta, viejo)
    print(f"[simulador] Archivo rotado: {ruta} -> {viejo}", file=sys.stderr)


def main():
    ap = argparse.ArgumentParser(description="Simulador de archivos .log para practicar tail/grep.")
    ap.add_argument("--archivo", default="app.log", help="archivo de salida (por defecto app.log)")
    ap.add_argument("--formato", choices=["app", "web"], default="app", help="app (aplicación) o web (access.log)")
    ap.add_argument("--tasa", type=float, default=2.0, help="líneas por segundo en modo continuo")
    ap.add_argument("--duracion", type=float, default=0, help="segundos a ejecutar (0 = infinito)")
    ap.add_argument("--lineas", type=int, default=0, help="modo lote: genera N líneas y termina")
    ap.add_argument("--rafagas", action="store_true", help="alterna 20 s normales con 5 s de errores")
    ap.add_argument("--rotar", type=int, default=0, help="rota el archivo cada N líneas (0 = no rotar)")
    ap.add_argument("--semilla", type=int, default=None, help="semilla aleatoria para resultados reproducibles")
    ap.add_argument("--anexar", action="store_true", help="agrega al archivo existente en vez de vaciarlo")
    args = ap.parse_args()

    if args.semilla is not None:
        random.seed(args.semilla)
    generar = linea_app if args.formato == "app" else linea_web
    modo = "a" if args.anexar else "w"

    # ---------- Modo lote: historial con marcas de tiempo del pasado ----------
    if args.lineas > 0:
        ts = datetime.now() - timedelta(seconds=args.lineas * 3)
        with open(args.archivo, modo, encoding="utf-8", newline="\n") as f:
            for i in range(args.lineas):
                ts += timedelta(seconds=random.uniform(0.5, 5.5))
                rafaga = args.rafagas and (i % 125) >= 100
                f.write(generar(ts, PESOS_RAFAGA if rafaga else PESOS_NORMAL) + "\n")
        print(f"[simulador] {args.lineas} líneas escritas en {args.archivo}", file=sys.stderr)
        return

    # ---------- Modo continuo: el archivo "crece" en vivo ----------
    print(f"[simulador] Escribiendo en {args.archivo} a {args.tasa} líneas/s. Ctrl+C para detener.",
          file=sys.stderr)
    inicio, escritas = time.time(), 0
    f = open(args.archivo, modo, encoding="utf-8", newline="\n")
    try:
        while True:
            transcurrido = time.time() - inicio
            if args.duracion and transcurrido >= args.duracion:
                break
            rafaga = args.rafagas and (transcurrido % 25) >= 20
            f.write(generar(datetime.now(), PESOS_RAFAGA if rafaga else PESOS_NORMAL) + "\n")
            f.flush()  # importante: para que tail -f vea la línea de inmediato
            escritas += 1
            if args.rotar and escritas % args.rotar == 0:
                f.close()
                rotar(args.archivo)
                f = open(args.archivo, "w", encoding="utf-8", newline="\n")
            time.sleep(1.0 / args.tasa * (0.3 if rafaga else 1.0))
    except KeyboardInterrupt:
        pass
    finally:
        f.close()
        print(f"\n[simulador] Fin. {escritas} líneas escritas.", file=sys.stderr)


if __name__ == "__main__":
    main()
