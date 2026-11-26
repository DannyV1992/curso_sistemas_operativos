# Clase 12 — Sistemas operativos hoy: tendencias en memoria, procesos, dispositivos y archivos

**Curso:** IIIC2026 - Sistemas Operativos, LEAD University

**Docente:** Mario Miguel Agüero Obando

**Fecha:** 23 de noviembre de 2026 (estimada por continuidad semanal respecto a la Clase 11; en la grabación solo se mencionan fechas relativas: «hoy en 8», sábado 5 y lunes 7 de diciembre)

**PDF fuente:** `11 - Sistemas_Operativos_Modernos.pdf` (19 diapositivas). El número 11 es por tema, no por clase.

**Cobertura del PDF:** Completo (diapositivas 1 a 19). Las diapositivas 6, 8, 11 y 14 se comentaron solo en parte; los datos puntuales que no se mencionaron (siglas, versiones, tabla por plataforma) salen del PDF.

**Nota sobre la transcripción:** los primeros ~7 minutos son comentarios personales ajenos al curso (omitidos); las tareas y la logística quedan en la última sección. La clase fue corta y **no es evaluable**: son perspectivas de lo que pasa hoy en el mundo de los SO. Términos mal reconocidos corregidos por contexto: «Rost / Ross» = Rust, «6 C más más» = C y C++, «onnership» = ownership, «Copy on right» = copy-on-write, «electrum» = Electron, «Bercel» = Vercel, «ADN» = ARM, «n, p u» = NPU, «ex cuatro» = ext4, «post ITS» = POSIX, «Ian» = IA, «juices» = quizzes, «frotando» = thrashing (interpretación).

**Contexto.** Cierre del contenido del curso. Se revisa, con los mismos cuatro ejes de toda la materia (memoria, procesos, dispositivos, archivos), qué está cambiando en los SO de móviles y escritorio, para mostrar que el tema **no es un problema resuelto**. Hilo conductor: seguridad, IA en el dispositivo y convergencia entre móvil y escritorio.

---

## Ruta de la clase

| Bloque | Tema | Diapositivas |
|--------|------|--------------|
| — | Conversación inicial, tareas y examen (ver última sección) | — |
| 1 | Los cuatro pilares y por qué importa hoy | 2–3 |
| 2 | Memoria: compresión, páginas grandes, Rust, IA local, móvil vs. escritorio | 4–6 |
| 3 | Procesos: hardware heterogéneo, aislamiento y ciclo de vida móvil | 7–9 |
| 4 | Dispositivos: NPU, Arm, drivers, permisos | 10–11 |
| 5 | Archivos: copy-on-write, cifrado, nube, plataformas | 12–14 |
| 6 | Cambios recientes, tendencias y cómo se vive hoy | 15–17 |
| 7 | Conclusiones y preguntas | 18–19 |

---

## 1. Los cuatro pilares y por qué importa hoy (diapositivas 2–3)

| Pilar | Qué cambia hoy |
|-------|----------------|
| Memoria | Compresión, páginas más grandes, seguridad de memoria |
| Procesos | Núcleos heterogéneos, ciclo de vida y aislamiento |
| Dispositivos | NPU, Arm, drivers más seguros, permisos |
| Archivos | Copy-on-write, cifrado por defecto, nube |

**Por qué sigue importando:**

| Dato | Significado |
|------|-------------|
| **2027** | Último año de parches extendidos (ESU) de Windows 10; su soporte regular terminó en octubre de 2025. Quien siga en Windows 10 queda sin parches |
| **16 KB** | Tamaño de página que Google Play exige desde nov. 2025 a las apps que apuntan a Android 15+ |
| **Linux 7.0** | Versión (abril de 2026) en la que **Rust** dejó de ser experimental en el kernel. Recordar que Linux es un **kernel** |

- El SO dejó de ser «invisible»: define seguridad, batería, rendimiento y qué hardware sigue siendo útil.
- En seguridad, los equipos de TI viven corriendo: sale una vulnerabilidad, se aplica el parche en producción y a las pocas horas hay que revisar si ya salió otro.

---

## 2. Memoria (diapositivas 4–6)

> Más RAM requerida, más presión sobre ella y más exigencias de seguridad. La RAM disponible para comprar es cada vez menor, y todo el mundo necesita más.

### Prácticas modernas (diapositiva 5)

