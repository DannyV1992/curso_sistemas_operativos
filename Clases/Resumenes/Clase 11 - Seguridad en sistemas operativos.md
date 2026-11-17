# Clase 11 — Fundamentos de seguridad y seguridad en Linux y Windows

**Curso:** IIIC2026 - Sistemas Operativos, LEAD University

**Docente:** Mario Miguel Agüero Obando

**Fecha:** 16 de noviembre de 2026 (estimada por continuidad semanal respecto a la Clase 10; en la grabación solo se menciona que se está en la semana 11)

**PDF fuente:** `10 - Fundamentos de Seguridad.pdf` (19 diapositivas) y `10 - Seguridad_en_Sistemas_Operativos_v3.pdf` (38 diapositivas). Ambos llevan el número 10 porque la numeración es por tema, no por clase.

**Cobertura del PDF:**

- Fundamentos de Seguridad: Completo (diapositivas 1 a 19).
- Seguridad en Sistemas Operativos v3: Completo (diapositivas 1 a 38), pero el tramo final (Windows y seguridad moderna) se dio con prisa. Las diapositivas 27 y 28 (memoria en Windows) no se comentaron y salen solo del PDF; las tablas de siglas (21, 24, 34) y la lista de gusanos de la diapositiva 23 solo se tocaron de pasada.
- La diapositiva 30 de `9 - Administración de Archivos.pdf` (listas de capacidad), que quedó pendiente de la Clase 10, no aparece en esta transcripción.

**Nota sobre la transcripción:** los primeros ~51 minutos son una conversación ajena al curso (omitida). Hay un receso a mitad de clase. Términos mal reconocidos corregidos por contexto: «the night of Service / D o s» = Denial of Service, «while tuping / man in the virus» = wiretapping / man-in-the-middle, «querberos» = Kerberos, «Ruth» = root, «smot / Zero» = chmod, «post IT» = POSIX, «Selling Inux / Lab Armor» = SELinux / AppArmor, «D a C / Mac» = DAC / MAC, «ENT / Mario no» = NT / Microsoft, «chips Wifi» = TPM, «tustep authentication» = two-step authentication, «Michel Angelo» = Michelangelo.

**Contexto.** Se abre el bloque de seguridad. Primero los fundamentos: por qué un SO que comparte recursos tiene que protegerlos, qué ataques y programas maliciosos existen y qué defensas básicas se usan. Luego, cómo implementan la seguridad Linux y Windows (y por qué Windows tardó décadas en alcanzar a Linux), y por último los principios de la seguridad moderna.

---

## Ruta de la clase

| Bloque | Tema | PDF y diapositivas |
|--------|------|--------------------|
| — | Conversación inicial (fuera de tema) | — |
| 1 | Dilema compartir/proteger y propiedades de seguridad | Fundamentos, 2–3 |
| 2 | Autenticación vs. autorización | Fundamentos, 4–5 |
| 3 | Intrusión y tipos de ataque | Fundamentos, 6–7 |
| 4 | Malware (repasado tras el receso) | Fundamentos, 8–13 |
| 5 | Cuatro pilares de la protección | Fundamentos, 14–19 |
| — | Receso | — |
| 6 | Linux: modelo base, identidad y procesos | Seguridad, 4–8 |
| 7 | Linux: memoria | Seguridad, 9–12 |
| 8 | Linux: dispositivos y archivos | Seguridad, 13–17 |
| 9 | Windows: del DOS a NT y el costo de la retrocompatibilidad | Seguridad, 18–23 |
| 10 | Windows NT: modelo de seguridad | Seguridad, 24–30 |
| 11 | Linux y Windows lado a lado | Seguridad, 31 |
| 12 | Seguridad moderna | Seguridad, 32–38 |

---

## 1. El dilema y las propiedades de seguridad (Fundamentos, diapositivas 2–3)

- **El gran dilema:** el SO debe **compartir** recursos (CPU, memoria, dispositivos, archivos) entre muchos procesos y usuarios, y a la vez **protegerlos**. Ambas metas se oponen, y el problema crece con la cantidad de usuarios y procesos concurrentes. En un simulador de tarea programada casi no se nota; en un sistema real sí.
- Un SO que resiste ataques necesita cuatro propiedades:

| Propiedad | Qué exige | Estrategias |
|-----------|-----------|-------------|
| Resistencia a ataques | Repeler ataques | Autenticación, controles de acceso, encriptación, filtrado, aislamiento funcional |
| Reconocer ataques y daños | Detectar problemas y daños | Chequeo de integridad, estructuras redundantes físicas |
| Recuperación después de un ataque | Limitar daños, restaurar servicios, volver a trabajar | Replicación de datos, respaldos del sistema |
| Adaptación a ataques | Actualizarse lo antes posible | Detectar patrones de ataques |

- **Aislamiento funcional:** cada cosa se maneja por separado. Lo que se escribe en Word no debe aparecer en Notepad.
- **Chequeo de integridad:** copias de seguridad y claves de verificación (*checksum*) para detectar que algo fue alterado.
- **Estructuras redundantes físicas:** discos en espejo con intercambio en caliente (*hot-swap*). Un segundo disco se sincroniza con el de producción; si el primario falla, se retira y el sistema sigue sobre el otro avisando que se reemplace.

