# Examen 2

**Curso:** IIIC2026 - Sistemas Operativos, LEAD University

**Docente:** Mario Miguel Agüero Obando

**Estudiante:** Daniel Vásquez González

---

## Parte 1. Lo que sabía o pensaba antes del curso

Antes del curso tenía una idea bastante simplificada. Sabía que al dar doble clic a un programa este "se abre", que para ejecutarse tenía que pasar del disco a la memoria RAM y que luego el procesador iba ejecutando sus instrucciones. De la programación (por ejemplo, la pila de llamados que vimos en Compiladores) tenía claro que un programa son instrucciones y datos, pero imaginaba que el programa "hablaba" directamente con el hardware: que si escribía en el teclado el programa recibía la tecla, y que si guardaba un archivo escribía en el disco por su cuenta.

Del arranque sabía solamente que al prender la computadora aparecía el logo del fabricante, luego cargaba Windows y que existía algo llamado BIOS que se podía configurar. Pensaba que el sistema operativo "ya estaba ahí" y no tenía claro cómo llegaba a la memoria, ni quién lo cargaba.

Tampoco distinguía bien programa de proceso, ni sabía que alguien decide a cuál programa le toca el procesador. Suponía que varios programas corrían "a la vez" de forma literal, y que la memoria se repartía de forma sencilla, sin páginas ni memoria virtual. Lo que sigue es lo que entiendo ahora, con los conceptos del curso.

---

## Parte 2. Qué ocurre desde que el usuario inicia el programa hasta que termina

Se toma como ejemplo un programa de notas que sincroniza con un servidor por Internet y guarda una bitácora de cada acción del usuario en el disco duro.

### 0. Antes del clic: el escenario ya está montado

Al encender el equipo la CPU ejecuta el firmware de la placa (BIOS/UEFI), que hace el POST (inventario y verificación de RAM, discos y periféricos). Luego busca un dispositivo booteable en el orden configurado y lee su primer sector (el MBR), donde está el *bootloader*. Este carga el **kernel** en la RAM y le cede el control; el firmware no es el sistema operativo. El kernel inicializa memoria, drivers y servicios y levanta el **shell** (el escritorio). A partir de ahí el kernel corre en **modo kernel** (acceso total) y todo lo demás, incluido el escritorio, corre en **modo usuario**, con restricciones: solo ve la memoria que se le asignó y todo lo demás lo pide al kernel mediante **llamadas al sistema**. Dentro del kernel trabajan los cuatro *managers*: Procesador/Procesos, Memoria, Dispositivos y Archivos.

### 1. El doble clic: de la mano al kernel

El mouse es un dispositivo **dedicado** que el Device Manager asigna al shell, que tiene el foco. Cada movimiento o clic produce una **interrupción** de hardware: la CPU detiene lo que hace, guarda el contexto del proceso en ejecución en su PCB, pasa a modo kernel y ejecuta el manejador (el *driver*) del dispositivo. Este lee el dato en la dirección de memoria asignada al dispositivo, y el kernel se lo entrega al proceso con el foco, que estaba en estado *Waiting* esperando eventos y pasa a *Ready*. Si el mouse es USB, el dato viaja por el único canal físico del bus, donde el controlador (HCI) reparte turnos entre los dispositivos y los atiende por tipo de transferencia de interrupción. Después se restaura el contexto y el proceso interrumpido continúa. El shell interpreta el doble clic sobre el acceso directo y le pide al kernel, con una llamada al sistema, crear un proceso para ese ejecutable.

### 2. Del archivo al proceso: File Manager, Memory Manager y Job Scheduler

