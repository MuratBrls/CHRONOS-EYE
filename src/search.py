"""
CHRONOS-EYE Semantic Search Engine
Natural language search over indexed media files.
"""

import numpy as np
from typing import List, Optional, Dict
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from embedder import EmbeddingPipeline
from database import VectorDatabase, SearchResult


class SemanticSearch:
    """
    Semantic search engine for media files.
    
    Features:
    - Natural language queries
    - Multimodal search (text + image)
    - Metadata filtering
    - Result ranking
    """
    
    def __init__(
        self,
        database: VectorDatabase,
        embedder: EmbeddingPipeline
    ):
        """
        Initialize semantic search engine.
        
        Args:
            database: VectorDatabase instance
            embedder: EmbeddingPipeline instance
        """
        self.database = database
        self.embedder = embedder
    
    def search_text(
        self,
        query: str,
        top_k: int = 10,
        file_type: Optional[str] = None,
        min_score: float = 0.0
    ) -> List[SearchResult]:
        """
        Search using natural language text query.
        
        Args:
            query: Text description of desired content
            top_k: Number of results to return
            file_type: Optional filter ('video' or 'image')
            min_score: Minimum similarity score threshold (0-1)
        
        Returns:
            List of SearchResult objects
        """
        # Encode query to embedding
        query_embedding = self.embedder.encode_text(query)
        
        # Build metadata filter
        filter_metadata = None
        if file_type:
            filter_metadata = {'file_type': file_type}
        
        # Search database
        results = self.database.search(
            query_embedding=query_embedding,
            top_k=top_k,
            filter_metadata=filter_metadata
        )
        
        # Filter by minimum score
        if min_score > 0:
            results = [r for r in results if r.similarity_score >= min_score]
        
        return results
    
    def search_image(
        self,
        image_path: str,
        top_k: int = 10,
        file_type: Optional[str] = None,
        min_score: float = 0.0
    ) -> List[SearchResult]:
        """
        Search using a reference image.
        
        Args:
            image_path: Path to reference image
            top_k: Number of results to return
            file_type: Optional filter ('video' or 'image')
            min_score: Minimum similarity score threshold (0-1)
        
        Returns:
            List of SearchResult objects
        """
        # Encode image to embedding
        image_embedding = self.embedder.encode_images([image_path], show_progress=False)
        
        # Build metadata filter
        filter_metadata = None
        if file_type:
            filter_metadata = {'file_type': file_type}
        
        # Search database
        results = self.database.search(
            query_embedding=image_embedding,
            top_k=top_k,
            filter_metadata=filter_metadata
        )
        
        # Filter by minimum score
        if min_score > 0:
            results = [r for r in results if r.similarity_score >= min_score]
        
        return results
    
    def search_multimodal(
        self,
        text_query: Optional[str] = None,
        image_path: Optional[str] = None,
        text_weight: float = 0.5,
        top_k: int = 10,
        file_type: Optional[str] = None,
        min_score: float = 0.0
    ) -> List[SearchResult]:
        """
        Search using both text and image.
        
        Args:
            text_query: Optional text description
            image_path: Optional path to reference image
            text_weight: Weight for text (0-1), image gets (1 - text_weight)
            top_k: Number of results to return
            file_type: Optional filter ('video' or 'image')
            min_score: Minimum similarity score threshold (0-1)
        
        Returns:
            List of SearchResult objects
        """
        # Encode multimodal query
        query_embedding = self.embedder.encode_multimodal(
            text_query=text_query,
            image_path=image_path,
            text_weight=text_weight
        )
        
        # Build metadata filter
        filter_metadata = None
        if file_type:
            filter_metadata = {'file_type': file_type}
        
        # Search database
        results = self.database.search(
            query_embedding=query_embedding,
            top_k=top_k,
            filter_metadata=filter_metadata
        )
        
        # Filter by minimum score
        if min_score > 0:
            results = [r for r in results if r.similarity_score >= min_score]
        
        return results
    
    def get_similar_files(
        self,
        file_id: str,
        top_k: int = 10
    ) -> List[SearchResult]:
        """
        Find files similar to a specific indexed file.
        
        Args:
            file_id: ID of the reference file
            top_k: Number of results to return
        
        Returns:
            List of SearchResult objects
        """
        # Get the file's embedding
        file_data = self.database.get_by_id(file_id)
        
        if not file_data or not file_data['embedding']:
            raise ValueError(f"File not found in database: {file_id}")
        
        # Convert embedding to numpy array
        embedding = np.array(file_data['embedding'], dtype=np.float32)
        
        # Search for similar files
        results = self.database.search(
            query_embedding=embedding,
            top_k=top_k + 1  # +1 because the file itself will be in results
        )
        
        # Remove the query file from results
        results = [r for r in results if r.file_id != file_id][:top_k]
        
        return results


def print_search_results(results: List[SearchResult], max_display: int = 10):
    """Pretty print search results."""
    if not results:
        print("No results found.")
        return
    
    print(f"\nFound {len(results)} results:\n")
    
    for i, result in enumerate(results[:max_display]):
        print(f"{i+1}. {Path(result.file_path).name}")
        print(f"   Path: {result.file_path}")
        print(f"   Score: {result.similarity_score:.4f}")
        print(f"   Type: {result.metadata.get('file_type', 'unknown')}")
        if 'timestamp' in result.metadata:
            print(f"   Timestamp: {result.metadata['timestamp']:.2f}s")
        print()
    
    if len(results) > max_display:
        print(f"... and {len(results) - max_display} more results")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Search indexed media files")
    parser.add_argument("query", help="Search query text")
    parser.add_argument("--db-path", default="./chromadb_storage", help="Path to database")
    parser.add_argument("--top-k", type=int, default=10, help="Number of results")
    parser.add_argument("--file-type", choices=['video', 'image'], help="Filter by file type")
    parser.add_argument("--min-score", type=float, default=0.0, help="Minimum similarity score")
    
    args = parser.parse_args()
    
    print("Initializing search engine...")
    
    # Initialize database
    db = VectorDatabase(persist_directory=args.db_path)
    
    if db.count() == 0:
        print("Error: Database is empty. Please index files first.")
        sys.exit(1)
    
    # Initialize embedder
    embedder = EmbeddingPipeline(
        model_name="openai/clip-vit-base-patch32",
        device="auto",
        quantization="float16"
    )
    
    # Create search engine
    search = SemanticSearch(database=db, embedder=embedder)
    
    # Perform search
    print(f"\nSearching for: '{args.query}'")
    results = search.search_text(
        query=args.query,
        top_k=args.top_k,
        file_type=args.file_type,
        min_score=args.min_score
    )
    
    # Display results
    print_search_results(results)
