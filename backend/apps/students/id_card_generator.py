import hashlib
import random
from datetime import date

from django.utils import timezone
from PIL import Image, ImageOps
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics

from apps.settings_app.models import SystemSettings

from .qr_utils import ensure_student_qr_code, get_existing_file_path


CARD_WIDTH = 85.6 * mm
CARD_HEIGHT = 54 * mm
ID_CARD_SIZE = (CARD_WIDTH, CARD_HEIGHT)

CARD_MARGIN = 4
CARD_X = CARD_MARGIN
CARD_Y = CARD_MARGIN
CARD_W = CARD_WIDTH - (CARD_MARGIN * 2)
CARD_H = CARD_HEIGHT - (CARD_MARGIN * 2)

DEEP_PURPLE = colors.HexColor("#241045")
ROYAL_PURPLE = colors.HexColor("#56207F")
VIOLET = colors.HexColor("#7B2DB8")
HOT_PINK = colors.HexColor("#F12BBE")
SOFT_PINK = colors.HexColor("#FF7BD8")
WHITE = colors.white
MUTED = colors.HexColor("#E7DAF6")
GREEN = colors.HexColor("#2E9D78")
SLATE = colors.HexColor("#657083")


def get_id_card_settings():
    return SystemSettings.objects.first()


def draw_student_id_card(pdf, student, system_settings=None):
    """
    Draw one premium landscape student ID card on the active ReportLab page.
    """

    system_settings = system_settings or get_id_card_settings()
    organization_name = _organization_name(system_settings)

    _draw_background(pdf, student)
    _draw_brand(pdf, organization_name, system_settings)
    _draw_photo(pdf, student)
    _draw_student_details(pdf, student)
    _draw_qr_code(pdf, student)
    _draw_status(pdf, student)
    _draw_footer(pdf, organization_name)


def _organization_name(system_settings):
    if system_settings and system_settings.organization_name:
        return system_settings.organization_name.strip()

    return "CodeCamp Innovation Hub"


def _draw_background(pdf, student):
    pdf.setFillColor(colors.white)
    pdf.rect(0, 0, CARD_WIDTH, CARD_HEIGHT, fill=1, stroke=0)

    pdf.setFillColor(DEEP_PURPLE)
    pdf.roundRect(CARD_X, CARD_Y, CARD_W, CARD_H, 9, fill=1, stroke=0)

    _draw_gradient_band(
        pdf,
        CARD_Y + 9,
        CARD_Y + CARD_H - 6,
        ROYAL_PURPLE,
        DEEP_PURPLE,
        28,
    )

    _draw_glow(pdf, CARD_X + CARD_W * 0.64, CARD_Y + CARD_H * 0.58, 78, VIOLET)
    _draw_glow(pdf, CARD_X + CARD_W * 0.78, CARD_Y + CARD_H * 0.24, 42, HOT_PINK)
    _draw_speckles(pdf, student)

    _draw_wave(
        pdf,
        y=CARD_Y + CARD_H * 0.72,
        height=16,
        stroke_color=SOFT_PINK,
        fill_color=colors.Color(0.92, 0.12, 0.72, alpha=0.15),
        line_width=1.8,
    )
    _draw_wave(
        pdf,
        y=CARD_Y + CARD_H * 0.22,
        height=19,
        stroke_color=HOT_PINK,
        fill_color=colors.Color(0.89, 0.12, 0.76, alpha=0.22),
        line_width=2.2,
    )


def _draw_gradient_band(pdf, bottom, top, start_color, end_color, steps):
    band_height = (top - bottom) / steps

    for step in range(steps):
        ratio = step / max(steps - 1, 1)
        color = colors.Color(
            start_color.red + ((end_color.red - start_color.red) * ratio),
            start_color.green + ((end_color.green - start_color.green) * ratio),
            start_color.blue + ((end_color.blue - start_color.blue) * ratio),
        )

        pdf.setFillColor(color)
        pdf.rect(
            CARD_X,
            bottom + (step * band_height),
            CARD_W,
            band_height + 1,
            fill=1,
            stroke=0,
        )


