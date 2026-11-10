# Clase 10 — Almacenamiento SSD y administración de archivos (File Manager)

**Curso:** IIIC2026 - Sistemas Operativos, LEAD University

**Docente:** Mario Miguel Agüero Obando

**Fecha:** 9 de noviembre de 2026 (estimada por continuidad semanal respecto a la Clase 9; en la grabación solo se menciona que se está en la semana 10)

**PDF fuente:** `8 - SSD.pdf` (6 diapositivas) y `9 - Administración de Archivos.pdf` (30 diapositivas).

**Cobertura del PDF:**

- SSD: Completo (diapositivas 1 a 6). Pendiente de la Clase 9.
- Administración de archivos: Parcial, diapositivas 1 a 29 de 30 (hasta «Módulo de Control de Acceso», listas de control de acceso y grupos). La diapositiva 30 (listas de capacidad) queda para la siguiente clase. Las diapositivas 24 y 25 («Conexión File Manager – Device Manager») no se proyectaron como tal y salen solo del PDF; las diapositivas 28 y 29 (códigos de bits y lista de control de acceso) solo se tocaron de forma conceptual.

**Nota sobre la transcripción:** incluye muchas tangentes (anécdotas laborales, series, fútbol, matrícula) que no aportan contenido. Términos mal reconocidos corregidos por contexto: «Fine/Final Manager» = File Manager, «la FAC o la ex» = FAT o ext, «yunix / Linux Ionics» = Unix, «llave maya» = llave USB (memoria flash), «juicios» = quizzes, «smooth» = chmod, «Ruth» = root, «btris» = B-trees, «Charlie Piti» = ChatGPT, «D o s» = DOS.

**Contexto.** Se cierra el material de almacenamiento con los SSD (por qué guardan datos sin energía y por qué son tan rápidos) y se abre el cuarto manager del SO: el **File Manager**. Se ve qué es, qué le puede pedir un proceso, cómo se organiza un volumen (descriptor, MFD, directorios, entradas), cómo se guardan los archivos físicamente (contiguo, enlazado, indexado) y cómo se controla quién accede a qué.

---

## Ruta de la clase

| Bloque | Tema | PDF y diapositivas |
|--------|------|--------------------|
| — | Calificaciones y logística (ver «Fuera del PDF») | — |
| 1 | Almacenamiento SSD | SSD, 2–6 |
| 2 | File Manager: responsabilidades, uso y comandos | Archivos, 2–6 |
| 3 | Conceptos básicos y configuración de un sistema de archivos | Archivos, 7–15 |
| — | Receso | — |
| 4 | Organización de archivos | Archivos, 16–19 |
| 5 | Almacenamiento físico y métodos de acceso | Archivos, 20–23 |
| 6 | Conexión File Manager – Device Manager (solo PDF) | Archivos, 24–25 |
| 7 | Módulo de control de acceso | Archivos, 26–29 |

---

## 1. Almacenamiento SSD (SSD, diapositivas 2–6)

### Origen y costo (diapositiva 2)
- Los *Solid State Drive* crecieron en paralelo a las memorias USB («llaves»). La barrera fue el **costo**; desde ~2012 bajó y, con la miniaturización, se volvieron accesibles.
- Referencia: en 2008, cambiar la mitad de los servidores de un cliente a SSD costaba ~$125 000; en 2016 se migró **todo** por ~$20 000 y con más capacidad.

### Tecnología (diapositivas 3–4)
- Los circuitos de almacenamiento son, en esencia, **los mismos que los de la RAM**: **compuertas lógicas** que guardan 1 bit. La figura de la diapositiva es un *latch* hecho con compuertas **NAND** (AND con negación: da 0 solo si todas las entradas son 1).
- **Diferencia clave:** la RAM necesita electricidad constante; al perderla, sus transistores vuelven al estado de fábrica y todo queda en cero. La memoria **flash** usa transistores con un **aislamiento** que atrapa la carga y **conserva el estado** (el 1 o el 0) sin corriente. Sin ese aislamiento, la carga se disiparía por el circuito.
- La RAM sigue siendo más rápida; el SSD es no volátil.

