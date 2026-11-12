# Piano Chord Trainer

Play-along pages for learning classical piano pieces from their chords: falling melody and chord notes on a piano, a chord bar and full chord map, rolling sheet music, looping and adjustable speed.

Live site: https://carloslam999.github.io/piano-chord-trainer/

## Pieces

| Piece | Composer | Level |
| --- | --- | --- |
| Old French Song, Op. 39 No. 16 | Tchaikovsky | Beginner |
| Prelude in C major, BWV 846 | Bach | Beginner |
| Gymnopédie No. 1 | Satie | Beginner |
| Gnossienne No. 1 | Satie | Intermediate |
| Für Elise | Beethoven | Intermediate |
| Moonlight Sonata, 1st movement | Beethoven | Intermediate |
| Prelude in E minor, Op. 28 No. 4 | Chopin | Intermediate |
| Träumerei, Op. 15 No. 7 | Schumann | Intermediate |
| Nocturne No. 5 in B♭ major, H. 37 | Field | Intermediate |
| Prelude in A major, Op. 28 No. 7 | Chopin | Beginner |
| Minuet in G minor, BWV Anh. 115 | Bach (now credited to Petzold) | Beginner |
| The Entertainer | Joplin | Intermediate |
| Rondo alla Turca, K. 331 | Mozart | Intermediate |
| Sonata in C, K. 545, 1st movement | Mozart | Intermediate |
| Arabesque No. 1 | Debussy | Advanced |
| Nocturne in E♭ major, Op. 9 No. 2 | Chopin | Advanced |
| Clair de Lune | Debussy | Advanced |

## How it is organised

- `index.html` is the library page listing every piece.
- `assets/trainer.js` and `assets/trainer.css` are the player, shared by all pieces.
- `songs/<id>.js` holds one piece: its notes, chords, sections and page text.
- `<id>.html` is a small page that loads one song file into the player.

To add a piece, see `tools/README.md`: `tools/import_midi.py` turns a Mutopia MIDI file into song data with suggested chords, and `tools/songs_extra.py` lists each piece's text, level and mood.

## Sources and credits

- Nocturne chords follow the bar-by-bar table at chopinlefthand.com. Its notes come from the G. Schirmer 1881 edition as typeset by the Mutopia Project (Renato Biolcati Rinaldi), licensed CC BY-SA 3.0; that note data is shared here under the same license.
- Clair de Lune notes come from the E. Fromont 1905 edition as typeset by the Mutopia Project (Keith OHara, public domain). Its chord names are an original reading of the score.
- The eight pieces added in November 2026 come from Mutopia Project MIDI and LilyPond files. Gnossienne No. 1 (Knute Snortum) is CC BY-SA 4.0 and the Moonlight Sonata (Stewart Holmes) is CC BY-SA 2.5; their note data is shared here under the same licenses. The others are public domain. Their chord names were worked out automatically from the notes and spot-checked.
- John Field's Nocturne No. 5 (Alex Schreiber, Mutopia Project) is CC BY-SA 4.0; its note data is shared here under the same license.
- Mozart's Sonata K. 545 (Alejandro Sierra, Mutopia Project) is CC BY-SA 3.0 and shared under the same license; The Entertainer, Rondo alla Turca, Arabesque No. 1 and Chopin's A major Prelude are public domain.
