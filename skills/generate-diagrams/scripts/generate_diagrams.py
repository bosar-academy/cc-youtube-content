#!/usr/bin/env python3
"""
Excalidraw Diagram Generator — Whiteboard Sketch Style

Generates .excalidraw JSON files with a hand-drawn whiteboard aesthetic:
- Thick sketchy outlines on white/transparent backgrounds
- Monochrome base with selective pastel accent colors
- Excalifont (hand-drawn font) with maximum roughness
- Generous whitespace and clear visual hierarchy

Usage:
    python generate_diagrams.py build --spec diagram-spec.json --output diagram.excalidraw
    python generate_diagrams.py combine --specs spec1.json spec2.json ... --output all.excalidraw

Requires:
    pip install requests
"""

import argparse
import base64
import json
import math
import mimetypes
import os
import random
import string
import sys
from pathlib import Path

import requests


# ─── Design System ───────────────────────────────────────────────────────────

COLORS = {
    "purple": "#8B5CF6",
    "blue": "#3B82F6",
    "orange": "#F59E0B",
    "green": "#10B981",
    "red": "#EF4444",
    "dark": "#1e1e1e",
    "white": "#FFFFFF",
    "light_gray": "#F8FAFC",
    "gray": "#94A3B8",
}

STROKE_COLORS = {
    "purple": "#7C3AED",
    "blue": "#2563EB",
    "orange": "#D97706",
    "green": "#059669",
    "red": "#DC2626",
    "dark": "#0F172A",
}

# Light pastel fills for "accent" style boxes
ACCENT_FILLS = {
    "red": "#FEE2E2",
    "green": "#DCFCE7",
    "blue": "#DBEAFE",
    "purple": "#EDE9FE",
    "orange": "#FEF3C7",
    "dark": "#F1F5F9",
    "gray": "#F1F5F9",
}

# ─── Whiteboard sketch style ─────────────────────────────────────────────────
# fontFamily 1 = Excalifont (hand-drawn), roughness 2 = maximum sketchy
FONT_FAMILY = 1
ROUGHNESS = 2


def gen_id():
    """Generate a random Excalidraw element ID."""
    return "".join(random.choices(string.ascii_letters + string.digits, k=16))


def make_rectangle(x, y, w, h, color="dark", label="", opacity=100,
                   font_size=24, corner_radius=12, style="outline"):
    """Create a rectangle with optional label.

    Styles:
        outline: Transparent fill, thick black stroke, black text (whiteboard default)
        filled:  Colored fill, darker stroke, white text
        accent:  Light pastel fill, black stroke, black text
    """
    elements = []
    rect_id = gen_id()

    if style == "outline":
        fill = "transparent"
        stroke = "#1e1e1e"
        text_color = "#1e1e1e"
        stroke_width = 2
    elif style == "accent":
        fill = ACCENT_FILLS.get(color, "#F1F5F9")
        stroke = "#1e1e1e"
        text_color = "#1e1e1e"
        stroke_width = 2
    elif style == "filled":
        fill = COLORS.get(color, color)
        stroke = STROKE_COLORS.get(color, fill)
        text_color = COLORS["white"]
        stroke_width = 2
    else:
        fill = "transparent"
        stroke = "#1e1e1e"
        text_color = "#1e1e1e"
        stroke_width = 2

    rect = {
        "id": rect_id,
        "type": "rectangle",
        "x": x,
        "y": y,
        "width": w,
        "height": h,
        "angle": 0,
        "strokeColor": stroke,
        "backgroundColor": fill,
        "fillStyle": "solid",
        "strokeWidth": stroke_width,
        "roughness": ROUGHNESS,
        "opacity": opacity,
        "roundness": {"type": 3, "value": corner_radius},
        "isDeleted": False,
        "boundElements": [],
        "locked": False,
    }
    if label:
        text_id = gen_id()
        lines = label.split("\n")
        num_lines = len(lines)
        max_line_len = max(len(line) for line in lines)
        char_width = font_size * 0.55
        text_w = min(max_line_len * char_width, w - 20)
        text_h = num_lines * font_size * 1.25

        # Auto-expand box if text would be cropped
        min_h = text_h + 24  # 12px padding top + bottom
        if h < min_h:
            print(f"⚠️  Auto-expanding box height: {h:.0f}px → {min_h:.0f}px "
                  f"for: {repr(label[:50])}", file=sys.stderr)
            h = min_h
            rect["height"] = h

        min_w = text_w + 24  # 12px padding left + right
        if w < min_w:
            print(f"⚠️  Auto-expanding box width: {w:.0f}px → {min_w:.0f}px "
                  f"for: {repr(label[:50])}", file=sys.stderr)
            w = min_w
            rect["width"] = w

        text = {
            "id": text_id,
            "type": "text",
            "x": x + (w - text_w) / 2,
            "y": y + (h - text_h) / 2,
            "width": text_w,
            "height": text_h,
            "angle": 0,
            "strokeColor": text_color,
            "backgroundColor": "transparent",
            "fillStyle": "solid",
            "strokeWidth": 1,
            "roughness": 0,
            "opacity": 100,
            "text": label,
            "fontSize": font_size,
            "fontFamily": FONT_FAMILY,
            "textAlign": "center",
            "verticalAlign": "middle",
            "containerId": rect_id,
            "lineHeight": 1.25,
            "autoResize": True,
            "originalText": label,
            "isDeleted": False,
            "boundElements": None,
        }
        rect["boundElements"].append({"id": text_id, "type": "text"})
        elements.append(text)

    elements.insert(0, rect)
    return elements


