# Clase 8 — Administración de dispositivos y dispositivos de almacenamiento

**Curso:** IIIC2026 - Sistemas Operativos, LEAD University

**Docente:** Mario Miguel Agüero Obando

**Fecha:** 26 de octubre de 2026 (estimada por continuidad semanal respecto a la Clase 7; no se menciona explícitamente en la transcripción)

**PDF fuente:** `7 - Administracion de Dispositivos.pdf` (26 diapositivas) y, para la actividad inicial, `6 - Buses Memoria y Procesos.pdf` (diapositiva 13).

**Cobertura del PDF:**

- Administración de dispositivos: Parcial, diapositivas 1 a 15 de 26 (hasta «Dispositivos de Acceso directo (3)», la ubicación de los datos en discos de cabeza fija). Desde la diapositiva 16 («Acceso directo (4)», discos de cabeza movible) queda para la siguiente clase, junto con la organización del subsistema de E/S y la comunicación entre dispositivos.
- Buses: se resolvió la actividad de la diapositiva 13 (pendiente de la Clase 7).

**Nota sobre la transcripción:** incluye ~40 min de trabajo en grupos (sin audio útil), un receso de ~25 min y varias tangentes (herramientas de software, hosting, anécdotas de programación antigua, asuntos personales) que no aportan contenido de estudio. Términos mal reconocidos corregidos por contexto: «PSI» = PCI, «a G p» = AGP, «Besa» = VESA, «pata» = PATA, «halp dúplex» = half dúplex, «The Frac» = defrag, «chel» = shell, «Loadisket» = diskette, «process manager» = Processor Manager.

**Contexto.** Tras el bloque de procesos y memoria, el curso pasa a los **dispositivos**: cómo el SO controla el hardware de entrada/salida y almacenamiento. Se cierra primero la actividad de buses de la clase anterior y luego se ve el **Device Manager**, los **tipos de dispositivos** y el inicio de los **dispositivos de almacenamiento** (secuenciales y de acceso directo).

---

## Ruta de la clase

| Bloque | Tema | PDF y diapositivas |
|--------|------|--------------------|
| — | Tarea Programada 3 y Examen 1 (ver «Fuera del PDF») | — |
| 1 | Actividad en grupos: repaso de buses | Buses, 13 |
| — | Receso | — |
| 2 | Enfoque y Device Manager | Dispositivos, 2–4 |
| 3 | Tipos de dispositivos: dedicados, compartidos, virtuales | Dispositivos, 5–8 |
| 4 | Almacenamiento secuencial (cintas) | Dispositivos, 9–12 |
| 5 | Almacenamiento de acceso directo: cabeza fija | Dispositivos, 13–15 |

---

## 1. Actividad en grupos: repaso de buses (Buses, diapositiva 13)

Cuatro preguntas respondidas en grupo y discutidas en plenaria.

### ¿Por qué SATA es más rápido que PATA?
- **ATA** = *Advanced Technology Attachment*; **PATA** = *Parallel* ATA y **SATA** = *Serial* ATA. Ambos conectan discos duros (HDD) y SSD.
- SATA envía los bits uno tras otro a alta velocidad por un único canal; PATA usa señalización en paralelo (muchos bits a la vez).
- Idea clave: **lo serial es más rápido que lo paralelo**.

### ¿Qué fueron VESA y AGP, y por qué AGP superó a VESA?
- **VESA** fue un *local bus* de los 90 para tarjetas de video. **AGP** (*Accelerated Graphics Port*) se creó específicamente para tarjetas gráficas: más rápido, con mejor manejo de gráficos de videojuegos y programas 3D.
- De VESA solo sobreviven los conectores de video rectangulares (DisplayPort).

### Diferencias entre PCI y PCI Express
| | **PCI** | **PCI Express** |
|---|---------|-----------------|
| Transmisión | Paralela, **bus compartido** | **Serial**, conexión por **carriles** |
| Ancho de banda | 133 MB/s | Desde 250 MB/s hasta varios GB/s (según carriles y versión) |
| Dirección | Half dúplex | Full dúplex |

