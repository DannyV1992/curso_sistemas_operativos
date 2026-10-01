# Extraer la transcripción de una clase

Script para copiar la transcripción completa de un video de SharePoint/Stream cuando el botón "Descargar" está deshabilitado.

## Pasos

1. Abrir el video y dejar visible el panel de **Transcripción**.
2. Presionar `F12` y ir a la pestaña **Consola**.
3. Ir hasta abajo de la consola (o limpiarla con el icono 🚫) y hacer clic en la línea con `>`.
4. Si pide permiso para pegar, escribir `allow pasting` a mano y presionar Enter.
5. Pegar el script de abajo y presionar Enter.
6. Esperar el mensaje "Listo" y pegar en `Notas.txt` con `Ctrl+V`.

Si el mensaje dice que no se pudo copiar solo, escribir a mano en la consola:

```js
copy(transcripcion)
```

Si responde "No encontré timestamps", cambiar el selector `top` (arriba a la izquierda de la consola) al marco de `stream` o `sharepoint` y ejecutar de nuevo.

## Script

```js
(async () => {
  const copiar = copy;
  const ts = /^\d{1,2}:\d{2}(:\d{2})?$/;
  const leaf = [...document.querySelectorAll('*')]
    .find(e => e.children.length === 0 && ts.test(e.textContent.trim()));
  if (!leaf) return console.log('No encontré timestamps');

  let box = leaf;
  while (box && box.scrollHeight <= box.clientHeight + 5) box = box.parentElement;

  const seen = new Map();
  const grab = () => {
    for (const e of document.querySelectorAll('*')) {
      if (e.children.length || !ts.test(e.textContent.trim())) continue;
      const time = e.textContent.trim();
      let row = e;
      while (row.parentElement && row.innerText.trim() === time) row = row.parentElement;
      if (!seen.has(time)) seen.set(time, row.innerText.trim());
    }
  };

  box.scrollTop = 0;
  await new Promise(r => setTimeout(r, 600));
  let prev = -1;
  while (box.scrollTop !== prev) {
    grab();
    prev = box.scrollTop;
    box.scrollTop += box.clientHeight * 0.7;
    await new Promise(r => setTimeout(r, 350));
  }
  grab();

  const secs = t => t.split(':').reduce((a, n) => a * 60 + +n, 0);
  const text = [...seen.entries()]
    .sort((a, b) => secs(a[0]) - secs(b[0]))
    .map(([, v]) => v).join('\n\n');
  window.transcripcion = text;
  try {
    copiar(text);
    console.log(`Listo: ${seen.size} bloques copiados al portapapeles.`);
  } catch (e) {
    console.log(`Listo: ${seen.size} bloques. No se pudo copiar solo; escribe: copy(transcripcion)`);
  }
})();
```
