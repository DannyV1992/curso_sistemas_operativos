# Clase 9 — Discos de cabeza movible, subsistema de E/S, arranque y estructura de discos, y USB

**Curso:** IIIC2026 - Sistemas Operativos, LEAD University

**Docente:** Mario Miguel Agüero Obando

**Fecha:** 2 de noviembre de 2026 (estimada por continuidad semanal respecto a la Clase 8; no se menciona explícitamente en la transcripción)

**PDF fuente:** `7 - Administracion de Dispositivos.pdf` (26 diapositivas), `8 - Arranque y estructura de DD.pdf` (13 diapositivas) y `8 - USB.pdf` (10 diapositivas).

**Cobertura del PDF:**

- Administración de dispositivos: Parcial, diapositivas 16 a 26 de 26 (desde «Acceso directo (4)», cabeza movible, hasta «Buffers»). Con esto el PDF queda **completo**; las diapositivas 1 a 15 se vieron en la Clase 8 y solo se repasaron.
- Arranque y estructura de discos: Completo (diapositivas 1 a 13).
- USB: Completo (diapositivas 1 a 10). Las diapositivas 7 a 9 (funcionamiento, USB Stack y tipos de transferencia) no se mencionan en la transcripción y salen solo del PDF.
- `8 - SSD.pdf` **no** se cubrió; queda pendiente.

**Nota sobre la transcripción:** incluye anécdotas sobre cintas, disquetes y series antiguas, y tangentes sobre BSD que no aportan contenido de estudio. Términos mal reconocidos corregidos por contexto: «x2/x3/x4» = ext2/ext3/ext4, «máster bus record» = Master Boot Record, «bus ladder» = bootloader, «fdisc» = fdisk, «vertical software distribution» = Berkeley Software Distribution, «hci» = Host Controller Interface, «schmuck» = chmod.

**Contexto.** Se cierra la unidad de dispositivos. Tras un repaso de los tipos de dispositivos y del almacenamiento secuencial y de cabeza fija (Clase 8), se completan los discos de acceso directo, se ve cómo la CPU se comunica con los dispositivos (canales, unidades de control, buffers), cómo se organiza un disco y cómo arranca una computadora, y por qué USB simplifica todo. Al inicio se presentan los **Talleres 3 y 4** (ver «Fuera del PDF»).

---

## Ruta de la clase

| Bloque | Tema | PDF y diapositivas |
|--------|------|--------------------|
| — | Talleres 3 y 4 (ver «Fuera del PDF») | — |
| — | Repaso: Device Manager, tipos de dispositivos, cintas y cabeza fija | Dispositivos, 1–15 (Clase 8) |
| 1 | Discos de cabeza movible y ópticos | Dispositivos, 16–20 |
| 2 | Subsistema de E/S: analogía del taxi, canales y unidades de control, Channel Status Word, buffers | Dispositivos, 21–26 |
| — | Receso | — |
| 3 | Conceptos de almacenamiento, organización física vs. lógica, File Manager, FAT, particiones, ext2/3/4 | Arranque, 2–10 |
| 4 | Disco booteable y proceso de booteo | Arranque, 11–13 |
| 5 | USB | USB, 1–10 |

---

## 1. Discos de acceso directo: cabeza movible y ópticos (Dispositivos, diapositivas 16–20)

### Cabeza movible: los discos duros (diapositivas 16–18)
- Son los **discos duros** (HDD) tradicionales. Varios platos se apilan en una estructura **cilíndrica**; hay **una cabeza de lectura/escritura por superficie** (un disco de 3 platos tiene 6 superficies y 6 cabezas) y un brazo mueve todas las cabezas a la vez.
- Las cabezas **no tocan** la superficie: detectan los unos y ceros por atracción magnética. Sin contacto no hay fricción, así que son **más rápidos y duran más** que los de cabeza fija.
- Al poder hacer las pistas más finas, la capacidad crece mucho (diskettes de 1,44 MB frente a discos de 20–60 MB, y luego más con la miniaturización).
- **Pista (*track*):** anillo de una superficie; el *track* 0 normalmente es el más externo.
- **Cilindro:** conjunto de las pistas del **mismo número** en todas las superficies, vistas verticalmente. Es una abstracción que permite pedirle al hardware un cilindro y una superficie concretos.
- Para acceder a un dato se necesita: **número de cilindro, superficie a leer y número de sector**. El **sector** es el bloque de datos que se lee o escribe.
- Cuando el disco se apaga, las cabezas se «parquean» en una zona segura; los primeros discos exigían un comando para parquearlas antes de apagar.
- Frente al problema de cabeza fija (esperar vueltas), aquí el brazo se **desplaza** a la pista y el tiempo de espera típico es de **media vuelta** del disco.

