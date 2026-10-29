"""Pruebas automáticas de MiniOS (Tarea Programada 2).

Ejecutar desde esta carpeta:
    python -m unittest -v
"""

import contextlib
import io
import random
import sys
import tempfile
import unittest
from collections import defaultdict, deque
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import minios  # noqa: E402

CASOS = Path(__file__).resolve().parent / "casos"

# Ejemplo conceptual de la sección 10 del enunciado
EJEMPLO_10 = [("P1", 0, 5), ("P2", 2, 3), ("P3", 3, 4)]
# Archivo procesos.csv de la sección 4 del enunciado
PROCESOS_CSV = [("P1", 0, 5), ("P2", 2, 3), ("P3", 3, 8), ("P4", 6, 2)]

LOG_SECCION_17 = """\
[0] P1 llega al sistema
[0] P1 inicia ejecución
[2] P2 llega al sistema
[2] P2 entra a la cola
[2] P1 agota su quantum (restante=3)
[2] P1 vuelve a la cola
[2] P2 inicia ejecución
[3] P3 llega al sistema
[3] P3 entra a la cola
[4] P2 agota su quantum (restante=1)
[4] P2 vuelve a la cola
[4] P1 retoma ejecución
[6] P1 agota su quantum (restante=1)
[6] P1 vuelve a la cola
[6] P3 inicia ejecución
[8] P3 agota su quantum (restante=2)
[8] P3 vuelve a la cola
[8] P2 retoma ejecución
[9] P2 termina
[9] P1 retoma ejecución
[10] P1 termina
[10] P3 retoma ejecución
[12] P3 termina
"""


def crear(datos):
    return [minios.Proceso(i, ll, d) for i, ll, d in datos]


def correr(datos, politica, quantum=None, costo=0):
    """Devuelve (procesos, simulacion, metricas) para una lista de tuplas (id, llegada, duracion)."""
    return minios.ejecutar_politica(crear(datos), politica, quantum, costo)


def fila(procesos, id_):
    p = next(p for p in procesos if p.id == id_)
    return (p.inicio, p.fin, p.espera, p.retorno, p.respuesta, p.expropiaciones)


def referencia(datos, quantum):
    """Simulador de referencia, tick a tick, escrito directamente desde las reglas 9.2 del enunciado.

    Es deliberadamente distinto del motor (los que llegan siempre pasan por la cola y el CPU se
    asigna una sola vez por instante) para poder contrastar ambos. quantum=None equivale a FIFO.
    """
    resto = {i: d for i, _, d in datos}
    llegan = defaultdict(list)
    for i, ll, _ in datos:
        llegan[ll].append(i)
    cola, actual, usado, t, ultimo = deque(), None, 0, 0, None
    inicio, fin, expropiaciones, cambios = {}, {}, defaultdict(int), 0
    while len(fin) < len(datos):
        if actual is not None and resto[actual] == 0:
            fin[actual] = t
            actual = None
        cola.extend(llegan.get(t, []))
        if actual is not None and quantum is not None and usado == quantum:
            if cola:
                expropiaciones[actual] += 1
                cola.append(actual)
                actual = None
            else:
                usado = 0
        if actual is None and cola:
            actual, usado = cola.popleft(), 0
            inicio.setdefault(actual, t)
            if ultimo is not None and ultimo != actual:
                cambios += 1
            ultimo = actual
        if actual is not None:
            resto[actual] -= 1
            usado += 1
        t += 1
    return inicio, fin, dict(expropiaciones), cambios


