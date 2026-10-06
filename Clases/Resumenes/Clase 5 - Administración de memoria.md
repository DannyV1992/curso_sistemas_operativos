# Clase 5 — Administración de memoria: particiones fijas y dinámicas

**Curso:** IIIC2026 - Sistemas Operativos, LEAD University
**Docente:** Mario Miguel Agüero Obando
**Fecha:** 5 de octubre de 2026 (estimada por continuidad semanal respecto a la Clase 4; no se menciona explícitamente en la transcripción)
**PDF fuente:** `4 - Administracion de Memoria.pdf` (20 diapositivas). El repaso inicial corresponde a la diapositiva 16 de `3 - Asignacion De Procesos.pdf` (ejercicio de planificación).
**Cobertura del PDF:** Completo (diapositivas 1 a 20). Las diapositivas 18 a 20 son ejercicios que quedan como práctica para revisarse la clase siguiente; no se resolvieron. No se saltó ninguna diapositiva.
**Nota sobre la transcripción:** hay una pausa de ~30 min a media clase y una demostración de Linux dentro de Windows que no aporta contenido de estudio. Varios tramos están mal reconocidos (p. ej. «Ley de Ámbar/Amda» = Ley de Amdahl, «Festfit» = Best Fit, «Homergy» = Omarchy) y se corrigieron por contexto. Los cálculos a mano del repaso tienen errores aritméticos; se señalan en notas.

**Contexto.** La sesión abre con la revisión del ejercicio de planificación de la Clase 4 y luego inicia el tema de **administración de memoria**: por qué importa, y cómo evolucionaron los primeros esquemas (memoria exclusiva, particiones fijas, dinámicas y relocalizables). La administración moderna (segmentación, paginación, memoria virtual) queda para la siguiente clase.

---

## Ruta de la clase

| Bloque | Tema | Diapositivas |
|--------|------|--------------|
| 0 | Repaso: ejercicio de planificación (PDF 3) | — |
| 1 | Memoria principal y Memory Manager | 1–3 |
| 2 | Memoria exclusiva del usuario | 4–5 |
| 3 | Particiones fijas | 6–8 |
| 4 | Particiones dinámicas, First Fit / Best Fit y listas de memoria | 9–13 |
| 5 | Liberación de memoria y fragmentación | 14–15 |
| 6 | Particiones dinámicas relocalizables | 16–17 |
| 7 | Ejercicios propuestos | 18–20 |

---

## 0. Repaso: ejercicio de planificación (PDF 3, diapositiva 16)

Procesos (llegada, duración): A(0, 2), B(1, 12), C(2, 4), D(4, 3), E(5, 8), F(7, 5), G(8, 3).

| Política | Salida de A, B, C, D, E, F, G | Promedio dicho en clase | Turnaround real (salida − llegada) |
|----------|-------------------------------|-------------------------|------------------------------------|
| FCFS | 2, 14, 18, 21, 29, 34, 37 | 21 | 18.29 |
| Shortest Next Job | 2, 37, 6, 9, 25, 17, 12 | 15 | 11.57 |
| Prioridad | 2, 29, 17, 32, 16, 37, 11 | ≈ 20 | 16.71 |
| Round Robin, quantum 4 | 2, 37, 8, 11, 28, 29, 23 | no se calculó | 15.86 |

> **Nota:** los promedios dichos en clase (21, 15, ≈ 20) se acercan al promedio de los **tiempos de salida** sin restar la llegada. Como el turnaround se define como salida − llegada (Clase 4), los valores de la última columna son los que corresponden. En Round Robin se dijo que B salía en 36, pero el trabajo total es 37 ms, así que B sale en 37.