- **Half dúplex:** comunicación en ambos sentidos, pero no a la vez; como un carril reversible que sirve a un sentido a la vez.
- **Full dúplex:** ambos sentidos **simultáneamente**.
- Al explicar términos técnicos, tener lista una respuesta corta y simple; si faltan las palabras, apelar a ideas como «comunicación bidireccional».

### Puertos usados históricamente
- **COM/serial** (módems, ratón), **LPT/paralelo** (impresoras), **PS/2** (teclado y ratón), **VGA** (monitor), puerto de **joystick**.
- Luego **USB** (varios dispositivos en un mismo puerto) y **FireWire** (cámaras, transferencia de datos).
- Dentro del equipo, conexiones específicas para discos duros y unidades de CD/DVD.
- Tendencia: pasar de lo paralelo a lo serial y buscar **bidireccionalidad**. Más bidireccionalidad aumenta el problema de **sincronización** (quién llega primero, notificaciones que rebotan de ida y vuelta), un tema de diseño de software fuera del curso.

---

## 2. Enfoque y Device Manager (Dispositivos, diapositivas 2–4)

### Enfoque de la unidad (diapositiva 2)
Conceptos generales → tipos de dispositivos → introducción a los dispositivos de almacenamiento → organización de los dispositivos de E/S → comunicación entre dispositivos.

### El Device Manager (diapositiva 3)
- Así como hay un administrador de procesos y uno de memoria, el SO tiene un **Device Manager** que interactúa con los buses especializados y los dispositivos.
- Es un **proceso propio del SO** y habita en el **kernel** (la parte con acceso a todo el computador).
- **No confundir** con la ventana «Administrador de dispositivos» de Windows (ni su equivalente en Linux): esa es una **interfaz** que se comunica con el Device Manager real, que permite ver cosas y hacer algunas acciones (deshabilitar un dispositivo, por ejemplo), pero no es el Device Manager.
- Analogía: el tacómetro y el pedal de un carro permiten interactuar con el motor, pero no son el motor. La relación es la misma que entre el *shell* y el kernel.

### Funciones del verdadero Device Manager (diapositiva 4)
- **Administra y mantiene en equilibrio** el uso de los recursos de los dispositivos del sistema.
- **Monitorea el estatus** de cada dispositivo (libre u ocupado).
- **Colabora con el Processor Manager** para saber qué proceso usa un dispositivo y por cuánto tiempo.
- **Asigna recursos físicos** al dispositivo.
- **Libera** los recursos cuando el proceso termina o cuando ocurre una **interrupción** (teclado, mouse, fin de una operación de E/S), o bien los libera permanentemente.
- Es el «encargado de los tenedores» del problema de los filósofos (Clase 7): debe evitar que un proceso **acapare** un recurso de forma permanente.

---

## 3. Tipos de dispositivos (Dispositivos, diapositivas 5–8)

Aunque los dispositivos cambian mucho, se clasifican según el **uso que les da el Device Manager**: dedicados, compartidos y virtuales.

| Tipo | Quién lo usa | Ventaja / problema | Ejemplos |
|------|--------------|--------------------|----------|
| **Dedicado** | Un solo proceso a la vez | Fácil de administrar (se tiene o no se tiene); si hay mucha demanda se forman **colas de espera** | Teclado, impresora, plotter, respaldos en cinta |
| **Compartido** | Varios procesos a la vez | Evita esperas, pero genera **competencia** y **conflictos de prioridad**, que son clave | Disco duro, audífonos |
| **Virtual** | Dedicado convertido en compartido mediante *wrappers* | Combina ambos | Cola de impresión, USB |

