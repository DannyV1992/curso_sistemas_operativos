# Examen 1

**Curso:** IIIC2026 - Sistemas Operativos, LEAD University

**Docente:** Mario Miguel Agüero Obando

**Estudiante:** Daniel Vásquez González

---

## Pregunta 1. Páginas o segmentos en las simulaciones de las Tareas Programadas 1 y 2

Las tareas 1 y 2 simulan **solo la CPU**: un proceso es un id, una llegada y una duración, y el simulador decide quién usa la CPU en cada unidad de tiempo. Para agregar memoria paginada hay que darle al proceso **tamaño** y al simulador un **administrador de memoria** que responda a una pregunta nueva: ¿están en RAM las partes del proceso que va a ejecutar?

**Cambios concretos (sobre el `Simulador` de la Tarea 2):**

1. **Datos de entrada.** El CSV `id,llegada,duracion` necesita al menos una columna `memoria` (KB o número de páginas). Para que haya fallos de página interesantes, también una **secuencia de páginas referenciadas** por el proceso (por ejemplo `1,2,3,1,4`), porque sin patrón de acceso no hay nada que reemplazar.
2. **Memoria física.** Una lista de **marcos** de tamaño fijo, con su estado (libre o con qué página de qué proceso). Es la versión con páginas de la lista de particiones de la Tarea 3.
3. **Tabla de páginas por proceso.** Para cada página: ¿está en memoria?, ¿en qué marco?, ¿fue referenciada?, ¿fue modificada? (los campos de la PMT de la Clase 6).
4. **Algoritmos de reemplazo.** Cuando no hay marcos libres, elegir una página víctima con **FIFO** o **LRU**. Esto es lo que reemplaza a First Fit y Best Fit.
5. **Estado nuevo y evento nuevo.** Un fallo de página no se resuelve en cero tiempo: el proceso pasa a un estado **Bloqueado/Esperando E/S** durante N unidades (el tiempo de traer la página del disco) y la CPU se asigna a otro proceso listo. Aparece el evento "fallo de página" en el log.
6. **Interacción con Round Robin.** Si el proceso se bloquea a mitad de su quantum, ese quantum se pierde o se devuelve parcial. Hay que decidir (y justificar) qué hace el simulador, y eso afecta métricas como el tiempo de respuesta.
7. **Métricas nuevas.** Número de fallos de página por proceso, tasa de fallos, uso de memoria (marcos ocupados) y fragmentación interna en la última página. La utilización de CPU empeora si hay demasiados fallos.

**Si fueran segmentos:** cada proceso tendría una tabla de segmentos con tamaño variable (código, datos, pila, bibliotecas). Se necesitaría un asignador de huecos (First/Best Fit otra vez), manejo de **fragmentación externa** y, posiblemente, **compactación**. La complejidad cambia de lugar: menos tablas por proceso, pero más trabajo para ubicar cada segmento.

### Para un estudiante de ciencia de datos (pregunta 1b)

- La paginación funciona porque los programas tienen **localidad**: usan por ratos las mismas pocas páginas. Es la misma razón por la que procesar un DataFrame por bloques (chunks) es mucho más rápido que saltar a posiciones aleatorias.
- Si el conjunto de datos activo no cabe en RAM, el sistema pasa a **thrashing**: el equipo pasa más tiempo moviendo páginas entre RAM y disco que calculando. Se nota como una máquina que "se congela" al cargar un archivo grande. Aprendizaje: dimensionar los lotes y evitar copias innecesarias de los datos.
- La **memoria virtual** permite que un programa use más memoria de la que hay, pero con un costo oculto de velocidad. Eso explica por qué el mismo script corre en segundos o en horas según la RAM disponible.
- Las bibliotecas que mapean archivos a memoria (memory-mapping, p. ej. en NumPy) usan este mismo mecanismo: el SO trae del disco solo las páginas que se tocan.

### Lo que suele olvidarse
- Que un fallo de página **bloquea** al proceso y obliga a cambiar el modelo de estados.
- Que paginar elimina la fragmentación externa, pero deja interna en la **última página**.
- Que el tamaño de página es una decisión de diseño con compromisos (páginas pequeñas: menos desperdicio pero tablas enormes; grandes: lo contrario).

### Preguntas para profundizar
- ¿Qué pasa con las métricas de la Tarea 2 (espera, retorno, respuesta) si el bloqueo por fallos de página es largo?
- ¿Cómo detectaría el simulador que un conjunto de procesos está en thrashing?

---

## Pregunta 2. ¿Por qué con la segmentación desaparece la importancia de First Fit y Best Fit?