### Discos ópticos (diapositivas 19–20)
- Usan tecnología **láser** (CD, DVD): mucho menos contacto físico, mayor velocidad y capacidad.
- Se organizan en **espiral**: hay **un solo *track*** con sectores del mismo tamaño. El hardware ajusta la velocidad de lectura según se lea cerca del centro o del borde.
- **Tasa de transferencia elevadísima y tiempo de acceso bajísimo**, pero son fundamentalmente **secuenciales**: su rendimiento cae si los datos están fragmentados. Por eso el software para quemar CD/DVD «monta» primero la secuencia completa a escribir.

---

## 2. Subsistema de entrada/salida (Dispositivos, diapositivas 21–26)

### Analogía de la compañía de taxis (diapositivas 21–22)
- Los dispositivos de E/S forman el **subsistema de E/S**.
- Llegan muchas solicitudes de toda la ciudad; un **operador** asigna el taxi óptimo. Hay distintos tipos de vehículos (limosinas, vans, colectivas) guardados en un taller donde un **mecánico** indica cuáles están listos. El operador pide un vehículo al mecánico y el chofer hace el servicio.
- Antes los taxis esperaban en paradas o garajes; la idea es la misma: despachar rápido sin que el solicitante lidie con cada vehículo.
- Correspondencia sugerida: cliente = proceso que pide E/S; operador = Device Manager; mecánico = quien lleva el estado (libre/ocupado) de los dispositivos; vehículos = dispositivos.

### Canales y unidades de control (diapositiva 23)
Este fue el punto donde se **le quitó a la CPU el manejo directo de los datos**. En vez de conectar la CPU a cada disco, cinta o diskette, aparecen dos piezas:

| Pieza | Función |
|-------|---------|
| **Canal de E/S (*I/O channel*)** | Comunica la CPU con las unidades de control. Antes era un único bus de E/S; la especialización exigió más coordinación, que dan las unidades de control |
| **Unidad de control (*I/O control unit*)** | Recibe las instrucciones y ejecuta las acciones con el dispositivo. Hoy una unidad puede tener varios dispositivos a cargo |

- La CPU solo envía órdenes («mándeme este dato al disco») y **se desentiende**: es como hacer una encomienda. Por eso la CPU queda más liviana.
- Hoy estas funciones viven en los **chips (chipset) de la tarjeta madre**. Antes, cada dispositivo (mouse, etc.) venía con una tarjeta donde se instalaba el *driver* que administraba su unidad de control.

### Comunicación entre dispositivos (diapositiva 24)
El Device Manager debe saber:
- Qué componentes están **ocupados y cuáles libres** (lo más fácil).
- Cómo **organizar las solicitudes** cuando hay muchas.
- Cómo **coordinar el acceso a datos** entre CPU y E/S.

Cada unidad del subsistema puede terminar su trabajo **independientemente** de las demás (una impresora no espera a otra), y la CPU puede **seguir procesando** mientras espera eventos de E/S.

