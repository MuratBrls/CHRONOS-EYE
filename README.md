# CHRONOS-EYE 👁️

**AI-Powered Semantic Media Search Engine**

Search your photos and videos using natural language. Find "woman walking outdoor" instead of browsing through folders.

![CHRONOS-EYE Screenshot](https://img.shields.io/badge/Platform-Windows-blue)
![Python Version](https://img.shields.io/badge/Python-3.10+-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## ✨ Features

- 🔍 **Natural Language Search** - Search with phrases like "sunset over mountains"
- 🖼️ **Image & Video Support** - Works with photos and video files
- 🎯 **AI-Powered** - Uses OpenAI CLIP for semantic understanding
- 🖥️ **Dual Interface** - Desktop GUI (Tkinter) & Web UI (FastAPI)
- 📊 **Thumbnail Previews** - See results at a glance
- ⚡ **Fast Indexing** - Incremental indexing with GPU acceleration
- 🎨 **Modern Dark Theme** - Sleek blue/purple aesthetic

## 🚀 Quick Start

### Installation

1. **Clone the repository**:
```bash
git clone https://github.com/YOUR_USERNAME/CHRONOS-EYE.git
cd CHRONOS-EYE
```

2. **Create virtual environment**:
```bash
python -m venv venv
.\venv\Scripts\activate  # Windows
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

### Usage

**Desktop App**:
```bash
python src/app.py
```

**Web Version**:
```bash
python web_app/server.py
# Then open http://localhost:8000
```

## 📖 How It Works

1. **Index** - Point CHRONOS-EYE to your media folder
2. **AI Processing** - CLIP model creates semantic embeddings
3. **Search** - Type natural language queries
4. **Results** - Get ranked matches with thumbnails

## 🎯 Example Searches

- "woman in red dress"
- "sunset over ocean"
- "person jumping"
- "landscape mountain"
- "indoor office scene"

## 📁 Project Structure

```
CHRONOS-EYE/
├── src/              # Core backend
│   ├── app.py       # Desktop GUI
│   ├── database.py  # Vector DB
│   ├── embedder.py  # CLIP embeddings
│   └── search.py    # Search engine
├── web_app/         # Web interface
│   ├── server.py    # FastAPI backend
│   └── static/      # HTML/CSS/JS
├── index.py         # Media indexer
└── requirements.txt
```

## 🛠️ Technologies

- **AI**: OpenAI CLIP (ViT-B/32 & ViT-L/14)
- **Database**: ChromaDB (vector storage)
- **Desktop**: Python + Tkinter
- **Web**: FastAPI + Vanilla JS
- **Processing**: PyTorch, Pillow, OpenCV

## 📋 Requirements

- Python 3.10+
- CUDA-capable GPU (optional but recommended)
- 8GB+ RAM
- Windows 10/11

## 🤝 Contributing

Contributions welcome! Please feel free to submit a Pull Request.

## 📝 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- OpenAI for CLIP model
- ChromaDB for vector storage
- FastAPI for web framework

## 📧 Contact

Questions? Open an issue or reach out!

---

**Made with ❤️ for easier media management**
