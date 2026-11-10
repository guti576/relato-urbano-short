---
name: relato-urbano-short
description: Monta Shorts promocionales verticales (1080x1920) de un reportaje largo de Relato Urbano con su propio material (sobre todo clips de vídeo y las mejores piezas animadas de Remotion), con voz gratuita en el borrador y de Fish Audio cuando Antonio lo aprueba, para que la gente no deslice, aguante hasta el final, comente, dé like y vaya al reportaje. Prepara tres ángulos distintos (tráiler, quiz para comentar y dato) de la duración que pida Antonio, los pasa por sus puertas y por un juez a ciegas, y deja un informe de una página para que él elija cuáles publicar y cuándo. Úsala siempre que Antonio pida "shorts de L07", "promociona el reportaje de X", "un short de 30 segundos del gusano", "saca shorts del vídeo largo" o similar, aunque no nombre la skill. No es para Shorts sueltos sin reportaje detrás ni para Ovillo Rojo.
---

# Relato Urbano: Shorts promocionales de un reportaje

Antonio dice de qué reportaje y de qué duración; tú haces el resto y te paras solo para que elija cuáles se publican y cuándo. Háblale en español y sin jerga. Va en la línea de la skill `relato-urbano-reportaje` y usa sus piezas (carpeta de proyectos, `voz_fish.py`, maestro de audio, Remotion del reportaje): léela si no la conoces.

## Qué busca cada Short

Lo pidió Antonio (8-11-2026): **impacto**, que **no deslicen y aguanten hasta el final**, que **comenten y den like**, y que **lleven al reportaje largo**, porque así los posiciona YouTube. Las reglas concretas están en `references/retencion.md`: léelas antes de escribir nada.

**Un Short no es una foto con texto y voz** (Antonio, 10-11-2026): **casi todo son clips de vídeo** del reportaje o **piezas animadas de las que quedaron muy bien**. Las fotos y los documentos solo pasan de largo (1,5 s como mucho y una cuarta parte del Short en total); `short.py control` lo comprueba.

**Quien ve el Short no conoce el caso** (Antonio, 9-11-2026): no ha visto el reportaje ni sabe quién es nadie. La narración lo sitúa (qué, dónde, cuándo) y explica cada nombre, sigla y lugar al entrar; si no, se pierde y desliza.

Por defecto, **tres Shorts por reportaje, cada uno con un ángulo**: tráiler, **quiz** y dato. El quiz (Antonio, 8-11-2026) es un quick quiz para que la gente comente: pregunta, tres opciones, cuenta atrás y «Comenta A, B o C»; **la respuesta no se da: está en el reportaje publicado en el canal**. El dilema queda como alternativa al quiz. Todos de la duración que diga Antonio (o la que diga para cada uno). El borrador lleva la voz gratuita; el Short que Antonio aprueba pasa a la voz de Fish (Gabriel VO, modelo de pago).

## El proceso

Proyecto: `<carpeta de proyectos>/<LNN_Tema>/` (la encuentra `relato-urbano-reportaje/scripts/rutas.py`). Todo lo de los Shorts va en `<LNN_Tema>/shorts/`. El script es `scripts/short.py` de esta skill.

1. **Inventario.** `python short.py inventario <id>` → `shorts/inventario.md`: lo que **no** se puede contar (la respuesta es del reportaje), los giros de la hoja Pistas, las cifras demostradas y todos los planos del montaje numerados, con lo que dice la voz en cada uno. Si el reportaje aún no tiene `m1.json`, los Shorts esperan: se hacen con el material ya montado.
2. **Guiones.** Escribe `shorts/S1/guion.json`, `S2` y `S3` (formato en `references/guion_short.md`), uno por ángulo, sin repetir gancho ni planos. Para elegir el `foco` de un plano, mira su fotograma (`relato-urbano-reportaje/scripts/render.py <id> stills` o el clip).
3. **Puertas en papel, antes de pagar nada.** `python short.py control <id> S1 --papel` y el deslizador en papel: `python short.py juez <id> S1 papel` y dos subagentes nuevos con los mensajes que imprime. Corrige en una tanda (`short.py ronda`).
4. **Voz gratuita para el borrador.** `python short.py voz <id> S1` (sin `--modelo`): la voz gratuita de Microsoft (Álvaro, de Edge; sin internet, la de Windows). Todo el borrador (montaje, render, jueces e informe) va con ella. **Fish no se toca hasta el ok final de Antonio a ese Short** (Antonio, 10-11-2026): el script lo rechaza sin `--ok`. Recorta silencios y la pone a 1,08x.
5. **Montaje y render.** `python short.py montar <id> S1` (short.json con los tiempos reales de la voz; si se aleja de la duración pedida, ajusta el texto) y `python short.py render <id> S1 --stills` para mirar fotogramas sueltos antes del render completo; después `python short.py render <id> S1` → `shorts/S1/<id>_S1.mp4`, nivelado a -14 LUFS. El render del Short usa su propia composición (`ShortsRoot.tsx`, que se copia sola al Remotion del reportaje): no toca el reportaje ni pasa por su candado, pero si hay un render del reportaje en marcha, espera a que acabe.
6. **Puertas del vídeo.** `python short.py juez <id> S1 video` (dos subagentes) y `python short.py control <id> S1`. Puertas en `references/puertas.md`.
7. **Informe y decisión.** `python short.py informe <id>` → `shorts/informe.md`, una página: por Short, título, pregunta, voz, qué pasa, qué falla y qué se puede mejorar. Enséñale a Antonio los tres borradores y el informe, y pregunta cuáles da por buenos y en qué fechas (propuesta en `references/publicar.md`).
8. **Voz final, solo de los que apruebe.** `python short.py voz <id> S1 --presupuesto` y luego `--modelo s2.1-pro --ok "<sus palabras>"` (unos 300-600 caracteres por Short). Va por `voz_fish.py` de la skill del reportaje: caché, tope y registro de gasto incluidos. Después `montar`, `render` y `control` (solo las puertas técnicas y de duración; el texto ya no cambia, así que no hacen falta jueces nuevos).
9. **Publicar.** Solo con su confirmación de título, fecha y hora: escribe `shorts/S1/publicacion.json` (título, descripción, vídeo relacionado, comentario fijado, fecha) y súbelo como dice `references/publicar.md`.

## Sin bucles

Como en los reportajes (Antonio: «no puede estar constantemente iterando»): se corrige en tandas, todo de una vez; cada tanda se registra con `short.py ronda <id> S1 --nota "..."`; **dos rondas por Short como mucho**. Si después algo sigue fallando, no se toca más: va al informe y decide él. La segunda ronda del deslizador es `--verificar`. La voz de Fish se paga una vez y al final, con el texto ya aprobado; hasta entonces, la gratuita.

## Lo que siempre se pregunta

- **Publicar o programar**: título, fecha y hora de cada Short.
- Material nuevo con derechos dudosos.
- Si el reportaje largo aún no es público: un Short no se publica antes que su reportaje.

No crees tareas programadas ni recordatorios. Si Antonio corrige algo que vale para los siguientes Shorts, añádelo a `references/retencion.md` y díselo en una línea.
