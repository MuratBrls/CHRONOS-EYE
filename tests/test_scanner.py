"""
Unit tests for the MediaScanner class.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from scanner import MediaScanner, MediaFile


class TestMediaScanner:
    """Test suite for MediaScanner."""
    
    @pytest.fixture
    def temp_media_dir(self):
        """Create a temporary directory with sample media files."""
        temp_dir = tempfile.mkdtemp()
        temp_path = Path(temp_dir)
        
        # Create sample files
        (temp_path / "video1.mp4").write_bytes(b"fake video content 1")
        (temp_path / "video2.mov").write_bytes(b"fake video content 2")
        (temp_path / "image1.jpg").write_bytes(b"fake image content 1")
        (temp_path / "image2.png").write_bytes(b"fake image content 2")
        (temp_path / "document.txt").write_bytes(b"not a media file")
        
        # Create subdirectory with more files
        subdir = temp_path / "subfolder"
        subdir.mkdir()
        (subdir / "video3.mkv").write_bytes(b"fake video content 3")
        (subdir / "image3.webp").write_bytes(b"fake image content 3")
        
        yield temp_path
        
        # Cleanup
        shutil.rmtree(temp_dir)
    
    def test_scanner_initialization(self, temp_media_dir):
        """Test scanner initializes correctly."""
        scanner = MediaScanner(str(temp_media_dir))
        assert scanner.root_path == temp_media_dir
        assert len(scanner.all_extensions) > 0
    
    def test_path_validation_success(self, temp_media_dir):
        """Test path validation succeeds for valid directory."""
        scanner = MediaScanner(str(temp_media_dir))
        is_valid, message = scanner.validate_path()
        assert is_valid is True
        assert "success" in message.lower()
    
    def test_path_validation_nonexistent(self):
        """Test path validation fails for nonexistent directory."""
        scanner = MediaScanner("/nonexistent/path/12345")
        is_valid, message = scanner.validate_path()
        assert is_valid is False
        assert "does not exist" in message.lower()
    
    def test_scan_discovers_media_files(self, temp_media_dir):
        """Test scanner discovers all media files."""
        scanner = MediaScanner(str(temp_media_dir))
        files = scanner.scan_directory(incremental=False, verbose=False)
        
        # Should find 6 media files (4 in root, 2 in subfolder)
        assert len(files) == 6
        
        # Check file types
        video_files = [f for f in files if f.file_type == 'video']
        image_files = [f for f in files if f.file_type == 'image']
        
        assert len(video_files) == 3  # .mp4, .mov, .mkv
        assert len(image_files) == 3  # .jpg, .png, .webp
    
    def test_scan_ignores_non_media_files(self, temp_media_dir):
        """Test scanner ignores non-media files."""
        scanner = MediaScanner(str(temp_media_dir))
        files = scanner.scan_directory(incremental=False, verbose=False)
        
        # document.txt should not be in results
        file_names = [Path(f.path).name for f in files]
        assert "document.txt" not in file_names
    
    def test_incremental_scanning(self, temp_media_dir):
        """Test incremental scanning skips already indexed files."""
        scanner = MediaScanner(str(temp_media_dir))
        
        # First scan
        files_first = scanner.scan_directory(incremental=False, verbose=False)
        scanner.update_ignore_file(files_first)
        
        # Second scan (incremental)
        files_second = scanner.scan_directory(incremental=True, verbose=False)
        
        # Should find 0 new files
        assert len(files_second) == 0
    
    def test_incremental_scanning_new_files(self, temp_media_dir):
        """Test incremental scanning finds new files."""
        scanner = MediaScanner(str(temp_media_dir))
        
        # First scan
        files_first = scanner.scan_directory(incremental=False, verbose=False)
        scanner.update_ignore_file(files_first)
        
        # Add a new file
        (temp_media_dir / "new_video.mp4").write_bytes(b"new video content")
        
        # Second scan (incremental)
        files_second = scanner.scan_directory(incremental=True, verbose=False)
        
        # Should find 1 new file
        assert len(files_second) == 1
        assert Path(files_second[0].path).name == "new_video.mp4"
    
    def test_file_hash_uniqueness(self, temp_media_dir):
        """Test that different files get different hashes."""
        scanner = MediaScanner(str(temp_media_dir))
        files = scanner.scan_directory(incremental=False, verbose=False)
        
        # All hashes should be unique
        hashes = [f.file_hash for f in files]
        assert len(hashes) == len(set(hashes))
    
    def test_ignore_file_persistence(self, temp_media_dir):
        """Test that ignore file persists across scanner instances."""
        # First scanner instance
        scanner1 = MediaScanner(str(temp_media_dir))
        files = scanner1.scan_directory(incremental=False, verbose=False)
        scanner1.update_ignore_file(files)
        
        # Second scanner instance (should load existing ignore file)
        scanner2 = MediaScanner(str(temp_media_dir))
        assert len(scanner2.indexed_files) == len(files)
    
    def test_get_stats(self, temp_media_dir):
        """Test get_stats returns correct information."""
        scanner = MediaScanner(str(temp_media_dir))
        files = scanner.scan_directory(incremental=False, verbose=False)
        scanner.update_ignore_file(files)
        
        stats = scanner.get_stats()
        assert stats['total_indexed'] == len(files)
        assert stats['root_path'] == str(temp_media_dir)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
