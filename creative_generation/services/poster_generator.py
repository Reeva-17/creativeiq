
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps
import uuid


# Poster dimensions: Instagram portrait format
WIDTH = 1080
HEIGHT = 1350

GENERATED_DIR = Path(__file__).resolve().parents[1] / "generated"
GENERATED_DIR.mkdir(parents=True, exist_ok=True)


def get_font(size, bold=False):
    """Load a Windows font, with a fallback."""
    font_path = (
        "C:/Windows/Fonts/arialbd.ttf"
        if bold
        else "C:/Windows/Fonts/arial.ttf"
    )

    try:
        return ImageFont.truetype(font_path, size)
    except OSError:
        return ImageFont.load_default()


def generate_poster(
    image_path,
    brand_name,
    headline,
    offer,
    cta
):
    # Open and resize the AI-generated image
    image = Image.open(image_path).convert("RGB")

    image = ImageOps.fit(
        image,
        (WIDTH, HEIGHT)
    )

    # Add a dark transparent area at the bottom
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw_overlay = ImageDraw.Draw(overlay)

    draw_overlay.rectangle(
        (0, 650, WIDTH, HEIGHT),
        fill=(0, 0, 0, 165)
    )

    image = Image.alpha_composite(
        image.convert("RGBA"),
        overlay
    )

    draw = ImageDraw.Draw(image)

    # Load fonts
    brand_font = get_font(42, bold=True)
    headline_font = get_font(68, bold=True)
    offer_font = get_font(54, bold=True)
    cta_font = get_font(36, bold=True)

    # Add brand name
    draw.text(
        (70, 760),
        brand_name.upper(),
        font=brand_font,
        fill="white"
    )

    # Add headline
    draw.text(
        (70, 850),
        headline,
        font=headline_font,
        fill="white"
    )

    # Add offer
    draw.text(
        (70, 1050),
        offer,
        font=offer_font,
        fill="#FFD700"
    )

    # Add CTA button
    draw.rounded_rectangle(
        (70, 1160, 520, 1245),
        radius=20,
        fill="white"
    )

    draw.text(
        (95, 1180),
        cta,
        font=cta_font,
        fill="#222222"
    )

    # Save final poster
    filename = f"poster_{uuid.uuid4().hex}.png"
    poster_path = GENERATED_DIR / filename

    image.convert("RGB").save(poster_path)

    return poster_path
