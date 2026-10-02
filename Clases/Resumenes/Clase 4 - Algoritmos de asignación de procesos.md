# Clase 4 — Algoritmos de asignación de procesos

**Curso:** IIIC2026 - Sistemas Operativos, LEAD University
**Docente:** Mario Miguel Agüero Obando
**Fecha:** 28 de septiembre de 2026 (estimada por continuidad semanal respecto a la Clase 3; no se menciona explícitamente en la transcripción)
**PDF fuente:** `3 - Asignacion De Procesos.pdf` (16 diapositivas), apoyado en `3 - Ejemplos Algoritmos Procesos.xlsx`, la hoja de cálculo con la que se resolvieron los ejemplos en clase. El repaso inicial coincide con las diapositivas 26 a 28 de `2 - Kernel y Procesos.pdf` (criterios de las políticas y tiempos muertos).
**Cobertura del PDF:** Completo (diapositivas 1 a 16): FCFS, Shortest Next Job, Prioridad, Próximo a terminar, Round Robin, SO modernos y ejercicio final.
**Nota sobre la transcripción:** varios cálculos hechos a mano en clase contienen errores aritméticos corregidos sobre la marcha o mal transcritos (p. ej. el turnaround de Shortest Next Job y de Próximo a terminar). En esos casos se usan los valores del PDF. El resultado del ejemplo de Round Robin no se enuncia completo en la transcripción y se calculó a partir de los tiempos de salida dichos en clase.

**Contexto.** Sesión práctica sobre las **políticas del Process Scheduler**: en qué orden se asigna la CPU a los procesos que están en estado *Ready*. Se resuelven ejemplos en Excel con diagramas de tiempo y se introduce la métrica **turnaround time** para comparar algoritmos.

**Repaso:** el *Process Manager* tiene dos partes: el **Job Scheduler** (mete y saca procesos del ciclo de ejecución) y el **Process Scheduler** (alterna los procesos en la CPU). Un proceso pasa a *Waiting* por una interrupción de E/S o cuando se le acaba el tiempo asignado, y regresa a *Ready*. Hay máquinas y SO antiguos que tienen Process Manager pero **no** Process Scheduler: solo ejecutan los procesos en orden de llegada (el Process Scheduler apareció hace unos 40–50 años). Aun con varios núcleos, cada CPU rota sus propios procesos; a eso se le llama **multiprogramación**.

**Objetivo de las políticas:** maximizar la productividad (trabajo terminado por unidad de tiempo) y minimizar los tiempos de respuesta. Todas tienen ventajas y desventajas; empíricamente hay una que en promedio funciona mejor (Round Robin).

**Simplificación de los ejercicios:** se ignoran los **tiempos muertos** del cambio de proceso (en la realidad, cambiar de proceso cuesta tiempo); también en la tarea programada. Los procesos se miden en milisegundos/ciclos de CPU.

---

## Ruta de la clase

| Bloque | Tema | Diapositivas |
|--------|------|--------------|
| 1 | FCFS y turnaround time | 2–5 |
| 2 | Shortest Next Job | 6–7 |
| 3 | Prioridad | 8 |
| 4 | Próximo a terminar | 9–11 |
| 5 | Round Robin | 12–14 |
| 6 | SO modernos y ejercicio propuesto | 15–16 |

---

## 1. First Come / First Served (FCFS) (diapositivas 2–5)

- Filosofía **FIFO**: apenas se crea el PCB, el proceso se coloca al final de una cola. Los procesos pasan directo a *Ready* y se ejecutan en orden de llegada.
- **No hay estado *Wait*:** cada proceso se ejecuta **hasta completarse**, sin interrupciones. Era el modelo de las computadoras que solo hacían una cosa a la vez.

### Métrica: turnaround time (diapositiva 4)
Tiempo requerido para completar un proceso **desde el momento en que está listo** (no es la duración del proceso):

$$TAT_i = t_{\text{fin},i} - t_{\text{llegada},i} \qquad \overline{TAT} = \frac{\sum_i TAT_i}{n}$$

