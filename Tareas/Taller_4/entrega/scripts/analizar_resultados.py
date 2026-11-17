#!/usr/bin/env python3
"""Procesa las carpetas de resultados/ del Laboratorio 4 y genera tablas y gráficas.

Lee, para cada corrida, los archivos que dejan monitorear.sh y correr_corrida.sh:
vmstat.txt, free.txt, psi.txt, top.txt, analisis.txt y marcas.txt.

Uso:
  python -I analizar_resultados.py
  python -I analizar_resultados.py --resultados resultados --salida ../graficas

Requisitos: pandas y matplotlib.
Firma: Daniel Vásquez González (DannyV1992) - Sistemas Operativos, LEAD University, III Cuat. 2026
"""

import argparse
import re
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

FMT = "%Y-%m-%d %H:%M:%S"
VM_COLS = ["r", "b", "swpd", "free", "buff", "cache", "si", "so", "bi", "bo",
           "in", "cs", "us", "sy", "id", "wa", "st", "gu"]
TAM_GB = {"demo": 0.2, "1gb": 1, "2gb": 2, "4gb": 4}

# Paleta validada con validate_palette (modo claro): una pareja categórica, un color por modo
AZUL, NARANJA = "#2a78d6", "#eb6834"
COLOR = {"chunks": AZUL, "full": NARANJA}
SUPERFICIE, TEXTO, TEXTO2, REJILLA, GUIA = "#fcfcfb", "#0b0b0b", "#52514e", "#e6e5e1", "#c4c3be"


def es(v, d=1):
    """Número con coma decimal (como en el documento) y sin separador de miles."""
    return f"{v:.{d}f}".replace(".", ",")


def res_ventana(c):
    """RES de Python solo mientras corre el análisis (fuera de ahí top muestra otro proceso python)."""
    tp = c["top"]
    return tp[(tp["t"] >= 0) & (tp["t"] <= c["t_fin"])]


def leyenda_trazos(ax, etiquetas):
    """Leyenda neutra (gris) para distinguir línea continua y punteada."""
    h = [plt.Line2D([0], [0], color=TEXTO2, lw=1.6, ls=ls, label=txt) for ls, txt in zip(("-", "--"), etiquetas)]
    ax.legend(handles=h, loc="center", fontsize=9)


# ----------------------------------------------------------------------------
# Lectura de los archivos de una corrida
# ----------------------------------------------------------------------------
def _dt(texto):
    return pd.to_datetime(texto.strip(), format=FMT)


def _kib(valor):
    """top muestra RES en KiB, o con sufijo m/g/t cuando es grande."""
    mult = {"k": 1, "m": 1024, "g": 1024 ** 2, "t": 1024 ** 3}
    if valor[-1].lower() in mult:
        return float(valor[:-1].replace(",", ".")) * mult[valor[-1].lower()]
    return float(valor)


def leer_marcas(d):
    marcas = {}
    p = d / "marcas.txt"
    if p.exists():
        for linea in p.read_text(encoding="utf-8").splitlines():
            partes = linea.split(maxsplit=1)
            if len(partes) == 2:
                marcas[partes[0]] = partes[1].strip()
    return marcas


def leer_analisis(d):
    p = d / "analisis.txt"
    if not p.exists():
        return {}
    texto = p.read_text(encoding="utf-8", errors="replace")
    patrones = {"duracion": r"Duración:\s*([\d.]+)", "rss": r"RSS máximo del proceso:\s*([\d.]+)",
                "filas": r"Filas procesadas:\s*([\d,]+)", "df_mib": r"DataFrame completo antes del filtro:\s*([\d.]+)"}
    out = {}
    for clave, patron in patrones.items():
        m = re.search(patron, texto)
        if m:
            out[clave] = float(m.group(1).replace(",", ""))
    return out


