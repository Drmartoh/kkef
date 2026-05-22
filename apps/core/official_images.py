"""Normalize official portrait uploads to a consistent, web-friendly size."""

from __future__ import annotations

import os
from io import BytesIO

from django.core.files.base import ContentFile
from PIL import Image, ImageOps

# Square headshot — keeps pages fast and cards uniform
OFFICIAL_PHOTO_PX = 400
JPEG_QUALITY = 88


def normalize_official_photo(field_file) -> ContentFile | None:
    """Center-crop, resize, and return a JPEG suitable for public cards."""
    if not field_file:
        return None

    try:
        field_file.open("rb")
        image = Image.open(field_file)
        image = ImageOps.exif_transpose(image)
    except Exception:
        return None
    finally:
        try:
            field_file.close()
        except Exception:
            pass

    if image.mode in ("RGBA", "P", "LA"):
        background = Image.new("RGB", image.size, (255, 255, 255))
        alpha = image.convert("RGBA").split()[-1]
        background.paste(image.convert("RGBA"), mask=alpha)
        image = background
    elif image.mode != "RGB":
        image = image.convert("RGB")

    width, height = image.size
    side = min(width, height)
    left = (width - side) // 2
    top = (height - side) // 2
    image = image.crop((left, top, left + side, top + side))
    image = image.resize(
        (OFFICIAL_PHOTO_PX, OFFICIAL_PHOTO_PX),
        Image.Resampling.LANCZOS,
    )

    buffer = BytesIO()
    image.save(buffer, format="JPEG", quality=JPEG_QUALITY, optimize=True)
    buffer.seek(0)

    stem = os.path.splitext(os.path.basename(getattr(field_file, "name", "portrait")))[0]
    safe_stem = "".join(c if c.isalnum() or c in "-_" else "-" for c in stem)[:80] or "portrait"
    return ContentFile(buffer.getvalue(), name=f"{safe_stem}.jpg")