### Ejemplo: A = 15 ms, B = 2 ms, C = 1 ms (todos listos en 0)

| Orden | Tiempos de terminación | Turnaround promedio |
|-------|------------------------|---------------------|
| A, B, C | 15, 17, 18 | (15+17+18)/3 = **16.67** |
| C, B, A | 1, 3, 18 | (1+3+18)/3 = **7.3** |

- Mismo trabajo, distinto orden de llegada: el promedio cambia muchísimo. **Debilidad:** el rendimiento depende de la «suerte» del orden de llegada. Es muy sencillo de implementar.
- **Interpretación de la métrica:** un turnaround bajo indica que los procesos cortos salen rápido; uno alto, que los largos son los que se ejecutan primero. No permite afirmar por sí sola que una política sea «mejor»: dar prioridad a los cortos maximiza la cantidad de trabajo terminado por unidad de tiempo; dar prioridad a los largos es «sacarse las tareas pesadas» primero. Depende de la filosofía que se quiera seguir.
- Esta es la política que implementa la **Tarea programada 1**.

---

## 2. Shortest Next Job (SNJ) (diapositivas 6–7)

Surgió como reacción a la variabilidad de FCFS: en lugar de respetar el orden de llegada, se prioriza la **productividad** ejecutando siempre el proceso de **menor duración**. En empates se respeta el orden de llegada.

### Ejemplo: A = 5, B = 2, C = 6, D = 4 (todos en 0)
Orden: B(2), D(4), A(5), C(6) → terminan en 2, 6, 11, 17 → $\overline{TAT} = (2+6+11+17)/4 = 9.0$

### Variante con llegadas distintas
J = 4, K = 8, L = 3, M = 6 llegan en 0; N = 5 llega en 10. Se ejecuta L (3), J (4), M (6), N (5, cuando ya llegó y es menor que K) y K (8).
Terminaciones: L 3, J 7, M 13, N 18, K 26. Al restar la llegada, N (que llegó tarde) tiene un TAT pequeño: $\overline{TAT} = 11.4$.

### Por qué no se usa hoy: el problema de la estimación
- Para aplicarlo el Process Scheduler tiene que **estimar la duración** revisando el código, y esa estimación debe ser lo más exacta posible.
- La duración no depende solo del tamaño del programa: un programa de 6 líneas con un triple `for` anidado es $O(n^3)$, y lo que tarda depende de la **cantidad de datos de entrada** (procesar 1,000 millones de registros tarda mucho aunque el código sea corto).
- Los programadores aprendieron a «engañar» al planificador dividiendo un programa grande en pedazos pequeños (como un *pipeline*) para que recibieran prioridad.
- Es fácil de implementar en SO de **lotes** (*batch*), donde se conoce el volumen de datos y la duración total; en **sistemas interactivos es prácticamente imposible**, porque no se sabe cuándo terminará un Word o un Excel (terminan cuando el usuario los cierra). El modelo de eventos no encaja con este algoritmo.

---

## 3. Prioridad (diapositiva 8)

- Es el algoritmo **más común en sistemas batch**, porque da preferencia a los procesos importantes.
- Se ordena la cola de procesos con PCB creados según su **prioridad** (el campo *prioridad* del PCB). **Si dos procesos tienen la misma prioridad, se usa FIFO.**
- Es lo mismo que SNJ pero cambiando el criterio de selección: en vez del más corto, se toma el de mayor prioridad (se agrega una columna «prioridad», por omisión 0).
- Criterios posibles para asignar la prioridad: accesos a memoria, accesos a dispositivos de E/S, tiempo de operaciones de CPU y **tiempo que el proceso ya lleva en el sistema (*aging*)**.
- Calcular todo eso analizando el código es muy complejo (sería como un sistema que evalúa programas y los ordena, con posibilidad de equivocarse); por eso en la práctica las prioridades se asignan de otras formas y este algoritmo suele quedar como complemento (ver sección 6).

---

## 4. Próximo a terminar (*Shortest Remaining Time*) (diapositivas 9–11)

