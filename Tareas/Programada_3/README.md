# Simulador de particiones fijas (First Fit y Best Fit)

**Tarea Programada 3** · Sistemas Operativos (IIIC 2026) · LEAD University

El programa simula una memoria principal dividida en **particiones de tamaño fijo**. Cada partición aloja un único proceso y el sobrante queda como **fragmentación interna**. El usuario elige entre dos estrategias para decidir en qué partición va cada proceso:

- **First Fit (primer ajuste):** la primera partición libre, en el orden en que se definieron, donde quepa el proceso.
- **Best Fit (mejor ajuste):** la partición libre más pequeña donde quepa; en empate, la de menor identificador.

Los procesos que no caben esperan en una **cola** (orden de llegada) que se revisa cada vez que se libera una partición. Solo usa la biblioteca estándar de Python (`sys`, `collections`, `dataclasses`), sin `pip install`. Requiere Python 3.10 o superior (probado con 3.12).

## Estructura de la carpeta

```
Programada_3/
├── particiones.py        Programa principal (menú de consola)
├── casos/                Entradas de prueba (una opción del menú por línea)
│   ├── escenario_1_ajuste_exacto.txt
│   ├── escenario_2_varias_particiones_{first,best}.txt
│   ├── escenario_3_no_cabe_en_libres.txt
│   ├── escenario_4_excede_maximo.txt
│   ├── escenario_5_todas_ocupadas.txt
│   ├── escenario_6_finalizar_asigna_espera.txt
│   ├── escenario_7_memoria_libre_suficiente.txt
│   ├── escenario_8_distinta_asignacion_{first,best}.txt    Ejemplo de la sección 5 del enunciado
│   ├── extra_best_peor_que_first_{first,best}.txt          Best Fit con más fragmentación que First Fit
│   └── errores_validacion.txt                               Entradas inválidas y mensajes de error
├── evidencias/           Salida de cada caso (*.out.txt)
├── informe/              Documento de análisis (PDF)
└── enunciado/            PDF entregado por el docente
```

## Uso

```powershell
python particiones.py
```

> Si `python` no se reconoce, prueba con `py particiones.py` (Windows) o `python3 particiones.py` (Linux/macOS).

Se maneja con este menú (la configuración y la estrategia se eligen **antes** de crear procesos):

| Opción | Acción |
|--------|--------|
| 1 | Configurar las particiones: cantidad y, para cada una, identificador y tamaño en KB |
| 2 | Seleccionar la estrategia: First Fit o Best Fit |
| 3 | Crear un proceso (id y tamaño en KB) e intentar asignarlo |
| 4 | Finalizar un proceso que está en memoria (libera su partición y revisa la cola) |
| 5 | Consultar el estado de las particiones |
| 6 | Consultar la cola de espera |
| 7 | Mostrar las estadísticas de utilización |
| 8 | Reiniciar la simulación (pide confirmación) |
| 9 | Salir |

Después de asignar o finalizar un proceso se imprime automáticamente el estado de la memoria.

### Repetir una sesión sin escribir cada opción

Cada archivo de `casos/` contiene lo que se escribiría a mano, una entrada por línea. Al redirigirlo, el programa repite lo que lee para que la traza se entienda:

```powershell
python particiones.py < casos/escenario_8_distinta_asignacion_best.txt
```

Para regenerar todas las evidencias (PowerShell, desde `Programada_3/`):

```powershell
Get-ChildItem casos/*.txt | ForEach-Object { Get-Content $_ | python particiones.py > "evidencias/$($_.BaseName).out.txt" }
```

## Salidas

### Estado de las particiones

```
Partición  Tamaño  Estado   Proceso  Memoria no utilizada
---------  ------  -------  -------  --------------------
        1  120 KB  Ocupada  P2                      10 KB
        2  300 KB  Ocupada  P1                     120 KB
        3  200 KB  Libre    —                      200 KB
        4  500 KB  Ocupada  P3                     250 KB
En espera: P4 (400 KB)
```

En las particiones ocupadas la última columna es **fragmentación interna**; en las libres es la **capacidad disponible**.

### Estadísticas

```
Memoria total                  : 1120 KB
Memoria utilizada por procesos :  540 KB
Memoria libre                  :  200 KB
Fragmentación interna          :  380 KB
Utilización efectiva           : 48.21 %
Procesos en espera             :     1
Procesos en memoria            :     3
Procesos finalizados           :     0
Verificación: 1120 = 540 + 380 + 200 -> OK
```

La utilización efectiva es `memoria utilizada ÷ memoria total × 100`. El programa verifica en cada consulta que **total = utilizada + fragmentación interna + libre**.

## Reglas implementadas

