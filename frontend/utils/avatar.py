import base64
import io
from pathlib import Path

_AVATAR_COLORS = [
    "#8B5CF6", "#F97316", "#10B981",
    "#3B82F6", "#EC4899", "#0EA5E9",
]

_IMG_DIR = Path(__file__).parent.parent / "assets" / "profile"

_IMG_CACHE: dict[str, str] = {}
_THUMB_SIZE = 160  # px — more than enough for 84px display


def _load_thumbnail(img_path: Path) -> str:
    try:
        from PIL import Image
        img = Image.open(img_path).convert("RGB")
        img.thumbnail((_THUMB_SIZE, _THUMB_SIZE), Image.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=85, optimize=True)
        b64 = base64.b64encode(buf.getvalue()).decode()
        return f"data:image/jpeg;base64,{b64}"
    except ImportError:
        # Pillow not installed — fall back to raw base64 (original behavior)
        ext = img_path.suffix.lstrip(".")
        b64 = base64.b64encode(img_path.read_bytes()).decode()
        return f"data:image/{ext};base64,{b64}"


def _initials(name: str) -> str:
    parts = name.strip().split()
    if len(parts) >= 2:
        return (parts[0][0] + parts[-1][0]).upper()
    return parts[0][0].upper() if parts else "?"


def _color(name: str) -> str:
    return _AVATAR_COLORS[sum(ord(c) for c in name) % len(_AVATAR_COLORS)]


def avatar_html(name: str, image: str | None, size: int = 72, radius: int = 14) -> str:
    if image:
        if image not in _IMG_CACHE:
            img_path = _IMG_DIR / image
            _IMG_CACHE[image] = _load_thumbnail(img_path) if img_path.exists() else ""
        data_url = _IMG_CACHE[image]
        if data_url:
            return (
                f'<img src="{data_url}" '
                f'width="{size}" height="{size}" '
                f'style="border-radius:{radius}px;border:1.5px solid #EDE8E3;'
                f'flex-shrink:0;object-fit:cover;" />'
            )
    initials = _initials(name)
    color = _color(name)
    font = max(12, size // 3)
    return (
        f'<div style="width:{size}px;height:{size}px;border-radius:{radius}px;'
        f'background:{color};display:flex;align-items:center;justify-content:center;'
        f'font-family:DM Sans,sans-serif;font-size:{font}px;font-weight:700;'
        f'color:#fff;flex-shrink:0;letter-spacing:0.04em;">'
        f'{initials}</div>'
    )