1. **File Manager.** Recibe la ruta del ejecutable y la busca en la estructura jerárquica de directorios. El **módulo de control de acceso** verifica, con permisos o ACL, que el usuario tenga permiso de ejecución (autorización, distinta de la autenticación, que se hizo al iniciar sesión). El sistema lógico de archivos traduce el archivo a los clusters que ocupa (con la FAT o los inodes, según el sistema de archivos) y el sistema físico lo traduce a direcciones de dispositivo.
2. **Device Manager.** Las solicitudes llegan a la unidad de control del disco mediante el canal de E/S; la CPU solo da la orden y "se desentiende". Si el disco está ocupado (su *Channel Status Word* lo indica), la solicitud espera en una **cola** y el proceso queda en *Waiting*. En un HDD hay que mover el brazo al cilindro correcto y esperar la media vuelta del plato; en un SSD no hay partes mecánicas. Los datos van del disco a la RAM por **DMA**, sin pasar por la CPU, y los **buffers** absorben la diferencia de velocidad. Al terminar, una interrupción avisa al kernel.
3. **Memory Manager.** El programa queda en estado **Hold** y el Memory Manager decide dónde cargarlo. Con **páginas por demanda** solo se carga la parte necesaria (las primeras páginas de código) en marcos libres, aunque no sean contiguos; el resto sigue en disco. Se actualizan la **Job Table** (tamaño del job y dónde empieza su tabla), la **Page Map Table** (página, estado en memoria, referenciada, modificada y marco) y la **Memory Map Table** (qué marcos están libres u ocupados). El proceso recibe sus cuatro zonas: instrucciones, datos, *heap* y pila.
4. **Job Scheduler.** Le asigna un identificador, **crea el PCB** (id, estado, registros, recursos, prioridad y contabilidad) y lo pasa a **Ready**. Un programa es solo bytes en disco; ahora es un proceso, una instancia de ejecución independiente (abrirlo dos veces genera dos procesos).

### 3. El programa corre: Process Scheduler, memoria virtual y fallos de página

El **Process Scheduler** toma el proceso de la cola de *Ready* y lo pasa a **Running** (por ejemplo con Round Robin: cada proceso recibe un quantum y, al agotarse, una interrupción de reloj lo devuelve a *Ready* tras un **cambio de contexto**). Por eso muchos programas parecen correr en paralelo, aunque cada núcleo ejecuta uno solo a la vez; en un equipo con núcleos de alto y de bajo rendimiento, el planificador manda este programa al núcleo que le conviene. El proceso solo emite **direcciones lógicas**; el hardware de memoria las convierte en físicas con la PMT (dirección de inicio de la página más el *offset*). Si toca una página que no está en RAM ocurre un **fallo de página**: el proceso pasa a *Waiting* mientras se trae la página del disco por el mismo camino de E/S descrito antes. Si no hay marcos libres, se elige una víctima con **FIFO** o **LRU**; si la víctima fue modificada hay que escribirla antes a disco (*swap*), y si es solo código se descarta. Al llegar la página, una interrupción devuelve el proceso a *Ready* (nunca directo a *Running*). Si el proceso accediera a memoria ajena, la MMU lo detectaría y el kernel lo mataría con SIGSEGV: muere el proceso, no el sistema.

### 4. Interacción con el teclado y el mouse durante la ejecución

El programa espera una tecla y está en *Waiting*, sin consumir CPU. Al teclear, el teclado genera una interrupción; el kernel guarda el contexto del proceso que estaba corriendo, el *driver* lee el código de la tecla y lo deja en el buffer del teclado. Como el teclado es un dispositivo dedicado que el Device Manager asigna solo al programa con el **foco**, lo tecleado va únicamente a este (si fuera compartido aparecería también en otras ventanas). El proceso pasa a *Ready* y, cuando le toca, procesa la tecla y la dibuja en pantalla, lo que implica pedir a la tarjeta gráfica que actualice la ventana. Las teclas del sistema (como la de Windows) las atiende el shell y no el programa. Los clics del mouse siguen el mismo camino que el doble clic inicial.

### 5. Interacción con la red

