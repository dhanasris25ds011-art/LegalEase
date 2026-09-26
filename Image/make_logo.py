from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

S = 4  # supersampling factor for smooth edges


def find_font(size):
    for path in ("C:/Windows/Fonts/times.ttf",
                 "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"):
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            pass
    return ImageFont.load_default(size=size)


def make_logo(path, color):
    W, H = 1000, 300
    img = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    s = lambda v: int(v * S)

    # ---- scales of justice icon ----
    cx, beam_y = 140, 95
    lx, rx = cx - 90, cx + 90
    d.line([(s(cx), s(60)), (s(cx), s(225))], fill=color, width=s(7))            # pillar
    d.ellipse([s(cx - 11), s(48), s(cx + 11), s(70)], fill=color)                 # top ball
    d.line([(s(lx), s(beam_y)), (s(rx), s(beam_y))], fill=color, width=s(7))      # beam
    for x in (lx, rx):
        d.ellipse([s(x - 6), s(beam_y - 6), s(x + 6), s(beam_y + 6)], fill=color)
        d.line([(s(x), s(beam_y)), (s(x - 42), s(170))], fill=color, width=s(3))  # strings
        d.line([(s(x), s(beam_y)), (s(x + 42), s(170))], fill=color, width=s(3))
        d.pieslice([s(x - 50), s(140), s(x + 50), s(200)], 0, 180, fill=color)    # pan
    d.rectangle([s(cx - 50), s(225), s(cx + 50), s(238)], fill=color)             # base
    d.rectangle([s(cx - 32), s(214), s(cx + 32), s(225)], fill=color)

    # ---- text ----
    font = find_font(s(120))
    box = d.textbbox((0, 0), "LegalEase", font=font)
    text_h = box[3] - box[1]
    d.text((s(315), s(143) - text_h // 2 - box[1]), "LegalEase", font=font, fill=color)

    # ---- shrink + trim empty space ----
    img = img.resize((W, H), Image.LANCZOS)
    left, top, right, bottom = img.getbbox()
    img = img.crop((max(left - 10, 0), max(top - 10, 0), right + 10, bottom + 10))
    img.save(path)

OUT = Path(__file__).parent
OUT.mkdir(exist_ok=True)
make_logo(OUT / "Logo.png", (20, 20, 20, 255))            # dark logo -> light pages / DOCX / PDF
make_logo(OUT / "inverseLogo.png", (255, 255, 255, 255))  # white logo -> dark pages
print("Logos created in", OUT)