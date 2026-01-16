import os
import argparse
import sys
from PIL import Image
import pillow_avif

import imageio
import numpy as np

def convert_images(input_folder, output_file, fps=24, quality=85, width=None, progress_callback=None):
    """
    Converts a sequence of PNG images in a folder to an animated AVIF, GIF, APNG, or WebM.
    
    Args:
        input_folder (str): Folder containing PNG images.
        output_file (str): Path to the output file (extension determines format).
        fps (int): Frames per second.
        quality (int): Quality (0-100).
        width (int): Target width for resizing (optional).
        progress_callback (callable): Function to call with (current, total, message).
    """
    images = []
    
    # Sort files
    try:
        files = [f for f in os.listdir(input_folder) if f.lower().endswith('.png')]
        files.sort()
    except FileNotFoundError:
        print(f"Error: Folder '{input_folder}' not found.")
        return False
    except Exception as e:
        print(f"Error accessing folder: {e}")
        return False

    if not files:
        print(f"No PNG files found in '{input_folder}'.")
        return False

    total_files = len(files)
    print(f"Found {total_files} images.")

    try:
        # Load images
        for i, file in enumerate(files):
            if progress_callback:
                progress_callback(i, total_files, f"Loading image {i+1}/{total_files}...")
            
            file_path = os.path.join(input_folder, file)
            img = Image.open(file_path)
            
            # Resize if width specified and different from original
            if width and width < img.width:
                aspect_ratio = img.height / img.width
                new_height = int(width * aspect_ratio)
                img = img.resize((width, new_height), Image.Resampling.LANCZOS)
                
            images.append(img)
        
        if not images:
             return False

        # Calculate duration per frame in milliseconds
        duration = int(1000 / fps)

        print(f"Saving to {output_file}...")
        
        ext = os.path.splitext(output_file)[1].lower()
        format_name = "AVIF"
        if ext == ".gif":
            format_name = "GIF"
        elif ext == ".png":
            format_name = "PNG" # APNG
        elif ext == ".webm":
            format_name = "WebM"
        elif ext == ".mov":
            format_name = "Safari" # HEVC
        
        if progress_callback:
            progress_callback(total_files, total_files, f"Encoding {format_name} (this may take a while)...")
            
        print(f"FPS: {fps}, Duration: {duration}ms, Quality: {quality}, Width: {width if width else 'Original'}, Format: {format_name}")

        if format_name == "WebM":
             # Use imageio for WebM
             # Convert images to numpy arrays (RGB or RGBA)
             # Note: WebM supports transparency with VP9 but handling it perfectly depends on params.
             # pixel_format='yuva420p' allows alpha
             writer = imageio.get_writer(output_file, fps=fps, codec='libvpx-vp9', pixelformat='yuva420p')
             for img in images:
                 writer.append_data(np.array(img))
             writer.close()
        
        elif format_name == "Safari":
             # Use imageio for HEVC (Safari) with alpha
             # Parameters mimic Apple's requirements for transparency
             writer = imageio.get_writer(
                output_file, 
                fps=fps, 
                codec='libx265', 
                pixelformat='yuva420p',
                ffmpeg_params=['-tag:v', 'hvc1', '-x265-params', 'alpha=1']
             )
             for img in images:
                 writer.append_data(np.array(img))
             writer.close()
             
        else:
            # Pillow formats
            first_image = images[0]
            rest_images = images[1:]
            
            save_kwargs = {
                "save_all": True,
                "append_images": rest_images,
                "duration": duration,
                "loop": 0,
            }
            
            if format_name == "AVIF":
                 save_kwargs["format"] = "AVIF"
                 save_kwargs["quality"] = quality
                 save_kwargs["optimize"] = True
            elif format_name == "GIF":
                 save_kwargs["format"] = "GIF"
                 save_kwargs["optimize"] = True
            elif format_name == "PNG":
                 save_kwargs["format"] = "PNG"
                 save_kwargs["blend"] = 0
                 save_kwargs["disposal"] = 1

            first_image.save(output_file, **save_kwargs)
        
        print("Conversion complete!")
        return os.path.getsize(output_file)

    except Exception as e:
        print(f"Error during conversion: {e}")
        return False

# Alias for backward compatibility if needed, though we will update gui.py
convert_images_to_avif = convert_images

def main():
    parser = argparse.ArgumentParser(description="Convert PNG sequence to animated AVIF, GIF, or APNG.")
    parser.add_argument("input_folder", help="Path to the folder containing PNG images.")
    parser.add_argument("output_file", help="Path to the output file (.avif, .gif, .png).")
    parser.add_argument("--fps", type=int, default=24, help="Frames per second (default: 24).")
    parser.add_argument("--quality", type=int, default=85, help="Quality (0-100) (default: 85).")
    parser.add_argument("--width", type=int, help="Target width for resizing.")

    args = parser.parse_args()

    success = convert_images(args.input_folder, args.output_file, args.fps, args.quality, width=args.width)
    if not success:
        sys.exit(1)
    
    print(f"File size: {success} bytes")

if __name__ == "__main__":
    main()