### Channel Status Word y direcciones de memoria (diapositiva 25)
- A cada dispositivo se le asigna un **área de memoria** con su identificador y su estado (*Channel Status Word*): ocupado, libre, etc. Normalmente se controla por **interrupciones**.
- Cada dispositivo también tiene una **dirección de memoria**: para recibir datos de él, el SO indica a la CPU que lea esa dirección; para enviarle datos, el canal los deposita en ella. Esa zona sirve de buzón en ambos sentidos.
- Ejemplo visto en el Administrador de dispositivos (pestaña de detalles del *driver*): el teclado y la cámara muestran la **misma dirección** porque cuelgan de la misma expansión USB; un disco duro muestra otra.
- **DMA** (*Direct Memory Access*): los datos viajan del dispositivo de E/S **directo a la RAM**, sin pasar por la CPU.

### Buffers (diapositiva 26)
- Son bloques de memoria intermedios que **absorben la diferencia de velocidad** entre dispositivos, memoria y CPU: guardan datos mientras el componente más lento va desocupando.
- Casi todo dispositivo tiene uno (teclado, mouse…); el más grande de una computadora suele ser la **cola de impresión**, que guarda todos los trabajos pendientes.

---

## 3. Conceptos de almacenamiento y estructura lógica (Arranque, diapositivas 2–10)

### Conceptos básicos (diapositiva 2)
- Cada superficie se divide en **pistas** (los ópticos solo tienen una); cada pista en **sectores** que guardan la misma cantidad de datos.
- **Cluster:** conjunto de sectores consecutivos en la misma pista.

### ¿Cómo se administra? Formateo y sistemas de archivos (diapositiva 3)
- Los programas solo piden «lea X archivo» o «escriba Y archivo»; el SO oculta pistas, sectores y superficies.
- **Formatear** un disco es dividirlo en sectores lógicos según el sistema de archivos del SO: FAT (12, 16, 32) y NTFS en Windows; ext2, ext3, ext4 en Linux. Como la organización es distinta, un disco de un SO no se ve de forma nativa en el otro (hoy ya es casi transparente por software).

### Organización física vs. lógica (diapositiva 4)

| Concepto | Aspecto físico | Aspecto lógico |
|----------|----------------|----------------|
| Unidad mínima | **Sector** (la unidad física más pequeña) | **Cluster** (conjunto de sectores consecutivos) |
| Dirección | Coordenadas: plato (superficie), cilindro, cabeza, sector | **Sistema de archivos**: estructura jerárquica |
| Gestión | Circuitería | **Tabla de asignación** (FAT en DOS/Windows) o **inodes** (Unix/Linux) |

- Ejemplo: un archivo de 29 bytes aparecía antes como de «4K» en el listado, porque el SO debe reservar el cluster completo aunque no lo llene (igual que con páginas o particiones de memoria). Los SO actuales muestran el tamaño real, pero el espacio reservado sigue siendo el cluster.
- Las cabezas lidian con superficies, pistas y sectores; el usuario solo lidia con el **sistema de archivos** (carpetas, tablas de asignación, inodes).

### File Manager (diapositiva 5)
- Es el **cuarto manager** del SO (Processor/Process, Memory, Device y File Manager). Trabaja con el Device Manager, pero se encarga de las operaciones sobre archivos y de conservarlos.
- Abstrae el hardware con una estructura jerárquica, guarda **información sobre los archivos** (en Unix, en estructuras separadas llamadas **inodes**), mantiene la integridad de los datos y permite organizarlos.

### FAT (diapositiva 6)
- Pensado originalmente para los PCs y los discos *floppy*. Primero fue FAT8; la primera versión amplia fue **FAT12**, seguida de **FAT16** y **FAT32** (la usada hasta hace poco).
- Una FAT es una **tabla de listas enlazadas** con las posiciones de los clusters de cada archivo (dónde está cada pedazo).
- El número (8, 12, 16, 32) indica el **límite de clusters** direccionables: $2^8 < 2^{12} < 2^{16}$.
- Si el disco era mayor que la capacidad de la FAT, era **inutilizable** (solo se usaba hasta donde alcanzaba la FAT) o había que **crear particiones**.

