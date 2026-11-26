# Simulador de impresora 3D compartida (modo BLOQUEO y modo COLA)

**Tarea Programada 4** · Sistemas Operativos (IIIC 2026) · LEAD University

El programa simula una única impresora 3D que piden varios procesos (P1, P2, P3, ...). Al iniciar se elige cómo reacciona el sistema cuando la impresora está ocupada, y ese modo no cambia durante la simulación:

- **BLOQUEO (sin cola):** la solicitud se rechaza y el proceso queda `BLOQUEADO`. Nadie lo atiende automáticamente; debe volver a solicitar la impresora (reintento manual).
- **COLA (FIFO):** el proceso pasa a `ESPERANDO` en una cola. Al liberarse la impresora se asigna automáticamente al primero de la cola.

Solo usa la biblioteca estándar de Python (`sys`, `collections.deque`), sin `pip install`. Requiere Python 3.10 o superior (probado con 3.12). La simulación es por eventos: no hay hilos ni temporizadores, el usuario decide cuándo llega una solicitud y cuándo termina un proceso.

## Cómo ejecutarlo

```powershell
python impresora.py
```

> Si `python` no se reconoce, prueba con `py impresora.py` (Windows) o `python3 impresora.py` (Linux/macOS).

Primero pregunta el modo (1 = BLOQUEO, 2 = COLA) y luego muestra este menú:

| Opción | Acción |
|--------|--------|
| 1 | Crear un proceso (se numera solo: P1, P2, P3, ...; nace en estado `LISTO`) |
| 2 | Solicitar la impresora: pide el proceso (acepta `P1`, `p1` o `1`) |
| 3 | Liberar la impresora: termina el proceso que la está usando |
| 4 | Mostrar el estado del sistema (quién usa la impresora, bloqueados o cola, y el estado de cada proceso) |
| 5 | Salir: muestra las estadísticas finales |

Al terminar la entrada (Ctrl+Z en Windows, Ctrl+D en Linux/macOS) el programa también muestra las estadísticas y sale.

### Repetir una sesión sin escribir cada opción

Cada archivo de `casos/` contiene lo que se escribiría a mano, una entrada por línea (la primera es el modo). Al redirigirlo, el programa repite lo que lee para que la traza se entienda:

```powershell
python impresora.py < casos/ejemplo_seccion4_cola.txt
```

Para regenerar todas las evidencias (PowerShell, desde `Programada_4/`):

```powershell
Get-ChildItem casos/*.txt | ForEach-Object { Get-Content $_ | python impresora.py > "evidencias/$($_.BaseName).out.txt" }
```

## Estados de los procesos

| Estado | Significado |
|--------|-------------|
| `LISTO` | Puede solicitar la impresora (estado inicial y al terminar de usarla) |
| `USANDO` | Tiene asignada la impresora |
| `BLOQUEADO` | Solicitó la impresora y no la obtuvo (solo en modo BLOQUEO) |
| `ESPERANDO` | Está en la cola FIFO (solo en modo COLA) |

Un proceso `USANDO` o `ESPERANDO` no puede volver a solicitar la impresora (el programa lo rechaza con un mensaje). Un proceso `BLOQUEADO` sí: el reintento equivale a despertarlo y hacer una solicitud nueva.

## Decisiones de implementación

- **Contadores del reto adicional:** *solicitudes realizadas* cuenta cada solicitud aceptada, incluidos los reintentos de un proceso bloqueado. *Solicitudes sin impresora inmediata* cuenta las que encontraron la impresora ocupada. *Asignaciones exitosas* cuenta cada vez que un proceso recibe la impresora, ya sea al pedirla estando libre, en un reintento o automáticamente desde la cola. Las solicitudes rechazadas por error (proceso `USANDO` o `ESPERANDO`) no se cuentan.
- **Liberar:** la opción 3 no pide identificador, porque solo un proceso puede tener la impresora; libera a quien la esté usando. Si está libre, avisa del error.
- **Impresora libre con bloqueados:** en modo BLOQUEO, la opción 4 muestra un aviso cuando la impresora está `LIBRE` pero hay procesos `BLOQUEADOS` que la necesitan.
- **Orden en la cola:** si un proceso libera la impresora y la vuelve a pedir mientras otros esperan, entra al final de la cola.
- **Al salir** se listan los procesos que se quedaron sin obtener la impresora (bloqueados o en cola).

## Nota: proceso bloqueado vs. trabajo en cola (*spooling*)

En clase se explicó el modo COLA como la cola de impresión (*spooling*): el proceso **no se bloquea**, su trabajo queda encolado y el proceso sigue ejecutándose. El enunciado, en cambio, pide que el proceso pase al estado `ESPERANDO` mientras está en la cola FIFO y lo reciba automáticamente al liberarse la impresora. Esta implementación sigue el enunciado, porque es lo que define los estados y la rúbrica.

