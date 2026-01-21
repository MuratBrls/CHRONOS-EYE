"""
Standalone GUI Application for CHRONOS-EYE.
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from pathlib import Path
from typing import List, Optional
import os
import sys

# Ensure project root is in path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from src.database import VectorDatabase
from src.embedder import EmbeddingPipeline
from src.search import SemanticSearch
from index import ChronosIndexer
from src.theme import ChronosTheme, BG_DARK, BG_PANEL, ACCENT_PRIMARY, ACCENT_SUCCESS, TEXT_SECONDARY

class ChronosApp:
    """Main Standalone Application for CHRONOS-EYE."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("CHRONOS-EYE 👁️ Semantic Media Engine")
        self.root.geometry("1100x750")
        self.root.minsize(900, 600)
        
        # State
        self.db_path = project_root / "chromadb_storage"
        self.db = VectorDatabase(persist_directory=str(self.db_path))
        self.embedder = None
        self.search_engine = None
        
        # Theme
        self.theme = ChronosTheme(self.root)
        self.theme.apply()
        
        self.create_widgets()
        self.update_stats()

    def create_widgets(self):
        """Create the application layout."""
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)
        
        # --- Top Header ---
        header_frame = ttk.Frame(self.root, padding=(20, 10))
        header_frame.grid(row=0, column=0, sticky="ew")
        
        ttk.Label(header_frame, text="CHRONOS-EYE", style="Header.TLabel").pack(side="left")
        ttk.Label(header_frame, text=" v1.0 • Standalone Engine", style="Secondary.TLabel").pack(side="left", padx=10, pady=(10, 0))
        
        # Stats Bar (right side of header)
        self.stats_var = tk.StringVar(value="Database: 0 items")
        stats_label = ttk.Label(header_frame, textvariable=self.stats_var, style="Secondary.TLabel")
        stats_label.pack(side="right", pady=(10, 0))
        
        # --- Notebook (Tabs) ---
        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        
        # Tab 1: Search
        self.search_frame = ttk.Frame(self.notebook, padding=20)
        self.notebook.add(self.search_frame, text="👁️ Search Engine")
        self.setup_search_tab()
        
        # Tab 2: Indexer
        self.index_frame = ttk.Frame(self.notebook, padding=20)
        self.notebook.add(self.index_frame, text="⚡ Media Indexer")
        self.setup_index_tab()
        
        # --- Status Bar ---
        self.status_var = tk.StringVar(value="System Ready")
        status_bar = ttk.Frame(self.root, style="TFrame")
        status_bar.grid(row=2, column=0, sticky="ew")
        ttk.Label(status_bar, textvariable=self.status_var, style="Secondary.TLabel", padding=(10, 2)).pack(side="left")

    def setup_search_tab(self):
        """Build the search interface."""
        self.search_frame.columnconfigure(0, weight=1)
        self.search_frame.rowconfigure(2, weight=1)
        
        # Search Entry Block
        query_frame = ttk.Frame(self.search_frame)
        query_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        query_frame.columnconfigure(0, weight=1)
        
        self.search_entry = ttk.Entry(query_frame, font=("Segoe UI", 12))
        self.search_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.search_entry.bind("<Return>", lambda e: self.run_search())
        
        btn_search = ttk.Button(query_frame, text="Search Locally", command=self.run_search, style="Accent.TButton")
        btn_search.grid(row=0, column=1)
        
        ttk.Label(self.search_frame, text="Describe what you're looking for (e.g., 'a drone shot of mountains at sunset')", 
                  style="Secondary.TLabel").grid(row=1, column=0, sticky="w", pady=(0, 10))
        
        # Results Table
        results_frame = ttk.Frame(self.search_frame)
        results_frame.grid(row=2, column=0, sticky="nsew")
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        
        columns = ("score", "name", "tags", "path")
        self.search_tree = ttk.Treeview(results_frame, columns=columns, show="tree headings", height=8)
        
        # Configure tree column for thumbnails
        self.search_tree.column("#0", width=90, minwidth=90, stretch=False)
        self.search_tree.heading("#0", text="Preview")
        
        self.search_tree.heading("score", text="Match")
        self.search_tree.heading("name", text="Filename")
        self.search_tree.heading("tags", text="Visual Content")
        self.search_tree.heading("path", text="Location")
        
        self.search_tree.column("score", width=80, anchor="center")
        self.search_tree.column("name", width=180)
        self.search_tree.column("tags", width=220)
        self.search_tree.column("path", width=350)
        
        self.search_tree.grid(row=0, column=0, sticky="nsew")
        
        # Add double-click handler to open files
        self.search_tree.bind("<Double-Button-1>", lambda e: self.open_selected_file())
        
        
        sb_search = ttk.Scrollbar(results_frame, orient="vertical", command=self.search_tree.yview)
        sb_search.grid(row=0, column=1, sticky="ns")
        self.search_tree.configure(yscrollcommand=sb_search.set)
        
        # Search Context Actions
        actions_frame = ttk.Frame(self.search_frame, padding=(0, 15))
        actions_frame.grid(row=3, column=0, sticky="ew")
        
        ttk.Button(actions_frame, text="Open File", command=self.open_selected_file).pack(side="left", padx=5)
        ttk.Button(actions_frame, text="Open Folder", command=self.open_selected_folder).pack(side="left", padx=5)

    def setup_index_tab(self):
        """Build the indexing and management interface."""
        self.index_frame.columnconfigure(0, weight=1)
        
        # Directory Selection
        dir_frame = ttk.LabelFrame(self.index_frame, text="Scan Media Library", padding=15)
        dir_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        dir_frame.columnconfigure(1, weight=1)
        
        ttk.Label(dir_frame, text="Folder Path:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.idx_path_var = tk.StringVar()
        ttk.Entry(dir_frame, textvariable=self.idx_path_var).grid(row=0, column=1, sticky="ew", padx=(0, 10))
        ttk.Button(dir_frame, text="Browse...", command=self.browse_index_dir).grid(row=0, column=2)
        
        # Settings
        settings_frame = ttk.Frame(self.index_frame)
        settings_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        
        ttk.Label(settings_frame, text="Indexing Mode:").pack(side="left", padx=(0, 10))
        self.idx_mode_var = tk.StringVar(value="Incremental")
        ttk.Combobox(settings_frame, textvariable=self.idx_mode_var, values=["Incremental", "Full Re-index"], 
                     state="readonly", width=15).pack(side="left", padx=(0, 30))
        
        ttk.Label(settings_frame, text="VRAM Quantization:").pack(side="left", padx=(0, 10))
        self.quant_var = tk.StringVar(value="float16")
        ttk.Combobox(settings_frame, textvariable=self.quant_var, values=["float32", "float16", "int8"], 
                     state="readonly", width=10).pack(side="left")
        
        # Action Center
        action_frame = ttk.Frame(self.index_frame, padding=20, style="Panel.TFrame")
        action_frame.grid(row=2, column=0, sticky="ew")
        action_frame.columnconfigure(0, weight=1)
        
        self.idx_btn = ttk.Button(action_frame, text="START INDEXING ENGINE", command=self.run_index, style="Accent.TButton")
        self.idx_btn.grid(row=0, column=0, ipady=10)
        
        self.progress_bar = ttk.Progressbar(action_frame, mode="determinate", length=400)
        self.progress_bar.grid(row=1, column=0, pady=(20, 0), sticky="ew")
        
        self.idx_status_var = tk.StringVar(value="Waiting to scan...")
        ttk.Label(action_frame, textvariable=self.idx_status_var, style="PanelSecondary.TLabel").grid(row=2, column=0, pady=(5, 0))

    # --- Actions ---
    
    def update_stats(self):
        """Update database statistics display."""
        try:
            stats = self.db.get_stats()
            count = stats.get('count', 0)
            self.stats_var.set(f"Database: {count} media entries")
        except:
            self.stats_var.set("Database: disconnected")

    def browse_index_dir(self):
        path = filedialog.askdirectory(title="Select Media Folder to Index")
        if path:
            self.idx_path_var.set(path)

    def run_index(self):
        """Launch the indexing process in a thread."""
        path = self.idx_path_var.get()
        if not path or not os.path.exists(path):
            messagebox.showwarning("Invalid Path", "Please select a valid folder to index.")
            return
            
        self.idx_btn.config(state="disabled")
        self.idx_status_var.set("Initializing engine...")
        self.progress_bar['value'] = 0
        
        threading.Thread(target=self._index_worker, args=(path,), daemon=True).start()

    def _index_worker(self, path):
        try:
            incremental = self.idx_mode_var.get() == "Incremental"
            quant = self.quant_var.get()
            
            self.root.after(0, lambda: self.status_var.set(f"Indexing {path}..."))
            self.root.after(0, lambda: self.idx_status_var.set("Initializing indexer..."))
            
            # Auto-detect correct model based on database
            db_stats = self.db.get_stats()
            db_embedding_dim = db_stats.get('embedding_dim', 'auto')
            
            # Map embedding dimensions to model names
            if db_embedding_dim == 512:
                model_name = "openai/clip-vit-base-patch32"
                print(f"Database has 512-dim embeddings, indexer will use BASE model")
            elif db_embedding_dim == 768:
                model_name = "openai/clip-vit-large-patch14"
                print(f"Database has 768-dim embeddings, indexer will use LARGE model")
            else:
                # Default to base model for new/empty databases
                model_name = "openai/clip-vit-base-patch32"
                print(f"No existing embeddings, indexer will use BASE model (512-dim)")
            
            indexer = ChronosIndexer(
                root_path=path,
                db_path=str(self.db_path),
                model_name=model_name,
                quantization=quant
            )
            
            # Notify scan started
            self.root.after(0, lambda: self.idx_status_var.set(f"Scanning for media files... (Mode: {'Incremental' if incremental else 'Full Re-index'})"))
            self.root.after(0, lambda: self.progress_bar.start(10))
            
            # Capture initial count
            initial_count = self.db.count()
            
            indexer.index_directory(incremental=incremental)
            
            # Check if anything was actually indexed  
            final_count = self.db.count()
            new_items = final_count - initial_count
            
            if new_items == 0:
                self.root.after(0, lambda: self._index_complete_no_new_files(incremental))
            else:
                self.root.after(0, lambda: self._index_complete_with_count(new_items, final_count))
                
                
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            error_msg = str(e)  # Capture before lambda
            print(f"Indexing error details:\n{error_details}")
            self.root.after(0, lambda: messagebox.showerror("Error", f"Indexing failed:\n\n{error_msg}\n\nCheck console for details."))
            self.root.after(0, lambda: self.idx_btn.config(state="normal"))
            self.root.after(0, self.progress_bar.stop)
            self.root.after(0, lambda: self.idx_status_var.set(f"Error: {error_msg}"))


    def _index_complete_with_count(self, new_items, total_count):
        """Called when indexing completes successfully with new files."""
        self.progress_bar.stop()
        self.progress_bar['value'] = 100
        self.idx_status_var.set(f"✅ Indexing complete! Added {new_items} new items.")
        self.idx_btn.config(state="normal")
        self.status_var.set("System Ready")
        self.update_stats()
        messagebox.showinfo("Success", f"Media indexing finished successfully!\n\n{new_items} new items added.\nTotal database size: {total_count} items.")
    
    def _index_complete_no_new_files(self, was_incremental):
        """Called when scan completes but no new files were indexed."""
        self.progress_bar.stop()
        self.progress_bar['value'] = 100
        self.idx_btn.config(state="normal")
        self.status_var.set("System Ready")
        
        if was_incremental:
            msg = ("No new media files found to index.\n\n"
                   "Possible reasons:\n"
                   "• All files in this folder were already indexed\n"
                   "• No supported media files (.mp4, .jpg, .png, etc.) found\n"
                   "• Files may be in subdirectories (scanning is recursive)\n\n"
                   "To re-index existing files, switch to 'Full Re-index' mode.")
            self.idx_status_var.set("⚠️ No new files found")
        else:
            msg = ("No media files found in the selected folder.\n\n"
                   "Supported formats:\n"
                   "• Videos: .mp4, .mov, .mkv, .avi, .webm, .flv, .wmv, .m4v\n"
                   "• Images: .jpg, .jpeg, .png, .webp, .bmp, .tiff, .tif, .gif\n\n"
                   "Please select a folder containing media files.")
            self.idx_status_var.set("⚠️ No media files found")
        
        messagebox.showwarning("No Files Indexed", msg)


    def run_search(self):
        query = self.search_entry.get().strip()
        if not query:
            return
            
        self.status_var.set("AI is searching... 🧠")
        self.search_tree.delete(*self.search_tree.get_children())
        
        threading.Thread(target=self._search_worker, args=(query,), daemon=True).start()

    def _search_worker(self, query):
        try:
            # First-time model loading message
            if not self.search_engine:
                self.root.after(0, lambda: self.status_var.set("⏳ Loading AI model (first time only, ~30 seconds)..."))
                
                if not self.embedder:
                    # Auto-detect correct model based on database embedding dimension
                    db_stats = self.db.get_stats()
                    db_embedding_dim = db_stats.get('embedding_dim', 'auto')
                    
                    # Map embedding dimensions to model names
                    if db_embedding_dim == 512:
                        model_name = "openai/clip-vit-base-patch32"
                        print(f"Database has 512-dim embeddings, using BASE model")
                    elif db_embedding_dim == 768:
                        model_name = "openai/clip-vit-large-patch14"
                        print(f"Database has 768-dim embeddings, using LARGE model")
                    else:
                        # Default to base model for new databases
                        model_name = "openai/clip-vit-base-patch32"
                        print(f"No existing embeddings detected, using BASE model (512-dim)")
                    
                    print(f"Initializing CLIP model: {model_name}")
                    self.embedder = EmbeddingPipeline(model_name=model_name, device="auto")
                    print("Model loaded successfully!")
                    
                self.search_engine = SemanticSearch(self.db, self.embedder)
                self.root.after(0, lambda: self.status_var.set("AI is searching... 🧠"))
            
            
            # Search with relevance filtering
            # min_score of 0.2 means at least 20% similarity required
            results = self.search_engine.search_text(query, top_k=20, min_score=0.2)
            
            
            if not results:
                self.root.after(0, lambda: messagebox.showinfo("No Results", 
                    f"No matches found for: '{query}'\n\nTry:\n• A broader query\n• Checking if media is indexed\n• Using different keywords"))
                self.root.after(0, lambda: self.status_var.set("No results found"))
            else:
                self.root.after(0, lambda: self._display_results(results))
                
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Search error:\n{error_details}")
            self.root.after(0, lambda: messagebox.showerror("Search Error", f"Search failed:\n\n{str(e)}\n\nCheck console for details."))
            self.root.after(0, lambda: self.status_var.set("Search failed"))

    def _display_results(self, results):
        from PIL import Image, ImageTk
        import cv2
        
        # Store references to prevent garbage collection
        if not hasattr(self, 'thumbnail_images'):
            self.thumbnail_images = []
        self.thumbnail_images.clear()
        
        for res in results:
            score_pct = f"{res.similarity_score * 100:.1f}%"
            name = Path(res.file_path).name
            file_path = res.file_path
            
            # Create thumbnail
            thumbnail = None
            try:
                if file_path.lower().endswith(('.mp4', '.mov', '.avi', '.mkv', '.webm', '.flv', '.wmv', '.m4v')):
                    # Extract first frame from video
                    cap = cv2.VideoCapture(file_path)
                    ret, frame = cap.read()
                    cap.release()
                    if ret:
                        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        img = Image.fromarray(frame_rgb)
                    else:
                        img = None
                else:
                    # Load image
                    img = Image.open(file_path)
                
                if img:
                    # Resize to thumbnail
                    img.thumbnail((80, 80), Image.Resampling.LANCZOS)
                    thumbnail = ImageTk.PhotoImage(img)
                    self.thumbnail_images.append(thumbnail)  # Keep reference
            except Exception as e:
                print(f"Could not create thumbnail for {name}: {e}")
            
            # Extract Quick Tags for "detail"
            try:
                img = Image.open(file_path).convert('RGB')
                tags_list = self.embedder.get_labels_for_image(img)
                tags = ", ".join(tags_list) if tags_list else "media content"
            except:
                tags = "media content"
            
            # Insert with thumbnail if available
            item_id = self.search_tree.insert("", "end", values=(score_pct, name, tags, file_path), image=thumbnail if thumbnail else '')
        
        self.status_var.set(f"Found {len(results)} matches")

    def open_selected_file(self):
        selection = self.search_tree.selection()
        if not selection:
            messagebox.showinfo("No Selection", "Please select a file from the search results first.")
            return
        try:
            file_path = self.search_tree.item(selection[0])['values'][3]
            os.startfile(file_path)
            self.status_var.set(f"Opened: {Path(file_path).name}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not open file:\n{str(e)}")

    def open_selected_folder(self):
        selection = self.search_tree.selection()
        if not selection:
            messagebox.showinfo("No Selection", "Please select a file from the search results first.")
            return
        try:
            file_path = self.search_tree.item(selection[0])['values'][3]
            folder_path = os.path.dirname(file_path)
            os.startfile(folder_path)
            self.status_var.set(f"Opened folder: {Path(folder_path).name}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not open folder:\n{str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ChronosApp(root)
    root.mainloop()
