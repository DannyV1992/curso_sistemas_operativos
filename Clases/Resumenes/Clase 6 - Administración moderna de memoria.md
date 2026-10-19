# Clase 6 — Administración moderna de memoria: paginación, segmentación y memoria virtual

**Curso:** IIIC2026 - Sistemas Operativos, LEAD University
**Docente:** Mario Miguel Agüero Obando
**Fecha:** 12 de octubre de 2026 (estimada por continuidad semanal respecto a la Clase 5; no se menciona explícitamente en la transcripción)
**PDF fuente:** `5 - Administracion Moderna de Memoria.pdf` (22 diapositivas). Los ejercicios del inicio se revisan con `5 - Administracion de memoria - drawio.pdf` (3 páginas con las soluciones de las diapositivas 18–20 de `4 - Administracion de Memoria.pdf`).
**Cobertura del PDF:** Completo (diapositivas 1 a 22). No se saltó ninguna diapositiva; los puntos de la diapositiva 22 (ventajas de la memoria virtual) salen solo del PDF.
**Nota sobre la transcripción:** hay un receso de ~30 min a media clase y varias tangentes (fútbol, problemas con Microsoft Forms, historia del hardware) que no aportan contenido de estudio. Hay términos mal reconocidos que se corrigieron por contexto (p. ej. «Roll Robin» = Round Robin, «FIFA» = FIFO, «cuarto» = quantum, «Live resionly used» = Least Recently Used, «soap» = swap, «escoci» = SCSI, «Abraham/Bran» = RAM). Algunas afirmaciones técnicas del docente se aclaran en notas.

**Contexto.** La sesión resuelve los ejercicios de particiones de la Clase 5 y presenta cómo se administra la memoria hoy: en lugar de cargar procesos completos en cajas de tamaño fijo, se dividen en **páginas** y **segmentos** y solo se carga lo necesario, apoyándose en el disco (**memoria virtual**). Además se asigna la Tarea Programada 2 (Round Robin).

---

## Ruta de la clase

| Bloque | Tema | Diapositivas |
|--------|------|--------------|
| 0 | Repaso: ejercicios de particiones (Clase 5) | — (PDF 4, 18–20) |
| 1 | Justificación y tendencias | 2–3 |
| 2 | Paginación de memoria | 4–10 |
| 3 | Páginas por demanda, swapping y políticas de sustitución | 11–15 |
| 4 | Segmentación de memoria | 16–18 |
| 5 | Páginas segmentadas por demanda y memoria asociativa | 19–20 |
| 6 | Memoria virtual y papel del hardware | 21–22 |

---

## 0. Repaso: ejercicios de particiones (PDF 4, diapositivas 18–20)

Mismos eventos en los tres ejercicios: llegan A(5) y B(15); C(30) y D(14); E(40) y F(16); termina A; llegan G(8) y H(9); terminan C y E; llegan I(4), J(8) y K(18); terminan F y G.

| Esquema | Cómo se resuelve | Qué muestra |
|---------|------------------|-------------|
| **Fijas** (2 de 10 K, 4 de 20 K, 2 de 50 K) | Cada proceso va a una partición libre donde quepa: A→10, B→20, C→50, D→20, E→50, F→20. G y H ocupan las dos de 10; I→20 (la única libre), J y K→las dos de 50 | Mayor **fragmentación interna**: K (18 K) y J (8 K) en particiones de 50 K desperdician 32 K y 42 K |
| **Dinámicas** (múltiplos de 5) | El tamaño del proceso se redondea hacia arriba a múltiplo de 5 (D: 14→15, F: 16→20). Al terminar un proceso queda un hueco, pero **las particiones no se mueven** | G y H (10 K cada una) no caben en el hueco de 5 K que dejó A y van al final. Quedan huecos dispersos: **fragmentación externa** |
| **Dinámicas relocalizables** | Igual, pero al terminar un proceso se **compacta**: todos suben y el espacio libre queda en un solo bloque | I, J y K no pueden usar los huecos viejos: se agregan tras el último proceso. Al final el orden es B, D, H, I, J, K sin huecos |

- Para dibujar: usar como unidad de cuadro el divisor común de los tamaños (aquí 5 K) y duplicar la escala si hace falta.
- El desperdicio de una partición es tamaño de la partición − tamaño del proceso. En fijas, los procesos pequeños en particiones grandes (J, K) dominan la fragmentación interna; K usa solo 18 de 50 K.
- En un examen se puede pedir reconstruir el escenario y calcular quién desperdicia más espacio asignado.
- La compactación es la solución más simple y la que se impuso: hubo intentos de esquemas «más inteligentes», pero resultaron más difíciles que juntar todo a un lado y liberar el otro.

