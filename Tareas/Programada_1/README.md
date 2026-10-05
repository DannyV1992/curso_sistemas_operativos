# MiniOS — Simulador básico de procesos

**Tarea Programada 1** · Sistemas Operativos (IIIC 2026) · LEAD University

MiniOS simula un computador con **un único CPU** y una **cola FIFO** (First In, First Out). Los procesos se leen de un archivo CSV, llegan en distintos instantes, esperan en la cola y se ejecutan **sin interrupciones**: una vez que un proceso toma el CPU, lo conserva hasta terminar. Al final se calculan métricas de espera y retorno.

Solo usa la biblioteca estándar de Python (`csv`, `collections`, `dataclasses`, `datetime`, `pathlib`, `re`, `sys`, `unicodedata`). No requiere `pip install`.

## Estructura de la carpeta

```
Programada_1/
├── minios.py        Programa principal (menú interactivo)
├── casos/           CSV de entrada: aquí se agregan los archivos a ejecutar
│   ├── procesos.csv               Ejemplo del enunciado (4 procesos)
│   ├── caso1_un_proceso.csv
│   ├── caso2_misma_llegada.csv
│   ├── caso3_cpu_inactivo.csv
│   ├── caso4_proceso_largo.csv
│   └── caso5_errores.csv
├── salida/          Archivos generados, uno por ejecución (con fecha y hora en el nombre)
└── enunciado/       PDFs entregados por el docente
```

Las carpetas `casos/` y `salida/` se buscan junto a `minios.py`, así que el programa funciona aunque se ejecute desde otra ubicación.

## Requisitos

Python 3.10 o superior (usa la sintaxis `int | None`). Desarrollado y probado con Python 3.12.

## Uso

1. Abre una terminal (PowerShell, CMD o Git Bash) y ubícate en la carpeta `Programada_1`, es decir, la que contiene `minios.py`:

   ```
   cd "<ruta donde descargaste o clonaste el proyecto>/Programada_1"
   ```

2. Ejecuta el programa. No recibe argumentos: todo se elige desde el menú.

   ```powershell
   python minios.py
   ```

> Si `python` no se reconoce, prueba con `py minios.py` (Windows) o `python3 minios.py` (Linux/macOS).

### El menú

```
========================================
  MINIOS - Simulador de procesos
========================================
  1. Ejecutar un caso
  2. Ver casos disponibles
  0. Salir

Opción:
```

| Opción | Qué hace |
|--------|----------|
| `1` | Pide el archivo, simula, muestra el resumen final y guarda los archivos de salida (resultados, eventos y traza) |
| `2` | Lista los CSV que hay en `casos/` |
| `0` | Sale del programa |

Al elegir `1` se muestra la lista de casos y se pide el archivo. Se puede escribir:

- el **nombre** del archivo, con o sin `.csv` (`caso4_proceso_largo` o `caso4_proceso_largo.csv`), o
- el **número** que aparece en la lista (`4`).

Con solo pulsar Enter se cancela y se vuelve al menú. Después de cada ejecución el menú vuelve a aparecer, así que se pueden correr varios casos seguidos. `Ctrl+C` también sale del programa.

### Ejecutar tus propios procesos

Crea un archivo `.csv` dentro de `casos/` con el formato descrito en *Formato de entrada* y aparecerá en la lista la próxima vez que lo pidas.

### Dónde quedan los resultados

Cada ejecución guarda tres archivos en `salida/`. Sus nombres empiezan con la fecha y hora (`AAAAMMDD_HHMMSS`) y terminan con el caso, de modo que ninguna ejecución sobrescribe a otra y los archivos quedan ordenados cronológicamente, con los de una misma ejecución juntos:

```
salida/
├── 20261004_153012_resultados_caso4_proceso_largo.csv
├── 20261004_153012_eventos_caso4_proceso_largo.txt
└── 20261004_153012_traza_caso4_proceso_largo.txt
```

Si los datos tienen errores (por ejemplo el caso 5), no se simula: los errores se muestran en pantalla y se guardan en un único archivo, `<fecha_hora>_errores_<caso>.txt`, sin resultados, eventos ni traza. Ver la sección *Validaciones*.

## Formato de entrada

```csv
id,llegada,duracion
P1,0,5
P2,2,3
P3,3,8
P4,6,2
```

