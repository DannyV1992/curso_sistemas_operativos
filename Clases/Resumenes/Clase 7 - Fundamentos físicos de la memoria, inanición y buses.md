# Clase 7 — Fundamentos físicos de la memoria, inanición de procesos y buses

**Curso:** IIIC2026 - Sistemas Operativos, LEAD University
**Docente:** Mario Miguel Agüero Obando
**Fecha:** 19 de octubre de 2026 (estimada por continuidad semanal respecto a la Clase 6; no se menciona explícitamente en la transcripción)
**PDF fuente:** `6 - Fundamentos Fisicos de la administracion de Memoria.pdf` (16 diapositivas), `6 - Inanicion-Desfallecimiento-DeProcesos-1.pdf` (6 diapositivas) y `6 - Buses Memoria y Procesos.pdf` (13 diapositivas).
**Cobertura del PDF:**
- Fundamentos físicos: Completo (diapositivas 1 a 16).
- Inanición/Desfallecimiento: Completo (diapositivas 1 a 6).
- Buses: Parcial, diapositivas 1 a 12 de 13 (hasta «PCI»). La diapositiva 13 (preguntas) y la profundización en PCI Express, SATA y AGP quedan para la siguiente clase.

**Nota sobre la transcripción:** hay un receso de ~25 min a media clase y varias tangentes (anécdotas, colección de hardware antiguo, asuntos personales) que no aportan contenido de estudio. Términos mal reconocidos corregidos por contexto: «Memory gol/Bold» = Memory Wall, «Diustra» = Dijkstra, «Ron Robin» = Round Robin, «cereales» = seriales, «PSI» = PCI, «a G p» = AGP, «Sims/dim» = SIMM/DIMM, «Besa» = VESA, «Elisa» = EISA, «Microchanel» = Micro Channel. Algunas cifras y afirmaciones técnicas del docente se aclaran en notas.

**Contexto.** Cierre del bloque de memoria: lo que antes se vio desde el software (particiones, páginas, segmentos, memoria virtual) tiene límites y condicionamientos de **hardware** (buses, tamaño de palabra, velocidad de la RAM). Además se presenta la **inanición de procesos** (el último tema que conecta memoria con procesos) y se inicia la historia de los **buses**.

---

## Ruta de la clase

| Bloque | Tema | PDF y diapositivas |
|--------|------|--------------------|
| 1 | Buses de datos, direcciones y control; chipsets | Fundamentos, 2–5 |
| 2 | Cuánta memoria se puede acceder | Fundamentos, 6–8 |
| 3 | Especialización de buses | Fundamentos, 9 |
| 4 | Memory Wall | Fundamentos, 10–12 |
| 5 | Evolución de la RAM y tipos de chip | Fundamentos, 13–16 |
| — | Receso | — |
| 6 | Inanición de procesos: problema de los filósofos | Inanición, 2–6 |
| 7 | Buses: tipos, evolución e historia (ISA → PCI) | Buses, 2–12 |

---

## 1. Buses de datos, direcciones y control (Fundamentos, diapositivas 2–5)

- En la arquitectura de **Von Neumann** el acceso a la memoria principal es fundamental. La RAM es la memoria principal; antes la CPU interactuaba directamente con ella y con los dispositivos de E/S.
- Casi todas las computadoras usan esta idea con tres buses:

| Bus | Función |
|-----|---------|
| **Datos** | Lleva y trae los datos entre CPU y memoria |
| **Direcciones** | Indica **dónde** deben ponerse los datos o de dónde vienen |
| **Control** | Orquesta la operación: «lea» o «escriba» (es el que da la autorización) |

- Ejemplo: la CPU necesita un dato → coloca la dirección en el bus de direcciones → el bus de control indica LEER → la memoria escribe el contenido de esa dirección en el bus de datos → llega a la CPU.
- En el diagrama de los equipos basados en **Motorola 68000** (Macintosh, un chip más caro y superior al 8086) también aparecen los tres buses, con un bus especializado para caché. Siempre aparecen los tres porque fue la primera forma de **liberar a la CPU** de responsabilidades.
- En los **Intel i3/i5/i7** la CPU ya no habla con la memoria ni con los dispositivos directamente:
  - El **puente norte** controla memoria y PCI Express (gráficos); el **puente sur** es el hub de control de E/S.
  - En las CPU recientes, un controlador de memoria y uno de PCI Express están **dentro de la CPU**, y los periféricos se comunican por otro enlace (DMI).
  - Idea central: la CPU **delega** el acceso a memoria y a E/S en un subsistema.