def leer_vmstat(p):
    filas = []
    for linea in p.read_text(encoding="utf-8").splitlines():
        t = linea.split()
        if len(t) == 20 and t[0].isdigit():
            filas.append([int(x) for x in t[:18]] + [t[18] + " " + t[19]])
    df = pd.DataFrame(filas, columns=VM_COLS + ["ts"])
    df["ts"] = pd.to_datetime(df["ts"], format=FMT)
    return df.iloc[1:].reset_index(drop=True)  # la 1.ª fila es el promedio desde el arranque


def leer_free(p):
    filas, ts, mem = [], None, None
    for linea in p.read_text(encoding="utf-8").splitlines():
        if linea.startswith("###"):
            ts, mem = _dt(linea[3:]), None
        elif linea.startswith("Mem:"):
            t = linea.split()
            mem = {"total": int(t[1]), "usada": int(t[2]), "disp": int(t[6])}
        elif linea.startswith("Swap:") and mem is not None:
            t = linea.split()
            filas.append({"ts": ts, **mem, "swap_total": int(t[1]), "swap_usado": int(t[2])})
    return pd.DataFrame(filas)


def leer_psi(p):
    filas, ts, fila = [], None, {}
    patron = re.compile(r"(some|full) avg10=([\d.]+) avg60=([\d.]+) avg300=([\d.]+) total=(\d+)")
    for linea in p.read_text(encoding="utf-8").splitlines():
        if linea.startswith("###"):
            ts, fila = _dt(linea[3:]), {}
            continue
        m = patron.match(linea)
        if m:
            tipo = m.group(1)
            fila[f"{tipo}10"], fila[f"{tipo}60"] = float(m.group(2)), float(m.group(3))
            fila[f"{tipo}_total"] = int(m.group(5))
            if "some10" in fila and "full10" in fila:
                filas.append({"ts": ts, **fila})
    return pd.DataFrame(filas)


def leer_top(p):
    """Por cada muestra, el proceso 'python*' con más memoria residente (RES)."""
    filas, ts, en_tabla, mejor = [], None, False, None

    def cerrar():
        if ts is not None:
            filas.append({"ts": ts, "pid": mejor[0] if mejor else np.nan,
                          "res_mib": mejor[1] / 1024 if mejor else np.nan})

    for linea in p.read_text(encoding="utf-8").splitlines():
        if linea.startswith("###"):
            cerrar()
            ts, en_tabla, mejor = _dt(linea[3:]), False, None
        elif linea.lstrip().startswith("PID USER"):
            en_tabla = True
        elif en_tabla:
            t = linea.split()
            if len(t) >= 12 and t[0].isdigit() and t[11].startswith("python"):
                res = _kib(t[5])
                if mejor is None or res > mejor[1]:
                    mejor = (int(t[0]), res)
    cerrar()
    return pd.DataFrame(filas)


def cargar(d):
    m = re.match(r"ventas_(demo|\d+gb)_(full|chunks)_(\d{8}_\d{6})$", d.name)
    if not m:
        return None
    archivo, modo, sello = m.groups()
    marcas = leer_marcas(d)
    inicio = _dt(marcas["inicio_analisis"])
    c = {"nombre": d.name, "archivo": archivo, "modo": modo, "sello": sello,
         "marcas": marcas, "analisis": leer_analisis(d),
         "vm": leer_vmstat(d / "vmstat.txt"), "free": leer_free(d / "free.txt"),
         "psi": leer_psi(d / "psi.txt"), "top": leer_top(d / "top.txt")}
    for clave in ("vm", "free", "psi", "top"):
        c[clave]["t"] = (c[clave]["ts"] - inicio).dt.total_seconds()
    c["fin"] = (_dt(marcas["fin_analisis"]) - inicio).total_seconds() if "fin_analisis" in marcas else None
    c["murio"] = "fin_analisis" not in marcas
    c["t_fin"] = c["fin"] if c["fin"] is not None else float(c["vm"]["t"].max())
    return c