**La premisa es discutible: con segmentación pura no desaparece.** Los segmentos son de **tamaño variable**, y cada vez que hay que cargar uno hay que buscar un hueco libre donde quepa. Esa es exactamente la situación de las particiones dinámicas, y ahí First Fit, Best Fit (y Worst Fit) siguen siendo necesarios. Además, la segmentación **aumenta la fragmentación externa**, que es el problema que esos algoritmos intentan manejar.

**¿Cuándo sí pierden importancia?** En dos casos cercanos a la afirmación:

1. **Con paginación (y páginas segmentadas por demanda).** Todos los marcos tienen el mismo tamaño, así que **cualquier marco libre sirve** y no hay que decidir cuál "queda mejor". La pregunta ya no es "¿dónde cabe?" sino "¿qué página saco si no hay marcos libres?", y ahí entran FIFO y LRU. Probablemente esto es lo que quiere decir el enunciado: la importancia de elegir el hueco desaparece cuando se parte la memoria en unidades uniformes.
2. **Con segmentos que se dividen en páginas**, por la misma razón: el segmento es un concepto lógico y la memoria física se asigna por marcos.

**Resumen de la idea:**

| Esquema | ¿Importa First/Best Fit? | Por qué |
|---------|--------------------------|---------|
| Particiones fijas | Sí, para elegir partición | Hay que elegir entre varias particiones de distinto tamaño |
| Particiones dinámicas / segmentación pura | **Sí** | Se buscan huecos de tamaño variable |
| Paginación | **No** | Cualquier marco libre es equivalente |
| Páginas segmentadas | **No** (en memoria física) | Los segmentos se componen de páginas |

Es decir, lo que reduce la importancia de First/Best Fit no es la segmentación en sí, sino **usar bloques de tamaño uniforme**. Los algoritmos no desaparecen del todo: siguen viviendo en los asignadores dinámicos (como `malloc`) que administran el heap de un programa.

### Lo que suele olvidarse
- Distinguir segmentación **pura** de segmentación **combinada con paginación**.
- Que el problema cambia de "dónde ubico" a "qué reemplazo".

### Preguntas para profundizar
- Si los segmentos se paginan, ¿dónde queda la fragmentación externa?
- ¿Por qué los sistemas modernos prefieren paginación a segmentación pura?

---

## Pregunta 3. Universalización de interfaces de puertos vía USB

**Ventajas.** Un solo conector reduce costos, cables y residuos; permite conectar y desconectar en caliente; entrega energía y datos; y simplifica la vida del usuario y del fabricante. Desde la perspectiva del SO, el controlador USB trata a todos los dispositivos como parte de un único bus y administra el acceso y el intercambio de datos, así que el SO no necesita un manejo especial por tipo de puerto. Según la Clase 8, USB es un **dispositivo virtual** que convierte recursos dedicados en compartidos mediante controladores.

**Problemas derivados:**

1. **Mismo conector, capacidades distintas.** Un puerto o cable USB-C puede ser USB 2.0, USB 3.x, Thunderbolt, DisplayPort o solo carga, con velocidades y potencias muy distintas. El usuario no puede saber qué obtiene. La universalización física no es universalización funcional.
2. **Ancho de banda compartido.** Todos los dispositivos de un controlador comparten el mismo bus. Un disco externo copiando datos puede afectar a la cámara web o al audio conectados al mismo concentrador (*hub*).
3. **Seguridad.** Un USB es una puerta de entrada: dispositivos que se hacen pasar por teclados e inyectan comandos (BadUSB), memorias con malware, y cargadores públicos que intentan transferir datos (*juice jacking*). Un estándar universal convierte a cualquier puerto en superficie de ataque.
4. **Potencia y calor.** Con cargas de cientos de vatios por USB-C, un cable defectuoso o un cargador de mala calidad puede dañar equipos.
5. **Rendimiento y latencia.** Para tareas muy exigentes (tarjetas gráficas, almacenamiento NVMe, audio profesional de baja latencia, buses industriales) se sigue usando **PCI Express** u otros buses especializados, que ofrecen más ancho de banda y latencia más predecible. Es el mismo argumento de la clase de buses: especializar libera a la CPU y mejora el rendimiento.
6. **Dependencia y obsolescencia.** Si todo depende de un estándar, un fallo o cambio de estándar afecta a todo el ecosistema; además, la compatibilidad hacia atrás complica el diseño.
7. **Regulación.** Imponer un conector común (como ha pasado con los cargadores en la Unión Europea) reduce residuos, pero puede frenar la innovación en nuevos conectores.

**Conclusión.** La universalización es mayormente buena para el usuario, pero necesita **etiquetado claro** de capacidades, seguridad por defecto (pedir confirmación antes de aceptar un dispositivo nuevo) y la convivencia con buses especializados donde el rendimiento lo exige.

### Lo que suele olvidarse
- Separar el conector (forma física) del **protocolo** (qué velocidad y qué funciones soporta).
- Mencionar la seguridad, no solo la comodidad.

