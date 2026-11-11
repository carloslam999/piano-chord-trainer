# Piano Chord Trainer

Play-along pages for learning classical piano pieces from their chords: falling melody and chord notes on a piano, a chord bar and full chord map, rolling sheet music, looping and adjustable speed.

Live site: https://carloslam999.github.io/nocturne-chord-trainer/

## Pieces

- Chopin, Nocturne in E♭ major, Op. 9 No. 2 (`nocturne-op9-no2.html`)
- Debussy, Clair de Lune (`clair-de-lune.html`)

## How it is organised

- `index.html` is the library page listing every piece.
- `assets/trainer.js` and `assets/trainer.css` are the player, shared by all pieces.
- `songs/<id>.js` holds one piece: its notes, chords, sections and page text.
- `<id>.html` is a small page that loads one song file into the player.

To add a piece: add `songs/<id>.js`, copy one of the song pages and point it at the new file, then add a card to the `SONGS` list in `index.html`.

## Sources and credits

- Nocturne chords follow the bar-by-bar table at chopinlefthand.com. Its notes come from the G. Schirmer 1881 edition as typeset by the Mutopia Project (Renato Biolcati Rinaldi), licensed CC BY-SA 3.0; that note data is shared here under the same license.
- Clair de Lune notes come from the E. Fromont 1905 edition as typeset by the Mutopia Project (Keith OHara, public domain). Its chord names are an original reading of the score.
