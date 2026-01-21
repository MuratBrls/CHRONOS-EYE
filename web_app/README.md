# CHRONOS-EYE Web Interface 🌐

Access CHRONOS-EYE through your web browser!

## Quick Start

1. **Install Dependencies** (first time only):
```powershell
.\venv\Scripts\activate
pip install fastapi uvicorn python-multipart
```

2. **Start the Server**:
```powershell
.\venv\Scripts\python.exe web_app\server.py
```

3. **Open Browser**:
Navigate to `http://localhost:8000`

## Features

✅ **Search**: Natural language search with thumbnail previews  
✅ **Index**: Add new media files to database  
✅ **Stats**: View database information  
✅ **Modern UI**: Same dark theme as desktop app

## Usage

### Search
1. Type your query (e.g., "woman walking")
2. Click "Search Locally"
3. View results with thumbnails
4. Click any result to open the file

### Indexing
1. Enter folder path (e.g., `C:\Users\...\Videos`)
2. Choose incremental or full re-index
3. Click "START INDEXING ENGINE"
4. Watch progress bar

## Tech Stack

- **Backend**: FastAPI + Python
- **Frontend**: HTML/CSS/JavaScript
- **Database**: Shared ChromaDB with desktop app
- **Models**: Auto-detected CLIP models

## Compared to Desktop App

| Feature | Desktop GUI | Web Interface |
|---------|-------------|---------------|
| Search | ✅ | ✅ |
| Indexing | ✅ | ✅ |
| Thumbnails | ✅ | ✅ |
| Interface | Tkinter | Browser |
| Access | Desktop only | Any browser |

Both versions use the **same database**, so you can index with one and search with the other!

## Stopping the Server

Press `Ctrl+C` in the terminal where the server is running.

---

**Note**: The web version requires FastAPI. Install it once, then use anytime!
