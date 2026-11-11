# Build tools

These scripts turned the Mutopia LilyPond scores into the song files in `songs/`. They were written for the two current pieces, so treat them as a starting point for new ones, not a finished pipeline.

## Files

- `parse_cdl.py`: parses a LilyPond score (`\parallelMusic`, english note names) into notes with timing, pitch and spelling, plus clef and 8va changes. Prints a check that every bar has the right length.
- `parse_noc.py`: the same for the Nocturne's simpler two-staff score, reusing `parse_cdl.py`.
- `build_cdl.py` + `cdl_addon.py`: earlier one-off build of the Clair de Lune page; holds its chord list (`C = {...}`), chord spellings and section notes.
- `build_site.py`: builds the site: `assets/trainer.js`, `assets/trainer.css`, `songs/*.js`, each song page and `index.html`. It reads the frozen pages in `base/` and the parsed notes in `src/`.
- `make_preview.py`: draws `assets/preview.png`, the image shown when a link is shared (needs Pillow).
- `src/`: the original Mutopia scores and the parsed note data.

## Re-running

From this folder, with `<work>` set to a scratch folder laid out as `build_site.py` expects (`base/`, `noc/notes.json`, `preview.png`):

```bash
python3 parse_cdl.py src/clair.ly src/clair-notes.json
python3 build_site.py <work> <output-folder>
```

## Adding a piece

1. Find the piece on the Mutopia Project and download its `.ly` file into `src/`.
2. Parse it and check the bar-length report is clean.
3. Write the chord list for each bar (symbol, Roman numeral, length in eighth notes) and the sections.
4. Write `songs/<id>.js` in the same shape as the existing ones, copy a song page to `<id>.html`, and add a card to `SONGS` in `index.html`.
