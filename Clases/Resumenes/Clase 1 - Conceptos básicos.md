# Clase 1 — Conceptos básicos de Sistemas Operativos

- **Curso:** IIIC2026 - Sistemas Operativos, LEAD University
- **Docente:** Mario Miguel Agüero Obando
- **Fecha:** 7 de septiembre de 2026
- **PDF fuente:** ninguno aplicable — el archivo `Clase 1 - Conceptos básicos.pdf` es en realidad el enunciado del Taller 1 (duplicado de `Tareas/Taller_1/Taller-1.pdf`), no las diapositivas de la clase. Este resumen se basa **únicamente en la transcripción** (`Notas.txt`).
- **Cobertura:** completa según la transcripción disponible (desde la presentación del curso hasta el cierre de la sesión).

Primera sesión del curso. Se presenta el programa y la evaluación, y se desarrolla el primer bloque de contenido: qué es un sistema operativo (SO), qué papeles cumple, y cómo el modelo de Von Neumann y el ciclo de ejecución explican por qué las computadoras funcionan como lo hacen.

## 1. ¿Qué es un sistema operativo?

Un SO es **software** que administra los recursos de hardware de una **máquina** para sus usuarios y para los demás programas que corren en ella. Se dice "máquina" y no "computador" porque el concepto se extiende a cualquier dispositivo con recursos que necesite administración: microondas, reproductores de DVD, decodificadores de TV, automóviles, teléfonos. Cualquier dispositivo con funciones y recursos que requiera un programa administrador tiene, en este sentido amplio, un sistema operativo.

Este curso no se enfoca en construir sistemas operativos, sino en entender la **administración de recursos** que hacen posible, como ciencia de datos / devops, comprender por qué ciertas restricciones y comportamientos existen tal como existen.

## 2. Los tres papeles del sistema operativo

**Árbitro.** El SO separa y aísla los recursos entre aplicaciones: lo que pasa en una aplicación no debe afectar a las demás (salvo un crash grave del sistema). Permite, por ejemplo, hacer copy-paste entre aplicaciones sin que el pegado termine en la ventana equivocada, o que al oprimir una tecla el efecto quede confinado a la aplicación activa y no a las demás que comparten el mismo monitor.

> Antes de esto, usar la computadora era mucho más tedioso: en entornos como DOS solo se podía tener una aplicación abierta a la vez, y no existía copiar/pegar entre programas.

La tecnología que introdujo el copy-paste entre aplicaciones fue **OLE** (*Object Linking and Embedding*), lanzada con Windows 3.1 (±1992-93) — la primera versión de Windows que permitió abrir más de una aplicación a la vez.

**Ilusionista.** El SO hace creer que existen recursos que en realidad no existen físicamente:
- **Virtualización:** una máquina virtual parece "otra computadora" dentro de la propia, pero es una ilusión de software.
- **Cola de impresión:** no es una impresora física adicional, sino un espacio de memoria que el SO ofrece para encolar documentos sin bloquear la máquina mientras se imprime.
- **Particiones de disco:** un solo disco físico puede hacerse ver como varios discos independientes.
- **Memoria virtual:** hace creer que hay más memoria RAM disponible de la que realmente existe, usando disco para descargar contenido que no está activo en RAM.

**Estandarizador.** El SO unifica comportamientos (botones de ventana, drivers de impresora, manejo de dispositivos) para que programadores y usuarios no tengan que reimplementarlos en cada programa. Antes de esta estandarización, cada aplicación debía programar su propio soporte para cada impresora (de ahí que programas como WordPerfect compitieran por tener el catálogo de impresoras soportadas más completo).

Dos computadoras con hardware idéntico pero sistemas operativos distintos (p. ej. Windows y Linux) se perciben como máquinas completamente distintas, porque el SO es el que define la experiencia visible; y a la inversa, hardware muy distinto bajo el mismo SO puede parecer "la misma computadora", solo que una es más rápida. Los programas de un SO no corren nativamente en otro (ej. Windows en Linux) salvo que exista un emulador/intermediario (ej. *Wine*).

## 3. El modelo de Von Neumann

Es el esquema básico que describe toda computadora desde las primeras máquinas, y la base para entender cualquier arquitectura posterior. Define tres componentes:

- **CPU:** ejecuta instrucciones y procesos.
- **Memoria principal:** almacena el programa, que se ejecuta **secuencialmente** (instrucción por instrucción).
- **Sistemas de entrada/salida:** permiten la interacción con el usuario (originalmente teletipos — *TTY*, de ahí el nombre de las salidas estándar en los sistemas operativos actuales — y más tarde monitores).

En las primeras computadoras, la CPU tenía que encargarse directamente de **todo**: leer del teclado, escribir a la impresora, administrar la memoria. Esto consumía una fracción importante del tiempo de procesamiento y era una de las razones de la lentitud de esas máquinas.

Un programa cargado en memoria principal se organiza en al menos dos segmentos:
- **Segmento de código:** las instrucciones.
- **Segmento de datos:** variables y objetos.

El sistema operativo puede además asignar espacio adicional para datos (comúnmente llamado el **heap**).

