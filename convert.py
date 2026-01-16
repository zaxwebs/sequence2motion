import os
import argparse
import sys
from PIL import Image
import pillow_avif

def convert_images_to_avif(input_folder, output_file, fps=24, quality=85, width=None, progress_callback=None):
    """
    Converts a sequence of PNG images in a folder to an animated AVIF.
    
    Args:
        input_folder (str): Folder containing PNG images.
        output_file (str): Path to the output AVIF file.
        fps (int): Frames per second.
        quality (int): AVIF quality (0-100).
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
        if progress_callback:
            progress_callback(total_files, total_files, "Encoding AVIF (this may take a while)...")
            
        print(f"FPS: {fps}, Duration: {duration}ms, Quality: {quality}, Width: {width if width else 'Original'}")

        # Save as animated AVIF
        # append_images takes the rest of the images
        first_image = images[0]
        rest_images = images[1:]
        
        first_image.save(
            output_file,
            format='AVIF',
            save_all=True,
            append_images=rest_images,
            duration=duration,
            loop=0,
            quality=quality,
            optimize=True
        )
        print("Conversion complete!")
        return True

    except Exception as e:
        print(f"Error during conversion: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Convert PNG sequence to animated AVIF.")
    parser.add_argument("input_folder", help="Path to the folder containing PNG images.")
    parser.add_argument("output_file", help="Path to the output AVIF file.")
    parser.add_argument("--fps", type=int, default=24, help="Frames per second (default: 24).")
    parser.add_argument("--quality", type=int, default=85, help="Quality (0-100) (default: 85).")
    parser.add_argument("--width", type=int, help="Target width for resizing.")

    args = parser.parse_args()

    success = convert_images_to_avif(args.input_folder, args.output_file, args.fps, args.quality, width=args.width)
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
