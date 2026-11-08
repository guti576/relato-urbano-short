// Short promocional vertical (1080x1920) montado con el material del propio reportaje: sus clips, fotos, documentos y
// piezas animadas (Piezas.tsx), recortadas o enmarcadas en vertical. Todo sale de short.json (props «datos»), que escribe
// scripts/short.py. Reglas de impacto, zona segura e interacción: references/retencion.md de la skill.
import React from "react";
import {AbsoluteFill, Audio, Easing, Img, OffthreadVideo, Sequence, interpolate, staticFile, useCurrentFrame} from "remotion";
import {FILTRO_OSCURO, Grano, IMPACTO, SANS, Tiniebla} from "./estilo";
import {Pieza} from "./Piezas";

const FPS = 30;
const W = 1080, H = 1920;
const AMBAR = "#FFB627";
const m = (r: string) => staticFile("m/" + r);
const clamp = {extrapolateLeft: "clamp", extrapolateRight: "clamp"} as const;
const fr = (s: number) => Math.round(s * FPS);

// Zona segura de Shorts: arriba la barra, abajo título y descripción, a la derecha los botones.
export const SEGURA = {izq: 70, der: 150, arriba: 260, abajo: 560};

type Plano = {tipo: "V" | "F" | "D" | "A"; ini: number; dur: number; clip?: string; img?: string; key?: string; desde?: number; total?: number;
  foco?: [number, number]; zoom?: [number, number]; encaje?: "recorte" | "marco"; brillo?: number; golpe?: boolean; vel?: number};
type Texto = {ini: number; dur: number; rot: string; arriba?: boolean; ya?: boolean};
type Datos = {dur: number; planos: Plano[]; textos: Texto[]; voz: {src: string; ini: number; dur: number}[];
  musica?: {src: string; desde?: number; vol?: number}; sfx?: {t: number; src: string; vol?: number; dur?: number}[];
  final?: {ini: number; pregunta: string; cta: string; like?: string}};

const zoomDe = (p: Plano, f: number, n: number) => {
  const [a, b] = p.zoom ?? [1.04, 1.12];
  return interpolate(f, [0, n], [a, b], {...clamp, easing: Easing.inOut(Easing.quad)});
};

// Vídeo o foto a pantalla completa en vertical: recorte con el foco elegido, o enmarcado con fondo desenfocado.
const Imagen: React.FC<{p: Plano; n: number}> = ({p, n}) => {
  const f = useCurrentFrame();
  const z = zoomDe(p, f, n);
  const [fx, fy] = p.foco ?? [0.5, 0.5];
  const filtro = `${FILTRO_OSCURO}${p.brillo ? ` brightness(${p.brillo})` : ""}`;
  const fuente = (estilo: React.CSSProperties) => p.tipo === "V"
    ? <OffthreadVideo src={m("clips/" + p.clip)} muted trimBefore={fr(p.desde ?? 0)} playbackRate={p.vel ?? 1} style={estilo} />
    : <Img src={m((p.tipo === "D" ? "img/" : "fotos/") + p.img)} style={estilo} />;
  if (p.encaje === "marco") {
    return <AbsoluteFill style={{background: "#000", overflow: "hidden"}}>
      {fuente({position: "absolute", inset: -80, width: W + 160, height: H + 160, objectFit: "cover", filter: "blur(44px) brightness(.3) saturate(.6)"})}
      <div style={{position: "absolute", left: 0, top: 700, width: W, height: 608, overflow: "hidden"}}>
        {fuente({width: "100%", height: "100%", objectFit: "cover", objectPosition: `${fx * 100}% ${fy * 100}%`, transform: `scale(${z})`, filter: filtro})}
      </div>
      <Grano opacidad={0.1} />
    </AbsoluteFill>;
  }
  return <AbsoluteFill style={{background: "#000", overflow: "hidden"}}>
    {fuente({width: "100%", height: "100%", objectFit: "cover", objectPosition: `${fx * 100}% ${fy * 100}%`, transform: `scale(${z})`, transformOrigin: `${fx * 100}% ${fy * 100}%`, filter: filtro})}
    <Tiniebla fuerza={0.5} />
    <Grano opacidad={0.09} />
  </AbsoluteFill>;
};