- **Comprimir antes que paginar:** a lo visto (particiones, segmentos, páginas) se suma que las páginas se **comprimen**. zram en Android y memoria comprimida en Windows y macOS: se comprime en RAM antes de escribir al disco o cerrar apps. Cuando una página va a la memoria virtual en disco, se guarda comprimida.
- **Páginas más grandes:** Android 15+ admite páginas de **16 KB**: arranque ~8 % más rápido y apps que abren ~3 % antes en promedio (hasta 30 %). Es un cambio de hardware y SO que obliga a **recompilar el código nativo**.

> **Nota:** en clase se dijo «páginas de 6 K que antes eran de 8»; según el PDF son de 16 KB (y las anteriores eran de 4 KB).

- **Seguridad de memoria:** Rust en kernels y drivers (Linux, Android, Windows) y etiquetado de memoria por hardware (ARM MTE, Apple MIE).
- **Memoria para IA local:** los modelos en el dispositivo piden más RAM. Los PC **Copilot+** exigen 16 GB y Apple Silicon comparte memoria entre CPU, GPU y NPU.

### Rust y la seguridad de memoria

- Cerca del **60–70 %** de las vulnerabilidades de seguridad provienen de mal manejo de memoria en **C y C++**. No es que manejen mal la memoria: son lenguajes muy cercanos a ensamblador que permiten al programador ser descuidado.
- Ejemplo de descuido en C (puntero colgante, *use-after-free*):

```c
int *ptr = malloc(sizeof(int));  // ptr guarda la dirección donde irá el 42
*ptr = 42;
free(ptr);                       // libera el bloque, pero ptr sigue guardando la dirección
```

  Tras `free`, el programa ya no «sabe» que ese bloque es suyo, pero la variable conserva la dirección. Un virus pegado al programa puede usarla para acceder a esa memoria.

> **Nota:** `free` libera el bloque del heap, no la variable `ptr`; en clase se describió como que «desaparece la flecha». El problema es que `ptr` sigue apuntando a memoria que ya no le pertenece.

- **Reglas estrictas de Rust** que eliminan esa clase de errores:
  - **Inmutabilidad por defecto:** una variable no cambia de valor salvo que se declare con `mut` (`let mut y = 5;`).
  - **Ownership (propiedad):** todo valor en memoria tiene un único dueño. Se puede **prestar** (*borrow*) pero no modificar, salvo permiso explícito dentro de un bloque de código.
  - Ejemplo: si una variable apunta al elemento 0 de una lista y luego se inserta otro elemento en la posición 0, la referencia apuntaría a un valor distinto. Rust lo rechaza: obliga a hacer una copia o sacar el valor de la lista.
- Es duro de aprender, pero está revolucionando kernels y drivers por la seguridad. Eso sí, **compila lento**.
- **Adopción citada en clase:** Microsoft migra código de C/C++ a Rust, Google lo usa en Android, Dropbox movió sus partes pesadas, el bloqueador de Brave fue reescrito y los navegadores incorporan partes en Rust. Caso reciente de **Discord**: migró su app de Electron a Rust; según la noticia mostrada, pasó de 1–4 GB de RAM a ~290 MB (≈25 % o menos) y de ~5,5 s de arranque a ~1 s. Electron consume mucha RAM; existe un framework en Rust para interfaces que lo compite.
- **Go** (aparte): nació en Google porque compilar para un *deploy* tomaba ~4 horas; se diseñó como lenguaje simple y de compilación muy rápida. Se hizo popular con **Docker**. El compilador de TypeScript se migró a Go y quedó 8–12 veces más rápido.
- La IA facilita migrar código entre lenguajes, lo que acelera estas mudanzas.

### Móvil frente a escritorio (diapositiva 6)

| | **Móvil (Android, iOS)** | **Escritorio (Windows, macOS, Linux)** |
|---|---|---|
| Swap | Sin swap clásico: el sistema cierra apps en segundo plano (LMKD en Android, Jetsam en iOS); se evita el *thrashing* | Memoria virtual completa: archivo de paginación más compresión |
| Estado | Cada app debe **guardar y restaurar su estado** al volver (por eso reabre donde se quedó) | Cargas pesadas conviven: navegadores, IDE, máquinas virtuales, modelos de IA |
| Límites | Android 17 añade topes de memoria por app | Linux: MGLRU y cgroups v2 reparten memoria entre servicios y contenedores |
| Otros | **zram**: «swap» comprimido dentro de la propia RAM | Observabilidad: Administrador de tareas, Monitor de actividad, htop, métricas de presión (PSI) |