> **Nota:** en clase se mencionó SCSI; la técnica descrita es el espejo de discos (RAID 1).

---

## 2. Autenticación vs. autorización (Fundamentos, diapositivas 4–5)

Es el **punto clave** del tema y una pregunta de repaso frecuente.

- **Autenticación:** ¿usted es quien dice ser? (demostrarlo con clave, huella, cara).
- **Autorización:** ¿usted puede hacer lo que quiere hacer?
- Ejemplo del bar: un menor entra con la cédula de un adulto de 40 años → falla la **autenticación** (no es esa persona). Si en cambio tiene una cédula falsa perfecta, con su cara y sus huellas, pero con su fecha de nacimiento real, **sí se autentica** (es quien dice ser) pero falla la **autorización**: por su edad no tiene derecho a entrar.
- Son controles independientes: se puede pasar el primero y fallar el segundo.

---

## 3. Intrusión y tipos de ataque (Fundamentos, diapositivas 6–7)

### Intrusión no intencional (diapositiva 6)
- La mayoría de los ingresos problemáticos se deben a **usuarios descuidados y accesos mal asignados**: configuraciones que no se hacen o se modifican sin cuidado. Es la primera causa de intrusiones. El problema más grande, claro, son las intrusiones intencionadas.
- Ejemplo típico: los routers y equipos de red vienen con un **administrador por omisión**. Hay que cambiarle la clave, crear un administrador propio y **deshabilitar el de fábrica** (si se quiere rehabilitar, que sea solo físicamente, con el botón de reset). Quien ubique la IP del dispositivo de salida a Internet y encuentre el usuario por defecto entra con derechos totales. Se deja por pereza.

### Tipos de ataque (diapositiva 7)
- **DoS (*Denial of Service*):** sobrecargar un sistema con tantas solicitudes (p. ej. pedir páginas sin parar a un servidor web) que no puede ofrecer servicios. No busca entrar sino agotar el servidor; un servidor solo no lo aguanta, únicamente infraestructuras diseñadas para eso (Amazon, Google).
- **Browsing:** un usuario consigue permiso de lectura en un repositorio al que no debería acceder. Solo **ver** ya es grave, a veces tanto como escribir.
- **Wiretapping:** acceso pasivo a la comunicación, «escuchando» y copiando la información. Su versión avanzada es el ***sniffing***. Ejemplo: ubicar la forma en que dos equipos se comunican, poner otra computadora en medio y leer lo que se envía mientras el destinatario cree que nada pasó.
- **Trapdoors / backdoors:** puertas no documentadas que se dejan abiertas, normalmente por mala práctica o como «elemento de diagnóstico». Dan acceso a la información sin que el usuario lo note. Windows tuvo muchos; en Linux se han intentado y se han detectado.

> **Nota:** el *sniffing* es pasivo (solo escucha). Interponerse y hacerse pasar por uno de los extremos, retransmitiendo o alterando datos, es un ataque *man-in-the-middle*, activo.

### Ingeniería social (no está en el PDF)
- **La mayor debilidad es el ser humano.** Ejemplo: en un café Internet se conversó ~15 días con usuarios recolectando datos personales (nombre de la mascota, fecha de nacimiento) y con ellos se adivinaron las contraseñas de unas seis personas (nombre de la mascota + fecha).
- Caso reciente en el ecosistema Linux: se presionó (*bullying*) al único mantenedor de un proyecto hasta introducir código fraudulento (ver sección 12, cadena de suministro).

---

## 4. Malware (Fundamentos, diapositivas 8–13)

### Virus (diapositiva 8)
- Pequeño programa que altera el funcionamiento del computador: **autoejecutable** y **autorreplicante**. El efecto va desde volver lento el equipo hasta borrar o secuestrar archivos. **Ningún virus puede o debe considerarse benigno.**

### Tipos de virus (diapositivas 9–10)

| Tipo | Qué hace |
|------|----------|
| **Infector de archivos** | Infecta archivos de cierto tipo (el más conocido, los `.exe` de PC; también Word, Excel). Se convierte en un proceso residente que infecta otros. Hoy son menos porque las aplicaciones se cuidan más |
| **Boot sector** | Se aloja en el *boot sector* de un disco de arranque (donde se lee dónde buscar el SO); se activa cada vez que el sistema levanta. Clásico de MS-DOS |
| **Master Boot Record** | Puede caer en cualquier SO (también Linux, aunque pocos casos): se carga en memoria y luego carga el arranque real del SO, que copió a otra parte |
| **Múltiples** | Infectan el sector de arranque **y** los ejecutables. Muy difíciles de quitar: puede requerir reinstalar con un borrado fuerte del disco (restablecerlo a estado de fábrica; no basta con «borrar») |
| **Macro** | Se pegan a utilitarios con un «motor» de ejecución (Word, Excel con macros en Visual Basic). Consecuencia de un mal diseño de permisos; por eso Office bloquea la edición de archivos descargados de Internet |

### Gusanos y troyanos (diapositiva 11)
- **Gusano:** programa que se copia **a través de la red, sin necesidad de infectar un archivo**; se mueve solo entre computadoras. Fueron muy comunes al inicio de Internet.
- **Troyano:** programa o proceso que se instala **sin autorización del usuario**, disfrazado de algo legítimo (como el caballo de Troya: se copia algo y lo copiado daña). Por eso la revisión de código de las Apps de Apple (con agentes automáticos que comprueban que no alteren lo que no deben) hace diferencia.

