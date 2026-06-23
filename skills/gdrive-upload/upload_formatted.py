#!/usr/bin/env python3
"""
Google Drive Upload with Markdown formatting.

Converts markdown to proper Google Docs formatting:
- # / ## / ### become real Heading 1/2/3
- **bold** becomes bold text
- `inline code` becomes monospace
- ```code blocks``` become monospace paragraphs with grey background
- - bullet items become real bullet lists
- 1. numbered items become real numbered lists
- | tables | become formatted tables
- > blockquotes become indented italic text
- [text](url) becomes clickable links
- --- becomes a horizontal rule (thin paragraph)

Usage:
    python3 upload_formatted.py --file /path/to/file.md --title "My Document"
"""

import argparse
import json
import os
import re
import sys
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Config dir holds your Google OAuth files. Override with env vars if you keep
# them elsewhere. Run authorize.py once to create token.json from credentials.json.
CONFIG_DIR = os.environ.get(
    "GDRIVE_CONFIG_DIR", os.path.expanduser("~/.claude/.gdrive")
)
TOKEN_PATH = os.environ.get("GDRIVE_TOKEN_PATH", os.path.join(CONFIG_DIR, "token.json"))


def get_services():
    if not os.path.exists(TOKEN_PATH):
        sys.exit(
            f"No OAuth token found at {TOKEN_PATH}.\n"
            "Run the one-time authorizer first:\n"
            "    python3 ~/.claude/skills/gdrive-upload/authorize.py"
        )
    with open(TOKEN_PATH, "r") as f:
        token_data = json.load(f)
    scopes = token_data.get("scopes", [])
    creds = Credentials.from_authorized_user_file(TOKEN_PATH, scopes)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(TOKEN_PATH, "w") as f:
            f.write(creds.to_json())
    drive_service = build("drive", "v3", credentials=creds)
    docs_service = build("docs", "v1", credentials=creds)
    return drive_service, docs_service


def parse_markdown(md_text):
    """Parse markdown into a list of blocks with type and content."""
    lines = md_text.split("\n")
    blocks = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # Skip empty lines
        if not line.strip():
            i += 1
            continue

        # Horizontal rule
        if re.match(r"^---+\s*$", line):
            blocks.append({"type": "hr"})
            i += 1
            continue

        # Code block
        if line.strip().startswith("```"):
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            i += 1  # skip closing ```
            blocks.append({"type": "code", "text": "\n".join(code_lines)})
            continue

        # Table
        if "|" in line and i + 1 < len(lines) and re.match(r"^\|[\s\-:|]+\|", lines[i + 1]):
            table_lines = []
            while i < len(lines) and "|" in lines[i]:
                # Skip separator row
                if not re.match(r"^\|[\s\-:|]+\|$", lines[i]):
                    cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                    table_lines.append(cells)
                i += 1
            blocks.append({"type": "table", "rows": table_lines})
            continue

        # Headings
        h_match = re.match(r"^(#{1,6})\s+(.*)", line)
        if h_match:
            level = len(h_match.group(1))
            blocks.append({"type": f"h{level}", "text": h_match.group(2)})
            i += 1
            continue

        # Blockquote
        if line.strip().startswith(">"):
            text = line.strip().lstrip(">").strip()
            blocks.append({"type": "blockquote", "text": text})
            i += 1
            continue

        # Bullet list
        bullet_match = re.match(r"^(\s*)[-*]\s+(.*)", line)
        if bullet_match:
            items = []
            while i < len(lines):
                bm = re.match(r"^(\s*)[-*]\s+(.*)", lines[i])
                if bm:
                    indent = len(bm.group(1))
                    items.append({"text": bm.group(2), "indent": indent})
                    i += 1
                elif lines[i].strip() == "":
                    i += 1
                    # Check if next line continues the list
                    if i < len(lines) and re.match(r"^(\s*)[-*]\s+", lines[i]):
                        continue
                    break
                else:
                    break
            blocks.append({"type": "bullet_list", "items": items})
            continue

        # Numbered list
        num_match = re.match(r"^(\s*)\d+\.\s+(.*)", line)
        if num_match:
            items = []
            while i < len(lines):
                nm = re.match(r"^(\s*)\d+\.\s+(.*)", lines[i])
                if nm:
                    items.append({"text": nm.group(2), "indent": len(nm.group(1))})
                    i += 1
                elif lines[i].strip() == "":
                    i += 1
                    if i < len(lines) and re.match(r"^(\s*)\d+\.\s+", lines[i]):
                        continue
                    break
                else:
                    break
            blocks.append({"type": "numbered_list", "items": items})
            continue

        # Regular paragraph
        blocks.append({"type": "paragraph", "text": line})
        i += 1

    return blocks