Para sincronizar, el programa abre un *socket* mediante llamadas al sistema; el programa nunca toca la tarjeta de red. El kernel, con el **firewall** y el filtrado de paquetes, decide si la conexión sale. La tarjeta de red es un dispositivo **compartido** (varios procesos usan la misma conexión): el Device Manager organiza las solicitudes en colas y los **buffers** guardan los paquetes mientras la red, más lenta que la CPU, los despacha. El proceso queda en *Waiting* hasta que llega la respuesta. Cuando llegan datos, la tarjeta los deposita en memoria por **DMA** y lanza una interrupción; el kernel reconoce a cuál proceso pertenecen y lo pasa a *Ready*. Si el tráfico va cifrado, el cifrado lo hace el programa o una biblioteca en modo usuario. Si la tarjeta está ocupada, la solicitud espera su turno; si se pierde la conexión, el kernel devuelve un error y el programa decide qué hacer. Si se conecta un dispositivo nuevo durante la sesión (una llave USB, por ejemplo), el HCI lo detecta, lo enumera, le asigna un canal virtual y el kernel busca su *driver*, sin afectar al programa.

### 6. La bitácora: escribir y leer archivos

Cada acción del usuario genera una línea en la bitácora:

1. El programa hace una llamada al sistema (`open` y luego `write`). El File Manager revisa **permisos** (el usuario debe poder escribir; si dos procesos quisieran escribir a la vez se protege la integridad) y localiza el archivo por su entrada de directorio.
2. Los datos se copian primero a un **buffer** en RAM, porque el disco es mucho más lento. El proceso puede seguir o, si debe esperar la confirmación, pasa a *Waiting*.
3. El sistema lógico decide en qué **clusters** (conjuntos de sectores) caen los datos nuevos. Si el último cluster está lleno, reserva otro libre y actualiza la FAT o el inode (tamaño, fecha, punteros). Un cluster se reserva completo aunque no se llene, lo que causa fragmentación interna.
4. El Device Manager envía la orden a la unidad de control del disco (cilindro, superficie y sector en un HDD; bloques en un SSD) y, si el disco está ocupado, la encola. Los datos van por **DMA** al dispositivo y, al terminar, una **interrupción** avisa al kernel, que devuelve el proceso a *Ready*.
5. **Leer** la bitácora (por ejemplo para mostrar el historial) recorre el camino inverso: el File Manager traduce nombre, clusters y sectores, el disco entrega los datos por DMA a un buffer y de ahí pasan a la memoria del proceso, con una interrupción al finalizar. Si los datos aún están en un buffer o caché en RAM, no hace falta ir al disco.

Como la bitácora solo crece, se accede de forma secuencial y todo el rato hay pequeñas escrituras: mientras ocurre una E/S la CPU atiende a otros procesos, que es lo que permite la multiprogramación.

### 7. Cómo termina el programa

El usuario cierra la ventana. El clic es una interrupción que llega al programa como evento. Este guarda su estado, vacía el buffer de la bitácora al disco (por el camino descrito), cierra el *socket* y el archivo, y llama a `exit`. Si en cambio fallara, el kernel lo terminaría por error o por el comando de terminación directa. El proceso pasa a **Finished** y el **Job Scheduler** lo saca del ciclo de ejecución. El Memory Manager marca como libres sus marcos en la Memory Map Table (los datos no se borran, solo se libera el espacio, como en la papelera de reciclaje), el Device Manager libera los dispositivos y buffers que tenía asignados, el File Manager cierra los archivos abiertos y el kernel guarda las estadísticas de la contabilidad del PCB y elimina el PCB. El proceso padre (el shell) es notificado, y vuelve a ser el que espera la siguiente interacción del usuario, con el procesador atendiendo a los demás procesos.

En todo el recorrido el patrón se repite: el programa nunca toca el hardware directamente; pide al kernel, el kernel verifica **autorización**, el *manager* correspondiente coordina el recurso, y las **interrupciones** avisan cuando el dispositivo termina, mientras el procesador se reparte entre los demás procesos.