> **Nota:** en clase se habló de «6 unidades» de desperdicio para D; con la partición de 15 K el desperdicio es de 1 K.

---

## 1. Justificación y tendencias (diapositivas 2–3)

- El **multiprocesamiento** exige un manejo de memoria más complejo; la demanda de memoria de un proceso **no se puede prever** (siempre piden más); y se necesitan varios procesos corriendo a la vez.
- A esto se suma que la RAM siempre ha sido limitada (por costo o disponibilidad), lo que obliga a ser «creativos». Hoy un programa pequeño puede manejar muchos datos (listas, procesamiento intensivo), y las cajas de tamaño fijo se vuelven un obstáculo.
- Cuatro grandes tendencias, cada una evolución de la anterior:
  1. **Paginación.**
  2. **Páginas por demanda.**
  3. **Segmentación.**
  4. **Páginas segmentadas por demanda**, fundamento de la **memoria virtual moderna**.

---

## 2. Paginación de memoria (diapositivas 4–10)

### Idea
- Al cargarse, el programa se divide en partes llamadas **páginas**, que se cargan en **page frames** (marcos de página) de la memoria principal. Ya no hay particiones de tamaño variable, sino marcos fijos del tamaño de una página.
- La tendencia es que **página = bloque de memoria = sector de disco** (mismo tamaño), lo que facilita mover información entre ellos. Origen: en los discos duros mecánicos (HDD) solo se podía leer un bloque fijo por vez, así que se dividían los programas en páginas de ese tamaño. Es un ejemplo de cómo el hardware condiciona el diseño del SO.
- Al ejecutar un programa, el Memory Manager: (1) determina cuántas páginas necesita, (2) localiza marcos libres y (3) carga el programa ahí.
- **Las páginas no quedan contiguas ni en orden** en memoria.
- Compiladores y SO evolucionaron juntos: el compilador genera en el binario estructuras que facilitan identificar páginas y segmentos.

| Ventaja | Desventaja |
|---------|------------|
| Uso más eficiente de la memoria: desaparece la fragmentación externa y la interna se limita a la **última página** del proceso | El Memory Manager se complica: debe saber dónde está cada parte. Es de las piezas más difíciles de escribir de un SO |

- **Tamaño de página:** de él depende el éxito del modelo. Un tamaño que sirve para ciertos procesos puede no servir para otros.
- Ejemplo (diapositiva 6): un proceso de 350 K con páginas de 100 K ocupa 4 páginas (3 completas y una de 50 K con 50 K desperdiciados), cargadas en marcos no consecutivos (8, 10, 5 y 11). Aquí empieza a verse la diferencia entre lo **lógicamente disponible** y lo **físicamente disponible**: el SO puede contar 700 K disponibles aunque haya 750 K libres.

### Tablas del Memory Manager (diapositivas 7–8)
En lugar de flechas, el Memory Manager usa tres tablas (los nombres varían entre SO):

| Tabla | Contenido |
|-------|-----------|
| **Job Table** | Por cada proceso activo: su tamaño y la posición en la Page Map Table donde está guardado |
| **Page Map Table (PMT)** | Lista consecutiva de las páginas de cada proceso: número de página y dirección de inicio |
| **Memory Map Table** | **Todas** las páginas/marcos de la memoria y su estado (libre u ocupado) |

- Ejemplo: Job 1 empieza en la entrada 150 de la PMT; las entradas 150–153 guardan las direcciones de sus cuatro páginas (800, 1000, 500, 1100). La Memory Map Table marca 0 y 100 como ocupadas (SO), 200–400 libres, 500 ocupada (página de Job 1), etc.
- La Memory Map Table dice **qué marcos están libres**; la PMT dice **dónde está cada página del proceso**; la Job Table dice **dónde empieza la PMT del proceso**.

### Desplazamiento (*offset*) y resolución de dirección (diapositiva 9)
- La memoria guarda datos e instrucciones, y el SO debe poder llegar a un byte o palabra concretos dentro de una página, no solo a la página.
- El **offset** es cuántos bytes (o palabras) hay que avanzar desde el inicio de la página para llegar al dato o instrucción:

$$\text{dirección física} = \text{dirección de inicio de la página} + \text{offset}$$

