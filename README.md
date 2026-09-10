# Il Fondale Misterioso - CNR Sharper Night 2026

Gioco Pygame sul benthos per lo stand del CNR ad Ancona (25 settembre 2026).
Il visitatore sceglie un avatar, scrive il proprio nome e affronta 3 livelli
su animali bentonici e i loro habitat. Alla fine viene mostrata (ed e'
salvata) una classifica con tempo totale - la parte che ha avuto successo
l'anno scorso.

## Come si gioca

1. **Avatar + nome**: si sceglie un'icona tra 6 e si scrive il proprio nome.
2. **Livello 1 - Memory**: le carte si scoprono per qualche secondo, poi
   si girano. Bisogna trovare le coppie animale/habitat.
3. **Livello 2 - Trascina**: si trascina ogni animale nella casella del
   suo habitat corretto (tasto sinistro del mouse, drag & drop).
4. **Livello 3 - Quiz**: 6 domande a risposta multipla sul benthos,
   estratte a caso da un elenco di 10.
5. **Risultati**: tempo totale (con penalita' per gli errori), posizione
   in classifica, e piccola animazione finale con gli animaletti che
   "esplodono" a schermo (l'effetto particellare dell'anno scorso).

Il punteggio finale e la classifica sono salvati in `leaderboard.json`,
nella stessa cartella dello script, e persistono tra una partita e l'altra
(utile per tenere la classifica viva per tutta la serata).

## Avvio

```
pip install pygame
python3 benthos_game.py
```

Tasti/azioni:
- Click sinistro per selezionare/trascinare
- Digitare per scrivere il nome nella schermata iniziale
- `Esc` per uscire
- Ridimensionare la finestra e' supportato (tutto si riadatta)

## Immagini

Il gioco funziona GIA' ORA anche senza immagini reali: ogni icona mancante
viene sostituita automaticamente da un riquadro colorato con le iniziali,
cosi' puoi testare tutta la logica del gioco da subito. Quando avrai le
immagini vere, mettile semplicemente nei percorsi elencati in
`ASSETS_NEEDED.md` (stessi nomi file, stessa cartella) e verranno usate
in automatico, senza toccare il codice.

Consiglio per lo stand: immagini quadrate, sfondo trasparente (PNG),
almeno 500x500 px, cosi' restano nitide anche a schermo intero.

## Personalizzare le domande del quiz o le coppie animale/habitat

Tutto il contenuto (coppie animale-habitat, avatar, domande del quiz) e'
raccolto all'inizio del file `benthos_game.py`, nelle liste `PAIRS`,
`AVATARS` e `QUIZ_QUESTIONS`: si puo' modificare/aggiungere voci senza
toccare il resto del codice.