class PruebasEnunciado(unittest.TestCase):
    """Reproduce los ejemplos numéricos del enunciado."""

    def test_seccion_10_round_robin_quantum_2(self):
        procesos, _, m = correr(EJEMPLO_10, minios.RR, 2)
        self.assertEqual(fila(procesos, "P1"), (0, 10, 5, 10, 0, 2))
        self.assertEqual(fila(procesos, "P2"), (2, 9, 4, 7, 0, 1))
        self.assertEqual(fila(procesos, "P3"), (6, 12, 5, 9, 3, 1))
        self.assertAlmostEqual(m["espera_promedio"], 4.67, places=2)
        self.assertAlmostEqual(m["retorno_promedio"], 8.67, places=2)
        self.assertAlmostEqual(m["respuesta_promedio"], 1.00, places=2)
        self.assertEqual(m["tiempo_total"], 12)
        self.assertEqual(m["utilizacion_cpu"], 100.0)
        self.assertEqual(m["cambios_contexto"], 6)
        self.assertEqual(m["mayor_espera"], ("P1", 5))
        self.assertEqual(m["menor_espera"], ("P2", 4))

    def test_seccion_17_registro_de_eventos(self):
        _, sim, _ = correr(EJEMPLO_10, minios.RR, 2)
        texto = "".join(f"[{t}] {e}\n" for t, e in sim.eventos)
        self.assertEqual(texto, LOG_SECCION_17)

    def test_seccion_10_fifo(self):
        procesos, _, m = correr(EJEMPLO_10, minios.FIFO)
        self.assertAlmostEqual(m["espera_promedio"], 2.67, places=2)
        self.assertAlmostEqual(m["retorno_promedio"], 6.67, places=2)
        self.assertAlmostEqual(m["respuesta_promedio"], 2.67, places=2)

    def test_seccion_18_round_robin_quantum_3(self):
        procesos, _, m = correr(PROCESOS_CSV, minios.RR, 3)
        self.assertEqual(fila(procesos, "P1")[:5], (0, 11, 6, 11, 0))
        self.assertEqual(fila(procesos, "P2")[:5], (3, 6, 1, 4, 1))
        self.assertEqual(fila(procesos, "P3")[:5], (6, 18, 7, 15, 3))
        self.assertEqual(fila(procesos, "P4")[:5], (11, 13, 5, 7, 5))
        self.assertEqual(m["tiempo_total"], 18)
        self.assertAlmostEqual(m["espera_promedio"], 4.75)
        self.assertAlmostEqual(m["retorno_promedio"], 9.25)
        self.assertAlmostEqual(m["respuesta_promedio"], 2.25)
        self.assertEqual(m["utilizacion_cpu"], 100.0)
        self.assertEqual(m["cambios_contexto"], 5)

    def test_seccion_18_expropiaciones(self):
        # La tabla del enunciado indica 2 expropiaciones para P3, pero a las 16 P3 agota su
        # quantum con la cola vacía y, según la regla 9.2.7, ahí NO hay expropiación: solo
        # pierde el CPU una vez (a las 9). Se sigue la regla (ver README).
        procesos, _, _ = correr(PROCESOS_CSV, minios.RR, 3)
        self.assertEqual([p.expropiaciones for p in procesos], [1, 0, 1, 0])


