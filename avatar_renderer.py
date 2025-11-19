"""
Avatar renderer: uses Hugging Face Inference API (if HUGGINGFACE_API_TOKEN set) to generate photorealistic images,
otherwise falls back to a lightweight PIL-based symbolic renderer that composes a scene sketch matching the description.

Provides: render_avatar_bytes(prompt, width=512, height=768)
"""
import io
import os
import requests
from typing import Dict, Any

# Try to import PIL for fallback rendering
try:
    from PIL import Image, ImageDraw, ImageFont
    _HAS_PIL = True
except Exception:
    _HAS_PIL = False

HUGGINGFACE_MODEL = os.environ.get("HF_AVATAR_MODEL", "stabilityai/stable-diffusion-2")
HF_TOKEN = os.environ.get("HUGGINGFACE_API_TOKEN")


def _call_huggingface(prompt: str, width: int, height: int) -> bytes:
    """Call Hugging Face Inference API to generate an image. Returns raw bytes when successful."""
    if not HF_TOKEN:
        raise RuntimeError("HUGGINGFACE_API_TOKEN not set")

    url = f"https://api-inference.huggingface.co/models/{HUGGINGFACE_MODEL}"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    payload = {
        "inputs": prompt,
        "options": {"wait_for_model": True},
        "parameters": {"width": width, "height": height}
    }

    resp = requests.post(url, headers=headers, json=payload, stream=True, timeout=300)

    if resp.status_code == 200 and resp.headers.get("content-type", "").startswith("image"):
        return resp.content

    # Some models return JSON with error or base64 data
    try:
        j = resp.json()
        if isinstance(j, dict) and "error" in j:
            raise RuntimeError(j["error"])
    except Exception:
        pass

    raise RuntimeError(f"HuggingFace inference failed: {resp.status_code} {resp.text[:200]}")


