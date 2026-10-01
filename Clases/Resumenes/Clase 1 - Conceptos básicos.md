# Clase 1 — Conceptos básicos de Sistemas Operativos

**Curso:** IIIC2026 - Sistemas Operativos, LEAD University
**Docente:** Mario Miguel Agüero Obando
**Fecha:** 7 de septiembre de 2026
**PDF fuente:** `1 - Conceptos básicos.pdf` (36 diapositivas)
**Cobertura del PDF:** Parcial: diapositivas 1 a 21 de 36 (hasta «¿Cómo se ejecutan los programas? (y 10)»). No se saltó ninguna diapositiva del rango. El resto (Memoria, Jerarquía de memoria, Tipos de SO, Historia y generaciones de los SO) queda para la siguiente clase.
**Notas de fuente:** las aclaraciones marcadas como *Nota* corrigen o matizan algo dicho en clase que no es exacto; el contenido de la transcripción se conserva.

**Contexto.** Primera sesión del curso. Se presenta el programa y la evaluación, y se desarrolla el primer bloque de contenido: qué es un sistema operativo (SO), qué papeles cumple y cómo el modelo de Von Neumann, el ciclo de ejecución, los buses y las interrupciones explican por qué las computadoras funcionan como lo hacen.

---

## Ruta de la clase

| Bloque | Tema | Diapositivas |
|--------|------|--------------|
| 1 | Qué es un SO: definición, papeles y abstracción | 3–10 |
| 2 | Modelo de Von Neumann y programas en memoria | 11–12 |
| 3 | Ciclo de ejecución, reloj y rendimiento | 13–15 |
| 4 | Buses, caché y abstracción del hardware | 16–18 |
| 5 | Interrupciones y múltiples cores | 19–21 |

---

## 1. Definición (diapositiva 3)

Un SO es **software** que administra los recursos de hardware de una **máquina** para sus usuarios y para los demás programas que corren en ella. Se dice "máquina" y no "computador" porque el concepto se extiende a cualquier dispositivo con recursos que necesite administración: microondas, reproductores de DVD, decodificadores de TV, automóviles, teléfonos.

El curso no se enfoca en construir sistemas operativos sino en entender la **administración de recursos**, para comprender por qué ciertas restricciones y comportamientos existen tal como existen (útil en ciencia de datos y devops/operaciones).

---

## 2. ¿Cómo puede verse un SO? (diapositivas 4–7)

La máquina tiene recursos **limitados** (memoria, buses, ancho de banda, disco, procesador). Con varias aplicaciones abiertas a la vez (editor, navegador, visor de PDF, varias pestañas) comparten el mismo monitor, teclado y mouse; el SO hace que, al cambiar de programa activo, los eventos de teclado y mouse afecten solo a ese programa.

### Árbitro (diapositiva 5)

El SO separa y aísla los recursos entre aplicaciones:
- **Separación:** cada actividad se mantiene separada y recibe los recursos que necesita cuando los necesita.
- **Aislamiento (*fault isolation*):** lo que pasa en una aplicación no debe afectar a las demás; un error en una no debería tener consecuencias en otras, salvo una falla grave del sistema (caída general, daño del disco).
- **Comunicación:** permite pasar datos entre aplicaciones (copy-paste de un navegador a un editor) o entre computadoras, sin que el pegado caiga en la ventana equivocada.

El SO balancea necesidades, aísla conflictos y facilita el compartir.

> Antes, en entornos como DOS, solo se podía tener una aplicación abierta a la vez y no existía copiar/pegar entre programas.

La tecnología que permitió comunicar aplicaciones de forma natural fue **OLE** (*Object Linking and Embedding*), asociada a Windows 3.1 (±1992).

> **Nota:** en clase se dijo que Windows 3.1 fue la primera versión que permitió abrir más de una aplicación y que OLE introdujo el copy-paste. Históricamente no es exacto: versiones anteriores de Windows ya ofrecían multitarea básica y portapapeles. Lo que aportó OLE fue **vincular e incrustar objetos** entre aplicaciones (p. ej. una tabla de Excel dentro de un documento de Word).

