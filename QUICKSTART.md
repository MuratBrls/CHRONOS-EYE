# CHRONOS-EYE Quick Start Guide

## Installation

1. **Create virtual environment**
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure settings** (optional)
   ```bash
   copy .env.template .env
   # Edit .env to customize model, GPU settings, etc.
   ```

## Usage

### 1. Index Your Media Library

```bash
python index.py "C:\path\to\your\media\folder"
```

**Options:**
- `--db-path`: Database location (default: `./chromadb_storage`)
- `--model`: CLIP model (default: `openai/clip-vit-base-patch32`)
- `--device`: GPU device (default: `auto`)
- `--quantization`: Model precision (default: `float16`)
- `--batch-size`: Batch size (default: `32`)
- `--max-frames`: Max frames per video (default: `30`)
- `--full-reindex`: Reindex all files (ignores `.chronos_ignore`)

**Example:**
```bash
python index.py "D:\Videos\Vacation2024" --model openai/clip-vit-large-patch14 --max-frames 50
```

### 2. Search Your Media

```bash
python src\search.py "sunset over the ocean"
```

**Options:**
- `--db-path`: Database location
- `--top-k`: Number of results (default: `10`)
- `--file-type`: Filter by type (`video` or `image`)
- `--min-score`: Minimum similarity score (0-1)

**Examples:**
```bash
# Find drone shots
python src\search.py "aerial drone shot of city skyline" --top-k 20

# Find only videos
python src\search.py "cinematic sunset" --file-type video

# High-confidence results only
python src\search.py "mountain landscape" --min-score 0.7
```

## Workflow

1. **Initial Indexing**: Run `index.py` on your media directory
2. **Incremental Updates**: Re-run `index.py` to index new files only
3. **Search**: Use `search.py` with natural language queries
4. **Batch Rename** (coming soon): Select search results for AI-powered renaming

## Performance Tips

- **GPU Memory**: Use `--quantization float16` for 12GB VRAM, `int8` for 6GB
- **Large Libraries**: Process in batches by indexing subdirectories separately
- **Video Processing**: Adjust `--max-frames` based on video length (30 for short clips, 100+ for long videos)

## Troubleshooting

**"No module named 'scenedetect'"**
- Scene detection is optional. The system will fall back to fixed-interval sampling.
- To enable: `pip install scenedetect[opencv]`

**CUDA out of memory**
-   Reduce `--batch-size` (try 16 or 8)
-   Use `--quantization int8`
-   Use smaller model: `openai/clip-vit-base-patch32`

**Search returns no results**
-   Check database has been populated: Look for `chromadb_storage/` directory
-   Try broader queries: "landscape" instead of "sunset over mountain lake at golden hour"
-   Lower `--min-score` threshold

## Future Ideas (Phase D+)

Advanced features for power users:

- Time-based filtering (search within date ranges)
- Multi-modal search (text + image example)
- Batch operations on search results
- Add audio transcription for searching spoken words
- Build GUI for visual search interface
