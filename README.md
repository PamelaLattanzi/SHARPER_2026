# Apprendista Biologo Marino: Missione Mare - CNR Sharper Night 2026

> **English summary** — An educational Pygame game about marine benthic life,
> built for the CNR (IRBIM Ancona) stand at SHARPER Night 2026 (Ancona, Italy).
> Players pick an avatar and go through three levels: *spot the odd one out*,
> *drag each animal to its habitat* and a *quiz*, racing against the clock for
> a place on the leaderboard. The game is in Italian.
>
> ```
> pip install -r requirements.txt
> python benthos_game.py
> ```

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
   Dopo la risposta viene mostrata la spiegazione per qualche secondo,
   con tempo a sufficienza per leggerla con calma (quel tempo non conta
   nel cronometro, che infatti si ferma finche' la spiegazione e' a
   schermo).
3. **Livello 2 - Trascina**: si trascina ogni animale nella zona giusta
   dello sfondo (tasto sinistro del mouse, drag & drop). Prima la sfida
   facile (aria/spiaggia, colonna d'acqua, fondale, su `sfondo.jpg`),
   poi quella difficile (stessa identica meccanica, ma con due zone
   invece di tre, su `sfondo2.jpg`).
4. **Livello 3 - Quiz**: una domanda facile e una difficile, estratte a
   caso dall'elenco del file JSON.
5. **Risultati**: tempo totale (con penalita' per gli errori), posizione
   in classifica — con l'avatar scelto accanto al nome — e l'animazione
   finale con gli animaletti che "esplodono" a schermo.

Durante ogni sfida e' visibile in alto a destra un **timer** ("Tempo:
m:ss") che mostra il tempo trascorso: si ferma automaticamente ogni
volta che viene mostrato un feedback/spiegazione, cosi' il numero non
"salta" quando quel tempo viene escluso dal punteggio.

Nelle schermate introduttive di ogni livello, oltre al bottone **"Vai!"**
ci sono due frecce: **"<" (Livello precedente)**, per tornare
all'introduzione del livello appena concluso e rigiocarlo da capo
(cancellandone il punteggio gia' registrato), e **">" (Salta livello)**,
per passare al livello successivo senza giocare quello corrente. Non
serve conferma su queste frecce perche' il livello non e' ancora
iniziato: non si perde nulla di gia' giocato. La freccia "<" non compare
sulla schermata del Livello 1 (non c'e' un livello precedente).

In ogni livello, mentre si gioca, e' presente anche un bottone **"Salta
livello"** (in alto a sinistra, sotto il nome del giocatore), per chi
vuole passare oltre — ad esempio se la fila e' lunga o il visitatore non
e' interessato a quella prova. Il bottone chiede prima conferma ("Sì,
salta" / "Continua a giocare"), cosi' non si salta per sbaglio con un
click. Il livello confermato come saltato non viene giocato e il
punteggio finale viene abbassato in modo molto marcato
(`SKIP_RANK_PENALTY` in cima al file, di default 100000 "secondi
equivalenti"), cosi' chi salta finisce comunque sotto chiunque abbia
completato quel livello: in pratica vale zero. La classifica segnala
quante prove ha saltato ogni giocatore.

Il punteggio finale e la classifica sono salvati in `leaderboard.json`,
nella stessa cartella dello script, e persistono tra una partita e l'altra.

## Avvio

```
pip install -r requirements.txt
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
│     ├── sfondo.jpg                  (scena facile: aria / acqua / fondale)
│     ├── sfondo2.jpg                 (scena difficile: aria-acqua / acqua-fondale)
│     ├── easy/
│     │     aria_spiaggia/   immagini
│     │     colonna_acqua/   immagini
│     │     fondale/         immagini
│     └── difficult/
│           aria_acqua/      immagini (vivono nella meta' aria-acqua di sfondo2)
│           acqua_fondale/   immagini (vivono nella meta' acqua-fondale di sfondo2)
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

Le fasce verticali delle zone sono definite in `ZONE_BANDS` in cima al
file, come frazioni dell'altezza dell'immagine di sfondo: tre fasce
(aria/colonna d'acqua/fondale) per la sfida facile su `sfondo.jpg`, due
fasce (aria-acqua/acqua-fondale) per la sfida difficile su `sfondo2.jpg`
— stessa meccanica, senza sovrapposizioni ne' concetto di "interfaccia".
Vanno corrette se le fasce delle tue immagini non coincidono con quelle
di default (facile: alto=aria, meta'=acqua, basso=fondale; difficile:
meta' superiore=aria-acqua, meta' inferiore=acqua-fondale).

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

Il gioco usa il font **Source Sans Pro** (nome in `PREFERRED_FONT_NAMES`,
in cima a `benthos_game.py`), che deve essere installato come font di
sistema: si scarica gratuitamente da
[Google Fonts](https://fonts.google.com/specimen/Source+Sans+3) o da
[Adobe Fonts](https://github.com/adobe-fonts/source-sans). Se non e'
installato, il gioco parte comunque usando senza errori il font di
default di pygame. Per cambiare font basta sostituire il nome nella lista
`PREFERRED_FONT_NAMES`, purche' il nuovo font sia installato sul sistema.

## Licenza e immagini

Il codice è distribuito con licenza [MIT](LICENSE).

Le immagini nella cartella `placeholder/` provengono da archivi di foto
gratuite e libere da copyright e sono state modificate per il gioco.

La classifica (`leaderboard.json`) viene creata automaticamente alla prima
partita e non è inclusa nel repository, perché contiene i nomi dei giocatori.