> **Nota:** es una simplificación. En la práctica la celda flash tiene una compuerta aislada («flotante») que retiene la carga, y la DRAM se basa en capacitores; la idea de fondo (transistores como unidad de 1 bit) es la misma.

### Tipos (diapositivas 5–6)
- **mSATA / SATA3 y los primeros SSD:** memoria flash **montada sobre los protocolos de los discos mecánicos** (cajas que se atornillaban). Popularizaron la tecnología, pero estaban limitados por esos conectores.
- **PCIe / NVMe (M.2):** tarjetas del tamaño de una tarjeta de crédito alargada que se conectan directo al bus. Siguen siendo SSD: **cambia el conector, no la tecnología**. Teóricamente hasta **16 Gbit/s**.
- El límite teórico no se alcanza en la práctica: más líneas implican más electricidad (fuente más potente) y más calor.

### Por qué un SSD le gana a un disco mecánico
- Se elimina la **parte mecánica**: no hay giro, cabeza que mover ni cálculo de pista/sector.
- Con cabeza fija o móvil, si dos pedazos de un archivo quedan en puntos distintos, hay que esperar a que el disco dé (casi) una vuelta completa. En un SSD el archivo vive en una memoria con **direccionamiento directo**: se pide la dirección y en el siguiente ciclo de reloj empiezan a bajar los datos.
- Los SO han cambiado su parte lógica para acceder a los archivos casi como si estuvieran en RAM.
- **El SSD no exime al SO de saber dónde guarda cada cosa.** Sigue siendo responsable de ubicar y encontrar los archivos: de eso se encarga el File Manager, pase lo que pase con el dispositivo (mecánico, SSD o incluso un disquete).

---

## 2. Administración de archivos y File Manager (Archivos, diapositivas 2–6)

### Qué es (diapositiva 2)
- El **File Manager** guarda y organiza los archivos, vigila sus accesos y mantiene su seguridad. Trabaja de la mano del Device Manager, que administra el acceso de los procesos a los dispositivos de almacenamiento.
- Es el «hermano» del Device Manager: fue **la primera necesidad** (administrar discos) y de él nació el Device Manager completo; hoy está subordinado a este pero es un manager por sí mismo, muy importante aunque poca gente sepa que existe.
- **No es el *File Explorer* de Windows ni el *Finder* de Mac.** Esos son interfaces de usuario (*shells*) que dan acceso a algunas funciones, igual que el *Task Manager* de Windows no es el administrador de procesos ni el *Device Manager* de Windows es el administrador de dispositivos.

### Responsabilidades (diapositiva 3)
- Registrar **dónde** está cada archivo.
- Definir la **política** de dónde y cómo almacenarlos (depende del sistema de archivos configurado: FAT16/32 en Windows, ext2/3/4 en Linux…).
- **Localizar** un archivo y dar acceso solo si el usuario fue validado.
- **Liberar** un archivo que ya no se usa.
- **Proteger** los archivos de errores del sistema: si una operación se interrumpe, no deben quedar corruptos.
- Marcar los archivos **en uso**: por eso no se puede borrar un archivo que está abierto. Al cerrarlo se quita la marca. Conviene **cerrar los archivos lo antes posible** para evitar este tipo de bloqueos en cadena.

### Cómo se usa (diapositiva 4)
- Es un programa que **responde a comandos**: un «mayordomo» que espera órdenes.
- Los procesos le envían los comandos y reciben una respuesta. Ejemplo: al dar doble clic a un documento de Word, el SO abre el proceso Word, este pide el archivo al File Manager («ábrame ese archivo de ese directorio»), el File Manager confirma y empieza a entregarle los datos.

### Comandos comunes y abstracción (diapositivas 5–6)
- **Create** (o *Open New*), **Open**, **Delete**, **Rename**, **Copy**.
- Los comandos de terminal (`copy`, `delete`, `move`…) son otra forma de acceder a estas funciones. `move` no copia los datos: **cambia el path** del archivo.
- Los comandos **no especifican elementos físicos**, solo la ubicación lógica (el path). Da igual si el destino es un disco mecánico, un SSD, una llave USB o una ruta de red.
- Esa es la **abstracción** del sistema de archivos: no hace falta saber superficie, pista, cilindro ni sector. Sin File Manager, cada programa tendría que programar su propia forma de leer archivos.