| Columna | Significado | Regla |
|---------|-------------|-------|
| `id` | Identificador único del proceso | No vacío, sin repetirse |
| `llegada` | Instante en que el proceso entra al sistema | Entero ≥ 0 |
| `duracion` | Unidades de tiempo de CPU que necesita | Entero > 0 |

Si varios procesos llegan en el mismo instante, se atienden en el orden en que aparecen en el archivo.

## Salidas

### En pantalla

```
========================================
  RESULTADO MINIOS
========================================

Proceso  Llegada  Inicio    Fin  Espera  Retorno
P1             0       0      5       0        5
P2             2       5      8       3        6
P3             3       8     16       5       13
P4             6      16     18      10       12

Procesos ejecutados: 4
Tiempo total: 18
Espera promedio: 4.50
Retorno promedio: 9.00
Mayor tiempo de espera: P4 (10)
Menor tiempo de espera: P1 (0)
Utilización del CPU: 100.00%
```

Si hay empates en la mayor o menor espera, se listan todos los procesos empatados.

### `<fecha_hora>_resultados_<caso>.csv`

Una fila por proceso, en el orden del archivo de entrada. Pensado para análisis posterior.

```csv
id,llegada,duracion,inicio,fin,espera,retorno
P1,0,5,0,5,0,5
P2,2,3,5,8,3,6
```

### `<fecha_hora>_eventos_<caso>.txt`

Registro de lo ocurrido durante la simulación:

```
[0] P1 llega al sistema
[0] P1 inicia ejecución
[2] P2 llega al sistema
[2] P2 entra a la cola
[5] P1 termina
[5] P2 inicia ejecución
```

El mensaje "entra a la cola" solo aparece cuando el proceso realmente tiene que esperar; si el CPU está libre al llegar, inicia de inmediato.

### `<fecha_hora>_traza_<caso>.txt`

La **traza** es el registro paso a paso de la simulación: además de los eventos, muestra en cada unidad de tiempo qué proceso está en el CPU, cuánto le queda y quién espera en la cola. Sirve para seguir el comportamiento FIFO instante por instante. Al final incluye el mismo **resumen** que se muestra en pantalla (tabla de procesos y métricas globales), para que esa información también quede guardada.

```
--- Traza de la simulacion ---
[0] P1 llega al sistema
[0] P1 inicia ejecucion
[0]   CPU: P1 (restante 15) | Cola: vacia
[1] P2 llega al sistema
[1] P2 entra a la cola
[1]   CPU: P1 (restante 14) | Cola: P2
...
[20] P4 termina

========================================
  RESULTADO MINIOS
========================================

Proceso  Llegada  Inicio    Fin  Espera  Retorno
P1             0       0     15       0       15
...

Procesos ejecutados: 4
Tiempo total: 20
...
```

## Cómo funciona la simulación

El tiempo comienza en 0 y avanza de una unidad en una. En cada instante `t`, `simular()` hace lo siguiente, en este orden:

1. **Terminar:** si el proceso en el CPU ya consumió toda su duración, termina en `t` y el CPU queda libre.
2. **Despachar:** si el CPU está libre y hay procesos en la cola, entra el primero.
3. **Llegadas:** los procesos con `llegada == t` ingresan en el orden del archivo. Si el CPU está libre arrancan de inmediato; si no, entran al final de la cola.
4. **Ejecutar:** el proceso en el CPU consume una unidad de tiempo.

La simulación termina cuando todos los procesos han terminado. Si el CPU y la cola están vacíos pero aún faltan llegadas, el reloj sigue avanzando (CPU inactivo).

Cada proceso pasa por los estados **Nuevo → Listo → Ejecutando → Terminado**.

### Métricas

$$\text{retorno} = \text{fin} - \text{llegada} \qquad \text{espera} = \text{inicio} - \text{llegada}$$

- **Tiempo total:** desde 0 hasta el `fin` del último proceso.
- **Utilización del CPU:** suma de duraciones ÷ tiempo total (métrica adicional, no exigida).

## Validaciones

Antes de simular se revisan todos los datos y se reportan **todos** los errores encontrados (con el número de línea), sin intentar repararlos. Si hay alguno, no se simula: solo se muestran en pantalla y se guardan en `<fecha_hora>_errores_<caso>.txt`, sin generar resultados, eventos ni traza.