class PruebasReglas(unittest.TestCase):
    def test_empate_nuevos_entran_antes_que_el_expropiado(self):
        # P2 y P3 llegan en t=3, justo cuando P1 agota su quantum (q=3)
        procesos, sim, _ = correr([("P1", 0, 6), ("P2", 3, 2), ("P3", 3, 4)], minios.RR, 3)
        textos = [e for t, e in sim.eventos if t == 3]
        self.assertLess(textos.index("P3 entra a la cola"), textos.index("P1 vuelve a la cola"))
        self.assertEqual(textos[-1], "P2 inicia ejecución")  # P2 (primero en el archivo) pasa antes que P1
        self.assertEqual([e for t, e in sim.eventos if "retoma" in e][0], "P1 retoma ejecución")
        self.assertEqual(procesos[0].inicio, 0)

    def test_cola_vacia_no_hay_expropiacion_ni_cambio_de_contexto(self):
        procesos, sim, m = correr([("P1", 0, 7)], minios.RR, 3)
        self.assertEqual(procesos[0].expropiaciones, 0)
        self.assertEqual(m["cambios_contexto"], 0)
        self.assertEqual((procesos[0].inicio, procesos[0].fin), (0, 7))

    def test_proceso_que_termina_justo_al_agotar_el_quantum(self):
        procesos, _, _ = correr([("P1", 0, 4), ("P2", 1, 2)], minios.RR, 4)
        self.assertEqual(fila(procesos, "P1"), (0, 4, 0, 4, 0, 0))
        self.assertEqual(fila(procesos, "P2")[0], 4)  # arranca en el mismo instante en que P1 termina

    def test_cpu_ocioso(self):
        procesos, sim, m = correr([("P1", 0, 2), ("P2", 10, 3)], minios.FIFO)
        self.assertEqual(m["tiempo_total"], 13)
        self.assertAlmostEqual(m["utilizacion_cpu"], 5 / 13 * 100)
        self.assertIn((2, "CPU ocioso (no hay procesos listos)"), sim.eventos)
        self.assertEqual(m["cambios_contexto"], 1)  # P2 es un proceso distinto del último que usó el CPU

    def test_cpu_ocioso_al_inicio(self):
        procesos, sim, _ = correr([("P1", 4, 2)], minios.RR, 3)
        self.assertEqual((procesos[0].inicio, procesos[0].fin), (4, 6))
        self.assertEqual(sim.eventos[0], (0, "CPU ocioso (no hay procesos listos)"))

    def test_misma_llegada_respeta_orden_del_archivo(self):
        procesos, _, _ = correr([("A", 0, 5), ("B", 0, 3), ("C", 0, 4)], minios.FIFO)
        self.assertEqual([p.inicio for p in procesos], [0, 5, 8])

    def test_fifo_espera_igual_a_respuesta(self):
        procesos, _, _ = correr(PROCESOS_CSV, minios.FIFO)
        self.assertTrue(all(p.espera == p.respuesta for p in procesos))
        self.assertTrue(all(p.expropiaciones == 0 for p in procesos))

    def test_quantum_mayor_o_igual_que_el_proceso_mas_largo_equivale_a_fifo(self):
        for datos in (PROCESOS_CSV, EJEMPLO_10, [("A", 0, 5), ("B", 0, 3), ("C", 20, 4)]):
            mayor = max(d for _, _, d in datos)
            fifo, _, mf = correr(datos, minios.FIFO)
            rr, _, mr = correr(datos, minios.RR, mayor)
            self.assertEqual([fila(fifo, p.id) for p in fifo], [fila(rr, p.id) for p in rr])
            self.assertEqual(mf["cambios_contexto"], mr["cambios_contexto"])
            self.assertEqual(mf["espera_promedio"], mr["espera_promedio"])

    def test_quantum_uno(self):
        procesos, _, m = correr([("P1", 0, 3), ("P2", 1, 2), ("P3", 2, 1)], minios.RR, 1)
        # Cola tras cada instante: t1 [P2,P1], t2 [P1,P3,P2], t3 [P3,P2,P1]
        self.assertEqual([p.fin for p in procesos], [6, 5, 4])
        self.assertEqual(m["tiempo_total"], 6)

    def test_empates_en_mayor_y_menor_espera_muestran_el_primero_del_archivo(self):
        _, _, m = correr([("A", 0, 2), ("B", 0, 2), ("C", 0, 2)], minios.RR, 5)
        self.assertEqual(m["mayor_espera"], ("C", 4))
        _, _, m = correr([("A", 0, 1), ("B", 5, 1)], minios.FIFO)
        self.assertEqual(m["menor_espera"], ("A", 0))  # A y B esperan 0: se muestra A

    def test_duraciones_enormes(self):
        procesos, _, m = correr([("P1", 0, 10**12), ("P2", 1, 10**12)], minios.RR, 10**6)
        self.assertEqual(m["tiempo_total"], 2 * 10**12)