---

## 2. Cuánta memoria se puede acceder (Fundamentos, diapositivas 6–8)

- La memoria direccionable depende del tamaño de la **palabra** del procesador. Los **registros** (memoria dentro de la CPU) definen cuántos bits se pueden manejar a la vez, y los buses normalmente tienen el mismo ancho que la palabra.

$$\text{direcciones posibles} = 2^{n} \quad (n = \text{bits del registro})$$

- Con registros de 64 bits: $2^{64}$ direcciones. Contando una dirección por byte son 16 exabytes (≈ 17 mil millones de GB); si cada dirección es una palabra de 64 bits, el total es 8 veces mayor (≈ 147 mil millones de GB).
- Es un **límite teórico**: llegar a él exigiría enormes cantidades de energía (gigavatios, varias plantas nucleares), de espacio (hectáreas solo para los chips) y de dinero. Una cosa es lo que se puede direccionar, otra lo que se puede instalar y otra lo que se puede pagar.

> **Nota:** la diapositiva 6 dice que con registros de 24 bits se accede «hasta 24 direcciones»; lo correcto es $2^{24}$ (≈ 16 millones). Las cifras exactas de energía y área del cálculo hecho en clase son aproximadas y sirven solo como orden de magnitud.

### Ejemplo histórico: 8086 y 8088
- El **8086** tenía registros y bus de 16 bits. El **8088** era el mismo procesador por dentro (16 bits) pero con bus de datos externo de **8 bits**, para abaratar la tarjeta madre: cada dato de 16 bits requería dos accesos. Más lento, pero más barato (prioridad comercial).
- Con palabras de 16 bits solo se direccionan $2^{16}$ palabras = **128 KB**. Para usar 1 MB se recurrió a **segmentos**: la memoria se parte en bloques y cada dirección se compone de *segmento + posición dentro del segmento*.
- Algunas computadoras logran más memoria «haciendo magia» con ayuda del SO, pero se necesita hardware especializado (controladores).

> **Nota:** en el 8086 real los segmentos son de 64 KB y las direcciones de 20 bits (registro de segmento × 16 + desplazamiento), lo que da 1 MB; la idea conceptual es la misma.

### Memoria byte direccionable (diapositiva 8)
- Una memoria es **byte direccionable** si, aunque el procesador trabaje con palabras de 16, 32 o 64 bits, se puede acceder a un **byte específico** dentro de la palabra. Los bloques directamente accesibles suelen ser múltiplos de la palabra.
- Esto complica el hardware: la memoria se divide en bloques, estos en palabras y estas en bytes, y el procesador y el SO deben saber direccionarlos. Aquí se unen hardware y software: lo que el procesador permite define el ensamblador, y este es la base de los compiladores y los lenguajes.

---

## 3. Especialización de buses (Fundamentos, diapositiva 9)

- Con buses especializados (PCI, USB, etc.) es común usar **controladores externos** que facilitan su administración. Por eso **cada CPU viene con un chipset relacionado**: la tarjeta madre debe tener un chipset compatible con la CPU.
- Gracias a esto cada componente evoluciona por separado (RAM, buses, chips) y el procesador solo necesita saber comunicarse con los chips. Se obtiene el máximo rendimiento de los dispositivos.

---

## 4. Memory Wall (Fundamentos, diapositivas 10–12)

