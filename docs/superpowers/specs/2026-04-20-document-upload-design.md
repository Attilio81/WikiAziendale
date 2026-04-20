# Document Upload → Procedura — Design Spec

**Data:** 2026-04-20  
**Stato:** Approvato  

---

## Obiettivo

Permettere il caricamento diretto di file Word, PDF e testo nella pagina Procedure. Il sistema estrae il testo grezzo e crea automaticamente una procedura, che viene poi compilata in wiki dall'agente AI esistente.

---

## Architettura

```
Procedures.tsx
    │  "Carica documento" button → file picker
    │  POST /api/v1/procedures/upload
    │  multipart/form-data {file, categoria?, autore?}
    ▼
Backend (api/procedures.py)
    │
    ├─ Estrazione testo:
    │   ├─ .docx  → python-docx
    │   ├─ .pdf   → pdfplumber
    │   └─ .txt   → read decode utf-8
    │
    ├─ Crea ProcedureRaw
    │   ├─ titolo = filename senza estensione (strip, title-case)
    │   └─ contenuto_md = testo estratto
    │
    └─ BackgroundTask: compile_in_background (flusso esistente)
    
    Ritorna: ProcedureRead (stesso schema esistente)
```

---

## Backend

### Modificato: `backend/app/api/procedures.py`

Nuovo endpoint aggiunto al router esistente:

```
POST /api/v1/procedures/upload
Content-Type: multipart/form-data
```

**Parametri Form:**
- `file: UploadFile` — obbligatorio, estensioni accettate: `.pdf`, `.docx`, `.txt`
- `categoria: str | None` — opzionale
- `autore: str | None` — opzionale

**Logica:**
1. Verifica estensione file — 400 se non supportata
2. Legge bytes del file in memoria
3. Estrae testo in base all'estensione:
   - `.docx`: `python-docx` → concatena paragrafi con `\n`
   - `.pdf`: `pdfplumber` → concatena testo di ogni pagina con `\n`
   - `.txt`: `content.decode('utf-8', errors='replace')`
4. Deriva `titolo` dal filename: rimuove estensione, sostituisce `-_` con spazio, `.title()`
5. Crea `ProcedureRaw` con status `pending`
6. Avvia `compile_in_background` in BackgroundTasks
7. Ritorna `ProcedureRead` con status 201

**Errori gestiti:**
- Estensione non supportata → 400 `{"detail": "Formato non supportato. Usa .pdf, .docx o .txt"}`
- Testo estratto vuoto → 400 `{"detail": "Impossibile estrarre testo dal file"}`
- Errore parsing → 422 con dettaglio eccezione

### Modificato: `backend/pyproject.toml`

Nuove dipendenze:
```toml
"python-docx>=1.1.0",
"pdfplumber>=0.11.0",
```

---

## Frontend

### Modificato: `frontend/src/pages/Procedures.tsx`

**Aggiunta UI:**
- Pulsante "Carica documento" accanto al pulsante "Nuova procedura" (header della pagina)
- `<input type="file" accept=".pdf,.docx,.txt" style={{display:'none'}} ref={fileInputRef}>`
- Click sul pulsante → `fileInputRef.current.click()`

**State aggiunto:**
```typescript
const [uploading, setUploading] = useState(false)
const fileInputRef = useRef<HTMLInputElement>(null)
```

**Handler `handleFileUpload`:**
1. Prende `event.target.files[0]`
2. Costruisce `FormData` con `file`
3. `setUploading(true)`
4. POST `multipart/form-data` a `/api/v1/procedures/upload`
5. On success: invalida React Query cache procedure → lista si aggiorna
6. On error: mostra messaggio errore inline
7. `setUploading(false)` + reset `fileInputRef.current.value = ''`

**UX del pulsante durante upload:**
- Testo cambia in "Caricamento..." 
- Pulsante disabilitato per prevenire doppio invio

### Modificato: `frontend/src/api/procedures.ts`

Nuova funzione:
```typescript
uploadProcedure(file: File, categoria?: string, autore?: string): Promise<ProcedureRead>
```

---

## Flusso dati completo

```
1. Utente clicca "Carica documento"
   └─ Si apre file picker nativo (.pdf, .docx, .txt)

2. Utente seleziona file
   └─ Frontend: POST multipart/form-data /api/v1/procedures/upload

3. Backend estrae testo dal file

4. Backend crea ProcedureRaw (status = pending)
   └─ titolo = nome file pulito
   └─ contenuto_md = testo estratto

5. BackgroundTask avvia compile_in_background
   └─ Stesso flusso di una procedura creata manualmente

6. Backend risponde ProcedureRead (201)

7. Frontend invalida cache React Query
   └─ Lista procedure si aggiorna
   └─ La nuova procedura appare con status "In attesa"

8. Compilazione avviene in background (agente AI)
   └─ Status diventa "Compilata" alla fine
```

---

## Cosa non è incluso in questo scope

- Upload multiplo (più file contemporaneamente)
- Preview del testo estratto prima della creazione
- Mapping automatico di categoria/autore dal contenuto del documento
- Supporto `.odt`, `.rtf`, altri formati
- Dimensione massima file (si può aggiungere con `UploadFile` FastAPI limit)