# ----------------------------------------------------------------------------
# Métricas
# ----------------------------------------------------------------------------
def _corr(a, b):
    ok = np.isfinite(a) & np.isfinite(b)
    a, b = a[ok], b[ok]
    if len(a) < 5 or np.std(a) == 0 or np.std(b) == 0:
        return np.nan
    return float(np.corrcoef(a, b)[0, 1])


def metricas(c):
    t_fin = c["t_fin"]
    vm = c["vm"][(c["vm"]["t"] >= 0) & (c["vm"]["t"] <= t_fin)]
    fr = c["free"][(c["free"]["t"] >= 0) & (c["free"]["t"] <= t_fin)]
    ps = c["psi"][(c["psi"]["t"] >= 0) & (c["psi"]["t"] <= t_fin)]
    tp = c["top"][(c["top"]["t"] >= 0) & (c["top"]["t"] <= t_fin)]
    base = c["free"][c["free"]["t"] < 0]
    swap_base = float(base["swap_usado"].iloc[0]) if len(base) else np.nan
    a = c["analisis"]
    # Correlaciones dentro de la ventana de análisis (series alineadas por tiempo)
    uno = pd.merge_asof(fr[["t", "swap_usado", "disp"]].sort_values("t"),
                        tp[["t", "res_mib"]].dropna().sort_values("t"),
                        on="t", tolerance=2, direction="nearest").dropna()
    dos = pd.merge_asof(vm[["t", "so", "si"]].sort_values("t"),
                        ps[["t", "some10"]].sort_values("t"),
                        on="t", tolerance=2, direction="nearest").dropna()
    return {
        "corrida": c["nombre"], "archivo": c["archivo"], "modo": c["modo"],
        "termino": not c["murio"],
        "duracion_s": a.get("duracion", np.nan), "rss_max_mib": a.get("rss", np.nan),
        "ventana_s": round(t_fin, 1),
        "swap_inicio_mib": swap_base,
        "swap_max_mib": float(fr["swap_usado"].max()),
        "swap_extra_mib": float(fr["swap_usado"].max()) - swap_base,
        "so_total_mib": float(vm["so"].sum() / 1024), "si_total_mib": float(vm["si"].sum() / 1024),
        "so_max_kib_s": int(vm["so"].max()), "si_max_kib_s": int(vm["si"].max()),
        "wa_prom": float(vm["wa"].mean()), "wa_max": int(vm["wa"].max()),
        "bloq_max": int(vm["b"].max()),
        "disp_min_mib": float(fr["disp"].min()),
        "psi_some_max": float(ps["some10"].max()), "psi_full_max": float(ps["full10"].max()),
        "psi_some_s": float((ps["some_total"].iloc[-1] - ps["some_total"].iloc[0]) / 1e6),
        "psi_full_s": float((ps["full_total"].iloc[-1] - ps["full_total"].iloc[0]) / 1e6),
        "res_py_max_mib": float(tp["res_mib"].max()),
        "corr_res_swap": _corr(uno["res_mib"].to_numpy(), uno["swap_usado"].to_numpy()),
        "corr_res_disp": _corr(uno["res_mib"].to_numpy(), uno["disp"].to_numpy()),
        "corr_so_psi": _corr(dos["so"].to_numpy(dtype=float), dos["some10"].to_numpy()),
    }


# ----------------------------------------------------------------------------
# Gráficas
# ----------------------------------------------------------------------------
def estilo():
    plt.rcParams.update({
        "figure.facecolor": SUPERFICIE, "axes.facecolor": SUPERFICIE, "savefig.facecolor": SUPERFICIE,
        "axes.edgecolor": REJILLA, "axes.labelcolor": TEXTO2, "xtick.color": TEXTO2, "ytick.color": TEXTO2,
        "text.color": TEXTO, "axes.titlecolor": TEXTO, "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": True, "axes.grid.axis": "y", "grid.color": REJILLA, "grid.linewidth": 0.8,
        "axes.axisbelow": True, "font.size": 10, "axes.titlesize": 11, "axes.titleweight": "bold",
        "axes.titlelocation": "left", "legend.frameon": False, "lines.linewidth": 1.6,
        "lines.solid_capstyle": "round", "lines.solid_joinstyle": "round"})