- Tamaños de particiones y procesos siempre **mayores que cero** (se vuelve a pedir el dato si es inválido). Identificadores de partición únicos y enteros positivos.
- No puede haber dos procesos **activos** (en memoria o esperando) con el mismo identificador. Un identificador de un proceso ya finalizado se puede volver a usar.
- Un proceso ocupa **una sola partición**; nunca se reparte entre varias, aunque la memoria libre total alcance. Cuando eso ocurre, el programa lo avisa.
- Cola de espera en orden de llegada. Al liberar una partición se revisa **toda** la cola: el que no cabe sigue esperando, pero se siguen revisando los siguientes.
- Solo se puede finalizar un proceso que esté en memoria (se rechazan los inexistentes, los que ya terminaron y los que están en cola).
- Las particiones y la estrategia **no se pueden cambiar** si hay procesos en el sistema; hay que reiniciar (opción 8).
- Sin compactación, sin mover procesos entre particiones y sin intercambio con disco.

## Decisiones y puntos del enunciado a tener presentes

- **Proceso mayor que la partición más grande.** La sección 3.2 del enunciado dice que se **rechaza** por imposibilidad de asignación, y eso hace el programa: muestra el error y el proceso no se registra (su id queda libre). En clase se comentó que podría ir a la cola y quedarse esperando para siempre. Si el profe prefiere eso, basta cambiar la constante `RECHAZAR_SI_EXCEDE_MAXIMO` a `False` en `particiones.py`.
- **Memoria libre.** Se calcula como la suma de las capacidades de las particiones desocupadas (sección 4), de modo que el sobrante de una partición ocupada cuenta solo como fragmentación interna.
- **Empates en Best Fit.** Gana la partición de menor identificador (no la de menor posición en la lista); coinciden salvo que se definan las particiones con identificadores desordenados.

## Organización del código

| Función / clase | Responsabilidad |
|-----------------|-----------------|
| `Particion`, `Proceso` | Datos de cada partición (id, tamaño, proceso, KB usados) y de cada proceso (id, tamaño, estado, partición) |
| `buscar_first_fit`, `buscar_best_fit` | Los dos algoritmos, por separado; reciben las particiones y el tamaño y devuelven la partición elegida (o `None`) |
| `ALGORITMOS` | Tabla que asocia cada estrategia con su función |
| `Simulador` | Estado de la simulación: particiones, estrategia, procesos activos, finalizados y cola. Validaciones, asignación, finalización, revisión de la cola y estadísticas |
| `tabla`, `formatear_particiones`, `formatear_cola`, `formatear_estadisticas`, `mostrar_estado`, `mostrar_menu` | Presentación |
| `leer`, `leer_entero_positivo` | Lectura y validación de la entrada |
| `opcion_*`, `main` | Una función por opción del menú y el ciclo principal |

## Casos de prueba (en `casos/`)

Configuración base: particiones de 120, 300, 200 y 500 KB (1120 KB), salvo que se indique otra.

| Escenario | Caso | Qué comprueba | Resultado |
|-----------|------|---------------|-----------|
| 1 | `escenario_1_ajuste_exacto` | Proceso que cabe exactamente | P1 (120 KB) → partición 1, fragmentación 0 |
| 2 | `escenario_2_varias_particiones_{first,best}` | Proceso de 180 KB, cabe en 300, 200 y 500 | First Fit → 300 (frag. 120 KB); Best Fit → 200 (frag. 20 KB) |
| 3 | `escenario_3_no_cabe_en_libres` | P1 500 KB ocupa la 4; P2 400 KB no cabe en las libres | P2 espera en la cola |
| 4 | `escenario_4_excede_maximo` | Proceso de 600 KB (mayor que 500) | Rechazado; no entra a la cola |
| 5 | `escenario_5_todas_ocupadas` | Particiones 100 y 200 ocupadas; llega un tercero | P3 espera |
| 6 | `escenario_6_finalizar_asigna_espera` | Al terminar P2, entra P3 que esperaba | P3 pasa de la cola a la partición 2 |
| 7 | `escenario_7_memoria_libre_suficiente` | Particiones 100, 100 y 300; P1 250 KB y P2 200 KB | 200 KB libres en total, pero P2 espera (el programa lo avisa) |
| 8 | `escenario_8_distinta_asignacion_{first,best}` | Procesos 180, 110 y 250 KB (ejemplo del enunciado) | First Fit: 380 KB de fragmentación; Best Fit: 80 KB |
| Extra | `extra_best_peor_que_first_{first,best}` | Particiones 500, 200 y 150; P1 180, P2 120, P3 140; termina P2 | Final: First Fit 330 KB; Best Fit 380 KB |
| Errores | `errores_validacion` | Datos inválidos, ids repetidos, finalizar inexistente o en cola, cambiar estrategia con procesos | Mensaje claro en cada caso; el programa sigue |