### Ilusionista (diapositiva 6)

El SO hace creer que existen recursos que físicamente no existen, o disimula restricciones del hardware mediante una división apropiada de los recursos:
- **Virtualización:** una máquina virtual parece otra computadora dentro de la propia. Un espacio del disco real (un archivo en la máquina *host*) actúa como el disco "real" de la máquina virtual, y un fragmento de la RAM real como toda su RAM. Permite usar varios SO en una misma máquina.
- **Cola de impresión:** no es una impresora adicional sino un espacio de memoria que el SO ofrece para encolar documentos sin bloquear la máquina mientras se imprime.
- **Particiones de disco:** un solo disco físico se ve como varios discos.
- **Memoria virtual:** hace creer que hay más RAM de la que existe, descargando a disco el contenido que no está activo.

### Estandarizador (diapositiva 7)

El SO provee un modelo de servicios y reglas para construir aplicaciones: no es necesario que cada una "invente" cómo mostrarse en pantalla, leer el mouse o el teclado. Ese estándar actúa como **pegamento** y es el fundamento para compartir datos entre aplicaciones. Ejemplos: botones de ventana con comportamiento uniforme, drivers de impresora (antes cada programa debía soportar cada impresora por su cuenta; de ahí que programas como WordPerfect compitieran por tener el catálogo de impresoras más completo).

---

## 3. La abstracción del sistema operativo (diapositivas 8–10)

El SO oculta el hardware: el usuario percibe la máquina tal como el SO se la presenta.
- **Mismo SO, hardware distinto** (Windows 95 sobre un 80386 con slots ISA frente a un Pentium con slots PCI): para el usuario es "la misma compu", solo que una es más rápida.
- **Mismo hardware, SO distinto** (Windows 11 frente a Linux sobre un Ryzen 5000): para el usuario son dos computadoras completamente diferentes, y los programas de una no corren nativamente en la otra. Solo es posible con un intermediario como *Wine*.
- **Casi el mismo hardware, distinto CPU** (macOS sobre Intel frente a Apple Silicon): misma experiencia; solo usuarios muy especializados perciben la diferencia (se verá luego por qué).

> **Nota:** Wine se describió como emulador o máquina virtual de Windows; en rigor es una **capa de compatibilidad** que traduce las llamadas de Windows a las del SO anfitrión, no un emulador ni una VM.

---

## 4. ¿Cómo se ejecutan los programas? — Modelo de Von Neumann (diapositiva 11)

Es el esquema básico que describe toda computadora y la base para entender cualquier arquitectura posterior:
- **Entrada/Salida:** unidades separadas de la CPU. Originalmente teletipos (*TTY*, de *typing*; de ahí el nombre de las salidas estándar actuales) y más tarde monitores.
- **CPU** (*Central Processing Unit*): ejecuta instrucciones y procesos. Tiene tres partes:
  - **Registros:** memoria más básica y rápida dentro del procesador (p. ej. 16 registros de 64 bits en CPU modernas de 64 bits). Uno especial, el **contador de programa** (*program counter*), guarda la dirección de la **siguiente instrucción a ejecutar**.
  - **Unidad de control:** decodifica la instrucción y coordina al resto, como director de orquesta.
  - **ALU** (unidad aritmético-lógica): realiza los cálculos.
- **Memoria principal:** almacena el programa, que se ejecuta **secuencialmente**. Datos e instrucciones se guardan en áreas separadas (segmentos).

En las primeras computadoras la CPU tenía que encargarse directamente de **todo** (teclado, impresora, memoria), lo que consumía una fracción importante de su tiempo y las hacía lentas. Dentro de la CPU se realiza el **ciclo de ejecución**.

---

## 5. Los programas en memoria (diapositiva 12)