- **Prioridad:** se resolvió **con desalojo**: todos con prioridad 0 salvo C = 1, E = 2 y G = 3. Al llegar un proceso de mayor prioridad, el que está ejecutándose cede la CPU (C desaloja a B, E a C, G a E). Al empatar en prioridad, FIFO. Es el algoritmo «interesante y totalmente distinto», pero aquí quedó cerca de FCFS; se podría ajustar dando prioridad al proceso más viejo (*aging*).
- **Próximo a terminar:** no se desarrolló; solo se explicó que se comporta de forma muy parecida a Shortest Next Job con estos datos (ningún proceso que llega es más corto que lo que le queda al actual). Con estos datos da las mismas salidas que SNJ. Para que hubiera desalojo, tendría que llegar, por ejemplo, un proceso de 2 ms mientras F lleva 2 ms ejecutados (le quedan 3).
- **Round Robin, quantum 4:** se contó el quantum sobre marcas de reloj fijas (0, 4, 8, …), de modo que B, que arrancó en t = 2, solo ejecutó 2 ms antes de perder la CPU y volvió a la cola con 10. Quien se desaloja va al final de la cola, **detrás de los que llegaron durante su quantum**. Conviene dibujar la cola y marcar cada proceso con un color.

> **Nota:** este criterio del quantum (ticks fijos de reloj) difiere del planteamiento de la Clase 4 (el quantum completo desde que el proceso arranca). Al resolver la tarea conviene seguir la convención que fije el enunciado.

- **Regla de «menos de 2 ciclos» (punto 6 del ejercicio):** si al terminar el quantum el proceso solo ha usado 2 ciclos o menos del quantum vigente (es decir, apenas «agarró la colilla» del ciclo), se le deja seguir en el siguiente en vez de cambiar de proceso. Así se ahorra un cambio de contexto, cuyo costo (los «tiempos muertos») los ejercicios no modelan pero existe.
- **Criterio al evaluar:** se califica sobre todo que la **secuencia** de ejecución sea correcta y se siguen las reglas de asignación. Un error aritmético aislado no se penaliza con cero.
- **Incentivos mal diseñados (efecto cobra):** una métrica o incentivo mal diseñado empeora el problema. En la India británica se pagó por cobras muertas, la gente las crió para cobrar, se canceló el pago y se liberaron las cobras: terminó habiendo más. Igual pasa con prioridades manipulables (programas «dummy» que aparentan ser cortos).

### Estado del ejercicio de la diapositiva 16

| Punto | Enunciado | Estado |
|-------|-----------|--------|
| 1 | FCFS | Resuelto en clase |
| 2 | Shortest Next Job | Resuelto en clase |
| 3 | Próximo a terminar | Solo explicado; **no resuelto** |
| 4 | Prioridad | Resuelto en clase |
| 5 | Round Robin, quantum 4 y 5 | Quantum 4 resuelto; **quantum 5 pendiente** |
| 6 | Round Robin con regla de ≤ 2 ciclos (quantum 5 y 6) | Solo explicada la regla; **pendiente** |

---

## 1. Memoria principal y Memory Manager (diapositivas 1–3)

- Recordatorio del modelo básico (diapositiva 2): el programa se carga en **memoria principal** (la RAM) y desde allí la CPU toma instrucciones y datos para ejecutar. La CPU tiene registros, unidad de control y ALU; el **contador de programa** guarda la dirección de la siguiente instrucción. Datos e instrucciones se guardan en áreas separadas (segmentos).
- Si el **Process Manager** administra los procesos, el **Memory Manager** administra la memoria.
- La administración de memoria **define el rendimiento** del sistema. Un SO que la administra mal se arrastra (p. ej. algunas versiones de Windows), mientras que Linux, aun dentro de una máquina virtual, se siente muy rápido.

### Ley de Amdahl: rendimientos decrecientes
«Comprar más memoria» no arregla una mala administración, y además cuesta. Hay un punto de **costo-beneficio** a partir del cual cada GB adicional aporta cada vez menos.

| Salto de RAM | Costo adicional (ilustrativo) | Mejora de rendimiento (ilustrativa) |
|--------------|-------------------------------|-------------------------------------|
| 8 → 16 GB | ≈ 250 USD | muy grande |
| 16 → 32 GB | ≈ 300 USD | grande |
| 32 → 64 GB | ≈ 550 USD | pequeña |

