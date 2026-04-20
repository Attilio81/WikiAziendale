# Document Upload — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Aggiungere un pulsante "Carica documento" nella pagina Procedure che permette di caricare file `.pdf`, `.docx`, `.txt` e li converte automaticamente in procedure wiki.

**Architecture:** Nuovo endpoint `POST /api/v1/procedures/upload` accetta multipart/form-data, estrae testo con `python-docx` e `pdfplumber`, crea una `ProcedureRaw` e avvia la compilazione wiki. Il frontend aggiunge un input file nascosto e un pulsante nel header della pagina Procedure.

**Tech Stack:** FastAPI `UploadFile`, python-docx 1.1, pdfplumber 0.11, React 18, TypeScript

---

## File Map

| Azione | File |
|--------|------|
| Modifica | `backend/pyproject.toml` |
| Modifica | `backend/app/api/procedures.py` |
| Modifica | `backend/tests/test_procedures.py` |
| Modifica | `frontend/src/api/procedures.ts` |
| Modifica | `frontend/src/pages/Procedures.tsx` |

---

## Task 1: Dipendenze Python

**Files:**
- Modifica: `backend/pyproject.toml`

- [ ] **Step 1: Aggiungi le dipendenze**

Apri `backend/pyproject.toml`. Nella lista `dependencies`, aggiungi dopo `"agno>=1.4.0",`:

```toml
"python-docx>=1.1.0",
"pdfplumber>=0.11.0",
```

- [ ] **Step 2: Installa**

```bash
pip install -e "backend[dev]"
```

Expected: installa `python-docx` e `pdfplumber` senza errori

- [ ] **Step 3: Commit**

```bash
git add backend/pyproject.toml
git commit -m "chore: add python-docx and pdfplumber dependencies"
```

---

## Task 2: Backend — funzioni di estrazione testo

**Files:**
- Modifica: `backend/app/api/procedures.py`
- Modifica: `backend/tests/test_procedures.py`

- [ ] **Step 1: Scrivi i test di estrazione**

Apri `backend/tests/test_procedures.py` e aggiungi in fondo:

```python
import io


def _make_docx(text: str) -> bytes:
    from docx import Document
    doc = Document()
    doc.add_paragraph(text)
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


def test_extract_txt():
    from app.api.procedures import _extract_txt
    content = b"Procedura aziendale\nPasso 1: fare qualcosa"
    result = _extract_txt(content)
    assert "Procedura aziendale" in result
    assert "Passo 1" in result


def test_extract_docx():
    from app.api.procedures import _extract_docx
    docx_bytes = _make_docx("Contenuto procedura di test")
    result = _extract_docx(docx_bytes)
    assert "Contenuto procedura di test" in result


def test_extract_docx_multiple_paragraphs():
    from app.api.procedures import _extract_docx
    from docx import Document
    doc = Document()
    doc.add_paragraph("Primo paragrafo")
    doc.add_paragraph("Secondo paragrafo")
    buf = io.BytesIO()
    doc.save(buf)
    result = _extract_docx(buf.getvalue())
    assert "Primo paragrafo" in result
    assert "Secondo paragrafo" in result


def test_derive_title_from_filename():
    from app.api.procedures import _derive_title
    assert _derive_title("ricezione-merci.pdf") == "Ricezione Merci"
    assert _derive_title("gestione_non_conformita.docx") == "Gestione Non Conformita"
    assert _derive_title("Procedura Acquisti.txt") == "Procedura Acquisti"
```

- [ ] **Step 2: Esegui — devono fallire**

```bash
cd backend
pytest tests/test_procedures.py -v -k "extract or derive_title"
```

Expected: `ImportError: cannot import name '_extract_txt'`

- [ ] **Step 3: Aggiungi le funzioni helper in `procedures.py`**

Apri `backend/app/api/procedures.py`. In cima, aggiungi questi import dopo quelli esistenti:

```python
import io
from pathlib import Path
from typing import Optional
from fastapi import UploadFile, File, Form
```

Poi aggiungi queste funzioni prima della definizione del `router`:

```python
def _extract_txt(content: bytes) -> str:
    return content.decode("utf-8", errors="replace")


def _extract_docx(content: bytes) -> str:
    from docx import Document
    doc = Document(io.BytesIO(content))
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())


def _extract_pdf(content: bytes) -> str:
    import pdfplumber
    with pdfplumber.open(io.BytesIO(content)) as pdf:
        pages = [page.extract_text() or "" for page in pdf.pages]
    return "\n".join(pages)


def _derive_title(filename: str) -> str:
    stem = Path(filename).stem
    return stem.replace("-", " ").replace("_", " ").strip().title()
```

