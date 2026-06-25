# AI Note Summarizer and Concept Explainer

This project is a web-based study tool for students. It accepts pasted text or uploaded `PDF` and `TXT` files, summarizes them into key bullet points, explains difficult concepts in simple language, and stores saved notes in MySQL.

## Tech Stack

- Backend: FastAPI + SQLAlchemy
- Frontend: HTML, CSS, JavaScript, Bootstrap
- AI/NLP: Hugging Face Transformers
- Database: MySQL
- File Handling: `pypdf` for PDF text extraction

## Project Structure

```text
New project/
├── app/
│   ├── api/
│   │   └── routes.py
│   ├── core/
│   │   └── config.py
│   ├── db/
│   │   └── database.py
│   ├── models/
│   │   └── note.py
│   ├── schemas/
│   │   └── note.py
│   ├── services/
│   │   ├── file_service.py
│   │   ├── note_service.py
│   │   └── nlp_service.py
│   ├── static/
│   │   ├── app.js
│   │   └── styles.css
│   ├── templates/
│   │   └── index.html
│   └── main.py
├── sql/
│   └── schema.sql
├── uploads/
│   └── .gitkeep
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

## Setup

1. Create and activate a virtual environment.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

2. Install the required packages.

```powershell
pip install -r requirements.txt
```

3. Create a MySQL database named `note_summarizer`.

4. Run the schema file inside MySQL.

```sql
SOURCE sql/schema.sql;
```

5. Copy `.env.example` to `.env` and update the database credentials if needed.

```powershell
Copy-Item .env.example .env
```

6. Start the application.

```powershell
uvicorn app.main:app --reload
```

7. Open the application in your browser.

```text
http://127.0.0.1:8000
```

## API Endpoints

- `POST /summarize` - summarize text into bullet points
- `POST /explain` - explain difficult concepts in simple language
- `POST /upload` - upload `PDF` or `TXT` files and extract text
- `POST /save` - store a note, its summary, and explanation
- `GET /history` - fetch previously saved notes

## Notes

- The first time the summarizer runs, Hugging Face may download the model.
- If the transformer model is unavailable, the app uses a simpler extractive summary fallback so the feature still works.
- Uploaded files are saved in the `uploads/` folder.
