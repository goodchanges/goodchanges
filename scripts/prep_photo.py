import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from rembg import remove


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/prep_photo.py source-photo.jpg")
        sys.exit(1)

    source = Path(sys.argv[1])

    if not source.exists():
        print(f"File not found: {source}")
        sys.exit(1)

    output_path = Path("source-prepped.png")

    print("Loading image...")
    image = Image.open(source).convert("RGBA")

    print("Removing background...")
    no_background = remove(image)

    rgba = np.array(no_background)

    rgb = rgba[:, :, :3]
    alpha = rgba[:, :, 3].astype(np.float32) / 255.0

    print("Converting to grayscale...")
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)

    # Composite transparent areas onto pure white.
    white = np.full_like(gray, 255)

    gray = (
        gray.astype(np.float32) * alpha
        + white.astype(np.float32) * (1.0 - alpha)
    )

    gray = np.clip(gray, 0, 255).astype(np.uint8)

    print("Improving local contrast...")
    clahe = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8)
    )

    enhanced = clahe.apply(gray)

    result = Image.fromarray(enhanced)

    result.save(output_path)

    print(f"Done: {output_path}")


if __name__ == "__main__":
    main()