### Dedicados (diapositiva 6)
- El proceso debe **terminar o liberar** el dispositivo para que otro lo use.
- Ejemplo del teclado: lo escrito va solo al programa que tiene el **foco**. Al cambiar de ventana, el Device Manager reasigna el teclado; si el teclado fuera compartido, lo tecleado en Word aparecería también en el Bloc de notas.
- La impresora es un dispositivo dedicado que igual debe atender a muchos usuarios (comprar una por documento no es viable), de ahí la cola.

### Compartidos (diapositiva 7)
- Ejemplo: dos navegadores reproduciendo canciones distintas por los mismos audífonos suenan a la vez; también el disco duro.
- El teclado puede actuar como compartido en ciertos eventos: la tecla Windows interactúa con el *shell* y no con el programa en primer plano (funciona como una interrupción).
- El punto crítico es la **competencia**: dos procesos con máxima prioridad pidiendo el mismo dispositivo. Los conflictos de uso deben resolverse.
- Los SSD simplificaron mucho esta administración frente a los discos mecánicos.

### Virtuales (diapositiva 8)
- Un dispositivo virtual convierte uno dedicado en compartido por medio de *wrappers* que manejan usuarios y procesos.
- **Cola de impresión:** no existe como pieza de hardware; es un **espacio de memoria** donde esperan los trabajos hasta que la impresora se libere. Un *print server* es un computador con una impresora conectada que la comparte con toda una red.
- **USB:** a nivel de implementación es una «superautopista» única con canales para cada dispositivo (mouse, llaves, discos). El **controlador USB** administra el acceso al bus y el intercambio de datos.

---

## 4. Dispositivos de almacenamiento (Dispositivos, diapositivas 9–12)

- Son los dispositivos **más clásicos** que requieren control del SO. Antes eran muy limitados, por lo que su operación era clave: **con ellos nació el Device Manager**.
- Hasta los años 90 se dividían en dos tipos: **secuenciales** y de **acceso directo**.

### Almacenamiento secuencial: cintas (diapositivas 10–12)
- Cintas magnéticas (*tapes*). Los registros solo se acceden por **su posición en la cinta**, por lo que se necesitan **registros de tamaño homogéneo** y **calcular posiciones**.
- Localizar, insertar, etc. es de complejidad **O(N)**. **Insertar** casi no se hacía: se copiaba la cinta a otra intermedia y se intercalaba el dato nuevo durante la copia, para evitar sobrescribir registros.
- Capacidades: carretes de 5 a 140 MB; luego cartuchos y casetes (desde los 80) de hasta 500 GB. Hoy existen cintas de ~1 TB, usadas en aplicaciones muy específicas (típicamente **mainframes** de IBM) y fabricadas casi por demanda.
- **Desgaste físico:** el cabezal debe tocar la cinta, y el desgaste significa costo. Por eso las cintas se rotaban de forma preventiva (se anotaba la fecha de apertura y el número de respaldos, y se reemplazaban antes de llegar a la tasa de falla conocida).
- La transferencia estaba **físicamente limitada**.
- Resumen: eran rápidas, buenas y las más económicas de su época, pero con **acceso lineal** y **desgaste**.

---

## 5. Dispositivos de acceso directo (Dispositivos, diapositivas 13–15)

- Se conocen como **DASD** (*Direct Access Storage Devices*): pueden leer o escribir en un **lugar específico**. Son casi como una **tabla hash física**.
- Tipos: discos magnéticos de **cabeza fija**, discos magnéticos de **cabeza movible** y **discos ópticos**.
- **Concepto clave de todos: la pista o *track***. Se imagina como la pista de atletismo, no la autopista.

### Discos de cabeza fija (diapositivas 14–15)
- Los datos se guardan en pistas y hay **una cabeza fija por cada pista**: cada cabeza lee solo su pista.
- El disco gira y las cabezas leen o escriben cuando el dato pasa frente a ellas. Los datos se guardan **serialmente en cada pista**.
- Son como un LP antiguo: un solo disco. Muy rápidos, pero de **almacenamiento limitado** y con el mismo problema de **desgaste** de las cintas. Se usan en dispositivos espaciales o muy específicos; los más modernos evitan el contacto físico.

