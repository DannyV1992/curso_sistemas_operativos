# CLAUDE.md — Resúmenes de clase

**Leer este archivo al inicio de cada sesión antes de generar o modificar un resumen.**

---

## Datos del curso (editar al copiar esta plantilla a otro curso)

- **Curso:** IIIC2026 - Sistemas Operativos, LEAD University
- **Docente:** Mario Miguel Agüero Obando
- **Carpetas:** PDFs en `Clases/PDFs/`, transcripción en `Clases/Notas.txt`, resúmenes en `Clases/Resumenes/`
- **Nombre del resumen:** `Clase N - Tema.md`, usando el tema que corresponda al contenido real cubierto en esa clase (no necesariamente el nombre completo del PDF, ya que un mismo PDF puede abarcar varias clases, p. ej. `2 - Kernel y Procesos.pdf` cubre las Clases 2 y 3)
- **Lenguajes/herramientas del curso:** línea de comandos Unix/Linux (bash), máquinas virtuales; no es un curso de un lenguaje de programación específico
- **Tipo de evaluación a tener presente:** talleres de aplicación, tareas programadas (simulaciones), quizzes, examenes, asistencia/participación (ver sección "Fuera del PDF" de cada resumen)
- **Nota sobre los PDFs:** los PDFs de diapositivas viven en `Clases/PDFs/` numerados por tema (`1 - Conceptos básicos.pdf`, `2 - Kernel y Procesos.pdf`, …) y no corresponden 1:1 con las clases — cada PDF puede extenderse a lo largo de varias sesiones. Siempre verificar en qué diapositiva exacta terminó la transcripción de la clase antes de fijar la cobertura.

Todo lo demás de este archivo es independiente del curso.

---

## Objetivo

Un **resumen por clase para estudiar y repasar**, no una reconstrucción de la sesión. Se construye con dos fuentes:

1. **La transcripción** (`Notas.txt`): es la fuente principal. Contiene lo que el docente realmente explicó, con sus ejemplos y advertencias. `Notas.txt` guarda solo la clase que se está trabajando y se sobrescribe cada vez.
2. **El PDF de la clase**: aporta el esqueleto, las fórmulas y los datos exactos, y cubre lo que la transcripción no tiene.

---

## Reglas de trabajo

- Leer **solo el PDF de la clase pedida**, no los demás.
- Si no hay transcripción, basarse solo en el PDF.
- Si la transcripción tiene tramos faltantes o cortados **dentro del alcance de la clase** (ver "Alcance"), usar el PDF para esos tramos y **anotarlo en el encabezado** (qué partes salen solo del PDF).
- Los timestamps de `Notas.txt` sirven para ubicar en qué parte de la clase se habló de cada tema. No se incluyen en el resumen.

---

## Jerarquía entre fuentes: la transcripción manda

1. Si la transcripción y el PDF **difieren**, se sigue la transcripción a menos que lo que se este diciendo en la transcripción este completamente errado (p. ej. una herramienta que aparece en el PDF pero el docente dice que no se usa; un valor o criterio corregido en clase).
2. Si **coinciden**, se escribe una sola versión, con la redacción que sea más clara.
3. Si el PDF tiene algo que la transcripción no menciona **dentro del alcance de la clase**, se incluye solo si es contenido de estudio (definición, fórmula, dato), y de forma breve.
4. **Estructura:** el orden y los títulos de las secciones siguen el PDF, para que el resumen se pueda cotejar con las diapositivas. El contenido de cada sección se redacta desde la transcripción.
5. Lo que el docente dijo sobre un tema del PDF va **dentro de la sección de ese tema**, no en una sección aparte.

---

## Alcance: solo lo que se cubrió en la clase

Un mismo PDF puede usarse en varias clases. El resumen cubre **solo hasta donde llegó el docente** según la transcripción.