- Las direcciones de las páginas son **lógicas** (relativas); el SO las convierte a **físicas** cada vez que necesita una instrucción o dato. Este proceso se llama **resolución de dirección** (*address resolution*).
- Al construir compiladores y SO hay que considerar si la memoria es direccionable por byte, el tamaño del bus, de la palabra y de los registros.
- Ejemplo cotidiano: los mensajes de error de memoria de Windows reportan una dirección y un desplazamiento dentro de ella.

---

## 3. Páginas por demanda y memoria virtual (diapositivas 11–15)

### Idea (diapositivas 11–12)
- **Cargar en memoria solo la parte del programa que el proceso requiere.** Fue el primer modelo que eliminó la idea de cargar todo el programa. Las páginas restantes quedan en disco y se traen cuando se necesitan.
- Aprovecha la ejecución secuencial de la arquitectura de Von Neumann. Los procesos necesitan **menos memoria**, y de aquí nace la **memoria virtual**.
- Ejemplo: en un procesador de texto, casi todo el tiempo se escribe y no se usan las funciones de dibujo o referencias; su código se trae del disco a la memoria solo la primera vez que se abre esa pestaña. En equipos viejos se nota como una pausa al usar funciones complejas.
- Es posible gracias a **buses** rápidos entre CPU y almacenamiento (IDE, SCSI, PCI Express; memorias flash/USB). Los primeros discos necesitaban una tarjeta controladora en una ranura; con IDE el controlador pasó al propio disco y la transferencia se disparó (luego SATA y PCIe).
- Para que funcione, los datos deben moverse **rápido** entre RAM y almacenamiento físico. Ese intercambio es el **swapping**; las **políticas de swapping** definen cómo se hace. Con muchas aplicaciones abiertas (p. ej. Chrome) se nota cuando el equipo trae páginas del disco.
- Dónde vive la memoria virtual: en **Windows** es un archivo configurable (Propiedades del sistema → Rendimiento → Opciones avanzadas); en **Linux** es una **partición swap** dedicada, definida al instalar (unos 4 GB suelen bastar).

### Cambios en las tablas (diapositivas 13–14)
Solo cambia la PMT, que gana tres campos:

| Campo | Para qué sirve |
|-------|----------------|
| **Estado** (en memoria: Y/N) | Si la página no está en memoria y se necesita, se inicia la operación de *swap* |
| **Modificada** | Si hubo cambios, hay que reescribirla en disco al sacarla. Si es solo código sin cambios, se descarta sin guardar |
| **Referenciada** (accedida recientemente) | Si no se ha leído ni escrito en los últimos turnos de CPU, es mejor descargarla |

- Cada entrada de la PMT lleva entonces: página, estado, referenciada, modificada y número de marco. Ejemplo (diapositiva 14): Job 4 tiene 6 páginas; P0–P2 están en memoria (marcos 6, 13 y 15) y P3–P5 no (estado N).
- Cada campo agregado complica más al Memory Manager.

### Políticas de sustitución de páginas (diapositiva 15)
Cuando falta una página en memoria (**fallo de página**) hay que decidir cuál sacar:

| Política | Criterio | Características |
|----------|----------|-----------------|
| **FIFO** (First In/First Out) | Sale la página con **más tiempo cargada**, como una cola | Muy simple; tiende a dar muchos fallos en programas largos |
| **LRU** (Least Recently Used) | Sale la página **menos accedida** en los últimos momentos | Prioriza el uso; hay varias variantes y se pueden combinar con FIFO; más difícil de implementar, pero es la más usada |

---

## 4. Segmentación de memoria (diapositivas 16–18)

- Se origina en aprovechar la **modularización** del software (bibliotecas, módulos, componentes, objetos, subrutinas). Al estar el código dividido en módulos, el compilador o intérprete identifica qué partes usa cada programa, y solo esas se cargan; el resto queda en memoria virtual.
- Cada proceso se divide en **segmentos de tamaños distintos** (programa principal, subrutina A, subrutina B…). La memoria **no se divide en marcos**: desaparece el concepto de página. **Requiere trabajo de los compiladores.**
- Ejemplo: de una biblioteca de unos 120 K de la que solo se usa una parte, se carga solo el segmento necesario (p. ej. 60 K).
- El Memory Manager sabe qué segmentos pertenecen al programa en ejecución y cuáles se relacionan entre sí (el principal puede llamar a la subrutina A).
- Para **cada proceso** mantiene una **Segment Map Table** (reemplaza a la PMT) con: número de segmento, tamaño, estado (en memoria Y/N), acceso (E = solo ejecución) y dirección en memoria. Ejemplo (diapositiva 18): programa principal de 350 K (Y, dirección 4000), subrutina A de 200 K (Y, 7000) y subrutina B de 100 K (N, no cargada).
- **Problema:** aumenta mucho la **fragmentación externa**, porque los segmentos son de tamaño variable y dejan huecos como las particiones dinámicas.

