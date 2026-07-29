from __future__ import annotations

import argparse
import re
import subprocess
from html.parser import HTMLParser
from pathlib import Path


PLACEHOLDER_PATTERN = re.compile(
    r"<(?:task|decision[^>]*|specific unknown[^>]*|name|meaningfully different[^>]*)>",
    re.IGNORECASE,
)
NETWORK_URL_PATTERN = re.compile(r"^(?:https?:)?//", re.IGNORECASE)
NETWORK_CODE_PATTERN = re.compile(
    r"\b(?:fetch|WebSocket|EventSource)\s*\(\s*['\"](?:https?:)?//",
    re.IGNORECASE,
)
NETWORK_ATTRIBUTES = {"action", "formaction", "href", "poster", "src"}
RESOURCE_TAGS = {"audio", "embed", "iframe", "img", "link", "object", "script", "source", "video"}


class PrototypeParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.doctype = False
        self.tags: set[str] = set()
        self.ids: list[str] = []
        self.controls: list[tuple[str, dict[str, str | None]]] = []
        self.panels: list[dict[str, str | None]] = []
        self.text: list[str] = []
        self.styles: list[str] = []
        self.scripts: list[str] = []
        self.panel_text: dict[str, list[str]] = {}
        self.external_resources: list[str] = []
        self.has_viewport = False
        self._in_style = False
        self._in_script = False
        self._active_panel: str | None = None
        self._panel_depth = 0

    def handle_decl(self, decl: str) -> None:
        if decl.strip().lower() == "doctype html":
            self.doctype = True

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if self._active_panel is not None:
            self._panel_depth += 1
        self.tags.add(tag)
        element_id = attributes.get("id")
        if element_id:
            self.ids.append(element_id)
        if attributes.get("data-direction") is not None:
            self.controls.append((tag, attributes))
        if attributes.get("data-panel") is not None:
            self.panels.append(attributes)
            self._active_panel = attributes.get("data-panel")
            self._panel_depth = 1
            if self._active_panel:
                self.panel_text.setdefault(self._active_panel, [])
        if tag == "meta" and attributes.get("name", "").lower() == "viewport":
            self.has_viewport = True
        if tag == "style":
            self._in_style = True
        if tag == "script" and not attributes.get("src"):
            self._in_script = True

        for name, value in attrs:
            if name not in NETWORK_ATTRIBUTES or not value:
                continue
            normalized = value.strip()
            allowed_inline = normalized.startswith(("#", "data:"))
            if not allowed_inline and (
                tag in RESOURCE_TAGS
                or name in {"action", "formaction", "poster", "src"}
                or NETWORK_URL_PATTERN.match(normalized)
            ):
                self.external_resources.append(f"{tag}[{name}={value!r}]")

    def handle_endtag(self, tag: str) -> None:
        if tag == "style":
            self._in_style = False
        if tag == "script":
            self._in_script = False
        if self._active_panel is not None:
            self._panel_depth -= 1
            if self._panel_depth == 0:
                self._active_panel = None

    def handle_data(self, data: str) -> None:
        self.text.append(data)
        if self._in_style:
            self.styles.append(data)
        if self._in_script:
            self.scripts.append(data)
        if self._active_panel:
            self.panel_text[self._active_panel].append(data)