- **Memory Wall:** la memoria, aunque cada vez es más rápida, **aumenta su rendimiento a un ritmo menor que el de los procesadores**.
- Datos: de 1986 a 2000 los procesadores de PC mejoraron ~**55 % anual** y las memorias solo ~**10 %**. Hacia 2004 las CPU toparon con el límite térmico (~3,8 GHz), y desde entonces el rendimiento crece con **múltiples núcleos**. Desde 1996 el microprocesador es del orden de 1 400 veces más rápido y la RAM ni siquiera 8 veces.
- Analogía: el reloj de la CPU es un tambor que marca ciclos; la CPU va a gran velocidad y la RAM «con una tortuga».

> **Nota:** las cifras de MHz de la RAM (p. ej. 8 000) son velocidades de transferencia (MT/s), no ciclos completos de reloj; la comparación con los GHz de la CPU es una referencia de magnitud.

### Solución: ancho de banda y caché (diapositivas 11–12)
- Como la **latencia** casi no ha mejorado, se aumentan la **capacidad** y el **ancho de banda**: no se compite en velocidad sino en **amplitud**.
- En lugar de mover datos sueltos, la RAM mueve a través de los buses **bloques grandes** (hasta GB por segundo) hacia memorias intermedias como la **caché**, para que la CPU no espere por la RAM. Ejemplo: se copia toda una página de una vez.

$$\text{Memory Wall} \;\Rightarrow\; \text{más ancho de banda} + \text{caché}$$

---

## 5. Evolución de la RAM y tipos de chip (Fundamentos, diapositivas 13–16)

### Evolución (diapositivas 13–14)
| Hito | Dato |
|------|------|
| Primeras RAM (1947) | Concebidas por Von Neumann, con núcleos magnéticos; acuñó el término *Random Access Memory* |
| **DRAM** | IBM, ~20 años después, con transistores. Barata; aún se usa donde la velocidad no es crítica |
| **SRAM** | Creada en los 60, más rápida que la DRAM, pero llegó al mercado en los 80 |
| **DDR SDRAM** | Años 2000. *Double Data Rate*: aprovecha los dos flancos del reloj (subida y bajada) para aumentar el ancho de banda y compensar la brecha con la CPU. Va por la generación 5 |
| **LPDDR** | Bajo consumo, usada en móviles |

> **Nota:** SDRAM significa *Synchronous* DRAM; no es una combinación de SRAM y DRAM.

### Empaquetamiento (diapositivas 15–16)
| | **SIMM** | **DIMM** |
|---|----------|----------|
| Contactos | Un solo lado (1 canal) | Ambos lados |
| Capacidad (diapositiva) | 4 MB a 64 MB | 32 MB hasta 1 GB por módulo; se agrupan para formar los chips modernos de 8 o 16 GB |
| Ancho de banda | 32 o 64 bits | 64 bits |
| Otros | Obsoleta en PC, pero barata; se sigue fabricando para autos, tablets básicas y dispositivos con poca memoria | Consume menos voltaje y es más rápida en frecuencia |

---

## 6. Inanición/desfallecimiento de procesos (Inanición, diapositivas 2–6)

### Origen (diapositiva 2)
- Hasta ahora se vio qué pasa cuando los recursos se asignan libremente mientras haya disponibles: **condiciones de carrera**, **bloqueos** y **esperas**. Ejemplos: una sola impresora o un solo bloque de RAM disputados por varios programas; varios programas escribiendo al disco duro; un navegador que se «pega» por completo.
- Si se es más estricto con las reglas, aparece otro problema: los procesos pueden **desfallecer** (*starvation*, inanición), es decir, esperar indefinidamente.

### El problema de los filósofos (diapositivas 3–6)
- Planteado por **Dijkstra** (el del algoritmo de grafos) en 1968: 5 filósofos comen espagueti de un tazón al centro; hay 5 platos y solo **5 tenedores**. Cada filósofo necesita **los dos tenedores** contiguos para comer (el filósofo 1 necesita F1 y F5, el 2 necesita F2 y F1, etc.).
- Desarrollo: el filósofo 1 toma F1 y F5 y come; el 3 toma F2 y F3. El 2 tiene hambre pero sus tenedores están ocupados. Cuando el 3 suelta, el 2 sigue sin poder comer porque el 1 no ha soltado F1; el 4 aprovecha y come, y el 5 sigue esperando. Cuando el 4 termina, el 3 retoma los tenedores. Los filósofos 2 y 5 nunca comen.
- Cada filósofo que toma sus dos cubiertos deja sin comer a los dos vecinos; quien suelta y vuelve a tomar rápido se aprovecha, y el resto muere de hambre.
- Paralelo con el SO: **los recursos son como los tenedores**. Si la asignación de recursos no previene el tiempo muerto de los procesos, estos pueden esperar para siempre solo porque «no hay la combinación perfecta de recursos disponibles».

