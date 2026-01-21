"""
Generate sample test images for CHRONOS-EYE demo.
"""
from PIL import Image, ImageDraw, ImageFont
import os

# Create test_media directory
os.makedirs("test_media", exist_ok=True)

# Generate sample images with different themes
samples = [
    ("sunset_beach.jpg", (255, 150, 100), "Sunset Beach"),
    ("mountain_landscape.jpg", (100, 150, 200), "Mountain View"),
    ("city_skyline.jpg", (80, 80, 120), "City Skyline"),
    ("forest_path.jpg", (50, 150, 50), "Forest Path"),
    ("ocean_waves.jpg", (50, 100, 200), "Ocean Waves"),
]

for filename, color, text in samples:
    # Create image
    img = Image.new('RGB', (800, 600), color=color)
    draw = ImageDraw.Draw(img)
    
    # Add text
    try:
        font = ImageFont.truetype("arial.ttf", 60)
    except:
        font = ImageFont.load_default()
    
    # Center text
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    position = ((800 - text_width) // 2, (600 - text_height) // 2)
    
    draw.text(position, text, fill=(255, 255, 255), font=font)
    
    # Save
    img.save(f"test_media/{filename}")
    print(f"Created: {filename}")

print("\n✅ Test images created in test_media/")