Un programa cargado en memoria tiene al menos dos segmentos (igual que un programa en ensamblador con `section .data` y `section .text`):
- **Segmento de datos:** las variables.
- **Segmento de código:** las instrucciones.

```asm
section .data
   mensaje db 'Hola, mundo!$', 0Dh, 0Ah
section .text
start:
   mov dx, mensaje   ; carga la dirección del mensaje
   mov ah, 09h       ; función para mostrar una cadena
   int 21h           ; llama a la interrupción del SO
```

El SO asigna además espacio adicional para las variables creadas a discreción del programador (objetos, datos leídos de un archivo): el **heap**.

---

## 6. El ciclo de ejecución (diapositiva 13)

Secuencia que la CPU repite, sin pausa, para cada instrucción de cada programa; es lo único que sabe hacer:

1. **Fetching:** se trae de memoria la siguiente instrucción, cuya dirección está en el *program counter*. Lo que se trae es prácticamente una instrucción de ensamblador.
2. **Decodificación:** la unidad de control identifica la instrucción y activa los circuitos de ejecución.
3. **Operación en la ALU:** calcula direcciones de memoria, identifica operandos y realiza las operaciones.
4. **Acceso a memoria:** se accede a la memoria del sistema para traer, escribir o enviar datos.
5. **Updates:** se actualizan los registros (y se avanza el program counter a la siguiente instrucción).

Según el autor el ciclo se describe con 4 a 7 pasos; 5 es el más estándar.

---

## 7. El reloj de la CPU y la velocidad de procesamiento (diapositiva 14)

El reloj (medido en Hz) no da la hora: genera pulsos (0 y 1) a frecuencia fija. **1 ciclo** es una subida y bajada completa; la cantidad de ciclos por segundo se mide en hertzios:
- 1 KHz = 1.000 ciclos/s; 1 MHz = 1.000.000 ciclos/s; 1 GHz = 1.000.000.000 ciclos/s.
- Más ciclos = más velocidad, pero también **más calor** en el procesador.

Cada instrucción dura una cantidad distinta de ciclos. Rangos por etapa:

| Fetching | Decodificación | Exec. ALU | Acceso a memoria | Updates |
|----------|----------------|-----------|------------------|---------|
| 8 | 10-12 | 20-40 | 10-30 | 8-20 |

**Ejemplo resuelto — del 8086 a un CPU moderno.** Con valores promedio de 8, 11, 30, 20 y 14 ciclos por etapa:

$$8 + 11 + 30 + 20 + 14 = 83 \text{ ciclos por instrucción}$$

8086 a ~5 MHz:

$$\frac{5.000.000}{83} \approx 60.241 \text{ instrucciones/segundo}$$

CPU moderno (i7 a ~4,5 GHz), suponiendo la misma duración por instrucción:

$$\frac{4.500.000.000}{83} \approx 54.216.900 \text{ instrucciones/segundo}$$

Es unas **900 veces** más. Este cálculo refleja solo el aumento de frecuencia. A eso se suma que la CPU moderna ya no administra memoria ni E/S (sección 9): antes cerca de un tercio de sus ciclos se iba en esas tareas, así que hoy una proporción mayor se dedica a instrucciones del programa real.

---

## 8. Una instrucción a la vez: multiprogramación y cores (diapositiva 15)

El ciclo de ejecución **solo puede procesar una instrucción a la vez**. Que parezca que Word, el navegador y Zoom corren "al mismo tiempo" es una **ilusión**:
- **Multiprogramación:** técnica que alterna rápidamente entre programas en una sola CPU. No es paralelismo real.
- **Múltiples cores:** la ilusión es "más real". Un core es un CPU; un procesador de 8 cores tiene 8 CPU y puede correr 8 programas en paralelo, normalmente uno por core (el detalle de los cores está al final de la sección 11).

Para mejorar el rendimiento, la arquitectura de las computadoras cambió para disminuir tiempos (secciones 9 y 10).

---

