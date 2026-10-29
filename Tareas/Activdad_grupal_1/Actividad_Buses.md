# Actividad grupal — Buses de memoria y procesos

**Curso:** IIIC2026 - Sistemas Operativos, LEAD University

**Docente:** Mario Miguel Agüero Obando

**Fuente:** presentación «Buses», diapositiva 13 (Preguntas)

**Integrantes:** Daniel Vásquez González

---

## Pregunta 1. ¿Por qué SATA es más rápido que PATA?

**Qué son.** Ambos son interfaces para conectar dispositivos de almacenamiento (discos duros, SSD de 2.5", unidades ópticas) a la placa madre.

- **PATA** (*Parallel Advanced Technology Attachment*, antes llamado IDE): bus **paralelo**. Un cable plano de 40 hilos (80 en la versión con tierras intercaladas) transmite **16 bits a la vez**.
- **SATA** (*Serial Advanced Technology Attachment*): bus **serial**. Un cable delgado de 7 conductores transmite los bits **uno detrás de otro** por un par diferencial.

**Por qué el serial gana.** Parece contraintuitivo (16 carriles deberían superar a 1), pero en un bus paralelo los problemas crecen con la frecuencia:

| Problema | Bus paralelo (PATA) | Bus serial (SATA) |
|----------|---------------------|-------------------|
| Sincronización entre hilos (*skew*) | Los 16 bits deben llegar a la vez; al subir la frecuencia, unos hilos llegan antes que otros y se leen mal | Un solo canal, no hay nada con qué desincronizarse |
| Interferencia entre hilos (*crosstalk*) | Hilos pegados se interfieren entre sí | Pares diferenciales, mucho menos ruido |
| Topología | Un cable compartido por dos dispositivos (maestro/esclavo) que se reparten el ancho de banda | Un cable por dispositivo, punto a punto |
| Frecuencia alcanzable | Techo bajo (≈ 133 MB/s en UDMA/133) | Mucho más alta |

Como el serial elimina esos límites, puede subir la frecuencia de reloj muy por encima de la del paralelo y, aun enviando un bit a la vez, entrega más datos por segundo:

| Interfaz | Velocidad máxima |
|----------|------------------|
| PATA (UDMA/133) | 133 MB/s |
| SATA I | 1,5 Gbit/s ≈ 150 MB/s |
| SATA II | 3 Gbit/s ≈ 300 MB/s |
| SATA III | 6 Gbit/s ≈ 600 MB/s |

**Ventajas extra de SATA:** cable más pequeño (mejor flujo de aire en la caja), conexión en caliente (*hot-swap*) y comandos en cola (NCQ).

**Analogía.** Una autopista de 16 carriles donde todos los carros deben llegar al mismo tiempo a la meta se frena por el carro más lento; un solo carril donde los carros pasan a gran velocidad, uno tras otro, termina moviendo más.

---

## Pregunta 2. ¿Por qué superó el AGP a VESA?

**Qué son.** Ambos nacieron para mejorar el video, que dejó de ser un dispositivo más y empezó a exigir su propio camino.

- **VESA Local Bus (VLB, 1992)**, de la *Video Electronics Standards Association*: bus de 32 bits conectado **directamente al bus local del procesador** (pensado para el 486), a 33 MHz y con unos 130 MB/s teóricos. Fue la primera separación exitosa del video.
- **AGP** (*Accelerated Graphics Port*, Intel, 1997): puerto **dedicado** entre la tarjeta gráfica y el chipset, hecho solo para gráficos.

**Por qué AGP ganó.**

1. **Diseñado específicamente para video.** Es un puerto punto a punto exclusivo de la tarjeta gráfica y no compite con otros dispositivos. VESA seguía siendo una extensión del bus del procesador.
2. **Más ancho de banda y escalable.** AGP 1x ≈ 266 MB/s (66 MHz); luego 2x ≈ 533 MB/s, 4x ≈ 1 GB/s y 8x ≈ 2,1 GB/s.
3. **Acceso directo a la memoria principal.** La tarjeta podía usar la RAM del sistema para texturas (mapeo GART), importante para los gráficos 3D y los videojuegos de la época.
4. **Independencia del procesador.** VESA estaba atada al bus del 486; con la llegada del Pentium dejó de tener sentido. AGP depende del chipset y funciona con distintas CPU.
5. **Limitaciones eléctricas de VESA.** Al colgarse del bus del procesador, cada tarjeta le añadía carga eléctrica; solo se podían instalar dos o tres, y a mayor frecuencia se volvía inestable.

**Nota histórica.** AGP fue a su vez reemplazado hacia 2004 por PCI Express, que repite la idea de enlace serial dedicado. De VESA como organización sobrevivió el estándar DisplayPort, que es el conector rectangular de video que se ve hoy en muchos monitores.

---

## Pregunta 3. ¿Cuáles son las diferencias entre PCI Express y PCI original?

**PCI** (*Peripheral Component Interconnect*, 1992) fue un estándar muy exitoso porque el bus funciona **independientemente** de la CPU: delega eventos y permite mejorar los dispositivos por separado. **PCI Express** (PCIe, 2003) conserva esa idea, pero cambia la tecnología de transporte.

| Característica | PCI original | PCI Express |
|----------------|--------------|-------------|
| Transmisión | **Paralela** (32 o 64 bits) | **Serial**, por carriles (*lanes*) |
| Topología | **Bus compartido**: todos los dispositivos usan el mismo bus y se reparten el ancho de banda | **Punto a punto**: cada dispositivo tiene su propio enlace hacia un conmutador (*switch*) |
| Ancho de banda | 133 MB/s (32 bits / 33 MHz); 533 MB/s en la variante de 64 bits / 66 MHz | ≈ 250 MB/s por carril y por sentido en la 1.0, y se duplica casi en cada generación (≈ 1 GB/s en la 3.0, ≈ 2 GB/s en la 4.0, ≈ 4 GB/s en la 5.0) |
| Escalabilidad | Fija | Flexible: x1, x4, x8, x16, según los carriles que use el dispositivo |
| Dirección | **Half dúplex**: un sentido a la vez | **Full dúplex**: envía y recibe simultáneamente |
| Conexión en caliente y energía | Limitado | Soportado de forma nativa, con administración de energía |
| Compatibilidad | — | Mantiene el modelo de software de PCI, así que los controladores y el sistema operativo siguen funcionando casi igual |

**Half dúplex vs. full dúplex.**

- **Half dúplex:** la comunicación va en ambos sentidos, pero **no al mismo tiempo**. Como un carril reversible en una carretera: o va en una dirección o en la otra.
- **Full dúplex:** ambos sentidos **a la vez**, como una carretera con carriles independientes para cada dirección.

**Conclusión.** PCIe es, en esencia, «PCI pasado a serial y punto a punto». Es la misma lección de la pregunta 1: el serial dedicado supera al paralelo compartido. Habilitar bidireccionalidad total trae el reto de la **sincronización** (quién llega primero a qué, evitar que dos notificaciones se queden dando vueltas), y eso se resuelve en el diseño del protocolo.

---

## Pregunta 4. Puertos usados históricamente por las PCs

Resumen sin entrar en detalle, de los puertos más antiguos a los más recientes:

| Puerto | Tipo | Dispositivos con los que se usaba |
|--------|------|-----------------------------------|
| **COM** (serial, RS-232) | Serial | Módems, ratones, algunos equipos de comunicación |
| **LPT** (paralelo, Centronics) | Paralelo | Impresoras; también escáneres y unidades externas |
| **PS/2** | Serial | Teclado y ratón |
| **Puerto de juegos** (15 pines) | Analógico | Joysticks y gamepads |
| **VGA** | Analógico | Monitores |
| **IDE/PATA** y controlador de disquete | Interno, paralelo | Discos duros, unidades de CD/DVD, disqueteras |
| **SCSI** | Paralelo | Discos duros, escáneres, unidades de cinta y ópticas (más común en equipos profesionales y servidores) |
| **USB** (desde 1996) | Serial | Casi todo: teclado, ratón, impresoras, discos, memorias, cámaras. Un solo puerto para muchos dispositivos |
| **FireWire** (IEEE 1394) | Serial | Cámaras de video digitales y discos externos |
| **SATA / eSATA** | Serial | Discos internos y externos, unidades ópticas |
| **PCMCIA / ExpressCard** | Expansión en portátiles | Tarjetas de red, módem, almacenamiento |
| **DVI / HDMI / DisplayPort** | Serial digital | Monitores y televisores |
| **Thunderbolt** | Serial | Discos externos, pantallas, estaciones de acople |

**Tendencia que se observa.** Se pasó de **un puerto distinto por cada tipo de dispositivo** (COM, LPT, PS/2, VGA, juegos) a **interfaces seriales universales** (USB y sus sucesores). Hacia dentro del equipo ocurrió lo mismo: IDE/PATA dio paso a SATA, y VESA, PCI y AGP dieron paso a PCI Express.

---

## Conclusiones generales

1. La evolución de los buses es una historia de **especialización**: separar los caminos (memoria, video, E/S, almacenamiento) para liberar a la CPU y evitar los transbordos por un único punto, como pasaba con el transporte público que obligaba a pasar por San José.
2. **Serial supera a paralelo** cuando sube la frecuencia, porque se evitan el *skew* y el *crosstalk*, y se pasa de buses compartidos a enlaces dedicados punto a punto.
3. Los dispositivos con exigencias propias (video, almacenamiento) acabaron teniendo su **bus dedicado** (AGP, SATA) y, finalmente, todo convergió en el modelo serial punto a punto de **PCI Express**.
4. Los buses de **dispositivos** son donde más ha habido cambios, mientras que los buses de datos apenas han cambiado.
