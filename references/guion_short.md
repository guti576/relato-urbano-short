# guion.json de un Short

Uno por Short, en `<reportaje>/shorts/S1/guion.json` (S2, S3…). Lo escribe Claude a partir de `shorts/inventario.md`.

```json
{
  "angulo": "tráiler",
  "dur": 30,
  "titulo": "Millones de moscas, soltadas a propósito #shorts",
  "descripcion": "Una plaga que ya ha cruzado a EE. UU. y un muro hecho de moscas. El caso completo, en el canal.",
  "comentario_fijado": "¿Lo frenarán a tiempo o ya es tarde? 👇",
  "beats": [
    {"voz": "Millones de moscas, soltadas a propósito.", "rot": "MILLONES DE MOSCAS|SOLTADAS *A PROPÓSITO*",
     "planos": [{"de": 22, "golpe": true, "ves": "una bandeja llena de moscas vivas"}]},
    {"voz": "Para frenar un gusano que se come vivo al ganado.", "rot": "UN GUSANO QUE SE COME|*VIVO* AL GANADO",
     "planos": [{"de": 3, "foco": [0.4, 0.5], "ves": "larvas en una herida"}, {"de": 7}], "sfx": "impactos"},
    {"voz": "La hembra solo se aparea una vez.", "rot": "LA HEMBRA SE APAREA|*UNA VEZ*",
     "planos": [{"de": 24, "desde": 6.0, "dur": 3.0, "foco": [0.55, 0.5], "ves": "animación: macho estéril y hembra"}]}
  ],
  "pregunta": "¿LO FRENARÁN|O YA ES *TARDE*?",
  "pregunta_voz": "¿Y tú qué crees? Te leo en los comentarios.",
  "cta": "El caso completo, en el canal",
  "like": "👍 si quieres más casos así",
  "bucle": false,
  "musica": {"src": "musica/climax/<pista>.mp3", "desde": 12, "vol": 0.42}
}
```

## Campos

- **angulo:** tráiler, dilema o dato (`retencion.md`). **dur:** la duración que pidió Antonio, en segundos.
- **beats:** una frase de voz cada uno, con su rótulo (`|` = salto de línea, `*palabra*` = ámbar) y sus planos. Un beat sin voz lleva `"dur"`.
- **planos:** se reparten la duración del beat a partes iguales, salvo los que llevan `"dur"`. Un beat sin planos alarga el plano anterior.
  - `{"de": n}`: el plano n del reportaje (columna «n» del inventario): copia el clip, la foto o la pieza.
  - `"desde"`: segundo de arranque dentro del clip o de la pieza (en una explicativa, el paso que interesa).
  - `"foco": [x, y]`: qué parte del 16:9 queda en el vertical (0-1; 0,5 = centro). Elegirlo mirando el fotograma: una cara o un detalle cortados no valen.
  - `"encaje"`: `"recorte"` (el plano llena la pantalla vertical) o `"marco"` (el 16:9 entero a lo ancho, en la franja central, con el rótulo del Short encima). **Las piezas animadas van enmarcadas por defecto**, porque llevan su propio texto (títulos, cifras) y recortadas lo pierden; se recortan solo si se da `"foco"`. Los clips y fotos van recortados por defecto; un archivo antiguo de baja resolución se ve borroso recortado (sale ampliado unas 3 veces): mejor enmarcado.
  - `"zoom": [1.04, 1.15]`, `"golpe": true` (sacudida y destello al entrar), `"vel"` (velocidad de un clip).
  - `"ves"`: lo que se ve, en palabras. Solo lo lee el juez a ciegas del guion: escríbelo como lo vería un espectador.
- **sfx** de un beat: uso del maestro de efectos (`impactos`, `tension`, `transiciones`, `documentos`, `electricidad`, `ambientes`).
- **pregunta / pregunta_voz / cta / like / comentario_fijado:** la interacción (`retencion.md`, S5).
- **musica.src:** ruta dentro de `relato-urbano-reportaje/audio/` (`musica/<uso>/<pista>.mp3`); `desde`, en qué segundo de la pista empieza.