---

## 3. Conceptos básicos y configuración de un sistema de archivos (Archivos, diapositivas 7–15)

### Campo, registro, archivo (diapositivas 7–8)
- **Campo:** grupo de bytes identificable como un dato. **Registro:** conjunto de campos relacionados. **Archivo:** conjunto de registros.
- Ejemplo de los archivos de datos antiguos: nombre en 20 caracteres, apellido en 20… cada campo de tamaño fijo y cada registro del mismo tamaño. Un CSV sigue la misma idea: cada línea es un registro y cada campo está separado por coma.
- **Base de datos:** conjunto de archivos relacionados e interconectados a varios niveles. **Program files:** archivos con instrucciones y datos de un programa. **Directorio (carpeta):** conjunto de archivos y sus atributos. **Volumen:** unidad que contiene archivos.

### Descriptor de volumen y MFD (diapositivas 9–10)
- Cada volumen tiene un **identificador**: `C:`, `D:`, `E:` en DOS/Windows; algo como `/dev/hdd` en Unix/Linux. Esto aplica igual a discos mecánicos o SSD.
- Esa identificación se escribe al **inicio** de la unidad en el **descriptor de volumen** (su «cédula»), que contiene: fecha de creación, puntero al área de directorios, puntero al área de archivos, código del sistema de archivos (para detectar volúmenes con formato incorrecto) y nombre del volumen.
- Después viene el **Master File Directory (MFD)**: la lista de **todos** los archivos y directorios del volumen, sin importar su tipo, con las direcciones de dónde está cada uno. Los primeros SO solo permitían un directorio por volumen.
- Los **subdirectorios** son registros con una **bandera especial** que indica al File Manager que no son un archivo sino una carpeta. Nacieron con los SO **multiusuario**, para separar los archivos de cada usuario (un subdirectorio por usuario).

### Estructura de árbol y entrada de archivo (diapositivas 11–12)
- Para ubicar archivos y subdirectorios se usan estructuras de **árbol**, en concreto variantes del **B-tree**. Un *path* es realmente una **secuencia de nodos del árbol**.
- Cada archivo tiene en su directorio una **entrada** con:
  - Nombre (**único** dentro de cada directorio).
  - Tipo (archivo real o subdirectorio).
  - Tamaño (para no recalcularlo leyendo).
  - Ubicación física (dónde están sus bloques).
  - Fecha y hora de creación/modificación.
  - Derechos de acceso (seguridad).
  - Tamaño de los registros.

### Nombre, extensión y path (diapositivas 13–15)
- **Longitud del nombre:** en DOS y hasta Windows NT 3.5 regía el formato **8.3** (8 caracteres de nombre relativo, un punto y 3 de extensión). Luego, hasta Windows 10, hasta 260 caracteres; hoy más de 32 000. Con 8.3 había que inventar códigos para nombrar los archivos y luego nadie recordaba qué significaban.
- Lo estandarizado hoy: el nombre tiene **dos partes**, el **nombre relativo** (lo que diferencia al archivo; cada SO tiene sus reglas) y la **extensión**.
- La **extensión** es una convención del SO para indicar si es ejecutable (`.sh` en Linux/Mac) o a qué programa se asocia (`.doc`/`.docx` con Word). Esa asociación es solo **configuración del SO**. Algunas extensiones están restringidas (`.SYS`, `.BAT`, `.COM` en DOS/Windows); casi solo `.com`, `.bat` y `.exe` están amarradas al SO.
- **La extensión y el ícono son ayudas para el ser humano, no para el archivo.** Si se cambia la extensión de un Excel a `.xyz`, el SO advierte que podría quedar inutilizable, pero al abrirlo con Excel funciona igual: al programa solo le importa que el contenido tenga el formato correcto. Algunos programas rechazan extensiones no esperadas, pero es una medida preventiva. Si un archivo no tiene extensión asociada, el SO ofrece «abrir con…» una lista de programas porque no sabe cuál usar.
- Muchos formatos tienen estructura interna propia. Ejemplo: un `.docx` renombrado a `.zip` se abre como archivo comprimido y muestra sus carpetas de estilos y el documento en **XML**; un PDF renombrado a `.zip` en cambio falla («formato desconocido»).

