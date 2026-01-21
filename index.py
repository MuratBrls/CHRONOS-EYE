"""
CHRONOS-EYE Main Indexing Pipeline
End-to-end media indexing workflow.
"""

import sys
from pathlib import Path
from typing import Optional
import tempfile
from PIL import Image
import numpy as np
from tqdm import tqdm
import os
from dotenv import load_dotenv

# Add src and utils to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))
sys.path.insert(0, str(Path(__file__).parent / 'utils'))

from scanner import MediaScanner
from embedder import EmbeddingPipeline
from database import VectorDatabase
from frame_sampler import FrameSampler


class ChronosIndexer:
    """
    Main indexing pipeline for CHRONOS-EYE.
    
    Orchestrates:
    1. Media file discovery (Scanner)
    2. Frame extraction (FrameSampler)
    3. Embedding generation (EmbeddingPipeline)
    4. Vector storage (VectorDatabase)
    """
    
    def __init__(
        self,
        root_path: str,
        db_path: str = "./chromadb_storage",
        model_name: str = "openai/clip-vit-large-patch14",
        device: str = "auto",
        quantization: str = "float16",
        sampling_method: str = "scene_detect",
        batch_size: int = 32
    ):
        """
        Initialize the indexing pipeline.
        
        Args:
            root_path: Root directory to scan for media
            db_path: Path to vector database
            model_name: CLIP model to use
            device: Device for inference
            quantization: Model quantization
            sampling_method: Frame sampling method
            batch_size: Batch size for embedding generation
        """
        self.root_path = root_path
        self.batch_size = batch_size
        
        print("=" * 60)
        print("CHRONOS-EYE Indexing Pipeline")
        print("=" * 60)
        
        # Initialize components
        print("\n[1/4] Initializing Scanner...")
        self.scanner = MediaScanner(root_path)
        
        print("\n[2/4] Initializing Embedding Pipeline...")
        self.embedder = EmbeddingPipeline(
            model_name=model_name,
            device=device,
            quantization=quantization
        )
        
        print("\n[3/4] Initializing Vector Database...")
        self.database = VectorDatabase(
            persist_directory=db_path,
            embedding_dim=self.embedder.embedding_dim
        )
        
        print("\n[4/4] Initializing Frame Sampler...")
        self.frame_sampler = FrameSampler(method=sampling_method)
        
        print("\n" + "=" * 60)
        print("Initialization complete!")
        print("=" * 60)
    
    def index_directory(
        self,
        incremental: bool = True,
        max_frames_per_video: int = 30
    ):
        """
        Index all media files in the directory.
        
        Args:
            incremental: Skip already indexed files
            max_frames_per_video: Maximum frames to extract per video
        """
        # Validate path
        is_valid, message = self.scanner.validate_path()
        if not is_valid:
            raise ValueError(message)
        
        print(f"\nScanning directory: {self.root_path}")
        print(f"Incremental mode: {incremental}\n")
        
        # Scan for media files
        media_files = self.scanner.scan_directory(
            incremental=incremental,
            verbose=True
        )
        
        if not media_files:
            print("\nNo new files to index.")
            return
        
        # Separate images and videos
        images = [f for f in media_files if f.file_type == 'image']
        videos = [f for f in media_files if f.file_type == 'video']
        
        print(f"\nProcessing {len(images)} images and {len(videos)} videos...\n")
        
        # Index images
        if images:
            self._index_images(images)
        
        # Index videos
        if videos:
            self._index_videos(videos, max_frames_per_video)
        
        # Update ignore file
        self.scanner.update_ignore_file(media_files)
        
        # Show final stats
        print("\n" + "=" * 60)
        print("Indexing Complete!")
        print("=" * 60)
        print(f"Total embeddings in database: {self.database.count()}")
        print(f"Database location: {self.database.persist_directory}")
        
        # Offload model to free VRAM
        print("\nOffloading model to free VRAM...")
        self.embedder.offload_model()
    
    def _index_images(self, images):
        """Index image files."""
        print(f"[Images] Processing {len(images)} files...")
        
        # Prepare data
        image_paths = [img.path for img in images]
        
        # Generate embeddings in batches
        embeddings = self.embedder.encode_images(
            image_paths,
            batch_size=self.batch_size,
            show_progress=True
        )
        
        # Prepare metadata
        ids = [img.file_hash for img in images]
        metadatas = [
            {
                'file_path': img.path,
                'file_type': img.file_type,
                'size_bytes': img.size_bytes,
                'modified_time': img.modified_time
            }
            for img in images
        ]
        
        # Add to database
        self.database.add_embeddings(ids, embeddings, metadatas)
    
    def _index_videos(self, videos, max_frames_per_video):
        """Index video files."""
        print(f"\n[Videos] Processing {len(videos)} files...")
        
        all_embeddings = []
        all_ids = []
        all_metadatas = []
        
        for video in tqdm(videos, desc="Extracting frames"):
            try:
                # Sample frames from video
                frames = self.frame_sampler.sample_video(
                    video.path,
                    max_frames=max_frames_per_video
                )
                
                if not frames:
                    print(f"Warning: No frames extracted from {Path(video.path).name}")
                    continue
                
                # Save frames to temp files for embedding
                temp_paths = []
                temp_dir = tempfile.mkdtemp()
                
                for i, frame in enumerate(frames):
                    temp_path = Path(temp_dir) / f"frame_{i}.jpg"
                    Image.fromarray(frame.frame_data).save(temp_path)
                    temp_paths.append(str(temp_path))
                
                # Generate embeddings
                frame_embeddings = self.embedder.encode_images(
                    temp_paths,
                    batch_size=self.batch_size,
                    show_progress=False
                )
                
                # Create IDs and metadata for each frame
                for i, frame in enumerate(frames):
                    # Use video hash + actual frame number for unique ID
                    frame_id = f"{video.file_hash}_f{frame.frame_number}"
                    metadata = {
                        'file_path': video.path,
                        'file_type': video.file_type,
                        'size_bytes': video.size_bytes,
                        'modified_time': video.modified_time,
                        'timestamp': frame.timestamp,
                        'frame_number': frame.frame_number
                    }
                    
                    all_ids.append(frame_id)
                    all_metadatas.append(metadata)
                    all_embeddings.append(frame_embeddings[i])
                
                # Cleanup temp files
                for temp_path in temp_paths:
                    os.remove(temp_path)
                os.rmdir(temp_dir)
                
            except Exception as e:
                print(f"Error processing {Path(video.path).name}: {e}")
                continue
        
        # Add all video frame embeddings to database
        if all_embeddings:
            embeddings_array = np.vstack(all_embeddings)
            self.database.add_embeddings(all_ids, embeddings_array, all_metadatas)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Index media files with CHRONOS-EYE")
    parser.add_argument("directory", help="Directory to index")
    parser.add_argument("--db-path", default="./chromadb_storage", help="Database path")
    parser.add_argument("--model", default="openai/clip-vit-base-patch32", help="CLIP model")
    parser.add_argument("--device", default="auto", help="Device (auto/cuda/mps/cpu)")
    parser.add_argument("--quantization", default="float16", help="Quantization (float32/float16/int8)")
    parser.add_argument("--batch-size", type=int, default=32, help="Batch size")
    parser.add_argument("--max-frames", type=int, default=30, help="Max frames per video")
    parser.add_argument("--full-reindex", action="store_true", help="Reindex all files (ignore .chronos_ignore)")
    
    args = parser.parse_args()
    
    # Load environment variables
    load_dotenv()
    
    # Create indexer
    indexer = ChronosIndexer(
        root_path=args.directory,
        db_path=args.db_path,
        model_name=args.model,
        device=args.device,
        quantization=args.quantization,
        batch_size=args.batch_size
    )
    
    # Run indexing
    indexer.index_directory(
        incremental=not args.full_reindex,
        max_frames_per_video=args.max_frames
    )


if __name__ == "__main__":
    main()