## 4. El ciclo de ejecución (fetch–decode–execute)

Es la secuencia que la CPU repite para cada instrucción, de forma ininterrumpida mientras el programa corre:

1. **Fetch:** se trae de memoria la siguiente instrucción, cuya dirección está en el **program counter** (un registro de la CPU).
2. **Decode:** la unidad de control decodifica qué hay que hacer.
3. **Execute:** la unidad aritmético-lógica (ALU) realiza los cálculos necesarios.
4. **Memory access:** se traen de memoria los datos que la instrucción requiere.
5. **Write-back / salida:** se actualiza la memoria o se envía la salida a los dispositivos correspondientes, y se avanza el program counter a la siguiente instrucción.

Según el autor, este ciclo se describe con 4 a 7 pasos, pero 5 es el número más estándar. La CPU repite este ciclo **siempre**, para cada instrucción de cada programa — es, literalmente, lo único que sabe hacer.

Dentro de la CPU hay tres componentes clave:
- **Registros:** la memoria más básica y rápida de la CPU (p. ej. 16 posiciones de 64 bits en procesadores modernos de 64 bits).
- **Unidad aritmético-lógica (ALU):** ejecuta los cálculos.
- **Unidad de control:** decodifica la instrucción y coordina al resto, como un director de orquesta.

## 5. El reloj de la CPU y la velocidad de procesamiento

El reloj de la computadora (medido en Hz/MHz/GHz) no es un reloj de hora: es un generador de pulsos (0 y 1) a una frecuencia fija. **1 Hz = 1 ciclo por segundo.** Cada ciclo del reloj corresponde a un paso elemental de procesamiento.

**Ejemplo resuelto — del 8086 a un CPU moderno:**

Suponiendo que una instrucción típica requiere, en promedio: 8 ciclos de fetch, 11 de decodificación, 30 de operaciones en la ALU, 20 de acceso a memoria y 14 de escritura de salida:

$$8 + 11 + 30 + 20 + 14 = 83 \text{ ciclos por instrucción}$$

Con el 8086 (procesador original de las PC) corriendo a ~5 MHz (5.000.000 Hz):

$$\frac{5.000.000}{83} \approx 60.241 \text{ instrucciones/segundo}$$

Con un CPU moderno (p. ej. un i7 a ~4.5 GHz = 4.500.000.000 Hz), suponiendo la misma duración por instrucción:

$$\frac{4.500.000.000}{83} \approx 54.216.900 \text{ instrucciones/segundo}$$

Esto representa un incremento de aproximadamente **900 veces** más instrucciones por segundo que hace 50 años. Dos factores explican esta mejora:
1. El aumento bruto de la frecuencia del reloj.
2. Que la CPU moderna **ya no administra directamente** la memoria ni la entrada/salida (ver sección 6), por lo que una proporción mayor de sus ciclos se dedica a instrucciones del programa real, en vez de a tareas de administración de dispositivos.

## 6. Descarga de tareas de la CPU: buses y controladores

Las primeras CPU manejaban directamente memoria y dispositivos de entrada/salida, lo cual era muy ineficiente. Con el tiempo, estas tareas se delegaron a componentes especializados:
- **Bus de direcciones:** gestionado por un controlador de direcciones de memoria.
- **Bus de datos:** comunica la CPU con la memoria para traer/enviar datos.
- **Controladores específicos de entrada/salida:** manejan cada dispositivo (teclado, mouse, impresora) por separado.
- **Bus de video dedicado:** liberó a la CPU de dibujar directamente lo que se muestra en pantalla.

El costo de este cambio fue una CPU algo más compleja, pero el beneficio neto fue mayor: se cambió la complejidad de "administrar cada dispositivo en detalle" por la complejidad de "coordinar la comunicación entre componentes", lo cual escaló mucho mejor.

**Memoria caché:** por la misma razón de reducir la distancia (y por tanto la latencia) hasta la memoria principal, los procesadores incorporan caché interno, con una división equivalente a la de los programas: **caché de datos** y **caché de código/instrucciones**. Físicamente, la memoria RAM se coloca siempre lo más cerca posible del chip de la CPU (a menudo a menos de 5 cm) para minimizar la latencia de transporte de datos, que a escala de circuitería representa una distancia enorme.

## 7. Multiprogramación y múltiples núcleos (cores)

El ciclo de ejecución de una CPU **solo puede ejecutar una instrucción a la vez**. Sin embargo, da la impresión de que varios programas corren "al mismo tiempo" (Word, el navegador, Zoom, etc.) gracias a dos mecanismos distintos:

- **Multiprogramación:** una técnica que *simula* la ejecución simultánea alternando rápidamente entre programas en una sola CPU — es una ilusión, no paralelismo real.
- **Múltiples cores:** cuando el chip tiene varios núcleos, cada uno es efectivamente una CPU independiente, por lo que sí es posible ejecutar varios programas verdaderamente en paralelo, uno por core. Aquí la "ilusión" de simultaneidad es real.

