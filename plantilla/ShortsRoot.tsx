// Raíz de los Shorts promocionales (skill relato-urbano-short). Se copia a <reportaje>/remotion/src/ y se renderiza con su
// propio punto de entrada, sin tocar el Root.tsx del reportaje. Los datos del Short llegan como props (short.json).
import React from "react";
import {Composition, continueRender, delayRender, registerRoot} from "remotion";
import {cargarFuentes} from "./estilo";
import {ShortPromo} from "./ShortPromo";

const espera = delayRender("fuentes");
cargarFuentes().then(() => continueRender(espera));

const Root: React.FC = () => (
  <Composition id="ShortPromo" component={ShortPromo as any} fps={30} width={1080} height={1920} durationInFrames={300}
    defaultProps={{datos: null}}
    calculateMetadata={({props}) => ({durationInFrames: Math.max(30, Math.ceil(((props as any).datos?.dur ?? 10) * 30))})} />
);
registerRoot(Root);
