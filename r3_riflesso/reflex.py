#!/usr/bin/env python3
"""Loop riflesso."""
from __future__ import annotations
import argparse, json, sys, time
from pathlib import Path
from .actions import execute
from .decide import ReflexDecider

ROOT = Path(__file__).resolve().parents[1]

def load_cfg(path):
    # utf-8-sig: PowerShell Set-Content -Encoding UTF8 scrive il BOM.
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))

def tick(decider, cfg, transcript, last_fired):
    t=transcript.strip()
    if len(t)<cfg["min_chars"]:
        print(f"  … '{t}'  (troppo corto)"); return
    t0=time.perf_counter(); d=decider.decide(t); ms=(time.perf_counter()-t0)*1000
    bar=f"complete={d.complete:.2f}  action={d.action}  target={d.target}"
    if d.complete<cfg["wait_threshold"]:
        print(f"  [{ms:6.0f} ms] FERMO   {bar}  «{t}»"); return
    if d.complete<cfg["fire_threshold"] or d.action=="none":
        print(f"  [{ms:6.0f} ms] ATTESA  {bar}"); return
    sig=f"{d.action}:{d.target}:{d.dictate_text}:{d.volume}"
    if sig==last_fired[0]:
        print(f"  [{ms:6.0f} ms] gia' eseguito"); return
    if d.destructive>=0.75:
        print(f"  [{ms:6.0f} ms] BLOCCATO p={d.destructive:.2f}"); return
    result=execute(d,cfg); last_fired[0]=sig
    print(f"  [{ms:6.0f} ms] SCATTO  {bar}\n           → {result}")

def replay_reel(decider, cfg):
    last=[""]
    print("\nRiproduzione reel:\n")
    for fragment in ("abre el","abre el bloc","abre el bloc de notas"):
        print(f"# {fragment}"); tick(decider,cfg,fragment,last)
    print("\nItaliano:\n")
    for fragment in ("apri il","apri il blocco note","volume al 30","apri la cartella download"):
        print(f"# {fragment}"); tick(decider,cfg,fragment,last)

def loop_stdin(decider, cfg):
    last=[""]
    print("\nModalita' testo. :q per uscire.\n")
    while True:
        try: line=input("tu> ").strip()
        except (EOFError,KeyboardInterrupt):
            print("\nstop"); return
        if not line: continue
        if line in {":q","esci","stop"}: return
        tick(decider,cfg,line,last)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--config", default=str(ROOT/"config.json"))
    p.add_argument("--backend", choices=["auto","jev","kev","demo"])
    p.add_argument("--text")
    p.add_argument("--replay", action="store_true")
    args=p.parse_args()
    cfg=load_cfg(args.config)
    if args.backend: cfg["backend"]=args.backend
    decider=ReflexDecider(cfg)
    print("SISTEMA RIFLESSO  ·  System One, non chatbot")
    print(f"backend={decider.backend} fire={cfg['fire_threshold']} wait={cfg['wait_threshold']}")
    if args.replay:
        cfg["dry_run"]=True; replay_reel(decider,cfg); return 0
    if args.text:
        tick(decider,cfg,args.text,[""]); return 0
    loop_stdin(decider,cfg); return 0

if __name__=="__main__":
    sys.exit(main())
