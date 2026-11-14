# data/repositorio.csv (CSV oficial del reto)

Coloca aquí el archivo oficial del repositorio EdTech **sin modificarlo**, con el nombre `repositorio.csv`.

Columnas exactas esperadas: `Bloque, Tabla, Dato, Valor, Comparación o nota, Fuente, Enlace`.

- La app valida encabezados, encoding (UTF-8, UTF-8 con BOM, CP1252) y separador.
- Cada indicador usado en pantalla se busca por su etiqueta exacta (ver `INDICADORES` en `datos.py`) y su
  valor se compara con el esperado. Si no coincide, se marca «requiere revisión» y NO se muestra.
- Sin este archivo la simulación funciona igual (datos sintéticos); los datos de contexto se muestran como
  «no disponibles» y Metodología → Fuentes permite cargar el CSV solo para la sesión.

Los demás CSV de esta carpeta son **sintéticos** y se regeneran con `python datos.py`.