def make_line(x1, y1, x2, y2, color="dark", stroke_width=1):
    """Create a line element (for dividers, underlines, etc.)."""
    return [{
        "id": gen_id(),
        "type": "line",
        "x": x1,
        "y": y1,
        "width": x2 - x1,
        "height": y2 - y1,
        "angle": 0,
        "strokeColor": COLORS.get(color, color),
        "backgroundColor": "transparent",
        "fillStyle": "solid",
        "strokeWidth": stroke_width,
        "roughness": ROUGHNESS,
        "opacity": 35,
        "points": [[0, 0], [x2 - x1, y2 - y1]],
        "startArrowhead": None,
        "endArrowhead": None,
        "roundness": {"type": 2},
        "isDeleted": False,
        "boundElements": None,
        "locked": False,
    }]


def make_arrow(start_x, start_y, end_x, end_y, color="dark", stroke_width=3,
               label=""):
    """Create a sketchy arrow between two points."""
    fill = COLORS.get(color, color)
    mid_x = (start_x + end_x) / 2
    mid_y = (start_y + end_y) / 2

    elements = []
    arrow_id = gen_id()

    arrow = {
        "id": arrow_id,
        "type": "arrow",
        "x": start_x,
        "y": start_y,
        "width": end_x - start_x,
        "height": end_y - start_y,
        "angle": 0,
        "strokeColor": fill,
        "backgroundColor": "transparent",
        "fillStyle": "solid",
        "strokeWidth": stroke_width,
        "roughness": ROUGHNESS,
        "opacity": 100,
        "points": [
            [0, 0],
            [end_x - start_x, end_y - start_y],
        ],
        "startArrowhead": None,
        "endArrowhead": "arrow",
        "roundness": {"type": 2},
        "isDeleted": False,
        "boundElements": [],
        "locked": False,
    }
    elements.append(arrow)

    if label:
        text_id = gen_id()
        label_lines = label.split("\n")
        max_line = max(len(l) for l in label_lines)
        label_w = max_line * 18 * 0.55
        label_h = len(label_lines) * 18 * 1.25
        text = {
            "id": text_id,
            "type": "text",
            "x": mid_x - label_w / 2,
            "y": mid_y - label_h - 8,
            "width": label_w,
            "height": label_h,
            "angle": 0,
            "strokeColor": fill,
            "backgroundColor": "transparent",
            "fillStyle": "solid",
            "strokeWidth": 1,
            "roughness": 0,
            "opacity": 80,
            "text": label,
            "fontSize": 18,
            "fontFamily": FONT_FAMILY,
            "textAlign": "center",
            "verticalAlign": "middle",
            "containerId": None,
            "isDeleted": False,
            "boundElements": None,
        }
        elements.append(text)

    return elements


def make_text(x, y, text, color="dark", font_size=28, align="left"):
    """Create a standalone text element. Supports multiline via \\n."""
    fill = COLORS.get(color, color)
    lines = text.split("\n")
    max_line = max(len(l) for l in lines)
    return [{
        "id": gen_id(),
        "type": "text",
        "x": x,
        "y": y,
        "width": max_line * font_size * 0.55,
        "height": len(lines) * font_size * 1.25,
        "angle": 0,
        "strokeColor": fill,
        "backgroundColor": "transparent",
        "fillStyle": "solid",
        "strokeWidth": 1,
        "roughness": 0,
        "opacity": 100,
        "text": text,
        "fontSize": font_size,
        "fontFamily": FONT_FAMILY,
        "textAlign": align,
        "verticalAlign": "top",
        "containerId": None,
        "isDeleted": False,
        "boundElements": None,
    }]


