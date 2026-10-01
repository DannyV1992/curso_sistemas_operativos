# Clase 2 — Memoria, historia de los SO y el Kernel

- **Curso:** IIIC2026 - Sistemas Operativos, LEAD University
- **Docente:** Mario Miguel Agüero Obando
- **Fecha:** 14 de septiembre de 2026 (estimada por continuidad semanal respecto a la Clase 1 del 7 de septiembre; no se menciona explícitamente en la transcripción)
- **PDF fuente:** `1 - Conceptos básicos.pdf` (segunda mitad) y `2 - Kernel y Procesos.pdf` (primera mitad)
- **Cobertura:**
  - `1 - Conceptos básicos.pdf`: continúa desde donde terminó la Clase 1 (diapositiva "¿Cómo se ejecutan los programas? y 10") hasta el final del documento (diapositiva 36, "Las 4 partes de un Sistema Operativo"). **Completo** en lo que corresponde a esta clase.
  - `2 - Kernel y Procesos.pdf`: **parcial**, diapositivas 1 a 5 de 20 (hasta la crítica al microkernel). No se alcanzaron los ejemplos de SO de microkernel (AmigaOS, Minix, NexStep, AIX), los núcleos híbridos, el exonúcleo, ni nada de arranque del SO en forma de diapositiva, Process Control Block o estados de proceso — esos temas quedan para la Clase 3.

Segunda sesión del curso. Retoma la administración de recursos y la memoria, cierra la historia de los sistemas operativos (de los años 40 a Linux/Windows en los 90), y abre el tema de Kernel: qué es, sus funciones y sus tipos (monolítico y microkernel).

## 1. Repaso: el sistema operativo como ilusionista (la papelera de reciclaje)

Como ejemplo adicional al rol de **ilusionista** visto en la Clase 1: borrar un archivo no borra sus datos. La papelera de reciclaje no es un espacio físico aparte; es una lista de direcciones de inicio de los archivos "borrados". Al borrar, el sistema operativo solo marca ese espacio como **libre** (free), pero los datos siguen físicamente ahí hasta que algo los sobrescribe — de forma similar a quitar la placa de un carro en un parqueo para que el sistema crea que el espacio está vacío. Por eso existen herramientas de "undelete", y por eso los archivos borrados eran (y son) un vector de robo de información si no se sobrescriben realmente.

## 2. La memoria: evolución, jerarquía y costo

La memoria ha cambiado radicalmente en tamaño, velocidad y costo: un disco de **5 MB pesaba y costaba como un contenedor en 1956**, uno de **10 MB en 1964** era del tamaño de un plato grande, y para los años 80 un disco duro de 10 MB costaba cerca de **$3,398**. Hasta mediados de los 70 una memoria RAM de 16 KB (del tamaño de una carta larga) era de supercomputadora.

La **jerarquía de memoria** ordena los distintos tipos de almacenamiento según su cercanía a la CPU:

$$\text{Registros} \to \text{Caché (L1, L2, L3)} \to \text{RAM} \to \text{Disco(s) duro(s)} \to \text{Almacenamiento externo} \to \text{Almacenamiento en red}$$

- A mayor cercanía a la CPU: **más velocidad y más costo por bit**, pero **menos capacidad**.
- A mayor lejanía: **más capacidad y menor costo**, pero **menos velocidad**.
- Los discos de estado sólido (SSD) y PCI Express "rompen" la pirámide clásica: un SSD moderno es mucho más rápido que cualquier disco mecánico, sin importar cuán optimizado esté este último — los dispositivos mecánicos siempre pierden frente a los puramente electrónicos.

## 3. Tipos de sistemas operativos

Según el tipo de interacción que ofrecen, los sistemas operativos se clasifican en 5 tipos:

- **De lote (batch):** los más antiguos; leen instrucciones de cintas o tarjetas y ejecutan las operaciones de un proceso sin interacción.
- **Interactivos:** permiten depurar procesos en tiempo de ejecución; de aquí nació el **tiempo compartido** (*time sharing*), antecesor directo de los sistemas operativos de PC actuales.
- **De tiempo real:** la interacción con el hardware debe ser muy rápida (p. ej. sistemas embebidos industriales).
- **Híbridos:** combinan lote e interactivo.
- **Embebidos (o empotrados):** construidos para un propósito único dentro de un dispositivo (microondas, equipo de sonido, un decodificador de TV tradicional — no una caja Android TV, que corre un SO de propósito general).

## 4. Historia de los sistemas operativos

**Primera generación (años 40 a mediados de los 50):** los programas eran prácticamente "alambrados" (cableados a mano); no existían sistemas operativos. Los primeros sistemas que aparecieron fueron de **lote**, para dirigir la carga de tarjetas perforadas; los programadores debían **reservar tiempo** de la máquina para correr sus programas.

**Segunda generación (1955–1965):** apareció la **planeación de trabajos** (cargar programas cuando el sistema de lote + compilador correspondiente ya estaba listo) y el rol de **operador de la computadora**, la única persona que interactuaba directamente con la máquina. En esta época, **Grace Hopper** promovió la idea de no escribir todo en ensamblador y ayudó a consolidar el concepto de **compilador**, además de las primeras librerías de software.

**Tercera generación (desde 1965):** para lidiar con dispositivos de entrada/salida más lentos que la CPU, apareció la **multiprogramación**: cargar varios programas y repartirles tiempo de CPU, de forma que mientras uno espera una impresión, otro se ejecuta. De aquí nacieron las primeras formas de multitarea y, junto con ellas, el concepto de **interrupción** (si un usuario oprimía una tecla, el sistema debía interrumpir lo que hacía para atenderlo cuando correspondiera).

**Cuarta generación:** superado el problema de los dispositivos, el siguiente cuello de botella fue la escasez y el costo de la memoria RAM. A mediados de los 70 apareció la **memoria virtual**: usar parte del almacenamiento físico (disco) como extensión de la RAM. También aparecieron las primeras bases de datos.

## 5. Las computadoras personales: de las "caseras" a la guerra de los 90

En los 80 surgieron las computadoras caseras (monoprocesador, capacidad limitada, poco o nulo almacenamiento interno), pensadas para llevar la computación a los hogares. La británica **Sinclair** fue muy popular en Europa por su bajo costo; su competencia, **Acorn Computers**, construyó la **BBC Micro** (subvencionada por el gobierno británico para enseñar programación) y de ese proyecto nació la arquitectura **ARM**, creada por **Sophie Wilson** (diseño del set de instrucciones y del primer intérprete de BASIC) y **Steve Furber** (hardware). Es la misma arquitectura que hoy domina los procesadores de los celulares y los chips Apple Silicon.

> En las computadoras caseras venía el manual con las instrucciones de lenguaje máquina: cada quien programaba directamente para ese hardware específico.

**IBM** inventó la PC, pero publicó las especificaciones de bajo nivel para fomentar la compatibilidad — su "gran error", porque le permitió a **Compaq** usar la técnica de **diseño de cuarto oscuro** (*clean room design*) para replicar el comportamiento del hardware de IBM sin copiar su código fuente, abriendo el mercado de clones de PC y quitándole a IBM el control sobre su propia plataforma.

El triunfo de las PC en el mercado no fue solo por hardware: lo definieron las aplicaciones. **Lotus 1-2-3** (la primera hoja de cálculo para PC) y **WordPerfect** fueron las razones por las que muchas empresas compraron computadoras. Un dato curioso: el error de año bisiesto de Excel con el año 1900 viene de un bug heredado de Lotus 1-2-3, mantenido por compatibilidad. **Harvard Graphics** (el PowerPoint antes de PowerPoint) fue creado por el costarricense Mario Chávez.