Variante **con desalojo** de SNJ: se escoge el proceso que está «más cerca» de terminar (el criterio básico es qué tan cerca está el puntero de instrucciones del final). Regla clave:

> Si llega a la cola un proceso que dura menos de lo que le queda al que está ejecutándose, se detiene el actual y se pasa de inmediato al más corto.

Busca aumentar la productividad: generar la mayor cantidad de trabajo en el menor tiempo. Ante empate en lo que queda, se respeta el orden de llegada.

### Ejemplo: A(0) = 6, B(1) = 3, C(2) = 1, D(3) = 4

| t | 0 | 1 | 2 | 3–4 | 5–8 | 9–13 |
|---|---|---|---|-----|-----|------|
| Se ejecuta | A | B | C | B | D | A |

- t = 1: a A le quedan 5 y B (3) es menor → pasa B. t = 2: a B le quedan 2 y llega C (1) → pasa C. t = 3: C terminó; B (2) es menor que D (4) y A (5). t = 5: B termina y entra D (4) antes que A (5). t = 9: D termina y retoma A.
- Aquí el TAT es **tiempo de terminación − tiempo de entrada** (no la duración): A = 14−0, B = 5−1, C = 3−2, D = 9−3.

$$\overline{TAT} = \frac{14+4+1+6}{4} = 6.25$$

- Al trabajar el ejercicio conviene ir anotando, bajo el proceso en ejecución, cuánto le queda a cada uno, y no temer hacer el cambio en medio de la ejecución de un proceso.

---

## 5. Round Robin (diapositivas 12–14)

- El sistema más común en los **SO interactivos** (sistemas que esperan estímulos del usuario y permiten alternar entre programas). Es lo que permitió pasar de abrir un solo programa (DOS) a varios a la vez en las primeras versiones de Windows.
- La CPU reparte su tiempo en segmentos fijos llamados **quantums** (*time quantums*); por ejemplo, de los miles de millones de ciclos por segundo de un procesador, cada proceso recibe un quantum y luego cede su turno.
  - Los procesos se atienden con **FIFO**.
  - Si el proceso **termina antes** de que su quantum acabe, se pasa de inmediato al siguiente.
  - Si **no termina**, pierde la CPU y vuelve **al final de la cola** con su tiempo restante.
  - Si hay una **interrupción**, se procede como ya se conoce: salvar el estado del procesador, ejecutar el manejador de interrupciones y restaurar el estado.
- Tiempo restante: quantum − lo ejecutado se resta de la duración (si el proceso dura 12 y el quantum es 4, vuelve a la cola con 8).

### Ejemplo: quantum = 4 ms (se ignoran interrupciones)

| Proceso | Llegada | Duración |
|---------|---------|----------|
| A | 0 | 8 |
| B | 1 | 4 |
| C | 2 | 9 |
| D | 3 | 5 |

Secuencia: A(0–4), B(4–8, termina), C(8–12), D(12–16), A(16–20, termina), C(20–24), D(24–25, termina), C(25–26, termina).
Terminaciones: A 20, B 8, C 26, D 25 → TAT = 20, 7, 24, 22 → $\overline{TAT} = 18.25$ (valor calculado a partir de la secuencia; el gráfico del PDF extiende el eje hasta 32, pero el trabajo total es 26 ms).

- El turnaround promedio es mayor que en otras políticas porque todos los procesos se van alternando, pero a cambio nadie es ignorado. Lo valioso es la **ilusión de ejecución simultánea**.
- Al armar la cola hay que tener cuidado con el orden: el proceso que sale va al final de la cola, pero detrás de los que llegaron durante su quantum.

### Cómo evolucionó el quantum
- Al inicio todos recibían **el mismo** quantum (en los Windows 95/98 se notaban «tirones» al escribir en Word porque se repartía igual el tiempo entre todos). Hoy el SO **detecta actividad** (muchas interrupciones de teclado, edición de video, muchas pestañas) y asigna más tiempo a los procesos con mayor actividad; los procesos inactivos se dejan guardados (memoria virtual, tema posterior). Esto es más fácil de programar que estimar cuántos registros va a leer un programa.
- **Variante para reducir cambios de proceso:** si un proceso solo ejecutó **2 ciclos o menos** del quantum actual (le quedaba poco), no se cambia de proceso al terminar el quantum: se le deja seguir en el siguiente. Busca economizar cambios de contexto consecutivos.