def _draw_glow(pdf, cx, cy, radius, color):
    for step in range(10, 0, -1):
        factor = step / 10
        pdf.setFillColor(
            colors.Color(
                color.red,
                color.green,
                color.blue,
                alpha=0.035 * factor,
            )
        )
        pdf.circle(cx, cy, radius * factor, fill=1, stroke=0)


def _draw_speckles(pdf, student):
    seed = hashlib.sha256(str(student.student_id).encode("utf-8")).hexdigest()
    rng = random.Random(seed)

    for _ in range(90):
        x = rng.uniform(CARD_X + 8, CARD_X + CARD_W - 8)
        y = rng.uniform(CARD_Y + 12, CARD_Y + CARD_H - 24)
        radius = rng.uniform(0.12, 0.38)
        alpha = rng.uniform(0.08, 0.26)
        pdf.setFillColor(colors.Color(1, 1, 1, alpha=alpha))
        pdf.circle(x, y, radius, fill=1, stroke=0)


def _draw_wave(pdf, y, height, stroke_color, fill_color, line_width):
    path = pdf.beginPath()
    path.moveTo(CARD_X, y)
    path.curveTo(
        CARD_X + CARD_W * 0.24,
        y - height,
        CARD_X + CARD_W * 0.47,
        y + height * 0.85,
        CARD_X + CARD_W,
        y + height * 0.18,
    )
    path.lineTo(CARD_X + CARD_W, y - 5)
    path.curveTo(
        CARD_X + CARD_W * 0.68,
        y - height * 0.7,
        CARD_X + CARD_W * 0.42,
        y + height * 0.15,
        CARD_X,
        y - height * 0.45,
    )
    path.close()

    pdf.setFillColor(fill_color)
    pdf.drawPath(path, fill=1, stroke=0)

    line = pdf.beginPath()
    line.moveTo(CARD_X, y)
    line.curveTo(
        CARD_X + CARD_W * 0.24,
        y - height,
        CARD_X + CARD_W * 0.47,
        y + height * 0.85,
        CARD_X + CARD_W,
        y + height * 0.18,
    )
    pdf.setStrokeColor(stroke_color)
    pdf.setLineWidth(line_width)
    pdf.drawPath(line, fill=0, stroke=1)


def _draw_brand(pdf, organization_name, system_settings):
    logo_path = get_existing_file_path(system_settings.logo) if system_settings else None
    logo_x = CARD_X + 11
    logo_y = CARD_Y + CARD_H - 31
    logo_size = 22

    if logo_path:
        pdf.setFillColor(colors.Color(1, 1, 1, alpha=0.88))
        pdf.roundRect(logo_x, logo_y, logo_size, logo_size, 5, fill=1, stroke=0)
        _draw_image_fit(
            pdf,
            logo_path,
            logo_x + 2,
            logo_y + 2,
            logo_size - 4,
            logo_size - 4,
        )
    else:
        _draw_fallback_logo(pdf, logo_x, logo_y, logo_size)

    text_x = logo_x + logo_size + 8
    text_y = logo_y + 14

    pdf.setFillColor(WHITE)
    _draw_fit_text(
        pdf,
        organization_name.upper(),
        text_x,
        text_y,
        CARD_X + CARD_W - text_x - 15,
        "Helvetica-Bold",
        14,
        8,
    )

    pdf.setFillColor(MUTED)
    pdf.setFont("Helvetica", 6.6)
    pdf.drawString(text_x, text_y - 10, "STUDENT IDENTIFICATION CARD")


def _draw_fallback_logo(pdf, x, y, size):
    pdf.setFillColor(colors.Color(0.97, 0.25, 0.74, alpha=0.2))
    pdf.roundRect(x, y, size, size, 7, fill=1, stroke=0)

    pdf.setStrokeColor(SOFT_PINK)
    pdf.setLineCap(1)
    pdf.setLineWidth(3)
    pdf.arc(x + 3, y + 5, x + size - 3, y + size - 3, 88, 250)
    pdf.setStrokeColor(HOT_PINK)
    pdf.arc(x + 7, y + 7, x + size + 1, y + size - 2, 92, 228)

    pdf.setFillColor(WHITE)
    pdf.setFont("Helvetica-Bold", 9)
    pdf.drawCentredString(x + (size / 2), y + 7.5, "C")