En los 90, **Windows** venció a sus competidores no solo por el modo gráfico (inspirado en el Macintosh de Apple), sino porque Microsoft integró su propia suite ofimática (**Office**: Word, Excel, PowerPoint), contratando a programadores clave de WordPerfect, Lotus y Harvard Graphics. En paralelo, en 1992, nació **Linux**, que resolvió lo que le faltaba al proyecto **GNU**: un **kernel**.

## 6. Concepto clave: Kernel

El kernel es el **corazón** del sistema operativo: controla todo. Tiene un área de memoria exclusiva llamada **espacio de kernel**, a la que nadie puede entrar salvo el propio kernel (Windows es un ejemplo clásico de sistema con debilidades de seguridad históricas por brechas que permitían a atacantes llegar hasta ese espacio). El kernel decide quién usa cada recurso, quién lo libera, a quién le toca el turno, quién recibe memoria y qué hacer ante interrupciones.

El kernel tiene dos **modos de trabajo**:
- **Modo kernel:** instrucciones que solo el kernel puede ejecutar, relacionadas con la administración de bajo nivel del sistema.
- **Modo usuario:** donde corren las aplicaciones del usuario (el navegador, un editor de texto), con acceso restringido a los recursos.

## 7. Proceso, hilo y Shell

- **Proceso:** un programa que se está ejecutando. Se guarda en memoria y pasa por varias etapas. Todo programa en ejecución se relaciona con al menos un proceso.
- **Hilo (thread):** un proceso puede tener uno o más hilos de ejecución; todo proceso tiene al menos uno.
- **Shell:** una capa de interacción — un programa que permite usar el sistema operativo. El más clásico es la **línea de comandos** (terminal); la interfaz gráfica es otro tipo de shell. Saber usar la línea de comandos es, según el curso, indispensable para aspirar a roles técnicos avanzados.

Estudiar sistemas operativos es, en esencia, estudiar **cómo trabaja el kernel**: cómo administra el procesador, la memoria, los dispositivos y los archivos — las **4 partes** en las que se va a analizar un sistema operativo a lo largo del curso.

## 8. ¿Qué es un Kernel? (profundizando)

El kernel es quien separa las aplicaciones entre sí y mantiene segura la máquina — no solo frente a ataques externos, sino para evitar, por ejemplo, que lo que se escribe en Word aparezca en el Notepad. En el fondo, el sistema operativo y el kernel actúan como un **proxy**: un intermediario entre el hardware y las aplicaciones, procurando que todas "se entiendan" aunque no "hablen el mismo idioma".

## 9. Funciones del Kernel

- Garantizar que los procesos (programas, entradas/salidas) se ejecuten.
- Asegurar que los recursos sean usados exclusivamente por la aplicación que corresponde en cada momento (p. ej. que un `Ctrl+V` pegue lo del programa activo y no de otro).
- Establecer el estándar de comunicación entre programas (la tecnología OLE de la Clase 1 es un ejemplo de esto).
- Asignar memoria, tiempo de procesador y periféricos a cada programa cuando se ejecuta.

Las funciones de **comunicación** (red) y **almacenamiento físico** normalmente no viven dentro del núcleo mismo, pero su gestión se administra como un proceso más dentro del kernel — es como si el kernel tuviera "asistentes" a quienes delega tareas puntuales (p. ej. la descarga de un archivo) sin dejar de supervisarlas. Abrir un puerto de red, por ejemplo, no implica meterse directamente con el kernel.

## 10. Tipos de Kernel

- **Monolítico:** está directamente ligado al hardware — en la práctica, al **juego de instrucciones** del procesador (p. ej. x64, usado por Intel y AMD; Apple Silicon; o ARM, usado también por procesadores Snapdragon). Por eso un Windows compilado para x64 no corre en un PC con Snapdragon: hace falta una versión específica ("Windows on ARM"). No es modular: agregar una funcionalidad puede implicar recompilar todo el sistema. A pesar de esta rigidez, es el modelo que ha triunfado: Linux, Unix, DOS y MacOS (hasta la versión 8.6) son monolíticos. Los sistemas operativos modernos siguen siendo, en esencia, monolíticos, aunque han ido adoptando ideas de otras filosofías de diseño.
- **Microkernel:** el núcleo se limita a comunicación y planificación de procesos, delegando todo lo demás (entrada/salida, memoria, archivos) a servidores internos especializados. En el papel suena ideal (más modular, más fácil de optimizar y aislar fallos), pero en la práctica **nunca se ha logrado construir un microkernel que funcione bien en producción**, en casi 40 años de intentos — la sincronización entre esos servidores resulta demasiado compleja.