### Lecciones
1. **Justifica Round Robin:** al rotar, evita procesos acaparadores y garantiza que todos tengan su turno; con turno para todos, todos tienen la oportunidad de conseguir sus recursos (salvo que un recurso quede retenido).
2. **No existe solución perfecta:** el problema solo se resolvería con recursos ilimitados para todos por tiempo ilimitado, y eso no existe. Lo que hay son formas de **aumentar la probabilidad de avance**.
3. Hay que **dar avance** a los procesos para que no queden colgados eternamente.

> **Nota:** el escenario es de **inanición** (algunos procesos nunca avanzan mientras otros sí). No es lo mismo que **interbloqueo** (*deadlock*), donde ninguno avanza porque cada uno espera lo que tiene otro.

> Como en la vida, no hay momento perfecto sino solo el ahora.

---

## 7. Buses (Buses, diapositivas 2–12)

### Concepto y tipos (diapositivas 2–3)
- Un **bus** es un subsistema que conecta partes de un computador. Originalmente todo estaba **centrado en la CPU**: todo debía pasar por ella. Analogía con el transporte público: ir de Alajuela a Cartago pasando siempre por el centro de San José. Se resolvió **descentralizando**: los buses se optimizaron y muchos trabajan aparte.

| Tipo | Cómo transmite | Notas |
|------|----------------|-------|
| **Paralelo** | Varias vías a la vez, una línea (carril) por bit; una autopista de varios carriles | Ejemplo: cable de datos **ATA/PATA** (el cable ancho tipo «faja») |
| **Serial** | Bit por bit, en fila | Más difícil de implementar, pero **más rápido y más barato**. Ejemplos: **USB** (*Universal Serial Bus*), **SATA** (*Serial ATA*) |

### Evolución (diapositivas 4–6)
1. **Un solo bus.** Las primeras computadoras eran monoproceso y monousuario: una instrucción como «cargar X de memoria a un registro» era lo único que hacía la máquina; solo se podía hacer una cosa por bus a la vez.
2. **Separación por función**, al haber varios procesos e interacción con el usuario: **bus de video**, **bus de E/S** (impresión, teclado, mouse) y **bus de memoria**.
   - Las primeras PC no tenían una tarjeta de video como la actual: el bus de video se conectaba a un pedazo de la memoria principal y mostraba lo que hubiera ahí **sin pasar por la CPU** (la CPU solo escribía en memoria). Esta idea permitió evolucionar los monitores: CGA (4 colores) → EGA (16 de 64) → VGA (1987; 256 colores simultáneos).
3. **Buses del sistema** (control, direcciones, datos), para que la CPU controlara mejor y más rápido la E/S.

### Funcionamiento y desarrollo (diapositivas 7–8)
- Si la CPU necesita un dato, el bus de control indica LEER; la memoria coloca en el bus de datos el contenido de la dirección indicada por el bus de direcciones.
- Los buses de **control** están modelados por el **juego de instrucciones**. Los de **memoria** tienen controladores para que los procesadores funcionen igual aunque cambie la tecnología (p. ej. DRAM). Los de **datos** apenas han cambiado. Donde más ha habido cambio es en los **buses de dispositivos**.

