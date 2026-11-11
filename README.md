# Summer Clover (夏色四葉草) — Traducción al Español Latino (fan patch)

Traducción no oficial, hecha por fans, del visual novel **Summer Clover** de Steam, al **español latino**. El juego venía originalmente en chino tradicional, con localizaciones oficiales a inglés, japonés, coreano y chino simplificado — pero no a español. Este proyecto agrega esa traducción faltante.

> ⚠️ **Contenido para adultos.** Este juego tiene contenido explícito. Este repositorio no redistribuye ningún asset del juego (imágenes, audio, modelos, etc.), solo texto traducido y las herramientas para aplicarlo sobre tu propia copia legalmente adquirida del juego.
>
> ⚠️ **Proyecto no oficial / no afiliado.** No tiene relación con los desarrolladores u editores del juego.

## Estado del proyecto

- ✅ Todo el texto de menús/sistema (23 categorías de "managed text": nombres, UI, mapa, cocina, tienda, etc.)
- ✅ Ruta común (`A_Story`, 12 guiones)
- ✅ Ruta de Kasumi completa: 10/10 capítulos principales, 5 guiones secundarios y las 10 escenas de galería (KasumiHCG01-10)
- ✅ Ruta de Ayano completa: 8 guiones de `F_Story2`, 10/10 capítulos principales (`Ayano_01-10`), 5 guiones secundarios y las 10 escenas de galería (AyanoHCG01-10)
- ⏳ Rutas de Shizuku y Sizuko: pendientes
- ⏳ Guiones varios (cocina, cuarto, minijuegos, etc.): pendientes

Este es un trabajo en progreso. Las traducciones se van agregando guion por guion, verificadas en el juego antes de subirlas.

## Cómo funciona

El juego usa el motor **Naninovel** sobre Unity. En vez de crear un nuevo idioma desde cero (lo cual requeriría modificar estructuras internas más riesgosas), este patch **reemplaza el contenido del idioma coreano (ko-KR)** dentro de `resources.assets` con el texto en español. Esto significa:

- Para jugar en español, debes seleccionar **"한국어" / Coreano** como idioma en el juego.
- El idioma coreano original queda sobrescrito (no se puede tener ambos a la vez con este método).

### Por qué el formato binario es delicado

Los guiones de diálogo compilados por Naninovel son objetos `MonoBehaviour` serializados con un formato tipo Odin Serializer, sin TypeTree embebido — por eso no se pueden leer/escribir con la API genérica de UnityPy, hay que parsear los bytes a mano.

**Regla crítica:** cada entrada de texto individual debe mantener exactamente el mismo tamaño en bytes que el texto original (coreano) — no solo el total agregado del objeto, sino cada entrada por separado. Si el texto en español es más corto, se rellena con espacios al final; si es más largo, hay que acortarlo a mano. Cambiar el tamaño de una sola entrada, aunque el total del objeto no cambie, provoca que el juego crashee al cambiar de idioma o de escena. Esto está confirmado empíricamente y ya implementado en `tools/patch_script_generic.py`.

## Estructura del repositorio

```
tools/                      Scripts de Python para extraer y parchear texto
  common.py                 Helpers de bajo nivel para parsear el blob binario
  patch_filters.py          Filtro compartido: separa diálogo real de metadatos/comandos
  extract_script_en.py      Extrae el texto en inglés de un guion (referencia para traducir)
  extract_pair.py           Extrae inglés + presupuesto de bytes coreano en un solo .json
  patch_script_generic.py   Aplica una traducción .json sobre un guion, validando bytes
  patch_menu.py / 2 / 3     Scripts usados para parchear las categorías de menú/sistema

translations/
  menus/                    Traducciones de las categorías de texto de sistema/menú
  A_Story/                  Ruta común (prólogo + capítulos compartidos)
  Kasumi/                   Ruta de Kasumi (10 capítulos + guiones secundarios)
    gallery/                 Escenas de repetición de la galería (KasumiHCG01-10)
  Ayano/                    Ruta de Ayano (F_Story2 + 10 capítulos + guiones secundarios)
    gallery/                 Escenas de repetición de la galería (AyanoHCG01-10)
```

Cada guion de diálogo tiene su traducción en `<Nombre>_es.json` (array plano, mismo orden y conteo que las entradas coreanas). La referencia en inglés aparece como `<Nombre>_en.json` (formato antiguo) o, en los guiones más recientes, dentro de `<Nombre>_pair.json` — un array de objetos `{"en": "...", "ko_bytes": N}` que además indica el presupuesto de bytes de cada línea para facilitar la traducción.

## Cómo aplicar el patch

Necesitas:
- Python 3.11+ con [UnityPy](https://github.com/K0lb3/UnityPy) instalado (`pip install UnityPy`)
- Tu propia copia del juego comprada en Steam

Pasos generales (los scripts tienen rutas de ejemplo que debes ajustar a tu instalación):

1. Haz una copia de seguridad de `SummerClover_Data/resources.assets` antes de tocar nada.
2. Para un guion de diálogo:
   ```bash
   python tools/patch_script_generic.py <NombreDelGuion> <path_id_coreano> translations/<ruta>/<Nombre>_es.json <carpeta_salida>
   ```
   El script busca el objeto coreano por `path_id`, valida que el número de entradas coincida, rellena/ajusta bytes, y guarda el `resources.assets` parcheado en `<carpeta_salida>`.
3. Reemplaza el `resources.assets` original del juego por el que se generó en `<carpeta_salida>` (con el juego cerrado).
4. Verifica abriendo el juego y seleccionando el idioma coreano — debería mostrar español.

Para los textos de menú, usa `patch_menu.py` (y las variantes 2/3), que son más simples porque son `TextAsset` planos, sin la restricción de tamaño de bytes.

## Cómo contribuir / traducir el resto

Si quieres ayudar a traducir los capítulos que faltan:

1. Extrae el guion en inglés como referencia: `python tools/extract_script_en.py <NombreDelGuion>`
2. Traduce cada línea a español latino, manteniendo el mismo orden y cantidad de líneas, en un archivo `<Nombre>_es.json`.
3. Prueba con `patch_script_generic.py`. Si hay un "mismatch" de conteo o alguna línea queda "too long" (excede el presupuesto de bytes del original coreano), el script te lo indica con detalle para que ajustes.
4. Abre un Pull Request con el `.json` nuevo.

## Descargo de responsabilidad

Este es un proyecto de fans sin fines de lucro, para hacer accesible el juego a la comunidad hispanohablante. No se distribuye ningún asset propietario del juego — solo texto traducido y herramientas. Debes poseer una copia legítima del juego en Steam para usar este patch.