### Bombas lógicas (diapositiva 12)
- Programa hecho para **hacer daño** (borrar, encriptar o renombrar archivos) en un momento o ante una condición dada. Variante: **bomba de tiempo**. Ejemplo: *Michelangelo* (años 90) actuaba en la fecha de nacimiento del artista (borraba archivos o reiniciaba el equipo).

### Otras sutilezas (diapositiva 13)
- **Spyware:** toma capturas de pantalla o revisa los archivos que se guardan para copiar los datos.
- **Keyloggers:** registran todo lo que la persona escribe. Hay programas que son ambas cosas, o combinaciones de todo lo anterior.
- **Ransomware** («la nueva moda»): bloquea los archivos y cobra el rescate en bitcoins, es decir, secuestra la computadora.

---

## 5. Los cuatro pilares de la protección (Fundamentos, diapositivas 14–19)

Antivirus, firewalls, correcta configuración de seguridad/acceso/derechos y encriptación (más mantener siempre las actualizaciones de seguridad).

### Antivirus (diapositiva 15)
- Lo más básico, pero **siempre van detrás**: son **reactivos**, actúan cuando la amenaza ya es conocida y probablemente ya hay afectados («como una medicina»). Solo en los últimos años empezaron a prevenir. Hay que mantenerlos actualizados lo antes posible.
- Los autores de virus compran los antivirus y los analizan para ver cómo saltárselos. Un administrador debe estar **constantemente informado** y bloquear amenazas incluso antes que el antivirus.

### Firewalls (diapositiva 16)
- Pueden ser de hardware o de software. Funcionan como una «Gran Muralla China»: bloquean los accesos desde y hacia un computador **por todos sus puertos**, registran quién envió qué y hacia dónde (*log* de los intentos) y reportan quien intenta entrar sin autorización.
- Incluyen **filtrado de paquetes** (*packet filtering*) para revisar la información que entra y sale; muchos detectan *phishing*, troyanos y *cookie trackers*. Los de hardware son muy complejos.
- En las organizaciones definen además la zona militarizada (dentro) y la desmilitarizada (fuera).

> **Nota:** en la práctica la zona desmilitarizada (DMZ) es un segmento intermedio entre la red interna y el exterior, donde se colocan los servidores accesibles desde Internet.

### Seguridad, acceso y derechos (diapositivas 17–19)
- **Autenticación fuerte**, como **Kerberos**: motor que protege las credenciales con criptografía; los servidores Windows modernos incluyen motores así de fuertes.

> **Nota:** en clase se dijo que usa criptografía de llave abierta. Kerberos se basa sobre todo en criptografía simétrica y tiquetes temporales en lugar de enviar la contraseña; la llave pública es una extensión opcional.

- Usar **grupos** para distribuir políticas, en lugar de asignar derechos usuario por usuario.
- **Política de passwords razonable, que no abrume al usuario.** Basta: mínimo 8 caracteres, una mayúscula, un número y un carácter especial. Una política absurda (12 caracteres, vocales y consonantes en cierto orden, símbolos por mitad, frases de 80 caracteres…) lleva a olvidar credenciales y a perder tiempo recuperándolas.
- **Alternativas al password** para la autenticación en dos pasos (*two-step*): tarjetas de acceso, **biometría** (datos biológicos) y aplicaciones o SMS en el celular.

---

## 6. Linux: modelo base, identidad y procesos (Seguridad, diapositivas 4–8)

### Modelo base (diapositivas 4–5)
- Linux retoma la filosofía de **Unix**: la seguridad se incorpora **desde el diseño**. Un proceso arranca con la menor cantidad de derechos posible y no accede al hardware: depende de pedirlo al kernel, que decide.
- Todo proceso corre a nombre de un usuario (**UID**) y de sus grupos (**GID**). El kernel decide con números, no con nombres.
- **root (UID 0):** superusuario, lo más cerca del kernel que se puede estar; lo puede casi todo, y por eso es el **punto débil** del modelo clásico.
- El kernel corre en **modo privilegiado (anillo 0)** y los programas en **modo usuario (anillo 3)**. La **única puerta** al kernel son las **llamadas al sistema** (*syscalls*): una interfaz preconstruida, no una ventana. Los programas solo tienen lo que el SO les da.

> **Nota:** los «anillos» de protección de la CPU (0 = kernel, 3 = usuario) no son los tres tríos de permisos `rwx` (dueño, grupo, otros) de los archivos; en clase se mezclaron.

| Sigla | Significado | En palabras simples |
|-------|-------------|---------------------|
| UID / GID | User / Group Identifier | Número que identifica a cada usuario y grupo |
| PID | Process Identifier | Número único de cada proceso (guardado en su PCB) |
| syscall | System call | Solicitud de un programa al kernel (abrir un archivo, crear un proceso) |
| DAC | Discretionary Access Control | El dueño del recurso decide quién accede |
| MAC | Mandatory Access Control | Una política del sistema decide; ni el dueño ni root la cambian |
| ACL | Access Control List | Lista de «quién puede hacer qué» pegada a un recurso |
| LSM | Linux Security Modules | Punto del kernel donde se conectan SELinux y AppArmor |

