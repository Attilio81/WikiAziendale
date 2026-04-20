# Manuale Utente — Wiki Aziendale

## Cos'è la Wiki Aziendale

Un sistema che trasforma automaticamente le procedure aziendali in una wiki organizzata e navigabile. Tu carichi le procedure nel formato che hai (anche testo grezzo), l'intelligenza artificiale le struttura e le collega tra loro.

---

## Come accedere

Apri il browser e vai su: **http://localhost:5175**

Vedrai due sezioni nella barra in alto:
- **Procedure** — dove carichi e gestisci le procedure grezze
- **Wiki** — dove leggi le pagine wiki generate dall'AI

---

## Caricare una procedura

1. Clicca su **"Procedure"** nella barra in alto
2. Clicca il pulsante **"+ Nuova procedura"** in alto a destra
3. Compila il modulo:

| Campo | Obbligatorio | Descrizione |
|-------|:---:|---------|
| **Titolo** | Sì | Nome breve della procedura (es. "Ricezione merci da fornitore") |
| **Categoria** | No | Gruppo di appartenenza (es. "Magazzino", "Qualità") |
| **Autore** | No | Chi ha scritto la procedura |
| **Contenuto** | Sì | Il testo completo della procedura |
| **Tag** | No | Parole chiave separate da virgola |

4. Clicca **"Salva"**

Non preoccuparti della formattazione: l'AI sa leggere anche testi scritti in modo informale.

---

## Cosa succede dopo il salvataggio

Appena salvi una procedura, il sistema avvia in automatico la compilazione wiki. Nella lista procedure vedrai lo stato della procedura:

| Stato | Significato |
|-------|-------------|
| **In attesa** | La compilazione è in coda o in corso |
| **Compilata** | La pagina wiki è stata creata o aggiornata |
| **Errore** | La compilazione non è riuscita |

La compilazione richiede in genere da pochi secondi a qualche minuto, a seconda della lunghezza della procedura e del modello AI in uso.

---

## Leggere la wiki

1. Clicca su **"Wiki"** nella barra in alto
2. A sinistra trovi l'elenco di tutte le pagine wiki
3. Usa il campo **"Cerca pagina..."** per filtrare per nome
4. Clicca su una pagina per aprirla

Ogni pagina wiki è strutturata così:

- **Panoramica** — descrizione sintetica dell'argomento
- **Procedura** — passi numerati con responsabile e azioni
- **Documenti e moduli** — moduli, DDT, codici di riferimento
- **Vedi anche** — link cliccabili ad altre pagine correlate

---

## Aggiornare una procedura

1. Vai in **"Procedure"**
2. Clicca sull'icona di modifica nella riga della procedura
3. Modifica il contenuto e salva
4. Il sistema aggiorna automaticamente la pagina wiki corrispondente

---

## Eliminare una procedura

1. Vai in **"Procedure"**
2. Clicca sull'icona del cestino nella riga della procedura
3. Conferma l'eliminazione

La pagina wiki rimane nella wiki anche dopo l'eliminazione della procedura grezza.

---

## Ricompilare tutta la wiki

Se vuoi forzare una ricompilazione completa di tutte le pagine wiki:

1. Vai in **"Wiki"**
2. Chiedi all'amministratore di chiamare il comando di rebuild (disponibile tramite l'API)

In condizioni normali non è necessario: il sistema aggiorna la wiki in modo automatico ogni volta che una procedura viene aggiunta o modificata.

---

## Domande frequenti

**La procedura è stata salvata ma la wiki non si aggiorna — cosa faccio?**
Attendi qualche minuto. Se lo stato rimane "In attesa" per più di 5 minuti, verifica che il backend sia attivo e che LM Studio sia raggiungibile.

**L'AI ha fuso la mia procedura con un'altra — è normale?**
Sì. Se due procedure trattano lo stesso argomento, l'AI le unisce in un'unica pagina wiki più completa. È il comportamento previsto.

**Posso scrivere direttamente in Markdown?**
Sì. Il campo "Contenuto" accetta testo in formato Markdown. Ma anche testo normale va benissimo.

**Chi può accedere al sistema?**
Chiunque abbia l'URL e la chiave API configurata. Chiedi all'amministratore.

---

## Contatti

Per problemi tecnici, contattare il team IT o l'amministratore del sistema.