> **Nota:** esto vale para los formatos modernos de Office (`.docx`, `.xlsx`), que son paquetes ZIP con XML. El antiguo `.doc` no es un ZIP.

- **Path:** la ruta lógica en el volumen para ubicar un archivo. No se considera parte del nombre porque los comandos son **relativos al directorio base**, el **working directory** (donde trabaja el usuario o el proceso); aun así el File Manager lo maneja. El path no incluye el nombre del archivo.

---

## 4. Organización de archivos (Archivos, diapositivas 16–19)

### Registros de tamaño fijo y variable (diapositivas 16–18)

| Tipo | Ventajas | Desventajas | Uso típico |
|------|----------|-------------|------------|
| **Fijo** | Cálculo de posición y recuperación sencillos | **Desperdicio** de espacio (p. ej. 30 bytes reservados para guardar 1); no se puede cambiar el tamaño | Archivos de datos |
| **Variable** | Reduce mucho el desperdicio | Más difícil de ubicar | Archivos que se leen **secuencialmente** |

- Ejemplo de registros variables: los **ejecutables**. Tienen un **encabezado** de formato fijo y luego registros con la información del programa, que le permiten al SO cargar segmentos y páginas.
  - Los `.com` de DOS eran código binario puro (tamaño máximo de 64 KB) y se ejecutaban directamente; los `.exe` tienen encabezado con las secciones y cómo organizar el programa en memoria, y pueden superar los 64 KB.
  - Otro ejemplo es el JPEG, que comienza con un encabezado y un marcador fijo.

> **Nota:** el marcador `FF D8` del JPEG es el de inicio de imagen (*Start Of Image*) y está al comienzo del archivo; no marca un punto posterior al encabezado.

- Casi cualquier archivo puede verse como una **secuencia de registros que son secuencias de campos**.

### Formas de guardar la información en disco (diapositiva 19)
- **Secuencial:** la más sencilla de leer y escribir (propia de las cintas), pero el mantenimiento se complica si hay que **modificar registros en puntos aleatorios**.
- **Directa:** se guardan partes del archivo en segmentos y bloques específicos, así que un archivo puede quedar **distribuido en varias partes**: aparece la **fragmentación**. Complica registrar dónde está cada parte; normalmente se usa **hashing**.
- **Indexada:** la más usada hoy. Para cada archivo se crea un **índice de acceso** con la lista de ubicaciones físicas de sus registros. Costo: leer implica además consultar los índices para saber dónde leer y dónde seguir. Muchos formatos y bases de datos también tienen índices internos hacia otras secciones.
- **Fragmentación:** lo ideal es que cada archivo quede continuo. En discos mecánicos eso es costoso de mantener, así que se permite guardar donde haya espacio y **después** se corre un desfragmentador que reordena los pedazos. Se prefirió así porque era más fácil de programar: permitir el problema y arreglarlo después, que prevenirlo. En SSD ya no tiene sentido por no haber partes mecánicas.

---

## 5. Almacenamiento físico y métodos de acceso (Archivos, diapositivas 20–23)

### Contiguo vs. no contiguo (diapositiva 20)
- **Almacenamiento continuo:** los primeros SO ponían un archivo detrás de otro (cintas magnéticas). Es sencillo y compacto, pero si un archivo cambia de tamaño no hay dónde crecer.
- Hoy se usa **almacenamiento no contiguo**, que va de la mano de la estructura indexada: se aprovecha cualquier espacio libre del disco y los segmentos del archivo se enlazan.