- Archivo inexistente, vacío o sin procesos
- Encabezado distinto de `id,llegada,duracion`
- Filas incompletas o con columnas de más
- Valores que no son enteros (`ABC`, `1.5`, campos vacíos)
- Identificadores vacíos o duplicados
- Llegadas negativas
- Duraciones menores o iguales a cero

Ejemplo (caso 5):

```
No se puede ejecutar la simulación. Se encontraron errores en los datos:
  Línea 3: el tiempo de llegada no puede ser negativo (-2)
  Línea 4: el valor de 'llegada' ('ABC') no es un número entero
  Línea 5: la duración debe ser mayor que cero (-1)
```

El archivo `<fecha_hora>_errores_<caso>.txt` tiene este mismo texto, precedido de una línea `Archivo: caso5_errores.csv`.

## Organización del código

| Función | Responsabilidad |
|---------|-----------------|
| `leer_procesos` | Lee el CSV y valida la estructura (columnas, enteros) |
| `validar_procesos` | Valida reglas de negocio (ids, llegada ≥ 0, duración > 0) |
| `formatear_errores` | Arma el texto de los errores, igual para pantalla y archivo |
| `mostrar_errores` | Imprime los errores de datos en `stderr` |
| `guardar_errores` | Escribe el archivo de errores |
| `simular` | Simulación FIFO tick a tick; devuelve eventos y traza |
| `calcular_metricas` | Espera y retorno por proceso y métricas globales |
| `formatear_resumen` | Arma el texto del resumen (tabla y métricas), igual para pantalla y archivo |
| `mostrar_resumen` | Imprime el resumen en pantalla |
| `guardar_traza` | Escribe la traza instante por instante seguida del resumen |
| `guardar_resultados` | Escribe el CSV de resultados |
| `guardar_eventos` | Escribe el registro de eventos |
| `ejecutar_caso` | Lee, valida, simula, muestra y guarda un caso (con el timestamp en los nombres de salida) |
| `listar_casos`, `mostrar_casos`, `elegir_caso` | Listan los CSV de `casos/` y resuelven el nombre o número elegido |
| `mostrar_menu`, `menu` | Menú interactivo |

Los procesos se representan con el `dataclass` `Proceso`, que guarda id, llegada, duración, estado, tiempo restante, inicio, fin, espera y retorno.

## Casos de prueba

Los cinco escenarios mínimos del enunciado y el ejemplo del enunciado están en [casos/](casos/).

| Caso | Entrada | Qué comprueba | Resultado |
|------|---------|---------------|-----------|
| 1 — Un único proceso | `P1,0,5` | Funcionamiento básico | Espera 0.00, retorno 5.00 |
| 2 — Misma llegada | `P1,0,4` `P2,0,2` `P3,0,6` | Orden FIFO (por orden del archivo) | Espera 3.33, retorno 7.33; orden P1, P2, P3 |
| 3 — Llegadas separadas | `P1,0,2` `P2,5,3` `P3,10,2` | CPU inactivo entre procesos | Espera 0.00, retorno 2.33; utilización 58.33% |
| 4 — Proceso largo primero | `P1,0,15` `P2,1,2` `P3,2,1` `P4,3,2` | Efecto de un proceso largo sobre los que esperan | Espera 11.00, retorno 16.00; P3 y P4 esperan 15 |
| 5 — Archivo con errores | `P2,-2,4` `P3,ABC,3` `P4,5,-1` | Validaciones | 3 errores reportados y guardados en `..._errores_...txt`; no se simula |
| 6 — Ejemplo del enunciado | `P1,0,5` `P2,2,3` `P3,3,8` `P4,6,2` | Ejemplo general de la sección 4 del enunciado (archivo `procesos.csv`; no es uno de los 5 casos mínimos) | Espera 4.50, retorno 9.00; tiempo total 18; P4 espera más (10) |

En el caso 4 se ve la principal debilidad de FIFO: P3 dura 1 unidad pero espera 15 porque P1 (15 unidades) llegó antes. Es el llamado *efecto convoy*.

Para probarlos, ejecuta `python minios.py` y elige cada caso con la opción `1`. Las salidas de las corridas de ejemplo están en [salida/](salida/).

## Limitaciones conocidas

- Se ignora el costo del cambio de contexto (simplificación indicada en clase).
- El reloj avanza de a una unidad, por lo que duraciones o llegadas del orden de millones hacen la simulación lenta.
- No hay E/S ni estado *Waiting*: los procesos nunca se interrumpen.