- «Tener 20 apps abiertas» en un móvil es nominal: en realidad casi todas están cerradas con su estado guardado. La memoria no se puede ampliar en un celular.
- Aun con equipos mucho más potentes que los de hace 50 años, la limitación de recursos persiste; en escritorio, con más memoria, hay más contenedores y más administración de plataformas.

---

## 3. Procesos (diapositivas 7–9)

### Planificar en hardware heterogéneo (diapositiva 8)

- Los procesadores traen muchos núcleos (*cores*), pero no todos de alto rendimiento: casi nadie ocupa potencia máxima en todo. Hay **núcleos P (performance)** y **núcleos E (eficiencia)**, además de GPU y NPU.
- El planificador asigna **cada hilo al núcleo adecuado**:
  - Ejemplo: un modelo local generando código y un editor de video van a los núcleos fuertes; un Notepad con el guion va a un núcleo liviano; los cálculos del modelo se delegan a la GPU y la NPU.
  - Beneficio: no se ahoga el hardware ni se desperdicia energía. Esto agrega **complejidad al kernel**.
- Implementaciones: **EAS** en Android/Linux, **Intel Thread Director** y clases **QoS** en Apple.
- **Nuevos planificadores en Linux:** EEVDF reemplazó a CFS (6.6) y `sched_ext` permite planificadores escritos en eBPF (6.12).

### Aislamiento y segundo plano

- **Aislamiento por defecto:** sandbox por app, contenedores (mini «dockers» por aplicación) y seguridad basada en virtualización (VBS) en Windows. Si alguien entra, solo ve el entorno de ejecución y no toda la máquina.
- **Segundo plano bajo control:** Doze y App Standby (Android), BGTaskScheduler (iOS), modo eficiencia (Windows). Se mantienen vivos los procesos que no urgen sin gastar recursos.

### Ciclo de vida de una app móvil (diapositiva 9)

| Estado | Qué ocurre |
|--------|-----------|
| **Primer plano** | Interactúa con el usuario; máxima prioridad |
| **Visible** | En pantalla pero sin foco (ventana, PiP) |
| **Segundo plano** | Tareas limitadas y programadas por el SO; no interrumpen la de primer plano |
| **En caché** | Congelada en memoria, sin CPU |
| **Terminada** | El SO la cierra si necesita memoria |

- **En móvil, el SO —no el usuario— decide cuándo vive o muere un proceso.** El escritorio va en la misma dirección: pestañas que se suspenden, modo eficiencia y apps que deben tolerar ser congeladas para ahorrar batería.

---

## 4. Dispositivos (diapositivas 10–11)

| Cambio | Detalle |
|--------|---------|
| **La NPU como recurso del SO** | Unidad de procesamiento neuronal a la que el SO delega tareas de IA. Windows ML, Core ML y AICore (Android) reparten la IA entre CPU, GPU y NPU |
| **Arm en el escritorio** | Apple Silicon fue un éxito; macOS 27 solo corre en Apple Silicon; Windows 11 26H1 llega para Snapdragon X2. Arm gana por eficiencia energética |
| **Drivers más seguros** | Drivers nuevos (impresoras, ratones…) en Rust en Linux; DriverKit en macOS saca código del kernel |
| **Permisos granulares** | Cámara, micrófono, ubicación y Bluetooth cercano, con indicadores de uso visibles. En un navegador, un permiso puede darse a **una pestaña**, no a toda la app; el recurso protegido pasa a ser la pestaña |
| **Pantallas y modo escritorio** | Android 17 lleva ventanas y PiP interactivo a pantallas externas |
| **Un solo conector** | USB-C, USB4 y Thunderbolt unifican carga, video, datos y periféricos |

- Aparece un recurso nuevo que el SO debe administrar: la **NPU**. Windows 12 (o como se llame) podría incorporar un modelo local pequeño con el que se opere la computadora.
- Un teléfono conectado a un monitor ya funciona como PC.

---

## 5. Archivos (diapositivas 12–14)

### Prácticas modernas (diapositiva 13)

- **Copy-on-write (COW) y snapshots** (APFS, Btrfs, ReFS): antes copiar era duplicar físicamente todo el archivo (y con discos mecánicos eso implicaba rotación y movimiento de cabezal). Hoy se crea un **registro que apunta al original**; solo cuando se edita la copia se escriben **bloques nuevos** con los cambios y se conserva el original. Resultado: snapshots y respaldos casi instantáneos.
- **Cifrado por defecto:** cifrado por archivo en Android, Data Protection en iOS, FileVault y BitLocker en escritorio. Lo que cambia no es cómo se estructuran los archivos, sino que se **cifran** y que los permisos se manejan con más detalle.
- **Acceso con alcance:** Scoped Storage y selector de fotos en Android, sandbox en Apple: la app ve solo lo autorizado (por ejemplo, solo ciertas fotos o audios).
- **Nube bajo demanda:** OneDrive, iCloud Drive y Google Drive muestran todo y descargan solo lo que se abre (al hacer doble clic); también sincronizan cuando el equipo está inactivo.

