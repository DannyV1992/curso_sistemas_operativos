# MiniOS — Planificación de procesos con Round Robin

**Tarea Programada 2** · Sistemas Operativos (IIIC 2026) · LEAD University

MiniOS simula un computador con **un único CPU** y una **cola de procesos listos**. Extiende el simulador de la Tarea 1 con dos políticas, que se eligen desde la línea de comandos:

- **FIFO:** el proceso que obtiene el CPU lo conserva hasta terminar (igual que en la Tarea 1).
- **Round Robin (RR):** cada proceso usa el CPU un máximo de *Q* unidades consecutivas (el *quantum*). Si no ha terminado, pierde el CPU y vuelve al final de la cola.

Solo usa la biblioteca estándar de Python (`argparse`, `csv`, `collections`, `dataclasses`, `pathlib`, `re`, `sys`). No requiere `pip install`. Requiere Python 3.10 o superior (probado con 3.12).

## Estructura de la carpeta

```
Programada_2/
├── minios.py                    Programa principal
├── procesos.csv                 Ejemplo del enunciado (4 procesos)
├── casos/                       Archivos de prueba propios
│   ├── un_solo_proceso.csv
│   ├── misma_llegada.csv
│   ├── desempate_quantum.csv
│   ├── cpu_ocioso.csv
│   ├── quantum_uno.csv
│   ├── ejemplo_enunciado_seccion10.csv
│   ├── comparativo_8_procesos.csv      Archivo de 8 procesos usado en el informe
│   └── error_*.csv                     Seis archivos inválidos para los mensajes de error
├── ejemplo/                     resultados.csv y eventos.txt de ejemplo (procesos.csv, rr, quantum 3)
├── informe/                     Informe de análisis comparativo
└── enunciado/                   PDF entregado por el docente
```

## Uso

Desde la carpeta que contiene `minios.py`:

```powershell
python minios.py --archivo procesos.csv --politica rr --quantum 3
```

> Si `python` no se reconoce, prueba con `py minios.py` (Windows) o `python3 minios.py` (Linux/macOS).

| Parámetro | Significado | Valor por defecto |
|-----------|-------------|-------------------|
| `--archivo` | Ruta del CSV con los procesos | `procesos.csv` |
| `--politica` | `fifo` o `rr` | `rr` |
| `--quantum` | Entero mayor que cero. Solo se usa con `rr`; con `fifo` se ignora | `3` |
| `--salida` | Carpeta donde se escriben `resultados.csv` y `eventos.txt` | la carpeta actual |
| `--comparar` | **[Extra]** Ejecuta FIFO y Round Robin sobre el mismo archivo y los muestra lado a lado | — |
| `--costo-cambio` | **[Extra]** Unidades de tiempo que consume cada cambio de contexto | `0` |

- Se puede ejecutar sin ningún parámetro: usa los valores por defecto. Nunca pide datos con `input()`.
- El archivo se busca primero tal como se escribió, luego junto a `minios.py` y luego en `casos/`; la extensión `.csv` es opcional (`--archivo cpu_ocioso` equivale a `casos/cpu_ocioso.csv`).
- Una política desconocida o un quantum inválido (con `rr`) muestran un mensaje y terminan **sin simular** (código de salida 2). Los errores en los datos terminan con código 1.

Ejemplos:

```powershell
python minios.py                                                  # rr, quantum 3, procesos.csv
python minios.py --politica fifo                                  # FIFO
python minios.py --archivo casos/comparativo_8_procesos.csv --quantum 5
python minios.py --comparar --quantum 3                           # FIFO vs RR lado a lado
python minios.py --costo-cambio 1 --quantum 1                     # cada cambio de contexto cuesta 1 unidad
python minios.py --salida ejemplo                                 # escribe los archivos en ejemplo/
```

## Formato de entrada

Igual que en la Tarea 1:

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
| `duracion` | Unidades de CPU que necesita | Entero > 0 |

Si varios procesos llegan en el mismo instante, entran a la cola en el orden en que aparecen en el archivo.

## Cómo funciona la simulación

El tiempo comienza en 0. En cada instante `t` el simulador hace lo siguiente, en este orden (clase `Simulador`):

1. **Terminar:** si el proceso en el CPU consumió toda su duración, termina en `t` y libera el CPU.
2. **Despachar:** si el CPU está libre, entra el primero de la cola.
3. **Llegadas:** los procesos con `llegada == t` entran en el orden del archivo. Si el CPU está libre arrancan de inmediato; si no, entran al final de la cola.
4. **Quantum:** si el proceso en el CPU agotó su quantum y todavía le queda tiempo:
   - con la cola **no vacía** es expropiado y entra al final de la cola, **después** de los que acaban de llegar en ese instante (regla de desempate);
   - con la cola **vacía** sigue con un nuevo quantum, sin expropiación ni cambio de contexto.