### Procesos: identidad y privilegios (diapositiva 6)
- **Credenciales:** cada proceso lleva UID/GID real y efectivo; los hijos los heredan al hacer `fork()`.
- **setuid / setgid:** un ejecutable corre con la identidad de su dueño (p. ej. `passwd` corre como root). Útil, pero fuente histórica de escaladas de privilegio. Es lo que permite ejecutar algo «como administrador» y no como el usuario.

> **Nota:** anteponer `sudo` a un comando es un mecanismo relacionado (ejecutar con otra identidad) pero distinto de los bits setuid/setgid.

- **Capabilities:** el poder de root se divide en unos 40 permisos (`CAP_NET_ADMIN`, `CAP_SYS_TIME`…); un servicio recibe solo los que necesita.
- **Aislamiento entre procesos:** un proceso solo puede enviar señales o depurar (`ptrace`) a procesos de su mismo usuario.

### Procesos: confinamiento (diapositiva 7)

| Mecanismo | Qué hace | Dónde se usa |
|-----------|----------|--------------|
| Namespaces | Cada proceso ve su propia versión de PIDs, red, montajes y usuarios | Docker, Podman |
| cgroups | Limita CPU, memoria y E/S por grupo de procesos (y permite monitorear su uso) | systemd, Kubernetes |
| seccomp-bpf | Filtra cuáles syscalls puede invocar un proceso | Chrome, Docker, Android |
| SELinux / AppArmor | Control obligatorio (MAC): la política manda aunque sea root | RHEL, Ubuntu, Android |
| Landlock | Un proceso sin privilegios se restringe a sí mismo (*sandbox* de aplicaciones) | Aplicaciones |

- Un **contenedor = namespaces + cgroups + seccomp + capabilities reducidas**: una «pequeña máquina virtual» donde el proceso puede hacer lo que quiera, pero solo ahí. Sobre estas ideas se construyeron Docker y Kubernetes.

> **Nota:** en clase se atribuyó esto a Landlock; según el PDF, los contenedores se apoyan sobre todo en namespaces y cgroups, y Landlock es un mecanismo de autorrestricción para aplicaciones.

### DAC contra MAC (diapositiva 8)

| | **DAC (discrecional)** | **MAC (obligatorio)** |
|---|---|---|
| Quién decide | El dueño del recurso | Una política central del administrador, en el kernel |
| Mecanismo | Permisos `rwx` y ACL | Cada proceso y archivo lleva una etiqueta o perfil |
| Root | Se salta todas las reglas | Se aplica **incluso a root** |
| Riesgo | Si comprometen un proceso de root, se pierde el sistema | Un servidor web comprometido sigue sin poder leer `/etc/shadow` |

- Linux aplica **ambos**: primero los permisos DAC y después la política MAC; **los dos deben permitir el acceso**. Para leer un archivo del propio directorio normalmente basta el DAC; se usan más los dos mientras más cerca del hardware se esté.

---

## 7. Linux: memoria (Seguridad, diapositivas 9–12)

*(Los términos de las diapositivas 9 y 10 son de contexto; no se preguntan en el quiz de seguridad.)*

### Conceptos básicos (diapositivas 9–10)
- **Kernel:** el único código con acceso total al hardware; corre en **modo supervisor** de la CPU.
- **Dirección virtual / física:** la que ve el programa / la posición real en RAM. **Página:** bloque de tamaño fijo (normalmente 4 KB) al que se le asignan permisos. **Tabla de páginas:** mapa por proceso de virtuales a físicas, con permisos.
- **Pila (*stack*):** variables locales y dirección de retorno de cada función. **Heap:** memoria que el programa pide mientras corre. **Búfer:** espacio fijo para datos; **se desborda** al escribir más de lo que cabe y pisa la memoria vecina.
- **MMU** (hardware): traduce direcciones virtuales a físicas y aplica los permisos. **SIGSEGV:** señal con que el kernel mata al proceso que toca memoria ajena.

### Aislamiento por proceso (diapositiva 11)
- Cada proceso recibe **su propio espacio de direcciones virtual** al crearse; nunca se mezclan. La MMU traduce con tablas de páginas que **solo el kernel modifica**, y cada página tiene permisos de lectura, escritura y ejecución.
- Un acceso inválido genera SIGSEGV: **muere el proceso, no el sistema**. La memoria del kernel es inaccesible desde modo usuario; cuando se dice que un hacker «llegó al kernel» se refiere a que logró entrar a esa memoria, donde está la interacción de bajo nivel con el hardware.
- Contraste con Windows: hasta Windows 95 la memoria era «todos contra todos»; Windows 10/11 sí aísla por proceso, pero tomó muchos años.

### Ataques y defensas (diapositiva 12)

| Ataque | Defensa | Cómo funciona |
|--------|---------|---------------|
| Inyectar código propio en la pila o el heap | **NX / W^X** | Una página es escribible o ejecutable, nunca ambas |
| **ROP**: reutilizar código que ya está en memoria | **ASLR y KASLR** | Pila, heap, bibliotecas y kernel se cargan en posiciones aleatorias |
| Desbordar un búfer de la pila | **Stack canaries** | Un valor aleatorio en la pila delata la sobreescritura antes de retornar |
| **Meltdown** (falla de CPU, 2018): leer memoria del kernel | **KPTI** | Tablas de páginas separadas para kernel y usuario |
| Engañar al kernel con datos del usuario | **SMEP / SMAP** | La CPU impide al kernel ejecutar o leer páginas de usuario |

