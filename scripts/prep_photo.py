"""Prep a photo for ASCII conversion.

1. Remove the background (rembg)
2. Boost local contrast (OpenCV CLAHE)
3. Composite onto pure white
Output: source-prepped.png (grayscale) in the project root.

Usage: python scripts/prep_photo.py source-photo.jpg
"""
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from rembg import remove

OUT = Path(__file__).resolve().parent.parent / "source-prepped.png"


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit("Usage: python scripts/prep_photo.py source-photo.jpg")
    src = Path(sys.argv[1])
    if not src.exists():
        sys.exit(f"Photo not found: {src}")

    # 1. Remove background -> RGBA image, transparent where the background was
    print("Removing background (first run downloads a model, please wait)...")
    cut = remove(Image.open(src).convert("RGB")).convert("RGBA")
    rgba = np.array(cut)
    alpha = rgba[:, :, 3]

    # Crop to the subject so the face fills the ASCII grid
    ys, xs = np.where(alpha > 10)
    if len(xs) == 0:
        sys.exit("No subject found in the photo. Try a clearer photo.")
    pad_x = int((xs.max() - xs.min()) * 0.05)
    pad_y = int((ys.max() - ys.min()) * 0.05)
    x0, x1 = max(xs.min() - pad_x, 0), min(xs.max() + pad_x, alpha.shape[1])
    y0, y1 = max(ys.min() - pad_y, 0), min(ys.max() + pad_y, alpha.shape[0])
    rgba = rgba[y0:y1, x0:x1]
    alpha = rgba[:, :, 3]

    # 2. Boost local contrast on the grayscale image
    gray = cv2.cvtColor(rgba[:, :, :3], cv2.COLOR_RGB2GRAY)
    gray = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8)).apply(gray)

    # 3. Composite onto pure white (white -> blank space in the ASCII ramp)
    a = alpha.astype(np.float32) / 255.0
    result = gray.astype(np.float32) * a + 255.0 * (1.0 - a)
    Image.fromarray(result.astype(np.uint8), mode="L").save(OUT)
    print(f"Saved {OUT}")


if __name__ == "__main__":
    main()
