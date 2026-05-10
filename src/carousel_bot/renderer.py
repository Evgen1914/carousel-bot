from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

from carousel_bot.models import CarouselPost, Slide


WIDTH = 1080
HEIGHT = 1350
SAFE_X = 92
FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/Library/Fonts/Arial.ttf",
    "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
]
BOLD_FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/Library/Fonts/Arial Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
]

PALETTES = [
    {"bg": "#F8FBFA", "ink": "#243333", "muted": "#627472", "accent": "#C9606A", "soft": "#DCEDE9"},
    {"bg": "#FBFAF7", "ink": "#28313A", "muted": "#6D737A", "accent": "#2E8F83", "soft": "#F3D9D4"},
    {"bg": "#F7FAFC", "ink": "#242B35", "muted": "#687386", "accent": "#B85C7A", "soft": "#DDE8F2"},
]


def _font_path(candidates: list[str]) -> str | None:
    return next((path for path in candidates if Path(path).exists()), None)


def _font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    path = _font_path(BOLD_FONT_CANDIDATES if bold else FONT_CANDIDATES)
    if path:
        return ImageFont.truetype(path, size=size)
    return ImageFont.load_default()


def _fit_lines(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, max_width: int) -> list[str]:
    words = text.replace("\n", " ").split()
    lines: list[str] = []
    current = ""
    for word in words:
        probe = f"{current} {word}".strip()
        if draw.textlength(probe, font=font) <= max_width:
            current = probe
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def _draw_multiline(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    font: ImageFont.ImageFont,
    fill: str,
    max_width: int,
    line_gap: int,
) -> int:
    x, y = xy
    for line in _fit_lines(draw, text, font, max_width):
        draw.text((x, y), line, font=font, fill=fill)
        bbox = draw.textbbox((x, y), line, font=font)
        y += bbox[3] - bbox[1] + line_gap
    return y


def _measure_block(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.ImageFont,
    max_width: int,
    line_gap: int,
) -> tuple[list[str], int]:
    lines = _fit_lines(draw, text, font, max_width)
    total = 0
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        total += bbox[3] - bbox[1] + line_gap
    return lines, max(0, total - line_gap)


def _draw_fitted_block(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    fill: str,
    max_width: int,
    max_height: int,
    start_size: int,
    min_size: int,
    bold: bool = False,
) -> int:
    size = start_size
    line_gap = max(8, size // 5)
    while size > min_size:
        font = _font(size, bold=bold)
        line_gap = max(8, size // 5)
        lines, height = _measure_block(draw, text, font, max_width, line_gap)
        if height <= max_height:
            break
        size -= 2

    x, y = xy
    font = _font(size, bold=bold)
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        bbox = draw.textbbox((x, y), line, font=font)
        y += bbox[3] - bbox[1] + line_gap
    return y


def _draw_brand(draw: ImageDraw.ImageDraw, palette: dict[str, str], index: int, total: int) -> None:
    draw.rounded_rectangle((SAFE_X, 78, SAFE_X + 210, 126), radius=24, fill=palette["soft"])
    draw.text((SAFE_X + 26, 89), "ГИНЕКОЛОГИЯ", font=_font(22, bold=True), fill=palette["ink"])
    draw.text((WIDTH - SAFE_X - 90, 88), f"{index:02}/{total:02}", font=_font(30, bold=True), fill=palette["accent"])


def render_slide(slide: Slide, index: int, total: int, output_dir: Path) -> Path:
    palette = PALETTES[(index - 1) % len(PALETTES)]
    image = Image.new("RGB", (WIDTH, HEIGHT), palette["bg"])
    draw = ImageDraw.Draw(image)

    draw.ellipse((WIDTH - 370, -160, WIDTH + 190, 400), fill=palette["soft"])
    draw.ellipse((-180, HEIGHT - 300, 280, HEIGHT + 160), fill=palette["soft"])
    draw.rounded_rectangle((SAFE_X, 1010, WIDTH - SAFE_X, 1218), radius=34, fill="#FFFFFF")

    _draw_brand(draw, palette, index, total)

    draw.text((SAFE_X, 238), slide.eyebrow.upper(), font=_font(28, bold=True), fill=palette["accent"])
    y = _draw_fitted_block(
        draw,
        (SAFE_X, 292),
        slide.title,
        palette["ink"],
        WIDTH - SAFE_X * 2,
        310,
        start_size=72,
        min_size=52,
        bold=True,
    )
    y += 44
    _draw_fitted_block(
        draw,
        (SAFE_X, y),
        slide.body,
        palette["ink"],
        WIDTH - SAFE_X * 2,
        330,
        start_size=42,
        min_size=32,
    )

    footer = "Образовательный материал. Не заменяет консультацию врача."
    _draw_multiline(draw, (SAFE_X + 36, 1054), footer, _font(30), palette["muted"], WIDTH - SAFE_X * 2 - 72, 10)

    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"slide_{index:02}.png"
    image.save(path, quality=95)
    return path


def render_carousel(post: CarouselPost, output_dir: Path) -> list[Path]:
    return [render_slide(slide, index, len(post.slides), output_dir) for index, slide in enumerate(post.slides, start=1)]
