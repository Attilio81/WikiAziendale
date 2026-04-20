# Come funziona la Wiki Aziendale con IA

## Il problema che risolve

Le procedure aziendali spesso esistono come documenti Word, PDF o testi sparsi, scritti in momenti diversi da persone diverse. Trovarle, capirle e tenerle aggiornate è faticoso. Questo sistema le trasforma automaticamente in una wiki navigabile, chiara e sempre coerente.

---

## Il flusso in tre passi

### 1. Carichi una procedura grezza

Inserisci nel sistema una procedura aziendale così com'è: un testo grezzo, anche scritto male, anche parziale. Per esempio:

> "Quando arriva un pacco dal fornitore, Mario del magazzino controlla la bolla e firma il registro. Se manca qualcosa chiama l'ufficio acquisti..."

Il sistema la salva e la mette in coda per l'elaborazione.

---

### 2. L'intelligenza artificiale la trasforma in una pagina wiki

Appena la procedura viene caricata, un agente IA entra in azione in automatico. L'agente:

- **Legge** la procedura grezza
- **Controlla** se esiste già una pagina wiki sull'argomento
- **Decide** se creare una nuova pagina o arricchire quella esistente — procedure simili vengono fuse insieme
- **Scrive** una pagina strutturata con: panoramica, passi numerati, responsabili, documenti coinvolti
- **Collega** la pagina ad altre pagine correlate nella wiki

Tutto questo avviene in background, senza che tu debba fare nulla.

---

### 3. La wiki è pronta per essere consultata

Il risultato è una wiki navigabile dove ogni pagina copre un argomento completo. Un dipendente può aprire la pagina "Ricezione merci", leggere i passi da seguire, e trovare link a pagine correlate come "Gestione non conformità" o "Reso a fornitore".

---

## Cosa non fa il sistema

- **Non inventa informazioni**: scrive solo ciò che c'è nelle procedure caricate
- **Non sostituisce il giudizio umano**: la pagina wiki è uno strumento di consultazione, non una norma legale
- **Non usa un motore di ricerca interno**: la conoscenza è già tutta nella wiki, organizzata per argomento

---

## Struttura di una pagina wiki

Ogni pagina generata ha sempre la stessa forma:

| Sezione | Contenuto |
|---|---|
| **Panoramica** | Cos'è e a cosa serve l'argomento (2-3 frasi) |
| **Procedura** | Passi numerati con responsabile e azioni |
| **Documenti e moduli** | Moduli, DDT, codici di riferimento (es. NC-01) |
| **Vedi anche** | Link ad altre pagine correlate |

---

## Cosa succede quando aggiorni una procedura

Se carichi una versione aggiornata di una procedura già esistente, l'agente IA rileva il cambiamento e aggiorna automaticamente la pagina wiki corrispondente. L'indice della wiki viene ricostruito di conseguenza.

---

## In sintesi

```
Procedura grezza  →  Agente IA  →  Pagina wiki strutturata
     (testo)           (LLM)          (navigabile e collegata)
```

L'obiettivo è che un nuovo dipendente possa aprire la wiki e capire come funziona l'azienda senza dover cercare tra file e cartelle.