### Archivos por plataforma (diapositiva 14)

| Plataforma | Sistema de archivos | Cifrado | Modelo de acceso |
|------------|--------------------|---------|------------------|
| Android | ext4 / F2FS | Por archivo (FBE), obligatorio | Scoped Storage, selector de fotos |
| iOS / iPadOS | APFS | Data Protection por clases | Sandbox + app Archivos |
| Windows | NTFS (ReFS en Dev Drive) | BitLocker / cifrado del dispositivo (opcional) | Carpetas de usuario + OneDrive |
| macOS | APFS | FileVault (propio de Apple) | Sandbox + permisos de privacidad |
| Linux | ext4, Btrfs, XFS | LUKS (opcional) | Permisos POSIX, portales Flatpak |

- macOS amplió el sistema de permisos de Linux/Unix. En Linux, ext4 es el predeterminado y los demás formatos permiten cifrado opcional. **POSIX** sigue siendo la base de permisos.

---

## 6. Cambios recientes y tendencias (diapositivas 15–17)

### Línea de tiempo 2025–2026 (diapositiva 15)

| Fecha | Evento |
|-------|--------|
| Oct 2025 | Fin del soporte regular de Windows 10 (ESU hasta oct. 2027) |
| Nov 2025 | Google Play exige páginas de 16 KB en apps para Android 15+ |
| Feb 2026 | Windows 11 26H1, versión para PC Arm con Snapdragon X2 |
| Abr 2026 | Linux 7.0: Rust deja de ser experimental |
| Jun 2026 | Android 17: límites de memoria por app y modo escritorio |
| Otoño 2026 | Windows 11 26H2, iOS 27 y macOS 27, centrados en rendimiento |

- **Windows 11 26H2** es la actualización más esperada: corrigió y quitó mucha de la integración con Copilot que había degradado el sistema, y recuperó velocidad.
- **Patrón común:** actualizaciones más frecuentes, más exigencias de hardware y foco en eficiencia antes que en funciones.

### Cinco tendencias (diapositiva 16)

| Tendencia | Idea |
|-----------|------|
| **IA en el dispositivo** | Modelos locales que compiten por RAM, NPU y batería |
| **Seguridad de memoria** | Rust y etiquetado por hardware frente a errores de memoria |
| **Convergencia** | El teléfono se vuelve escritorio y el escritorio se comporta como móvil. A corto plazo: comunicación inmediata teléfono-PC (p. ej. pasar todas las fotos por Bluetooth al acercarlos) en ~2 años |
| **Arm en todas partes** | Eficiencia por vatio como métrica clave; autonomía y manejo de energía cada vez más críticos |
| **Eficiencia primero** | Menos funciones nuevas, más rendimiento y autonomía |

### Cómo se vive hoy el ambiente (diapositiva 17)

| Usuario | Desarrollador | Equipos de TI |
|---------|---------------|---------------|
| Actualizaciones frecuentes y automáticas | Diseñar apps que se suspenden y restauran | Migrar el parque de Windows 10 antes de 2027 (la presión fuerte se espera en la segunda mitad de 2027) |
| Privacidad visible: permisos e indicadores | Recompilar código nativo para 16 KB y Arm | Cifrado y arranque seguro como requisito |
| El teléfono con monitor ya es un «PC» | Adaptarse a ventanas de cualquier tamaño (apps de móvil y escritorio) | Gestionar flotas mixtas x86, Arm y Apple Silicon |
| Presión para cambiar de equipo (Windows 10, IA local) | Aprovechar la NPU con APIs del sistema | Políticas para IA y datos en el dispositivo |

---

## 7. Conclusiones (diapositivas 18–19)

1. La **memoria** se comprime, se agranda por página y se protege con lenguajes seguros.
2. Los **procesos** se planifican en núcleos heterogéneos y viven aislados y bajo control del SO.
3. Los **dispositivos** suman NPU y Arm, con drivers más seguros y permisos visibles.
4. Los **archivos** están cifrados por defecto, versionados y cada vez más en la nube.

