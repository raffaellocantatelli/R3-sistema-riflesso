# R³∞ Sistema Riflesso

Satellite del Protocollo Rosso Rosso Rosso.

**auth: CA. Non è canone. Non scrive sul ledger. Jev è advisory.**

Non è un chatbot. È un riflesso: stato crescente → decisioni tipizzate (`noul` / `choice` / `score`) → soglie nel codice → esecutore con catalogo chiuso.

Sopra resta System Two (tesi, P6, uomo).  
Sotto sta questo strato. Una probabilità 0.82 non è RECUPERATO.

Repo: https://github.com/raffaellocantatelli/R3-sistema-riflesso  
Non tocca `protocollo-rosso-bot`, `R3-privato`, né il checkpoint `SYNC-2026-09-16-0615`.

## Avvio

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m r3_riflesso.reflex --backend demo --replay
python -m r3_riflesso.reflex --backend demo --text "apri il blocco note"
python -m r3_riflesso.reflex --backend demo          # stdin
```

Jev vero (opzionale):

```bash
pip install typesafe-sdk
export TYPESAFE_API_KEY=ts_...
python -m r3_riflesso.reflex --backend jev
```

Kev locale, stessa API:

```bash
export SYSTEMONE_BASE_URL=http://127.0.0.1:8009
export SYSTEMONE_API_KEY=local
python -m r3_riflesso.reflex --backend kev
```

## Soglie (reel Grant Keegan)

| Frase | complete | stance |
|---|---|---|
| abre el | 0.07 | FERMO |
| abre el bloc | 0.67 | ATTESA |
| abre el bloc de notas | ≥ 0.80 | SCATTO |

## Strato epistemico R3

```bash
python -m r3_riflesso.epistemic "voglio che lo inseriamo nel protocollo"
python -m r3_riflesso.epistemic "è dimostrato, non serve verificare"
python -m r3_riflesso.epistemic "ho committato su protocollo-rosso-bot"
```

## Test

```bash
python -m unittest discover -s tests -v
```

## Mappa

```
r3_riflesso/     loop + decider + esecutore + gate epistemico
docs/            candidato CA + pagina 3.5 proposta
tests/           soglie del reel e porte rosse
config.json      catalogo chiuso (se non è in lista, non si apre)
```

## Protocollo

Documento: [`docs/R3_RIFLESSO_SYSTEM_ONE_CA_2026-09-23.md`](docs/R3_RIFLESSO_SYSTEM_ONE_CA_2026-09-23.md)

Gate CN chiuso. Per fondere in `protocollo-rosso-bot` serve la frase nuda del custode: `COMMITA SU protocollo-rosso-bot`.