- Conclusión: el punto óptimo para uso diario suele estar en el salto 16 → 32 GB. Pasar de 32 a 64 GB cuesta varias veces más por una ganancia mucho menor. Solo se justifica con cargas especiales (entrenar modelos, levantar varios servidores para desarrollo).
- Es el **costo marginal**: lo que cuesta cada unidad adicional frente a lo que rinde. Ampliar la RAM de un equipo existente suele ser mejor medida a corto plazo que reemplazarlo.
- Las cifras del cuadro son de pizarra y aproximadas; los precios de la RAM han subido mucho (32 GB pasó de ≈ 100 USD en 2024 a varios cientos hoy).
- La optimización sigue importando: el *Super Mario Bros* original corría con 2 KB de RAM (cartucho de 32 KB). Hoy hay juegos que se traban en consolas de ~10 TFLOPS por falta de optimización.

> **Nota:** la Ley de Amdahl, en sentido estricto, establece que la aceleración total está limitada por la fracción del trabajo que **no** se puede mejorar: $S = \dfrac{1}{(1-p) + p/s}$, con $p$ la fracción mejorada y $s$ la mejora de esa fracción. En clase se usa en el sentido amplio de rendimientos decrecientes.

---

## 2. Memoria exclusiva del usuario (diapositivas 4–5)

- Los primeros SO ejecutaban **un solo programa a la vez**, cargado completo en memoria continua; toda la memoria era exclusiva de ese proceso (diapositiva 5: proceso de 30 KB y 170 KB libres, que no se podían aprovechar).
- Las primeras computadoras tenían muy poca memoria (p. ej. ZX Spectrum con 16 o 48 KB, NES con 2 KB, Atari 2600 con 128 bytes). Para crecer, un programa tenía que reducirse, dividirse en programas pequeños o comprar más memoria.
- El trabajo del Memory Manager era mínimo: fijar la **dirección de inicio** y verificar que el programa **cupiera**.
- Con el tiempo compartido y la multiprogramación (varios usuarios o varios programas) el problema se complicó.

---

## 3. Particiones fijas (diapositivas 6–8)

- Al encender el equipo (o al cargar el SO) la memoria se divide en **particiones de tamaño fijo**; en cada una se carga un proceso.
- **No se pueden cambiar sin reiniciar.** El tamaño se definía en un archivo de configuración que se editaba antes de apagar y reiniciar.
- Aparece el concepto de **protección**: lo que le ocurre a un proceso no debe afectar a los demás, y los datos no deben mezclarse. (En C/C++ un programa sí puede escribir fuera de su espacio, un problema conocido de esos lenguajes.)
- Aumenta la complejidad del Memory Manager (debe monitorear las particiones) y del Process Manager.

### Ejemplo (diapositiva 7)
Particiones de 100, 25, 25 y 50 KB. Cola de procesos *Ready*: P1 = 30, P2 = 50, P3 = 50, P4 = 25 KB.
- P1 → partición de 100 KB; P2 → partición de 50 KB; P4 → una de 25 KB.
- **P3 no puede ubicarse:** la única partición de 50 KB está ocupada. Debe esperar a que P2 termine, aunque quede una partición de 25 KB libre. P4, que llegó después, sí entra.

### Problemas
1. **Desperdicio dentro de la partición:** P1 usa 30 KB de 100, o sea se desperdician 70 KB (≈ 70 % de la partición). Está marcada como ocupada aunque no se use.
2. **Procesos retenidos o «perdidos»:** un proceso listo puede esperar mucho a que se libere una partición. Como las particiones no se pueden ajustar, solo queda esperar a que otro termine.
3. **Requieren conocer de antemano el tamaño** de los programas.
4. **Datos de crecimiento dinámico:** un programa pequeño que carga un *dataset* grande necesita más memoria mientras corre. Había que pedir memoria libre, cargar, procesar, vaciar y repetir por lotes.

Funcionan bien solo si los procesos tienen **tamaños parecidos** y **no generan datos que crecen dinámicamente**.

---

## 4. Particiones dinámicas (diapositivas 9–13)