def build_doc_requests(blocks):
    """Convert parsed blocks into Google Docs API batchUpdate requests."""
    requests = []
    idx = 1  # cursor position in the doc (starts at 1)

    def insert_text(text, add_newline=True):
        nonlocal idx
        full = text + ("\n" if add_newline else "")
        requests.append({
            "insertText": {
                "location": {"index": idx},
                "text": full
            }
        })
        start = idx
        idx += len(full)
        return start, start + len(text)

    def apply_heading(start, end, level):
        named = {1: "HEADING_1", 2: "HEADING_2", 3: "HEADING_3",
                 4: "HEADING_4", 5: "HEADING_5", 6: "HEADING_6"}
        style = named.get(level, "HEADING_3")
        requests.append({
            "updateParagraphStyle": {
                "range": {"startIndex": start, "endIndex": end + 1},
                "paragraphStyle": {"namedStyleType": style},
                "fields": "namedStyleType"
            }
        })

    def apply_inline_formatting(text, text_start):
        """Apply bold, inline code, and links within a text range."""
        # Find **bold** patterns
        for m in re.finditer(r"\*\*(.+?)\*\*", text):
            s = text_start + m.start()
            e = text_start + m.end()
            # We can't easily remove the ** markers after insert,
            # so we handle this differently below
            pass

        # We'll handle inline formatting in a second pass
        pass

    def insert_rich_text(text, add_newline=True):
        """Insert text with inline markdown converted to formatting."""
        nonlocal idx

        # Parse inline elements: **bold**, `code`, [link](url)
        segments = []
        pos = 0
        # Combined pattern for bold, inline code, and links
        pattern = re.compile(
            r"(\*\*(.+?)\*\*)"       # bold
            r"|(`([^`]+?)`)"          # inline code
            r"|(\[([^\]]+?)\]\(([^)]+?)\))"  # link
        )

        for m in pattern.finditer(text):
            # Add plain text before this match
            if m.start() > pos:
                segments.append({"text": text[pos:m.start()], "fmt": "plain"})

            if m.group(2):  # bold
                segments.append({"text": m.group(2), "fmt": "bold"})
            elif m.group(4):  # inline code
                segments.append({"text": m.group(4), "fmt": "code"})
            elif m.group(6):  # link
                segments.append({"text": m.group(6), "fmt": "link", "url": m.group(7)})

            pos = m.end()

        # Add remaining plain text
        if pos < len(text):
            segments.append({"text": text[pos:], "fmt": "plain"})

        if not segments:
            segments = [{"text": text, "fmt": "plain"}]

        full_text = "".join(s["text"] for s in segments)
        if add_newline:
            full_text += "\n"

        requests.append({
            "insertText": {
                "location": {"index": idx},
                "text": full_text
            }
        })

        # Apply formatting to each segment
        seg_start = idx
        for seg in segments:
            seg_end = seg_start + len(seg["text"])

            if seg["fmt"] == "bold":
                requests.append({
                    "updateTextStyle": {
                        "range": {"startIndex": seg_start, "endIndex": seg_end},
                        "textStyle": {"bold": True},
                        "fields": "bold"
                    }
                })
            elif seg["fmt"] == "code":
                requests.append({
                    "updateTextStyle": {
                        "range": {"startIndex": seg_start, "endIndex": seg_end},
                        "textStyle": {
                            "weightedFontFamily": {"fontFamily": "Roboto Mono"},
                            "backgroundColor": {
                                "color": {"rgbColor": {"red": 0.93, "green": 0.93, "blue": 0.93}}
                            },
                            "fontSize": {"magnitude": 9, "unit": "PT"}
                        },
                        "fields": "weightedFontFamily,backgroundColor,fontSize"
                    }
                })
            elif seg["fmt"] == "link":
                requests.append({
                    "updateTextStyle": {
                        "range": {"startIndex": seg_start, "endIndex": seg_end},
                        "textStyle": {
                            "link": {"url": seg["url"]},
                            "foregroundColor": {
                                "color": {"rgbColor": {"red": 0.06, "green": 0.36, "blue": 0.72}}
                            }
                        },
                        "fields": "link,foregroundColor"
                    }
                })

            seg_start = seg_end

        start = idx
        idx += len(full_text)
        return start, start + len(full_text) - (1 if add_newline else 0)

    for block in blocks:
        btype = block["type"]

        if btype == "hr":
            # Insert a thin line as a styled paragraph
            start, end = insert_text("─" * 50)
            requests.append({
                "updateTextStyle": {
                    "range": {"startIndex": start, "endIndex": end},
                    "textStyle": {
                        "foregroundColor": {
                            "color": {"rgbColor": {"red": 0.75, "green": 0.75, "blue": 0.75}}
                        },
                        "fontSize": {"magnitude": 6, "unit": "PT"}
                    },
                    "fields": "foregroundColor,fontSize"
                }
            })

        elif btype.startswith("h"):
            level = int(btype[1])
            start, end = insert_rich_text(block["text"])
            apply_heading(start, end, level)

        elif btype == "blockquote":
            start, end = insert_rich_text(block["text"])
            requests.append({
                "updateTextStyle": {
                    "range": {"startIndex": start, "endIndex": end},
                    "textStyle": {"italic": True},
                    "fields": "italic"
                }
            })
            requests.append({
                "updateParagraphStyle": {
                    "range": {"startIndex": start, "endIndex": end},
                    "paragraphStyle": {
                        "indentStart": {"magnitude": 36, "unit": "PT"},
                        "borderLeft": {
                            "color": {"color": {"rgbColor": {"red": 0.7, "green": 0.7, "blue": 0.7}}},
                            "width": {"magnitude": 3, "unit": "PT"},
                            "padding": {"magnitude": 12, "unit": "PT"},
                            "dashStyle": "SOLID"
                        }
                    },
                    "fields": "indentStart,borderLeft"
                }
            })

        elif btype == "code":
            code_text = block["text"]
            start, end = insert_text(code_text)
            # Monospace font
            requests.append({
                "updateTextStyle": {
                    "range": {"startIndex": start, "endIndex": end},
                    "textStyle": {
                        "weightedFontFamily": {"fontFamily": "Roboto Mono"},
                        "fontSize": {"magnitude": 9, "unit": "PT"},
                        "foregroundColor": {
                            "color": {"rgbColor": {"red": 0.2, "green": 0.2, "blue": 0.2}}
                        }
                    },
                    "fields": "weightedFontFamily,fontSize,foregroundColor"
                }
            })
            # Grey background on paragraph
            requests.append({
                "updateParagraphStyle": {
                    "range": {"startIndex": start, "endIndex": end + 1},
                    "paragraphStyle": {
                        "shading": {
                            "backgroundColor": {
                                "color": {"rgbColor": {"red": 0.95, "green": 0.95, "blue": 0.95}}
                            }
                        },
                        "indentStart": {"magnitude": 18, "unit": "PT"},
                        "indentEnd": {"magnitude": 18, "unit": "PT"},
                        "spaceAbove": {"magnitude": 6, "unit": "PT"},
                        "spaceBelow": {"magnitude": 6, "unit": "PT"}
                    },
                    "fields": "shading,indentStart,indentEnd,spaceAbove,spaceBelow"
                }
            })

        elif btype == "bullet_list":
            for item in block["items"]:
                start, end = insert_rich_text(item["text"])
                nesting = min(item.get("indent", 0) // 2, 3)
                requests.append({
                    "createParagraphBullets": {
                        "range": {"startIndex": start, "endIndex": end},
                        "bulletPreset": "BULLET_DISC_CIRCLE_SQUARE"
                    }
                })
                if nesting > 0:
                    requests.append({
                        "updateParagraphStyle": {
                            "range": {"startIndex": start, "endIndex": end},
                            "paragraphStyle": {
                                "indentStart": {"magnitude": 36 * (nesting + 1), "unit": "PT"},
                                "indentFirstLine": {"magnitude": 18 * (nesting + 1), "unit": "PT"}
                            },
                            "fields": "indentStart,indentFirstLine"
                        }
                    })

        elif btype == "numbered_list":
            for item in block["items"]:
                start, end = insert_rich_text(item["text"])
                requests.append({
                    "createParagraphBullets": {
                        "range": {"startIndex": start, "endIndex": end},
                        "bulletPreset": "NUMBERED_DECIMAL_NESTED"
                    }
                })

        elif btype == "table":
            rows = block["rows"]
            if not rows:
                continue
            # Render table as formatted text lines (avoids complex Google Docs table indexing)
            n_cols = max(len(r) for r in rows)
            # Calculate column widths
            col_widths = [0] * n_cols
            for row in rows:
                for c in range(n_cols):
                    cell = row[c] if c < len(row) else ""
                    # Strip markdown for width calc
                    clean = re.sub(r"\*\*(.+?)\*\*", r"\1", cell)
                    clean = re.sub(r"`([^`]+)`", r"\1", clean)
                    clean = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", clean)
                    col_widths[c] = max(col_widths[c], len(clean))

            for r, row in enumerate(rows):
                parts = []
                for c in range(n_cols):
                    cell = row[c] if c < len(row) else ""
                    clean = re.sub(r"\*\*(.+?)\*\*", r"\1", cell)
                    clean = re.sub(r"`([^`]+)`", r"\1", clean)
                    clean = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", clean)
                    parts.append(clean.ljust(col_widths[c]))
                line_text = "  ".join(parts)
                start, end = insert_text(line_text)
                # Monospace for table alignment
                requests.append({
                    "updateTextStyle": {
                        "range": {"startIndex": start, "endIndex": end},
                        "textStyle": {
                            "weightedFontFamily": {"fontFamily": "Roboto Mono"},
                            "fontSize": {"magnitude": 9, "unit": "PT"}
                        },
                        "fields": "weightedFontFamily,fontSize"
                    }
                })
                # Bold header row
                if r == 0:
                    requests.append({
                        "updateTextStyle": {
                            "range": {"startIndex": start, "endIndex": end},
                            "textStyle": {"bold": True},
                            "fields": "bold"
                        }
                    })
                    # Add separator after header
                    sep = "  ".join(["─" * w for w in col_widths])
                    sep_start, sep_end = insert_text(sep)
                    requests.append({
                        "updateTextStyle": {
                            "range": {"startIndex": sep_start, "endIndex": sep_end},
                            "textStyle": {
                                "weightedFontFamily": {"fontFamily": "Roboto Mono"},
                                "fontSize": {"magnitude": 9, "unit": "PT"},
                                "foregroundColor": {
                                    "color": {"rgbColor": {"red": 0.6, "green": 0.6, "blue": 0.6}}
                                }
                            },
                            "fields": "weightedFontFamily,fontSize,foregroundColor"
                        }
                    })

        elif btype == "paragraph":
            insert_rich_text(block["text"])

    return requests


def upload_formatted(title, md_content, folder_id=None):
    drive_service, docs_service = get_services()

    # Create empty doc
    doc = docs_service.documents().create(body={"title": title}).execute()
    doc_id = doc.get("documentId")

    # Parse and build formatting requests
    blocks = parse_markdown(md_content)
    doc_requests = build_doc_requests(blocks)

    # Send all requests in one batch (API supports up to 500)
    # Split into chunks of 450 to stay safe
    batch_size = 450
    for i in range(0, len(doc_requests), batch_size):
        batch = doc_requests[i:i + batch_size]
        try:
            docs_service.documents().batchUpdate(
                documentId=doc_id,
                body={"requests": batch}
            ).execute()
        except Exception as e:
            print(f"Error in batch {i//batch_size + 1}: {e}", file=sys.stderr)
            raise

    # Move to folder if specified
    if folder_id:
        file = drive_service.files().get(fileId=doc_id, fields="parents").execute()
        previous_parents = ",".join(file.get("parents", []))
        drive_service.files().update(
            fileId=doc_id,
            addParents=folder_id,
            removeParents=previous_parents,
            fields="id, parents",
        ).execute()

    # Make shareable
    drive_service.permissions().create(
        fileId=doc_id, body={"type": "anyone", "role": "reader"}
    ).execute()

    return f"https://docs.google.com/document/d/{doc_id}/edit"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", help="Path to markdown file")
    parser.add_argument("--title", required=True)
    parser.add_argument("--folder", help="Google Drive folder ID")
    parser.add_argument("--stdin", action="store_true")
    args = parser.parse_args()

    if args.stdin:
        content = sys.stdin.read()
    elif args.file:
        with open(args.file, "r") as f:
            content = f.read()
    else:
        print("Error: provide either --file or --stdin", file=sys.stderr)
        sys.exit(1)

    url = upload_formatted(args.title, content, args.folder)
    print(url)


if __name__ == "__main__":
    main()
