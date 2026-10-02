# MiniOS — Simulador básico de procesos

**Tarea Programada 1** · Sistemas Operativos (IIIC 2026) · LEAD University

MiniOS simula un computador con **un único CPU** y una **cola FIFO** (First In, First Out). Los procesos se leen de un archivo CSV, llegan en distintos instantes, esperan en la cola y se ejecutan **sin interrupciones**: una vez que un proceso toma el CPU, lo conserva hasta terminar. Al final se calculan métricas de espera y retorno.

Solo usa la biblioteca estándar de Python (`csv`, `argparse`, `collections`, `dataclasses`, `pathlib`, `re`, `sys`). No requiere `pip install`.

## Estructura de la carpeta

```
Programada_1/
├── minios.py                  Programa principal
├── procesos.csv               Entrada por defecto (ejemplo del enunciado con 4 procesos)
├── resultados.csv             Salida generada al ejecutar con procesos.csv
├── eventos.txt                Registro de eventos generado al ejecutar con procesos.csv
├── casos_prueba/              Distintos escenarios 
│   ├── caso1_un_proceso/
│   ├── caso2_misma_llegada/
│   ├── caso3_cpu_inactivo/
│   ├── caso4_proceso_largo/
│   └── caso5_errores/
└── enunciado/                 PDFs entregados por el docente
```

Cada carpeta de `casos_prueba/` contiene la entrada (`procesos.csv`) y lo que produce el programa con ella (`resultados.csv` y `eventos.txt`, o `errores.txt` en el caso 5).

## Requisitos

Python 3.10 o superior (usa la sintaxis `int | None`). Desarrollado y probado con Python 3.12.

## Uso

### Inicio rápido

1. Abre una terminal (PowerShell, CMD o Git Bash) y ubícate en esta carpeta:

   ```powershell
   cd "H:\Mi unidad\Universidad\Ulead\Repos\curso_sistemas_operativos\Tareas\Programada_1"
   ```

2. Ejecuta el programa:

   ```powershell
   python minios.py
   ```

Eso es todo. Sin más argumentos, MiniOS lee `procesos.csv` de la carpeta actual, muestra el resumen en pantalla y escribe `resultados.csv` y `eventos.txt` en la misma carpeta (si ya existían, los sobrescribe).

> Si `python` no se reconoce, prueba con `py minios.py` (Windows) o `python3 minios.py` (Linux/macOS).

### Sintaxis completa

```
python minios.py [archivo.csv] [--salida DIRECTORIO] [-v]
```

Todos los argumentos son opcionales y pueden ir en cualquier orden después de `minios.py`.

| Argumento | Para qué sirve | Si se omite |
|-----------|----------------|-------------|
| `archivo.csv` | **Qué leer:** ruta del CSV con los procesos | Usa `procesos.csv` |
| `--salida DIRECTORIO` | **Dónde guardar:** carpeta donde se escriben `resultados.csv` y `eventos.txt`. Se crea si no existe | Usa la carpeta actual |
| `-v`, `--verbose` | **Más detalle en pantalla:** muestra la simulación instante por instante antes del resumen. No cambia los archivos generados | Solo muestra el resumen |

Lo más importante:

- El primer valor sin guion es siempre el **archivo de entrada**. Para guardar en otra carpeta hay que usar `--salida`.
- `--salida` necesita un valor justo después (el nombre de la carpeta). `-v` no lleva valor.

### Ejemplos

| Quiero... | Comando |
|-----------|---------|
| Correr el ejemplo por defecto | `python minios.py` |
| Ver qué pasa en cada unidad de tiempo | `python minios.py -v` |
| Correr mis propios procesos | `python minios.py mis_procesos.csv` |
| Correr un caso de prueba | `python minios.py casos_prueba/caso4_proceso_largo/procesos.csv` |
| Guardar las salidas en otra carpeta | `python minios.py --salida mi_carpeta` |
| Combinar todo | `python minios.py mis_procesos.csv --salida mi_carpeta -v` |