def validate_prototype(path: Path) -> None:
    path = path.resolve()
    if not path.is_file():
        raise ValueError(f"visual prototype does not exist: {path}")
    if path.suffix.lower() != ".html":
        raise ValueError(f"visual prototype must be an HTML file: {path}")

    source = path.read_text(encoding="utf-8")
    parser = PrototypeParser()
    parser.feed(source)
    parser.close()

    errors: list[str] = []
    visible_text = " ".join(parser.text)
    normalized_text = " ".join(visible_text.split()).lower()
    styles = "\n".join(parser.styles)
    scripts = "\n".join(parser.scripts)

    if not parser.doctype:
        errors.append("missing <!doctype html>")
    for tag in ("html", "head", "body", "title", "style"):
        if tag not in parser.tags:
            errors.append(f"missing required <{tag}> element")
    if not parser.has_viewport:
        errors.append("missing responsive viewport metadata")
    if "@media" not in styles:
        errors.append("missing responsive @media rule")

    placeholder = PLACEHOLDER_PATTERN.search(visible_text)
    if placeholder:
        errors.append(f"unreplaced starter placeholder: {placeholder.group(0)}")

    if "prototype" not in normalized_text or not any(
        phrase in normalized_text
        for phrase in ("not production", "non-production", "disposable prototype")
    ):
        errors.append("missing clear prototype/non-production label")
    if not any(word in normalized_text for word in ("fake", "sanitized", "fictional", "sample data")):
        errors.append("missing an explicit fake or sanitized data label")

    if parser.external_resources:
        errors.append(f"external resource is not allowed: {parser.external_resources[0]}")
    css_urls = re.findall(r"url\(\s*['\"]?([^)'\"]+)", styles, re.IGNORECASE)
    if re.search(r"@import\s+", styles, re.IGNORECASE) or any(
        not value.strip().startswith(("data:", "#")) for value in css_urls
    ):
        errors.append("external resource is not allowed in CSS")
    if NETWORK_CODE_PATTERN.search(source):
        errors.append("external endpoint is not allowed in prototype code")
    if len(parser.ids) != len(set(parser.ids)):
        errors.append("element ids must be unique")

    directions: set[str] = set()
    pressed_count = 0
    panel_ids = {panel.get("id") for panel in parser.panels if panel.get("id")}
    panel_directions = {
        panel.get("data-panel") for panel in parser.panels if panel.get("data-panel")
    }
    for tag, attributes in parser.controls:
        direction = attributes.get("data-direction")
        if tag != "button" or attributes.get("type") != "button":
            errors.append("direction controls must be type=button elements")
        if not direction:
            errors.append("direction control has an empty data-direction")
        elif direction in directions:
            errors.append(f"duplicate direction: {direction}")
        else:
            directions.add(direction)
        pressed = attributes.get("aria-pressed")
        if pressed not in {"true", "false"}:
            errors.append(f"direction {direction or '<unknown>'} requires aria-pressed=true or false")
        elif pressed == "true":
            pressed_count += 1
        controlled = attributes.get("aria-controls")
        if not controlled:
            errors.append(f"direction {direction or '<unknown>'} requires aria-controls")
        elif controlled not in panel_ids:
            errors.append(f"direction {direction or '<unknown>'} controls missing panel {controlled}")

    if len(parser.panels) < 2:
        errors.append("at least two direction panels are required")
    panel_direction_list: list[str] = []
    for panel in parser.panels:
        direction = panel.get("data-panel")
        if not panel.get("id"):
            errors.append(f"panel {direction or '<unknown>'} requires an id")
        if not direction:
            errors.append("direction panel has an empty data-panel")
        else:
            panel_direction_list.append(direction)
        if not (panel.get("aria-label") or panel.get("aria-labelledby")):
            errors.append(f"panel {direction or '<unknown>'} requires an accessible label")
    if len(panel_direction_list) != len(set(panel_direction_list)):
        errors.append("direction panel values must be unique")

    if parser.controls:
        if len(parser.controls) < 2:
            errors.append("interactive prototypes require at least two direction controls")
        if pressed_count != 1:
            errors.append("exactly one direction must start with aria-pressed=true")
        if directions != panel_directions:
            errors.append("direction controls and panels must use the same direction values")
        if not scripts.strip() or not re.search(r"\b(?:addEventListener|onclick)\b", scripts):
            errors.append("missing direction interaction script")
        if "aria-pressed" not in scripts or not re.search(r"\.hidden\b|hidden\s*=", scripts):
            errors.append("interaction script must update pressed and visible direction state")
    elif any("hidden" in panel for panel in parser.panels):
        errors.append("static comparison panels must all be visible")
    panel_content = {
        direction: " ".join(" ".join(text).split()).lower()
        for direction, text in parser.panel_text.items()
    }
    if any(not content for content in panel_content.values()):
        errors.append("each direction panel requires visible content")
    if len(panel_content) >= 2 and len(set(panel_content.values())) != len(panel_content):
        errors.append("direction panels must not contain identical content")

    if errors:
        raise ValueError("Invalid visual prototype:\n- " + "\n- ".join(errors))

    print(f"Validated visual prototype: {path}")


def committed_prototypes(root: Path) -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "--", "docs/code-territory"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    return sorted(
        root / relative
        for relative in result.stdout.splitlines()
        if relative.endswith("/visual-prototype.html")
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate disposable visual prototype HTML files.")
    parser.add_argument("paths", nargs="*", type=Path)
    parser.add_argument(
        "--committed",
        action="store_true",
        help="Validate visual prototypes committed under docs/code-territory/.",
    )
    args = parser.parse_args()

    paths = list(args.paths)
    if args.committed:
        repository_root = Path(__file__).resolve().parents[3]
        paths.extend(committed_prototypes(repository_root))
    if not paths:
        if args.committed:
            print("No committed visual prototypes found under docs/code-territory/.")
            return
        parser.error("provide at least one prototype path or use --committed")

    for path in dict.fromkeys(paths):
        validate_prototype(path)


if __name__ == "__main__":
    main()