5. **Despachar** de nuevo si el CPU quedó libre.
6. **Avanzar** el reloj hasta el próximo evento (llegada, fin de quantum o fin de proceso). Si el CPU y la cola están vacíos pero faltan llegadas, el CPU queda **ocioso** y el reloj salta a la próxima llegada.

Saltar de evento en evento da exactamente el mismo resultado que avanzar de a una unidad, pero permite simular duraciones enormes sin esperar. FIFO es el mismo motor sin quantum.

Estados: **Nuevo → Listo → Ejecutando → Terminado**, y ahora también **Ejecutando → Listo** al ser expropiado.

**Cambio de contexto:** se cuenta cada vez que el CPU se asigna a un proceso distinto del último que lo utilizó (la primera asignación no cuenta). Por defecto no consume tiempo.

## Métricas

$$\text{retorno} = \text{fin} - \text{llegada} \qquad \text{espera} = \text{retorno} - \text{duracion} \qquad \text{respuesta} = \text{inicio} - \text{llegada}$$

- `inicio` es la **primera** vez que el proceso obtiene el CPU. La espera suma todas las veces que el proceso estuvo en la cola.
- En FIFO la espera y la respuesta de un proceso son iguales.
- **Utilización del CPU** = unidades en que el CPU ejecutó procesos ÷ tiempo total × 100.
- Si hay empate en mayor o menor espera, se muestra el primer proceso en el orden del archivo.

## Salidas

### En pantalla

```
===============================
RESULTADO MINIOS
Política: Round Robin (quantum = 2)
===============================
Proceso  Llegada  Inicio    Fin  Espera  Retorno  Respuesta
P1             0       0     10       5       10          0
P2             2       2      9       4        7          0
P3             3       6     12       5        9          3
Procesos ejecutados: 3
Tiempo total: 12
Espera promedio: 4.67
Retorno promedio: 8.67
Respuesta promedio: 1.00
Mayor espera: P1 (5)
Menor espera: P2 (4)
Utilización del CPU: 100.0%
Cambios de contexto: 6
```

### `resultados.csv`

Una fila por proceso, en el orden del archivo de entrada:

```csv
id,llegada,duracion,inicio,fin,espera,retorno,respuesta,expropiaciones
P1,0,5,0,10,5,10,0,2
P2,2,3,2,9,4,7,0,1
P3,3,4,6,12,5,9,3,1
```

`expropiaciones` es el número de veces que el proceso perdió el CPU sin haber terminado.

### `eventos.txt`

Registro de lo ocurrido, con el tiempo entre corchetes. Incluye llegadas, entradas a la cola, inicios y reanudaciones, quantums agotados, regresos a la cola, terminaciones y los periodos de CPU ocioso:

```
[0] P1 llega al sistema
[0] P1 inicia ejecución
[2] P2 llega al sistema
[2] P2 entra a la cola
[2] P1 agota su quantum (restante=3)
[2] P1 vuelve a la cola
[2] P2 inicia ejecución
...
```

Si el quantum se agota con la cola vacía se registra `Pn continúa con un nuevo quantum (la cola está vacía)`. Con `--costo-cambio` aparece además `cambio de contexto Pa -> Pb (costo=N)`.

Estos dos archivos se **sobrescriben** en cada corrida. Si se quieren conservar, se copian o se usa `--salida` con otra carpeta. Los archivos de `ejemplo/` se generaron con `python minios.py --archivo procesos.csv --politica rr --quantum 3 --salida ejemplo`.

### Opciones extra

- **`--comparar`:** ejecuta FIFO y RR sobre el archivo y muestra una tabla por proceso (espera, retorno y respuesta de cada política) y una tabla de métricas globales. No escribe archivos.
- **`--costo-cambio N`:** cada cambio de contexto deja al CPU *N* unidades sin ejecutar ningún proceso (las llegadas siguen ocurriendo durante ese tiempo). El resumen agrega el tiempo perdido, y la utilización pasa a ser el trabajo útil ÷ el tiempo total. El `inicio` de un proceso es el instante en que empieza a ejecutar, después del cambio.

## Validaciones

Antes de simular se revisan todos los datos y se reportan **todos** los errores encontrados (con el número de línea), sin intentar repararlos:

- Archivo inexistente, vacío o sin procesos; encabezado distinto de `id,llegada,duracion`.
- Filas incompletas o con columnas de más.
- Valores que no son enteros; llegadas negativas; duraciones ≤ 0.
- Identificadores vacíos o duplicados.
- Política desconocida y quantum que no sea un entero mayor que cero (con `rr`); costo de cambio inválido.

```
No se puede ejecutar la simulación. Se encontraron errores en los datos:
  Línea 3: el tiempo de llegada no puede ser negativo (-2)
  Línea 4: el valor de 'llegada' ('ABC') no es un número entero
  Línea 5: la duración debe ser mayor que cero (-1)
  Línea 6: la duración debe ser mayor que cero (0)
```