- Meltdown: al buscar más velocidad, los fabricantes de procesadores cometieron errores de diseño; forzando la CPU, esta hacía cosas indebidas y daba acceso al kernel.
- **DMA / IOMMU:** hay dispositivos que escriben directo en RAM; la IOMMU les pone límites.

> **Nota:** en clase el desbordamiento se describió como «llenar la memoria»; es escribir más datos de los que caben en un búfer de tamaño fijo.

---

## 8. Linux: dispositivos y archivos (Seguridad, diapositivas 13–17)

### Dispositivos: todo es un archivo (diapositiva 13)
- Linux monta y configura los dispositivos como **archivos** en `/dev`, con los mismos permisos que cualquier archivo. Solo el kernel (los drivers) toca el hardware; el usuario pide acceso con `open`, `read`, `write` e `ioctl`.
```text
$ ls -l /dev/sda /dev/ttyS0
brw-rw---- 1 root disk     8,  0  /dev/sda     (bloques: solo root y grupo disk)
crw-rw---- 1 root dialout  4, 64  /dev/ttyS0   (caracteres: grupo dialout)
```
- **udev** asigna dueño y grupo al conectar el dispositivo: se accede por pertenencia a grupos (`disk`, `audio`, `video`).
- **Módulos firmados y modo *lockdown*:** con Secure Boot ni root carga código arbitrario en el kernel. **IOMMU** impide que un dispositivo lea memoria ajena por DMA.

### Permisos clásicos de archivos (diapositivas 14–15)
- Tipo + permisos de **propietario**, **grupo** y **otros**, cada uno con `r` (leer), `w` (escribir), `x` (ejecutar o entrar a un directorio). Cada permiso es un bit, así que cada trío se escribe como un dígito octal.

| Notación | `-` | `rwx` | `r-x` | `---` |
|----------|-----|-------|-------|-------|
| Octal (`chmod 750`) | tipo | 7 | 5 | 0 |

- Cada archivo guarda en su **inodo** su UID, su GID y su modo; el kernel los compara con las credenciales del proceso en cada `open()`.
- **Bits especiales:** setuid/setgid (ejecutar con la identidad del dueño o grupo) y **sticky** (en `/tmp` solo el dueño borra sus archivos). **umask:** permisos por defecto de los archivos nuevos (típico 022: nadie más puede escribir).
- **Hay que dominar `chmod`** (visto en los talleres): cambiar permisos es una habilidad fundamental.
- **POSIX:** estándar universal definido por el IEEE para que los SO se comporten de forma parecida; incluye permisos separados para usuarios y grupos.

### Más allá de `rwx` (diapositiva 16)

| Mecanismo | Qué aporta |
|-----------|-----------|
| **ACL POSIX** (`setfacl`) | Permisos para usuarios y grupos específicos, más finos que dueño/grupo/otros |
| **`chattr +i`** | Archivo **inmutable**, incluso para root |
| **xattr** | Metadatos extra (p. ej. las etiquetas de SELinux) |
| Opciones de montaje | `nosuid`, `noexec`, `nodev`, `ro`: limitan lo que se puede hacer desde `/tmp` o una llave USB |
| **Cifrado** | LUKS / dm-crypt cifra el disco completo; fscrypt cifra por directorio |
| **Integridad** | dm-verity e IMA verifican que el sistema no fue modificado (Android, ChromeOS) |
| **Vista restringida** | `chroot` y *mount namespaces*: el proceso solo ve la parte del árbol que le corresponde |

### Linux en resumen (diapositiva 17)

| Área | Mecanismo base (Unix) | Refuerzos modernos |
|------|----------------------|--------------------|
| Procesos | UID/GID, modo usuario vs. kernel | Capabilities, namespaces, seccomp, SELinux / AppArmor |
| Memoria | Memoria virtual y permisos por página | NX, ASLR / KASLR, canaries, KPTI |
| Dispositivos | Archivos en `/dev` con permisos | udev, módulos firmados, lockdown, IOMMU |
| Archivos | `rwx` para dueño, grupo y otros | ACL, montajes restringidos, cifrado, dm-verity |

> Linux trae la seguridad **construida desde que empezó a construirse**; no se la pusieron después.

---

## 9. Windows: de DOS a NT (Seguridad, diapositivas 18–23)

### El punto de partida: MS-DOS (diapositiva 19)
- DOS (1981) se diseñó para una PC **personal, aislada y de un solo usuario** que corría un programa a la vez: la seguridad no era un requisito.
  - **Un solo usuario:** sin inicio de sesión, dueños ni permisos. Los archivos solo tenían atributos: normal, oculto (de mentiras, había forma de verlo) y solo lectura (se saltaba con un comando).
  - **Sin modo protegido:** todo programa corre con el mismo poder que el SO, sin restricción de llamadas, casi conectado directo al kernel.
  - **Sin protección de memoria:** cualquier programa puede escribir sobre otro o sobre DOS.
  - **Hardware abierto:** acceso directo a disco, puertos e interrupciones; así nacieron los virus de sector de arranque.