// Pieza animada del reportaje (16:9) en vertical: recortada a la altura con el foco elegido, o enmarcada a lo ancho.
const PiezaV: React.FC<{p: Plano; n: number}> = ({p, n}) => {
  const f = useCurrentFrame();
  const total = fr(p.total ?? p.dur);
  const pieza = <Sequence from={-fr(p.desde ?? 0)} layout="none"><Pieza k={p.key!} n={total} /></Sequence>;
  if (p.encaje === "marco") {
    const s = W / 1920;
    const sf = (H / 1080) * 1.1;
    return <AbsoluteFill style={{background: "#07080A", overflow: "hidden"}}>
      {/* detrás, la misma pieza ampliada y desenfocada: rellena el vertical sin dejar negro */}
      <div style={{position: "absolute", left: (W - 1920 * sf) / 2, top: (H - 1080 * sf) / 2, width: 1920, height: 1080, transformOrigin: "0 0", transform: `scale(${sf})`, filter: "blur(26px) brightness(.32) saturate(.7)"}}>{pieza}</div>
      <div style={{position: "absolute", left: 0, top: 700, width: 1920, height: 1080, transformOrigin: "0 0", transform: `scale(${s * zoomDe(p, f, n)})`}}>{pieza}</div>
    </AbsoluteFill>;
  }
  const s = (H / 1080) * zoomDe(p, f, n);
  const ancho = 1920 * s;
  const tx = Math.min(0, Math.max(W - ancho, W / 2 - (p.foco?.[0] ?? 0.5) * ancho));
  const ty = (H - 1080 * s) / 2;
  return <AbsoluteFill style={{background: "#000", overflow: "hidden"}}>
    <div style={{position: "absolute", left: 0, top: 0, width: 1920, height: 1080, transformOrigin: "0 0", transform: `translate(${tx}px, ${ty}px) scale(${s})`}}>{pieza}</div>
  </AbsoluteFill>;
};

// Texto centrado en la zona segura, Anton, palabra clave entre *asteriscos* en ámbar, | = salto de línea.
const Rotulo: React.FC<{t: Texto}> = ({t}) => {
  const f = useCurrentFrame();
  const lineas = t.rot.split("|");
  const grande = lineas.length === 1 && t.rot.replace(/\*/g, "").length <= 14;
  const sale = interpolate(f, [fr(t.dur) - 4, fr(t.dur)], [1, 0], clamp);
  return (
    <div style={{position: "absolute", left: SEGURA.izq, right: SEGURA.der, top: t.arriba ? SEGURA.arriba + 40 : 640, height: t.arriba ? 380 : 620,
      display: "flex", flexDirection: "column", justifyContent: "center", alignItems: "center", textAlign: "center", opacity: sale,
      fontFamily: IMPACTO, fontSize: grande ? 128 : 94, lineHeight: 1.12, letterSpacing: 1, color: "#fff", textShadow: "0 6px 24px rgba(0,0,0,.95), 0 0 4px #000"}}>
      {lineas.map((x, j) => {
        const k = t.ya ? 1 : interpolate(f, [j * 3, 4 + j * 3], [0, 1], clamp);   // el primer rótulo ya está en el fotograma 0
        return <div key={j} style={{opacity: k, transform: `translateY(${(1 - k) * 34}px) scale(${0.92 + 0.08 * k})`}}>
          {x.split("*").map((q, i) => <span key={i} style={{color: i % 2 ? AMBAR : "#fff"}}>{q}</span>)}
        </div>;
      })}
    </div>
  );
};

