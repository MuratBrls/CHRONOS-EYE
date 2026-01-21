"""
CHRONOS-EYE Scanner Module
Scoped media crawler with incremental indexing support.
"""

import os
import hashlib
from pathlib import Path
from typing import List, Set, Dict, Optional
from dataclasses import dataclass
from datetime import datetime
import json


@dataclass
class MediaFile:
    """Represents a discovered media file."""
    path: str
    file_hash: str
    file_type: str
    size_bytes: int
    modified_time: float
    
    def to_dict(self) -> dict:
        return {
            'path': self.path,
            'file_hash': self.file_hash,
            'file_type': self.file_type,
            'size_bytes': self.size_bytes,
            'modified_time': self.modified_time
        }


class MediaScanner:
    """
    Scoped media file scanner with state tracking.
    
    Features:
    - Directory validation (read/write permissions)
    - Recursive media file discovery
    - Incremental scanning via .chronos_ignore
    - SHA-256 file hashing for unique identification
    """
    
    def __init__(
        self,
        root_path: str,
        video_extensions: Optional[List[str]] = None,
        image_extensions: Optional[List[str]] = None,
        ignore_file_name: str = ".chronos_ignore"
    ):
        """
        Initialize the media scanner.
        
        Args:
            root_path: Root directory to scan
            video_extensions: List of video file extensions (e.g., ['.mp4', '.mov'])
            image_extensions: List of image file extensions (e.g., ['.jpg', '.png'])
            ignore_file_name: Name of the ignore file for tracking indexed files
        """
        self.root_path = Path(root_path).resolve()
        self.ignore_file_name = ignore_file_name
        self.ignore_file_path = self.root_path / ignore_file_name
        
        # Default extensions
        self.video_extensions = video_extensions or [
            '.mp4', '.mov', '.mkv', '.avi', '.webm', '.flv', '.wmv', '.m4v'
        ]
        self.image_extensions = image_extensions or [
            '.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff', '.tif', '.gif'
        ]
        
        # Normalize extensions to lowercase
        self.video_extensions = [ext.lower() for ext in self.video_extensions]
        self.image_extensions = [ext.lower() for ext in self.image_extensions]
        self.all_extensions = set(self.video_extensions + self.image_extensions)
        
        # Load previously indexed files
        self.indexed_files: Set[str] = self._load_ignore_file()
    
    def validate_path(self) -> tuple[bool, str]:
        """
        Validate that the root path exists and has proper permissions.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.root_path.exists():
            return False, f"Path does not exist: {self.root_path}"
        
        if not self.root_path.is_dir():
            return False, f"Path is not a directory: {self.root_path}"
        
        # Check read permission
        if not os.access(self.root_path, os.R_OK):
            return False, f"No read permission for: {self.root_path}"
        
        # Check write permission (needed for .chronos_ignore)
        if not os.access(self.root_path, os.W_OK):
            return False, f"No write permission for: {self.root_path}"
        
        return True, "Path validated successfully"
    
    def _load_ignore_file(self) -> Set[str]:
        """Load the set of previously indexed file hashes."""
        if not self.ignore_file_path.exists():
            return set()
        
        try:
            with open(self.ignore_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return set(data.get('indexed_hashes', []))
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load ignore file: {e}")
            return set()
    
    def _save_ignore_file(self, indexed_hashes: Set[str]):
        """Save the set of indexed file hashes to the ignore file."""
        data = {
            'indexed_hashes': list(indexed_hashes),
            'last_updated': datetime.now().isoformat(),
            'total_files': len(indexed_hashes)
        }
        
        try:
            with open(self.ignore_file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except IOError as e:
            print(f"Error: Could not save ignore file: {e}")
    
    def _compute_file_hash(self, file_path: Path) -> str:
        """
        Compute SHA-256 hash of a file.
        
        For large files, only hash the first 1MB + last 1MB + file size
        to balance uniqueness with performance.
        """
        hasher = hashlib.sha256()
        file_size = file_path.stat().st_size
        
        # For small files (<10MB), hash entire content
        if file_size < 10 * 1024 * 1024:
            try:
                with open(file_path, 'rb') as f:
                    hasher.update(f.read())
            except IOError as e:
                print(f"Warning: Could not hash {file_path}: {e}")
                # Fallback: hash path + size + mtime
                hasher.update(str(file_path).encode())
                hasher.update(str(file_size).encode())
        else:
            # For large files, hash first 1MB + last 1MB + metadata
            try:
                with open(file_path, 'rb') as f:
                    # First 1MB
                    hasher.update(f.read(1024 * 1024))
                    # Seek to last 1MB
                    f.seek(-1024 * 1024, 2)
                    hasher.update(f.read(1024 * 1024))
                    # Add file size to hash
                    hasher.update(str(file_size).encode())
            except IOError as e:
                print(f"Warning: Could not hash {file_path}: {e}")
                hasher.update(str(file_path).encode())
                hasher.update(str(file_size).encode())
        
        return hasher.hexdigest()
    
    def scan_directory(
        self,
        incremental: bool = True,
        verbose: bool = True
    ) -> List[MediaFile]:
        """
        Scan the root directory for media files.
        
        Args:
            incremental: If True, skip files that are already indexed
            verbose: If True, print progress information
        
        Returns:
            List of MediaFile objects for discovered files
        """
        # Validate path first
        is_valid, message = self.validate_path()
        if not is_valid:
            raise ValueError(message)
        
        discovered_files: List[MediaFile] = []
        skipped_count = 0
        
        if verbose:
            print(f"Scanning directory: {self.root_path}")
            print(f"Incremental mode: {incremental}")
        
        # Recursively walk the directory
        for root, dirs, files in os.walk(self.root_path):
            # Skip hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for filename in files:
                file_path = Path(root) / filename
                
                # Check if file has a valid media extension
                if file_path.suffix.lower() not in self.all_extensions:
                    continue
                
                # Compute file hash
                file_hash = self._compute_file_hash(file_path)
                
                # Skip if already indexed (incremental mode)
                if incremental and file_hash in self.indexed_files:
                    skipped_count += 1
                    continue
                
                # Determine file type
                file_type = 'video' if file_path.suffix.lower() in self.video_extensions else 'image'
                
                # Create MediaFile object
                media_file = MediaFile(
                    path=str(file_path),
                    file_hash=file_hash,
                    file_type=file_type,
                    size_bytes=file_path.stat().st_size,
                    modified_time=file_path.stat().st_mtime
                )
                
                discovered_files.append(media_file)
        
        if verbose:
            print(f"Discovered {len(discovered_files)} new files")
            if incremental:
                print(f"Skipped {skipped_count} already indexed files")
        
        return discovered_files
    
    def update_ignore_file(self, media_files: List[MediaFile]):
        """
        Update the ignore file with newly indexed files.
        
        Args:
            media_files: List of MediaFile objects that have been indexed
        """
        # Add new hashes to the set
        new_hashes = {mf.file_hash for mf in media_files}
        self.indexed_files.update(new_hashes)
        
        # Save to disk
        self._save_ignore_file(self.indexed_files)
    
    def get_stats(self) -> Dict[str, int]:
        """Get statistics about indexed files."""
        return {
            'total_indexed': len(self.indexed_files),
            'root_path': str(self.root_path)
        }


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python scanner.py <directory_path>")
        sys.exit(1)
    
    scanner = MediaScanner(sys.argv[1])
    
    # Validate path
    is_valid, message = scanner.validate_path()
    print(message)
    
    if is_valid:
        # Scan for new files
        files = scanner.scan_directory(incremental=True, verbose=True)
        
        # Display results
        print("\nDiscovered files:")
        for f in files[:10]:  # Show first 10
            print(f"  {f.file_type.upper()}: {Path(f.path).name} ({f.size_bytes} bytes)")
        
        if len(files) > 10:
            print(f"  ... and {len(files) - 10} more")
        
        # Update ignore file
        if files:
            scanner.update_ignore_file(files)
            print(f"\nUpdated {scanner.ignore_file_name}")