### De DOS a Windows 11 (diapositiva 20)

| Año | Sistema | Característica |
|-----|---------|----------------|
| 1981 | MS-DOS | Monousuario, sin protección |
| 1985–92 | Windows 1 a 3.x | Interfaz gráfica sobre DOS (era un *shell*) |
| 1993 | **Windows NT** | Kernel nuevo, seguro por diseño |
| 1995–2000 | 95 / 98 / Me | Para el hogar; siguen sobre DOS |
| 2001 | **Windows XP** | NT llega al hogar, pero todos como administradores |
| 2007 | Vista | UAC, ASLR, firma de drivers |
| 2015–21 | Windows 10 / 11 | VBS; TPM 2.0 obligatorio |

- Fueron **dos líneas paralelas** (DOS y NT) que solo se juntaron en 2001: quienes usaban 95/98/Me siguieron sin protección hasta entonces.
- NT era más seguro, pero «la vara estaba bajísima»: los hackeos a NT/XP continuaron, aunque fueron menos y menos riesgosos.
- **Por qué no se corrigió antes:** a Microsoft le interesaba facturar y que el software viejo siguiera funcionando (**retrocompatibilidad**). Tenía un kernel seguro desde 1993, pero lo configuró de forma permisiva. NT («New Technology») es el nombre del kernel; NTFS sustituyó a FAT.

### Lo que costó la retrocompatibilidad (diapositivas 21–22)

| Herencia | Por qué se mantuvo | Consecuencia |
|----------|--------------------|--------------|
| **Administrador por defecto** | DOS y Win9x asumían control total; todos los programas tenían los mismos derechos | Todo malware corría con poder total. En Win9x el inicio de sesión era de mentira (se podía entrar sin usuario) |
| **FAT / FAT32 sin permisos** | Compatibilidad con discos y llaves USB | Sin dueños ni control de acceso en medios removibles |
| **AutoRun** | Comodidad al instalar desde CD (en Linux había que dar «Run») | Gusanos por USB (Conficker, Stuxnet) |
| **Ejecutar según la extensión** | Convención de DOS (`.exe`, `.com`, `.bat`) | Troyanos tipo `foto.jpg.exe` |
| **Hashes LM, NTLM, SMBv1** | Interoperar con redes antiguas | Robo de contraseñas; **WannaCry (2017)** |
| **Buscar DLL en la carpeta actual** | Comportamiento de Windows de 16 bits | Secuestro de DLL (las **DLL** son las bibliotecas que cargan los programas) |

### La factura: la era de los gusanos (diapositiva 23)
- Gusanos que marcaron la época: Melissa (1999, macros de Word), ILOVEYOU (2000, script por correo), Code Red / Nimda (2001, servidor IIS), Blaster / Slammer (2003), Sasser (2004, sin intervención del usuario), Conficker (2008) y WannaCry (2017).
- **Respuesta de Microsoft:** memo «Trustworthy Computing» de Bill Gates (2002) que pone la seguridad como prioridad; **XP SP2 (2004)**: firewall encendido por defecto (Linux siempre lo tuvo) y DEP; **Vista (2007)**: UAC, ASLR y **verificación y firma obligatoria de drivers** (Linux ya la tenía).

---

## 10. Windows NT: modelo de seguridad (Seguridad, diapositivas 24–30)

### El modelo (diapositivas 24–25)
Flujo de una solicitud:

1. **Inicio de sesión:** el usuario presenta credenciales.
2. **LSASS** autentica contra la base de cuentas (**SAM** local o **Active Directory**, con Kerberos).
3. Se crea el **access token**: SID del usuario, grupos y privilegios.
4. El **monitor de referencia** (en el kernel) compara el token con la ACL del objeto.
5. **Decisión:** permitir o denegar, y **auditar**.

- **Todo es un objeto** (archivos, procesos, claves del registro, dispositivos) y pasa por el mismo control. Cada objeto guarda un **descriptor de seguridad**: dueño, **DACL** (quién accede) y **SACL** (qué accesos se auditan). Cada renglón de una ACL es una **ACE**.
- **SID:** identificador único de usuario o grupo; el equivalente al UID/GID de Linux. Antes de NT el sistema ni sabía qué usuario pedía un recurso y, si no lo sabía, lo dejaba pasar.
- El kernel decide si el usuario puede usar el recurso que solicita; esta filosofía combina acceso discrecional con un nivel superior para auditar.

### Procesos (diapositiva 26)
- **Access token:** la identidad viaja pegada a cada proceso.
- **UAC (control de cuentas):** incluso el administrador trabaja con un token limitado; elevar privilegios requiere su consentimiento.
- **Niveles de integridad** (bajo, medio, alto, sistema): un proceso no escribe en objetos de un nivel superior.
- **Aislamiento de sesión 0:** los servicios ya no comparten escritorio con el usuario.
- **AppContainer:** *sandbox* para navegadores y apps de la Store; solo tienen las capacidades que declaran.
- **Procesos protegidos (PPL):** ni un administrador puede inyectar código en LSASS o en el antimalware; hay partes del SO que nadie puede modificar.

### Memoria (diapositivas 27–28; solo PDF)