class PruebasContraReferencia(unittest.TestCase):
    """El motor (que salta de evento en evento) debe coincidir con el simulador tick a tick."""

    def test_casos_aleatorios(self):
        azar = random.Random(2026)
        for _ in range(400):
            n = azar.randint(1, 8)
            datos = [(f"P{i}", azar.randint(0, 15), azar.randint(1, 12)) for i in range(n)]
            quantum = azar.choice([None, 1, 2, 3, 5, 8, 20])
            politica = minios.FIFO if quantum is None else minios.RR
            procesos, sim, m = correr(datos, politica, quantum)
            inicio, fin, expropiaciones, cambios = referencia(datos, quantum)
            with self.subTest(datos=datos, quantum=quantum):
                self.assertEqual({p.id: p.inicio for p in procesos}, inicio)
                self.assertEqual({p.id: p.fin for p in procesos}, fin)
                self.assertEqual({p.id: p.expropiaciones for p in procesos if p.expropiaciones},
                                 {k: v for k, v in expropiaciones.items() if v})
                self.assertEqual(m["cambios_contexto"], cambios)
                # Invariantes de las métricas
                self.assertEqual(sim.tiempo_util, sum(p.duracion for p in procesos))
                for p in procesos:
                    self.assertEqual(p.retorno, p.fin - p.llegada)
                    self.assertEqual(p.espera, p.retorno - p.duracion)
                    self.assertGreaterEqual(p.espera, 0)
                    self.assertLessEqual(p.respuesta, p.espera)


class PruebasCostoCambio(unittest.TestCase):
    def test_costo_cero_no_cambia_nada(self):
        a, _, ma = correr(PROCESOS_CSV, minios.RR, 3, 0)
        b, _, mb = correr(PROCESOS_CSV, minios.RR, 3)
        self.assertEqual([fila(a, p.id) for p in a], [fila(b, p.id) for p in b])

    def test_costo_uno_agrega_una_unidad_por_cambio(self):
        procesos, sim, m = correr(PROCESOS_CSV, minios.RR, 3, 1)
        self.assertEqual(m["cambios_contexto"], 5)
        self.assertEqual(m["tiempo_cambios"], 5)
        self.assertEqual(m["tiempo_total"], 18 + 5)
        self.assertAlmostEqual(m["utilizacion_cpu"], 18 / 23 * 100)
        self.assertEqual(sim.tiempo_util, 18)


class PruebasDatos(unittest.TestCase):
    def errores(self, nombre):
        procesos, errores = minios.cargar_procesos(CASOS / nombre)
        return errores

    def test_archivos_validos(self):
        for ruta in sorted(CASOS.glob("*.csv")):
            if ruta.name.startswith("error_"):
                continue
            with self.subTest(archivo=ruta.name):
                self.assertEqual(minios.cargar_procesos(ruta)[1], [])

    def test_valores_invalidos(self):
        self.assertEqual(sorted(linea for linea, _ in self.errores("error_valores_invalidos.csv")), [3, 4, 5, 6])

    def test_ids_vacio_y_duplicado(self):
        mensajes = [m for _, m in self.errores("error_ids_vacio_duplicado.csv")]
        self.assertEqual(len(mensajes), 2)
        self.assertTrue(any("duplicado" in m for m in mensajes))
        self.assertTrue(any("vacío" in m for m in mensajes))

    def test_filas_incompletas_y_con_columnas_de_mas(self):
        mensajes = [m for _, m in self.errores("error_filas_mal_formadas.csv")]
        self.assertTrue(any("incompleta" in m for m in mensajes))
        self.assertTrue(any("demasiadas" in m for m in mensajes))

    def test_archivo_vacio_sin_procesos_encabezado_e_inexistente(self):
        self.assertIn("vacío", self.errores("error_archivo_vacio.csv")[0][1])
        self.assertIn("no contiene procesos", self.errores("error_sin_procesos.csv")[0][1])
        self.assertIn("encabezado", self.errores("error_encabezado.csv")[0][1])
        self.assertIn("no existe", self.errores("no_existe.csv")[0][1])