def make_group_background(x, y, w, h, color="purple", label=""):
    """Create a light-colored group background with title."""
    fill = COLORS.get(color, color)
    elements = []

    elements.append({
        "id": gen_id(),
        "type": "rectangle",
        "x": x,
        "y": y,
        "width": w,
        "height": h,
        "angle": 0,
        "strokeColor": fill,
        "backgroundColor": fill,
        "fillStyle": "solid",
        "strokeWidth": 1,
        "roughness": ROUGHNESS,
        "opacity": 8,
        "roundness": {"type": 3, "value": 16},
        "isDeleted": False,
        "boundElements": None,
        "locked": False,
    })

    if label:
        elements.extend(make_text(x + 16, y + 12, label, color=color, font_size=24))

    return elements


def make_image(x, y, w, h, file_id):
    """Create an image element that references an embedded file."""
    return [{
        "id": gen_id(),
        "type": "image",
        "x": x,
        "y": y,
        "width": w,
        "height": h,
        "angle": 0,
        "strokeColor": "transparent",
        "backgroundColor": "transparent",
        "fillStyle": "solid",
        "strokeWidth": 0,
        "roughness": 0,
        "opacity": 100,
        "roundness": None,
        "isDeleted": False,
        "boundElements": None,
        "locked": False,
        "status": "saved",
        "fileId": file_id,
        "scale": [1, 1],
    }]


def embed_image_file(image_path):
    """Read an image file and return (file_id, file_data_dict) for embedding."""
    p = Path(image_path)
    if not p.exists():
        print(f"Warning: Image not found: {image_path}", file=sys.stderr)
        return None, None

    mime = mimetypes.guess_type(str(p))[0] or "image/png"
    with open(p, "rb") as f:
        data = f.read()

    b64 = base64.standard_b64encode(data).decode()
    file_id = gen_id()

    return file_id, {
        "mimeType": mime,
        "id": file_id,
        "dataURL": f"data:{mime};base64,{b64}",
        "created": 1709000000000,
        "lastRetrieved": 1709000000000,
    }


def ensure_element_fields(element):
    """Add required Excalidraw fields that may be missing."""
    defaults = {
        "seed": random.randint(1, 2**31),
        "version": 1,
        "versionNonce": random.randint(1, 2**31),
        "updated": 1709000000000,
        "link": None,
        "groupIds": [],
    }
    for key, val in defaults.items():
        if key not in element:
            element[key] = val

    if element.get("type") == "text":
        if "originalText" not in element:
            element["originalText"] = element.get("text", "")
        if "lineHeight" not in element:
            element["lineHeight"] = 1.25
        if "autoResize" not in element:
            element["autoResize"] = True

    return element


def build_excalidraw(elements, files=None):
    """Wrap elements in the Excalidraw file format."""
    elements = [ensure_element_fields(e) for e in elements]

    return {
        "type": "excalidraw",
        "version": 2,
        "source": "https://excalidraw.com",
        "elements": elements,
        "appState": {
            "gridSize": None,
            "viewBackgroundColor": COLORS["white"],
        },
        "files": files or {},
    }


