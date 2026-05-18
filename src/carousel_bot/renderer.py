from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

from carousel_bot.models import CarouselPost, Slide


WIDTH = 1080
HEIGHT = 1350
SAFE_X = 92
CONTENT_TOP = 230
CONTENT_BOTTOM = 1065
FRAME_X = 110
TOP_LINE_Y = 96
BOTTOM_LINE_Y = 1212
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
SERIF_FONT_CANDIDATES = [
    "/System/Library/Fonts/NewYork.ttf",
    "/System/Library/Fonts/Supplemental/STIXTwoText.ttf",
    "/System/Library/Fonts/Supplemental/Georgia.ttf",
    "/System/Library/Fonts/Supplemental/Times New Roman.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
]
SERIF_BOLD_FONT_CANDIDATES = [
    "/System/Library/Fonts/Supplemental/STIXTwoText.ttf",
    "/System/Library/Fonts/Supplemental/Georgia Bold.ttf",
    "/System/Library/Fonts/Supplemental/Times New Roman Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
]

PALETTE = {"bg": "#F8F6F2", "ink": "#333333", "muted": "#494949", "accent": "#EBD5CC", "line": "#383838"}


def _font_path(candidates: list[str]) -> str | None:
    return next((path for path in candidates if Path(path).exists()), None)


def _font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    path = _font_path(BOLD_FONT_CANDIDATES if bold else FONT_CANDIDATES)
    if path:
        return ImageFont.truetype(path, size=size)
    return ImageFont.load_default()


def _serif_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    path = _font_path(SERIF_BOLD_FONT_CANDIDATES if bold else SERIF_FONT_CANDIDATES)
    if path:
        return ImageFont.truetype(path, size=size)
    return _font(size, bold=bold)


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


def _fitted_block_layout(
    draw: ImageDraw.ImageDraw,
    text: str,
    max_width: int,
    max_height: int,
    start_size: int,
    min_size: int,
    bold: bool = False,
    serif: bool = False,
) -> tuple[ImageFont.ImageFont, list[str], int, int]:
    size = start_size
    line_gap = max(8, size // 5)
    lines: list[str] = []
    height = 0
    while size > min_size:
        font = _serif_font(size, bold=bold) if serif else _font(size, bold=bold)
        line_gap = max(8, size // 6 if serif else size // 5)
        lines, height = _measure_block(draw, text, font, max_width, line_gap)
        if height <= max_height:
            return font, lines, height, line_gap
        size -= 2

    font = _serif_font(size, bold=bold) if serif else _font(size, bold=bold)
    line_gap = max(8, size // 6 if serif else size // 5)
    lines, height = _measure_block(draw, text, font, max_width, line_gap)
    return font, lines, height, line_gap


def _draw_lines(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    lines: list[str],
    font: ImageFont.ImageFont,
    fill: str,
    line_gap: int,
) -> int:
    x, y = xy
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        bbox = draw.textbbox((x, y), line, font=font)
        y += bbox[3] - bbox[1] + line_gap
    return y


def _draw_frame(draw: ImageDraw.ImageDraw, palette: dict[str, str], index: int, total: int) -> None:
    draw.line((FRAME_X, TOP_LINE_Y, WIDTH - FRAME_X, TOP_LINE_Y), fill=palette["line"], width=3)
    draw.line((FRAME_X, BOTTOM_LINE_Y, WIDTH - FRAME_X, BOTTOM_LINE_Y), fill=palette["line"], width=3)
    draw.text((FRAME_X, 122), "Доктор Ripsi", font=_font(24, bold=True), fill=palette["ink"])
    page = f"{index:02}/{total:02}"
    page_font = _font(24, bold=True)
    page_width = draw.textlength(page, font=page_font)
    draw.text((WIDTH - FRAME_X - page_width, 122), page, font=page_font, fill=palette["ink"])


def _visible_eyebrow(text: str) -> str:
    return "" if text.strip().casefold() == "доктор ripsi" else text


def _draw_last_slide_cta(draw: ImageDraw.ImageDraw, palette: dict[str, str]) -> None:
    cta = "ЗАПИСЬ НА КОНСУЛЬТАЦИЮ"
    cta_font = _font(30, bold=True)
    arrow_font = _font(42, bold=True)
    draw.text((FRAME_X, 1120), cta, font=cta_font, fill=palette["ink"])
    pill = (WIDTH - FRAME_X - 176, 1102, WIDTH - FRAME_X, 1160)
    draw.rounded_rectangle(pill, radius=29, fill=palette["accent"])
    draw.text((pill[0] + 71, pill[1] + 2), "↓", font=arrow_font, fill=palette["ink"])


def render_slide(slide: Slide, index: int, total: int, output_dir: Path) -> Path:
    palette = PALETTE
    image = Image.new("RGB", (WIDTH, HEIGHT), palette["bg"])
    draw = ImageDraw.Draw(image)

    _draw_frame(draw, palette, index, total)

    eyebrow = _visible_eyebrow(slide.eyebrow)
    eyebrow_font = _font(30, bold=True)
    eyebrow_height = 0
    eyebrow_gap = 34
    if eyebrow:
        bbox = draw.textbbox((0, 0), eyebrow.upper(), font=eyebrow_font)
        eyebrow_height = bbox[3] - bbox[1] + eyebrow_gap

    title_font, title_lines, title_height, title_gap = _fitted_block_layout(
        draw,
        slide.title,
        WIDTH - SAFE_X * 2,
        310,
        start_size=88,
        min_size=58,
        serif=True,
    )
    body_font, body_lines, body_height, body_gap = _fitted_block_layout(
        draw,
        slide.body,
        WIDTH - SAFE_X * 2,
        330,
        start_size=38,
        min_size=30,
    )
    title_body_gap = 48
    content_height = eyebrow_height + title_height + title_body_gap + body_height
    content_area_height = CONTENT_BOTTOM - CONTENT_TOP
    y = CONTENT_TOP + max(0, (content_area_height - content_height) // 2)

    if eyebrow:
        draw.text((SAFE_X, y), eyebrow.upper(), font=eyebrow_font, fill=palette["accent"])
        y += eyebrow_height

    y = _draw_lines(draw, (SAFE_X, y), title_lines, title_font, palette["ink"], title_gap)
    y += title_body_gap
    _draw_lines(draw, (SAFE_X, y), body_lines, body_font, palette["ink"], body_gap)

    if index == total:
        _draw_last_slide_cta(draw, palette)

    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"slide_{index:02}.png"
    image.save(path, quality=95)
    return path


def render_carousel(post: CarouselPost, output_dir: Path) -> list[Path]:
    return [render_slide(slide, index, len(post.slides), output_dir) for index, slide in enumerate(post.slides, start=1)]