> **Nota:** en clase se dijo que los SO actuales dejaron de usar páginas. En la práctica, Windows y Linux siguen usando **paginación por demanda** como mecanismo central de memoria virtual; la segmentación pura prácticamente ya no se usa. Esta sección y la siguiente describen la evolución conceptual del PDF.

---

## 5. Páginas segmentadas por demanda (diapositivas 19–20)

- Es la evolución de los dos esquemas anteriores: **crear páginas por demanda y colocar en ellas segmentos**. Los segmentos se dividen en páginas del mismo tamaño, con lo que se conserva la visión modular y se evita la fragmentación externa.
- El costo es que la administración es **mucho más compleja** tanto en hardware como en software. El Memory Manager necesita saber qué proceso se trabaja, cuáles son sus segmentos, dónde está cada uno y si está cargado.
- Cadena de tablas (diapositiva 20): **Active Job Table** → **Segment Map Table** de cada job → **Page Map Table** de cada segmento → marco en la memoria principal.
- **Problema adicional:** el tiempo necesario para localizar **segmentos interdependientes**. Para minimizarlo se creó la **memoria asociativa**: registros extra por proceso que permiten que, cuando un segmento X necesita trabajar con otros, estos se carguen o se ubiquen rápido.
- Analogía: como las pestañitas adhesivas que se pegan en un libro; cada segmento lleva una tablita que describe dónde están sus métodos y variables, y se llega directo al punto sin recorrerlo.
- No se pedirá simular esto en tareas; basta con entender la idea.

> **Nota:** la memoria asociativa corresponde conceptualmente al **TLB** (*Translation Lookaside Buffer*) del hardware real, una caché de traducciones recientes de dirección lógica a física.

---

## 6. Memoria virtual (diapositivas 21–22)

- Es la capacidad de guardar parte de lo que debería estar en memoria principal en **memoria física** (disco). Originalmente los programadores vigilaban el tamaño de sus programas e incluso dividían un sistema en varios programas; hoy esa labor la asumen el SO y el hardware.
- Requiere **colaboración entre el Memory Manager y el hardware alrededor del procesador** (buses, controladores, interrupciones, chipset). Cuando la CPU pide una dirección que no está en RAM, el controlador de memoria detecta que está en disco, el controlador de disco la trae y la CPU solo recibe el dato. Sin ese hardware, cada programa tendría que gestionarlo (los editores antiguos traían un controlador de impresión propio para cada marca de impresora). Es algo que cubre todo el diseño del sistema computacional.
- **Ventajas** (diapositiva 22): su diseño e implementación es complejo y **costoso**, pero (1) es muy difícil alcanzar un límite real para el tamaño de los programas, (2) se usa con más eficiencia la memoria principal y (3) se **potencia la multiprogramación**.
- Resumen de la evolución: se dejó de cargar procesos completos en cajas de tamaño fijo, se pasó a dividirlos en partes más pequeñas (primero páginas, luego segmentos) y apareció la memoria virtual. Los avances de hardware aceleraron la transferencia disco → RAM hasta volverla casi invisible.
- **La RAM sigue siendo un cuello de botella.** La CPU trabaja a miles de millones de ciclos por segundo (3,5 GHz ≈ 3 500 millones), mientras que la RAM es mucho más lenta y, a su vez, más rápida que el disco. Los buses y controladores existen para no atrasar a la CPU. La próxima clase profundiza en las características de la memoria.

> **Nota:** en clase se comparó la RAM como si funcionara a «megahercios» (miles de veces más lenta). La brecha real es de **latencia**: acceder a la RAM cuesta del orden de cientos de ciclos de CPU. Sigue siendo un cuello de botella, y por eso existen las cachés.

---

## Conceptos clave

