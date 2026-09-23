"""System One: state crescente -> noul/choice/score."""
from __future__ import annotations
import json, os, re, urllib.request
from dataclasses import dataclass, field
from typing import Any

@dataclass
class Decision:
    complete: float = 0.0
    action: str = "none"
    action_probs: dict[str, float] = field(default_factory=dict)
    target: str = "none"
    target_probs: dict[str, float] = field(default_factory=dict)
    volume: float | None = None
    dictate_text: str = ""
    destructive: float = 0.0
    raw: dict[str, Any] = field(default_factory=dict)

ACTIONS = {
    "open_app": "Aprire un programma del catalogo",
    "close_app": "Chiudere un programma aperto",
    "open_folder": "Aprire una cartella nota",
    "dictate": "Dettare via clipboard",
    "set_volume": "Volume percentuale",
    "mute": "Muta",
    "unmute": "Smuta",
    "screenshot": "Screenshot",
    "read_screen": "Leggere lo schermo",
    "youtube": "Aprire YouTube",
    "obs_start": "Start OBS",
    "obs_stop": "Stop OBS",
    "none": "Nessuna azione",
}

_OPEN = re.compile(r"\b(apri|aprire|abre|open|avvia|lancia)\b", re.I)
_CLOSE = re.compile(r"\b(chiudi|chiudere|cierra|close|esci)\b", re.I)
_VOL = re.compile(r"\b(volume|audio)\b.*?(\d{1,3})", re.I)
_MUTE = re.compile(r"\b(muta|mute|silenzio)\b", re.I)
_UNMUTE = re.compile(r"\b(smuta|unmute|riattiva audio)\b", re.I)
_DICT = re.compile(r"\b(scrivi|detta|dettare|type|pega)\b", re.I)
_SHOT = re.compile(r"\b(screenshot|cattura schermo|foto schermo)\b", re.I)
_READ = re.compile(r"\b(leggi schermo|ocr)\b", re.I)
_YT = re.compile(r"\b(youtube|metti un video)\b", re.I)
_OBS_ON = re.compile(r"\b(inizia|avvia|start).{0,20}\b(obs|registrazione)\b", re.I)
_OBS_OFF = re.compile(r"\b(ferma|stop|smetti).{0,20}\b(obs|registrazione)\b", re.I)
_FOLDER = re.compile(r"\b(cartella|folder|download|documenti|desktop)\b", re.I)

def _match_target(text, catalog):
    low = text.lower(); best, score = "none", 0.0
    for name in catalog:
        if name.lower() in low and len(name) > score:
            best, score = name, float(len(name))
    if best == "none":
        return "none", 0.15
    return best, min(0.95, 0.45 + score / 20)

def _demo_decide(transcript, apps, folders):
    t = transcript.strip(); words = len(t.split()); catalog = {**apps, **folders}
    def base(action, target="none", complete=0.0):
        return Decision(complete=complete, action=action,
            action_probs={action: complete, "none": max(0.0, 1-complete)},
            target=target, destructive=0.85 if action=="close_app" else 0.05)
    if words == 0:
        return base("none", complete=0.02)
    target, tp = _match_target(t, catalog)
    if _VOL.search(t):
        n = int(_VOL.search(t).group(2)); d = base("set_volume", complete=0.9 if n<=100 else 0.4); d.volume=float(min(n,100)); return d
    if _MUTE.search(t): return base("mute", complete=0.88)
    if _UNMUTE.search(t): return base("unmute", complete=0.88)
    if _SHOT.search(t): return base("screenshot", complete=0.9)
    if _READ.search(t): return base("read_screen", complete=0.86)
    if _YT.search(t): return base("youtube", complete=0.84 if words>=2 else 0.4)
    if _OBS_ON.search(t): return base("obs_start", complete=0.86)
    if _OBS_OFF.search(t): return base("obs_stop", complete=0.86)
    if _DICT.search(t):
        d = base("dictate", complete=0.7 if words>=3 else 0.35)
        m = _DICT.search(t); d.dictate_text = t[m.end():].strip(" :,-"); return d
    if _CLOSE.search(t):
        return base("close_app", target, 0.82 if target!="none" else (0.55 if words>=2 else 0.2))
    if _FOLDER.search(t) and _OPEN.search(t):
        return base("open_folder", target, 0.83 if target!="none" else 0.5)
    if _OPEN.search(t):
        if target!="none": complete=max(tp,0.82)
        elif words<=2: complete=0.07
        else: complete=0.67
        return base("open_app", target, complete)
    return base("none", complete=min(0.25, words*0.04))