### Preguntas para profundizar
- ¿Por qué un disco USB 3 conectado a un concentrador USB 2 se vuelve lento?
- ¿Qué hace el SO cuando se conecta un dispositivo USB nuevo (detección, controlador, asignación de recursos)?

---

## Pregunta 4. Memoria y procesos en sistemas operativos móviles

### Primero, hipótesis antes de investigar

Qué se espera que importe en un teléfono, comparado con un computador de escritorio:

1. **Menos RAM y sin disco "grande" como respaldo.** La memoria flash tiene un número limitado de escrituras, así que usar el almacenamiento como memoria virtual (swap) desgasta el dispositivo. Hipótesis: se evita el swap tradicional.
2. **La batería manda.** Cada proceso que despierta gasta energía. Hipótesis: el SO limita fuertemente lo que puede ejecutarse en segundo plano.
3. **Un solo programa en primer plano.** La pantalla es pequeña, así que casi siempre un usuario interactúa con una aplicación. Hipótesis: el planificador da prioridad enorme al proceso visible, para que la interfaz no se trabe.
4. **Muchas aplicaciones "abiertas" pero casi todas inactivas.** Hipótesis: el SO puede congelar o cerrar procesos que el usuario no ve, y la aplicación debe poder recuperarse.
5. **Calor.** Sin ventilador, el procesador baja su velocidad si se calienta. Hipótesis: el rendimiento no es constante.

### Lo investigado (verificar en la documentación oficial)

**Android** (núcleo Linux):
- Cada aplicación corre en su propio proceso. Los procesos se crean a partir de un proceso base (*Zygote*), lo que permite **compartir páginas de memoria** de las bibliotecas comunes entre aplicaciones y ahorrar RAM.
- Cuando la memoria escasea, un demonio de bajo consumo de memoria (**lmkd**, *low memory killer daemon*) **termina procesos** según su prioridad: primero los que ya no están a la vista y están en caché, y al final los visibles. La prioridad refleja el estado de la aplicación (primer plano, visible, servicio, en caché).
- Usa **zRAM**: una zona de la RAM donde se guardan páginas comprimidas, en lugar de enviarlas al almacenamiento.
- La aplicación recibe avisos de presión de memoria (como `onTrimMemory`) y debe estar preparada para que el sistema la cierre y la vuelva a abrir. Por eso el ciclo de vida de una *Activity* tiene guardado y restauración de estado.
- Para ahorrar energía: modos de ahorro (**Doze**, **App Standby**) y límites a la ejecución en segundo plano.

**iOS:**
- Tradicionalmente **no usa swap a disco** para memoria de aplicaciones; usa **compresión de memoria**.
- Cuando falta memoria, un mecanismo (**Jetsam**) termina procesos según prioridad. Antes, la aplicación recibe una **advertencia de memoria** para que libere lo que pueda.
- Estados de una aplicación: activa, inactiva, en segundo plano y **suspendida** (queda en memoria sin ejecutar código; puede ser eliminada sin aviso).
- El tiempo de ejecución en segundo plano está muy limitado y solo se permite en casos específicos (audio, ubicación, descargas, etc.).

**Común a ambos:** planificación consciente de energía (núcleos de alto rendimiento y de bajo consumo, tipo big.LITTLE), regulación por temperatura y memoria compartida entre CPU y GPU.

### Conclusiones (qué enseña y qué sorprende)

- **Se confirma:** la memoria es escasa, la batería condiciona todo y el proceso visible tiene prioridad. Además, por lo general no se usa swap al almacenamiento como en escritorio (se comprime en RAM).
- **Lo sorprendente:** en móvil **el SO puede matar procesos sin pedir permiso** como parte normal de su funcionamiento, y el programador debe **diseñar para eso**. En escritorio, un proceso que el usuario dejó abierto sigue ahí; en móvil, "estar abierta" no garantiza que la aplicación siga cargada.
- **Relación con el curso:** el modelo de estados de la Clase 3 (Nuevo, Listo, Ejecutando, Bloqueado, Terminado) se queda corto; en móvil aparecen estados como **suspendido** o **en caché**, que son "procesos congelados en memoria" listos para volver rápido o para ser eliminados. Es una política de reemplazo, pero **a nivel de procesos completos** y no de páginas.
- **Diferencia de enfoque:** en escritorio, la presión de memoria se resuelve moviendo páginas al disco; en móvil, **matando procesos y comprimiendo memoria**. Cambia el criterio de qué se sacrifica.

### Lo que suele olvidarse
- Explicar **por qué** (flash, batería, pantalla única), no solo qué hacen Android e iOS.
- Distinguir lo que se supone de lo que se verificó con fuentes.