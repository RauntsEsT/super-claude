---
name: notebooklm
description: Google NotebookLM integratsioon — loo notebookke, lisa allikaid, saa analüüse ja väljundeid (infograafikad, slaidid, podcastid)
user_invocable: true
---

# NotebookLM Skill

Integratsioon Google NotebookLM-iga. Analüüs toimub Google'i serverites TASUTA.

## CLI path
```bash
NLM="notebooklm"  # Install: pip install notebooklm (or see README for platform-specific path)
```

## Käsud

### Notebookid
```bash
$NLM list                           # Loetelu
$NLM create "Nimi"                   # Loo uus
$NLM use <id>                       # Vali aktiivne notebook
$NLM status                         # Näita aktiivne notebook
$NLM delete <id>                    # Kustuta
$NLM rename <id> "Uus nimi"         # Nimeta ümber
$NLM summary                        # AI kokkuvõte
```

### Allikad
```bash
$NLM source add <id> --youtube "https://youtube.com/watch?v=..."
$NLM source add <id> --url "https://..."
$NLM source add <id> --text "tekst"
$NLM source add <id> --file path/to/file.pdf
$NLM source list <id>               # Allikate loetelu
$NLM source wait <id>               # Oota kuni allikad töödeldud
```

### Küsimused
```bash
$NLM use <id>                       # Vali notebook
$NLM ask "Mis on peamised teemad?"  # Küsi
$NLM history                        # Vestluse ajalugu
```

### Väljundid (generate + download)
```bash
$NLM generate audio                 # Podcast
$NLM generate infographic           # Infograafika
$NLM generate slide-deck            # Slaidid
$NLM generate mind-map              # Mind map
$NLM generate quiz                  # Quiz
$NLM generate flashcards            # Flashcard'id
$NLM generate report                # Raport
$NLM generate video                 # Video
$NLM generate data-table            # Andmetabel

$NLM download infographic           # Lae alla
$NLM download slide-deck
$NLM download audio
# jne...
```

### Märkused ja jagamine
```bash
$NLM note create "Pealkiri" "Sisu"  # Loo märkus
$NLM note list                      # Märkmete loetelu
$NLM share status                   # Jagamise olek
```

## Töövoog koos YouTube Search skill'iga
1. `/yt-search` — otsi videod
2. `$NLM create "Teema"` — loo notebook
3. `$NLM source add <id> --youtube "url"` — lisa videod (max 50)
4. `$NLM source wait <id>` — oota töötlemist
5. `$NLM use <id>` + `$NLM ask "küsimus"` — saa analüüs
6. `$NLM generate infographic` — genereeri väljund
7. `$NLM download infographic` — lae alla

## Oluline
- Max 50 allikat ühe notebooki kohta
- Analüüs on TASUTA — Google maksab
- Kasuta `source wait` enne küsimuste esitamist
- Notebook ID võib olla osaline (nt esimesed 6 tähemärki)
