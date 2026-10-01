# Clase 3 — Tipos de kernel, arranque del SO y procesos

**Curso:** IIIC2026 - Sistemas Operativos, LEAD University
**Docente:** Mario Miguel Agüero Obando
**Fecha:** 21 de septiembre de 2026 (estimada por continuidad semanal respecto a la Clase 2; no se menciona explícitamente en la transcripción)
**PDF fuente:** `2 - Kernel y Procesos.pdf` (28 diapositivas; versión actualizada por el docente el mismo día, con una aclaración nueva sobre el BIOS y el arranque)
**Cobertura del PDF:** Parcial: diapositivas 6 a 23 de 28 (de «Tipos de Kernel (2.1)» a «El Process Scheduler»). Las diapositivas 1 a 5 se cubrieron en la Clase 2. No se saltó ninguna diapositiva del rango. Las diapositivas 24 a 28 (bloques de E/S y de operación, cómo se ejecuta un proceso, políticas, algoritmos y tiempos muertos) no se reflejan en este resumen; sus temas se retoman en la Clase 4.
**Nota sobre la transcripción:** hay una pausa de ~30 min a media clase (la segunda parte repasa el ciclo de vida del proceso) y varios tramos de la transcripción están mal reconocidos (p. ej. «Turingbaum» = Tanenbaum, «Love performance» = low performance); se corrigieron por contexto.

**Contexto.** Sesión dedicada a cerrar los tipos de kernel, explicar cómo arranca una computadora hasta que el kernel toma el control, y presentar el **proceso** como abstracción: su representación en memoria, el **Process Control Block**, sus **estados** y los dos planificadores del **Process Manager**. Deja listo el terreno para los algoritmos de planificación de la próxima clase.

**Repaso rápido de clases anteriores:** el SO administra recursos y crea ilusiones (papelera, cola de impresión); sus dos grandes componentes son el **kernel** (modo administrador, acceso a todo) y el **shell** (interfaz con el usuario, en texto o gráfica). Sin el SO, cada programa tendría que reimplementar desde cero cosas como la interfaz gráfica o el soporte de impresoras (como ocurría en la era de MS-DOS, donde cada editor de texto traía su lista limitada de impresoras compatibles).

---

## Ruta de la clase

| Bloque | Tema | Diapositivas |
|--------|------|--------------|
| 1 | Tipos de kernel (continuación) | 5–8 |
| 2 | Arranque del SO | 9–11 |
| 3 | Procesos y kernel; proceso en memoria | 12–14 |
| 4 | Process Control Block | 15–18 |
| 5 | Estados de un proceso | 19 |
| 6 | Job Scheduler y Process Scheduler | 20–23 |

---

## 1. Tipos de Kernel (continuación) (diapositivas 5–8)

### 1.1 Monolítico (repaso) y por qué domina (repaso de la diapositiva 4)
Un kernel monolítico está ligado a una plataforma de hardware concreta, no es modular y escribir algo nuevo cuesta mucho. Por eso al descargar una distribución de Linux hay que elegir la versión acorde al procesador (`amd64` = PC de 64 bits, tanto Intel como AMD; `i386` = 32 bits; `arm64` = procesadores ARM).

- Ejemplos: Linux, Unix, DOS, MacOS hasta la 8.6.
- Aun los SO que incorporan ideas de otros modelos tienen ~80–90 % de su núcleo monolítico.

### 1.2 Microkernel (diapositivas 5–6)
Núcleo mínimo (comunicación y planificación de procesos) que delega todo lo demás a **servidores** (memoria, disco, seguridad, procesos, archivos…), que se comunican con él por IPC. En teoría: SO más óptimos para multitarea, recursos y errores más aislados, y cada servidor mejorable por separado.

- **Problema de fondo:** administrar procesos y administrar memoria son tareas que en la práctica **no se pueden separar**; sincronizar los servidores es muy complejo y además son más difíciles de programar.
- Donde se ha aplicado la idea a un problema puntual (p. ej. comunicación en red) ha funcionado parcialmente; aplicada a todo el SO «es lentísima» y nunca ha prosperado.
- **Ejemplos:** AmigaOS, Minix, NeXTSTEP (considerado híbrido), AIX.
  - **NeXTSTEP** fue el SO de las estaciones de trabajo que Steve Jobs fundó al salir de Apple: muy avanzado, pero cada equipo costaba varios miles de dólares (lo mismo que ~10–20 PC normales), por lo que casi no se vendió. Su SO sirvió de base para el **macOS moderno**.

### Historia: Minix, GNU y el origen de Linux (explicación oral)
Contexto que explica por qué Linux es monolítico:

- **Andrew Tanenbaum** (profesor en Holanda, referente de teoría de SO) promovía el diseño con microkernel y escribió un libro con el SO **Minix**. El código venía en el libro, pero para modificarlo había que comprar el diskette con el código compilado (~80 USD).
- **Richard Stallman** (MIT) fundó el **movimiento de Software Libre** tras no poder obtener el código fuente del driver de una impresora que su institución sí había comprado: el comprador obtiene derecho de uso, no el código.
- El proyecto **GNU** reescribió todo Unix (compilador de C, comandos y herramientas como `grep`, el que se usa en el Taller 1), pero su kernel, **Hurd**, se diseñó como microkernel y **nunca funcionó bien** (sin avances relevantes desde ~2015).
- **Linus Torvalds**, estudiante, leyó el libro de Tanenbaum, se encontró con que microkernel era un enredo y hacerlo todo le obligaba a pagar, y optó por un kernel **monolítico** sencillo para los PC 386. Lo compiló con el compilador de GNU y le acopló las herramientas de GNU: de ahí el nombre **GNU/Linux**.
- Tanenbaum y Torvalds protagonizaron una histórica discusión pública (listas de correo) sobre microkernel vs. monolítico; la evidencia del uso masivo de Linux zanjó el tema.

### 1.3 Núcleos híbridos (diapositiva 7)
Mezclan filosofía monolítica y microkernel: una parte queda en el kernel y otra se expone para que cada aplicación/proceso la gestione individualmente. Es la **tendencia moderna**, adoptada por Windows desde Windows NT y por Mac OS X.

- En la práctica son ~90 % monolíticos; se usa software aparte dentro del SO solo para cosas puntuales (red, USB y administración de muchos dispositivos).

### 1.4 Exonúcleo (diapositiva 8)
Solo se usa en **investigación**. El kernel se reduce a las operaciones más básicas (el BIOS y las abstracciones mínimas de hardware) y todo lo demás lo dan gestores/librerías específicos a las aplicaciones. Análogo a una **arquitectura de microservicios**. No se estudia en detalle.

---

## 2. ¿Cómo se carga el sistema operativo? (diapositivas 9–11)

> El kernel no está «en el BIOS»: el firmware prepara y entrega; el SO toma el control cuando empieza a ejecutarse el kernel.

| Paso | Etapa | Qué ocurre |
|------|-------|------------|
| 1 | **Encendido** | La CPU comienza a ejecutar el **firmware** guardado en la placa base. |
| 2 | **BIOS/UEFI + POST** | *Basic Input/Output System*. Hace el «inventario» del equipo: cuenta la RAM, detecta discos y periféricos, verifica e inicializa el hardware (*Power-On Self-Test*). |
| 3 | **Dispositivo de arranque** | Busca un medio booteable (SSD/HDD, USB o red) **en el orden configurado** en el BIOS y lee su primer código de arranque (MBR/GPT o partición EFI). |
| 4 | **Cargador de arranque** (*bootloader*) | El firmware lo invoca y le cede el control. Es «la llave del carro»: el que enciende el SO. Ejemplos: GRUB, systemd-boot, Windows Boot Manager. |
| 5 | **Kernel** | Se descomprime y se carga en RAM; luego inicializa memoria, controladores y servicios (impresión, puertos seriales, sonido, cámara…) y el espacio de usuario. |

- El **firmware no es el SO**: su función termina al entregar el control. Desde que corre el kernel, el SO administra la máquina.
- El kernel va tomando control poco a poco de la RAM, los dispositivos y el resto del hardware.

---

## 3. Ya con el S.O. cargado: procesos y kernel (diapositivas 12–13)

- El kernel tiene acceso a **toda** la máquina: se ejecuta directamente en el procesador **sin limitaciones** y puede hacer cualquier cosa. Lo primero que hace es levantar procesos.
- Un **proceso** es una **abstracción interna** del SO para la ejecución de un programa:
  - **Programa** = entidad inactiva (bytes en disco). **Proceso** = entidad activa (programa cargado en memoria).
  - Tiene **restricciones**: solo ve la memoria asignada y los recursos a los que el kernel le da paso (p. ej. si puede usar la impresora o escribir en ciertos sectores del disco).
  - Para acceder a memoria o leer/escribir en disco **necesita permisos del kernel**.
  - **Tarea** (*task*) es sinónimo de proceso.
- Las restricciones varían por SO: Windows deja guardar casi en cualquier directorio; macOS y Linux son más restrictivos y exigen permisos especiales. Esa diferencia la define la política de seguridad del kernel.

### ¿Cómo conviven kernel y procesos restringidos en el mismo procesador?
Se piensa en el procesador como alguien con **dos personalidades**: cuando está «con el kernel» lo puede todo (acceso completo a todos los recursos); cuando el control se devuelve a un programa de usuario, se le retiran los privilegios (**modo usuario**) y queda limitado. El kernel recupera el control en ciertos momentos para administrar.

---

## 4. Procesos y el Kernel: representación en memoria (diapositiva 14)

