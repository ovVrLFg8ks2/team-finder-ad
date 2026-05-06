import io
from random import randint

from django.core.files.base import ContentFile
from django.core.paginator import Paginator
from PIL import Image, ImageDraw, ImageFont

from .constants import (
    AVATAR_FONT_PATH,
    AVATAR_LETTER_COLOR,
    AVATAR_LETTER_STROKE_COLOR,
    AVATAR_LETTER_STROKE_WIDTH,
    AVATAR_MINIMUM_COLOR_INTENSITY,
    AVATAR_SIZE_PX,
    DEFAULT_PAGE_CONTENT_COUNT,
)


def paginate(request, queryset, per_page=DEFAULT_PAGE_CONTENT_COUNT):
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get("page")
    return paginator.get_page(page_number)


def make_avatar(letter):
    m = AVATAR_MINIMUM_COLOR_INTENSITY

    x = randint(0, 765)
    k = (255 - m) / 255
    r = int(max(0, abs(x - 382) - 127) * k + m)
    g = int(max(0, 255 - abs(x - 255)) * k + m)
    b = int(max(0, 255 - abs(x - 510)) * k + m)

    size = AVATAR_SIZE_PX
    img = Image.new("RGB", (size, size), color=(r, g, b))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype(AVATAR_FONT_PATH, size=size // 2)
    except OSError:
        font = ImageFont.load_default(size=size // 2)
    textbox = draw.textbbox((0, 0), letter, font=font)
    text_w = textbox[2] - textbox[0]
    text_h = textbox[3] - textbox[1]
    x = (size - text_w) / 2 - textbox[0]
    y = (size - text_h) / 2 - textbox[1]
    draw.text(
        (x, y), letter,
        fill=AVATAR_LETTER_COLOR, font=font,
        stroke_width=AVATAR_LETTER_STROKE_WIDTH,
        stroke_fill=AVATAR_LETTER_STROKE_COLOR
    )
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG")
    return ContentFile(buffer.getvalue())