### Particiones (diapositivas 7–8)
- Una **partición** es una región administrada por separado; es como tener **otro disco** aunque sea la misma unidad física (otro caso de dispositivo virtual). Es la forma natural de aprovechar discos que crecen más rápido que lo que el SO sabe administrar.
- En PCs DOS/Windows lo usual es **una sola partición** con todo: SO, archivos, utilitarios, memoria virtual.
- En Unix/Linux hay **dos tipos**: la de **sistema de archivos** y la de **swap**.
  - Cada directorio puede montarse en su propia partición, lo que **minimiza el riesgo de pérdida** de información (es más complicado al inicio, pero más seguro).
  - La partición de **swap** es donde el SO mueve la memoria de procesos que no necesita en RAM; está optimizada para entrar y sacar datos de memoria y es **parte de la clave de velocidad** de Linux. macOS usa varios **archivos** de swap en lugar de una partición.

### ext2, ext3 y ext4 (diapositivas 9–10)
- **ext2:** sistema de archivos básico de Linux, basado en el *Berkeley Fast File System* de **BSD** (*Berkeley Software Distribution*, una versión de Unix muy influyente cuyo código no pudo difundirse por disputas de licencia con AT&T). En él la metadata de cada archivo (seguridad, permisos…) vive en **inodes** y cada volumen es una unidad aparte. Límite: archivos de menos de 2 GB y menos de 32 000 directorios.
- **ext3:** reemplazó a ext2, mejoró la integridad de los datos y redujo la fragmentación (el problema de los pedazos «inalcanzables»), pero se criticó por **lento**.
- **ext4:** permite archivos descomunales y es más veloz, pero se critica su integridad de datos (sin casos críticos conocidos) y tiene problemas con el **borrado de datos** (inseguro).

---

## 4. Disco booteable y proceso de booteo (Arranque, diapositivas 11–13)

### ¿Cómo hacer un disco booteable? (diapositivas 11–12)
- Sin importar el tipo de unidad (flash, disco duro, diskette, CD, SSD), su **primer sector es booteable si contiene la dirección donde está el SO**, es decir, el comando que «prende» el kernel.
- Ese primer sector es el **MBR** (*Master Boot Record*). Además contiene un **programa que sabe cargar el arranque del SO en la RAM**. La BIOS (memoria física de la tarjeta madre) lo busca y lo ejecuta.
- Por eso, al formatear o particionar hay que hacer una **partición booteable**, aunque hoy los programas lo hacen solos.
- **`fdisk`** es una herramienta genérica que acompaña a casi todo SO para listar y editar particiones. En su salida, un **asterisco** bajo «Boot» (p. ej. `/dev/sda1 *`) marca la partición booteable. Es **muy peligrosa** si no se sabe lo que se hace.
  - En algunos Linux viejos solo la primera partición puede ser booteable; en otros se puede elegir entre varias.

> **Nota:** el asterisco marca la partición **activa**; el MBR en sí reside en el primer sector del disco.

### Proceso de booteo (diapositiva 13)
1. Se enciende la computadora y la BIOS busca el **primer sector** del disco (MBR).
2. Se carga el **bootloader**, el puente entre hardware y software.
3. El bootloader **carga el kernel**, que toma control total del equipo.
4. Se cargan los **dispositivos** y luego los **programas**. Listo.

---

## 5. USB (USB, diapositivas 1–10)

### Qué es y por qué es popular (diapositivas 2, 5)
- **Universal Serial Bus:** estándar para conectar dispositivos. La «S» es de *serial*: lo serial es más rápido que lo paralelo; nació de la proliferación de puertos y formatos vista en la Clase 7.
- Razones de su popularidad: **plug and play** (surge a mediados de los 90; antes había que apagar, editar archivos de configuración y reiniciar), **alta velocidad** y **suministro de energía** por el mismo cable.
- Modos de transferencia: **doble vía** (envío y recepción a la vez) o **unilateral**. Velocidades desde **12 Mbps** (USB 1.1) hasta **5 Gbps ~ 40 Gbps** en las versiones 3.x. Contrapartida: más dispositivos significa más energía, gasto y calor.