def _draw_photo(pdf, student):
    cx = CARD_X + 47
    cy = CARD_Y + 65
    radius = 33
    photo_path = get_existing_file_path(student.photo)

    pdf.setFillColor(colors.Color(1, 1, 1, alpha=0.23))
    pdf.circle(cx + 2, cy - 2, radius + 3, fill=1, stroke=0)

    pdf.setFillColor(WHITE)
    pdf.circle(cx, cy, radius + 3, fill=1, stroke=0)

    if photo_path:
        _draw_circular_image(pdf, photo_path, cx, cy, radius)
    else:
        _draw_initials_placeholder(pdf, student, cx, cy, radius)


def _draw_circular_image(pdf, image_path, cx, cy, radius):
    image = _square_image_reader(image_path)

    if not image:
        return

    pdf.saveState()
    clip = pdf.beginPath()
    clip.circle(cx, cy, radius)
    pdf.clipPath(clip, stroke=0, fill=0)
    pdf.drawImage(
        image,
        cx - radius,
        cy - radius,
        width=radius * 2,
        height=radius * 2,
        mask="auto",
    )
    pdf.restoreState()


def _square_image_reader(image_path):
    try:
        with Image.open(image_path) as image:
            image = ImageOps.exif_transpose(image).convert("RGB")
            width, height = image.size
            side = min(width, height)
            left = (width - side) // 2
            top = (height - side) // 2
            image = image.crop((left, top, left + side, top + side))
            return ImageReader(image.copy())
    except (OSError, ValueError):
        return None


def _draw_initials_placeholder(pdf, student, cx, cy, radius):
    initials = "".join(
        part[:1]
        for part in [
            student.first_name,
            student.last_name,
        ]
        if part
    ).upper() or "ST"

    pdf.setFillColor(colors.HexColor("#F2E9FF"))
    pdf.circle(cx, cy, radius, fill=1, stroke=0)
    pdf.setFillColor(VIOLET)
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawCentredString(cx, cy - 6, initials[:2])


def _draw_student_details(pdf, student):
    x = CARD_X + 84
    y = CARD_Y + 80
    max_width = 89
    full_name = student.full_name.upper().strip()
    lines = _wrap_text(full_name, "Helvetica-Bold", 15.4, max_width, max_lines=2)

    pdf.setFillColor(WHITE)
    font_size = 15.4 if len(lines) == 1 else 14
    line_gap = 15.5 if len(lines) == 1 else 14
    pdf.setFont("Helvetica-Bold", font_size)

    for index, line in enumerate(lines):
        pdf.drawString(x, y - (index * line_gap), line)

    after_name_y = y - (len(lines) * line_gap) - 1
    pdf.setFillColor(MUTED)
    pdf.setFont("Helvetica-Bold", 7.9)
    pdf.drawString(x, after_name_y, _student_class_label(student).upper())

    pdf.setFillColor(WHITE)
    pdf.setFont("Helvetica-Bold", 8.2)
    pdf.drawString(x, after_name_y - 17, "ID:")
    _draw_fit_text(
        pdf,
        student.student_id,
        x + 16,
        after_name_y - 17,
        max_width - 16,
        "Helvetica-Bold",
        10.5,
        7,
    )


def _student_class_label(student):
    teaching_class = getattr(student, "teaching_class", None)

    if teaching_class:
        return teaching_class.name

    if student.class_name:
        return student.class_name

    return "Student"


