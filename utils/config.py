import flet as ft

# Dynamic icon/color resolution for different Flet versions
ICONS = getattr(ft, "icons", None) or getattr(ft, "Icons", None)
COLORS = getattr(ft, "colors", None) or getattr(ft, "Colors", None)

if ICONS is None:
    raise RuntimeError("No icons module found on 'ft'. Please check your flet installation.")
if COLORS is None:
    class _C: 
        BLUE = "blue"
        GREY = "grey"
        GREEN = "green"
        RED = "red"
    COLORS = _C


def normalize_asset_image_path(path, default_path="images/default-user.png"):
    """Normalize image paths to an assets-relative path for Flet web serving."""
    if not path:
        return default_path

    normalized = str(path).strip().replace("\\", "/")
    if not normalized:
        return default_path

    # Already an external URL/data URL.
    if normalized.startswith(("http://", "https://", "data:")):
        return normalized

    while normalized.startswith("../"):
        normalized = normalized[3:]

    if normalized.startswith("./"):
        normalized = normalized[2:]

    if normalized.startswith("assets/"):
        normalized = normalized[7:]

    if normalized.startswith("images/"):
        return normalized

    # Legacy profile uploads saved outside assets are not web-accessible.
    if normalized.startswith("storage/"):
        return default_path

    return f"images/{normalized.lstrip('/')}"