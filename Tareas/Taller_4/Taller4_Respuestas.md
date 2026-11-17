# Taller 4: Uso de memoria y herramientas de procesamiento (Laboratorio 4)

**Curso:** Sistemas Operativos, LEAD University

**Estudiante:** Daniel Vásquez González

**Entorno:** Ubuntu 26.04.1 en VirtualBox 7.2.20 (máquina virtual "Ubuntu-SO", usuario `daniel`), con 3,3 GiB de RAM, 3,8 GiB de swap (archivo `/swap.img`), 2 CPU y un disco de 25 GB

**Carpeta de trabajo:** `/home/daniel/lab_mem`

---

## Entrega

Todo el trabajo se entrega en este repositorio de GitHub. Los archivos de datos (CSV de 1, 2 y 4 GB) **no** se incluyen por su tamaño; se regeneran con `generar_dataset.py` y la semilla por defecto.

**Scripts (los dos del profesor y los dos propios, con mi firma):** [scripts](https://github.com/DannyV1992/curso_sistemas_operativos/tree/main/Tareas/Taller_4/scripts)

**Resultados del monitoreo (una carpeta por corrida):** [scripts/resultados](https://github.com/DannyV1992/curso_sistemas_operativos/tree/main/Tareas/Taller_4/scripts/resultados)

**Capturas de pantalla:** [Screenshots](https://github.com/DannyV1992/curso_sistemas_operativos/tree/main/Tareas/Taller_4/Screenshots)

### Lista de verificación

- [x] Archivos de datos de 1, 2 y 4 GB (cada uno el doble del anterior) y uno de 200 MB para pruebas.
- [x] Monitoreo con `vmstat`, `free`, `top` y presión de memoria, guardado en archivos.
- [x] Explicación de qué mide cada comando.
- [x] Corridas en modo `chunks` y `full` con 1 GB.
- [x] Corridas con 2 GB (`chunks` y `full`) y con 4 GB (`chunks`). El modo `full` con 4 GB no se ejecutó porque ya con 2 GB el sistema mata el proceso.
- [ ] Serie de corridas repetidas, alternando `full` y `chunks`.
- [ ] Procesamiento de los resultados y gráficas.
- [ ] Interpretación final de `full` frente a `chunks`.
- [x] Pregunta extra: monitoreo en Windows.

---

## La pregunta del laboratorio

**¿Qué sucede cuando se intenta analizar un archivo que supera la RAM disponible, y cómo se resuelve sin agregar memoria física?**

> **PENDIENTE:** la respuesta final va en la sección de conclusiones, cuando estén las corridas de 2 y 4 GB y la serie repetida.

---

## Material usado y cambios hechos

| Archivo | Origen | Qué hace |
|---|---|---|
| `generar_dataset.py` | Profesor (modificado, ver abajo) | Crea un CSV de ventas sintéticas escribiendo por bloques de unos 4 MiB, sin cargarlo en RAM |
| `analizar_datos.py` | Profesor | Calcula el importe total por región y categoría, en modo `full` (todo en memoria) o `chunks` (por bloques) |
| `monitorear.sh` | Propio | Registra `vmstat`, `free`, `top` y la presión de memoria mientras corre un análisis |
| `correr_corrida.sh` | Propio | Ejecuta una corrida completa: monitoreo, análisis y cierre |

**Cambio al generador.** `generar_dataset.py` solo aceptaba `--size-gb` entre 20 y 50, pero la máquina virtual tiene **11 GB libres** de disco y un archivo de 20 GB no cabe. Se bajó el mínimo a 1 GB (líneas 58, 59, 67 y 68 del script) y el resto del programa quedó igual. Con esto se pueden generar archivos de 1, 2 y 4 GB, que ocupan 7 GB en total.

**Cómo funciona `correr_corrida.sh`:**

1. Crea la carpeta `resultados/ARCHIVO_MODO_FECHA/`.
2. Vacía la caché de archivos del sistema (`sync` y `drop_caches`), para que todas las corridas partan en condiciones parecidas.
3. Lanza `monitorear.sh` en segundo plano, con una muestra por segundo.
4. Espera **10 segundos** antes de lanzar el análisis, como recomienda el enunciado, para ver cómo cambia la situación.
5. Ejecuta `analizar_datos.py` con los parámetros recibidos y guarda su salida en `analisis.txt`.
6. Anota en `marcas.txt` la hora de inicio, la de fin y el código de salida (un **137** significa que el sistema mató el proceso por falta de memoria).
7. Sigue monitoreando 10 segundos más y detiene el monitoreo.

**Archivos que genera cada corrida:**

| Archivo | Comando | Contenido |
|---|---|---|
| `vmstat.txt` | `vmstat -w -t 1` | Una línea por segundo, con la hora al final |
| `free.txt` | `free -m` | RAM y swap, en MiB para poder procesarlos, cada segundo |
| `psi.txt` | `cat /proc/pressure/memory` | Presión de memoria, cada segundo |
| `top.txt` | `top -b -n 1 -o %MEM` | Los procesos que más memoria usan, cada segundo |
| `analisis.txt` | `analizar_datos.py` | Salida del análisis, con duración y RSS máximo |
| `marcas.txt` | | Inicio, fin y código de salida |

El enunciado indica `free -h`; se usó `free -m` porque muestra los mismos datos en MiB exactos y no con redondeos como `1.3Gi`, lo que facilita procesarlos.

---

## Paso 0: Recursos de la máquina

```bash
ls -lh ~/lab_mem/*.csv
df -h /
free -h
swapon --show
```

**Respuesta:** La máquina tiene **3,3 GiB de RAM** (2,1 GiB disponibles con el escritorio abierto), **3,8 GiB de swap** (casi sin uso: 632 KiB) y 2 CPU. El disco es de 25 GB; antes de generar los datos había 11 GB libres y después de generarlos quedan **3,3 GB (86 % usado)**. Estas cifras definen el experimento: un archivo de 2 o 4 GB ya supera la RAM disponible, y la RAM más el swap suman unos 7 GiB.

> `ls -lh` muestra los tamaños en MiB y GiB (`954M`, `1.9G`, `3.8G`), mientras que el generador usa GB decimales (1,000 GB = 999 999 988 bytes).

![Archivos y recursos](Screenshots/05_archivos_y_recursos.png)

---

## Paso 1: Qué mide cada comando de monitoreo

Los cuatro comandos se ejecutaron primero a mano, con la máquina en reposo, para conocer sus salidas:

```bash
vmstat 1 5
free -h
top -b -n 1 | head -n 12
cat /proc/pressure/memory
```

![Los cuatro comandos](Screenshots/03_comandos_monitoreo.png)

### `vmstat`: memoria virtual

Muestra una línea por intervalo con el estado del sistema. La primera línea es el **promedio desde el arranque**, no una medición del momento. Columnas principales:

| Grupo | Columna | Significado |
|---|---|---|
| `procs` | `r` | Procesos listos para ejecutar o ejecutándose |
| | `b` | Procesos bloqueados esperando entrada/salida (en la corrida, suben cuando hay swapping) |
| `memory` (KiB) | `swpd` | Memoria virtual en uso, es decir, cuánto está en el swap |
| | `free` | Memoria libre |
| | `buff`, `cache` | Memoria usada como caché de archivos (se devuelve si hace falta) |
| `swap` (KiB/s) | `si` | Memoria que **entra** desde el swap al disco → RAM |
| | `so` | Memoria que **sale** de la RAM al swap |
| `io` (bloques/s) | `bi`, `bo` | Bloques leídos y escritos en los dispositivos |
| `system` | `in`, `cs` | Interrupciones y cambios de contexto por segundo |
| `cpu` (%) | `us`, `sy` | Tiempo en modo usuario y en modo kernel |
| | `id` | Tiempo ocioso |
| | `wa` | Tiempo esperando a que termine una operación de disco |

En la captura, en reposo: `swpd` 632 KiB, `si` y `so` en 0 y la CPU casi siempre ociosa (`id` por encima del 90 %).

### `free`: RAM y swap usados

Resume la memoria física y el swap. La columna más útil es **`available`**: cuánta memoria se podría dar a un programa nuevo sin recurrir al swap, contando la caché que se puede liberar. En reposo: 3,3 GiB en total, 1,3 GiB usados, 2,1 GiB disponibles y 632 KiB de swap usado.

### `top`: procesos

Lista los procesos ordenados por uso de recursos y resume el estado general en el encabezado (tareas, CPU, memoria y swap). Para este taller importan las columnas por proceso:

| Columna | Significado |
|---|---|
| `VIRT` | Memoria virtual total reservada por el proceso |
| `RES` | Memoria física (RAM) que el proceso tiene realmente cargada ahora |
| `SHR` | Parte de `RES` que es compartida con otros procesos |
| `%CPU`, `%MEM` | Porcentaje de CPU y de RAM que usa |

Con `top` se **correlaciona** el comportamiento de la memoria con el proceso responsable (en reposo, el que más memoria usa es `gnome-shell`).

### Presión de memoria: `/proc/pressure/memory` (PSI)

PSI (*Pressure Stall Information*) mide cuánto tiempo pierden los procesos esperando por memoria. Tiene dos líneas:

| Línea | Significado |
|---|---|
| `some` | Porcentaje del tiempo en que **al menos un** proceso esperó por memoria |
| `full` | Porcentaje del tiempo en que **todos** los procesos útiles esperaron a la vez (la máquina no avanza) |

Cada línea trae `avg10`, `avg60` y `avg300` (promedio de los últimos 10, 60 y 300 segundos) y `total` (microsegundos acumulados). En reposo todos los promedios son `0.00`. Es el indicador más directo de que el sistema está sufriendo por falta de memoria, aun antes de que mate procesos.

---

## Paso 2: Generación de los datos

```bash
python3 generar_dataset.py --size-gb 1 --output ~/lab_mem/ventas_1gb.csv
python3 generar_dataset.py --size-gb 2 --output ~/lab_mem/ventas_2gb.csv
python3 generar_dataset.py --size-gb 4 --output ~/lab_mem/ventas_4gb.csv
```

**Respuesta:** Se generaron tres archivos, cada uno del doble del anterior, en 1,9 s, 3,8 s y 9,1 s. Además se creó uno de 200 MB (`--demo-mb 200`) para probar el monitoreo. El generador escribe por bloques de unos 4 MiB, así que no necesita RAM proporcional al archivo, y comprueba el espacio libre antes de empezar.

| Archivo | Tamaño exacto | Filas procesadas |
|---|---|---|
| `ventas_demo.csv` | 199 999 996 bytes | 4 575 207 |
| `ventas_1gb.csv` | 999 999 988 bytes | 22 878 219 |
| `ventas_2gb.csv` | 1 999 999 974 bytes | 45 754 872 |
| `ventas_4gb.csv` | 3 999 999 962 bytes | 91 511 526 |

![Generación de los archivos](Screenshots/04_generacion.png)

---

## Paso 3: Prueba del monitoreo con el archivo chico

```bash
./correr_corrida.sh ~/lab_mem/ventas_demo.csv chunks
ls resultados/*/
cat resultados/*/marcas.txt
head -n 4 resultados/*/vmstat.txt
```

**Respuesta:** La corrida de prueba procesó 4 575 207 filas en 2,61 s con un RSS máximo de 111,3 MiB. La carpeta de resultados tiene los seis archivos esperados (`analisis.txt`, `free.txt`, `marcas.txt`, `psi.txt`, `top.txt` y `vmstat.txt`), `marcas.txt` registra `codigo_salida 0` y `vmstat.txt` guarda la hora de cada muestra (columna `CST`), que servirá para alinear las cuatro fuentes entre sí.

![Corrida de prueba](Screenshots/01_prueba_corrida.png)

![Archivos de la corrida de prueba](Screenshots/02_prueba_resultados.png)

---

## Paso 4: Corridas exploratorias

### 4.1 Archivo de 1 GB

```bash
./correr_corrida.sh ~/lab_mem/ventas_1gb.csv chunks
./correr_corrida.sh ~/lab_mem/ventas_1gb.csv full --force
```

El modo `full` se niega a ejecutarse sin `--force`, porque el script estima que un CSV mayor al 35 % de la memoria disponible puede agotar la RAM. Aquí se forzó a propósito en una máquina virtual aislada.

| Modo | Filas | Duración | RSS máximo |
|---|---|---|---|
| `chunks` | 22 878 219 | 12,23 s | 111,2 MiB |
| `full` (1.ª corrida) | 22 878 219 | 62,46 s | 2653,7 MiB |
| `full` (2.ª corrida) | 22 878 219 | 45,47 s | 2548,0 MiB |

**Respuesta:** Los tres resultados numéricos son idénticos (el mismo Top 10 de región y categoría), pero el uso de recursos es muy distinto:

- `full` usó unas **23 veces más memoria** que `chunks` (unos 2,6 GiB frente a 111 MiB) y fue entre 3,7 y 5,1 veces más lento.
- El script estimó que el DataFrame completo ocupa **4252,5 MiB**, unas 4,5 veces el tamaño del CSV (954 MiB). Aun así el RSS máximo fue de 2,6 GiB: el resto **no cabía en la RAM** y el sistema lo mandó al swap. Con el escritorio ocupando 1,3 GiB, a Python le quedaban unos 2 GiB de RAM física.
- Las dos corridas de `full` no dieron el mismo tiempo (62,46 s y 45,47 s). Entre una corrida y otra queda swap ocupado de la anterior, como se ve en la segunda corrida: `swpd` ya valía 494 676 KiB antes de empezar. Por eso el laboratorio pide repetir las corridas.

![chunks con 1 GB](Screenshots/06_chunks_1gb.png)

![full con 1 GB](Screenshots/07_full_1gb.png)

**Las dos terminales en vivo.** A la izquierda corre `correr_corrida.sh` y a la derecha `tail -f` sobre el `vmstat.txt` de esa corrida:

```bash
tail -f "$(ls -dt ~/lab_mem/scripts/resultados/*/ | head -1)vmstat.txt"
```

![Dos terminales durante full](Screenshots/08_dos_terminales_full.png)

Lo que se ve en el `vmstat` de la captura a medida que avanza `full`:

- **Antes de cargar** (14:11:44 a 14:11:55): `swpd` estable en unos 483 MiB (swap que dejó la corrida anterior), `free` en 2,2 GiB y `cache` de unos 0,45 GiB. La máquina está tranquila.
- **Durante la carga** (14:11:56 a 14:12:04): `free` se desploma de 1,8 GiB a unos 100 MiB y `cache` **crece** de 0,63 a 1,4 GiB, porque el archivo CSV se lee a través de la caché de archivos.
- **Cuando la RAM se agota** (desde 14:12:05): `cache` cae a unos 0,3 GiB, o sea que el sistema **descarta la caché** para hacer sitio. `swpd` empieza a subir (de 0,5 GiB a más de 1,4 GiB) y aparecen `si` y `so` (por ejemplo, a las 14:12:21: `so` = 85 704 KiB/s, unos 84 MiB/s).
- **Efecto en la CPU** en ese momento: `sy` (modo kernel) = 74 %, `wa` (espera de disco) = 16 % e `id` = 0 %. La CPU se gasta administrando la memoria y esperando al disco, no calculando. Es el comportamiento típico de la **hiperpaginación** (*thrashing*), aunque aquí es moderado.
- Los procesos bloqueados (`b`) suben a 1 – 3 mientras duran las operaciones con el swap.

### 4.2 Archivo de 2 GB

```bash
./correr_corrida.sh ~/lab_mem/ventas_2gb.csv chunks
./correr_corrida.sh ~/lab_mem/ventas_2gb.csv full --force
```

| Modo | Filas | Duración | RSS máximo | Resultado |
|---|---|---|---|---|
| `chunks` | 45 754 872 | 24,62 s | 111,1 MiB | Terminó (código 0) |
| `full` | no terminó | unos 10 min 24 s hasta la muerte | 2,6 GiB al morir | **El sistema mató el proceso** |

![chunks con 2 GB](Screenshots/09_chunks_2gb.png)

**`chunks` con 2 GB** terminó sin problemas y con el mismo RSS que con 1 GB y que con 200 MB.

**`full` con 2 GB no terminó.** El script alcanzó a cargar el archivo (`DataFrame completo antes del filtro: 8504.7 MiB`), pero esa cifra ya es mayor que la RAM más el swap de la máquina (3,3 + 3,8 = 7,1 GiB), y la consulta todavía necesita copias adicionales. La pantalla se quedó sin respuesta varios minutos y al final el script apareció como `Terminated`:

![full con 2 GB](Screenshots/10_full_2gb.png)

Casi al mismo tiempo, GNOME mostró el aviso *"Device memory is nearly full. An application was using a lot of memory and was forced to stop"* y la terminal indicó `Process Exited from Signal 9` (SIGKILL, una terminación forzada que el proceso no puede ignorar). El `pgrep` posterior confirma que no quedó ningún Python ni monitoreo huérfano (el único `python3` es `wsdd`, un servicio del sistema):

![Aviso del sistema](Screenshots/10a_full_2gb_notificacion.png)

**Quién lo mató.** El registro del sistema (`journalctl`) lo dice con precisión:

```bash
sudo journalctl -b --no-pager | grep -i -E "oomd|memory pressure|out of memory|killed" | tail -n 10
```

```
14:29:21 kernel: systemd-oomd invoked oom-killer: ...
14:29:21 kernel: Out of memory: Killed process 12448 (python3) total-vm:6255856kB, anon-rss:2751244kB ...
```

Fue el **OOM killer del kernel**. El `12448` es exactamente el PID que imprimió el script al arrancar (`PID=12448`), así que murió el proceso de análisis. Cuando la memoria física y el swap se terminaron, el kernel eligió como víctima al proceso que más memoria ocupaba (el RSS de Python era de unos 2,6 GiB, `anon-rss`) y lo terminó. Como el script y el monitoreo corrían en la misma terminal, también se perdieron con ella, por eso la corrida no llegó a escribir `fin_analisis` ni `codigo_salida`.

![Registro del sistema](Screenshots/13_oomd_journal.png)

**Qué muestran los datos guardados** antes de la muerte (`marcas.txt` solo tiene `inicio_analisis 14:18:57`; el kernel mató el proceso a las 14:29:21, es decir, la máquina estuvo **más de 10 minutos** agonizando):

```bash
D="$(ls -dt ~/lab_mem/scripts/resultados/*/ | head -1)"
ls "$D"; cat "$D/marcas.txt"; tail -n 5 "$D/vmstat.txt"; tail -n 8 "$D/psi.txt"
```

![Datos guardados de la corrida](Screenshots/10b_full_2gb_resultados.png)

| Indicador | Valor al final de la corrida | En reposo |
|---|---|---|
| `swpd` (swap usado) | 4 003 7xx KiB, unos 3,8 GiB: **el swap estaba completamente lleno** | 632 KiB |
| `free` | unos 90 MiB | 1,5 GiB |
| `cache` | unos 54 MiB: el sistema descartó casi toda la caché de archivos | 0,8 GiB |
| `wa` (espera de disco) | 88 % a 92 % | 0 % |
| `us` (CPU en modo usuario) | 0 % | |
| `b` (procesos bloqueados) | hasta **31** | 0 |
| PSI `some` (avg10 / avg60) | 12 – 23 % / 20 – 23 % | 0,00 |
| PSI `full` (avg10 / avg60) | 11 – 17 % / 16 – 19 % | 0,00 |

La CPU estaba casi toda en **espera de disco**: no calculaba, solo movía páginas entre la RAM y el swap. Es la hiperpaginación (*thrashing*) en su forma extrema: cuando el swap también se llena, el sistema ya no puede liberar espacio y solo le queda matar un proceso.

### 4.3 Archivo de 4 GB

```bash
./correr_corrida.sh ~/lab_mem/ventas_4gb.csv chunks
```

Solo se ejecutó el modo `chunks`. El modo `full` no se probó: con 2 GB ya muere, así que con 4 GB solo moriría antes y se arriesgaría a congelar la máquina virtual sin aportar un dato nuevo.

| Modo | Filas | Duración | RSS máximo | Resultado |
|---|---|---|---|---|
| `chunks` | 91 511 526 | 59,14 s | 111,1 MiB | Terminó (código 0) |

![chunks con 4 GB](Screenshots/11_chunks_4gb.png)

**Respuesta:** `chunks` procesó 91,5 millones de filas con los mismos 111 MiB de memoria. Un archivo de **4 GB** (más grande que toda la RAM de la máquina) se analiza sin problema, y el tiempo crece de forma casi lineal con el tamaño.

---

## Paso 5: Serie de corridas repetidas

> **PENDIENTE:** al menos 4 corridas por modo (de preferencia 6), con el mismo archivo y alternando `full` y `chunks`, con la tabla resumen (captura 14).

---

## Paso 6: Procesamiento de los resultados

> **PENDIENTE:** script de análisis y gráficas de memoria virtual (`swpd`), swapping (`si` y `so`), presión de memoria (PSI) y correlación con los procesos (`RES` del proceso de Python en `top`), una gráfica por corrida o por modo.

---

## Paso 7: Interpretación

### Diferencia entre `full` y `chunks`

Con lo observado hasta ahora (hasta 4 GB):

| | `full` | `chunks` |
|---|---|---|
| Qué hace | Lee todo el CSV a un DataFrame y después consulta | Lee 100 000 filas, las consulta, descarta ese bloque y acumula el resultado parcial |
| Memoria máxima | Crece con el tamaño del archivo (4,5 veces el CSV en el DataFrame) | **Constante**: unos 111 MiB con 200 MB, 1, 2 y 4 GB |
| Tiempo | Mucho mayor cuando la memoria no alcanza (el swap pone al disco en medio) | Casi lineal con el archivo: 2,6 s, 12,2 s, 24,6 s y 59,1 s para 0,2, 1, 2 y 4 GB |
| Swap y presión | Usa swap, descarta la caché y, si todo se llena, el sistema mata el proceso | No usa swap |
| Límite | El DataFrame debe caber en RAM + swap (con 1 GB sí, con 2 GB no) | Ninguno práctico: procesó 4 GB en una máquina de 3,3 GiB |
| Resultado | El mismo cuando termina | El mismo |

Por qué ocurre:

- En `full` el DataFrame tiene que existir completo en memoria antes de la consulta, así que necesita varias veces el tamaño del CSV (cada fila se convierte en objetos de Python, más las copias que crean el filtro y la columna calculada). Cuando eso supera la RAM, el sistema **envía al swap** páginas de memoria anónima (las del DataFrame, que no tienen archivo de respaldo) y por eso aparecen `swpd`, `si` y `so`.
- En `chunks` la memoria depende del **tamaño del bloque** (100 000 filas) y no del archivo; cada bloque se libera al terminar. Por eso el RSS no cambia con el tamaño del archivo.
- `chunks` funciona aquí porque la consulta es una **suma por grupo**, que se puede acumular parcialmente (`acumulado.add(parcial)`). No todas las consultas se pueden partir así: una mediana exacta, un orden global o una unión entre tablas grandes necesitan una estrategia distinta.

### Qué pasa cuando el archivo supera la memoria

Con 1 GB, `full` todavía termina porque el DataFrame (4,2 GiB estimados) cabe en RAM + swap (7,1 GiB), pero a un costo alto: swapping, caché descartada, CPU en modo kernel y espera de disco, y 4 a 5 veces más tiempo. Con 2 GB, el DataFrame estimado (8,5 GiB) ya no cabe: el swap se llena, la máquina pasa más de 10 minutos casi sin avanzar (88 % a 92 % de espera de disco) y el OOM killer del kernel mata el proceso sin entregar ningún resultado. Es una falla total, no una degradación gradual.

> **PENDIENTE:** completar con las gráficas y con la serie repetida de 1 GB.

---

## Pregunta extra: ¿se puede hacer en Windows tradicional?

**Sí, con dos salvedades.** La parte de monitoreo existe en Windows, pero hay que adaptar el script de análisis y las herramientas son otras.

**1. El script del profesor no corre tal cual en Windows.** `analizar_datos.py` importa el módulo `resource`, que solo existe en Linux y macOS, y la estimación de memoria usa `/proc/meminfo`. Habría que cambiar esa parte para medir el pico de memoria con otra librería, por ejemplo `psutil` (`psutil.Process().memory_info()`, que da el *working set*, la memoria física en uso). El resto del script, que es pandas puro, funciona igual.

**2. El monitoreo se hace con los contadores de rendimiento de Windows**, que equivalen a los comandos de Linux:

| Qué se observa | Linux | Windows (contador de rendimiento) |
|---|---|---|
| Memoria virtual y swap | `vmstat`, `free` | `\Memory\Available MBytes`, `\Paging File(_Total)\% Usage` |
| Swapping (entrada y salida de páginas) | columnas `si` y `so` | `\Memory\Pages Input/sec` y `\Memory\Pages Output/sec` |
| Procesos | `top` | `\Process(python)\Working Set` y `\Process(python)\Page Faults/sec` |
| Presión de memoria | `/proc/pressure/memory` | No existe un PSI exacto; lo más cercano son los *hard page faults* (`Pages Input/sec`) y la poca memoria disponible |

La herramienta de línea de comandos es `typeperf`, que ya viene con Windows y guarda las muestras en un archivo CSV, listo para procesar:

```powershell
typeperf "\Memory\Available MBytes" "\Memory\Pages Input/sec" "\Memory\Pages Output/sec" "\Paging File(_Total)\% Usage" "\Process(python)\Working Set" -si 1 -f CSV -o metricas_windows.csv
```

`-si 1` toma una muestra por segundo, igual que `vmstat 1`. También sirve el monitor de rendimiento (`perfmon`) con un *conjunto de recopiladores de datos*, o `Get-Counter ... | Export-Counter` en PowerShell. Otra opción es usar WSL2, que es un Linux completo y permite correr los scripts sin cambios, aunque WSL limita su propia memoria (archivo `.wslconfig`) y no ve la memoria de Windows de la misma forma.

> **Nota:** esta respuesta es de investigación; los comandos de Windows no se ejecutaron en esta entrega.

---

## Problemas encontrados y cómo se resolvieron

El enunciado pide identificar las otras razones por las que los procesos pueden fallar. Lo que apareció:

| Problema | Causa | Solución |
|---|---|---|
| El generador rechaza `--size-gb 1` | El script exige entre 20 y 50 GB y el disco solo tenía 11 GB libres | Se bajó el mínimo a 1 GB (ver "Material usado") |
| `analizar_datos.py --mode full` se detiene sin ejecutar | Protección del script: el CSV supera el 35 % de la memoria disponible | Se usa `--force` en la máquina virtual aislada |
| El enunciado dice `--chuck-size` | Error de tipeo del PDF; el parámetro real es `--chunk-size` | Se usa `--chunk-size` (por defecto ya vale 100 000) |
| `full` con 2 GB termina sin resultado | El DataFrame (8,5 GiB) no cabe en RAM + swap (7,1 GiB) y el OOM killer del kernel mata el proceso, junto con el script y el monitoreo de esa terminal | Es el comportamiento esperado: se usa `chunks`. Se documenta la corrida en el Paso 4.2 |
| El disco quedó al 86 % | Los tres archivos ocupan 7 GB de los 11 libres | Se evita generar más archivos y se borran los CSV al terminar |
| Las corridas no parten de cero | El swap usado por una corrida queda ocupado en la siguiente (`swpd` de unos 483 MiB antes de la segunda corrida de `full`) | Se repiten las corridas y se vacía la caché de archivos antes de cada una |
| El script no corre en Windows | Importa `resource` y lee `/proc` | Ver la pregunta extra |

---

## Conclusiones

> **PENDIENTE:** respuesta final a la pregunta del laboratorio, con los resultados de 2 y 4 GB y de la serie repetida.