## Decisiones y puntos del enunciado a tener presentes

- **Expropiaciones en la sección 18.** La tabla del enunciado indica 2 expropiaciones para P3 con `procesos.csv` y quantum 3, pero la regla 9.2.7 dice que si el quantum se agota con la cola vacía **no hay expropiación**. Eso es lo que ocurre a las 16 (P3 sigue solo en el sistema), así que el programa informa **1**. Todos los demás valores de esa tabla (inicio, fin, espera, retorno, respuesta, promedios, utilización y 5 cambios de contexto) coinciden. Si el profe confirma que la tabla es la correcta, el cambio es contar también los quantums agotados con cola vacía en `Simulador._verificar_quantum`.
- **Valores por defecto.** Se siguieron los del enunciado escrito (política `rr`, quantum 3), que no coinciden con lo comentado en clase 6 donde se dijo que era FIFO por defecto. Un quantum inválido no se reemplaza por 3: se muestra un error y termina, como pide la sección 5.
- **Tamaño del archivo comparativo.** La sección 19 pide "al menos 6 procesos" y los entregables "al menos 8"; `casos/comparativo_8_procesos.csv` tiene 8 y cumple ambos.
- **Salidas.** Siguiendo la sección 16, siempre se llaman `resultados.csv` y `eventos.txt` (la Tarea 1 las guardaba con fecha y hora). La traza de la Tarea 1 ya no se genera porque el enunciado no la pide; el registro de eventos cubre ese papel.
- **Menú.** El menú interactivo de la Tarea 1 se eliminó: el enunciado prohíbe `input()`.

## Organización del código

| Función / clase | Responsabilidad |
|-----------------|-----------------|
| `leer_procesos`, `validar_procesos`, `cargar_procesos` | Lectura del CSV y validación de estructura y reglas de negocio |
| `formatear_errores`, `formatear_errores_parametros` | Texto de los errores de datos y de parámetros |
| `leer_parametros`, `resolver_archivo` | Línea de comandos (`argparse`) y validación de parámetros |
| `Simulador` | Motor de la simulación: CPU, cola, reloj, quantum, cambios de contexto y registro de eventos |
| `simular_fifo`, `simular_round_robin` | Una función por política, sobre el mismo motor |
| `calcular_metricas` | Métricas por proceso y globales; **una sola función para ambas políticas** |
| `ejecutar_politica` | Copia los procesos, simula y calcula métricas |
| `formatear_resumen`, `mostrar_resumen`, `formatear_comparacion` | Salida en pantalla |
| `guardar_resultados`, `guardar_eventos` | Archivos de salida |
| `ejecutar_simple`, `ejecutar_comparacion`, `main` | Flujo del programa |

## Casos de prueba (en `casos/`)

| Caso | Cómo ejecutarlo | Qué comprueba | Resultado |
|------|-----------------|---------------|-----------|
| `un_solo_proceso` | `--archivo un_solo_proceso --quantum 3` | Proceso solo: el quantum se agota con la cola vacía | Sin expropiaciones ni cambios de contexto; fin en 7 |
| `misma_llegada` | `--archivo misma_llegada --quantum 2` | Llegadas simultáneas (orden del archivo) | Espera 6.67 (FIFO: 4.33); 6 cambios de contexto |
| `desempate_quantum` | `--archivo desempate_quantum --quantum 3` | P2 y P3 llegan justo cuando P1 agota su quantum | Entran antes que P1; orden P1, P2, P3, P1, P3; respuesta 0.67 |
| `cpu_ocioso` | `--archivo cpu_ocioso --quantum 2` | Hueco entre P1 (termina en 2) y P2 (llega en 10) | `CPU ocioso` en el log; utilización 46.7 % |
| `quantum_uno` | `--archivo quantum_uno --quantum 1` | Quantum 1 | 5 cambios de contexto (FIFO: 2); respuesta 0.33 (FIFO: 1.67) |
| `ejemplo_enunciado_seccion10` | `--archivo ejemplo_enunciado_seccion10 --quantum 2` | Ejemplo conceptual del enunciado | Espera 4.67, retorno 8.67, respuesta 1.00, 6 cambios de contexto |
| `procesos.csv` con quantum ≥ 8 | `--quantum 8` | Quantum ≥ duración mayor | Idéntico a FIFO |
| `error_valores_invalidos` | `--archivo error_valores_invalidos` | Llegada negativa, texto, duraciones ≤ 0 | 4 errores con su línea |
| `error_ids_vacio_duplicado` | `--archivo error_ids_vacio_duplicado` | Id duplicado y vacío | 2 errores |
| `error_filas_mal_formadas` | `--archivo error_filas_mal_formadas` | Fila incompleta y con columnas de más | 2 errores |
| `error_archivo_vacio`, `error_sin_procesos`, `error_encabezado` | igual | Archivo vacío, solo encabezado, encabezado incorrecto | 1 error cada uno |