### Conectores y colores (diapositivas 3, 6)
- **Tipo A:** rectangular estándar. **Tipo B:** más voluminoso, para equipos que requieren conexión más segura (impresoras, webcams, discos externos). **Tipo C:** reversible, transfiere datos y energía. **Micro-USB:** móviles. **Mini-USB:** antiguo, cada vez menos común.
- Los conectores tipo A de 3.0 se ven distintos a los de 2.0.
- El **color del puerto** indica la versión: **blanco = 1.x**, **negro = 2.x**, **azul = 3.x**; el rojo es *always active* (da energía aun con el equipo apagado). Para máxima velocidad, conectar al puerto 3.0.

### El truco de USB: un solo canal (diapositivas 4, 7)
Recuerda el esquema de canales y unidades de control (sección 2): con USB hay **un único canal** y el **HCI** (*Host Controller Interface*) hace de unidad de control.

- Hay una unidad de control por puerto o conjunto de puertos (traseros, frontales…). El HCI **detecta** el dispositivo, lo **enumera** (le asigna un canal virtual o **pipe** y obtiene su descripción: fabricante, tipo, capacidades), asigna recursos y actúa como tráfico de datos.
- El SO busca el *driver* automáticamente y los datos se intercambian según lo que el controlador permite.
- La computadora **cree** que cada dispositivo tiene su propio canal, pero físicamente es **uno solo**: el HCI va dando turno («ahora fluye usted, ahora fluye usted») sin que el SO pierda tiempo. **La fuerza de USB está en el hardware.** Analogía: una bomba de presión que absorbe o envía datos por muchas cañerías administradas por el HCI.
- Tipos de HCI (cada uno controla un número limitado de dispositivos):

| Controlador | Para |
|-------------|------|
| **UHCI** | Dispositivos de baja velocidad |
| **EHCI** | Alta velocidad |
| **XHCI** (*eXtensible*) | Velocidades extremas de las últimas versiones |

### USB Stack (diapositiva 8)
Capas del *host*: SO anfitrión → *USB driver* → *HC driver* → *host controller* → **SIE** (*Serial Interface Engine*), que empuja o absorbe los bits desde y hacia el dispositivo por el cable.