---

## 6. ¿Qué hacen los SO más modernos? (diapositiva 15)

- Hoy los SO son en su mayoría **interactivos**. Linux, Windows y macOS usan **Round Robin** y lo complementan con técnicas vistas (en especial **colas de prioridad**) para acelerar algunas tareas.
- Los programas actuales responden a eventos del usuario y no a procesamiento secuencial de datos en bloques, por lo que Round Robin es una forma mucho más sencilla de darle tiempo a todos los procesos para que avancen o estén listos para ejecutarse.

---

## 7. Ejercicio propuesto (diapositiva 16)

Dados los jobs: A(llegada 0, 2 ciclos), B(1, 12), C(2, 4), D(4, 3), E(5, 8), F(7, 5), G(8, 3), calcular el turnaround time con:

1. FCFS (orden A, B, C…).
2. Shortest Next Job (orden dado).
3. Próximo a terminar.
4. Prioridad, con todos en 0 excepto C (1), E (2) y G (3).
5. Round Robin con quantum de 4 y de 5 ciclos, **cambiando de proceso con el quantum**.
6. Round Robin con quantum de 5 y de 6, **sin cambiar de proceso si solo ejecutó 2 ciclos o menos**; comparar con el punto 5.

Se revisan la próxima clase; el Excel con los ejemplos de clase sirve de plantilla.

---

## Conceptos clave

- **Turnaround time** = tiempo de terminación − tiempo de llegada (promediado); mide cuánto tarda un proceso en completarse desde que está listo.
- **FCFS:** FIFO sin interrupciones; simple pero muy sensible al orden de llegada.
- **SNJ:** ejecuta el más corto; requiere estimar duraciones, sirve en batch y es inviable en sistemas interactivos.
- **Prioridad:** cola ordenada por prioridad (empate = FIFO); criterios como E/S, memoria, CPU y *aging*.
- **Próximo a terminar:** SNJ con desalojo; si llega un proceso más corto que lo que le queda al actual, se cambia de inmediato.
- **Round Robin:** quantums fijos, cola FIFO y reencolado al final; base de la multiprogramación y de los SO modernos, complementado con prioridades y asignación dinámica de tiempo según la actividad.
- Los ejercicios ignoran los tiempos muertos del cambio de proceso.

---

## Fuera del PDF — logística, tareas y metodología

- **Tarea programada 1:** fecha de entrega el miércoles (los 8 días desde que se publicó); es la simulación FIFO de la clase anterior. Debe estar lista para la clase siguiente.
- **Tarea programada 2** (se publicará la próxima semana): la misma simulación extendida con **Round Robin y quantums**, con ciclos del orden de millones. La lógica nueva es contar el quantum, restar lo ejecutado del tiempo restante y reencolar.
- **Taller 1:** plazo hasta el **30** (antes de la medianoche); existe un espacio de entrega en el aula virtual (al final, sección «Entregas»).
  - Primera parte: capturas de pantalla **antes y después** de ejecutar los comandos y descripción de cada uno, organizadas en un documento, en una carpeta de OneDrive compartida (se entrega el enlace).
  - El video es solo evidencia de que se levantó la máquina (basta un video corto, ~30 s, mostrando la hora del sistema); los resultados de los comandos se prefieren en capturas.
- **Recursos:** el docente publicó el Excel con los ejemplos de clase y el formulario de repaso de la semana (recordar llenarlo). Recomienda videos sobre la historia de Linux y la disputa Microsoft vs. software libre, y sobre el ataque a la librería de compresión `xz` (2024, una puerta trasera casi llega a los servidores Linux de todo el mundo), que se retomará en el tema de **seguridad**.
- **Próxima clase (lunes siguiente):** revisión rápida de los ejercicios y dudas, y comienzo del tema de **administración de memoria**.
