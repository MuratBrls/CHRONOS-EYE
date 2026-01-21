"""
CHRONOS-EYE Vector Database Manager
Local vector storage and similarity search using ChromaDB.
"""

import chromadb
from chromadb.config import Settings
import numpy as np
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import json


@dataclass
class SearchResult:
    """Represents a search result."""
    file_id: str
    file_path: str
    similarity_score: float
    metadata: dict
    
    def to_dict(self) -> dict:
        return {
            'file_id': self.file_id,
            'file_path': self.file_path,
            'similarity_score': self.similarity_score,
            'metadata': self.metadata
        }


class VectorDatabase:
    """
    Vector database manager using ChromaDB.
    
    Features:
    - Persistent local storage
    - HNSW indexing for fast similarity search
    - Metadata filtering
    - Batch operations
    """
    
    def __init__(
        self,
        persist_directory: str = "./chromadb_storage",
        collection_name: str = "chronos_media",
        embedding_dim: Optional[int] = None
    ):
        """
        Initialize vector database.
        
        Args:
            persist_directory: Directory to store database files
            collection_name: Name of the collection
            embedding_dim: Dimension of embedding vectors (auto-detected if None)
        """
        self.persist_directory = Path(persist_directory)
        self.collection_name = collection_name
        self.embedding_dim = embedding_dim
        
        # Create persist directory if it doesn't exist
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Get or create collection
        self.collection = self._get_or_create_collection()
        
        print(f"Vector database initialized at: {self.persist_directory}")
        print(f"Collection: {self.collection_name}")
    
    def _get_or_create_collection(self):
        """Get existing collection or create new one."""
        try:
            collection = self.client.get_collection(
                name=self.collection_name,
                embedding_function=None  # We provide embeddings manually
            )
            print(f"Loaded existing collection with {collection.count()} items")
        except Exception:
            collection = self.client.create_collection(
                name=self.collection_name,
                embedding_function=None,
                metadata={
                    "hnsw:space": "cosine",  # Use cosine similarity
                    "hnsw:M": 16,  # Number of connections per layer
                    "hnsw:construction_ef": 200,  # Construction time accuracy
                    "hnsw:search_ef": 100  # Search time accuracy
                }
            )
            print("Created new collection")
        
        return collection
    
    def add_embeddings(
        self,
        ids: List[str],
        embeddings: np.ndarray,
        metadatas: List[dict]
    ):
        """
        Add embeddings to the database.
        
        Args:
            ids: List of unique file IDs (SHA-256 hashes)
            embeddings: NumPy array of shape (n, embedding_dim)
            metadatas: List of metadata dictionaries
        """
        if len(ids) != len(embeddings) != len(metadatas):
            raise ValueError("ids, embeddings, and metadatas must have same length")
        
        # Auto-detect embedding dimension if not set
        if self.embedding_dim is None:
            if len(embeddings.shape) == 2:
                self.embedding_dim = embeddings.shape[1]
            else:
                self.embedding_dim = embeddings.shape[0]
            print(f"Auto-detected embedding dimension: {self.embedding_dim}")
        
        # Verify dimension matches
        expected_dim = embeddings.shape[1] if len(embeddings.shape) == 2 else embeddings.shape[0]
        if expected_dim != self.embedding_dim:
            raise ValueError(f"Embedding dimension mismatch: expected {self.embedding_dim}, got {expected_dim}")
        
        # Convert embeddings to list of lists
        embeddings_list = embeddings.tolist()
        
        # Add to collection
        self.collection.add(
            ids=ids,
            embeddings=embeddings_list,
            metadatas=metadatas
        )
        
        print(f"Added {len(ids)} embeddings to database")
    
    def search(
        self,
        query_embedding: np.ndarray,
        top_k: int = 10,
        filter_metadata: Optional[dict] = None
    ) -> List[SearchResult]:
        """
        Search for similar embeddings.
        
        Args:
            query_embedding: Query embedding vector of shape (1, embedding_dim) or (embedding_dim,)
            top_k: Number of results to return
            filter_metadata: Optional metadata filters (e.g., {'file_type': 'video'})
        
        Returns:
            List of SearchResult objects sorted by similarity
        """
        # Ensure query embedding is 2D
        if query_embedding.ndim == 1:
            query_embedding = query_embedding.reshape(1, -1)
        
        # Convert to list
        query_list = query_embedding.tolist()
        
        # Build where clause for filtering
        where = filter_metadata if filter_metadata else None
        
        # Query collection
        results = self.collection.query(
            query_embeddings=query_list,
            n_results=top_k,
            where=where
        )
        
        # Parse results
        search_results = []
        
        if results['ids'] and len(results['ids'][0]) > 0:
            for i in range(len(results['ids'][0])):
                result = SearchResult(
                    file_id=results['ids'][0][i],
                    file_path=results['metadatas'][0][i].get('file_path', ''),
                    similarity_score=1.0 - results['distances'][0][i],  # Convert distance to similarity
                    metadata=results['metadatas'][0][i]
                )
                search_results.append(result)
        
        return search_results
    
    def delete_by_id(self, file_id: str):
        """Delete an embedding by its ID."""
        try:
            self.collection.delete(ids=[file_id])
            print(f"Deleted embedding: {file_id}")
        except Exception as e:
            print(f"Error deleting {file_id}: {e}")
    
    def delete_by_filter(self, filter_metadata: dict):
        """Delete embeddings matching metadata filter."""
        try:
            self.collection.delete(where=filter_metadata)
            print(f"Deleted embeddings matching filter: {filter_metadata}")
        except Exception as e:
            print(f"Error deleting with filter: {e}")
    
    def get_by_id(self, file_id: str) -> Optional[dict]:
        """Retrieve an embedding and metadata by ID."""
        try:
            result = self.collection.get(ids=[file_id])
            if result['ids']:
                return {
                    'id': result['ids'][0],
                    'embedding': result['embeddings'][0] if result['embeddings'] else None,
                    'metadata': result['metadatas'][0] if result['metadatas'] else {}
                }
        except Exception as e:
            print(f"Error retrieving {file_id}: {e}")
        return None
    
    def count(self) -> int:
        """Get total number of embeddings in database."""
        return self.collection.count()
    
    def get_stats(self) -> dict:
        """Get database statistics."""
        # If embedding_dim is not set, try to detect it from existing data
        detected_dim = self.embedding_dim
        
        if detected_dim is None:
            try:
                count = self.count()
                if count > 0:
                    # Get one embedding to check its dimension
                    result = self.collection.get(limit=1, include=['embeddings'])
                    emb_list = result.get('embeddings', [])
                    if len(emb_list) > 0:
                        embedding = emb_list[0]
                        # Works for both list and numpy array
                        detected_dim = len(embedding)
                        print(f"Auto-detected embedding dimension from database: {detected_dim}")
            except Exception as e:
                # If detection fails, leave it as None
                print(f"Could not auto-detect embedding dimension: {e}")
        
        return {
            'count': self.count(),
            'total_embeddings': self.count(),  # Backward compatibility
            'collection_name': self.collection_name,
            'persist_directory': str(self.persist_directory),
            'embedding_dim': detected_dim if detected_dim is not None else 'auto'
        }
    
    def backup(self, backup_path: str):
        """
        Create a backup of the database.
        
        Args:
            backup_path: Path to backup directory
        """
        import shutil
        
        backup_path = Path(backup_path)
        backup_path.mkdir(parents=True, exist_ok=True)
        
        # Copy entire persist directory
        shutil.copytree(
            self.persist_directory,
            backup_path / self.persist_directory.name,
            dirs_exist_ok=True
        )
        
        print(f"Database backed up to: {backup_path}")
    
    def reset(self):
        """Reset the database (delete all data)."""
        self.client.delete_collection(name=self.collection_name)
        self.collection = self._get_or_create_collection()
        print("Database reset complete")


if __name__ == "__main__":
    # Example usage
    print("Initializing vector database...")
    
    db = VectorDatabase(
        persist_directory="./test_chromadb",
        collection_name="test_collection",
        embedding_dim=512
    )
    
    # Test adding embeddings
    print("\nAdding test embeddings...")
    test_ids = ["file1", "file2", "file3"]
    test_embeddings = np.random.rand(3, 512).astype(np.float32)
    test_metadatas = [
        {'file_path': '/path/to/video1.mp4', 'file_type': 'video'},
        {'file_path': '/path/to/image1.jpg', 'file_type': 'image'},
        {'file_path': '/path/to/video2.mp4', 'file_type': 'video'}
    ]
    
    db.add_embeddings(test_ids, test_embeddings, test_metadatas)
    
    # Test search
    print("\nTesting search...")
    query = np.random.rand(1, 512).astype(np.float32)
    results = db.search(query, top_k=2)
    
    for i, result in enumerate(results):
        print(f"Result {i+1}: {result.file_path} (score: {result.similarity_score:.4f})")
    
    # Show stats
    print(f"\nDatabase stats: {db.get_stats()}")
