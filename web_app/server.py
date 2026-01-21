"""
CHRONOS-EYE Web Server
FastAPI backend for browser-based interface.
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
from pathlib import Path
import sys
import os
import io
from typing import Optional, List
from PIL import Image
import cv2

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.database import VectorDatabase
from src.embedder import EmbeddingPipeline
from src.search import SemanticSearch
from index import ChronosIndexer

app = FastAPI(title="CHRONOS-EYE Web")

# Global state
db_path = project_root / "chromadb_storage"
db = VectorDatabase(persist_directory=str(db_path))
embedder = None
search_engine = None
indexing_status = {"active": False, "progress": 0, "message": "Ready"}

# Models
class SearchRequest(BaseModel):
    query: str
    top_k: int = 20
    min_score: float = 0.2

class IndexRequest(BaseModel):
    folder_path: str
    incremental: bool = True
    quantization: str = "float16"

# Serve static files
app.mount("/static", StaticFiles(directory=str(Path(__file__).parent / "static")), name="static")

@app.get("/")
async def root():
    """Serve the main HTML page."""
    return FileResponse(str(Path(__file__).parent / "static" / "index.html"))

@app.get("/api/stats")
async def get_stats():
    """Get database statistics."""
    stats = db.get_stats()
    return {
        "total_items": stats['count'],
        "embedding_dim": stats['embedding_dim'],
        "collection": stats['collection_name']
    }

@app.post("/api/search")
async def search(request: SearchRequest):
    """Search for media files."""
    global embedder, search_engine
    
    try:
        # Initialize search engine if needed
        if not search_engine:
            if not embedder:
                # Auto-detect model from database
                stats = db.get_stats()
                dim = stats.get('embedding_dim', 'auto')
                model_name = "openai/clip-vit-base-patch32" if dim == 512 else "openai/clip-vit-large-patch14"
                embedder = EmbeddingPipeline(model_name=model_name, device="auto")
            search_engine = SemanticSearch(db, embedder)
        
        # Perform search
        results = search_engine.search_text(
            query=request.query,
            top_k=request.top_k,
            min_score=request.min_score
        )
        
        # Format results
        formatted_results = []
        for res in results:
            formatted_results.append({
                "id": res.file_id,
                "filename": Path(res.file_path).name,
                "score": round(res.similarity_score * 100, 1),
                "path": res.file_path,
                "metadata": res.metadata
            })
        
        return {"results": formatted_results, "count": len(formatted_results)}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/thumbnail/{file_id}")
async def get_thumbnail(file_id: str):
    """Get thumbnail for a file."""
    try:
        # Get file info from database
        file_data = db.get_by_id(file_id)
        if not file_data:
            raise HTTPException(status_code=404, detail="File not found")
        
        file_path = file_data['metadata']['file_path']
        
        # Generate thumbnail
        if file_path.lower().endswith(('.mp4', '.mov', '.avi', '.mkv', '.webm')):
            # Extract first frame from video
            cap = cv2.VideoCapture(file_path)
            ret, frame = cap.read()
            cap.release()
            if ret:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame_rgb)
            else:
                raise HTTPException(status_code=500, detail="Could not extract frame")
        else:
            # Load image
            img = Image.open(file_path)
        
        # Resize to thumbnail
        img.thumbnail((80, 80), Image.Resampling.LANCZOS)
        
        # Convert to bytes
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        
        return StreamingResponse(img_byte_arr, media_type="image/png")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/index")
async def start_indexing(request: IndexRequest, background_tasks: BackgroundTasks):
    """Start indexing a folder."""
    global indexing_status
    
    if indexing_status["active"]:
        raise HTTPException(status_code=400, detail="Indexing already in progress")
    
    # Start indexing in background
    background_tasks.add_task(index_worker, request)
    return {"message": "Indexing started"}

def index_worker(request: IndexRequest):
    """Background worker for indexing."""
    global indexing_status, embedder
    
    try:
        indexing_status = {"active": True, "progress": 0, "message": "Initializing..."}
        
        # Auto-detect model
        stats = db.get_stats()
        dim = stats.get('embedding_dim', 'auto')
        model_name = "openai/clip-vit-base-patch32" if dim == 512 else "openai/clip-vit-large-patch14"
        
        indexer = ChronosIndexer(
            root_path=request.folder_path,
            db_path=str(db_path),
            model_name=model_name,
            quantization=request.quantization
        )
        
        initial_count = db.count()
        indexing_status = {"active": True, "progress": 50, "message": "Indexing..."}
        
        indexer.index_directory(incremental=request.incremental)
        
        final_count = db.count()
        new_items = final_count - initial_count
        
        indexing_status = {
            "active": False,
            "progress": 100,
            "message": f"Complete! Added {new_items} items. Total: {final_count}"
        }
    
    except Exception as e:
        indexing_status = {"active": False, "progress": 0, "message": f"Error: {str(e)}"}

@app.get("/api/progress")
async def get_progress():
    """Get indexing progress."""
    return indexing_status

@app.get("/api/open/{file_id}")
async def open_file(file_id: str):
    """Open a file (returns file path for download)."""
    file_data = db.get_by_id(file_id)
    if not file_data:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_path = file_data['metadata']['file_path']
    
    # For Windows, open with default app
    os.startfile(file_path)
    
    return {"message": f"Opening {Path(file_path).name}"}

if __name__ == "__main__":
    import uvicorn
    print("🌐 Starting CHRONOS-EYE Web Server...")
    print("📍 Access at: http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
