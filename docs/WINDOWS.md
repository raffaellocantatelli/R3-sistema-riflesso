# Windows — collegare il riflesso a QUESTO PC

Grok non ha il mouse sul tuo desktop. Lo script configura Windows al posto dei click.

## Un comando

Apri **PowerShell** (Start → scrivi PowerShell → Invio) e incolla:

```powershell
irm https://raw.githubusercontent.com/raffaellocantatelli/R3-sistema-riflesso/main/scripts/setup-windows.ps1 | iex
```

Se Windows blocca gli script:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

poi rilancia la riga `irm ...`.

## Cosa fa, da solo

1. Installa Git e Python 3.12 se mancano (winget).
2. Clona il repo in `%USERPROFILE%\R3-sistema-riflesso`.
3. Crea `.venv` e installa le dipendenze.
4. Imposta `config.json` su italiano / backend demo.
5. Mette sul Desktop la scorciatoia **R3 Riflesso**.
6. Lancia il replay del reel (FERMO / ATTESA / SCATTO).

Non apre TeamViewer, RDP, AnyDesk, SSH. Non da' il mouse a Grok.

## Dopo il setup

Doppio click su **R3 Riflesso** sul Desktop. Scrivi:

```
apri il blocco note
volume al 30
```

Esci con `:q`.

## Catalogo

Se un'app non e' in `config.json`, il riflesso non la apre. Aggiungi il nome a mano. Questa e' la legge System One: non inventa target.
