# Las puertas de un Short

Las mismas ideas que el reglamento del reportaje: lo que se puede comprobar lo comprueba `short.py control` o un juez a ciegas, y a Antonio solo le llegan los vídeos y una página para decidir. **Sin bucles:** correcciones en tandas, dos rondas por Short como mucho (`short.py ronda`), y después el informe.

| # | Puerta | Guion (`--papel`, antes de pagar voz) | Vídeo montado |
|---|---|---|---|
| S1 | Gancho | Primera frase de 12 palabras o menos; el primer beat tiene imagen | La voz arranca antes de 0,3 s y el primer cambio de plano llega antes de 1,6 s; el deslizador no desliza en el 1 ni antes del 3 |
| S2 | Ritmo | — | Ningún plano de más de 2,5 s (explicativas, 4 s); ningún tramo quieto de 1,2 s o más |
| S3 | Duración y voz | Palabras dentro del presupuesto de la duración pedida | Duración a ±15 % de la pedida (fallo); 2,4-3,4 palabras por segundo (aviso) |
| S4 | Texto legible | Cada frase con su rótulo; 7 palabras por rótulo como mucho | (lo garantiza la plantilla: zona segura y tamaño) |
| S5 | Interacción | Pregunta final, su versión en voz, comentario fijado y llamada al reportaje; pregunta fácil de contestar; título de 60 caracteres o menos | El deslizador escribe un comentario concreto (fallo si «nada»); like y repetición, aviso. **Quiz:** 3 opciones (4 como mucho) de 4 palabras o menos, `correcta` marcada y la llamada dice que la respuesta está en el reportaje |
| S6 | Sin destripar | Aviso si comparte palabras con lo que el reportaje se guarda. **Quiz:** fallo si la opción buena se escapa fuera de las opciones (voz, rótulos, título, descripción, comentario fijado) | El deslizador no siente que ya sabe cómo acaba ni que el Short le dé la respuesta del quiz; le dan ganas de ver el reportaje |
| S7 | Bucle | Marcado si el ángulo lo pide | El último plano es el primero (aviso) |
| S8 | Técnica | Música del maestro de audio | 1080x1920, -14 LUFS ±1, pico ≤ -1 dBTP |
| S9 | Ángulos distintos | Ningún Short del mismo reportaje comparte ángulo ni plano de gancho (fallo); más del 25 % de planos en común, aviso | Igual |

## El deslizador (juez a ciegas)

Un subagente nuevo, sin contexto, que hace de espectador con el pulgar sobre la pantalla. Encargo fijo en `short.py` (`FORMULARIO`): si desliza en el segundo 1 o antes del 3, si llega al final, si siente que ya sabe cómo acaba, si le dan ganas de ver el reportaje, qué comentaría palabra por palabra, si daría like y si lo vería otra vez.

- **En papel** (`short.py juez <id> S1 papel`): antes de pagar la voz, con lo que se ve y se oye escrito. Es lo barato: aquí se cambia el gancho.
- **Montado** (`short.py juez <id> S1 video`): con los fotogramas de los 3 primeros segundos cada 0,25 s y uno por segundo del resto.
- Dos subagentes distintos cada vez; vale el peor. La segunda ronda, `--verificar` (portería fija: solo comprueba lo señalado).
- Lanza cada subagente con el mensaje exacto que imprime el script y nada más. Si el resultado no gusta, se cambia el Short, nunca el encargo.