## Conceptos clave

- El rol **ilusionista** del SO también explica por qué borrar un archivo no borra sus datos: solo se libera el espacio.
- La **jerarquía de memoria** relaciona cercanía a la CPU con velocidad, costo y capacidad; los SSD rompen la jerarquía clásica frente a los discos mecánicos.
- Los SO se clasifican en: **de lote, interactivos, de tiempo real, híbridos y embebidos**.
- La historia de los SO avanza resolviendo cuellos de botella sucesivos: sin SO → **lote** → **multiprogramación/interrupciones** (CPU más rápida que la E/S) → **memoria virtual** (RAM escasa y cara).
- **ARM** nació del proyecto educativo BBC Micro de Acorn Computers; **Compaq** rompió el monopolio de IBM sobre la PC con ingeniería de diseño de cuarto oscuro; **Windows** triunfó gracias a Office, no solo a su interfaz gráfica; **Linux** nació en 1992 dándole kernel al proyecto GNU.
- El **kernel** es el corazón del SO, con espacio de memoria exclusivo y dos modos de trabajo: **kernel** y **usuario**.
- Un **proceso** es un programa en ejecución (con al menos un **hilo**); un **shell** es la capa que expone los servicios del SO al usuario (línea de comandos o interfaz gráfica).
- El kernel actúa como **proxy** entre hardware y aplicaciones, con 4 funciones centrales: ejecución de procesos, aislamiento de recursos, estandarización de comunicación, y asignación de memoria/procesador/periféricos.
- Existen kernels **monolíticos** (ligados al juego de instrucciones del hardware, pero el modelo dominante en la práctica) y **microkernel** (más modulares en teoría, pero sin implementaciones exitosas en producción hasta la fecha).

## Fuera del PDF — logística, tareas y metodología

- **BIOS/UEFI (fuera de las diapositivas, respondiendo una pregunta):** es la configuración básica de la tarjeta madre — el nivel de hardware más bajo al que un usuario normal puede llegar sin soldar nada. Define, entre otras cosas, el **boot menu** (desde cuál dispositivo arranca el sistema operativo) y permite activar/desactivar periféricos, chipset, velocidad de CPU, fecha/hora del sistema (que vive en una batería separada de la tarjeta madre) y, relevante para el Taller 1, la **virtualización por hardware** (`Intel VT-x` / `AMD-V`), necesaria para correr una máquina virtual. Entrar al BIOS (usualmente `Supr`, `F2`, `F10` o `F12` al encender) y habilitar esa opción no daña la computadora.
- **Taller 1 (recordatorio):** instalar o habilitar un Linux (nativo, máquina virtual, modo demo desde USB, o WSL en Windows) y entregar evidencia en video. El docente recomienda distribuciones "mainstream" (Ubuntu, Arch, Mint) por tener más soporte y modo demo disponible; desaconseja distros minimalistas poco comunes (p. ej. Slackware). Se amplía con una segunda parte usando comandos de línea de comandos de Windows/Linux sobre un repositorio de libros de texto. Plazo: 15 días desde esta clase.
- No olvidar llenar el **formulario de seudónimos** (para el registro de notas) y el **formulario de repaso** semanal.
- El profesor recomienda un par de videos documentales fuera de clase sobre la pelea histórica entre sistemas operativos de microkernel vs. monolíticos, y sobre cómo Compaq le quitó a IBM el control del mercado de PC.