class PruebasParametros(unittest.TestCase):
    def test_valores_por_defecto(self):
        config, errores = minios.leer_parametros([])
        self.assertEqual(errores, [])
        self.assertEqual((config.politica, config.quantum, config.costo_cambio), ("rr", 3, 0))
        self.assertTrue(config.archivo.is_file())
        self.assertEqual(config.archivo.name, "procesos.csv")

    def test_fifo_ignora_el_quantum(self):
        config, errores = minios.leer_parametros(["--politica", "fifo", "--quantum", "abc"])
        self.assertEqual(errores, [])
        self.assertIsNone(config.quantum)

    def test_politica_desconocida(self):
        self.assertEqual(len(minios.leer_parametros(["--politica", "sjf"])[1]), 1)

    def test_quantum_invalido_con_rr(self):
        for valor in ("0", "-3", "abc", "2.5", ""):
            with self.subTest(quantum=valor):
                self.assertEqual(len(minios.leer_parametros(["--politica", "rr", "--quantum", valor])[1]), 1)

    def test_politica_en_mayusculas(self):
        self.assertEqual(minios.leer_parametros(["--politica", "RR", "--quantum", "2"])[0].quantum, 2)

    def test_costo_invalido(self):
        self.assertEqual(len(minios.leer_parametros(["--costo-cambio", "-1"])[1]), 1)
        self.assertEqual(len(minios.leer_parametros(["--costo-cambio", "x"])[1]), 1)


class PruebasPrograma(unittest.TestCase):
    def ejecutar(self, argv):
        salida, error = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(salida), contextlib.redirect_stderr(error):
            codigo = minios.main(argv)
        return codigo, salida.getvalue(), error.getvalue()

    def test_genera_resultados_y_eventos(self):
        with tempfile.TemporaryDirectory() as tmp:
            codigo, salida, _ = self.ejecutar(["--archivo", "ejemplo_enunciado_seccion10", "--quantum", "2", "--salida", tmp])
            self.assertEqual(codigo, 0)
            resultados = (Path(tmp) / "resultados.csv").read_text(encoding="utf-8")
            self.assertEqual(resultados, "id,llegada,duracion,inicio,fin,espera,retorno,respuesta,expropiaciones\n"
                                         "P1,0,5,0,10,5,10,0,2\nP2,2,3,2,9,4,7,0,1\nP3,3,4,6,12,5,9,3,1\n")
            self.assertEqual((Path(tmp) / "eventos.txt").read_text(encoding="utf-8"), LOG_SECCION_17)
        self.assertIn("Política: Round Robin (quantum = 2)", salida)
        self.assertIn("Cambios de contexto: 6", salida)

    def test_errores_de_datos_no_simulan_ni_escriben_archivos(self):
        with tempfile.TemporaryDirectory() as tmp:
            codigo, salida, error = self.ejecutar(["--archivo", "error_valores_invalidos", "--salida", tmp])
            self.assertEqual(codigo, 1)
            self.assertEqual(salida, "")
            self.assertIn("Línea 3", error)
            self.assertEqual(list(Path(tmp).iterdir()), [])

    def test_parametros_invalidos(self):
        codigo, salida, error = self.ejecutar(["--politica", "xyz"])
        self.assertEqual((codigo, salida), (2, ""))
        self.assertIn("política desconocida", error)

    def test_comparar(self):
        with tempfile.TemporaryDirectory() as tmp:
            codigo, salida, _ = self.ejecutar(["--comparar", "--quantum", "3", "--salida", tmp])
            self.assertEqual(codigo, 0)
            self.assertEqual(list(Path(tmp).iterdir()), [])
        self.assertIn("FIFO", salida)
        self.assertIn("RR (q=3)", salida)
        self.assertIn("4.75", salida)  # espera promedio de Round Robin
        self.assertIn("4.50", salida)  # espera promedio de FIFO


if __name__ == "__main__":
    unittest.main()
