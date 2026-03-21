---
name: yt-search
description: YouTube'ist videote otsimine ja metaandmete tõmbamine yt-dlp abil
user_invocable: true
---

# YouTube Search Skill

Otsib YouTube'ist videoid ja tagastab metaandmed (pealkiri, kanal, vaatamised, kestus, kuupäev).

## Kasutamine

### Otsing
```bash
python ~/.claude/skills/yt-search/yt_search.py "otsingutermin" [kogus]
```

- `otsingutermin` — mida otsida YouTube'ist
- `kogus` — mitu tulemust (vaikimisi 10, max 50)

### Näited
```bash
# Otsi 10 Claude Code videot
python ~/.claude/skills/yt-search/yt_search.py "Claude Code skills" 10

# Otsi 20 AI terminal videot
python ~/.claude/skills/yt-search/yt_search.py "AI terminal tools 2025" 20
```

## Väljund
JSON massiiv objektidega:
- `title` — video pealkiri
- `url` — YouTube link
- `channel` — kanali nimi
- `views` — vaatamiste arv
- `duration` — video pikkus
- `upload_date` — üleslaadimise kuupäev
- `description` — kirjelduse esimesed 200 tähemärki

## Soovitused
- Kasuta ingliskeelset otsingut parimate tulemuste jaoks
- Sorteeri vaatamiste järgi, et leida populaarseimad
- Kombineeri NotebookLM skill'iga: otsi videod → lae NotebookLM-i → saa analüüs