Para superar esos problemas, las particiones se crean como **bloques continuos del tamaño que el proceso necesita** cuando se carga (estado *Ready*). Se aprovecha mejor la memoria, y aquí es donde «el Memory Manager empieza a trabajar de verdad»: su complejidad es mayor.

### Ejemplo (diapositiva 10)
Memoria de 105 KB con el SO al inicio. Entran J1 = 10, J2 = 15, J3 = 20 y J4 = 50 KB; terminan J1 y J4 y sus huecos quedan libres; entran J5 = 5 y J6 = 30 KB en esos huecos; termina J3; entra J7 = 10 KB.
- Queda un hueco de 5 KB, uno de 10 KB y uno de 20 KB: **35 KB libres en total**.
- J8 (30 KB) **no puede entrar**: necesita un único espacio continuo y ningún hueco llega a 30 KB. Habría que esperar a que se liberen huecos contiguos.

### Estrategias de reserva (diapositiva 11)

| Estrategia | Criterio | Optimiza |
|------------|----------|----------|
| **First Fit** | Primera partición libre donde cabe | Velocidad de carga del proceso |
| **Best Fit** | La partición libre más pequeña que cumple el requerimiento (desperdicia menos) | Uso del espacio |

- Ejemplo: huecos libres de 30 y 25 KB y llega un proceso de 20 KB. First Fit lo coloca en el de 30 (desperdicia 10); Best Fit en el de 25 (desperdicia 5).
- **Analogía de la biblioteca:** ¿se acomoda todo lo más cerca posible, o se busca acomodar para llenar mejor el espacio? Programar una u otra estrategia da complejidad distinta al SO.
- La diapositiva 12 plantea como pregunta qué estrategia aplica la figura del ejemplo; no se resolvió en clase.

### Listas de memoria (diapositiva 13)
El Memory Manager lleva dos listas, **particiones libres** y **particiones ocupadas**, y en ambas guarda la **dirección de inicio** y el **tamaño**. Al liberarse una partición se marca como libre, y se puede dividir o reducir para crear otra. Así el tamaño de las «cajas» cambia dinámicamente.

---

## 5. Liberación de memoria y fragmentación (diapositivas 14–15)

- Con un solo proceso no hay problema; con particiones fijas basta marcar la partición como libre. Con **particiones dinámicas** liberar se complica, porque conviene **combinar** particiones libres contiguas. Hay tres escenarios: liberar una partición **adyacente a otra libre**, liberar una **entre dos libres**, o liberar un **bloque aislado**.
- Al desocuparse una partición se podría «subir» otra para unir sus huecos y formar uno más grande (p. ej. 10 KB + 20 KB → 30 KB), con lo que J8 habría podido entrar. De ahí nace la idea de mover particiones.

### Fragmentación
Es el espacio libre que no se puede aprovechar:
- **Fragmentación interna:** espacio desperdiciado **dentro de una partición ocupada** (p. ej. los 70 KB sin usar de la partición de P1).
- **Fragmentación externa:** espacios libres **en medio de espacio usado**: hay memoria libre suficiente en total, pero dispersa y no continua, por lo que no cabe un proceso.

> **Nota:** la diapositiva 15 define la fragmentación interna como «memoria libre total suficiente pero ninguna partición del tamaño necesario», que corresponde en realidad a la fragmentación **externa**, y dice que esta última aparece con particiones relocalizables. Se sigue aquí la definición de la clase: la interna ocurre en particiones fijas (y dentro de cualquier partición sobredimensionada) y la externa en particiones dinámicas sin reubicación. Las particiones relocalizables (sección 6) son justamente la solución a la externa.

---

## 6. Particiones dinámicas relocalizables (diapositivas 16–17)

