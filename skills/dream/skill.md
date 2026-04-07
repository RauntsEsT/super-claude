---
name: dream
description: Konsolideerib mälu — analüüsib sessiooni ajalugu, puhastab vananenud info, uuendab PROJECT_STATE.md
user_invocable: true
---

# Dream — Mälu Konsolideerija

Kui see skill aktiveerub, tee järgmist **ilma kasutajalt küsimata**:

## 1. Loe hetke olek
- `{{SUPER_CLAUDE_DIR}}\PROJECT_STATE.md`
- Viimased 3 sessiooni faili `{{SUPER_CLAUDE_DIR}}\sessions\` kaustast
- Praegune projekti CLAUDE.md (kui on)

## 2. Analüüsi ja konsolideeri
Tuvasta:
- **Korduvad mustrid** — mis probleeme lahendatakse pidevalt? → lisa PROJECT_STATE.md-sse "Known patterns"
- **Vananenud info** — otsused mis on muutunud, TODO-d mis on tehtud → kustuta või märgi
- **Uus teadmine** — mis õpiti, mis töötab hästi → säilita
- **Järgmised sammud** — mis on selgelt järgmine prioriteet?

## 3. Uuenda PROJECT_STATE.md
Struktuur:
```
# Project State
Last updated: [kuupäev]

## Active Project
[projekti nimi ja lühikirjeldus]

## Status
[Done / In Progress / Blocked]

## Key Decisions
- [otsus 1]
- [otsus 2]

## Known Patterns
- [korduv muster 1]

## Next Steps
1. [konkreetne samm]
2. [järgmine]

## Graveyard (done/dropped)
- [lõpetatud asjad]
```

## 4. Raport kasutajale
```
Dream complete.
Konsolideeritud: [N] sessiooni
Puhastatud: [mis eemaldati]
Uus teadmine: [1-2 lauset]
Järgmine prioriteet: [konkreetne]
```
