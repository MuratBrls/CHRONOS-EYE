"""
Build script to package CHRONOS-EYE as a standalone executable.
"""
import PyInstaller.__main__
import os
import sys
from pathlib import Path

# Project root
root = Path(__file__).parent

def build():
    print("🚀 Starting CHRONOS-EYE Build Process...")
    
    # Define arguments
    args = [
        'main_gui.py',              # Entry point
        '--name=CHRONOS-EYE',       # Name of the EXE
        '--onefile',                # Single file executable
        '--windowed',               # No console window
        '--clean',                  # Clean cache
        # Hidden imports for AI libraries
        '--hidden-import=transformers',
        '--hidden-import=torch',
        '--hidden-import=chromadb',
        '--hidden-import=chromadb.telemetry.product.posthog',
        '--hidden-import=chromadb.api.segmentation',
        '--hidden-import=chromadb.api.shared_system_client',
        '--hidden-import=chromadb.api.rust',
        '--hidden-import=chromadb.migrations',
        '--hidden-import=PIL',
        '--hidden-import=cv2',
        '--hidden-import=numpy',
        '--hidden-import=scenedetect',
        # Data files
        f'--add-data=.env.template;.',
        f'--add-data=src;src',
        f'--add-data=utils;utils',
    ]

    # Run PyInstaller
    PyInstaller.__main__.run(args)
    
    print("\n✅ Build complete! You can find the EXE in the 'dist' folder.")

if __name__ == "__main__":
    build()