Con múltiples cores la capacidad de cómputo se multiplica: un chip con 8 cores a 4.5 GHz podría manejar en teoría del orden de $8 \times 54.216.900 \approx 43.200.000$ instrucciones por segundo. Pero esto incrementa la complejidad: sigue habiendo un solo bus de datos a la RAM, un solo bus de video, etc., que ahora deben coordinarse entre varios CPU para evitar que programas se interfieran o que datos de un proceso se filtren a otro sin que se desee.

## 8. Interrupciones

Las interrupciones son el mecanismo con el que el SO reacciona a eventos externos: una tecla presionada, el movimiento del mouse, conectar o desconectar un USB. Cuando ocurre una interrupción, la CPU **se detiene**, la atiende (identificando además a qué programa pertenece el evento, para reflejarlo en la ventana activa correcta) y luego retoma la ejecución normal — todo esto en una fracción de milisegundo, un costo insignificante frente a los miles de millones de ciclos por segundo disponibles.

Existen interrupciones **recuperables** (teclado, mouse, USB) e **irrecuperables** (p. ej. una división entre cero, que puede desencadenar una pantalla azul). El sistema operativo gestiona esto mediante un **manejador de interrupciones**.

## Conceptos clave

- Un SO es software que administra recursos de hardware para usuarios y programas, en cualquier dispositivo ("máquina"), no solo en computadoras.
- El SO cumple tres papeles: **árbitro** (aísla recursos entre aplicaciones), **ilusionista** (virtualización, memoria virtual, colas de impresión, particiones) y **estandarizador** (unifica comportamientos como botones de ventana o drivers).
- El **modelo de Von Neumann** describe toda computadora como CPU + memoria principal (programa ejecutado secuencialmente) + entrada/salida.
- El **ciclo de ejecución** (fetch–decode–execute–acceso a memoria–escritura) es la única operación que la CPU sabe hacer, repetida sin pausa para cada instrucción.
- La **frecuencia del reloj** (Hz) mide ciclos por segundo; dividiendo esa frecuencia entre los ciclos promedio por instrucción se estima cuántas instrucciones por segundo puede ejecutar una CPU.
- Delegar la administración de memoria y E/S de la CPU a buses y controladores especializados (y el uso de caché) es una de las razones centrales de la mejora de rendimiento histórica, independientemente del aumento de frecuencia.
- La **multiprogramación** simula paralelismo en una sola CPU; los **múltiples cores** lo logran de verdad.
- Las **interrupciones** permiten que la CPU reaccione a eventos externos deteniéndose brevemente y retomando su ejecución normal.

## Fuera del PDF — logística, tareas y metodología

- **Enfoque del curso:** administración de recursos del sistema operativo, con fuerte énfasis en perder el miedo a la línea de comandos (terminal/consola), como complemento a devops/operaciones.
- **Evaluación:**
  - 4 talleres de aplicación, 5 puntos cada uno (manejo práctico del sistema operativo).
  - Talleres adicionales de scripting para resolver problemas con herramientas del SO (no todo es Python/una aplicación dedicada).
  - 4 tareas programadas (simulaciones de distribución de recursos: medir tiempos, atender solicitudes sobre un recurso limitado).
  - 6 quizzes de 3 puntos cada uno, con hasta 2 puntos de bono: 2 puntos de bono si el promedio de quizzes es ≥85 y se hicieron todos; 1 punto de bono si el promedio está entre 70 y 85, o si se falló un solo quiz; 0 puntos de bono si se fallan 2 o más quizzes o el promedio es menor a 70. Los quizzes no tienen reapertura posterior al cierre.
  - 2 exámenes: se permite usar herramientas de IA como apoyo para retroalimentación, pero se espera honestidad sobre su uso (hacer un esfuerzo propio primero).
  - 15 puntos de asistencia y participación, evaluados principalmente mediante formularios de repaso periódicos (cada una o dos semanas), no por registro estricto de asistencia.
- **Taller 1 — Habilitación de Linux** (el PDF que originalmente se buscaba como "Clase 1"): instalar o habilitar un Linux (nativo, máquina virtual, USB en modo de prueba, o WSL en Windows) y entregar evidencia en video de un comando ejecutado (p. ej. `ping www.yahoo.com`). Incluye una segunda parte con ejercicios de línea de comandos (`pwd`, `ls` y sus variantes, `man`, `cd`, `mkdir`, `cp`, `find`, `grep`, `less`/`cat`, redirección con `>` y tuberías con `|`) sobre archivos de texto descargados de un repositorio de libros clásicos. Fecha de entrega: 30 de setiembre de 2026.
- **Modalidad:** curso virtual con fechas presenciales opcionales (21 de septiembre y 19 de octubre de 2026); las fechas de noviembre y diciembre se definirán más adelante (el cierre del cuatrimestre sería alrededor del 8-14 de diciembre de 2026).
- **Canal de comunicación:** grupo de WhatsApp del curso (compartido en el aula virtual), además de correo.
- **Formulario de repaso de esta semana:** plazo de una semana para completarlo (antes del mediodía del lunes siguiente).
- Se menciona un formulario de "seudónimos" pendiente de compartir, para el registro de notas.