- [ ] **Step 4: Esegui i test — devono passare**

```bash
cd backend
pytest tests/test_procedures.py -v -k "extract or derive_title"
```

Expected: 4 test PASSED

- [ ] **Step 5: Commit**

```bash
git add backend/app/api/procedures.py backend/tests/test_procedures.py
git commit -m "feat(upload): add text extraction helpers for txt, docx, pdf"
```

---

## Task 3: Backend — endpoint upload

**Files:**
- Modifica: `backend/app/api/procedures.py`
- Modifica: `backend/tests/test_procedures.py`

- [ ] **Step 1: Aggiungi test endpoint upload**

Apri `backend/tests/test_procedures.py` e aggiungi:

```python
async def test_upload_txt_creates_procedure(client):
    content = b"Procedura di magazzino\n\nPasso 1: controllare DDT\nPasso 2: firmare registro"
    resp = await client.post(
        "/api/v1/procedures/upload",
        files={"file": ("ricezione-merci.txt", content, "text/plain")},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["titolo"] == "Ricezione Merci"
    assert data["compilation_status"] == "pending"
    assert "DDT" in data["contenuto_md"]


async def test_upload_docx_creates_procedure(client):
    docx_bytes = _make_docx("Procedura di qualità per la gestione delle non conformità")
    resp = await client.post(
        "/api/v1/procedures/upload",
        files={
            "file": (
                "gestione-nc.docx",
                docx_bytes,
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["titolo"] == "Gestione Nc"
    assert data["compilation_status"] == "pending"


async def test_upload_with_categoria_and_autore(client):
    content = b"Procedura di test"
    resp = await client.post(
        "/api/v1/procedures/upload",
        files={"file": ("test.txt", content, "text/plain")},
        data={"categoria": "Qualità", "autore": "Mario Rossi"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["categoria"] == "Qualità"
    assert data["autore"] == "Mario Rossi"


async def test_upload_unsupported_format_returns_400(client):
    resp = await client.post(
        "/api/v1/procedures/upload",
        files={"file": ("document.xlsx", b"fake", "application/octet-stream")},
    )
    assert resp.status_code == 400
    assert "non supportato" in resp.json()["detail"]


async def test_upload_empty_content_returns_400(client):
    resp = await client.post(
        "/api/v1/procedures/upload",
        files={"file": ("vuoto.txt", b"   \n\n   ", "text/plain")},
    )
    assert resp.status_code == 400
    assert "estrarre testo" in resp.json()["detail"]


async def test_upload_no_api_key_returns_401(client):
    from httpx import AsyncClient, ASGITransport
    from app.main import app as test_app
    async with AsyncClient(
        transport=ASGITransport(app=test_app),
        base_url="http://test",
    ) as ac:
        resp = await ac.post(
            "/api/v1/procedures/upload",
            files={"file": ("test.txt", b"contenuto", "text/plain")},
        )
    assert resp.status_code == 401
```

- [ ] **Step 2: Esegui — devono fallire**

```bash
cd backend
pytest tests/test_procedures.py -v -k "upload"
```

Expected: FAIL con `404 Not Found` (endpoint non ancora definito)

- [ ] **Step 3: Aggiungi l'endpoint in `procedures.py`**

Apri `backend/app/api/procedures.py`. Aggiungi questo endpoint dopo il `router = APIRouter()` e prima del primo `@router.post`:

```python
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}


@router.post("/upload", response_model=ProcedureRead, status_code=status.HTTP_201_CREATED)
async def upload_procedure(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(verify_api_key),
    file: UploadFile = File(...),
    categoria: Optional[str] = Form(None),
    autore: Optional[str] = Form(None),
):
    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Formato non supportato. Usa .pdf, .docx o .txt",
        )

    content_bytes = await file.read()

    if ext == ".txt":
        testo = _extract_txt(content_bytes)
    elif ext == ".docx":
        testo = _extract_docx(content_bytes)
    else:
        testo = _extract_pdf(content_bytes)

    if not testo.strip():
        raise HTTPException(
            status_code=400,
            detail="Impossibile estrarre testo dal file",
        )

    titolo = _derive_title(file.filename or "documento")
    proc = ProcedureRaw(titolo=titolo, contenuto_md=testo, categoria=categoria, autore=autore)
    db.add(proc)
    await db.commit()
    await db.refresh(proc)
    background_tasks.add_task(compile_in_background, [proc.id], "create")
    return proc
```

- [ ] **Step 4: Esegui i test upload — devono passare**

```bash
cd backend
pytest tests/test_procedures.py -v -k "upload"
```