- El SO se carga en memoria al inicio. Al ejecutar un programa, el SO **copia las instrucciones y datos** del ejecutable a la memoria física y le asigna un espacio con cuatro zonas: **instrucciones, datos, heap y pila** (esta última guarda las llamadas a procedimientos; es la pila de llamados vista en Compiladores).
- Un mismo programa puede ejecutarse **múltiples veces a la vez**; cada ejecución reserva espacios **distintos** en memoria y es **un proceso independiente**.
  - Ejemplo: abrir tres veces el Bloc de notas da el mismo código en disco pero 3 procesos separados; lo que se escribe en uno no afecta a los otros.
- Un proceso es una **instancia de ejecución** de un programa compilado, como un objeto es una instancia de una clase.

---

## 5. Process Control Block (PCB) (diapositivas 15–18)

Estructura de datos con la que el SO controla cada proceso: su «cédula de identidad» interna, que le permite administrarlo mejor. Punto clave del tema.

| Campo | Contenido |
|-------|-----------|
| **Id del proceso** | Descriptor único asignado por el Job Scheduler (como el número de cédula). |
| **Status** | Estado actual: HOLD, READY, RUNNING o WAITING. |
| **Estado** (contexto) | Cómo estaba el proceso en su última ejecución: *instrucción actual* (process status word; vacía si el proceso está corriendo), *contenido de los registros* de la CPU antes de interrumpirlo, *memoria principal* (dirección de su espacio y, si usa memoria virtual, el mapeo), *recursos* asignados (direcciones de memoria o sectores de disco) y *prioridad* (define cuándo vuelve a ejecutarse). |
| **Contabilidad** | Uso y rendimiento: tiempo de CPU usado, tiempo y espacio consumidos en memoria, uso de memoria virtual, cantidad y tipo de operaciones de E/S y tiempo usado en E/S. |

También registra el archivo de origen, el usuario que ordenó la ejecución y su nivel de privilegios.

---

## 6. Estados de un proceso a alto nivel (diapositiva 19)

Ciclo de vida completo (diagrama de la diapositiva 19):

```
Hold --(Job Scheduler)--> Ready --(Process Scheduler)--> Running --(Job Scheduler)--> Finished
                            ^                               |
                            |---- Time Interrupt -----------|   (se acabó su tiempo)
                            |                               |
                         Waiting <--- page interrupt / E/S (disco, impresora, otras colas)
```

1. **Hold:** al dar doble clic, el kernel asigna un espacio de memoria al programa y lo deja cargado. Esta parte la hace el **Memory Manager** (tema de las próximas semanas).
2. **Ready:** el **Job Scheduler** lo pasa a la cola de ejecución y **se le crea el PCB**. Significa que ya puede esperar un turno de CPU.
3. **Running:** el **Process Scheduler** le asigna CPU. El paso Ready → Running lo hace este planificador.
4. De Running puede ir a:
   - **Ready**, por *time interrupt* (se le acabó el tiempo asignado) o una interrupción atendida.
   - **Waiting**, cuando no puede continuar porque espera algo: un cambio de página, lectura/escritura de disco, impresión o entrada del teclado. Ejemplo: un programa en Python detenido en `input()` está en *waiting* y **no consume CPU**, aunque parezca que «está ocupado». Al terminar el evento vuelve a Ready, nunca directo a Running.
   - **Finished**, al terminar el programa, por error o por comando de terminación directa; el Job Scheduler lo saca.

El alcance del curso en este tema comienza en Hold: de ahí en adelante lo gestiona el Process Manager.

---

## 7. ¿Qué o quién es el Job Scheduler? (diapositivas 20–23)

El **Process Manager** (llamado *Processor Manager* en el PDF) es la parte del SO que lleva el control de los procesos: vigila si uno se ejecuta o espera operaciones de E/S. Tiene dos partes, especialmente críticas hoy con procesadores multinúcleo:

| | Job Scheduler | Process Scheduler |
|---|---------------|-------------------|
| **Decide** | Si un proceso **entra o sale** del ciclo de ejecución | **Qué proceso** usa la CPU y cuándo |
| **Transiciones** | Hold → Ready; Running → Finished | Ready → Running; Running → Ready/Waiting |
| **Nivel** | Alto nivel; cuida de no saturar la E/S y de mantener todo ocupado | Muy bajo nivel; opera constantemente |

**Analogía del Lego:** el Job Scheduler es decidir armar el Lego, buscar la caja y dejarla lista; el Process Scheduler es abrir la caja, sacar las instrucciones y ejecutar los pasos uno a uno. Una llamada telefónica a mitad del armado es una **interrupción**: se marca por dónde iba (se guarda el contexto en el PCB), se atiende y luego se retoma donde se dejó.

### Multiprogramación
El proceso de **asignar tiempo de procesador a cada proceso** se llama **multiprogramación**: resultado de la acción conjunta de ambos planificadores.

