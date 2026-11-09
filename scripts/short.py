# -*- coding: utf-8 -*-
"""Shorts promocionales de un reportaje de Relato Urbano, con su propio material (skill relato-urbano-short).

  python short.py inventario L07_Gusano                    # material, giros y lo que no se cuenta -> shorts/inventario.md
  python short.py control   L07_Gusano S1 --papel          # puertas del guion del Short (antes de pagar voz)
  python short.py juez      L07_Gusano S1 papel            # paquete del «deslizador» a ciegas (dos subagentes)
  python short.py voz       L07_Gusano S1 --presupuesto    # cuánto costaría la voz
  python short.py voz       L07_Gusano S1 --modelo s2.1-pro
  python short.py montar    L07_Gusano S1                  # short.json con los tiempos de la voz
  python short.py render    L07_Gusano S1 [--stills]       # vídeo nivelado -> shorts/S1/<id>_S1.mp4
  python short.py control   L07_Gusano S1                  # puertas del vídeo montado
  python short.py juez      L07_Gusano S1 video [--verificar]
  python short.py ronda     L07_Gusano S1 --nota "..."     # tanda de corrección (2 como mucho)
  python short.py informe   L07_Gusano                     # una página para Antonio con los tres Shorts

Cada Short vive en <reportaje>/shorts/<S>/ y lo describe guion.json (formato en references/guion_short.md). El montaje
usa la composición vertical ShortPromo (plantilla/), que tira de los clips, fotos y piezas del propio reportaje.
"""
import argparse, glob, hashlib, json, os, re, shutil, subprocess, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(AQUI)
REP = os.path.join(os.path.dirname(SKILL), "relato-urbano-reportaje")
sys.path.insert(0, os.path.join(REP, "scripts"))
from rutas import RAIZ  # noqa: E402
from control_reglas import excel, hoja, seg, mmss  # noqa: E402
import control_hilo  # noqa: E402

AUDIO = os.path.join(REP, "audio")
FPS = 30
VELOCIDAD = 1.08          # la voz del Short va un poco más rápida que la del reportaje (Hachiko, L07)
PAUSA = 0.08              # entre frases: casi nada, un Short no respira
ARRANQUE = 0.05           # la primera palabra suena en el fotograma 1 o 2
MAX_RONDAS = 2
PPS = (2.4, 3.4)          # palabras por segundo de la voz montada (aviso fuera)
PLANO_MAX = 2.5           # s por plano; las piezas explicativas, 4
PLANO_MAX_EXPLIC = 4.0
PALABRAS_PANTALLA = 7     # palabras por rótulo como mucho
VOZ_MODELOS = ("s2.1-pro", "s2.1-pro-free")


def log(*a):
    print(*a, flush=True)


def carpeta(a):
    return os.path.join(a.raiz, a.id)


def dir_short(a):
    return os.path.join(carpeta(a), "shorts", a.s)


def ffprobe_dur(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p], capture_output=True, text=True)
    return float(r.stdout or 0)


def m1(c):
    p = os.path.join(c, "remotion", "src", "m1.json")
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else None


def voz_reportaje(c):
    """{código: texto} de m1_voz.md del reportaje."""
    p = os.path.join(c, "m1_voz.md")
    out = {}
    if os.path.exists(p):
        for l in open(p, encoding="utf-8"):
            m = re.match(r"^\s*(\d{3,4})\.\s+(.+)$", l.strip())
            if m:
                out[m.group(1)] = m.group(2).strip()
    return out


def leer_guion(a):
    p = os.path.join(dir_short(a), "guion.json")
    if not os.path.exists(p):
        sys.exit(f"Falta {p} (formato en references/guion_short.md).")
    return json.load(open(p, encoding="utf-8"))


# ------------------------------------------------------------------ inventario