- **Página / marco (*page frame*):** parte de tamaño fijo en que se divide un programa / bloque de memoria física donde se carga; idealmente del mismo tamaño que un sector de disco.
- **Job Table, Page Map Table (PMT), Memory Map Table:** dónde empieza la PMT de cada proceso; dónde está cada página; qué marcos están libres.
- **Offset y resolución de dirección:** desplazamiento desde el inicio de la página; conversión de dirección lógica a física.
- **Paginación:** elimina la fragmentación externa; la interna queda limitada a la última página. Su éxito depende del tamaño de página.
- **Páginas por demanda / swapping:** solo se carga lo necesario; el intercambio RAM ↔ disco depende de buses rápidos.
- **Campos nuevos de la PMT:** en memoria, modificada, referenciada.
- **FIFO vs LRU:** sale la página más antigua vs la menos usada recientemente.
- **Segmentación:** segmentos de tamaño variable según módulos; requiere compiladores; aumenta la fragmentación externa.
- **Páginas segmentadas por demanda:** segmentos divididos en páginas; Active Job Table → Segment Map Table → PMT; **memoria asociativa** acelera la localización.
- **Memoria virtual:** usar el disco como extensión de la RAM, con apoyo del hardware; elimina el límite práctico al tamaño de los programas y potencia la multiprogramación.

---

## Fuera del PDF — logística, tareas y metodología

### Tarea Programada 2 (plazo: 15 días desde la clase)
Extiende la Tarea 1 con **Round Robin**. Mismas restricciones de siempre (nada que se instale con pip ni dependencias externas) y el código debe estar **dividido en funciones u objetos**, no en un archivo corrido.
- **Modelo:** una CPU, una cola de procesos listos, procesos que llegan en distintos momentos. **Round Robin** es con desalojo al agotarse el quantum; **FIFO** es sin desalojo.
- **Parámetros de llamada:** archivo de entrada, política (`fifo` o `rr`) y quantum (solo se usa con Round Robin). Valores por defecto: sin política → FIFO; quantum inválido (p. ej. −3) → 3.
- **Archivo de entrada:** igual que en la Tarea 1 (mismos archivos de prueba). Si trae errores, solo se notifica que tiene errores; **no se intenta repararlo**.
- **Simulación** por unidades de tiempo (0, 1, 2, …): en cada una se consideran las llegadas, si el proceso en CPU terminó y si agotó su quantum.
- **Reglas de Round Robin:**
  - Si en el mismo instante en que un proceso agota su quantum llegan procesos nuevos, **los nuevos entran primero a la cola y luego el expropiado**.
  - Si al agotarse el quantum la cola está vacía, el proceso **continúa con un nuevo quantum** sin cambio real.
  - Un proceso puede volver al estado *Listo* tras haber ejecutado.
- **Datos por proceso:** identificador, llegada, duración, **tiempo restante**, inicio, fin y **cantidad de veces que perdió la CPU sin terminar**.
- **Salida:** resumen por proceso (llegada, inicio, fin, espera, retorno, respuesta) y métricas globales (promedios, quién esperó más y menos, **utilización de la CPU**, **cantidad de cambios de contexto**), más un archivo de resultados con estructura similar.
- **Registro de eventos (log)**, para ambas políticas: llegada, entrada a la cola, inicio de ejecución, quantum agotado (con tiempo restante), regreso a la cola y finalización.
- **Informe de análisis comparativo:** con una mezcla de procesos largos y cortos, ¿qué política da menor tiempo de respuesta promedio? Se entregan casos de prueba con salida esperada; se pueden crear propios.

### Otros
- **Tarea 1:** retroalimentación a más tardar el lunes siguiente; las notas llegan por Moodle (miércoles o jueves en la noche). Las notas del Taller 1 se ingresan al día siguiente.
- **Taller 2:** se publica ese mismo día, corto, con **scripts ejecutables y configuraciones**. Quien use Windows debe instalar **WSL** (*Windows Subsystem for Linux*) o usar la máquina virtual del Taller 1; quien use Mac o Linux va directo a la parte de comandos. Comandos útiles: `ls -l` en lugar de `dir`, `grep`.
- **Quiz 2** (procesos): disponible hasta el martes siguiente. **Quiz 3** (administración de memoria): se publica ese día con plazo hasta el martes siguiente.
- **Formulario de repaso semanal:** recordatorio de completarlo (el de esta semana se publica ese día).
- **Próxima clase:** terminar memorias y entrar a las características de la memoria (cómo funciona por debajo y cómo se alivia el trabajo de la CPU), para luego pasar a teoría de componentes.

### Pendientes de clases anteriores (no se retomaron en esta clase)
- **PDF 3, diapositiva 16:** punto 3 (Próximo a terminar), punto 5 (Round Robin con quantum 5) y punto 6 (Round Robin con regla de ≤ 2 ciclos).
- **PDF 4, diapositiva 12:** qué estrategia (First Fit o Best Fit) aplica la figura del ejemplo.