---

## 8. Cómo se logra la ilusión de ejecutar varios programas a la vez (explicación oral)

- Un reloj de CPU genera miles de millones de ciclos por segundo. Con un solo núcleo, el SO reparte **fragmentos de esos ciclos** entre los programas, rotándolos tan rápido que parecen correr en paralelo, cuando en cada CPU solo se ejecuta uno a la vez.
- El SO no sabe qué hace el usuario; solo **detecta actividad** (p. ej. una ráfaga de interrupciones de teclado) y asigna más ciclos a los procesos activos, dejando el mínimo a los demás para que puedan atender eventos.
- En equipos con un solo núcleo, cambiar de aplicación podía tardar varios segundos por el costo de reasignar la memoria; hoy casi no se nota.
- Con **múltiples núcleos (multicore)** el SO reparte los procesos entre varias CPU, y cada una sigue alternándolos. Hay CPU con núcleos de **alto** y **bajo rendimiento**: el SO manda los programas pesados (navegador, intérprete de Python) a los primeros y los livianos o inactivos a los segundos.
- **Sin cambio de proceso** (una sola CPU sin rotación) habría que esperar a que terminara cada programa antes de ejecutar el siguiente. Por eso surgió la técnica en los mainframes compartidos por decenas de usuarios con terminales tontas.

### Políticas históricas para ordenar la ejecución (adelanto de la diapositiva 27)
1. **FIFO/FCFS** (primero en llegar, primero en ejecutarse): si llega un programa largo, todos esperan a que termine (incluso si falla).
2. **Prioridad al más corto** (o al más próximo a terminar): se descartó por lo complejo que hacía el SO.
3. **Round Robin** (rotación): todos reciben el mismo tiempo, en turnos. Es lo que usan en esencia todos los SO actuales, con variantes.

Los algoritmos se estudian en la próxima clase.

---

## Conceptos clave

- **Microkernel:** núcleo mínimo + servidores; buena idea teórica, poco viable en la práctica. **Híbrido** = tendencia actual; **exonúcleo** = solo investigación. Linux nació monolítico y con las herramientas de GNU.
- **Arranque:** encendido → BIOS/UEFI (POST) → dispositivo de arranque → bootloader → kernel en RAM. El firmware **no** es el SO.
- El kernel tiene acceso total; los procesos corren en **modo usuario** con restricciones y piden permisos al kernel.
- **Programa** = inactivo en disco; **proceso** = programa cargado en memoria, instancia de ejecución independiente (instrucciones, datos, heap, pila).
- El **PCB** es la cédula de identidad del proceso: id, status, estado/contexto, recursos, prioridad y contabilidad.
- **Estados:** Hold → Ready → Running → Finished, con Waiting por E/S o interrupciones; Waiting siempre regresa por Ready.
- **Job Scheduler** (entrada y salida del ciclo) vs. **Process Scheduler** (asignación de CPU); juntos hacen posible la **multiprogramación**.
- La «simultaneidad» es una ilusión por división de tiempo (y por reparto entre núcleos).

---

## Fuera del PDF — logística, tareas y metodología

- **Material actualizado:** la presentación `Kernel y Procesos` y el enunciado del **Taller 1** se actualizaron en el aula virtual (cambió una actividad y las referencias a archivos/libros que ya no existen en el repositorio). Volver a descargar ambos. Quien ya entregó el taller puede corregir: se permiten **1 o 2 entregas** a quien lo necesite.
- **Quiz 1:** publicado el día de la clase, con **8 días** para completarlo. Cubre solo lo visto hasta la clase anterior: sistema operativo, historia y conceptos fundamentales (incluye «¿qué es un kernel?»); **no incluye procesos**.
- **Tarea programada 1** (enunciado aún pendiente de publicar): simulación de procesos con **un único procesador y una sola cola**, política **FIFO**.
  - Los procesos (duración y momento de llegada) se leen de un archivo **CSV**; se debe validar que no haya **identificadores duplicados** ni **líneas incompletas**.
  - El tiempo arranca en 0; los procesos entran a la cola (Hold → Ready) y se ejecutan uno a uno hasta terminar, sin interrupciones ni transiciones a Waiting. Al terminar cada uno se guardan estadísticas de ejecución.
  - La tarea 2 modificará esta misma simulación agregando **segmentación en la ejecución**; el mismo simulador se irá extendiendo durante el curso.
- **Próxima clase:** algoritmos de asignación de tiempos/planificación de procesos y, después, administración de memoria.
- **Formulario de repaso semanal:** recordatorio de llenarlo.
- **Disponibilidad del docente:** no hay clase presencial hasta el **19 de octubre**. Puede coordinarse una reunión presencial los jueves (antes o después de clase presencial) o algún sábado si se avisa.