def cmd_inventario(a):
    c = carpeta(a)
    d = m1(c)
    if not d:
        sys.exit("El reportaje no tiene remotion/src/m1.json: los Shorts se hacen con el material ya montado.")
    xls, hojas = excel(c)
    est = json.load(open(os.path.join(c, "estado.json"), encoding="utf-8")) if os.path.exists(os.path.join(c, "estado.json")) else {}
    hilo = control_hilo.leer_hilo(hojas) or {}
    pistas = hoja(hojas, "Pistas") or []
    hechos = hoja(hojas, "Hechos") or []
    voz = voz_reportaje(c)
    tiempos = [(float(v["ini"]), float(v["ini"]) + float(v["dur"]), voz.get(str(v["n"]), "")) for v in d.get("voz", [])]
    lin = [f"# Inventario para Shorts · {a.id}", "", f"**Reportaje:** {est.get('titulo', '—')} · fase {est.get('fase', '—')} · {mmss(d.get('dur', 0))}",
           f"**Pregunta madre:** {hilo.get('pregunta') or '—'}", ""]
    lin += ["## Lo que NO se cuenta en un Short (la respuesta es del reportaje)", ""]
    for r in pistas:
        g = str(r.get("Qué se guarda") or "").strip()
        if g:
            lin.append(f"- {g}")
    if hilo.get("actos", {}).get(4):
        lin.append(f"- Final (acto 4): {hilo['actos'][4]}")
    cierre = [str(r.get("Voz en off") or "") for r in (hojas.get("guion") or []) if re.search("cierre", str(r.get("ID escena") or ""), re.I)]
    if cierre:
        lin.append(f"- Cierre: {' '.join(cierre)[:300]}")
    lin += ["", "## Giros (hoja Pistas): la materia prima de los ganchos", ""]
    for r in pistas:
        lin.append(f"- {r.get('Minuto aprox') or '?'} · {str(r.get('Qué se revela') or '').strip()} · función: {str(r.get('Función') or '').strip()}")
    lin += ["", "## Cifras demostradas", ""]
    for r in hechos:
        t = str(r.get("Afirmación") or "")
        if str(r.get("Qué es") or "").lower().startswith("demostr") and re.search(r"\d", t):
            lin.append(f"- {r.get('ID')}: {t[:160]}")
    lin += ["", "## Planos del reportaje (se citan en guion.json con {\"de\": n})", "",
            "| n | min | tipo | fuente | s | qué se ve | lo que dice la voz |", "|---|---|---|---|---|---|---|"]
    planos = []
    for i, p in enumerate(d.get("planos", []), 1):
        ini, dur = float(p.get("ini", 0)), float(p.get("dur", 0))
        dice = " ".join(t for b0, b1, t in tiempos if b0 < ini + dur and b1 > ini)[:110]
        src = p.get("clip") or p.get("img") or p.get("key") or ""
        tipo = p.get("tipo", "")
        marca = " (explicativa)" if p.get("explicativa") else ""
        planos.append({"n": i, "ini": ini, "dur": dur, "tipo": tipo, "src": src, "txt": p.get("txt", ""), "explicativa": bool(p.get("explicativa"))})
        if tipo in ("V", "F", "D", "A", "N"):
            lin.append(f"| {i} | {mmss(ini)} | {tipo}{marca} | {src} | {dur:.1f} | {str(p.get('txt', ''))[:60]} | {dice} |")
    lin += ["", "## Música del reportaje", ""] + [f"- {u.get('src')} ({mmss(u.get('ini', 0))})" for u in d.get("musica", [])]
    lin += ["", "Música nueva para el Short: solo del maestro de audio de la skill del reportaje (`audio/musica/<uso>/`)."]
    os.makedirs(os.path.join(c, "shorts"), exist_ok=True)
    open(os.path.join(c, "shorts", "inventario.md"), "w", encoding="utf-8").write("\n".join(lin) + "\n")
    json.dump({"planos": planos, "titulo": est.get("titulo"), "pregunta": hilo.get("pregunta")}, open(os.path.join(c, "shorts", "inventario.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    log(f"Inventario: {os.path.join(c, 'shorts', 'inventario.md')} ({len(planos)} planos, {len(pistas)} giros)")


# ------------------------------------------------------------------ voz

def frases_guion(g):
    """(código, texto) de la voz del Short: una frase por beat y la pregunta final."""
    out = [(str(101 + i), b["voz"].strip()) for i, b in enumerate(g["beats"]) if b.get("voz", "").strip()]
    if g.get("pregunta_voz"):
        out.append(("199", g["pregunta_voz"].strip()))
    return out


def cmd_voz(a):
    c, ds = carpeta(a), dir_short(a)
    g = leer_guion(a)
    lin = [f"{n}. {t}" for n, t in frases_guion(g)]
    open(os.path.join(ds, "m1_voz.md"), "w", encoding="utf-8").write("\n".join(lin) + "\n")
    for f in ("pronunciacion.txt",):
        if os.path.exists(os.path.join(c, f)) and not os.path.exists(os.path.join(ds, f)):
            shutil.copy(os.path.join(c, f), os.path.join(ds, f))
    cmd = [sys.executable, os.path.join(REP, "scripts", "voz_fish.py"), a.s, "--raiz", os.path.join(c, "shorts")]
    if a.presupuesto or not a.modelo:
        cmd.append("--presupuesto")
    else:
        cmd += ["--modelo", a.modelo] + (["--rehacer", a.rehacer] if a.rehacer else []) + (["--autoriza", a.autoriza] if a.autoriza else [])
    r = subprocess.run(cmd)
    if r.returncode or a.presupuesto or not a.modelo:
        return
    # tomas limpias: sin silencio en los extremos y un poco más rápidas
    dst = os.path.join(c, "remotion", "public", "m", "shorts", a.s, "voz")
    os.makedirs(dst, exist_ok=True)
    durs = {}
    for n, _ in frases_guion(g):
        src = os.path.join(ds, "voz_fish", f"{n}.mp3")
        out = os.path.join(dst, f"{n}.mp3")
        filtro = ("silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.02,areverse,"
                  "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.05,areverse," f"atempo={VELOCIDAD}")
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", src, "-af", filtro, "-ar", "44100", "-b:a", "192k", out], check=True)
        durs[n] = round(ffprobe_dur(out), 3)
    json.dump({"modelo": a.modelo, "durs": durs}, open(os.path.join(ds, "voz.json"), "w"), indent=1)
    log(f"Voz lista: {len(durs)} tomas, {sum(durs.values()):.1f} s a {VELOCIDAD}x. Siguiente: short.py montar {a.id} {a.s}")


# ------------------------------------------------------------------ montaje

def plano_de(ref, planos_m1, c=None):
    """Un plano del Short a partir de {"de": n} (plano n del reportaje) o escrito a mano."""
    p = dict(ref)
    if "de" in p:
        o = planos_m1[int(p.pop("de")) - 1]
        t = o.get("tipo")
        base = {"tipo": "A" if t in ("A", "N") else t}
        for k in ("clip", "img", "key", "brillo"):
            if o.get(k) is not None:
                base[k] = o[k]
        if base["tipo"] == "A":
            base["total"] = float(o.get("total") or o.get("dur"))
            base.setdefault("desde", float(o.get("desde") or 0))
        if o.get("explicativa"):
            base["explicativa"] = True
        base.update(p)
        p = base
    if c and p.get("tipo") in ("V", "F") and "encaje" not in p and not p.get("foco"):
        # archivo de baja resolución: recortado en vertical se amplía unas 3 veces y se pixela; mejor enmarcado
        alto = 0
        if p["tipo"] == "V" and p.get("clip"):
            f = os.path.join(c, "remotion", "public", "m", "clips", p["clip"])
            if os.path.exists(f):
                r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=height", "-of", "csv=p=0", f], capture_output=True, text=True)
                alto = int((r.stdout.strip() or "0").split(",")[0] or 0)
        elif p.get("img"):
            f = os.path.join(c, "remotion", "public", "m", "fotos", p["img"])
            if os.path.exists(f):
                from PIL import Image
                alto = Image.open(f).size[1]
        if 0 < alto < (720 if p["tipo"] == "V" else 1200):
            p["encaje"] = "marco"
    if p.get("tipo") == "A" and "encaje" not in p:
        # una pieza tiene su propio texto (títulos, cifras): recortada lo pierde. Se recorta solo si se pide foco.
        p["encaje"] = "recorte" if p.get("foco") else "marco"
    return p


def copia_audio(rel, c, s, sub):
    """Copia una pista o un efecto del maestro de audio a public/m/shorts/<S>/<sub>/ y devuelve la ruta para Remotion."""
    src = rel if os.path.isabs(rel) else os.path.join(AUDIO, rel)
    if not os.path.exists(src):
        sys.exit(f"No encuentro {rel} en el maestro de audio ({AUDIO}).")
    dst_dir = os.path.join(c, "remotion", "public", "m", "shorts", s, sub)
    os.makedirs(dst_dir, exist_ok=True)
    nombre = re.sub(r"[^A-Za-z0-9_.-]+", "_", os.path.basename(src))
    if not os.path.exists(os.path.join(dst_dir, nombre)):
        shutil.copy(src, os.path.join(dst_dir, nombre))
    return f"shorts/{s}/{sub}/{nombre}"


def efecto(uso, c, s, i=0):
    fs = sorted(glob.glob(os.path.join(glob.escape(AUDIO), "efectos", uso, "*.*")))
    fs = [f for f in fs if not f.lower().endswith(".md")]
    if not fs:
        return None
    return copia_audio(fs[i % len(fs)], c, s, "sfx")


def cmd_montar(a):
    c, ds = carpeta(a), dir_short(a)
    g = leer_guion(a)
    vz = os.path.join(ds, "voz.json")
    if not os.path.exists(vz):
        sys.exit("Falta la voz (short.py voz ... --modelo ...).")
    durs = json.load(open(vz))["durs"]
    d = m1(c)
    planos_m1 = d.get("planos", [])
    t = ARRANQUE
    planos, textos, voz, sfx = [], [], [], []
    golpe = efecto("impactos", c, a.s, 0)
    if golpe:
        sfx.append({"t": 0, "src": golpe, "vol": 0.7})
    qz = g.get("quiz")
    quiz = None
    for i, b in enumerate(g["beats"]):
        n = str(101 + i)
        if qz and i == len(g["beats"]) - 1:
            quiz = {"ini": round(t, 3), "pregunta": qz.get("pregunta", ""), "opciones": qz.get("opciones", [])}
        dur = durs.get(n, 1.2) if b.get("voz") else float(b.get("dur", 1.0))
        if b.get("voz"):
            voz.append({"src": f"shorts/{a.s}/voz/{n}.mp3", "ini": round(t, 3), "dur": dur})
        t0 = 0 if i == 0 else t     # imagen y texto desde el fotograma 0; la voz arranca en el 1-2
        rots = b.get("rot", "")
        rots = rots if isinstance(rots, list) else [rots]
        if quiz and i == len(g["beats"]) - 1:
            rots = []   # en el beat de las opciones, en pantalla solo el quiz
        tramo = (dur + PAUSA + (t - t0)) / max(len(rots), 1)   # una frase larga cambia de rótulo a mitad (el deslizador lo pidió en L07)
        for j, r in enumerate(rots):
            textos.append({"ini": round(t0 + j * tramo, 3), "dur": round(tramo, 3), "rot": r, **({"ya": True} if i == 0 and j == 0 else {})})
        ps = [plano_de(x, planos_m1, c) for x in b.get("planos", [])]
        if not ps:
            # sin planos nuevos, sigue el anterior (alargado, no repetido desde su inicio)
            if planos:
                planos[-1]["dur"] = round(t + dur + PAUSA - planos[-1]["ini"], 3)
            t += dur + PAUSA
            continue
        reparto = [float(x.get("dur")) for x in ps if x.get("dur")]
        libres = [x for x in ps if not x.get("dur")]
        resto = max(0.4, dur + PAUSA + (t - t0) - sum(reparto))
        u = t0
        if rots and any(x.get("encaje") == "marco" for x in ps):
            textos[-1]["arriba"] = True
        for x in ps:
            dx = float(x["dur"]) if x.get("dur") else resto / max(len(libres), 1)
            x = {k: v for k, v in x.items() if k != "dur"}
            planos.append({**x, "ini": round(u, 3), "dur": round(dx, 3)})
            u += dx
        if b.get("sfx"):
            e = efecto(b["sfx"], c, a.s, i)
            if e:
                sfx.append({"t": round(t, 3), "src": e, "vol": 0.55})
        t += dur + PAUSA
    if quiz:
        cuenta = int(qz.get("cuenta", 3))
        quiz["cuenta"] = round(t, 3)
        tic = efecto("documentos", c, a.s, 12)
        for k in range(cuenta):
            if tic:
                sfx.append({"t": round(t + k, 3), "src": tic, "vol": 0.8, "dur": 0.6})
        if planos:
            planos[-1]["dur"] = round(t + cuenta - planos[-1]["ini"], 3)
        t += cuenta
        quiz["fin"] = round(t, 3)
    final = None
    if g.get("pregunta"):
        n = "199"
        dv = durs.get(n, 1.8)
        if g.get("pregunta_voz"):
            voz.append({"src": f"shorts/{a.s}/voz/{n}.mp3", "ini": round(t, 3), "dur": dv})
        final = {"ini": round(t, 3), "pregunta": g["pregunta"], "cta": g.get("cta", "El caso completo, en el canal"), "like": g.get("like")}
        cola = max(dv + 0.5, 2.2)
        # el último plano sigue debajo de la pregunta
        if planos:
            planos[-1]["dur"] = round(t + cola - planos[-1]["ini"], 3)
        e = efecto("impactos", c, a.s, 1)
        if e:
            sfx.append({"t": round(t, 3), "src": e, "vol": 0.6})
        t += cola
    musica = None
    if g.get("musica"):
        musica = {"src": copia_audio(g["musica"]["src"], c, a.s, "musica"), "desde": g["musica"].get("desde", 0), "vol": g["musica"].get("vol", 0.42)}
    datos = {"dur": round(t, 3), "planos": planos, "textos": textos, "voz": voz, "musica": musica, "sfx": sfx, "final": final, "quiz": quiz}
    json.dump(datos, open(os.path.join(ds, "short.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    pedida = float(g.get("dur", 0))
    log(f"short.json: {t:.1f} s (pedida {pedida:.0f} s), {len(planos)} planos, {len(voz)} tomas de voz.")
    if pedida and abs(t - pedida) > max(1.0, 0.1 * pedida):
        log(f"OJO: se aleja de la duración pedida. Ajusta el TEXTO del guion (quita o añade frases), no la velocidad.")


# ------------------------------------------------------------------ render

def sincroniza(c):
    rem = os.path.join(c, "remotion")
    pl = os.path.join(SKILL, "plantilla")
    for f, dst in (("ShortPromo.tsx", "src"), ("ShortsRoot.tsx", "src"), ("render_short.mjs", "")):
        shutil.copy(os.path.join(pl, f), os.path.join(rem, dst, f))


def nivelar(src, dst):
    """Dos pasadas de loudnorm: -14 LUFS y pico -1,5 dBTP (estilo.md, «Short promocional»)."""
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", src, "-af", "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    j = json.loads(r.stderr[r.stderr.rfind("{"):r.stderr.rfind("}") + 1])
    af = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}:"
          f"measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", src, "-c:v", "copy", "-af", af, "-ar", "48000", "-c:a", "aac", "-b:a", "192k", dst], check=True)


def cmd_render(a):
    c, ds = carpeta(a), dir_short(a)
    if not os.path.exists(os.path.join(ds, "short.json")):
        sys.exit("Falta short.json (short.py montar).")
    sincroniza(c)
    rel = os.path.relpath(os.path.join(ds, "short.json"), c).replace("\\", "/")
    node = ["node", os.path.join(c, "remotion", "render_short.mjs"), "--datos", rel]
    if a.stills:
        d = json.load(open(os.path.join(ds, "short.json"), encoding="utf-8"))
        ts = [0, 0.5, 1.0, 1.5, 2.0, 3.0] + [round(x, 2) for x in frange(4, d["dur"], 2.5)] + [round(d["dur"] - 0.3, 2)]
        subprocess.run(node + ["--stills", ",".join(map(str, ts)), "--dir", os.path.relpath(os.path.join(ds, "_fot"), c).replace("\\", "/")], cwd=c, check=True)
        return
    crudo = os.path.join(ds, "_crudo.mp4")
    subprocess.run(node + ["--salida", os.path.relpath(crudo, c).replace("\\", "/")], cwd=c, check=True)
    final = os.path.join(ds, f"{a.id}_{a.s}.mp4")
    nivelar(crudo, final)
    log(f"Short: {final} ({ffprobe_dur(final):.1f} s)")


def frange(a, b, p):
    x = a
    while x < b:
        yield x
        x += p


# ------------------------------------------------------------------ controles (puertas S1-S9)

class Sem:
    def __init__(self):
        self.filas = []

    def __call__(self, r, e, t):
        self.filas.append((r, e, t))

    def fallos(self):
        return [f for f in self.filas if f[1] == "FALLO"]


NOMBRES = {"S1": "gancho", "S2": "ritmo", "S3": "duración y voz", "S4": "texto legible", "S5": "interacción", "S6": "sin destripar",
           "S7": "bucle", "S8": "técnica", "S9": "ángulos distintos", "S10": "sin conocer el caso"}


def palabras(t):
    return re.findall(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9]+", t or "")


def reglas_papel(a, s, g, c):
    beats = g.get("beats", [])
    if not beats:
        s("S1", "FALLO", "el guion no tiene beats")
        return
    primera = beats[0].get("voz", "")
    s("S1", "OK" if len(palabras(primera)) <= 12 else "AVISO", f"primera frase: «{primera}» ({len(palabras(primera))} palabras; la primera imagen y la primera frase lo deciden todo)")
    if not beats[0].get("planos"):
        s("S1", "FALLO", "el primer beat no tiene plano: el fotograma 0 tiene que tener imagen en movimiento")
    # presupuesto de palabras para la duración pedida
    total = sum(len(palabras(b.get("voz", ""))) for b in beats) + len(palabras(g.get("pregunta_voz", "")))
    dur = float(g.get("dur") or 0)
    if dur:
        lo, hi = (dur - 2.5) * 2.75, (dur - 1) * 3.0   # medido en L07: 2,9 palabras/s a 1,08x, más la cola de la pregunta
        s("S3", "OK" if lo <= total <= hi else "AVISO", f"{total} palabras para {dur:.0f} s (cabe entre {lo:.0f} y {hi:.0f} a la velocidad de los Shorts)")
    else:
        s("S3", "FALLO", "guion.json sin «dur» (la duración la pide Antonio)")
    rot_txt = lambda b: " ".join(b.get("rot")) if isinstance(b.get("rot"), list) else b.get("rot", "")
    largos = [r for b in beats for r in (b.get("rot") if isinstance(b.get("rot"), list) else [b.get("rot", "")]) if len(palabras(r.replace("|", " "))) > PALABRAS_PANTALLA]
    clavados = [rot_txt(b)[:30] for i, b in enumerate(beats) if not isinstance(b.get("rot"), list) and len(palabras(b.get("voz", ""))) > 11
                and not (g.get("quiz") and i == len(beats) - 1)]
    if clavados:
        s("S4", "AVISO", "frases de más de 11 palabras con un solo rótulo (se queda clavado; pon \"rot\" como lista de dos): " + "; ".join(clavados))
    if len(palabras(g.get("pregunta_voz", ""))) > 9:
        s("S5", "AVISO", f"la pregunta en voz tiene {len(palabras(g['pregunta_voz']))} palabras: alarga la tarjeta final (mejor 9 o menos, p. ej. «¿Y tú qué crees? Te leo abajo.»)")
    es_quiz = bool(g.get("quiz"))
    sin = [i + 1 for i, b in enumerate(beats) if b.get("voz") and not b.get("rot") and not (es_quiz and i == len(beats) - 1)]
    s("S4", "FALLO" if sin else "AVISO" if largos else "OK", f"rótulos: {len(beats)}" + (f" · beats con voz y sin texto en pantalla: {sin}" if sin else "")
      + (f" · de más de {PALABRAS_PANTALLA} palabras: " + "; ".join(x[:40] for x in largos) if largos else ""))
    preg = g.get("pregunta", "")
    qz = g.get("quiz")
    if g.get("angulo") == "quiz" or qz:
        ops = (qz or {}).get("opciones", [])
        cor = (qz or {}).get("correcta")
        prob = []
        if not 3 <= len(ops) <= 4:
            prob.append(f"{len(ops)} opciones (tienen que ser 3, como mucho 4)")
        if not isinstance(cor, int) or not 0 <= cor < len(ops):
            prob.append("falta «correcta» (índice de la opción buena; solo para el control)")
        if "reportaje" not in (g.get("cta", "") + g.get("comentario_fijado", "")).lower():
            prob.append("la llamada no dice que la respuesta está en el reportaje")
        largas = [o for o in ops if len(palabras(o)) > 4]
        s("S5", "FALLO" if prob else "AVISO" if largas else "OK", "quiz: " + ("; ".join(prob) if prob else f"{len(ops)} opciones")
          + (f" · opciones de más de 4 palabras: {'; '.join(largas)}" if largas else ""))
        if isinstance(cor, int) and 0 <= cor < len(ops):
            # todo lo que se ve o se oye fuera del beat que lee las opciones, más título, descripción y comentario fijado
            fuera = " ".join([b.get("voz", "") + " " + (" ".join(b["rot"]) if isinstance(b.get("rot"), list) else b.get("rot", "")) for b in beats[:-1]]
                             + [g.get("titulo", ""), g.get("descripcion", ""), g.get("comentario_fijado", ""), preg, g.get("pregunta_voz", "")])
            buena = control_hilo.claves(ops[cor]) - set().union(*[control_hilo.claves(o) for j, o in enumerate(ops) if j != cor])
            escapa = buena & control_hilo.claves(fuera)
            s("S6", "FALLO" if len(escapa) >= 2 or (buena and escapa == buena) else "OK",
              "quiz: la respuesta " + (f"se escapa fuera de las opciones ({', '.join(sorted(escapa))})" if len(escapa) >= 2 or (buena and escapa == buena) else "no aparece fuera de las opciones"))
    if g.get("bucle") and not preg:
        # en bucle la pregunta final cortaría la repetición: basta el comentario fijado
        s("S5", "OK" if g.get("comentario_fijado") else "FALLO", "interacción en bucle: sin pregunta final, con comentario fijado" if g.get("comentario_fijado") else "falta el comentario fijado")
    else:
        falta = [k for k in ("pregunta", "pregunta_voz", "comentario_fijado", "cta") if not g.get(k)]
        binaria = bool(re.search(r"\bo\b|¿", preg.replace("*", "").replace("|", " "), re.I))
        s("S5", "FALLO" if falta else "AVISO" if not binaria else "OK", "interacción" + (f" · falta: {', '.join(falta)}" if falta else "")
          + ("" if binaria else " · la pregunta final no es fácil de contestar (mejor «A o B»)"))
    # spoilers: lo que se guarda el reportaje no puede sonar en el Short
    _, hojas = excel(c)
    guarda = [str(r.get("Qué se guarda") or "") for r in (hoja(hojas, "Pistas") or [])]
    hilo = control_hilo.leer_hilo(hojas) or {}
    if hilo.get("actos", {}).get(4):
        guarda.append(hilo["actos"][4])
    texto = " ".join([b.get("voz", "") + " " + rot_txt(b) for b in beats] + [preg])
    claves_t = control_hilo.claves(texto)
    sosp = [x[:70] for x in guarda if len(control_hilo.claves(x) & claves_t) >= 3]
    s("S6", "AVISO" if sosp else "OK", "spoilers: " + ("el Short comparte palabras con lo que el reportaje se guarda, compruébalo: " + " / ".join(sosp[:3]) if sosp else "no repite lo que el reportaje se guarda"))
    if g.get("bucle"):
        s("S7", "OK", "pensado en bucle: la última frase enlaza con la primera")
    m = (g.get("musica") or {}).get("src", "")
    s("S8", "OK" if m and os.path.exists(os.path.join(AUDIO, m)) else "FALLO", f"música: {m or 'ninguna'}" + ("" if m and os.path.exists(os.path.join(AUDIO, m)) else " (solo del maestro de audio: audio/musica/<uso>/...)"))
    titulo = g.get("titulo", "")
    s("S5", "OK" if titulo and len(titulo) <= 60 else "AVISO", f"título: «{titulo}» ({len(titulo)} caracteres)")


def reglas_montaje(a, s, c, ds, g):
    d = json.load(open(os.path.join(ds, "short.json"), encoding="utf-8"))
    pl = d["planos"]
    v0 = d["voz"][0]["ini"] if d["voz"] else 9
    cambio1 = pl[1]["ini"] if len(pl) > 1 else d["dur"]
    s("S1", "OK" if v0 <= 0.3 and cambio1 <= 1.6 else "FALLO", f"la voz arranca en {v0:.2f} s y el primer cambio de plano llega en {cambio1:.2f} s (≤0,3 y ≤1,6)")
    largos = [p for p in pl[:-1] if p["dur"] > (PLANO_MAX_EXPLIC if p.get("explicativa") else PLANO_MAX)]
    cpm = len(pl) / max(d["dur"], 1) * 60
    s("S2", "FALLO" if largos else "OK", f"{len(pl)} planos ({cpm:.0f} por minuto)" + "".join(f"\n    - {p['ini']:.1f} s · {p['dur']:.1f} s · {p.get('clip') or p.get('key') or p.get('img')}" for p in largos))
    # un clip que se acaba antes que su plano se congela en el último fotograma
    cortos = []
    for p in pl:
        if p.get("tipo") == "V" and p.get("clip"):
            f = os.path.join(c, "remotion", "public", "m", "clips", p["clip"])
            if os.path.exists(f) and (p.get("desde") or 0) + p["dur"] * (p.get("vel") or 1) > ffprobe_dur(f) + 0.05:
                cortos.append(f"{p['ini']:.1f} s · {p['clip']} dura {ffprobe_dur(f):.1f} s y el plano pide {(p.get('desde') or 0) + p['dur'] * (p.get('vel') or 1):.1f}")
    if cortos:
        s("S2", "FALLO", "clips que se acaban antes que su plano (se congelan): " + "; ".join(cortos) + " · usa \"vel\" < 1, otro clip o un plano más")
    pedida = float(g.get("dur") or 0)
    hablado = sum(v["dur"] for v in d["voz"])
    pps = sum(len(palabras(b.get("voz", ""))) for b in g["beats"]) / max(hablado, 0.1)
    fuera = pedida and abs(d["dur"] - pedida) > max(1.5, 0.15 * pedida)
    s("S3", "FALLO" if fuera else "AVISO" if not PPS[0] <= pps <= PPS[1] else "OK", f"{d['dur']:.1f} s (pedida {pedida:.0f}) · {pps:.1f} palabras por segundo")
    if g.get("bucle") and pl:
        s("S7", "OK" if (pl[0].get("clip") or pl[0].get("key")) == (pl[-1].get("clip") or pl[-1].get("key")) else "AVISO", "bucle: el último plano " + ("es el primero" if (pl[0].get("clip") or pl[0].get("key")) == (pl[-1].get("clip") or pl[-1].get("key")) else "no es el primero: el salto se nota al repetirse"))


def medir(video):
    """Resolución, sonoridad y tramos quietos del vídeo final."""
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "csv=p=0", video], capture_output=True, text=True)
    w, h = [int(x) for x in r.stdout.strip().split(",")[:2]]
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", video, "-af", "loudnorm=I=-14:TP=-1.5:print_format=json", "-f", "null", "-"], capture_output=True, text=True, encoding="utf-8", errors="replace")
    j = json.loads(r.stderr[r.stderr.rfind("{"):r.stderr.rfind("}") + 1])
    import numpy as np
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", video, "-vf", "fps=10,scale=54:96,format=gray", "-f", "rawvideo", "-"], capture_output=True).stdout
    fr_ = np.frombuffer(raw, np.uint8).reshape(-1, 96, 54).astype(np.float32) / 255
    cambia = (np.abs(np.diff(fr_, axis=0)) > 0.05).mean(axis=(1, 2)) if len(fr_) > 1 else np.zeros(0)
    quietos, ini = [], None
    for i, x in enumerate(cambia):
        if x < 0.002:
            ini = i if ini is None else ini
        else:
            if ini is not None and (i - ini) / 10 >= 1.2:
                quietos.append((ini / 10, i / 10))
            ini = None
    if ini is not None and (len(cambia) - ini) / 10 >= 1.2:
        quietos.append((ini / 10, len(cambia) / 10))
    return w, h, float(j["input_i"]), float(j["input_tp"]), quietos


def reglas_video(a, s, ds):
    v = os.path.join(ds, f"{a.id}_{a.s}.mp4")
    if not os.path.exists(v):
        s("S8", "FALLO", "no hay vídeo renderizado (short.py render)")
        return
    w, h, lufs, tp, quietos = medir(v)
    s("S8", "OK" if (w, h) == (1080, 1920) and abs(lufs + 14) <= 1 and tp <= -1.0 else "FALLO", f"{w}x{h} · {lufs:.1f} LUFS · pico {tp:.1f} dBTP (1080x1920, -14 ±1, pico ≤ -1)")
    s("S2", "FALLO" if quietos else "OK", f"tramos quietos de 1,2 s o más: {len(quietos)}" + "".join(f"\n    - {x:.1f}-{y:.1f} s" for x, y in quietos[:8]))


def reglas_angulos(a, s, c):
    """Los Shorts del mismo reportaje no se repiten: ni gancho ni planos."""
    otros = {}
    for p in sorted(glob.glob(os.path.join(glob.escape(c), "shorts", "S*", "guion.json"))):
        otros[os.path.basename(os.path.dirname(p))] = json.load(open(p, encoding="utf-8"))
    if len(otros) < 2:
        return
    usa = lambda g: {json.dumps(x.get("de") or x.get("clip") or x.get("key") or x.get("img")) for b in g["beats"] for x in b.get("planos", [])}
    yo = otros.get(a.s)
    if not yo:
        return
    for k, g in otros.items():
        if k == a.s:
            continue
        comun = usa(yo) & usa(g)
        mismo_gancho = (yo["beats"][0].get("planos") or [{}])[0] == (g["beats"][0].get("planos") or [{}])[0]
        if mismo_gancho or g.get("angulo") == yo.get("angulo"):
            s("S9", "FALLO", f"con {k}: {'mismo plano de gancho' if mismo_gancho else 'mismo ángulo'}")
        elif len(comun) > 0.25 * max(len(usa(yo)), 1):
            s("S9", "AVISO", f"con {k}: comparten {len(comun)} planos de {len(usa(yo))}")
        else:
            s("S9", "OK", f"con {k}: ángulo y gancho distintos, {len(comun)} planos en común")


def leer_juez(p):
    if not os.path.exists(p):
        return None
    t = open(p, encoding="utf-8").read()
    g = lambda pat: (re.search(pat, t, re.I | re.M) or [None, ""])[1].strip().lower()
    return {"desliza1": g(r"^Deslizo en el segundo 1:\s*(s[ií]|no)"), "desliza3": g(r"^Deslizo antes del segundo 3:\s*(s[ií]|no)"),
            "final": g(r"^Me quedo hasta el final:\s*(s[ií]|no)"), "sabe": g(r"^Siento que ya s[ée] c[óo]mo acaba:\s*(s[ií]|no)"),
            "largo": g(r"^Me dan ganas de ver el reportaje completo:\s*(s[ií]|no)"), "comenta": g(r"^Comentar[íi]a:\s*(.+)"),
            "like": g(r"^Le dar[íi]a like:\s*(s[ií]|no)"), "otra": g(r"^Lo ver[íi]a otra vez:\s*(s[ií]|no)"),
            "veredicto": g(r"^Veredicto:\s*(.+)"), "perdido": g(r"^Me he perdido:\s*(s[ií]|no)"), "quiz": g(r"^El Short me da la respuesta del quiz:\s*(s[ií]|no)"), "texto": t}


def reglas_juez(a, s, ds, tipo):
    for nombre in (f"juez_{tipo}.md", f"juez_{tipo}_2.md"):
        e = leer_juez(os.path.join(ds, nombre))
        tag = "1.º" if not nombre.endswith("_2.md") else "2.º"
        if e is None:
            s("S1", "AVISO" if tag == "2.º" else "FALLO", f"falta {nombre} (short.py juez {a.id} {a.s} {tipo} y un subagente nuevo)")
            continue
        si = lambda k: e[k].startswith("s")
        prob, avis = [], []
        if si("desliza1") or si("desliza3"):
            prob.append("desliza en los primeros segundos")
        if e["final"] and not si("final"):
            prob.append("no llega al final")
        if si("sabe"):
            prob.append("siente que ya sabe cómo acaba (destripa el reportaje)")
        if si("quiz"):
            prob.append("el Short le da la respuesta del quiz")
        if si("perdido"):
            prob.append("se pierde: no conoce el caso y algo no se explica")
        if e["largo"] and not si("largo"):
            prob.append("no le dan ganas de ver el reportaje")
        if not e["comenta"] or re.match(r"(nada|no coment)", e["comenta"]):
            prob.append("no comentaría nada")
        if e["like"] and not si("like"):
            avis.append("no daría like")
        if e["otra"] and not si("otra"):
            avis.append("no lo vería otra vez")
        if not e["veredicto"].startswith("funciona"):
            prob.append(f"veredicto: {e['veredicto'] or 'sin veredicto'}")
        r = "S1" if "desliza" in " ".join(prob) else "S10" if "se pierde" in " ".join(prob) else "S6" if ("sabe" in " ".join(prob) or "respuesta del quiz" in " ".join(prob)) else "S5"
        s(r, "FALLO" if prob else "AVISO" if avis else "OK", f"deslizador {tipo} ({tag}): " + ("; ".join(prob + avis) or f"se queda, comentaría «{e['comenta'][:60]}»"))


def cmd_control(a):
    c, ds = carpeta(a), dir_short(a)
    g = leer_guion(a)
    s = Sem()
    reglas_papel(a, s, g, c)
    reglas_angulos(a, s, c)
    if a.papel:
        reglas_juez(a, s, ds, "papel")
    else:
        if not os.path.exists(os.path.join(ds, "short.json")):
            sys.exit("Falta short.json: para el control del vídeo, antes montar y render. Para el guion: --papel.")
        reglas_montaje(a, s, c, ds, g)
        reglas_video(a, s, ds)
        reglas_juez(a, s, ds, "video")
    icono = {"OK": "🟢", "AVISO": "🟡", "FALLO": "🔴"}
    lin = [f"# Control · {a.id} · {a.s} · {'guion' if a.papel else 'vídeo'}", ""]
    lin += [f"- {icono[e]} **{r} {NOMBRES[r]}** {e}: {t}" for r, e, t in sorted(s.filas, key=lambda x: int(x[0][1:]))]
    lin += ["", "**NO SE PUEDE ENTREGAR**" if s.fallos() else "**Puertas superadas**"]
    txt = "\n".join(lin) + "\n"
    open(os.path.join(ds, f"control_{'papel' if a.papel else 'video'}.md"), "w", encoding="utf-8").write(txt)
    print(txt)
    sys.exit(1 if s.fallos() else 0)


# ------------------------------------------------------------------ juez a ciegas

NO_AMABLE = ("No eres amable: eres alguien deslizando Shorts con el pulgar ya encima de la pantalla. Un juicio blando hace "
             "que el Short fracase y nadie te pedirá explicaciones por ser duro.")
FORMULARIO = """Contesta EXACTAMENTE con este formato (lo lee un programa; no añadas nada fuera de él):

## Primer segundo
Lo que veo y oigo: <una frase>
Deslizo en el segundo 1: sí|no · <por qué>
Deslizo antes del segundo 3: sí|no · <por qué>

## Hasta el final
Me quedo hasta el final: sí|no · <si no, en qué segundo me voy y por qué>
Peor momento: <segundo> · <por qué>

## Al terminar
Qué he entendido: <una frase>
Me he perdido: sí|no · <qué nombre, lugar, sigla o cosa no sé qué es, o en qué momento ya no sé de qué va>
Siento que ya sé cómo acaba: sí|no · <la historia completa, no este Short>
Me dan ganas de ver el reportaje completo: sí|no
Comentaría: <lo que escribiría en los comentarios, palabra por palabra, o «nada»>
Le daría like: sí|no
Lo vería otra vez: sí|no
El Short me da la respuesta del quiz: sí|no|no hay quiz

Veredicto: funciona|no funciona
"""


def cmd_juez(a):
    c, ds = carpeta(a), dir_short(a)
    g = leer_guion(a)
    out = os.path.join(ds, "_juez")
    os.makedirs(out, exist_ok=True)
    cuerpo = f"# Encargo: el deslizador ({'guion' if a.tipo == 'papel' else 'Short montado'})\n\n{NO_AMABLE}\n\n"
    cuerpo += ("No conoces este caso: es la primera vez que oyes hablar de él y no sabes quién es nadie ni dónde pasa. "
               "Si un nombre, una sigla o un sitio no te dicen nada, dilo.\n\n")
    if a.tipo == "papel":
        cuerpo += ("Abajo está un Short de YouTube de unos " + str(g.get("dur")) + " s, escrito: qué se ve y qué se oye en cada momento. "
                   "Imagínalo en el móvil, a pantalla completa, entre otros cien. Léelo una sola vez.\n\n" + FORMULARIO + "\n---\n\n## El Short\n\n")
        t = 0.0
        for b in g["beats"]:
            vista = "; ".join(x.get("ves") or x.get("txt") or "" for x in b.get("planos", []))
            rt = " / ".join(b["rot"]) if isinstance(b.get("rot"), list) else b.get("rot", "")
            cuerpo += f"- [{t:.1f} s] se ve: {vista or '(sigue la imagen anterior)'} · en pantalla: «{rt.replace('|', ' ').replace('*', '')}» · voz: «{b.get('voz', '')}»\n"
            t += len(palabras(b.get("voz", ""))) / 2.8 + PAUSA
        if g.get("quiz"):
            q = g["quiz"]
            cuerpo += (f"- [{t:.1f} s] en pantalla: la pregunta «{q.get('pregunta', '').replace('|', ' ').replace('*', '')}» y las opciones "
                       + " ".join(f"{'ABCD'[i]}) {o}" for i, o in enumerate(q.get("opciones", []))) + f"; cuenta atrás de {q.get('cuenta', 3)} s con un tic por segundo\n")
            t += q.get("cuenta", 3)
        cuerpo += f"- [{t:.1f} s] en pantalla: «{g.get('pregunta', '').replace('|', ' ').replace('*', '')}» y «{g.get('cta', '')}» · voz: «{g.get('pregunta_voz', '')}»\n"
        cuerpo += f"\nTítulo del Short: {g.get('titulo', '')}\n"
    else:
        v = os.path.join(ds, f"{a.id}_{a.s}.mp4")
        if not os.path.exists(v):
            sys.exit("Falta el vídeo (short.py render).")
        from PIL import Image, ImageDraw
        dur = ffprobe_dur(v)
        def rejilla(ts, nombre, cols):
            ims = []
            for t in ts:
                raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.2f}", "-i", v, "-frames:v", "1", "-vf", "scale=216:384", "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True).stdout
                im = Image.open(__import__("io").BytesIO(raw)).convert("RGB")
                ImageDraw.Draw(im).text((6, 6), f"{t:.2f} s", fill=(255, 255, 0))
                ims.append(im)
            filas = (len(ims) + cols - 1) // cols
            hoja_ = Image.new("RGB", (cols * 216, filas * 384), (0, 0, 0))
            for i, im in enumerate(ims):
                hoja_.paste(im, ((i % cols) * 216, (i // cols) * 384))
            hoja_.save(os.path.join(out, nombre), quality=85)
        rejilla([x * 0.25 for x in range(12)], "primeros_3s.jpg", 6)
        rejilla(list(frange(0, dur, 1.0)), "todo.jpg", 8)
        d = json.load(open(os.path.join(ds, "short.json"), encoding="utf-8"))
        textos = json.load(open(os.path.join(ds, "voz.json")))
        voz = {str(101 + i): b.get("voz", "") for i, b in enumerate(g["beats"])}
        voz["199"] = g.get("pregunta_voz", "")
        cuerpo += ("Tienes un Short de YouTube montado, de " + f"{dur:.1f}" + " s: `primeros_3s.jpg` (un fotograma cada 0,25 s de los 3 "
                   "primeros segundos) y `todo.jpg` (uno por segundo), más lo que dice la voz y cuándo. Imagínalo en el móvil entre otros "
                   "cien, con sonido.\n\n" + FORMULARIO + "\n---\n\n## La voz\n\n")
        for x in d["voz"]:
            n = os.path.basename(x["src"])[:-4]
            cuerpo += f"- [{x['ini']:.1f} s] «{voz.get(n, '')}»\n"
        cuerpo += f"\nTítulo del Short: {g.get('titulo', '')}\n"
    salida = f"juez_{a.tipo}.md"
    previas = [x for x in (salida, salida.replace(".md", "_2.md")) if os.path.exists(os.path.join(ds, x))]
    if a.verificar and previas:
        for x in previas:
            pv = os.path.join(out, x.replace("juez_", "verifica_"))
            open(pv, "w", encoding="utf-8").write(
                "# Verificación: segunda ronda del mismo juicio\n\nEste Short ya se juzgó con el encargo de abajo; tu respuesta anterior "
                "está al final. Desde entonces se ha corregido. Rellena el mismo formulario partiendo de ella: cambia lo que ahora esté "
                "bien, deja lo que siga mal y no añadas pegas nuevas salvo que sean graves (deslizaría, me voy antes del final, destripa "
                "el caso).\n\n" + cuerpo + "\n---\n\n## Tu respuesta anterior\n\n" + open(os.path.join(ds, x), encoding="utf-8").read())
            log(f"Verificación, con un subagente NUEVO: «Lee {pv} y haz exactamente lo que dice (las imágenes están en {out}). Escribe tu respuesta en {os.path.join(ds, x)}.»")
        return
    p = os.path.join(out, f"{a.tipo}.md")
    open(p, "w", encoding="utf-8").write(cuerpo)
    donde = "" if a.tipo == "papel" else f" (las imágenes están en {out})"
    log(f"Juez 1, con un subagente NUEVO: «Lee {p} y haz exactamente lo que dice{donde}. Escribe tu respuesta en {os.path.join(ds, salida)}.»")
    log(f"Juez 2, con OTRO subagente nuevo: «Lee {p} y haz exactamente lo que dice{donde}. Escribe tu respuesta en {os.path.join(ds, salida.replace('.md', '_2.md'))}.»")


# ------------------------------------------------------------------ rondas e informe

def estado_shorts(c):
    p = os.path.join(c, "shorts", "estado.json")
    return (json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}), p


def cmd_ronda(a):
    c = carpeta(a)
    e, p = estado_shorts(c)
    d = e.setdefault(a.s, {"rondas": 0, "notas": []})
    if d["rondas"] >= MAX_RONDAS and not a.palabras:
        sys.exit(f"{a.s} ya lleva {MAX_RONDAS} rondas: no se corrige más sin Antonio. short.py informe {a.id} y que decida.")
    d["rondas"] += 1
    d["notas"].append(a.nota + (f" (Antonio: «{a.palabras}»)" if a.palabras else ""))
    json.dump(e, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    log(f"Ronda {d['rondas']} de {MAX_RONDAS} en {a.s}. Corrige TODO lo de la lista y valida una sola vez.")


def cmd_informe(a):
    c = carpeta(a)
    e, _ = estado_shorts(c)
    lin = [f"# Shorts de {a.id}", ""]
    for ds in sorted(glob.glob(os.path.join(glob.escape(c), "shorts", "S*"))):
        s_ = os.path.basename(ds)
        gp = os.path.join(ds, "guion.json")
        if not os.path.exists(gp):
            continue
        g = json.load(open(gp, encoding="utf-8"))
        v = os.path.join(ds, f"{a.id}_{s_}.mp4")
        ctl = os.path.join(ds, "control_video.md") if os.path.exists(os.path.join(ds, "control_video.md")) else os.path.join(ds, "control_papel.md")
        filas = re.findall(r"^- \S+ \*\*(S\d) ([^*]+)\*\* (OK|AVISO|FALLO): (.+)$", open(ctl, encoding="utf-8").read(), re.M) if os.path.exists(ctl) else []
        pasa = sorted({f"{r} {n}" for r, n, est, _ in filas} - {f"{r} {n}" for r, n, est, _ in filas if est == "FALLO"})
        falla = [f"{r} {n}: {t[:140]}" for r, n, est, t in filas if est == "FALLO"]
        mejora = [f"{r}: {t[:110]}" for r, n, est, t in filas if est == "AVISO"]
        lin += [f"## {s_} · {g.get('angulo', '')} · {ffprobe_dur(v):.1f} s" if os.path.exists(v) else f"## {s_} · {g.get('angulo', '')} · sin vídeo",
                f"**Vídeo:** {os.path.basename(v) if os.path.exists(v) else '—'} · ronda {e.get(s_, {}).get('rondas', 0)} de {MAX_RONDAS}",
                f"**Título:** {g.get('titulo', '')}", f"**Pregunta para comentar:** {g.get('pregunta', '').replace('|', ' ').replace('*', '')}",
                f"**Pasa:** {', '.join(pasa) or '—'}"]
        lin += ["**Falla:**"] + [f"- {x}" for x in falla] if falla else ["**Falla:** nada"]
        if mejora:
            lin += ["**Se puede mejorar:**"] + [f"- {x}" for x in mejora[:5]]
        lin.append("")
    lin += ["## Decisión", "¿Cuáles se publican, y en qué fechas? (propuesta en references/publicar.md: el día después del largo y luego cada dos días, 18:00 de Madrid)"]
    out = os.path.join(c, "shorts", "informe.md")
    open(out, "w", encoding="utf-8").write("\n".join(lin) + "\n")
    print("\n".join(lin))


def main():
    for st in (sys.stdout, sys.stderr):
        if hasattr(st, "reconfigure"):
            st.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--raiz", default=RAIZ)
    sub = ap.add_subparsers(dest="cmd", required=True)
    x = sub.add_parser("inventario"); x.add_argument("id"); x.set_defaults(fn=cmd_inventario)
    x = sub.add_parser("voz"); x.add_argument("id"); x.add_argument("s"); x.add_argument("--modelo", choices=VOZ_MODELOS); x.add_argument("--presupuesto", action="store_true")
    x.add_argument("--rehacer", default=""); x.add_argument("--autoriza"); x.set_defaults(fn=cmd_voz)
    x = sub.add_parser("montar"); x.add_argument("id"); x.add_argument("s"); x.set_defaults(fn=cmd_montar)
    x = sub.add_parser("render"); x.add_argument("id"); x.add_argument("s"); x.add_argument("--stills", action="store_true"); x.set_defaults(fn=cmd_render)
    x = sub.add_parser("control"); x.add_argument("id"); x.add_argument("s"); x.add_argument("--papel", action="store_true"); x.set_defaults(fn=cmd_control)
    x = sub.add_parser("juez"); x.add_argument("id"); x.add_argument("s"); x.add_argument("tipo", choices=["papel", "video"]); x.add_argument("--verificar", action="store_true"); x.set_defaults(fn=cmd_juez)
    x = sub.add_parser("ronda"); x.add_argument("id"); x.add_argument("s"); x.add_argument("--nota", required=True); x.add_argument("--palabras"); x.set_defaults(fn=cmd_ronda)
    x = sub.add_parser("informe"); x.add_argument("id"); x.set_defaults(fn=cmd_informe)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