### Extensiones: enlazado vs. indexado (diapositivas 21–22)
- Cada parte de un archivo se llama **extend** o **extensión**.
- **Enlazado (primer enfoque):** cada bloque guarda dentro de sí el puntero al siguiente (el archivo 1 empieza en el bloque 2, sigue en el 8, luego en el 20, luego en el 18; sin puntero = último bloque). Aprovecha bien el espacio, pero el **acceso directo** a un punto del archivo **se complica**: hay que leer un bloque para saber cuál sigue.
- **Indexado:** el puntero **sale del bloque** y pasa a la tabla del directorio, que guarda por cada pedazo su dirección, tamaño y el siguiente. Ejemplo: el archivo 2 ocupa los bloques 3, 6 y 11; la tabla lo dice de entrada.
  - Con una sola consulta a la tabla se obtienen **todas las direcciones** y se piden **de un solo tiro**. En un SSD, con su gran ancho de banda, llegan juntos y el sistema los ordena. En un disco mecánico habría que esperar vueltas.
  - Por eso la tendencia moderna es indexar: secuencial obliga a moverse más; indexado permite acceso directo.

### Métodos de acceso (diapositiva 23)
- El método de acceso depende del método de almacenamiento.
- Como los procesos pueden **interrumpirse** (round robin, Clase 3), el File Manager guarda siempre la **última dirección accedida**, el **CBA** (*Current Byte Address*). Si un proceso que lee un archivo grande se interrumpe a mitad, al volver el SO sabe que le falta la otra mitad y la pide a partir de esa dirección.

---

## 6. Conexión File Manager – Device Manager (Archivos, diapositivas 24–25; solo PDF)

El File Manager baja por capas hasta el Device Manager:

| File Manager | → | Device Manager |
|--------------|---|----------------|
| Sistema de archivos (abstracción de más alto nivel) | | |
| Módulo de control de acceso (seguridad) | | |
| Sistema lógico de archivos (estructura lógica) | → | Sistema físico de archivos → interfaz del dispositivo → dispositivo |

- Según la organización de los archivos, el sistema lógico calcula las **direcciones exactas** y se las comunica al sistema físico; de ahí, vía Device Manager, se llega a la interfaz particular del dispositivo y al dispositivo mismo.

---

## 7. Módulo de control de acceso (Archivos, diapositivas 26–29)

### Por qué existe (diapositiva 26)
- Los primeros SO no podían compartir archivos entre usuarios. Al compartirlos hay que mantener la **integridad**: no se puede escribir mientras otro lee, ni dos procesos escribir a la vez.
- Todos los SO implementan una **matriz de control de accesos**: quién puede hacer qué sobre cada archivo.

### Matriz de acceso (diapositivas 27–28)
- Filas = archivos, columnas = usuarios; cada celda indica **R**ead, **W**rite, **E**xecute, **D**elete (p. ej. `R-E-`, `RWED`, `----`).
- Es fácil de implementar pero ocupa espacio y trabajo extra de almacenamiento. En la práctica se codifica con **bits**: `R-E-` = 1010, `RWED` = 1111, `----` = 0000.
- Esos códigos binarios son el equivalente de los códigos numéricos de `chmod` en Linux (el taller de la Clase 9).

> **Nota:** en Unix cada permiso son 3 bits (r, w, x) para dueño, grupo y otros, y cada trío se escribe como un dígito octal: 7 = 111 = `rwx`, 5 = 101 = `r-x`.

### Lista de control de acceso (diapositiva 29)
- Alternativa: para **cada archivo** se lista qué usuarios tienen acceso y de qué tipo (más `WORLD` para el resto).
- Permite usar **grupos** (administradores, usuarios finales…), lo que **ahorra espacio**. Es el esquema más popular entre los SO.
- Unix/Linux incorporó el usuario y también el **grupo de usuarios**, con `root` como administrador; Windows tardó mucho en incorporar este concepto.

### Seguridad: Unix vs. Windows
- Salida de `ls -l` en Linux, columna por columna: tipo (`d` = directorio), permisos en tríos (dueño, grupo, otros; `r`, `w`, `x`), enlaces, dueño, grupo, tamaño, fecha y hora, nombre.
  ```text
  drwxr-xr-x. 2 root root 4096 ... nombre
  ```
