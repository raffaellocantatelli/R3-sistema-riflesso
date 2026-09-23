"""Esecutore locale. Il modello sceglie SOLO dal catalogo."""
from __future__ import annotations
import os, platform, shutil, subprocess, webbrowser
from pathlib import Path
from urllib.parse import quote_plus
from .decide import Decision

def _which(cmd): return shutil.which(cmd)
def _run(args):
    try:
        p=subprocess.run(args,check=False,capture_output=True,text=True,timeout=15)
        return (p.stdout or p.stderr or "").strip()[:400]
    except Exception as exc:
        return f"errore: {exc}"
def _expand(path): return os.path.expanduser(os.path.expandvars(path))

def open_app(exe):
    system=platform.system()
    try:
        if system=="Windows":
            subprocess.Popen(["cmd","/c","start","",exe]); return f"aperto {exe}"
        if system=="Darwin":
            return _run(["open","-a",exe]) or f"aperto {exe}"
        bin_path=_which(exe)
        if not bin_path: return f"app '{exe}' non trovata"
        subprocess.Popen([bin_path], start_new_session=True); return f"aperto {bin_path}"
    except FileNotFoundError:
        return f"app '{exe}' non trovata"

def close_app(name):
    if platform.system()=="Windows": return _run(["taskkill","/IM",name,"/F"]) or f"chiuso {name}"
    return _run(["pkill","-f",name]) or f"chiusura {name}"

def open_folder(path):
    path=_expand(path); system=platform.system()
    if system=="Windows": subprocess.Popen(["explorer",path])
    elif system=="Darwin": subprocess.Popen(["open",path])
    else: subprocess.Popen(["xdg-open",path])
    return f"cartella {path}"

def set_clipboard(text):
    if not text: return "nessun testo"
    system=platform.system()
    try:
        if system=="Windows":
            p=subprocess.Popen(["clip"],stdin=subprocess.PIPE); p.communicate(text.encode("utf-16le"))
        elif system=="Darwin":
            p=subprocess.Popen(["pbcopy"],stdin=subprocess.PIPE); p.communicate(text.encode())
        elif _which("wl-copy"):
            p=subprocess.Popen(["wl-copy"],stdin=subprocess.PIPE); p.communicate(text.encode())
        elif _which("xclip"):
            p=subprocess.Popen(["xclip","-selection","clipboard"],stdin=subprocess.PIPE); p.communicate(text.encode())
        else:
            return "installa wl-copy o xclip"
        return f"clipboard {len(text)} caratteri"
    except Exception as exc:
        return f"clipboard fallita: {exc}"

def set_volume(percent):
    percent=max(0,min(100,percent)); system=platform.system()
    if system=="Darwin":
        _run(["osascript","-e",f"set volume output volume {int(percent)}"]); return f"volume {percent:.0f}%"
    if _which("pactl"):
        _run(["pactl","set-sink-volume","@DEFAULT_SINK@",f"{int(percent)}%"]); return f"volume {percent:.0f}%"
    if _which("nircmd"):
        _run(["nircmd","setsysvolume",str(int(percent*65535/100))]); return f"volume {percent:.0f}%"
    return "backend volume assente"

def mute(on):
    if platform.system()=="Darwin":
        _run(["osascript","-e",f"set volume output muted {'true' if on else 'false'}"])
        return "muto" if on else "audio on"
    if _which("pactl"):
        _run(["pactl","set-sink-mute","@DEFAULT_SINK@","1" if on else "0"])
        return "muto" if on else "audio on"
    return "mute non disponibile"

def screenshot():
    dest=str(Path.home()/"Desktop"/"reflex-shot.png"); system=platform.system()
    if system=="Darwin": _run(["screencapture","-x",dest]); return dest
    if _which("grim"): _run(["grim",dest]); return dest
    return "nessun tool screenshot"

def open_youtube(query):
    url="https://www.youtube.com" if query.strip().lower() in {"youtube","metti un video",""} else "https://www.youtube.com/results?search_query="+quote_plus(query)
    webbrowser.open(url); return url

def obs_recording(start):
    if _which("obs-cli"):
        cmd="start" if start else "stop"; return _run(["obs-cli","recording",cmd]) or cmd
    return "installa obs-cli"

def execute(decision: Decision, cfg: dict) -> str:
    if cfg.get("dry_run"):
        return f"DRY-RUN {decision.action} target={decision.target} volume={decision.volume}"
    apps=cfg.get("apps",{}); folders=cfg.get("folders",{}); act=decision.action; tgt=decision.target
    if act=="open_app":
        exe=apps.get(tgt) or apps.get(tgt.lower())
        return open_app(exe) if exe else f"target '{tgt}' fuori catalogo"
    if act=="close_app": return close_app(Path(apps.get(tgt) or tgt).name)
    if act=="open_folder":
        path=folders.get(tgt) or folders.get(tgt.lower())
        return open_folder(path) if path else f"cartella '{tgt}' sconosciuta"
    if act=="dictate": return set_clipboard(decision.dictate_text)
    if act=="set_volume": return set_volume(decision.volume) if decision.volume is not None else "manca il numero"
    if act=="mute": return mute(True)
    if act=="unmute": return mute(False)
    if act=="screenshot": return screenshot()
    if act=="read_screen": return "lettura schermo: placeholder locale, niente vision cloud"
    if act=="youtube": return open_youtube(decision.dictate_text or tgt or "")
    if act=="obs_start": return obs_recording(True)
    if act=="obs_stop": return obs_recording(False)
    return "nessuna azione"