def _draw_qr_code(pdf, student):
    ensure_student_qr_code(student)
    qr_code_path = get_existing_file_path(student.qr_code)
    box_size = 51
    box_x = CARD_X + CARD_W - box_size - 13
    box_y = CARD_Y + 46

    pdf.setFillColor(colors.Color(1, 1, 1, alpha=0.96))
    pdf.roundRect(box_x, box_y, box_size, box_size, 4, fill=1, stroke=0)

    if qr_code_path:
        pdf.drawImage(
            qr_code_path,
            box_x + 4,
            box_y + 4,
            width=box_size - 8,
            height=box_size - 8,
            mask="auto",
        )
    else:
        pdf.setFillColor(colors.HexColor("#111827"))
        pdf.setFont("Helvetica-Bold", 6)
        pdf.drawCentredString(
            box_x + (box_size / 2),
            box_y + (box_size / 2),
            "QR unavailable",
        )


def _draw_status(pdf, student):
    valid_until = _valid_until()
    box_size = 51
    box_x = CARD_X + CARD_W - box_size - 13
    y = CARD_Y + 19

    pdf.setFillColor(WHITE)
    pdf.setFont("Helvetica-Bold", 6.7)
    pdf.drawCentredString(box_x + (box_size / 2), y + 20, f"VALID UNTIL: {valid_until}")

    active = getattr(student, "is_active", True)
    badge_color = GREEN if active else SLATE
    badge_text = "ACTIVE" if active else "INACTIVE"
    badge_w = 48
    badge_h = 13
    badge_x = box_x + ((box_size - badge_w) / 2)
    badge_y = y

    pdf.setFillColor(badge_color)
    pdf.roundRect(badge_x, badge_y, badge_w, badge_h, 4, fill=1, stroke=0)
    pdf.setFillColor(WHITE)
    pdf.setFont("Helvetica-Bold", 8.5)
    pdf.drawCentredString(badge_x + (badge_w / 2), badge_y + 3.4, badge_text)


def _valid_until():
    today = timezone.localdate()

    if not isinstance(today, date):
        today = date.today()

    return date(today.year + 1, 12, 31).strftime("%b %d, %Y").upper()


def _draw_footer(pdf, organization_name):
    text = f"Property of {organization_name}"
    pdf.setFillColor(colors.Color(1, 1, 1, alpha=0.86))
    _draw_fit_text(
        pdf,
        text,
        CARD_X + 11,
        CARD_Y + 7,
        CARD_W - 22,
        "Helvetica-Bold",
        6.5,
        4.8,
    )


def _draw_image_fit(pdf, image_path, x, y, width, height):
    try:
        image = ImageReader(image_path)
    except (OSError, ValueError):
        return

    pdf.drawImage(
        image,
        x,
        y,
        width=width,
        height=height,
        preserveAspectRatio=True,
        anchor="c",
        mask="auto",
    )


def _draw_fit_text(pdf, text, x, y, max_width, font_name, max_size, min_size):
    size = max_size

    while size > min_size and pdfmetrics.stringWidth(text, font_name, size) > max_width:
        size -= 0.5

    pdf.setFont(font_name, size)
    pdf.drawString(x, y, text)


def _wrap_text(text, font_name, font_size, max_width, max_lines):
    words = text.split()
    lines = []
    current = ""

    for word in words:
        candidate = f"{current} {word}".strip()

        if pdfmetrics.stringWidth(candidate, font_name, font_size) <= max_width:
            current = candidate
            continue

        if current:
            lines.append(current)

        current = word

        if len(lines) == max_lines:
            break

    if current and len(lines) < max_lines:
        lines.append(current)

    if not lines:
        return [text]

    if len(lines) == max_lines and " ".join(lines) != text:
        lines[-1] = _ellipsize(lines[-1], font_name, font_size, max_width)

    return lines


def _ellipsize(text, font_name, font_size, max_width):
    ellipsis = "..."
    available = max_width - pdfmetrics.stringWidth(ellipsis, font_name, font_size)

    if available <= 0:
        return ellipsis

    while text and pdfmetrics.stringWidth(text, font_name, font_size) > available:
        text = text[:-1]

    return f"{text.rstrip()}{ellipsis}"