| Mitigación | Desde | Qué hace | En Linux |
|------------|-------|----------|----------|
| DEP | XP SP2 (2004) | Las páginas de datos no se ejecutan | NX |
| ASLR | Vista (2007) | Carga en posiciones aleatorias | ASLR |
| /GS y SEHOP | 2003–2008 | Detectan desbordamientos de pila | Stack canaries |
| CFG y CET | 8.1 (2014) y 10 (2020) | Validan saltos indirectos y direcciones de retorno | CFI, shadow stack |
| PatchGuard | x64 (2005) | Impide parchear el kernel en ejecución | Lockdown |
| VBS / HVCI | 10 (2015) | El hipervisor protege el código del kernel | Sin equivalente directo |

### Dispositivos y drivers (diapositiva 29)
- Los drivers **corren en modo kernel** porque interactúan con el hardware: un driver malo compromete todo. El I/O Manager media cada acceso y los dispositivos son objetos con ACL.
- **Firma obligatoria de drivers** (64 bits, desde Vista, 2007): cada driver nuevo viene certificado por su fabricante con llaves de validación, lo que evita drivers «truchos» con troyanos. También hay Secure Boot (UEFI), protección contra DMA y una lista de bloqueo de drivers vulnerables.
- **Julio de 2024, CrowdStrike:** una actualización defectuosa de un driver de seguridad en modo kernel dejó fuera de servicio unos **8,5 millones** de equipos Windows. Lección: menos código de terceros dentro del kernel; desde entonces se es más estricto con los drivers.

> **Nota:** en clase se describió como un driver «confiable» con un troyano; el PDF lo presenta como una actualización defectuosa, no un ataque.

### Archivos: NTFS (diapositiva 30)
- **ACL de NTFS:** cada archivo tiene una DACL con entradas de permitir o denegar por usuario o grupo, más fina que `rwx`.
- **Herencia:** los permisos fluyen de la carpeta a su contenido, salvo que se bloquee. **Auditoría (SACL):** registra quién accedió a qué y si lo logró.
- **Cifrado:** EFS por archivo; **BitLocker** cifra el disco completo con la clave en el TPM, de modo que aunque roben el equipo nadie puede leerlo.
- **Protección de recursos:** ni los administradores reemplazan archivos del sistema (solo `TrustedInstaller`). **Virtualización de UAC:** si un programa viejo escribe en «Archivos de programa», se redirige a la carpeta del usuario.
- Balance: Windows se fue **poniendo al día** desde ~2004; los últimos diez años han sido buenos.

---

## 11. Linux y Windows lado a lado (Seguridad, diapositiva 31)

| Aspecto | Linux | Windows |
|---------|-------|---------|
| Identidad | UID / GID | SID y access token |
| Superusuario | root, sudo, capabilities | Administrador, UAC, privilegios |
| Permisos de archivos | `rwx` y ACL POSIX | ACL de NTFS (DACL / SACL) |
| Control obligatorio | SELinux, AppArmor | Niveles de integridad, AppContainer |
| Cifrado de disco | LUKS / dm-crypt | BitLocker |
| Origen | Multiusuario desde Unix (años 70) | Monousuario (DOS); seguridad añadida después |

- Linux fue pensado **multiusuario** (venía de Unix); Windows nació **monousuario con acceso a todo**, y de ahí salieron la mayoría de sus problemas.
- Linux tiene al menos dos sistemas que vigilan los controles (SELinux y AppArmor) y siempre tuvo cifrado; Windows lo incorporó hace pocos años y organizó el control por niveles.

---

## 12. Seguridad moderna (Seguridad, diapositivas 32–38)

### Cinco principios de diseño (diapositiva 33)

| Principio | Idea |
|-----------|------|
| **Mínimo privilegio** | Cada proceso y usuario recibe solo lo que necesita, y solo por el tiempo necesario (idealmente con límite de tiempo) |
| **Defensa en profundidad** | Capas independientes: si una falla, la siguiente contiene el daño. No una sola línea de defensa al frente |
| **Zero Trust** | «Nunca confiar, siempre verificar»: estar dentro de la red no otorga confianza |
| **Seguro por defecto** | La configuración inicial es la segura; lo inseguro requiere una decisión explícita. No «después le meto la seguridad» |
| **Asumir la brecha** | Diseñar para detectar, contener y recuperarse, no solo para prevenir; asumir siempre el peor escenario y minimizarlo |

- Criterio práctico: es mejor equivocarse por **no** dar un derecho que por darlo de más.

### Confianza anclada en el hardware (diapositivas 34–35)
- **Secure Boot:** firmware UEFI → cargador de arranque → kernel → drivers y módulos; **cada eslabón verifica la firma digital del siguiente** antes de cederle el control.
- **TPM 2.0:** chip que guarda claves y mide el arranque; si algo cambió, no libera la clave del disco. Es requisito de Windows 11.
- **Entornos de ejecución confiables (TEE):** ARM TrustZone, Apple Secure Enclave, Intel TDX, AMD SEV; secretos aislados incluso del SO.
- **Virtualización como frontera:** un hipervisor protege credenciales y kernel aunque el sistema esté comprometido (VBS, Credential Guard).