// Cierre: la pregunta para comentar y la llamada al reportaje completo.
const Final: React.FC<{d: NonNullable<Datos["final"]>; n: number}> = ({d, n}) => {
  const f = useCurrentFrame();
  const a = interpolate(f, [0, 6], [0, 1], clamp);
  const b = interpolate(f, [10, 18], [0, 1], clamp);
  const late = 1 + 0.03 * Math.sin(f / 4);
  return (
    <AbsoluteFill>
      <AbsoluteFill style={{background: "rgba(0,0,0,.8)", opacity: a}} />
      <div style={{position: "absolute", left: SEGURA.izq, right: SEGURA.der, top: 520, height: 640, display: "flex", flexDirection: "column", justifyContent: "center", alignItems: "center", textAlign: "center"}}>
        <div style={{opacity: a, transform: `scale(${(0.9 + 0.1 * a) * late})`, fontFamily: IMPACTO, fontSize: 104, lineHeight: 1.1, color: "#fff", textShadow: "0 6px 24px #000"}}>
          {d.pregunta.split("|").map((x, j) => <div key={j}>{x.split("*").map((q, i) => <span key={i} style={{color: i % 2 ? AMBAR : "#fff"}}>{q}</span>)}</div>)}
        </div>
        <div style={{opacity: b, marginTop: 46, fontFamily: SANS, fontWeight: 700, fontSize: 44, letterSpacing: 2, color: "#F2ECE0", textShadow: "0 3px 12px #000"}}>{d.cta}</div>
        {d.like && <div style={{opacity: b, marginTop: 22, fontFamily: SANS, fontWeight: 600, fontSize: 38, color: AMBAR, textShadow: "0 3px 12px #000"}}>{d.like}</div>}
      </div>
    </AbsoluteFill>
  );
};

export const ShortPromo: React.FC<{datos: Datos}> = ({datos: d}) => {
  const f = useCurrentFrame();
  if (!d) return <AbsoluteFill style={{background: "#400"}} />;
  const t = f / FPS;
  const DUR = fr(d.dur);
  // golpe visual: sacudida y destello en el fotograma 0 y en cada plano marcado
  const golpes = [0, ...d.planos.filter((p) => p.golpe).map((p) => fr(p.ini))];
  const g = Math.max(0, ...golpes.map((a) => (f < a ? 0 : interpolate(f, [a, a + 7], [1, 0], clamp))));
  const habla = d.voz.some((v) => t > v.ini - 0.05 && t < v.ini + v.dur + 0.05);
  const volM = (q: number) => (d.musica?.vol ?? 0.42) * (habla ? 0.55 : 1) * interpolate(q, [DUR - 15, DUR], [1, 0], clamp);
  return (
    <AbsoluteFill style={{background: "#000"}}>
      <div style={{position: "absolute", inset: 0, transform: `translate(${Math.sin(f * 2.3) * 14 * g}px, ${Math.cos(f * 3.1) * 11 * g}px)`}}>
        {d.planos.map((p, i) => {
          const n = Math.max(1, fr(p.dur));
          return <Sequence key={i} from={fr(p.ini)} durationInFrames={n + 1} premountFor={15}>
            {p.tipo === "A" ? <PiezaV p={p} n={n} /> : <Imagen p={p} n={n} />}
          </Sequence>;
        })}
      </div>
      <AbsoluteFill style={{background: "#fff", opacity: g * 0.2}} />
      {d.textos.map((x, i) => <Sequence key={"t" + i} from={fr(x.ini)} durationInFrames={Math.max(1, fr(x.dur))}><Rotulo t={x} /></Sequence>)}
      {d.final && <Sequence from={fr(d.final.ini)}><Final d={d.final} n={DUR - fr(d.final.ini)} /></Sequence>}
      {d.voz.map((v, i) => <Sequence key={"v" + i} from={fr(v.ini)} durationInFrames={fr(v.dur) + 4}><Audio src={m(v.src)} /></Sequence>)}
      {d.musica && <Audio src={m(d.musica.src)} trimBefore={fr(d.musica.desde ?? 0)} volume={volM} />}
      {(d.sfx ?? []).map((x, i) => <Sequence key={"s" + i} from={fr(x.t)} durationInFrames={fr(x.dur ?? 2.5)}><Audio src={m(x.src)} volume={x.vol ?? 0.6} /></Sequence>)}
    </AbsoluteFill>
  );
};