- Los SO siguen vigentes y siguen apareciendo novedades inesperadas (como comprimir la memoria virtual). Queda abierta la pregunta de si la IA podría llegar a generar un SO completo a partir de requerimientos.

---

## Conceptos clave

- **Compresión de memoria** (zram / memoria comprimida) antes de paginar a disco; **páginas de 16 KB** (arranque ~8 % más rápido; obliga a recompilar código nativo).
- **Rust:** inmutabilidad por defecto (`mut`), ownership y préstamo; evita punteros colgantes y errores de memoria que causan ~60–70 % de las vulnerabilidades en C/C++. Contrapartida: compila lento. **Go** prioriza compilar rápido.
- **Móvil:** sin swap clásico, el SO decide qué vive o muere (LMKD / Jetsam); las apps guardan y restauran su estado; ciclo de vida primer plano → visible → segundo plano → en caché → terminada.
- **Planificación heterogénea:** núcleos P y E, GPU y NPU; cada hilo va al hardware más apropiado (EAS, Thread Director, QoS).
- **Aislamiento:** sandbox por app, contenedores y VBS; permisos granulares (por pestaña, por foto) con indicadores visibles.
- **NPU** como recurso nuevo del SO; **Arm** dominando por eficiencia energética; **USB-C / USB4** unificando conectores.
- **Archivos:** copy-on-write y snapshots (APFS, Btrfs, ReFS), cifrado por defecto (obligatorio en Android; opcional en Linux y Windows), acceso con alcance y nube bajo demanda.
- **Fechas:** Windows 10 sin parches desde oct. 2027; Linux 7.0 con Rust estable (abr. 2026); Android 17 con límites de memoria (jun. 2026).
- **Tendencias:** IA local, seguridad de memoria, convergencia móvil-escritorio, Arm y eficiencia antes que nuevas funciones.

---

## Fuera del PDF — logística, tareas y metodología

### Tarea programada 4 (simulador de impresora 3D)

- Tarea muy pequeña, para practicar. **Entrega: sábado 5 de diciembre.** Se simula una impresora compartida en **dos modos**: con **bloqueo** o con **cola de espera**.
- **Menú:** crear proceso, solicitar impresora (indicando el proceso), liberar impresora, mostrar estado del sistema. Sin gráficos: basta un listado.
- **Modo bloqueo:** el proceso que pide la impresora estando ocupada queda **bloqueado** (detenido, esperando). Ejemplo: P1 toma la impresora → P2 y P3 quedan bloqueados; P1 la libera → la impresora pasa a P2. El estado debe mostrar quién la tiene y quiénes están bloqueados.
- **Modo cola:** el proceso que pide la impresora ocupada **no se bloquea**: su trabajo entra a la cola de impresión y el proceso sigue ejecutándose. Ejemplo: P1 asignado, P2 y P3 en cola (cola = P2, P3); P1 libera → P2 recibe la impresora y la cola queda con P3. El estado debe mostrar el proceso asignado, el contenido de la cola y los procesos vivos.
- Es la misma diferencia vista en el curso entre **proceso bloqueado** y **trabajo en cola** (*spooling*).

### Examen 2 (último examen del curso)

- **Una sola pregunta:** qué sabía antes del curso sobre cómo se ejecuta un programa y, luego, contar «la historia» de cómo se ejecutan las cosas en una computadora usando todos los conceptos posibles: qué pasa cuando se hace doble clic al acceso directo de un programa o se ejecuta un comando en la consola.
- Debe cubrir procesos, asignación de memoria, dispositivos y archivos, y situaciones clave: qué pasa al escribir en el teclado, al conectar un dispositivo, si el dispositivo está ocupado, al escribir un archivo y al leerlo.
- Extensión máxima: **hoja y media**. Plazo: 8 días después de la clase.

### Quizzes y notas

- **Primer corte de notas:** se anunció que se publica más tarde ese mismo día (con retraso, por motivos personales del docente). Casi todas las notas ya están calculadas; faltan el examen, la última tarea programada y los quizzes.
- **Quizzes pendientes (3 o 4):** plazo hasta el **7 de diciembre**; después de esa fecha no se da más tiempo. Los enlaces aún no estaban subidos al momento de la clase; el docente indicó que los sube después, sin precisar el día.
- Las notas finales se empezarían a entregar **probablemente** el 7 de diciembre.
- La semana siguiente hay una sesión corta, solo para dudas de quizzes, calificaciones o el examen.
- Recordatorio de la clase anterior: charla sobre Rust el 5 de diciembre y, de forma no evaluable, dedicar parte de diciembre a aprender Docker.
