"""R3 · Strato Riflesso — CANDIDATO.

Non è canone. Non scrive sul ledger. Non parla della tesi del già.

Due backend:
  demo  — soglie locali, niente rete (default)
  jev   — TypeSafe / Kev, advisory. Se manca la chiave, ricade su demo.

Il riflesso risponde solo con primitive chiuse. Se la lista non contiene
l'oggetto, torna UNKNOWN. Una probabilità alta non è RECUPERATO.
"""

from __future__ import annotations

from dataclasses import dataclass

LAYERS = (
    "RECUPERATO",
    "INFERITO",
    "IPOTESI",
    "DESIDERIO",
    "TECNICO",
    "SIMULAZIONE",
    "RISONANZA",
    "UNKNOWN",
)

FIRE = 0.80
WAIT = 0.55
DESTRUCTIVE = 0.75
CLOSURE = 0.75


@dataclass(frozen=True)
class Reflex:
    layer: str
    complete: float
    closure: float
    destructive: float
    stance: str
    note: str
    backend: str


def _demo(text: str) -> Reflex:
    t = (text or "").strip().lower()
    if not t:
        return Reflex("UNKNOWN", 0.0, 0.0, 0.0, "FERMO", "vuoto", "demo")

    thesis = any(
        s in t
        for s in (
            "tesi del già",
            "ologramma",
            "tutto ciò che potrà",
            "esiste già ora",
            "campo del già",
        )
    )
    closing = any(
        s in t
        for s in ("è certo", "è dimostrato", "sicuramente", "è un fatto", "non verificare")
    )
    desire = any(s in t for s in ("desidero", "vorrei", "voglio che", "spero"))
    sim = any(s in t for s in ("simulo", "come se", "fingiamo", "esercizio"))
    recovered = any(
        s in t
        for s in ("ho letto alla fonte", "ho eseguito", "nel log", "status code", "ho committato")
    )
    technical = any(
        s in t
        for s in ("deploy", "ping", "commit", "clipboard", "apri il", "volume al")
    )

    if thesis:
        return Reflex(
            "IPOTESI",
            0.9,
            0.85 if closing else 0.1,
            0.0,
            "BLOCCO" if closing else "ATTESA",
            "Tesi del già. Resta aperta. Il riflesso non la promuove.",
            "demo",
        )
    if closing and not recovered:
        return Reflex(
            "UNKNOWN",
            0.7,
            0.86,
            0.0,
            "BLOCCO",
            "Suona chiusura senza fonte. P5.",
            "demo",
        )
    if recovered:
        return Reflex("RECUPERATO", 0.84, 0.05, 0.1, "SCATTO", "Sembra recupero. Serve terzo.", "demo")
    if technical:
        return Reflex("TECNICO", 0.86, 0.05, 0.1, "SCATTO", "Atto o dato, non fede.", "demo")
    if desire:
        return Reflex("DESIDERIO", 0.8, 0.05, 0.0, "ATTESA", "Lecito finché non si veste da fatto.", "demo")
    if sim:
        return Reflex("SIMULAZIONE", 0.8, 0.05, 0.0, "FERMO", "Non è accaduto nel mondo.", "demo")
    if len(t.split()) < 3:
        return Reflex("UNKNOWN", 0.07, 0.0, 0.0, "FERMO", "Frammento. Come «abre el».", "demo")
    return Reflex("UNKNOWN", 0.4, 0.1, 0.0, "ATTESA", "Non classificabile. Tratta come IPOTESI.", "demo")


def decide(text: str, backend: str = "demo") -> Reflex:
    if backend == "jev":
        try:
            return _jev(text)
        except Exception as exc:
            r = _demo(text)
            return Reflex(r.layer, r.complete, r.closure, r.destructive, r.stance, f"jev fallito ({exc}); demo", "demo")
    return _demo(text)


def _jev(text: str) -> Reflex:
    import os
    from typesafe_sdk import Choice, Noul, TypeSafeClient

    questions = {
        "complete": Noul(
            instructions="Il testo è un enunciato già eseguibile o classificabile senza chiedere altro?"
        ),
        "layer": Choice(
            instructions="Quale strato epistemico R3, senza promuovere tesi a fatto?",
            criteria={k: None for k in LAYERS},
        ),
        "closure": Noul(
            instructions="Il testo chiude una possibilità grande spacciandola per fatto, o vieta la verifica?"
        ),
        "destructive": Noul(
            instructions="Eseguirlo cancellerebbe dati o chiuderebbe il canone senza gate?"
        ),
    }
    with TypeSafeClient(model=os.getenv("R3_SYSTEMONE_MODEL", "jev-latest")) as client:
        out = client.system_one({"transcript": text, "protocol": "R3"}, questions)
    complete = float(out.nouls["complete"].noul)
    closure = float(out.nouls["closure"].noul)
    destructive = float(out.nouls["destructive"].noul)
    layer = out.choices["layer"].choice
    if layer not in LAYERS:
        layer = "UNKNOWN"
    if layer == "RECUPERATO" and closure >= CLOSURE:
        layer = "UNKNOWN"
    if complete < WAIT:
        stance = "FERMO"
    elif complete < FIRE:
        stance = "ATTESA"
    else:
        stance = "SCATTO"
    if closure >= CLOSURE or destructive >= DESTRUCTIVE:
        stance = "BLOCCO"
    return Reflex(layer, complete, closure, destructive, stance, "advisory System One", "jev")


def gate(reflex: Reflex) -> str:
    if reflex.stance == "BLOCCO":
        return "STOP — chiusura o distruttivo. Serve l'uomo."
    if reflex.layer in {"IPOTESI", "RISONANZA", "DESIDERIO", "SIMULAZIONE"}:
        return "non eseguire: non è strato tecnico"
    if reflex.stance == "FERMO":
        return "non ancora"
    if reflex.stance == "ATTESA":
        return "so che è qualcosa, manca il pezzo"
    return "eseguibile solo come TECNICO, con log visibile a un terzo"


def main() -> None:
    import sys
    text = " ".join(sys.argv[1:]) or ""
    r = decide(text)
    print(f"{r.stance}\t{r.layer}\tcomplete={r.complete:.2f}\tclosure={r.closure:.2f}\t{r.backend}")
    print(r.note)
    print(gate(r))


if __name__ == "__main__":
    main()
