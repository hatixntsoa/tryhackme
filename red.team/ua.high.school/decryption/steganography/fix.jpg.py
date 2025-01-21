import os
import sys

def fix_jpg_signature(file_path):
    try:
        with open(file_path, "rb") as file:
            data = file.read()

        # Check if the file has a PNG signature
        png_signature = b'\x89\x50\x4E\x47\x0D\x0A\x1A\x0A'
        jpg_signature = b'\xFF\xD8\xFF\xE0'

        if data.startswith(png_signature):
            print("[INFO] PNG signature found. Fixing the header...")

            # Replace PNG signature with JPEG signature
            fixed_data = jpg_signature + data[len(png_signature):]

            # Generate the new file name
            new_file_path = f"{os.path.splitext(file_path)[0]}.fixed.jpg"

            # Write the corrected data to the new file
            with open(new_file_path, "wb") as new_file:
                new_file.write(fixed_data)

            print(f"[SUCCESS] The file header has been corrected. Saved as: {new_file_path}")
        else:
            print("[INFO] No PNG signature found. The file might already be correct.")

    except Exception as e:
        print(f"[ERROR] Failed to fix the file: {e}")

# Usage: python fix_jpg.py <file_path>
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python fix.jpg.py <file_path>")
        sys.exit(1)

    fix_jpg_signature(sys.argv[1])