### Aislamiento y memoria segura (diapositiva 36)
- Cerca del **70 %** de las vulnerabilidades graves reportadas por Microsoft y Chromium son **errores de manejo de memoria en C y C++**. Por eso gana auge **Rust**, ya presente en el kernel de Linux (desde 6.1, 2022), en Windows y en Android.
- **Sandbox para todo** (navegadores, apps móviles con permisos explícitos, Flatpak, Snap); **contenedores y microVM** (Firecracker, gVisor); mitigaciones en el procesador (shadow stacks, etiquetado de memoria ARM MTE, autenticación de punteros).
- Recomendaciones al programar: usar *sandbox* y contenedores, evitar interactuar directamente con el procesador y poner todos los sistemas de verificación posibles.

### Identidad, detección y operación (diapositiva 37)
- **Sin contraseñas:** passkeys (FIDO2 / WebAuthn), biometría y MFA resistente al *phishing* (MFA = algo que sé, algo que tengo y algo que soy).
- **Cifrado por defecto:** disco completo en reposo y TLS en tránsito, sin que el usuario lo pida.
- **Parches continuos:** actualizaciones automáticas y parcheo del kernel en caliente.
- **EDR / XDR:** detección por comportamiento en lugar de firmas; eBPF para observar el kernel.
- **Cadena de suministro:** código firmado, SBOM y *builds* reproducibles. Lecciones: SolarWinds (2020) y XZ (2024, el caso del mantenedor presionado).
- **Sistemas inmutables:** base de solo lectura verificada y actualizaciones atómicas (ChromeOS, Android).
- Hábitos personales: activar siempre el segundo factor, revisar actualizaciones, bajar actualizaciones y drivers solo de sitios confiables y evitar cambios innecesarios en el equipo.

### Conclusiones (diapositiva 38)
- **Linux** heredó de Unix un diseño multiusuario y lo reforzó por capas (capabilities, namespaces, MAC). **Windows** tuvo un kernel seguro desde NT, pero pagó dos décadas el costo de ser compatible con DOS. **Hoy** ambos convergen: mínimo privilegio, aislamiento, confianza anclada en hardware y memoria segura.
- **La seguridad no es una característica que se agrega al final: es una decisión de diseño.**

---

## Conceptos clave

- **Dilema del SO:** compartir recursos vs. protegerlos. Cuatro propiedades: resistir, reconocer, recuperarse y adaptarse a ataques.
- **Autenticación** (¿es quien dice ser?) vs. **autorización** (¿puede hacer lo que pide?): controles distintos.
- **Intrusión:** la mayoría es **no intencional** (mala configuración, claves por defecto); la intencional incluye DoS, browsing, wiretapping/sniffing y backdoors. La **ingeniería social** explota al ser humano.
- **Malware:** virus (autorreplicante: archivos, boot sector, MBR, múltiples, macro), gusanos (por red, sin archivo), troyanos (sin autorización), bombas lógicas, spyware, keyloggers, ransomware.
- **Cuatro pilares:** antivirus (reactivo), firewalls, buena configuración de acceso (grupos, política de passwords razonable, segundo factor) y encriptación.
- **Linux:** seguridad desde el diseño; UID/GID, root, syscalls como única puerta al kernel, **DAC + MAC** (ambos deben permitir), capabilities, namespaces/cgroups/seccomp (contenedores).
- **Memoria en Linux:** espacio virtual por proceso, MMU y permisos por página, SIGSEGV; NX, ASLR, canaries, KPTI, SMEP/SMAP.
- **Dispositivos y archivos en Linux:** todo es un archivo con permisos `rwx` (dueño/grupo/otros, `chmod 750`); ACL, `chattr +i`, montajes restringidos, LUKS, dm-verity.
- **Windows:** nació de DOS (monousuario, sin protección); NT (1993) trajo un kernel seguro, pero la retrocompatibilidad (admin por defecto, FAT, AutoRun, SMBv1, DLL) causó la era de los gusanos. Corrección desde XP SP2 (2004) y Vista (2007).
- **Modelo NT:** LSASS → access token (SID) → monitor de referencia → ACL del objeto (DACL/SACL); UAC, niveles de integridad, AppContainer, firma de drivers, BitLocker.
- **Seguridad moderna:** mínimo privilegio, defensa en profundidad, Zero Trust, seguro por defecto, asumir la brecha; TPM y Secure Boot; lenguajes seguros en memoria; sandbox; seguridad como decisión de diseño.

---

## Fuera del PDF — logística, tareas y metodología

### Evaluación
- Los términos de las diapositivas de memoria y hardware (Seguridad, 9–10) no se preguntan en el quiz de seguridad. Sí conviene dominar la diferencia entre autenticación y autorización, los tipos de ataque y malware, y los permisos de archivos con `chmod`.
- **Quizzes pendientes:** se publican más tarde ese mismo día para ponerse al día.
- **Notas:** las calificaciones que se ven en cero en el aula virtual se ingresan al día siguiente. Queda una tarea programada pendiente de revisión; se informará la semana siguiente (semana 11 del curso).

### Recomendaciones y agenda
- Se recomienda dedicar parte de diciembre a aprender **Docker** (Kubernetes es opcional y mucho más complejo); no es evaluable.
- El docente da una charla sobre el lenguaje **Rust** el 5 de diciembre.
