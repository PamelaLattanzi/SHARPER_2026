# Elenco immagini da aggiungere (il gioco funziona anche senza: le
# immagini mancanti sono sostituite da un riquadro colorato con le
# iniziali del nome file)

Formato consigliato: JPG o PNG, quadrato o comunque non troppo
allungato, min. 500x500 px. Le cartelle dei gruppi/zone vengono lette
automaticamente: si puo' aggiungere o togliere gruppi, zone o immagini
senza toccare il codice (tranne per gli "intrusi" del livello 1, vedi
sotto). Estensioni accettate: `.jpg`, `.jpeg`, `.png`, `.webp`.

## placeholder/avatars/
- avatar_squalo.jpg
- avatar_polpo.jpg
- avatar_stella.jpg
- avatar_delfino.jpg
- avatar_tartaruga.jpg
- avatar_cavalluccio.jpg

## placeholder/background/
- sfondo.jpg   (sfondo generico per le schermate fuori dal livello 2;
  opzionale: se assente viene usato un gradiente blu "oceano" generato
  automaticamente)

## placeholder/level1_trova_intruso/  (trova l'intruso, 4 immagini a gruppo)

### easy/
- group1 -> cetriolo_di_mare.jpg, orata.jpg, polichete_Diopatra_neapolitana.jpg, stella_marina_Astropecten_irregularis.jpg
- group2 -> delfino.jpg, mobula.jpg, squalo_bianco.jpg, tonno.jpg
- group3 -> gorgonia.jpg, occhiata.jpg, riccio.jpg, spugna.jpg
- group4 -> cefalo.jpg, occhiata.jpg, riccio.jpg, sarago.jpg
- group5 -> granchio_corridore.jpg, mazzancolla.jpg, tartaruga.jpg, verdesca.jpg

### difficult/
- group1 -> aragosta.jpg, granceola.jpg, granchio_blu.jpg, panocchia.jpg
- group2 -> ulva.jpg, cystoseira.jpg, padina.jpg, posidonia.jpg
- group3 -> anemone.jpg, cystoseira.jpg, gorgonia.jpg, spirografo.jpg
- group4 -> cozza.jpg, lepre_di_mare.jpg, polpo.jpg, spugna.jpg
- group5 -> boga.jpg, cefalo.jpg, occhiata.jpg, pesce_scorpione.jpg

**IMPORTANTE**: per ogni gruppo va anche indicato QUALE immagine e'
l'intruso e PERCHE', nel dizionario `INTRUDERS` in cima a
`benthos_game.py`. Nel codice ho gia' inserito un tentativo di risposta
dedotto dai nomi dei file: vanno rivisti e corretti, in particolare
`easy/group5` e `difficult/group5`. Un gruppo senza intruso indicato (o
con un intruso il cui nome file non esiste nella cartella) viene escluso
dal gioco in automatico.

## placeholder/level2_trascinamento/

- **sfondo.jpg** — immagine della scena per la sfida FACILE, con le tre
  fasce (aria/spiaggia in alto, colonna d'acqua al centro, fondale in
  basso). Su questa immagine vengono disegnate le zone di trascinamento.
- **sfondo2.jpg** — immagine della scena per la sfida DIFFICILE, con due
  sole fasce (aria-acqua in alto, acqua-fondale in basso) — stessa
  identica meccanica della sfida facile, solo con due zone invece di tre.

### easy/ (aria/spiaggia - colonna d'acqua - fondale, su sfondo.jpg)
- aria_spiaggia -> berta.jpg, cormorano.jpg, gabbiano.jpg
- colonna_acqua -> delfino.jpg, medusa.jpg, occhiata.jpg, squalo_bianco.jpg
- fondale -> canestrello.jpg, cetriolo_di_mare.jpg, gorgonia.jpg, polichete_Diopatra_neapolitana.jpg, posidonia.jpg, riccio.jpg, spirografo.jpg, tellina.jpg

### difficult/ (aria-acqua - acqua-fondale, su sfondo2.jpg)
- acqua_fondale -> granchio_blu.jpg, mazzancolla.jpg, murena.jpg, polpo.jpg, seppia.jpg, sogliola.jpg, triglia.jpg
- aria_acqua -> caravella_portoghese.jpg, foca_monaca.jpg, tartaruga.jpg, velella.jpg

Nota: nel codice, `L2_MAX_PER_ZONE` limita quanti animali per zona
vengono estratti a caso a ogni partita (di default 3 per la sfida facile
e 4 per la difficile, cosi' il livello non diventa troppo lungo);
mettilo a `None` per usarli sempre tutti.

## placeholder/level3_quiz/
- questions_level3.json — due liste, `easy` e `difficult`; ogni partita
  ne estrae una domanda a caso da ciascuna.

## Note

- Le immagini del livello 2 vengono riusate anche per l'animazione finale
  a particelle (gli animaletti che "esplodono" a fine partita).
- Se vuoi cambiare le domande del quiz, modifica
  `placeholder/level3_quiz/questions_level3.json`.
- Se vuoi cambiare le fasce (altezza) delle zone del livello 2 sullo
  sfondo, modifica `ZONE_BANDS` in cima a `benthos_game.py`.
- Il bottone "Salta livello" (in alto a sinistra durante ogni livello,
  con richiesta di conferma) fa passare al livello successivo senza
  giocarlo, assegnando una penalita' molto marcata sul punteggio finale
  (`SKIP_RANK_PENALTY`, cima al file) che lo rende sostanzialmente nullo.
- Durante il gioco e' visibile un timer ("Tempo: m:ss") in alto a
  destra; si ferma automaticamente durante i feedback/spiegazioni.
- La spiegazione del livello 1 resta a schermo piu' a lungo che in
  passato (`L1_FEEDBACK_MS`, cima al file, di default 5000 ms) per dare
  tempo di leggerla con calma.
- Sulle schermate introduttive di ogni livello, le frecce "<" e ">"
  permettono di tornare al livello precedente (rigiocandolo da capo) o
  di saltare subito al successivo, senza dover prima iniziare a
  giocare.