### Cuatro tipos de transferencia (diapositiva 9)
| Tipo | Uso |
|------|-----|
| **Control** | Conversación entre el SO/*driver* y el dispositivo |
| **Interrupción** | Acceso a las interrupciones del sistema (teclado, mouse) |
| **Bulk** | Grandes volúmenes de datos (almacenamiento) |
| **Isocrónica** | Tiempo real (audio, video) |

### ¿Cuántos dispositivos? (diapositiva 10)
- Límite teórico: **127** (varía según controladores y SO). Récord práctico conocido: **111**, con teclados, limitado en la práctica por la energía disponible.

> **Nota:** en la grabación se menciona una cifra cercana a 120 teclados; la diapositiva indica 111.

---

## Conceptos clave

- **Cabeza movible:** una cabeza por superficie sin contacto físico; el **cilindro** agrupa las pistas del mismo número; el acceso exige cilindro + superficie + sector.
- **Disco óptico:** una sola pista en espiral, láser, muy rápido pero secuencial; sufre con la fragmentación.
- **Canal y unidad de control:** la CPU solo envía órdenes; el canal comunica con las unidades de control, que operan los dispositivos. Cada dispositivo tiene un área de memoria con su estado (*Channel Status Word*) y una dirección de memoria; **DMA** lleva datos directo a la RAM.
- **Buffer:** memoria intermedia que absorbe diferencias de velocidad; el mayor es la cola de impresión.
- **Sector (físico) vs. cluster (lógico):** el SO reserva clusters completos; la gestión usa FAT o inodes.
- **File Manager:** cuarto manager del SO; maneja la estructura jerárquica y la integridad de los archivos.
- **FAT:** tabla de listas enlazadas de clusters; el número (12/16/32) limita los clusters direccionables.
- **Partición:** región tratada como un disco aparte; Linux separa sistema de archivos y **swap**.
- **ext2 → ext3 → ext4:** basado en BSD FFS; más integridad, menos fragmentación, más tamaño y velocidad, con críticas de lentitud (ext3) y seguridad de borrado (ext4).
- **Booteo:** MBR (primer sector) → bootloader → kernel → dispositivos → programas. `fdisk` es peligroso.
- **USB:** un único canal, HCI por puerto (UHCI/EHCI/XHCI) que asigna canales virtuales (*pipes*); plug and play, energía incluida; colores blanco/negro/azul = 1.x/2.x/3.x; 127 dispositivos teóricos.

---

## Fuera del PDF — logística, tareas y metodología

### Taller 3 — cambiar la versión de Java con un script
- **Plazo:** 16 de noviembre de 2026, antes de la medianoche (unos 15 días desde la clase). Se entrega en el aula virtual; los espacios de entrega de los dos talleres se publican por separado. Son los **dos últimos talleres** del curso.
- **Motivación:** conviven versiones de un lenguaje (Java cambia de versión cada seis meses; hay quien mantiene programas en Java 8 y otros proyectos en Java 21). Se necesitan varias configuraciones instaladas, de las cuales solo una está **activa**.
- **Qué hacer:** en WSL (Windows) o en macOS, instalar varias versiones de Java (p. ej. 11, 17 y 21; mínimo dos máquinas virtuales, de preferencia tres) y escribir un **script `.sh`** (hecho ejecutable) que, al ejecutarlo, **cambie la versión activa**; se verifica con `java -version`. Instalación en Linux con `apt install` de los JDK.
- **Pistas del docente:** investigar `chmod`, el comando `update-alternatives` (y la relación con el script) y las **variables de entorno**.
- **Entregables:** documento que explique qué se aprendió de `chmod`, cómo se hizo el script y para qué sirve `alternatives`, más **evidencia** de que funciona. Quien use macOS lo tiene algo más fácil por tener terminal propia.

### Taller 4 — monitoreo de memoria con carga de datos
- **Plazo:** cuatro semanas desde la clase (≈ 2 de diciembre de 2026). Es más largo: no dejarlo para la última semana.
- **Material provisto:** dos scripts de Python, `generar_datos` (crea un archivo del tamaño en GB indicado, p. ej. `--size 50 --output datos50`) y `analizar_datos`, y los comandos de monitoreo para Linux/WSL y macOS.
- **Procedimiento:**
  1. Generar varios archivos de prueba (p. ej. 10, 20 y 30 GB; quien tenga más recursos, 20, 40 y 80). **No** se incluyen en el entregable.
  2. Usar **dos terminales** (dos WSL): en una se ejecuta el monitoreo y en la otra `analizar_datos`.
  3. El monitoreo debe repetirse periódicamente (cada ~10 s), ejecutar los comandos provistos y **guardar toda la salida** en archivos (no solo verla en pantalla).
- **Qué miden los comandos:** memoria virtual en uso, operaciones de swapping (entrada/salida de páginas), procesos activos y consumo de CPU, y **presión de memoria** (cuánta de la disponible se usa).
- **Dos modos de `analizar_datos`:** **full** (carga todo en memoria) y **chunks** (lee por pedazos). Ejecutar cada modo con los **mismos datos**, al menos 4 veces y de preferencia 6, alternando full / chunks, guardando los resultados.
- **Análisis pedido:** uso de memoria virtual, swapping, presión de memoria y correlación con procesos; interpretar los resultados y comparar cómo se comporta realmente el equipo en cada modo.
- **Se valora la creatividad:** parametrizar los nombres de archivo, extraer los datos con `grep`, apoyarse en IA (cuidando los tokens), etc.

> **Nota:** `cron` no ejecuta tareas con una frecuencia menor a un minuto; para repetir cada 10 s conviene un ciclo con `sleep` o un script que se invoque a sí mismo.

### Otras entregas y siguiente clase
- **Quiz de dispositivos:** se publica en el campus esa misma noche.
- **Pendiente de esta unidad:** `8 - SSD.pdf` no se vio en clase.
- **Próxima clase (lunes):** redes y seguridad.