> **Nota:** la diapositiva pone a los diskettes como ejemplo de cabeza fija; en la práctica, las unidades de diskette usan una cabeza móvil.

### Peor escenario de ubicación de los datos (diapositiva 15)
- Un archivo puede guardarse **en varias partes**, no necesariamente contiguas, y cada parte puede estar en una pista distinta (leída por una cabeza distinta).
- Si el dato que se necesita acaba de pasar frente a la cabeza, hay que **esperar una vuelta completa** del disco. Con el archivo repartido en varias pistas, cada fragmento ya pasado cuesta **otra vuelta**.
- Eso explica los programas **defrag** (desfragmentación) de los discos mecánicos: reubican los fragmentos de cada archivo de modo que queden **seguidos** y no haga falta esperar vueltas completas.
- Al borrar, quitar y meter archivos una y otra vez, el disco se llena de pedazos y el sistema se vuelve cada vez más lento hasta desfragmentar (se hacía cada ~6 meses).

---

## Conceptos clave

- **Device Manager real vs. ventana de Windows/Linux:** el real es un proceso del kernel; la ventana es solo una interfaz hacia él.
- **Funciones del Device Manager:** equilibrar recursos, monitorear estatus, coordinar con el Processor Manager, asignar recursos físicos y liberarlos (por fin de proceso o interrupción).
- **Dispositivo dedicado / compartido / virtual:** un proceso a la vez (con cola) / varios a la vez (con competencia y prioridades) / dedicado convertido en compartido mediante *wrappers* (cola de impresión, USB).
- **Almacenamiento secuencial:** cintas; acceso por posición, O(N), desgaste físico; hoy casi solo en mainframes.
- **DASD (acceso directo):** lectura/escritura en un lugar específico; concepto central: la **pista (*track*)**.
- **Cabeza fija:** una cabeza por pista; rápido, poco almacenamiento, desgaste.
- **Fragmentación en disco mecánico:** esperar vueltas completas; se corrige con **defrag**.
- **Half dúplex vs. full dúplex:** un sentido a la vez vs. ambos simultáneos. **Serial** supera a **paralelo** (SATA/PATA, PCI Express/PCI).

---

## Fuera del PDF — logística, tareas y metodología

### Tarea Programada 3 (simulador de particiones fijas)
- **Plazo:** 15 días a partir de la clase (≈ 10 de noviembre). Se entrega en el aula virtual (menú izquierdo, sección «Entregas»). Es más fácil que las anteriores y tiene una parte de análisis.
- **Qué hacer:** simular la administración de memoria con **particiones fijas** de tamaño distinto (ejemplo: 120, 300, 200 y 500 KB = 1120 KB), con interacción por consola (no se lee de archivo). Cada partición tiene id único, tamaño en KB, estado (libre/ocupada) y proceso asignado. No se crean, dividen ni redimensionan particiones durante la simulación.
- **Procesos:** id único, tamaño, estado (esperando, en memoria, finalizado) y partición asignada. Cada proceso ocupa **una sola partición**, aunque la suma de espacios libres alcance.
- **Estrategias** (a elegir por el usuario, implementadas por separado):
  - **First Fit:** primera partición libre, en orden de definición, donde quepa. Ejemplo: proceso de 180 KB → partición de 300 KB.
  - **Best Fit:** la partición libre más ajustada; en empate, la de menor id. Mismo ejemplo → partición de 200 KB.
- **Cola de espera:** un proceso que no cabe en ninguna partición libre espera en orden de llegada y se reintenta cada vez que se libera una partición. Un proceso mayor que cualquier partición también queda en cola y nunca podrá asignarse.

> **Nota:** el enunciado escrito indica que un proceso mayor que la partición más grande debe ser **rechazado** por imposibilidad de asignación, no encolado. Conviene seguir el enunciado y confirmarlo con el docente.

