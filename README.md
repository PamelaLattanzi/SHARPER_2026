# Il Fondale Misterioso - CNR Sharper Night 2026

Gioco Pygame sul benthos per lo stand del CNR ad Ancona (25 settembre 2026).
Il visitatore sceglie un avatar, scrive il proprio nome e affronta 3 livelli
sugli organismi marini e i loro habitat. Ogni livello ha una sfida FACILE
seguita da una DIFFICILE. Alla fine viene mostrata (ed e' salvata) una
classifica con tempo totale.

## Come si gioca

1. **Avatar + nome**: si sceglie un'icona tra 6 e si scrive il proprio nome
   (massimo 7 caratteri, per restare leggibile anche in classifica).
2. **Livello 1 - Trova l'intruso**: in un gruppo di 4 immagini, una non
   c'entra con le altre. Prima una sfida facile, poi una difficile.
   Dopo la risposta viene mostrata la spiegazione per qualche secondo
   (quel tempo non conta nel cronometro).
3. **Livello 2 - Trascina**: si trascina ogni animale nella zona giusta
   dello sfondo (tasto sinistro del mouse, drag & drop). Prima la sfida
   facile (aria/spiaggia, colonna d'acqua, fondale), poi quella difficile
   (le due interfacce: aria-acqua e acqua-fondale).
4. **Livello 3 - Quiz**: una domanda facile e una difficile, estratte a
   caso dall'elenco del file JSON.
5. **Risultati**: tempo totale (con penalita' per gli errori), posizione
   in classifica — con l'avatar scelto accanto al nome — e l'animazione
   finale con gli animaletti che "esplodono" a schermo.

In ogni livello e' presente un bottone **"Salta livello"** (in alto a
sinistra, sotto il nome del giocatore), per chi vuole passare oltre — ad
esempio se la fila e' lunga o il visitatore non e' interessato a quella
prova. Il bottone chiede prima conferma ("Sì, salta" / "Continua a
giocare"), cosi' non si salta per sbaglio con un click. Il livello
confermato come saltato non viene giocato e il punteggio finale viene
abbassato in modo molto marcato (`SKIP_RANK_PENALTY` in cima al file, di
default 100000 "secondi equivalenti"), cosi' chi salta finisce comunque
sotto chiunque abbia completato quel livello: in pratica vale zero. La
classifica segnala quante prove ha saltato ogni giocatore.

Il punteggio finale e la classifica sono salvati in `leaderboard.json`,
nella stessa cartella dello script, e persistono tra una partita e l'altra.

## Avvio

```
pip install pygame
python3 benthos_game.py
```

Tasti/azioni:
- Click sinistro per selezionare/trascinare/rispondere
- Digitare per scrivere il nome nella schermata iniziale
- `Esc` per uscire
- Ridimensionare la finestra e' supportato (tutto si riadatta)

## Struttura delle cartelle immagini

Il gioco legge automaticamente le cartelle: aggiungere o togliere gruppi,
zone o immagini NON richiede di modificare il codice (tranne per gli
"intrusi" del livello 1, vedi sotto). Struttura attesa:

```
placeholder/
├── avatars/
│     avatar_squalo.jpg, avatar_polpo.jpg, avatar_stella.jpg,
│     avatar_delfino.jpg, avatar_tartaruga.jpg, avatar_cavalluccio.jpg
├── background/
│     sfondo.jpg                      (sfondo generico, opzionale)
├── level1_trova_intruso/
│     ├── easy/
│     │     group1/  4 immagini (1 intruso + 3 simili)
│     │     group2/  ...
│     │     ...
│     └── difficult/
│           group1/  ...
│           ...
├── level2_trascinamento/
│     ├── sfondo.jpg                  (scena con aria / acqua / fondale)
│     ├── easy/
│     │     aria_spiaggia/   immagini
│     │     colonna_acqua/   immagini
│     │     fondale/         immagini
│     └── difficult/
│           aria_acqua/      immagini (vivono sull'interfaccia aria-acqua)
│           acqua_fondale/   immagini (vivono sull'interfaccia acqua-fondale)
└── level3_quiz/
      questions_level3.json
```

Formati immagine accettati: `.jpg`, `.jpeg`, `.png`, `.webp`.
Le immagini mancanti sono sostituite automaticamente da un riquadro
colorato con le iniziali, quindi il gioco e' giocabile/testabile anche a
cartelle incomplete.

Il nome visualizzato per ogni animale viene ricavato dal nome del file:
`stella_marina_Astropecten_irregularis.jpg` diventa
"Stella marina (Astropecten irregularis)".

### Livello 1 - chi e' l'intruso di ogni gruppo?

Le cartelle non dicono da sole quale immagine sia l'intruso: va indicato
nel dizionario `INTRUDERS` in cima a `benthos_game.py`, una voce per
`(sotto-livello, nome cartella)` con il nome del file intruso (senza
estensione) e la spiegazione mostrata al giocatore dopo la risposta. Un
gruppo senza voce in `INTRUDERS` (o con un intruso che non corrisponde a
nessun file nella cartella) viene saltato in automatico, con un avviso
stampato in console.

### Livello 2 - dove si trovano le zone sullo sfondo

Le fasce verticali delle zone (aria/colonna d'acqua/fondale, e le due
interfacce) sono definite in `ZONE_BANDS` in cima al file, come frazioni
dell'altezza dell'immagine `sfondo.jpg`. Vanno corrette se le fasce del
tuo sfondo non coincidono con quelle di default (alto=aria, meta'=acqua,
basso=fondale).

## Personalizzare le domande del quiz

Le domande sono nel file `placeholder/level3_quiz/questions_level3.json`
(o, in alternativa, `questions_level3.json` accanto allo script), diviso
in due liste `easy` e `difficult`. Ogni partita ne estrae una a caso da
ciascuna lista.

## Personalizzare avatar, penalita' e tempo di feedback

Tutte le costanti principali (avatar, lunghezza massima del nome,
penalita' per errore, penalita' per un livello saltato, durata del
feedback dopo una risposta) sono in cima al file `benthos_game.py` e si
possono modificare senza toccare il resto del codice.

## Font e grafica

Il gioco cerca automaticamente, in ordine di preferenza, alcuni font
"amichevoli" installati sul sistema (elenco `PREFERRED_FONT_NAMES` in
cima al file: Poppins, Nunito, Segoe UI, Trebuchet MS, Comic Sans, ecc.)
e usa il primo che trova; se nessuno e' installato usa senza errori il
font di default di pygame. Per usare un font specifico (ad esempio un
.ttf scaricato per l'occasione) basta aggiungerne il nome in cima alla
lista `PREFERRED_FONT_NAMES`, purche' sia installato come font di
sistema.

