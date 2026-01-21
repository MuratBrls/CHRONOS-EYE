"""
CHRONOS-EYE Embedding Pipeline
Multimodal AI embedding generation using CLIP/SigLIP.
"""

import torch
import numpy as np
from PIL import Image
from typing import List, Optional, Union
from pathlib import Path
from transformers import CLIPProcessor, CLIPModel
from tqdm import tqdm
import warnings


class EmbeddingPipeline:
    """
    Multimodal embedding pipeline using CLIP.
    
    Features:
    - Automatic GPU detection (CUDA/MPS/CPU)
    - Model quantization (float32/float16/int8)
    - Batch processing for efficiency
    - VRAM management and model offloading
    """
    
    def __init__(self, model_name: str = "openai/clip-vit-large-patch14", device: str = "auto", quantization: str = "float16"):
        self.device = self._get_device(device) if device == "auto" else device
        self.model_name = model_name if model_name else "openai/clip-vit-large-patch14"
        self.quantization = quantization
        
        # Load CLIP model and processor
        # Defaulting to a more precise model for better detail
        model_id = self.model_name
        
        self.processor = CLIPProcessor.from_pretrained(model_id)
        self.model = CLIPModel.from_pretrained(model_id)
        
        if self.quantization == "float16" and self.device != "cpu":
            self.model = self.model.half()
            
        self.model.to(self.device)
        self.model.eval()
        
        # Common labels for zero-shot "detail" extraction
        self.common_labels = [
            "woman", "man", "child", "white background", "outdoor", "indoor",
            "black dress", "red dress", "blue shirt", "cinematic", "drone shot",
            "landscape", "portrait", "close up", "nature", "city", "night", "day"
        ]
        
        # Get embedding dimension
        self.embedding_dim = self.model.config.projection_dim
        print(f"Embedding dimension: {self.embedding_dim}")

    def get_labels_for_image(self, image: Image.Image, threshold: float = 0.2) -> List[str]:
        """Predict high-probability labels for more detail."""
        inputs = self.processor(text=self.common_labels, images=image, return_tensors="pt", padding=True).to(self.device)
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits_per_image = outputs.logits_per_image
            probs = logits_per_image.softmax(dim=1)
            
        results = []
        for i, prob in enumerate(probs[0]):
            if prob > threshold:
                results.append(self.common_labels[i])
        return results
    
    def _get_device(self, device: str) -> str:
        """Determine the best available device."""
        if device == "auto":
            if torch.cuda.is_available():
                return "cuda"
            elif torch.backends.mps.is_available():
                return "mps"
            else:
                return "cpu"
        return device
    
    def encode_images(
        self,
        image_paths: List[str],
        batch_size: int = 32,
        show_progress: bool = True
    ) -> np.ndarray:
        """
        Encode images to embeddings.
        """
        embeddings = []
        
        # Process in batches
        iterator = range(0, len(image_paths), batch_size)
        if show_progress:
            iterator = tqdm(iterator, desc="Encoding images")
        
        for i in iterator:
            batch_paths = image_paths[i:i + batch_size]
            batch_embeddings = self._encode_image_batch(batch_paths)
            embeddings.append(batch_embeddings)
        
        # Concatenate all batches
        return np.vstack(embeddings)
    
    def _encode_image_batch(self, image_paths: List[str]) -> np.ndarray:
        """Encode a batch of images."""
        images = []
        valid_indices = []
        
        for idx, path in enumerate(image_paths):
            try:
                img = Image.open(path).convert('RGB')
                images.append(img)
                valid_indices.append(idx)
            except Exception as e:
                warnings.warn(f"Failed to load image {path}: {e}")
                continue
        
        if not images:
            return np.zeros((len(image_paths), self.embedding_dim), dtype=np.float32)
        
        # Process images
        inputs = self.processor(
            images=images,
            return_tensors="pt",
            padding=True
        ).to(self.device)
        
        # Generate embeddings
        with torch.no_grad():
            image_features = self.model.get_image_features(**inputs)
            # Normalize embeddings
            image_features = image_features / image_features.norm(dim=-1, keepdim=True)
        
        # Convert to numpy
        embeddings = image_features.cpu().numpy().astype(np.float32)
        
        # Handle failed images
        if len(valid_indices) < len(image_paths):
            full_embeddings = np.zeros((len(image_paths), self.embedding_dim), dtype=np.float32)
            full_embeddings[valid_indices] = embeddings
            return full_embeddings
        
        return embeddings
    
    def encode_text(self, query: str) -> np.ndarray:
        """Encode text query to embedding."""
        inputs = self.processor(
            text=[query],
            return_tensors="pt",
            padding=True
        ).to(self.device)
        
        with torch.no_grad():
            text_features = self.model.get_text_features(**inputs)
            text_features = text_features / text_features.norm(dim=-1, keepdim=True)
        
        return text_features.cpu().numpy().astype(np.float32)
    
    def offload_model(self):
        """Offload model and clear cache."""
        print("Offloading model to CPU...")
        self.model = self.model.to('cpu')
        
        if self.device == "cuda":
            torch.cuda.empty_cache()
            torch.cuda.synchronize()
        elif self.device == "mps":
            pass
    
    def get_vram_usage(self) -> dict:
        """Get current VRAM usage statistics."""
        if self.device == "cuda":
            return {
                'allocated_gb': torch.cuda.memory_allocated() / 1e9,
                'reserved_gb': torch.cuda.memory_reserved() / 1e9,
                'device': torch.cuda.get_device_name()
            }
        return {'device': self.device, 'vram_tracking': 'not_available'}


if __name__ == "__main__":
    pipeline = EmbeddingPipeline(
        model_name="openai/clip-vit-base-patch32",
        device="auto",
        quantization="float16"
    )
    text_embedding = pipeline.encode_text("a beautiful sunset over the ocean")
    print(f"Text embedding shape: {text_embedding.shape}")
    pipeline.offload_model()