En PowerShell y CMD también funcionan las rutas con `\` (por ejemplo `casos_prueba\caso4_proceso_largo\procesos.csv`).

### Qué verás al ejecutarlo

- **Sin `-v`:** solo el resumen (la tabla y las métricas que se muestran más abajo en *Salidas*), seguido de la línea `Archivos generados: ...` que indica dónde se guardaron los archivos.
- **Con `-v`:** primero la traza de la simulación y después el mismo resumen. Si la ventana es pequeña, la traza puede quedar arriba y fuera de la vista; sube con el scroll.
- **Si los datos tienen errores:** se listan los errores con su número de línea y no se genera ningún archivo. Ver la sección *Validaciones*.

### Errores de uso frecuentes

| Mensaje | Causa | Solución |
|---------|-------|----------|
| `el archivo 'salida' no existe` | Se escribió `python minios.py salida`: el primer valor se interpreta como archivo de entrada | Usar `python minios.py --salida salida` |
| `el archivo 'procesos.csv' no existe` | La terminal no está en esta carpeta | Hacer `cd` a `Programada_1` o indicar la ruta del CSV |
| `unrecognized arguments: ...` | Hay un argumento de más o mal escrito | Revisar la sintaxis de arriba |

### Códigos de salida

El programa termina con código `0` si la simulación se completó y con `1` si hubo errores en los datos o al guardar los archivos.

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

### `resultados.csv`

Una fila por proceso, en el orden del archivo de entrada. Pensado para análisis posterior.

```csv
id,llegada,duracion,inicio,fin,espera,retorno
P1,0,5,0,5,0,5
P2,2,3,5,8,3,6
```

### `eventos.txt`

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

Antes de simular se revisan todos los datos y se reportan **todos** los errores encontrados (con el número de línea), sin intentar repararlos. Si hay alguno, no se simula ni se generan archivos.

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

## Organización del código

| Función | Responsabilidad |
|---------|-----------------|
| `leer_procesos` | Lee el CSV y valida la estructura (columnas, enteros) |
| `validar_procesos` | Valida reglas de negocio (ids, llegada ≥ 0, duración > 0) |
| `mostrar_errores` | Imprime los errores de datos en `stderr` |
| `simular` | Simulación FIFO tick a tick; devuelve eventos y traza |
| `calcular_metricas` | Espera y retorno por proceso y métricas globales |
| `mostrar_resumen` | Tabla y métricas en pantalla |
| `mostrar_traza` | Salida detallada de la opción `-v` |
| `guardar_resultados` | Escribe `resultados.csv` |
| `guardar_eventos` | Escribe `eventos.txt` |
| `main` | Argumentos, orquestación y códigos de salida |

Los procesos se representan con el `dataclass` `Proceso`, que guarda id, llegada, duración, estado, tiempo restante, inicio, fin, espera y retorno.

## Casos de prueba

Los cinco escenarios mínimos del enunciado están en [casos_prueba/](casos_prueba/).

| Caso | Entrada | Qué comprueba | Resultado |
|------|---------|---------------|-----------|
| 1 — Un único proceso | `P1,0,5` | Funcionamiento básico | Espera 0.00, retorno 5.00 |
| 2 — Misma llegada | `P1,0,4` `P2,0,2` `P3,0,6` | Orden FIFO (por orden del archivo) | Espera 3.33, retorno 7.33; orden P1, P2, P3 |
| 3 — Llegadas separadas | `P1,0,2` `P2,5,3` `P3,10,2` | CPU inactivo entre procesos | Espera 0.00, retorno 2.33; utilización 58.33% |
| 4 — Proceso largo primero | `P1,0,15` `P2,1,2` `P3,2,1` `P4,3,2` | Efecto de un proceso largo sobre los que esperan | Espera 11.00, retorno 16.00; P3 y P4 esperan 15 |
| 5 — Archivo con errores | `P2,-2,4` `P3,ABC,3` `P4,5,-1` | Validaciones | 3 errores reportados; no se simula |

En el caso 4 se ve la principal debilidad de FIFO: P3 dura 1 unidad pero espera 15 porque P1 (15 unidades) llegó antes. Es el llamado *efecto convoy*.

Para regenerar las salidas de los casos 1 a 4 desde esta carpeta:

```bash
for d in casos_prueba/caso[1-4]*/; do python minios.py "$d/procesos.csv" --salida "$d"; done
```

## Limitaciones conocidas

- Se ignora el costo del cambio de contexto (simplificación indicada en clase).
- El reloj avanza de a una unidad, por lo que duraciones o llegadas del orden de millones hacen la simulación lenta.
- No hay E/S ni estado *Waiting*: los procesos nunca se interrumpen.
