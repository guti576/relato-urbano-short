# Publicar los Shorts

**Nunca se sube ni se programa sin que Antonio confirme título, fecha y hora** de cada uno.

## Cuándo

- El reportaje largo tiene que estar **público** (o al menos programado antes que el Short): el Short lo enlaza como «Vídeo relacionado».
- Propuesta por defecto (Antonio la cambia cuando quiera): largo el sábado a las 11:00; **S1 el domingo a las 18:00**, S2 el martes y S3 el jueves, a las 18:00 de Madrid. Primero el que más lleva al largo (tráiler), después el de comentarios (dilema) y el del dato.
- No coincidir con otro Short ya programado ese día (mira el calendario de la memoria del canal).

## Qué lleva cada uno (`shorts/S1/publicacion.json` lo junta)

- **Título**: el de `guion.json`, 60 caracteres o menos, con `#shorts` al final (y un espacio detrás: si no, Studio autocompleta «#shortsfeed»).
- **Descripción**: dos líneas que planteen la pregunta, sin enlaces (canal sin verificar), y los créditos del material usado (los del reportaje, `CREDITOS.txt`).
- **Vídeo relacionado**: el reportaje largo (en Studio está en «Video elements», no en «Details»).
- **Miniatura**: un fotograma del gancho con la clave en ámbar, si Studio deja subirla.
- **Comentario fijado**: la pregunta de `comentario_fijado`, publicado y fijado nada más salir el Short.
- «No, it's not made for kids»; zona horaria Madrid.

## Cómo

Subida con Claude in Chrome en YouTube Studio, como los Shorts del canal: subir el archivo, título, descripción, «Video elements» → vídeo relacionado, programar fecha y hora (escritas en el campo del calendario), y localizar los botones con `find` (las coordenadas cambian). Studio recomienda no publicar hasta que acaben las comprobaciones (unos 5 min). Pulsar Escape en el diálogo lo cierra y deja un borrador.

Después, anota en `shorts/estado.json` el enlace y la fecha de cada uno, y en la memoria del canal el calendario.
