# Impacto, retención e interacción en los Shorts

Lo que pidió Antonio (8-11-2026): Shorts **que tengan impacto**, que la gente **aguante hasta el final y no deslice**, que **comente y dé like**, y que **lleven al reportaje largo**. YouTube posiciona un Short por cuántos lo ven en vez de deslizar, cuánto ven (y si lo repiten) y cuánta interacción provoca. Todo lo de abajo sirve a eso.

## Los ángulos (uno por Short; nunca dos iguales del mismo reportaje)

Por defecto se proponen tres: **tráiler, quiz y dato**. El quiz lo pidió Antonio (8-11-2026) como una de las propuestas fijas, porque hace comentar. El dilema queda como alternativa al quiz cuando el caso no da para una pregunta con respuesta.

| Ángulo | Para qué | Estructura | Pregunta final |
|---|---|---|---|
| **tráiler** | Llevar al reportaje | Gancho con el hecho más fuerte → 2 giros que suben → la pregunta del caso sin responder | «¿…? La respuesta, en el reportaje» |
| **quiz** | Comentarios | Pregunta de entrada con su imagen → 2-3 frases de contexto → 3 opciones en pantalla, leídas por la voz → cuenta atrás de 3 s → **sin solución** | «Comenta A, B o C» · «La respuesta, en el reportaje del canal» |
| **dilema** | Comentarios (alternativa al quiz) | Un dato polémico o una decisión discutible del caso → las dos posturas en 2 frases cada una | «¿A o B?», fácil de contestar en una palabra |
| **dato** | Repetición y likes | Un solo hecho increíble explicado con la pieza explicativa del reportaje, en bucle | Opcional; la última frase enlaza con la primera |

Si Antonio pide otra cosa, manda lo suyo. Si pide más de tres, se repite ángulo con otro gancho y otros planos.

## El quiz (quick quiz)

- **Una pregunta con respuesta comprobada** que el reportaje sí da. Sale de la hoja «Hechos y fuentes» (Demostrado), nunca de algo que no se sabe. Por ejemplo, en Columbia: «¿Qué hizo la NASA cuando pidieron fotos del ala dañada?».
- **La pregunta va en el primer segundo**, en voz y en pantalla, con la imagen del caso más inquietante. El contexto viene después y es corto: el espectador ya está jugando.
- **Tres opciones**, cortas (4 palabras como mucho) y todas creíbles. La buena no es siempre la B, ni la más larga, ni la más rara. Con una opción absurda el quiz parece de broma.
- **La voz lee las opciones** («¿A, las pidió al ejército? ¿B…?») y entra la **cuenta atrás de 3 s** con un tic por segundo. Mientras dura, nada más en pantalla.
- **La respuesta no se da nunca, ni se insinúa.** Ni en la voz, ni en el texto, ni en la descripción, ni en el comentario fijado. Está en el reportaje: el cierre lo dice («La respuesta, en el reportaje del canal») y el reportaje va como vídeo relacionado.
- **Cierre:** en pantalla, «COMENTA: *A*, *B* O *C*». En voz, «¿Cuál dices tú? Te leo abajo». Comentario fijado: «¿A, B o C? La respuesta, en el reportaje del canal 👇».
- **Cuando el Short ya lleva días publicado**, se puede responder a los comentarios remitiendo al minuto del reportaje donde está la respuesta, sin decirla.

## Los dos primeros segundos (puerta S1)

- **Fotograma 0 con imagen en movimiento y texto.** Nada de negro, logo, título ni fundido de entrada.
- **La voz arranca en el fotograma 1-2** con la frase más fuerte del Short: un hecho que choca, un nombre con una acusación, una cifra que no cabe en la cabeza. Nunca contexto («En 1991…»).
- **Giro hacia el segundo 1,5:** cambia el plano o llega un golpe que da la vuelta a la primera frase (lección de los Shorts de octubre).
- La primera imagen es **del caso**, la más rara o inquietante del reportaje, no stock genérico.

