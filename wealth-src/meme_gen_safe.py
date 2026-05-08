from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import base64, math, os

FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/impact/Impact.ttf",  # often missing
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]

def load_font(size: int):
    for p in FONT_CANDIDATES:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size=size)
            except Exception:
                pass
    return ImageFont.load_default()

def text_width(draw, text, font, stroke):
    bbox = draw.textbbox((0,0), text, font=font, stroke_width=stroke)
    return bbox[2]-bbox[0]

def wrap_text(draw, text, font, max_w, stroke):
    words = text.split()
    if not words:
        return ""
    lines = []
    cur = words[0]
    for w in words[1:]:
        trial = cur + " " + w
        if text_width(draw, trial, font, stroke) <= max_w:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    return "\n".join(lines)

def fit_text(draw, text, box_w, box_h, max_size=64, min_size=14, stroke=4):
    # returns (font, wrapped_text)
    text = text.strip()
    for size in range(max_size, min_size-1, -1):
        font = load_font(size)
        wrapped = wrap_text(draw, text, font, box_w, stroke)
        bbox = draw.multiline_textbbox((0,0), wrapped, font=font, align="center", spacing=4, stroke_width=stroke)
        w = bbox[2]-bbox[0]
        h = bbox[3]-bbox[1]
        if w <= box_w and h <= box_h:
            return font, wrapped
    font = load_font(min_size)
    wrapped = wrap_text(draw, text, font, box_w, stroke)
    return font, wrapped