- Además de particiones dinámicas, el Memory Manager puede **reacomodarlas**: mueve los procesos en memoria para que todas las particiones ocupadas queden **juntas** y todo el espacio libre quede **unificado** (compactación). Así, cuando llega un proceso nuevo, se le crea su espacio en lugar de buscar dónde ponerlo.
- Analogía de la biblioteca: al bibliotecario se le agrega la función de acomodar bien **todo**, no solo cada estante.
- Ejemplo (diapositiva 17): hay dos huecos (12 y 30 KB) entre Job 1, Job 4, Job 2 y Job 5. Job 6 (84 KB) espera aunque hay memoria libre suficiente en total. Al compactar (subir Job 4, Job 2 y Job 5) el espacio libre queda unificado y Job 6 cabe.
- **Costo:** hay que conocer dónde empieza y termina el área de cada proceso para poder moverlo. Mover procesos implica **más trabajo para el procesador y para el Memory Manager**.

### Hacia dónde sigue el tema
Ya en memoria solo conviene tener lo inmediato: un programa se puede dividir en partes (por ejemplo, el trozo que concentra el tiempo de cómputo frente a las demás) y cargar solo las necesarias, guardando en otro lugar el resto. Esto da origen a la **segmentación**, la **paginación** y la **memoria virtual** (el ruido del disco duro mecánico al cambiar de aplicación en una laptop vieja), que se verán la próxima clase.

---

## 7. Ejercicios propuestos (diapositivas 18–20)

Todos usan la misma secuencia de eventos: llegan A (5K) y B (15K); llegan C (30K) y D (14K); llegan E (40K) y F (16K); termina A; llegan G (8K) y H (9K); terminan C y E; llegan I (4K), J (8K) y K (18K); terminan F y G. Hay que mostrar cómo cambia la memoria en el tiempo con:

1. **Particiones fijas:** 2 de 10K, 4 de 20K y 2 de 50K.
2. **Particiones dinámicas** en múltiplos de 5 (solo se crean particiones de 5, 10, 15, 20… K).
3. **Particiones dinámicas relocalizables** en múltiplos de 5.

Se resolverán y comentarán la próxima clase; se pide intentarlos antes.

---

## Conceptos clave

- **Memory Manager:** administra la memoria principal, igual que el Process Manager administra procesos; su administración define el rendimiento del sistema.
- **Ley de Amdahl (en sentido amplio):** más memoria mejora el rendimiento, pero con rendimientos decrecientes; existe un punto óptimo de costo-beneficio y un costo marginal creciente.
- **Memoria exclusiva:** un solo proceso en memoria; el Memory Manager solo verifica que quepa.
- **Particiones fijas:** tamaños fijos definidos antes de arrancar; traen protección, desperdicio interno y procesos retenidos.
- **Particiones dinámicas:** bloques continuos del tamaño del proceso; mejoran el uso pero generan huecos dispersos.
- **First Fit** (primer hueco que cabe, más rápido) frente a **Best Fit** (el hueco que menos desperdicia, mejor uso del espacio).
- **Listas de memoria:** particiones libres y ocupadas, con dirección de inicio y tamaño.
- **Fragmentación interna** (dentro de una partición ocupada) frente a **externa** (huecos libres entre particiones ocupadas).
- **Relocalización / compactación:** mover procesos para unificar el espacio libre, a cambio de más trabajo del procesador.

---

## Fuera del PDF — logística, tareas y metodología

- **Taller 1:** revisado; en general muy bien, sin críticas relevantes.
- **Tarea programada 1:** plazo hasta el miércoles antes de medianoche.
- **Tarea programada 2:** la misma simulación de la tarea 1 con **selección de algoritmo**, agregando **dos algoritmos** (uno de ellos todavía por confirmar). Se publica en el sitio del curso al día siguiente de la clase.
- **Quiz 2** (teoría de procesos): publicado el día de la clase.
- **Taller 2:** se publica la semana siguiente.
- **Formulario de repaso semanal:** recordatorio de llenarlo.
- **Práctica:** intentar los ejercicios de las diapositivas 18–20 antes de la próxima clase.
- **Próxima clase (lunes siguiente):** revisión de los ejercicios de memoria y de los pendientes del PDF 3 si quedan dudas, y comienzo de la **administración moderna de memoria** (segmentación, paginación y memoria virtual).