- **Límite final:** la última diapositiva o tema que la transcripción alcanza. Todo lo que el PDF tenga después se omite; pertenece a la clase siguiente.
- **Dentro del rango:** si el docente saltó una diapositiva que está antes del límite, se incluye brevemente desde el PDF.
- **Transcripción cortada:** si termina de forma abrupta (sin despedida ni cierre), no asumir que ahí terminó la clase. Preguntar al usuario hasta dónde llegó antes de escribir.
- **Encabezado:** incluir una línea **Cobertura del PDF** que diga una de dos cosas:
  - `Completo (diapositivas 1 a N)`, si se cubrió todo el PDF.
  - `Parcial: diapositivas X a Y de N (hasta «tema de la diapositiva Y»)`, si no. Aclarar que el resto queda para la siguiente clase y, si el PDF ya se había cubierto en parte en una clase anterior, desde qué diapositiva empieza esta.
  - Si se saltaron diapositivas dentro del rango, listarlas (p. ej. `se saltaron las diapositivas 12 y 13`).
- **Sin transcripción:** el alcance es todo el PDF (ver "Reglas de trabajo").

---

## Voz: apuntes, no crónica

Se anota el **contenido**, no quién lo dijo ni cuándo. Escribir el hecho directamente, en presente y en voz impersonal.

**No usar:** "el profesor explica / señala / aclara…", "un estudiante preguntó…", "en clase se vio…", "aclaración explícita:".

| ✗ Crónica | ✓ Apunte |
|-----------|----------|
| "El profesor aclara que esa herramienta no se usa." | "Esa herramienta no se usa en el curso." |
| "Un estudiante preguntó por los pesos y el profesor lo validó." | "Los pesos relativos son el aspecto crítico." |

**Citas literales:** solo frases memorables o que fijan un concepto, con `>` y sin atribución narrativa alrededor. Con moderación.

**Nombres propios:** no se registran nombres de estudiantes ni intercambios de aula. Sí se conservan los que son contenido (autores, empresas, referencias) y el docente en el encabezado.

---

## Selectividad y longitud

Es un **resumen**. Hay que descartar activamente.

- **Longitud objetivo:** unas 150–200 líneas (~2,000 palabras) por clase. Si una clase es muy densa puede pasarse un poco, pero preferir siempre lo corto y denso.
- **Se conserva:** definiciones, el "por qué" de cada concepto, criterios de decisión, errores comunes y advertencias, datos y parámetros relevantes, y lo necesario para las tareas y evaluaciones.
- **Ejemplos:** uno por idea, el más claro. Si hay varios que ilustran lo mismo, se elige el mejor.
- **Se descarta:** divagaciones, repeticiones, anécdotas personales sin valor conceptual, presentaciones, asistencia, coordinación de horarios y recesos, y relleno conversacional.

**Criterio:** si una frase no aporta un concepto, un dato, un ejemplo aclaratorio o una advertencia, no va.

**No repetir:** nunca dos párrafos que digan lo mismo con otras palabras.

---

## Contenido matemático y de código

- **Fórmulas:** incluir las que definen un concepto o se usan para calcular, en LaTeX (`$...$` y `$$...$$`), con una línea que diga qué significa cada símbolo si no es obvio.
- **Cálculos resueltos:** mostrar el planteamiento y el resultado de un ejemplo representativo, no todos los pasos intermedios. Importa el concepto, no la mecánica.
- **Código:** solo fragmentos cortos que ilustren una técnica, en bloques con el lenguaje indicado. No pegar scripts completos.
- **Tablas:** usarlas cuando el PDF presente comparaciones o matrices.

---

## Fuera del PDF

Lo que no tiene contraparte en el PDF va **al final**, en una sección titulada por ejemplo `## Fuera del PDF — logística, tareas y metodología`:

- Logística, evaluación, políticas (uso de IA, asistencia, fechas).
- Instrucciones de tareas y entregables.
- Hoja de ruta de clases futuras.

---

## Formato del archivo

- Encabezado: título de la clase, curso, docente, fecha, PDF fuente, **cobertura del PDF** (completo, o qué diapositivas se vieron; ver "Alcance") y, si aplica, nota sobre tramos sin transcripción.
- Breve contexto y objetivos de la sesión (2–4 líneas).
- Secciones numeradas siguiendo el orden del PDF.
- Cierre con una sección de **conceptos clave**.
- Preferir listas y tablas sobre párrafos largos: deben poder escanearse con la vista.
- Negrita solo en términos clave, no en frases enteras.

---

## Idioma

Todo en **español**, con ortografía correcta (tildes y caracteres especiales). Los términos técnicos y nombres de algoritmos se mantienen en su forma original.