## Ritmo (S2)

- Un plano cada 1-2,5 s (las piezas explicativas, hasta 4 s). Ningún tramo quieto de más de 1,2 s.
- **Bajo la pregunta final, un clip en movimiento**, nunca una pieza de cifras parada: la tarjeta dura 2-4 s y el último plano se alarga hasta el final (que el clip no se acabe antes: `"vel": 0.8`).
- Golpe de sonido en el fotograma 0, en cada giro y en la pregunta final; efectos solo del maestro de audio.
- Nada de pausas: 0,08 s entre frases. La voz va a 1,08x.
- **Una cifra dice dónde y desde cuándo** («solo en México y Centroamérica…»). Sin eso suena a exageración y se pierde el espectador (los dos deslizadores de la prueba de L07).
- No mezclar épocas a saltos: primero lo de época y, si hace falta, lo actual al final como remate.

## Texto (S4)

- Centrado, Anton en mayúsculas, **palabra clave en ámbar** (`*palabra*`), 7 palabras por pantalla como mucho, una idea por rótulo.
- Siempre dentro de la zona segura (la plantilla la respeta): libre la franja de abajo (título y descripción) y la de la derecha (botones).
- Cuando hay algo que mirar (un detalle de la pieza, una cara), el texto se retira o sube (`"arriba": true`).

## Duración y palabras (S3)

La duración la pide Antonio. A 1,08x la voz va a **unas 2,9 palabras por segundo** (medido en L07), y la pregunta final deja 1-2,5 s de cola:

| Duración | Palabras de voz (con la pregunta) |
|---|---|
| 15 s | 35-42 |
| 30 s | 75-87 |
| 45 s | 117-132 |
| 60 s | 158-177 |

Si el montaje se aleja más de un 10 %, se ajusta el **texto**, nunca la velocidad.

## Interacción (S5)

- **Una sola pregunta, al final**, que se conteste en una palabra («¿Amor o interés?», «¿Error o encubrimiento?»). En pantalla en grande: `COMENTA: *A* O *B*` o la pregunta con su clave en ámbar.
- **En la voz no se lee la llamada tal cual** (lo pidió Antonio con Hachiko): «¿Y tú qué crees? Te leo en los comentarios».
- **Like:** una línea pequeña bajo la pregunta (`like`), por ejemplo «👍 si quieres más casos así». Nunca a mitad de Short: corta la retención.
- **Llamada al reportaje** (`cta`): «El caso completo, en el canal». El enlace no va en la descripción (canal sin verificar): va en **Vídeo relacionado** al subir.
- **Comentario fijado** con la misma pregunta y las dos opciones, para que la conversación empiece sola.
- En los reportajes largos no se pide comentar (`estilo.md`); en los Shorts sí, con esta forma.

## Bucle (S7)

En el ángulo **dato** (y en otros si encaja): la última frase deja una idea abierta que completa la primera, y el último plano es el primero. Quien llega al final lo ve otra vez sin darse cuenta.

## No destripar (S6)

Un Short promociona: **no da la respuesta**. Lo que el reportaje se guarda (hoja Pistas, «Qué se guarda»; acto 4 y cierre de la hoja Hilo) no suena ni se ve. `short.py inventario` lo lista arriba del todo.

## Imagen y sonido

- Solo material del propio reportaje (sus clips, fotos, documentos y piezas). Si falta algo, se baja como en el reportaje (fuentes_material.md), con licencia y crédito.
- Personas de stock reconocibles nunca como víctimas, culpables ni enfermos.
- Música: solo del maestro de audio (`relato-urbano-reportaje/audio/musica/<uso>/`), elegida por el ángulo: tráiler → `climax` o `tension`; dilema → `misterio`; dato → `pulso`. Nada de Pixabay ni otras fuentes: Content ID.
- Sonoridad -14 LUFS y pico -1,5 (lo hace `short.py render`).
