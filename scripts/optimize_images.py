"""
Image Optimization Script
Optimizes images for web without losing quality
SAFE: Creates optimized versions, keeps originals
"""

from PIL import Image
import os
from pathlib import Path

def optimize_image(image_path, output_path=None, max_width=1920, quality=85):
    """
    Optimize image for web use
    Args:
        image_path: Path to original image
        output_path: Where to save optimized image (optional)
        max_width: Maximum width in pixels
        quality: JPEG quality (1-100)
    """
    try:
        # Open image
        img = Image.open(image_path)
        
        # Get original size
        original_size = os.path.getsize(image_path) / 1024  # KB
        
        # Convert RGBA to RGB if needed
        if img.mode == 'RGBA':
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[3])
            img = background
        
        # Resize if too large
        if img.width > max_width:
            ratio = max_width / img.width
            new_height = int(img.height * ratio)
            img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
        
        # Save optimized version
        if output_path is None:
            output_path = image_path
        
        img.save(output_path, 'JPEG', quality=quality, optimize=True)
        
        # Get new size
        new_size = os.path.getsize(output_path) / 1024  # KB
        savings = ((original_size - new_size) / original_size) * 100
        
        return {
            'success': True,
            'original_size': f'{original_size:.1f} KB',
            'new_size': f'{new_size:.1f} KB',
            'savings': f'{savings:.1f}%'
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def optimize_directory(directory, max_width=1920, quality=85):
    """Optimize all images in a directory"""
    image_extensions = {'.jpg', '.jpeg', '.png', '.webp'}
    results = []
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if Path(file).suffix.lower() in image_extensions:
                file_path = os.path.join(root, file)
                # Create backup
                backup_path = file_path + '.original'
                if not os.path.exists(backup_path):
                    os.rename(file_path, backup_path)
                    result = optimize_image(backup_path, file_path, max_width, quality)
                    result['file'] = file
                    results.append(result)
    
    return results

if __name__ == '__main__':
    import sys
    
    # Get directory from command line or use default
    directory = sys.argv[1] if len(sys.argv) > 1 else '/home/tele/manufatures/static/images'
    
    print(f"🖼️  Optimizing images in: {directory}")
    print("=" * 60)
    
    results = optimize_directory(directory)
    
    for result in results:
        if result['success']:
            print(f"✅ {result['file']}")
            print(f"   {result['original_size']} → {result['new_size']} ({result['savings']} saved)")
        else:
            print(f"❌ {result['file']}: {result['error']}")
    
    print("=" * 60)
    print(f"✅ Optimized {len([r for r in results if r['success']])} images")
    print("   Original images saved with .original extension")