def _http_systemone(base_url, api_key, model, state, questions):
    payload = json.dumps({"model":model,"state":state,"questions":questions}).encode()
    req = urllib.request.Request(base_url.rstrip("/")+"/v1/systemone", data=payload,
        headers={"Content-Type":"application/json","Authorization":f"Bearer {api_key}"}, method="POST")
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode())

def _questions(apps, folders):
    targets = {n: f"App o cartella {n}" for n in [*apps, *folders]}
    targets["none"] = "Nessun target"
    return {
        "complete": {"type":"noul","instructions":"La frase e' un comando gia' eseguibile?"},
        "action": {"type":"choice","instructions":"Quale azione?","criteria":ACTIONS},
        "target": {"type":"choice","instructions":"Quale target del catalogo?","criteria":targets},
        "destructive": {"type":"noul","instructions":"Azione difficile da annullare?"},
    }

def _from_api(answers):
    return Decision(
        complete=float(answers.get("complete",{}).get("noul",0.0)),
        action=answers.get("action",{}).get("choice","none"),
        action_probs=answers.get("action",{}).get("probabilities") or {},
        target=answers.get("target",{}).get("choice","none"),
        target_probs=answers.get("target",{}).get("probabilities") or {},
        destructive=float(answers.get("destructive",{}).get("noul",0.0)),
        raw=answers,
    )

class ReflexDecider:
    def __init__(self, cfg):
        self.cfg=cfg; self.apps=cfg.get("apps",{}); self.folders=cfg.get("folders",{})
        self.backend=self._resolve_backend(cfg.get("backend","auto"))
        print(f"[decide] backend = {self.backend}")
    def _resolve_backend(self, wanted):
        if wanted in {"demo","jev","kev"}:
            if wanted=="jev" and not (os.getenv("TYPESAFE_API_KEY") or os.getenv("SYSTEMONE_API_KEY")):
                print("[decide] nessuna chiave, demo"); return "demo"
            return wanted
        if os.getenv("SYSTEMONE_BASE_URL"): return "kev"
        if os.getenv("TYPESAFE_API_KEY"): return "jev"
        return "demo"
    def decide(self, transcript, extra_state=None):
        extra_state = extra_state or {}
        if self.backend=="demo":
            return _demo_decide(transcript, self.apps, self.folders)
        state={"transcript":transcript,"language":self.cfg.get("language","it"),
               "installed_apps":list(self.apps),"known_folders":list(self.folders),**extra_state}
        questions=_questions(list(self.apps), list(self.folders))
        base=os.getenv("SYSTEMONE_BASE_URL","https://api.typesafe.ai")
        key=os.getenv("SYSTEMONE_API_KEY") or os.getenv("TYPESAFE_API_KEY") or "local"
        raw=_http_systemone(base,key,self.cfg.get("model","jev-latest"),state,questions)
        d=_from_api(raw.get("answers",raw)); self._enrich_slots(d,transcript); return d
    def _enrich_slots(self, d, transcript):
        m=_VOL.search(transcript)
        if m: d.volume=float(min(int(m.group(2)),100))
        if d.action=="dictate":
            m=_DICT.search(transcript)
            d.dictate_text=transcript[m.end():].strip(" :,-") if m else transcript