### Historia de los buses de dispositivos (diapositivas 9–12)
| Bus | Qué fue |
|-----|---------|
| **ISA** (*Industry Standard Architecture*) | Primer gran estándar de las PC. 8 bits, ampliado a 16. Usado por todos los dispositivos, incluso los discos. Universal y barato pero lento. Evolucionó a **EISA** |
| **Micro Channel** | Arquitectura propietaria de IBM (PS/2) para recuperar el mercado tras los clones; exigía pagar licencia a IBM |
| **IDE / PATA** | *Integrated Drive Electronics* = *Parallel ATA*. Primer estándar para almacenamiento; paralelo (después sustituido por SATA, serial) |
| **VESA** | Principios de los 90. Primera separación exitosa del video. Superado rápidamente por **AGP**, un bus gráfico más ancho que dio origen a las tarjetas de video potentes, abuelas de las actuales (aceleración y redes neuronales) |
| **PCI** (*Peripheral Component Interconnect*) | Estándar abierto y gratuito, muy exitoso. Puede funcionar **independientemente** y tiene su propio **chipset** especializado: un solo conjunto de chips controla mouse, teclado, sonido, etc., sin una tarjeta controladora por dispositivo (como en ISA). La lógica de interacción se delega por eventos y cada dispositivo se mejora por separado. Evolucionó a **PCI Express** |

> **Nota:** en la historia real, PCI fue desarrollado por Intel (1992); la respuesta de los fabricantes de clones a Micro Channel fue EISA. VESA es *Video Electronics Standards Association* y AGP es *Accelerated Graphics Port*.

### Por qué nació USB
- Las PC antiguas tenían ~20 tipos de puertos distintos (teclado DIN, PS/2 verde para teclado y morado para mouse, serial, paralelo para impresora, video, sonido…) y casi cada dispositivo requería su tarjeta de expansión (sonido, video, impresora). Hoy gran parte está integrada en la tarjeta madre. Esa proliferación de conectores y tarjetas motivó la creación del estándar **USB**.
- Pista sobre SATA vs PATA: SATA es serial, por lo que es más rápido, más barato y usa cables más delgados.

---

## Conceptos clave

- **Buses de datos / direcciones / control:** llevan los datos / indican dónde van o de dónde vienen / ordenan leer o escribir.
- **Chipset:** conjunto de chips que administra los buses y libera a la CPU; cada CPU requiere uno compatible.
- **Memoria direccionable:** $2^n$ direcciones según el ancho del registro; el límite teórico no es el práctico (energía, espacio, costo).
- **Byte direccionable:** se puede acceder a un byte específico dentro de una palabra.
- **Memory Wall:** la RAM mejora más lento que la CPU; se compensa con mayor **ancho de banda** y **caché**, no con menor latencia.
- **DRAM, SRAM, DDR SDRAM, LPDDR:** tecnologías de RAM. **SIMM** (un lado) y **DIMM** (dos lados).
- **Inanición (*starvation*):** un proceso espera indefinidamente por recursos mientras otros avanzan. El problema de los filósofos de Dijkstra la ilustra y justifica **Round Robin**.
- **Bus paralelo vs serial:** varias líneas a la vez vs bit por bit; el serial es más rápido y barato (USB, SATA).
- **Evolución de buses:** ISA → (Micro Channel) → IDE/PATA → VESA → AGP → PCI → PCI Express; la tendencia es especializar y descentralizar para liberar a la CPU.

---

## Fuera del PDF — logística, tareas y metodología

- **Entregas:** la Tarea Programada 2 y el Taller 2 se entregan en el aula virtual (sección de tareas → «entrega»).
- **Próxima clase:** quiz y un taller más corto (los dos talleres restantes serán más cortos). Se profundiza en los buses mediante una **actividad más interactiva** y se comienza con el estándar **USB**.
- **Actividad pendiente (Buses, diapositiva 13):** ¿por qué SATA es más rápido que PATA?, ¿por qué AGP superó a VESA?, ¿diferencias entre PCI Express y PCI?, y buscar puertos usados históricamente por las PC y con qué buses o dispositivos se usaban.

### Pendientes de clases anteriores (no se retomaron)
- **PDF 3, diapositiva 16:** punto 3 (Próximo a terminar), punto 5 (Round Robin con quantum 5) y punto 6 (Round Robin con regla de ≤ 2 ciclos).
- **PDF 4, diapositiva 12:** qué estrategia (First Fit o Best Fit) aplica la figura del ejemplo.
