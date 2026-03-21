---
name: session-close
description: Sulgeb sessiooni — koondab töö, uuendab kontekstifailid, commitib Giti
user_invocable: true
---

# Session Closer

Kui see skill aktiveerub, tee järgmised sammud:

## 1. Koonda sessiooni kokkuvõte
- Loe läbi vestluse ajalugu
- Tuvasta: mis tehti, mis otsuseid langetati, mis jäi pooleli

## 2. Uuenda kontekstifailid
- Uuenda projekti CLAUDE.md praeguse olekuga
- Kui projektis on GEMINI.md või AGENTS.md, uuenda ka need
- Lisa: viimane sessiooni kuupäev, tehtud tööd, järgmised sammud

## 3. Uuenda sessiooni logi
- Fail: `session-log.md` projekti juurkaustas
- Lisa uus sissekanne formaadis:
```
## [kuupäev]
### Tehtud
- [nimekiri]
### Otsused
- [nimekiri]
### Järgmine kord
- [nimekiri]
```

## 4. Git commit
- Stage kõik muudetud failid
- Commit sõnum: "session: [kuupäev] - [lühikokkuvõte]"

## 5. Lõppsõnum kliendile
Formaadis:
```
Sessioon suletud.
Tehtud: [1-3 lauset]
Homme alusta siit: [konkreetne järgmine samm]
```