La diferencia de fondo entre los dos modos se mantiene igual: en BLOQUEO nadie atiende al proceso rechazado y este debe reintentar por su cuenta; en COLA el sistema guarda la solicitud y la atiende solo, en orden de llegada. El estado `ESPERANDO` representa el trabajo pendiente en la cola. La solicitud ya está registrada, a diferencia de `BLOQUEADO`, donde no hay nada registrado.

## Organización del código (`impresora.py`)

| Función / clase | Responsabilidad |
|-----------------|-----------------|
| `Simulador` | Estado de la simulación (modo, procesos, usuario actual, `deque` de la cola, contadores) y las operaciones `crear_proceso`, `solicitar` y `liberar` |
| `formatear_estado`, `formatear_estadisticas`, `formatear_cola`, `mostrar_menu` | Presentación |
| `leer`, `elegir_modo` | Lectura y validación de la entrada |
| `opcion_*`, `cierre`, `main` | Una función por opción del menú y el ciclo principal |

## Casos de prueba (en `casos/`, salidas en `evidencias/`)

| Caso | Qué comprueba |
|------|---------------|
| `ejemplo_seccion4_bloqueo` | Ejemplo del enunciado en modo BLOQUEO: P2 y P3 bloqueados, P1 libera, P3 reintenta y es asignado. Contadores: 4 / 2 / 2 |
| `ejemplo_seccion4_cola` | Ejemplo del enunciado en modo COLA: cola `[P2, P3]`, asignación automática a P2 y luego a P3. Contadores: 3 / 2 / 3 |
| `bloqueado_nunca_reintenta` | P2 nunca reintenta: la impresora queda `LIBRE` con un proceso bloqueado esperando para siempre |
| `bloqueo_reintento_fallido` | Reintento con la impresora todavía ocupada (sigue bloqueado), ids en minúscula o solo número |
| `cola_libera_y_vuelve_a_pedir` | P1 libera y vuelve a pedir: entra al final de la cola (`[P3, P1]`) |
| `errores_validacion` | Modo inválido, opción inválida, solicitar sin procesos, liberar con la impresora libre, proceso inexistente o vacío, solicitar estando `USANDO` o `ESPERANDO` |

## Comparación del comportamiento observado en ambos modos

1. En BLOQUEO el sistema operativo no guarda nada: el proceso rechazado debe acordarse de reintentar. En COLA el sistema guarda el pedido y lo atiende solo.
2. En el ejemplo del enunciado, BLOQUEO terminó con 4 solicitudes y 2 asignaciones: P2 sigue bloqueado y su solicitud inicial se perdió. COLA terminó con 3 solicitudes y 3 asignaciones: los tres procesos usaron la impresora.
3. En BLOQUEO la impresora quedó `LIBRE` mientras P2 y P3 la necesitaban. Con COLA eso no pasa: al liberarse pasa directo al primero de la cola.
4. COLA es justa (orden de llegada estricto, nadie se salta a otro). En BLOQUEO gana quien reintente primero, y P3 le ganó a P2 aunque P2 pidió antes.
5. BLOQUEO es más simple de implementar (sin estructura de datos) y no obliga al sistema a recordar a nadie. COLA necesita la estructura y la lógica de reasignación.
6. BLOQUEO necesita más solicitudes para atender a los mismos procesos, porque cada reintento fallido cuenta como solicitud sin éxito. COLA hace una sola solicitud por uso.
7. Con COLA el dispositivo se aprovecha mejor: no hay tiempo muerto entre un uso y el siguiente.

## Pregunta de reflexión

**¿Qué ventajas y desventajas tiene cada estrategia?**

- **BLOQUEO.** Ventajas: implementación mínima, no hay estructura que mantener y el sistema no necesita llevar la cuenta de quién espera. Desventajas: hay inanición (un proceso puede perder una y otra vez contra otros), el dispositivo puede quedar libre sin usarse, el orden de llegada no se respeta y la responsabilidad de reintentar recae en el proceso (con el costo extra de solicitudes).
- **COLA FIFO.** Ventajas: justicia por orden de llegada, sin inanición, la impresora se reasigna al instante y los procesos no tienen que reintentar. Desventajas: hay que mantener la cola y sus reglas; un proceso que usa la impresora mucho tiempo hace esperar a todos los de atrás (efecto convoy); y el sistema debe decidir qué pasa si un proceso en cola desaparece o termina.

**¿Qué sucede si un proceso bloqueado nunca vuelve a solicitar la impresora?**

Se queda `BLOQUEADO` indefinidamente: nadie lo despierta, nunca recibe la impresora y no avanza (inanición). La impresora puede estar `LIBRE` todo ese tiempo y el proceso sigue sin ser atendido, porque en modo BLOQUEO ninguna liberación asigna el dispositivo automáticamente. El caso `bloqueado_nunca_reintenta` lo muestra: al salir, P2 queda bloqueado y la impresora libre. En modo COLA esto no ocurre, porque el proceso espera dentro de la cola y recibe la impresora cuando le toca.
