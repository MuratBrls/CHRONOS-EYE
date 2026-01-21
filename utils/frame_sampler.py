"""
CHRONOS-EYE Frame Sampler
Intelligent video frame extraction using scene detection.
"""

import cv2
import numpy as np
from pathlib import Path
from typing import List, Tuple, Optional
from dataclasses import dataclass
import warnings

try:
    from scenedetect import VideoManager, SceneManager
    from scenedetect.detectors import ContentDetector
    SCENEDETECT_AVAILABLE = True
except ImportError:
    SCENEDETECT_AVAILABLE = False
    warnings.warn("PySceneDetect not installed. Scene detection will not be available.")


@dataclass
class SampledFrame:
    """Represents a sampled video frame."""
    frame_data: np.ndarray
    timestamp: float  # in seconds
    frame_number: int


class FrameSampler:
    """
    Intelligent video frame sampler.
    
    Supports two methods:
    1. Scene detection (primary): Extract keyframes when scenes change
    2. Fixed interval (fallback): Extract frames at regular intervals
    """
    
    def __init__(
        self,
        method: str = "scene_detect",
        fps: float = 1.0,
        scene_threshold: float = 27.0,
        min_scene_length: int = 15
    ):
        """
        Initialize frame sampler.
        
        Args:
            method: Sampling method ('scene_detect' or 'fixed_interval')
            fps: Frames per second for fixed_interval method
            scene_threshold: Threshold for scene detection (0-100, higher = less sensitive)
            min_scene_length: Minimum frames between scene changes
        """
        self.method = method
        self.fps = fps
        self.scene_threshold = scene_threshold
        self.min_scene_length = min_scene_length
        
        if method == "scene_detect" and not SCENEDETECT_AVAILABLE:
            warnings.warn("Scene detection requested but PySceneDetect not available. Falling back to fixed_interval.")
            self.method = "fixed_interval"
    
    def sample_video(
        self,
        video_path: str,
        max_frames: Optional[int] = None
    ) -> List[SampledFrame]:
        """
        Sample frames from a video file.
        
        Args:
            video_path: Path to video file
            max_frames: Maximum number of frames to extract (None = no limit)
        
        Returns:
            List of SampledFrame objects
        """
        video_path = Path(video_path)
        
        if not video_path.exists():
            raise FileNotFoundError(f"Video not found: {video_path}")
        
        if self.method == "scene_detect":
            return self._sample_scene_detect(str(video_path), max_frames)
        else:
            return self._sample_fixed_interval(str(video_path), max_frames)
    
    def _sample_scene_detect(
        self,
        video_path: str,
        max_frames: Optional[int]
    ) -> List[SampledFrame]:
        """Sample frames using scene detection."""
        # Detect scenes
        scene_list = self._detect_scenes(video_path)
        
        if not scene_list:
            warnings.warn(f"No scenes detected in {video_path}. Falling back to fixed interval.")
            return self._sample_fixed_interval(video_path, max_frames)
        
        # Extract frames at scene boundaries
        frames = []
        cap = cv2.VideoCapture(video_path)
        video_fps = cap.get(cv2.CAP_PROP_FPS)
        
        for idx, (start_frame, end_frame) in enumerate(scene_list):
            if max_frames and len(frames) >= max_frames:
                break
            
            # Extract frame at scene start
            cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
            ret, frame = cap.read()
            
            if ret:
                # Convert BGR to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                timestamp = start_frame / video_fps
                
                sampled_frame = SampledFrame(
                    frame_data=frame_rgb,
                    timestamp=timestamp,
                    frame_number=start_frame
                )
                frames.append(sampled_frame)
        
        cap.release()
        return frames
    
    def _detect_scenes(self, video_path: str) -> List[Tuple[int, int]]:
        """Detect scene changes in video."""
        if not SCENEDETECT_AVAILABLE:
            return []
        
        try:
            # Create video manager
            video_manager = VideoManager([video_path])
            scene_manager = SceneManager()
            
            # Add content detector
            scene_manager.add_detector(
                ContentDetector(
                    threshold=self.scene_threshold,
                    min_scene_len=self.min_scene_length
                )
            )
            
            # Start video manager
            video_manager.set_downscale_factor()
            video_manager.start()
            
            # Detect scenes
            scene_manager.detect_scenes(frame_source=video_manager)
            
            # Get scene list
            scene_list = scene_manager.get_scene_list()
            
            # Convert to frame numbers
            scenes = [(scene[0].get_frames(), scene[1].get_frames()) 
                     for scene in scene_list]
            
            video_manager.release()
            
            return scenes
            
        except Exception as e:
            warnings.warn(f"Scene detection failed: {e}")
            return []
    
    def _sample_fixed_interval(
        self,
        video_path: str,
        max_frames: Optional[int]
    ) -> List[SampledFrame]:
        """Sample frames at fixed intervals."""
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            raise ValueError(f"Could not open video: {video_path}")
        
        video_fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Calculate frame interval
        frame_interval = int(video_fps / self.fps)
        
        frames = []
        frame_number = 0
        
        while True:
            ret, frame = cap.read()
            
            if not ret:
                break
            
            # Sample at intervals
            if frame_number % frame_interval == 0:
                # Convert BGR to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                timestamp = frame_number / video_fps
                
                sampled_frame = SampledFrame(
                    frame_data=frame_rgb,
                    timestamp=timestamp,
                    frame_number=frame_number
                )
                frames.append(sampled_frame)
                
                if max_frames and len(frames) >= max_frames:
                    break
            
            frame_number += 1
        
        cap.release()
        return frames
    
    def extract_frame_at_timestamp(
        self,
        video_path: str,
        timestamp: float
    ) -> Optional[np.ndarray]:
        """
        Extract a single frame at a specific timestamp.
        
        Args:
            video_path: Path to video file
            timestamp: Time in seconds
        
        Returns:
            Frame as RGB numpy array, or None if extraction fails
        """
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            return None
        
        # Set position to timestamp
        cap.set(cv2.CAP_PROP_POS_MSEC, timestamp * 1000)
        
        ret, frame = cap.read()
        cap.release()
        
        if ret:
            return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return None
    
    def get_video_info(self, video_path: str) -> dict:
        """Get basic video information."""
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            raise ValueError(f"Could not open video: {video_path}")
        
        info = {
            'fps': cap.get(cv2.CAP_PROP_FPS),
            'total_frames': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
            'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            'duration_seconds': cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS)
        }
        
        cap.release()
        return info


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python frame_sampler.py <video_path>")
        sys.exit(1)
    
    video_path = sys.argv[1]
    
    # Test scene detection
    print("Testing scene detection method...")
    sampler_scene = FrameSampler(method="scene_detect", scene_threshold=27.0)
    
    try:
        info = sampler_scene.get_video_info(video_path)
        print(f"\nVideo info:")
        print(f"  Duration: {info['duration_seconds']:.2f}s")
        print(f"  FPS: {info['fps']:.2f}")
        print(f"  Resolution: {info['width']}x{info['height']}")
        
        frames = sampler_scene.sample_video(video_path, max_frames=10)
        print(f"\nExtracted {len(frames)} frames using scene detection")
        
        for i, frame in enumerate(frames[:5]):
            print(f"  Frame {i+1}: timestamp={frame.timestamp:.2f}s, shape={frame.frame_data.shape}")
    
    except Exception as e:
        print(f"Error: {e}")