def guardar(fig, ruta):
    fig.savefig(ruta, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  gráfica: {ruta}")


def marcar_ventana(ax, c, modo):
    ax.axvspan(0, c["t_fin"], color=COLOR[modo], alpha=0.07, lw=0)
    ax.axvline(0, color=GUIA, lw=1)
    if not c["murio"]:
        ax.axvline(c["t_fin"], color=GUIA, lw=1)


def fig_serie(serie, ruta):
    """Fig. 1: duración y memoria de las 6 corridas de cada modo (1 GB)."""
    fig, axs = plt.subplots(1, 2, figsize=(10, 4.4))
    medidas = (("duracion_s", "Duración de la corrida (s)"), ("rss_max_mib", "RSS máximo del proceso (MiB)"))
    for ax, (col, titulo) in zip(axs, medidas):
        for i, modo in enumerate(("chunks", "full")):
            v = serie[serie["modo"] == modo][col].dropna().to_numpy()
            ax.bar(i, v.mean(), width=0.38, color=COLOR[modo], alpha=0.22, lw=0)
            ax.plot(np.full(len(v), i) + np.linspace(-0.09, 0.09, len(v)), v, "o", color=COLOR[modo],
                    ms=7, mec=SUPERFICIE, mew=1.5)
            ax.annotate(f"media {es(v.mean())}", (i, max(v.max(), v.mean())), textcoords="offset points",
                        xytext=(0, 12), ha="center", va="bottom", color=TEXTO2, fontsize=9)
        ax.set_xticks([0, 1])
        ax.set_xticklabels(["chunks", "full"])
        ax.set_xlim(-0.6, 1.6)
        ax.set_ylim(0, serie[col].max() * 1.2)
        ax.set_title(titulo)
        ax.grid(axis="x", visible=False)
    n = serie.groupby("modo").size().min()
    fig.suptitle(f"Archivo de 1 GB: {n} corridas por modo, alternadas (cada punto es una corrida)",
                 x=0.01, ha="left", fontsize=12, color=TEXTO)
    guardar(fig, ruta)


def fig_linea_tiempo(rep, ruta):
    """Fig. 2: una corrida representativa de cada modo, lado a lado, con la misma escala vertical."""
    filas = ["Memoria disponible (MiB)", "Swap usado (MiB)", "Swapping (KiB/s)",
             "Presión de memoria, PSI (%)", "RES del proceso Python (MiB)"]
    fig, axs = plt.subplots(5, 2, figsize=(12, 13.5), sharex="col", sharey="row")
    for j, modo in enumerate(("chunks", "full")):
        c, col = rep[modo], COLOR[modo]
        vm, fr, ps, tp = c["vm"], c["free"], c["psi"], res_ventana(c)
        axs[0, j].plot(fr["t"], fr["disp"], color=col)
        axs[1, j].plot(fr["t"], fr["swap_usado"], color=col)
        axs[2, j].plot(vm["t"], vm["so"], color=col, label="sale al swap (so)")
        axs[2, j].plot(vm["t"], vm["si"], color=col, ls="--", label="entra desde el swap (si)")
        axs[3, j].plot(ps["t"], ps["some10"], color=col, label="some (al menos un proceso espera)")
        axs[3, j].plot(ps["t"], ps["full10"], color=col, ls="--", label="full (todos esperan)")
        axs[4, j].plot(tp["t"], tp["res_mib"], color=col, marker="o", ms=3)
        for i in range(5):
            marcar_ventana(axs[i, j], c, modo)
        axs[0, j].set_title(f"Modo {modo}  ({es(c['analisis'].get('duracion', 0))} s, "
                            f"RSS máx. {es(c['analisis'].get('rss', 0))} MiB)")
        axs[4, j].set_xlabel("Segundos desde el inicio del análisis")
        axs[4, j].grid(axis="x", visible=False)
    for i, nombre in enumerate(filas):
        axs[i, 0].set_ylabel(nombre)
    leyenda_trazos(axs[2, 0], ("sale al swap (so)", "entra desde el swap (si)"))
    leyenda_trazos(axs[3, 0], ("some: al menos un proceso espera", "full: todos esperan"))
    fig.suptitle("Archivo de 1 GB: el mismo cálculo en los dos modos (zona sombreada = el análisis)",
                 x=0.01, ha="left", fontsize=12, color=TEXTO, y=0.995)
    fig.tight_layout()
    guardar(fig, ruta)


def fig_superpuestas(serie_corridas, ruta):
    """Fig. 3: las 12 corridas superpuestas (reproducibilidad)."""
    fig, axs = plt.subplots(3, 1, figsize=(10, 10), sharex=True)
    for c in serie_corridas:
        col = COLOR[c["modo"]]
        axs[0].plot(c["free"]["t"], c["free"]["swap_usado"], color=col, alpha=0.75, lw=1.3)
        axs[1].plot(c["psi"]["t"], c["psi"]["some10"], color=col, alpha=0.75, lw=1.3)
        r = res_ventana(c)
        axs[2].plot(r["t"], r["res_mib"], color=col, alpha=0.75, lw=1.3)
    for ax, y in zip(axs, ("Swap usado (MiB)", "PSI some, promedio de 10 s (%)", "RES del proceso Python (MiB)")):
        ax.set_ylabel(y)
        ax.axvline(0, color=GUIA, lw=1)
    axs[2].set_xlabel("Segundos desde el inicio del análisis")
    axs[2].grid(axis="x", visible=False)
    handles = [plt.Line2D([0], [0], color=COLOR[m], lw=2, label=m) for m in ("chunks", "full")]
    axs[0].legend(handles=handles, loc="upper right")
    axs[0].set_title("Archivo de 1 GB: las 12 corridas de la serie superpuestas")
    fig.tight_layout()
    guardar(fig, ruta)


def fig_muerte(c, t_muerte, ruta):
    """Fig. 4: la corrida full con 2 GB, que el kernel termina."""
    fig, axs = plt.subplots(5, 1, figsize=(10, 12), sharex=True)
    col = COLOR["full"]
    vm, fr, ps, tp = c["vm"], c["free"], c["psi"], res_ventana(c)
    cap = float(fr["swap_total"].iloc[0])
    axs[0].plot(fr["t"], fr["swap_usado"], color=col)
    axs[0].axhline(cap, color=GUIA, lw=1)
    axs[0].set_ylim(0, cap * 1.08)
    axs[0].text(5, cap * 0.93, f"capacidad del swap ({cap:.0f} MiB)", color=TEXTO2, fontsize=9, va="top")
    axs[1].plot(fr["t"], fr["disp"], color=col)
    axs[2].plot(vm["t"], vm["wa"], color=col, label="CPU esperando disco (wa)")
    axs[2].plot(ps["t"], ps["some10"], color=col, ls="--", label="PSI some, 10 s")
    axs[3].plot(vm["t"], vm["b"], color=col)
    axs[4].plot(tp["t"], tp["res_mib"], color=col, marker="o", ms=3)
    for ax, y in zip(axs, ("Swap usado (MiB)", "Memoria disponible (MiB)", "Porcentaje (%)",
                           "Procesos bloqueados (b)", "RES del proceso Python (MiB)")):
        ax.set_ylabel(y)
        ax.axvline(0, color=GUIA, lw=1)
        ax.axvline(t_muerte, color=TEXTO2, lw=1.2)
    axs[0].text(t_muerte - 5, axs[0].get_ylim()[0], "el kernel mata\nal proceso", ha="right", va="bottom",
                color=TEXTO2, fontsize=9)
    axs[2].legend(loc="upper left", fontsize=9)
    axs[4].set_xlabel("Segundos desde el inicio del análisis")
    axs[4].grid(axis="x", visible=False)
    axs[0].set_title("Modo full con 2 GB: el swap se llena y el sistema mata el proceso")
    fig.tight_layout()
    guardar(fig, ruta)


def fig_escalado(res, ruta):
    """Fig. 5: duración y memoria según el tamaño del archivo."""
    fig, axs = plt.subplots(1, 2, figsize=(11, 4.6))
    ch = res[res["modo"] == "chunks"].groupby("archivo")[["duracion_s", "rss_max_mib"]].mean()
    ch["gb"] = [TAM_GB[a] for a in ch.index]
    ch = ch.sort_values("gb")
    fu = res[(res["modo"] == "full") & res["termino"]].groupby("archivo")[["duracion_s", "rss_max_mib"]].mean()
    fu["gb"] = [TAM_GB[a] for a in fu.index]
    muerto = res[(res["modo"] == "full") & ~res["termino"]]
    ax = axs[0]
    ax.plot(ch["gb"], ch["duracion_s"], "o-", color=AZUL, ms=7, mec=SUPERFICIE, mew=1.5)
    ax.plot(fu["gb"], fu["duracion_s"], "o", color=NARANJA, ms=8, mec=SUPERFICIE, mew=1.5)
    for gb, v in zip(ch["gb"], ch["duracion_s"]):
        ax.annotate(f"{v:.0f} s", (gb, v), textcoords="offset points", xytext=(0, 9), ha="center",
                    color=TEXTO2, fontsize=9)
    for gb, v in zip(fu["gb"], fu["duracion_s"]):
        ax.annotate(f"{v:.0f} s", (gb, v), textcoords="offset points", xytext=(0, 9), ha="center",
                    color=TEXTO2, fontsize=9)
    ax.set_title("Duración según el tamaño del archivo")
    ax.set_ylabel("Segundos")
    ax = axs[1]
    ax.plot(ch["gb"], ch["rss_max_mib"], "o-", color=AZUL, ms=7, mec=SUPERFICIE, mew=1.5)
    ax.plot(fu["gb"], fu["rss_max_mib"], "o", color=NARANJA, ms=8, mec=SUPERFICIE, mew=1.5)
    for gb, v in zip(ch["gb"], ch["rss_max_mib"]):
        ax.annotate(f"{v:.0f}", (gb, v), textcoords="offset points", xytext=(0, 9), ha="center",
                    color=TEXTO2, fontsize=9)
    for gb, v in zip(fu["gb"], fu["rss_max_mib"]):
        ax.annotate(f"{v:.0f}", (gb, v), textcoords="offset points", xytext=(0, 9), ha="center",
                    color=TEXTO2, fontsize=9)
    for _, f in muerto.iterrows():
        gb = TAM_GB[f["archivo"]]
        ax.plot([gb], [f["res_py_max_mib"]], "X", color=NARANJA, ms=11, mec=SUPERFICIE, mew=1.5)
        ax.annotate("murió (OOM killer)", (gb, f["res_py_max_mib"]), textcoords="offset points",
                    xytext=(0, 12), ha="center", color=TEXTO2, fontsize=9)
    ax.axhline(3398.8, color=GUIA, lw=1)
    ax.text(ax.get_xlim()[1], 3398.8 + 40, "RAM total de la máquina (3,3 GiB)", ha="right", va="bottom",
            color=TEXTO2, fontsize=9)
    ax.set_title("Memoria residente máxima (RSS)")
    ax.set_ylabel("MiB")
    for ax in axs:
        ax.set_xlabel("Tamaño del archivo (GB)")
        ax.set_xticks([0.2, 1, 2, 4])
        ax.set_xticklabels(["0,2", "1", "2", "4"])
        ax.set_ylim(0, ax.get_ylim()[1] * 1.1)
        ax.grid(axis="x", visible=False)
    handles = [plt.Line2D([0], [0], color=AZUL, marker="o", lw=2, label="chunks"),
               plt.Line2D([0], [0], color=NARANJA, marker="o", lw=0, label="full")]
    axs[0].legend(handles=handles, loc="lower right")
    fig.tight_layout()
    guardar(fig, ruta)


# ----------------------------------------------------------------------------
# Principal
# ----------------------------------------------------------------------------
def md(df, formato):
    """Tabla en Markdown a partir de un DataFrame."""
    cols = list(df.columns)
    lineas = ["| " + " | ".join(cols) + " |", "|" + "|".join(["---"] * len(cols)) + "|"]
    for _, f in df.iterrows():
        lineas.append("| " + " | ".join(formato.get(k, str)(f[k]) for k in cols) + " |")
    return "\n".join(lineas)


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    aqui = Path(__file__).resolve().parent
    ap = argparse.ArgumentParser(description="Analiza las corridas del Laboratorio 4.")
    ap.add_argument("--resultados", type=Path, default=aqui.parent / "resultados")
    ap.add_argument("--salida", type=Path, default=aqui.parent.parent / "graficas")
    ap.add_argument("--serie-desde", default="20261117_144000",
                    help="Las corridas de 1 GB desde esta marca (AAAAMMDD_HHMMSS) forman la serie repetida")
    ap.add_argument("--muerte-2gb", default="2026-11-17 14:29:21",
                    help="Hora en que el kernel mató la corrida full de 2 GB (sale de journalctl)")
    args = ap.parse_args()
    args.salida.mkdir(parents=True, exist_ok=True)
    estilo()

    corridas = [c for c in (cargar(d) for d in sorted(args.resultados.iterdir()) if d.is_dir()) if c]
    print(f"Corridas leídas: {len(corridas)}")
    res = pd.DataFrame([metricas(c) for c in corridas])
    res["sello"] = [c["sello"] for c in corridas]
    res["serie"] = (res["archivo"] == "1gb") & (res["sello"] >= args.serie_desde)
    ruta_csv = args.resultados.parent / "resumen_corridas.csv"
    res.drop(columns="sello").to_csv(ruta_csv, index=False)
    print(f"  tabla: {ruta_csv}")

    serie = res[res["serie"]]
    por_nombre = {c["nombre"]: c for c in corridas}

    # --- Tablas para el documento ---------------------------------------------------
    print("\n## Serie de 1 GB, corrida por corrida\n")
    t = serie.sort_values(["modo", "corrida"])[["corrida", "duracion_s", "rss_max_mib", "swap_extra_mib",
                                                 "so_total_mib", "wa_prom", "psi_some_max", "psi_some_s"]].copy()
    t["corrida"] = t["corrida"].str.replace("ventas_1gb_", "", regex=False)
    print(md(t, {"duracion_s": lambda x: f"{x:.2f}", "rss_max_mib": lambda x: f"{x:,.1f}",
                 "swap_extra_mib": lambda x: f"{x:,.0f}", "so_total_mib": lambda x: f"{x:,.0f}",
                 "wa_prom": lambda x: f"{x:.1f}", "psi_some_max": lambda x: f"{x:.1f}",
                 "psi_some_s": lambda x: f"{x:.1f}"}))

    print("\n## Resumen por modo (media, mínimo y máximo de la serie)\n")
    metr = [("duracion_s", "Duración (s)"), ("rss_max_mib", "RSS máximo (MiB)"),
            ("swap_extra_mib", "Swap adicional usado (MiB)"), ("so_total_mib", "Total enviado al swap (MiB)"),
            ("si_total_mib", "Total leído del swap (MiB)"), ("so_max_kib_s", "so máximo (KiB/s)"),
            ("wa_prom", "CPU en espera de disco, promedio (%)"), ("wa_max", "CPU en espera de disco, máximo (%)"),
            ("bloq_max", "Procesos bloqueados, máximo"), ("disp_min_mib", "Memoria disponible mínima (MiB)"),
            ("psi_some_max", "PSI some máximo (%)"), ("psi_full_max", "PSI full máximo (%)"),
            ("psi_some_s", "Segundos de espera 'some'"), ("psi_full_s", "Segundos de espera 'full'"),
            ("res_py_max_mib", "RES máximo de Python (MiB)")]
    filas = []
    for col, nombre in metr:
        f = {"Métrica": nombre}
        for modo in ("chunks", "full"):
            v = serie[serie["modo"] == modo][col]
            f[modo] = f"{v.mean():,.1f} ({v.min():,.1f} a {v.max():,.1f})"
        filas.append(f)
    print(md(pd.DataFrame(filas), {}))

    mc, mf = serie[serie["modo"] == "chunks"], serie[serie["modo"] == "full"]
    print(f"\nRazón de memoria full/chunks (RSS medio): {mf['rss_max_mib'].mean() / mc['rss_max_mib'].mean():.1f}x")
    print(f"Razón de tiempo full/chunks (duración media): {mf['duracion_s'].mean() / mc['duracion_s'].mean():.2f}x")

    print("\n## Correlaciones (Pearson) dentro de la ventana de análisis, corridas full de la serie\n")
    cor = mf[["corrida", "corr_res_swap", "corr_res_disp", "corr_so_psi"]].copy()
    cor["corrida"] = cor["corrida"].str.replace("ventas_1gb_", "", regex=False)
    print(md(cor, {k: (lambda x: f"{x:.2f}") for k in cor.columns if k != "corrida"}))
    print("\nMedia:", {k: round(float(mf[k].mean()), 2) for k in ("corr_res_swap", "corr_res_disp", "corr_so_psi")})
    print("Chunks (RES casi constante, la correlación con el swap no es significativa):",
          {k: (None if mc[k].isna().all() else round(float(mc[k].mean()), 2))
           for k in ("corr_res_swap", "corr_res_disp", "corr_so_psi")})

    print("\n## Corrida full de 2 GB (terminada por el kernel)\n")
    m2 = res[(res["archivo"] == "2gb") & (res["modo"] == "full")].iloc[0]
    for k in ("ventana_s", "swap_max_mib", "disp_min_mib", "wa_prom", "wa_max", "bloq_max", "psi_some_max",
              "psi_full_max", "psi_some_s", "psi_full_s", "res_py_max_mib"):
        print(f"  {k}: {m2[k]:.1f}")

    # --- Gráficas --------------------------------------------------------------------
    print("\nGráficas:")
    fig_serie(serie, args.salida / "01_serie_1gb.png")
    rep = {}
    for modo in ("chunks", "full"):
        s = serie[serie["modo"] == modo].copy()
        mediana = s["duracion_s"].median()
        elegido = s.iloc[(s["duracion_s"] - mediana).abs().argsort().iloc[0]]["corrida"]
        rep[modo] = por_nombre[elegido]
        print(f"  corrida representativa de {modo}: {elegido}")
    fig_linea_tiempo(rep, args.salida / "02_linea_de_tiempo_1gb.png")
    fig_superpuestas([por_nombre[n] for n in serie["corrida"]], args.salida / "03_serie_superpuesta.png")
    c2 = por_nombre[res[(res["archivo"] == "2gb") & (res["modo"] == "full")].iloc[0]["corrida"]]
    t_muerte = (_dt(args.muerte_2gb) - _dt(c2["marcas"]["inicio_analisis"])).total_seconds()
    fig_muerte(c2, t_muerte, args.salida / "04_full_2gb_muerte.png")
    fig_escalado(res, args.salida / "05_escalado_por_tamano.png")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