def build_from_spec(spec, offset_x=0, offset_y=0, image_map=None):
    """Build Excalidraw elements from a high-level spec dict.

    offset_x/offset_y shift all coordinates — used by combine command.
    image_map: dict of {name: file_path} for embedding images.

    Returns (elements, files_dict).
    """
    elements = []
    files = {}
    node_centers = {}
    image_map = image_map or {}

    # Draw lines first (dividers, underlines)
    for line in spec.get("lines", []):
        elements.extend(make_line(
            line["x1"] + offset_x, line["y1"] + offset_y,
            line["x2"] + offset_x, line["y2"] + offset_y,
            color=line.get("color", "dark"),
            stroke_width=line.get("stroke_width", 1),
        ))

    # Draw groups (background areas)
    for group in spec.get("groups", []):
        elements.extend(make_group_background(
            group["x"] + offset_x, group["y"] + offset_y,
            group["w"], group["h"],
            color=group.get("color", "purple"),
            label=group.get("label", ""),
        ))

    # Draw nodes
    for node in spec.get("nodes", []):
        style = node.get("style", "outline")
        label = node.get("label", "")

        node_elements = make_rectangle(
            node["x"] + offset_x, node["y"] + offset_y,
            node.get("w", 200), node.get("h", 80),
            color=node.get("color", "dark"),
            label=label,
            font_size=node.get("font_size", 24),
            style=style,
        )
        elements.extend(node_elements)

        cx = node["x"] + offset_x + node.get("w", 200) / 2
        cy = node["y"] + offset_y + node.get("h", 80) / 2
        node_centers[node["id"]] = (cx, cy, node.get("w", 200), node.get("h", 80))

    # Draw arrows
    for arrow in spec.get("arrows", []):
        from_id = arrow["from"]
        to_id = arrow["to"]

        if from_id not in node_centers or to_id not in node_centers:
            continue

        fx, fy, fw, fh = node_centers[from_id]
        tx, ty, tw, th = node_centers[to_id]

        dx = tx - fx
        dy = ty - fy

        if abs(dx) > abs(dy):
            if dx > 0:
                start_x = fx + fw / 2
                end_x = tx - tw / 2
            else:
                start_x = fx - fw / 2
                end_x = tx + tw / 2
            start_y = fy
            end_y = ty
        else:
            start_x = fx
            end_x = tx
            if dy > 0:
                start_y = fy + fh / 2
                end_y = ty - th / 2
            else:
                start_y = fy - fh / 2
                end_y = ty + th / 2

        elements.extend(make_arrow(
            start_x, start_y, end_x, end_y,
            color=arrow.get("color", "dark"),
            label=arrow.get("label", ""),
        ))

    # Draw titles (standalone text)
    for title in spec.get("titles", []):
        elements.extend(make_text(
            title["x"] + offset_x, title["y"] + offset_y,
            title["text"],
            color=title.get("color", "dark"),
            font_size=title.get("font_size", 36),
            align=title.get("align", "left"),
        ))

    # Draw embedded images
    for img in spec.get("images", []):
        img_name = img.get("src", "")
        img_path = image_map.get(img_name, img_name)
        file_id, file_data = embed_image_file(img_path)
        if file_id:
            files[file_id] = file_data
            elements.extend(make_image(
                img["x"] + offset_x, img["y"] + offset_y,
                img.get("w", 200), img.get("h", 200),
                file_id,
            ))

    return elements, files


def main():
    parser = argparse.ArgumentParser(description="Excalidraw diagram generator")
    subparsers = parser.add_subparsers(dest="command")

    # Build command — single diagram
    build = subparsers.add_parser("build", help="Build diagram from spec JSON")
    build.add_argument("--spec", required=True, help="Path to spec JSON file")
    build.add_argument("--output", required=True, help="Output .excalidraw file path")
    build.add_argument("--export-png", action="store_true", help="Also export to PNG")
    build.add_argument("--images", nargs="*", help="Image mappings: name:path")

    # Combine command — multiple diagrams on one canvas
    combine = subparsers.add_parser("combine", help="Combine multiple specs into one file")
    combine.add_argument("--specs", nargs="+", required=True, help="Spec JSON files")
    combine.add_argument("--output", required=True, help="Output .excalidraw file path")
    combine.add_argument("--cols", type=int, default=2, help="Columns in grid (default: 2)")
    combine.add_argument("--gap", type=int, default=400, help="Gap between diagrams (default: 400)")
    combine.add_argument("--images", nargs="*", help="Image mappings: name:path")

    args = parser.parse_args()

    if args.command == "build":
        with open(args.spec, "r") as f:
            spec = json.load(f)

        image_map = {}
        for img_arg in getattr(args, "images", None) or []:
            if ":" in img_arg:
                name, path = img_arg.split(":", 1)
                image_map[name] = path

        elements, files = build_from_spec(spec, image_map=image_map)
        diagram = build_excalidraw(elements, files)
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)

        with open(args.output, "w") as f:
            json.dump(diagram, f, indent=2)
        print(f"Saved diagram to: {args.output}", file=sys.stderr)

    elif args.command == "combine":
        all_elements = []
        all_files = {}
        cell_w = 1920
        cell_h = 1080

        image_map = {}
        for img_arg in getattr(args, "images", None) or []:
            if ":" in img_arg:
                name, path = img_arg.split(":", 1)
                image_map[name] = path

        for i, spec_path in enumerate(args.specs):
            col = i % args.cols
            row = i // args.cols
            offset_x = col * (cell_w + args.gap)
            offset_y = row * (cell_h + args.gap)

            with open(spec_path, "r") as f:
                spec = json.load(f)

            elements, files = build_from_spec(spec, offset_x, offset_y, image_map)
            all_elements.extend(elements)
            all_files.update(files)

        diagram = build_excalidraw(all_elements, all_files)
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)

        with open(args.output, "w") as f:
            json.dump(diagram, f, indent=2)
        print(f"Saved combined diagram ({len(args.specs)} diagrams) to: {args.output}",
              file=sys.stderr)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