def draw_meme(canvas, top_text, bottom_text, accent=(255, 210, 0), theme="default"):
    W, H = canvas.size
    draw = ImageDraw.Draw(canvas)

    # Background subtle gradient
    bg = canvas
    px = bg.load()
    for y in range(H):
        t = y/(H-1)
        r = int(20 + 15*math.sin(2*math.pi*t))
        g = int(22 + 18*(1-t))
        b = int(28 + 22*t)
        for x in range(W):
            # very cheap horizontal vignette
            v = 0.85 + 0.15*math.cos(2*math.pi*(x/(W-1)))
            px[x,y] = (int(r*v), int(g*v), int(b*v))

    # Panels
    margin = 18
    top_h = int(H*0.23)
    bottom_h = int(H*0.23)
    mid_box = (margin, margin+top_h+10, W-margin, H-margin-bottom_h-10)

    # Mid scene frame
    draw.rounded_rectangle(mid_box, radius=18, outline=(255,255,255), width=3)

    # Decorative scene depending on theme
    cx, cy = (W//2, (mid_box[1]+mid_box[3])//2)

    if theme == "nanny_vs_chaos":
        # Left: Nanny Bot (robot + shield)
        lb = (mid_box[0]+40, cy-85, mid_box[0]+220, cy+85)
        draw.rounded_rectangle(lb, radius=20, fill=(45, 95, 140), outline=(240,240,240), width=3)
        # eyes
        draw.ellipse((lb[0]+45, lb[1]+45, lb[0]+85, lb[1]+85), fill=(255,255,255))
        draw.ellipse((lb[0]+135, lb[1]+45, lb[0]+175, lb[1]+85), fill=(255,255,255))
        draw.ellipse((lb[0]+60, lb[1]+60, lb[0]+75, lb[1]+75), fill=(20,20,20))
        draw.ellipse((lb[0]+150, lb[1]+60, lb[0]+165, lb[1]+75), fill=(20,20,20))
        # shield
        sh = (lb[0]+190, lb[1]+55, lb[0]+250, lb[1]+140)
        draw.polygon([(sh[0], sh[1]), (sh[2], sh[1]), (sh[2]-10, sh[3]-10), ((sh[0]+sh[2])//2, sh[3]+10), (sh[0]+10, sh[3]-10)], fill=(80, 180, 120), outline=(240,240,240))
        draw.line([(sh[0]+10, sh[1]+20), (sh[2]-10, sh[3]-10)], fill=(240,240,240), width=3)

        # Right: Chaos Monkey (face + wrench)
        rb = (mid_box[2]-220, cy-85, mid_box[2]-40, cy+85)
        draw.ellipse(rb, fill=(140, 90, 55), outline=(240,240,240), width=3)
        # ears
        draw.ellipse((rb[0]-30, cy-30, rb[0]+30, cy+30), fill=(140, 90, 55), outline=(240,240,240), width=3)
        draw.ellipse((rb[2]-30, cy-30, rb[2]+30, cy+30), fill=(140, 90, 55), outline=(240,240,240), width=3)
        # muzzle
        draw.ellipse((rb[0]+45, cy-10, rb[2]-45, cy+60), fill=(200, 160, 120))
        # eyes
        draw.ellipse((rb[0]+55, cy-35, rb[0]+85, cy-5), fill=(255,255,255))
        draw.ellipse((rb[2]-85, cy-35, rb[2]-55, cy-5), fill=(255,255,255))
        draw.ellipse((rb[0]+67, cy-25, rb[0]+78, cy-14), fill=(20,20,20))
        draw.ellipse((rb[2]-78, cy-25, rb[2]-67, cy-14), fill=(20,20,20))
        # wrench
        wx1, wy1 = rb[0]+20, cy+70
        wx2, wy2 = rb[0]+160, cy+120
        draw.line([(wx1, wy1), (wx2, wy2)], fill=(180,180,200), width=10)
        draw.ellipse((wx2-18, wy2-18, wx2+18, wy2+18), outline=(180,180,200), width=8)

        # Center VS lightning
        draw.text((W//2, cy-10), "VS", fill=accent, anchor="mm", font=load_font(56), stroke_width=4, stroke_fill=(0,0,0))
        draw.polygon([(W//2-10, cy-70), (W//2+10, cy-70), (W//2, cy-35)], fill=accent)
        draw.polygon([(W//2-10, cy+70), (W//2+10, cy+70), (W//2, cy+35)], fill=accent)

    elif theme == "overlords":
        # Crown + clipboard
        crown_y = mid_box[1]+30
        crown = [(cx-80, crown_y+40), (cx-40, crown_y+10), (cx-15, crown_y+45), (cx, crown_y+5), (cx+15, crown_y+45), (cx+40, crown_y+10), (cx+80, crown_y+40), (cx+80, crown_y+70), (cx-80, crown_y+70)]
        draw.polygon(crown, fill=(240, 200, 60), outline=(255,255,255))
        # clipboard
        cb = (cx-110, crown_y+110, cx+110, crown_y+260)
        draw.rounded_rectangle(cb, radius=16, fill=(55,55,70), outline=(255,255,255), width=3)
        draw.rectangle((cb[0]+25, cb[1]+25, cb[2]-25, cb[3]-25), fill=(240,240,240))
        for i in range(5):
            y = cb[1]+45+i*30
            draw.line((cb[0]+35, y, cb[2]-35, y), fill=(120,120,120), width=3)
        # stamp
        draw.ellipse((cb[2]-90, cb[1]+140, cb[2]-20, cb[1]+210), fill=(220,60,60), outline=(255,255,255), width=3)
        draw.text((cb[2]-55, cb[1]+175), "SAFE", fill=(255,255,255), anchor="mm", font=load_font(28))

    else:
        # Default: pipeline + warning sign
        # pipeline
        y = cy+40
        draw.rounded_rectangle((mid_box[0]+50, y, mid_box[2]-50, y+40), radius=20, fill=(80, 100, 140))
        for x in range(mid_box[0]+70, mid_box[2]-70, 60):
            draw.line((x, y+8, x, y+32), fill=(40,50,70), width=4)
        # warning sign
        tri = [(cx, cy-90), (cx-70, cy+20), (cx+70, cy+20)]
        draw.polygon(tri, fill=(240, 200, 60), outline=(30,30,30))
        draw.text((cx, cy-10), "!", fill=(30,30,30), anchor="mm", font=load_font(64))

    # Text bars (top & bottom) with classic meme outline
    stroke = 5
    pad = 10
    top_box = (margin, margin, W-margin, margin+top_h)
    bottom_box = (margin, H-margin-bottom_h, W-margin, H-margin)

    # semi-transparent bars
    overlay = Image.new("RGBA", canvas.size, (0,0,0,0))
    od = ImageDraw.Draw(overlay)
    od.rectangle(top_box, fill=(0,0,0,120))
    od.rectangle(bottom_box, fill=(0,0,0,120))
    canvas.alpha_composite(overlay)

    draw = ImageDraw.Draw(canvas)

    # Fit top
    font_top, wrapped_top = fit_text(draw, top_text.upper(), top_box[2]-top_box[0]-2*pad, top_box[3]-top_box[1]-2*pad, max_size=56, min_size=18, stroke=stroke)
    bbox_top = draw.multiline_textbbox((0,0), wrapped_top, font=font_top, align="center", spacing=4, stroke_width=stroke)
    tw, th = bbox_top[2]-bbox_top[0], bbox_top[3]-bbox_top[1]
    tx = (W - tw)//2
    ty = top_box[1] + (top_h - th)//2
    draw.multiline_text((tx, ty), wrapped_top, font=font_top, fill=(255,255,255), align="center", spacing=4, stroke_width=stroke, stroke_fill=(0,0,0))

    # Fit bottom
    font_bot, wrapped_bot = fit_text(draw, bottom_text.upper(), bottom_box[2]-bottom_box[0]-2*pad, bottom_box[3]-bottom_box[1]-2*pad, max_size=48, min_size=16, stroke=stroke)
    bbox_bot = draw.multiline_textbbox((0,0), wrapped_bot, font=font_bot, align="center", spacing=4, stroke_width=stroke)
    bw, bh = bbox_bot[2]-bbox_bot[0], bbox_bot[3]-bbox_bot[1]
    bx = (W - bw)//2
    by = bottom_box[1] + (bottom_h - bh)//2
    draw.multiline_text((bx, by), wrapped_bot, font=font_bot, fill=(255,255,255), align="center", spacing=4, stroke_width=stroke, stroke_fill=(0,0,0))

    return canvas

def make_canvas(w=640, h=420):
    return Image.new("RGBA", (w,h), (0,0,0,255))

def to_b64(img, fmt="JPEG", quality=80):
    buff = BytesIO()
    if fmt.upper() == "JPEG":
        img = img.convert("RGB")
        img.save(buff, format="JPEG", quality=quality, optimize=True)
        mime = "image/jpeg"
    else:
        img.save(buff, format=fmt)
        mime = "image/png"
    b64 = base64.b64encode(buff.getvalue()).decode("utf-8")
    return mime, b64

memes = []

# Meme 1: Nanny Bot vs Chaos Monkey
img1 = make_canvas()
draw_meme(img1, "Nanny Bot vs Chaos Monkey", "Who wins? Production still loses.", theme="nanny_vs_chaos")
memes.append(("nanny_bot_vs_chaos_monkey",) + to_b64(img1, fmt="JPEG"))

# Meme 2: AI safety overlords
img2 = make_canvas()
draw_meme(img2, "AI safety overlords", "Just one more polic🪢y and your model will be saf🪢e", theme="overlords")
memes.append(("just_one_more_policy",) + to_b64(img2, fmt="JPEG"))

# Meme 3: Alignment vs data pipeline
img3 = make_canvas()
draw_meme(img3, "When they say: alignment first", "But the bug was in the data pipeline.", theme="default")
memes.append(("alignment_first_pipeline_bug",) + to_b64(img3, fmt="JPEG"))

out = {name: {"mime": mime, "base64": b64} for name, mime, b64 in memes}

# Print as a python literal (safe to copy)
out