Expected: tutti i test upload PASSED

- [ ] **Step 5: Esegui la suite completa**

```bash
cd backend
pytest tests/ -v
```

Expected: tutti PASSED

- [ ] **Step 6: Commit**

```bash
git add backend/app/api/procedures.py backend/tests/test_procedures.py
git commit -m "feat(upload): add POST /procedures/upload endpoint"
```

---

## Task 4: Frontend — API client upload

**Files:**
- Modifica: `frontend/src/api/procedures.ts`

- [ ] **Step 1: Aggiungi la funzione `uploadProcedure`**

Apri `frontend/src/api/procedures.ts`. Aggiungi in fondo al file:

```typescript
export async function uploadProcedure(
  file: File,
  categoria?: string,
  autore?: string,
): Promise<Procedure> {
  const formData = new FormData()
  formData.append('file', file)
  if (categoria) formData.append('categoria', categoria)
  if (autore) formData.append('autore', autore)

  const res = await fetch(`${BASE_URL}/procedures/upload`, {
    method: 'POST',
    headers: {
      'X-API-Key': defaultHeaders['X-API-Key'],
    },
    body: formData,
  })
  return handleResponse<Procedure>(res)
}
```

Nota: NON includere `Content-Type` negli headers — il browser lo imposta automaticamente con il boundary corretto per multipart/form-data.

- [ ] **Step 2: Verifica TypeScript**

```bash
cd frontend
npx tsc --noEmit
```

Expected: nessun errore

- [ ] **Step 3: Commit**

```bash
git add frontend/src/api/procedures.ts
git commit -m "feat(upload): add uploadProcedure API client function"
```

---

## Task 5: Frontend — Pulsante upload in Procedures.tsx

**Files:**
- Modifica: `frontend/src/pages/Procedures.tsx`

- [ ] **Step 1: Aggiungi import e state**

Apri `frontend/src/pages/Procedures.tsx`. Aggiungi `useRef` agli import React:

```tsx
import { useState, useRef } from 'react'
```

Aggiungi `uploadProcedure` agli import API:

```tsx
import {
  fetchProcedures,
  createProcedure,
  updateProcedure,
  deleteProcedure,
  uploadProcedure,
  type Procedure,
  type ProcedureCreate,
} from '../api/procedures'
```

- [ ] **Step 2: Aggiungi state e handler dentro il componente**

Dentro la funzione `Procedures()`, dopo le dichiarazioni di state esistenti, aggiungi:

```tsx
const [uploading, setUploading] = useState(false)
const fileInputRef = useRef<HTMLInputElement>(null)

async function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
  const file = e.target.files?.[0]
  if (!file) return
  setUploading(true)
  try {
    await uploadProcedure(file)
    qc.invalidateQueries({ queryKey: ['procedures'] })
  } catch (err) {
    alert(`Errore durante il caricamento: ${err instanceof Error ? err.message : 'sconosciuto'}`)
  } finally {
    setUploading(false)
    if (fileInputRef.current) fileInputRef.current.value = ''
  }
}
```

- [ ] **Step 3: Aggiungi pulsante e input nascosto nel JSX**

Trova il pulsante "Nuova procedura" nel JSX (inizia con `<button onClick={() => open()}`). Aggiungi subito prima di esso:

```tsx
<input
  ref={fileInputRef}
  type="file"
  accept=".pdf,.docx,.txt"
  className="hidden"
  onChange={handleFileChange}
/>
<button
  onClick={() => fileInputRef.current?.click()}
  disabled={uploading}
  className="px-5 py-2.5 border border-nav text-nav text-sm font-mono hover:bg-nav hover:text-white transition-colors flex items-center gap-2 disabled:opacity-50"
  style={{ borderRadius: '2px' }}
>
  {uploading ? 'Caricamento...' : '↑ Carica documento'}
</button>
```

- [ ] **Step 4: Verifica TypeScript**

```bash
cd frontend
npx tsc --noEmit
```

Expected: nessun errore

- [ ] **Step 5: Testa manualmente**

Avvia i server con `start.bat` e verifica:
- Il pulsante "Carica documento" appare accanto a "Nuova procedura"
- Cliccando si apre il file picker filtrato su .pdf/.docx/.txt
- Selezionando un file .txt la procedura appare in lista con status "In attesa"
- Il pulsante si disabilita durante il caricamento
- Un file .xlsx mostra un alert di errore

- [ ] **Step 6: Commit e push**

```bash
git add frontend/src/pages/Procedures.tsx
git commit -m "feat(upload): add document upload button in Procedures page"
git push origin master
```