- **Visualización:** tabla con partición, tamaño, estado, proceso y memoria no utilizada. En las ocupadas esa columna es **fragmentación interna**; en las libres es capacidad disponible.
- **Estadísticas mínimas:** memoria total, memoria utilizada por procesos, memoria libre, fragmentación interna, % de utilización efectiva (utilizada ÷ total × 100) y cantidad de procesos en espera. Debe cumplirse: **total = utilizada + fragmentación interna + libre**.
- **Ejemplo del enunciado** (P1 180, P2 110, P3 250 KB): First Fit da fragmentación interna total de 380 KB; Best Fit, 80 KB. Best Fit no siempre es mejor.
- **Menú:** configurar particiones, seleccionar estrategia, crear/asignar proceso, finalizar proceso, consultar particiones, consultar cola, estadísticas, reiniciar y salir. La configuración y la estrategia van antes de asignar procesos y no cambian durante la simulación.
- **Restricciones:** solo bibliotecas básicas de Python, sin compactación, sin intercambio con disco, sin mover procesos entre particiones, validar tamaños > 0 e ids de proceso activos no repetidos.
- **Pruebas obligatorias (8 escenarios):** cabe exacto; cabe en varias; no cabe en ninguna libre; mayor que toda partición; todas ocupadas; liberar permite asignar uno en espera; memoria libre total suficiente pero ninguna partición individual sirve; First y Best Fit asignan distinto.
- **Entregables:** código fuente comentado y un documento breve (PDF) con estructuras de datos, explicación de ambos algoritmos, evidencias (capturas) y comparación de resultados. El documento debe responder: por qué First/Best Fit aplican a particiones fijas, por qué el espacio sobrante no se reutiliza, cuándo Best Fit genera más fragmentación, si puede haber memoria libre suficiente sin poder asignar, y el impacto de repartir procesos entre varias particiones.
- **Evaluación:** modelado 15 %, First/Best Fit 25 %, gestión de procesos y cola 25 %, estadísticas 15 %, validaciones y pruebas 10 %, documento y calidad del código 10 %.

### Examen 1 (4 preguntas, para llevar a casa)
- **Plazo:** 8 días (≈ 3 de noviembre). Entrega en el campus, en un solo documento, de preferencia **PDF**.
- **Metodología:** primero responder con las propias ideas, dudas y partes que no se entienden; luego usar una **IA como coach** (pegar pregunta y respuesta, pedir qué está mal y qué ampliar), **compartir su respuesta** y desarrollar las ideas nuevas. Lo que se evalúa es la **evolución del razonamiento**.
- **Preguntas:**
  1. Implicaciones de agregar páginas o segmentos a las simulaciones de las dos tareas programadas (algoritmos y cambios necesarios; incluir ventajas y desventajas). Si no se tienen ideas, decirlo.
  2. Por qué con la segmentación desaparece la importancia de First Fit y Best Fit.
  3. Opinión sobre la universalización de interfaces vía USB y problemas derivados.
  4. Administración de memoria y de procesos en SO móviles: primero plantear por qué importa el contexto móvil (p. ej. menos memoria), luego investigar y concluir qué se aprendió o sorprendió.

### Otras entregas y siguiente clase
- **Tarea Programada 2:** el plazo se movió al **jueves de esa semana (29 de octubre), a medianoche**; no habrá más prórroga.
- **Actividad de buses:** documento grupal con los nombres de todos los integrantes.
- **Cuestionario de repaso de la semana:** se publica en el campus.
- **Próxima clase (lunes):** terminar los discos duros (cabeza movible, cilindros, sectores, discos ópticos) y ver cómo funcionan los puertos USB.

### Pendientes de clases anteriores (no se retomaron)
- **PDF 3, diapositiva 16:** punto 3 (Próximo a terminar), punto 5 (Round Robin con quantum 5) y punto 6 (Round Robin con regla de ≤ 2 ciclos).
- **PDF 4, diapositiva 12:** qué estrategia (First Fit o Best Fit) aplica la figura del ejemplo.