- En Unix/Linux la **seguridad está en el diseño** desde el inicio. En Windows se arrastró la debilidad de DOS, donde quien usaba la máquina tenía acceso a todo, incluso al kernel; estabilizar y aislar eso tomó décadas.
- Consecuencia práctica: en Linux hay que pedir permisos de administrador para instalar o cambiar el sistema. Cuando los programadores trabajan siempre como administrador, sus programas terminan **exigiendo** permisos totales, y bastaba infectarlos para tener acceso a todo. Por eso hoy se desarrolla con un **usuario normal** además del administrador, para que el software funcione sin privilegios de más.

> **Nota:** la matriz de control de acceso es un concepto general; lo propio de Unix es su modelo dueño/grupo/otros. Windows adoptó después un modelo similar de usuarios, grupos y permisos.

---

## Conceptos clave

- **SSD:** celdas flash de transistores con aislamiento que conservan el estado sin energía; sin partes mecánicas y con direccionamiento directo. PCIe/NVMe (M.2) cambia el conector, no la tecnología. El SO sigue necesitando saber dónde guarda cada cosa.
- **File Manager:** cuarto manager del SO; responde a comandos (create, open, delete, rename, copy); no es el File Explorer. Registra dónde está cada archivo, valida accesos, marca archivos en uso y protege de errores.
- **Abstracción:** los comandos usan paths lógicos; el File Manager se encarga de superficie/pista/sector y funciona igual con cualquier dispositivo o red.
- **Campo → registro → archivo;** base de datos = archivos interconectados; directorio = archivos + atributos; volumen = unidad con archivos.
- **Volumen:** descriptor de volumen (id, punteros, código de sistema de archivos) + **MFD**; subdirectorios = registros con bandera especial; estructura de árbol tipo B-tree; la entrada de cada archivo guarda nombre único, tipo, tamaño, ubicación, fechas, permisos.
- **Nombre y extensión:** la extensión es una ayuda humana y una configuración del SO, no una propiedad del archivo; el formato interno es lo que importa (`.docx` = ZIP con XML). Path relativo al *working directory*.
- **Registros fijos** (fáciles de ubicar, desperdician) vs. **variables** (ahorran, se leen secuencialmente).
- **Secuencial / directa / indexada:** hoy domina la indexada; la fragmentación se corrige con desfragmentación en discos mecánicos.
- **Enlazado vs. indexado:** puntero dentro del bloque vs. punteros en la tabla del directorio, que permiten pedir todos los bloques de una vez.
- **CBA:** última dirección accedida, para retomar tras una interrupción.
- **Control de acceso:** matriz (archivo × usuario, bits RWED), lista de control de acceso por archivo y grupos de usuarios; Unix lo tuvo desde el diseño y Windows lo heredó tarde.

---

## Fuera del PDF — logística, tareas y metodología

### Calificaciones
- **Tareas programadas 1 y 2** ya calificadas; en general hubo buenos resultados y mejoras visibles respecto a la primera.
- **Errores frecuentes** (útiles para la Programada 3): dejar **fijo en el código el nombre del archivo** en lugar de leerlo desde la línea de comandos, omitir el análisis pedido y olvidar un entregable.
- Las entregas hechas por fuera del aula virtual (por OneDrive, con justificación) aún no estaban calificadas: pueden verse con **cero** de forma temporal en el primer corte y se califican en el siguiente.

### Evaluación y entregas
- **Primer corte de notas:** al día siguiente de la clase, con los talleres 1 y 2, las tareas programadas 1 y 2 y los primeros quizzes. Un segundo corte saldría a inicios de la semana siguiente.
- **Programada 3:** fecha límite el lunes siguiente (16 de noviembre de 2026, estimada). Se asignará otra tarea programada después.
- **Quizzes pendientes:** faltan algunos enlaces; se publicará un **formulario de repaso** que valga por los que se deben.
- **Material por subir al aula virtual:** la presentación de administración de archivos y una simulación (generada con IA) sobre la asignación de archivos.
- **Notas finales:** el docente estima subirlas hacia mediados de diciembre de 2026 (estimación suya, no oficial).