## 9. Buses y controladores (diapositiva 16)

Las primeras CPU manejaban directamente memoria y dispositivos. Con el tiempo:
- El **bus único** se partió en tres: **bus de control**, **bus de direcciones** y **bus de datos**, que se usan de forma independiente. Un controlador de direcciones gestiona la memoria y **controladores específicos** manejan cada dispositivo de E/S.
- Se creó un **bus de video** dedicado (VESA, AGP) que liberó a la CPU de dibujar la pantalla. Hoy está en desuso a favor de buses estándar, para simplificar el diseño.

El costo fue una CPU algo más compleja, pero se cambió la complejidad de "administrar cada dispositivo" por la de "coordinar la comunicación entre componentes", que escaló mucho mejor.

---

## 10. Memoria caché (diapositiva 17)

Para reducir los viajes a la RAM, los procesadores incorporan **caché** dentro del chip, dividido como los programas: **caché de datos** y **caché de instrucciones** (p. ej. el Pentium original). La RAM se coloca siempre lo más cerca posible de la CPU (a menudo a menos de 5 cm) para minimizar la latencia; a escala de circuitería esa distancia es enorme.

---

## 11. Abstracción, interrupciones y múltiples cores (diapositivas 18–21)

**Abstracción (diapositiva 18).** Estas operaciones básicas son accesibles vía lenguaje máquina y ensamblador. Sin SO, cada programador tendría que lidiar con cada detalle (acceso a memoria, mostrar en pantalla, imprimir). El SO ofrece una **abstracción** que facilita el trabajo a usuarios y programadores.

**Interrupciones (diapositivas 19–20).** Una interrupción es un evento que **ordena al procesador interrumpir** lo que hace y ejecutar un programa específico, que puede estar en el SO (interrupción del sistema) o en el BIOS (normalmente los eventos físicos). Las producen teclas, movimiento y clics del mouse, operaciones de E/S y errores físicos como desconectar un dispositivo.

Secuencia al ocurrir una:
1. Se guarda el estado del procesador (PC, registros y todo lo posible).
2. Se ejecuta el **manejador** de la interrupción (en el PDF, «manejador de instrucciones»; en clase, «manejador de interrupciones»). Identifica además a qué programa pertenece el evento, para reflejarlo en la ventana activa.
3. Si no fue un error irrecuperable, el procesador vuelve al estado anterior y continúa su proceso normal.

Todo esto toma centenares de ciclos de reloj, un costo insignificante frente a los miles de millones por segundo.

| Tipo | Ejemplos |
|------|----------|
| **Recuperables** | teclado, mouse, conectar o desconectar un USB |
| **Irrecuperables** | división entre cero (puede terminar en pantalla azul) |

**Múltiples cores (diapositiva 21).** Cada core usa los buses para actualizar los recursos de memoria que le corresponden. Un chip de 8 cores a 4,5 GHz tiene en teoría una capacidad de:

$$8 \times 54.216.900 \approx 433.700.000 \text{ instrucciones/segundo}$$

Pero sigue habiendo una sola impresora, un solo bus de video y un solo bus de datos a la RAM, que deben coordinarse entre varias CPU para que los programas no se interfieran ni se filtren datos de un proceso a otro. Esto aumenta la complejidad del SO y del diseño de software. Las interrupciones se complican ("una fiesta"): hay que saber en qué programa ocurrió el evento, detener el core que lo ejecuta, atender la interrupción y volver al flujo normal; además, hay que decidir cuál de los cores las atiende.

---

## Conceptos clave