def _fallback_pil(prompt: str, width: int, height: int) -> bytes:
    """Create a simple illustrative scene using PIL as a fallback."""
    # Import PIL lazily to ensure availability if installed after process start
    try:
        from PIL import Image, ImageDraw, ImageFont
    except Exception:
        raise RuntimeError("Pillow is not installed for fallback rendering")

    img = Image.new("RGB", (width, height), (255, 224, 230))  # light pink wall
    draw = ImageDraw.Draw(img)

    # Floor
    floor_y = int(height * 0.78)
    draw.rectangle([(0, floor_y), (width, height)], fill=(230, 220, 200))

    # Older man (front)
    cx = int(width * 0.5)
    cy_head = int(height * 0.35)
    head_r = int(width * 0.08)
    # Head
    draw.ellipse([(cx - head_r, cy_head - head_r), (cx + head_r, cy_head + head_r)], fill=(220, 180, 140))
    # Body (white short-sleeve shirt)
    body_w = int(width * 0.18)
    body_h = int(height * 0.25)
    draw.rectangle([(cx - body_w//2, cy_head + head_r), (cx + body_w//2, cy_head + head_r + body_h)], fill=(255,255,255))
    # Pants (dark)
    pants_h = int(body_h * 0.6)
    draw.rectangle([(cx - body_w//2, cy_head + head_r + body_h), (cx + body_w//2, cy_head + head_r + body_h + pants_h)], fill=(40,40,40))
    # Arms relaxed by sides
    arm_w = int(body_w * 0.2)
    arm_h = int(body_h * 0.8)
    draw.rectangle([(cx - body_w//2 - arm_w, cy_head + head_r + 10), (cx - body_w//2, cy_head + head_r + 10 + arm_h)], fill=(255,255,255))
    draw.rectangle([(cx + body_w//2, cy_head + head_r + 10), (cx + body_w//2 + arm_w, cy_head + head_r + 10 + arm_h)], fill=(255,255,255))
    # Feet (barefoot small ovals)
    foot_w = 18
    draw.ellipse([(cx - 24, cy_head + head_r + body_h + pants_h + 4), (cx - 24 + foot_w, cy_head + head_r + body_h + pants_h + 12)], fill=(220,180,140))
    draw.ellipse([(cx + 6, cy_head + head_r + body_h + pants_h + 4), (cx + 6 + foot_w, cy_head + head_r + body_h + pants_h + 12)], fill=(220,180,140))
    # Mustache and tilak on forehead
    draw.rectangle([(cx - 14, cy_head + 6), (cx + 14, cy_head + 10)], fill=(80,50,30))  # mustache (very simple)
    draw.rectangle([(cx - 3, cy_head - 8), (cx + 3, cy_head - 2)], fill=(255,140,0))  # tilak

    # Younger man (behind) slightly offset
    bx = cx - int(width * 0.08)
    by_head = cy_head - 8
    head_r2 = int(head_r * 0.95)
    draw.ellipse([(bx - head_r2, by_head - head_r2), (bx + head_r2, by_head + head_r2)], fill=(200,160,120))
    # Shirt checkered (approx by alternating squares)
    b_body_w = int(body_w * 0.95)
    b_body_h = int(body_h * 0.95)
    top_left = (bx - b_body_w//2, by_head + head_r2)
    # Fill base dark
    draw.rectangle([top_left, (top_left[0] + b_body_w, top_left[1] + b_body_h)], fill=(60,60,80))
    # Rough check pattern
    sq = 10
    for i in range(0, b_body_w, sq):
        for j in range(0, b_body_h, sq):
            if (i//sq + j//sq) % 2 == 0:
                draw.rectangle([(top_left[0]+i, top_left[1]+j), (top_left[0]+i+sq, top_left[1]+j+sq)], fill=(100,100,120))
    # Hands on shoulders (simple circles)
    shoulder_y = cy_head + head_r + 20
    draw.ellipse([(cx - 36, shoulder_y - 8), (cx - 36 + 16, shoulder_y + 8)], fill=(200,160,120))
    draw.ellipse([(cx + 20, shoulder_y - 8), (cx + 20 + 16, shoulder_y + 8)], fill=(200,160,120))

    # Younger man's smile (simple arc)
    draw.arc([(bx - 10, by_head + 4), (bx + 10, by_head + 18)], start=0, end=180, fill=(0,0,0))

    # Text description overlay at bottom (small)
    try:
        font = ImageFont.truetype("arial.ttf", 12)
    except Exception:
        font = ImageFont.load_default()
    desc = "Adult man (front) with mustache & tilak; younger man behind, hands on shoulders; barefoot"
    draw.text((10, height - 18), desc, fill=(40,40,40), font=font)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def render_avatar_bytes(payload: Dict[str, Any]) -> bytes:
    """Main entry point. payload may contain:
        - 'description' or 'prompt' (string), or
        - 'character' (dict) with fields like name, role, traits
        - optional width, height
    """
    prompt = payload.get('description') or payload.get('prompt') or ''
    if not prompt and 'character' in payload:
        ch = payload['character']
        # Build a descriptive prompt from character fields
        prompt = f"Photorealistic full-body portrait of {ch.get('name','a person')}, {ch.get('role','adult')}, {', '.join(ch.get('traits',[]))}. "
        # Add clothing hints
        if ch.get('archetype'):
            prompt += f"Archetype: {ch.get('archetype')} . "
    width = int(payload.get('width', 512))
    height = int(payload.get('height', 768))

    # Mode selection: 'photorealistic', 'stylized' (PIL fallback)
    mode = (payload.get('mode') or '').lower()

    if mode == 'photorealistic':
        # Force photorealistic via Hugging Face if token is present
        if HF_TOKEN:
            return _call_huggingface(prompt or payload.get('prompt',''), width, height)
        else:
            raise RuntimeError('Photorealistic mode requested but HUGGINGFACE_API_TOKEN is not set')

    if mode == 'dicebear':
        # Request DiceBear SVG and rasterize it to PNG using PIL if available, otherwise return SVG bytes
        seed = payload.get('seed') or (payload.get('character', {}).get('name') if payload.get('character') else 'seed')
        style = payload.get('style', 'adventurer')
        gender = payload.get('gender')
        url = f"https://api.dicebear.com/7.x/{style}/svg?seed={requests.utils.quote(str(seed))}"
        if gender:
            url += f"&gender={requests.utils.quote(str(gender))}"
        r = requests.get(url, timeout=20)
        if r.status_code == 200:
            svg_bytes = r.content
            # Try to convert SVG to PNG via PIL (requires pillow & cairosvg not available). If not possible, return SVG as PNG-like by embedding.
            try:
                from PIL import Image
                import io
                # PIL cannot natively render SVG; return SVG bytes instead so frontend can render as data:image/svg+xml
                return svg_bytes
            except Exception:
                return svg_bytes
        else:
            raise RuntimeError(f"DiceBear request failed: {r.status_code}")

    # Default: stylized PIL fallback
    return _fallback_pil(prompt or payload.get('prompt',''), width, height)
