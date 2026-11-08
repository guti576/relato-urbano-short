// Render de un Short promocional (skill relato-urbano-short). scripts/short.py lo copia a <reportaje>/remotion/ y lo lanza;
// no se edita en el vídeo. Usa su propio punto de entrada (src/ShortsRoot.tsx): el Root.tsx del reportaje no se toca.
//   node remotion/render_short.mjs --datos shorts/S1/short.json --salida shorts/S1/_crudo.mp4
//   node remotion/render_short.mjs --datos shorts/S1/short.json --stills 0,0.5,1,1.5 --dir shorts/S1/_fot
// Nunca borra los temporales de Remotion de otros renders (puede haber un render del reportaje en marcha).
import fs from "node:fs";
import path from "node:path";
import {fileURLToPath} from "node:url";
import {bundle} from "@remotion/bundler";
import {renderMedia, renderStill, selectComposition} from "@remotion/renderer";

const here = path.dirname(fileURLToPath(import.meta.url));
const args = process.argv.slice(2);
const opt = (k) => (args.includes(k) ? args[args.indexOf(k) + 1] : null);
const raiz = path.join(here, "..");
const datos = JSON.parse(fs.readFileSync(path.resolve(raiz, opt("--datos")), "utf8"));
const serveUrl = await bundle({entryPoint: path.join(here, "src", "ShortsRoot.tsx"), publicDir: path.join(here, "public")});
process.on("exit", () => { try { fs.rmSync(serveUrl, {recursive: true, force: true}); } catch {} });
const inputProps = {datos};
const composition = await selectComposition({serveUrl, id: "ShortPromo", inputProps});
if (opt("--stills")) {
  const dir = path.resolve(raiz, opt("--dir") ?? "shorts/_fot");
  fs.mkdirSync(dir, {recursive: true});
  for (const s of opt("--stills").split(",").map(Number)) {
    const frame = Math.min(composition.durationInFrames - 1, Math.round(s * 30));
    await renderStill({composition, serveUrl, inputProps, frame, output: path.join(dir, `f_${s.toFixed(2)}.jpg`), imageFormat: "jpeg", jpegQuality: 82, scale: 0.5});
  }
  console.log("stills", dir);
  process.exit(0);
}
const salida = path.resolve(raiz, opt("--salida"));
await renderMedia({composition, serveUrl, inputProps, codec: "h264", crf: 18, audioCodec: "aac", outputLocation: salida, concurrency: 4,
  onProgress: ({progress}) => { if (Math.round(progress * 100) % 10 === 0) process.stdout.write(`\r${Math.round(progress * 100)} %`); }});
console.log("\nok", salida);
process.exit(0);