- Un SO es software que administra recursos de hardware para usuarios y programas, en cualquier dispositivo ("máquina"), no solo en computadoras.
- El SO es **árbitro** (separa y aísla recursos), **ilusionista** (virtualización, memoria virtual, colas de impresión, particiones) y **estandarizador** (unifica comportamientos y drivers).
- La abstracción del SO oculta el hardware: el usuario percibe el SO, no la máquina.
- El **modelo de Von Neumann** describe la computadora como CPU (registros, unidad de control, ALU) + memoria principal (programa ejecutado secuencialmente) + E/S.
- Un programa en memoria tiene segmento de **código** y segmento de **datos**; el **heap** aloja las variables creadas por el programador.
- El **ciclo de ejecución** (fetching, decodificación, operación en ALU, acceso a memoria, updates) se repite siempre, una instrucción a la vez.
- Instrucciones por segundo ≈ frecuencia del reloj ÷ ciclos promedio por instrucción.
- Delegar memoria y E/S a buses y controladores, y usar caché, mejora el rendimiento más allá de la frecuencia.
- La **multiprogramación** simula paralelismo en una CPU; los **múltiples cores** lo logran de verdad, a costa de más complejidad.
- Las **interrupciones** detienen brevemente la CPU para atender un evento (se guarda y restaura el estado); pueden ser recuperables o irrecuperables.

---

## Fuera del PDF — logística, tareas y metodología

- **Enfoque del curso:** administración de recursos del sistema operativo, con fuerte énfasis en perder el miedo a la línea de comandos (terminal/consola). Muchas tareas de administración (acceder a servidores, hacer un backup de una base de datos, bajar un archivo por SFTP) solo pueden hacerse por terminal.
- **Evaluación:**
  - 4 talleres de aplicación, 5 puntos cada uno (manejo práctico del SO). El primero es montar Linux; los demás son de scripting, para resolver problemas con herramientas del SO (no todo es Python ni una aplicación dedicada).
  - 4 tareas programadas (simulaciones de distribución de recursos: medir tiempos, atender solicitudes sobre un recurso limitado).
  - 6 quizzes de 3 puntos cada uno, con hasta 2 puntos de bono: 2 puntos si el promedio es ≥85 y se hicieron todos; 1 punto si el promedio está entre 70 y 85, o si se falló un solo quiz; 0 puntos si se fallan 2 o más quizzes o el promedio es menor a 70. Los quizzes no se reabren tras el cierre.
  - 2 exámenes: se permite usar herramientas de IA como apoyo para retroalimentación, pero se espera honestidad sobre su uso (hacer un esfuerzo propio primero).
  - 15 puntos de asistencia y participación, evaluados sobre todo con formularios de repaso periódicos (cada una o dos semanas), no con registro estricto de asistencia.
- **Taller 1 — Habilitación de Linux:** instalar o habilitar un Linux (nativo, máquina virtual, USB en modo de prueba, WSL en Windows o capa gratuita de la nube) y entregar evidencia en video de un comando ejecutado (p. ej. `ping www.yahoo.com`). Incluye una segunda parte con ejercicios de línea de comandos (`pwd`, `ls`, `man`, `cd`, `mkdir`, `cp`, `find`, `grep`, `less`/`cat`, redirección con `>` y tuberías con `|`) sobre textos de un repositorio de libros clásicos. Entrega: 30 de septiembre de 2026 (según `Tareas/Taller_1/Taller-1.pdf`). Es el único taller donde quienes usan Windows o Mac pueden tener dificultades; los siguientes se pueden hacer con la línea de comandos de Windows, o con los mismos comandos en Mac y Linux.
- **Modalidad:** curso virtual con fechas presenciales opcionales (21 de septiembre y 19 de octubre de 2026); las de noviembre y diciembre se definirán más adelante (cierre del cuatrimestre alrededor del 8-14 de diciembre de 2026). Todas las entregas estarán en una semana extra al final del aula virtual.
- **Canal de comunicación:** grupo de WhatsApp del curso (enlace en el aula virtual), además de correo. Ante una emergencia que impida cumplir una entrega, se debe escribir al docente por privado para acordar un plan.
- **Formulario de repaso de esta semana:** plazo de una semana (antes del mediodía del lunes siguiente).
- Se mencionó un formulario de "seudónimos" pendiente de compartir, para el registro de notas.
