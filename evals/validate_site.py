from __future__ import annotations

import sys
import math
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
SITE_ROOT = ROOT / "site"
INDEX_PATH = SITE_ROOT / "index.html"
OKLCH_TOKEN = re.compile(
    r"--(?P<name>[a-z0-9-]+):\s*oklch\((?P<lightness>[0-9.]+)\s+(?P<chroma>[0-9.]+)\s+(?P<hue>[0-9.]+)\)"
)


class SiteParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.tags: list[str] = []
        self.ids: list[str] = []
        self.links: list[str] = []
        self.resource_urls: list[str] = []
        self.buttons: list[dict[str, str]] = []
        self.mode_buttons: list[dict[str, str]] = []
        self.mode_panels: list[dict[str, str]] = []
        self.capability_buttons: list[dict[str, str]] = []
        self.meta_names: dict[str, str] = {}
        self.html_lang = ""
        self.title_depth = 0
        self.title_text: list[str] = []
        self.h1_count = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = {name: value or "" for name, value in attrs}
        self.tags.append(tag)

        if tag == "html":
            self.html_lang = attributes.get("lang", "")
        if element_id := attributes.get("id"):
            self.ids.append(element_id)
        if tag == "title":
            self.title_depth += 1
        if tag == "h1":
            self.h1_count += 1
        if tag == "meta" and attributes.get("name"):
            self.meta_names[attributes["name"].lower()] = attributes.get("content", "")
        if tag == "a" and attributes.get("href"):
            self.links.append(attributes["href"])
        if tag == "button":
            self.buttons.append(attributes)
            if "data-mode" in attributes:
                self.mode_buttons.append(attributes)
            if "data-capability" in attributes:
                self.capability_buttons.append(attributes)
        if "data-mode-panel" in attributes:
            self.mode_panels.append(attributes)

        resource_attribute = {
            "script": "src",
            "link": "href",
            "img": "src",
            "source": "src",
            "video": "src",
            "audio": "src",
            "iframe": "src",
        }.get(tag)
        if resource_attribute and attributes.get(resource_attribute):
            self.resource_urls.append(attributes[resource_attribute])

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self.title_depth -= 1

    def handle_data(self, data: str) -> None:
        if self.title_depth:
            self.title_text.append(data)


def oklch_luminance(lightness: float, chroma: float, hue: float) -> float:
    angle = math.radians(hue)
    a = chroma * math.cos(angle)
    b = chroma * math.sin(angle)
    l_root = lightness + 0.3963377774 * a + 0.2158037573 * b
    m_root = lightness - 0.1055613458 * a - 0.0638541728 * b
    s_root = lightness - 0.0894841775 * a - 1.291485548 * b
    l_value, m_value, s_value = l_root**3, m_root**3, s_root**3
    red = 4.0767416621 * l_value - 3.3077115913 * m_value + 0.2309699292 * s_value
    green = -1.2684380046 * l_value + 2.6097574011 * m_value - 0.3413193965 * s_value
    blue = -0.0041960863 * l_value - 0.7034186147 * m_value + 1.707614701 * s_value
    red, green, blue = (max(0.0, min(1.0, channel)) for channel in (red, green, blue))
    return 0.2126 * red + 0.7152 * green + 0.0722 * blue


def contrast_ratio(first: float, second: float) -> float:
    lighter, darker = max(first, second), min(first, second)
    return (lighter + 0.05) / (darker + 0.05)


def validate_html_text(text: str, *, site_root: Path = SITE_ROOT) -> list[str]:
    parser = SiteParser()
    parser.feed(text)
    errors: list[str] = []

    for tag in ("html", "head", "body", "header", "main", "footer", "title", "style", "script"):
        if tag not in parser.tags:
            errors.append(f"missing required <{tag}> element")

    if parser.html_lang.lower() != "en":
        errors.append("html lang must be en")
    if not "".join(parser.title_text).strip():
        errors.append("title must not be empty")
    if parser.h1_count != 1:
        errors.append(f"expected exactly one h1, found {parser.h1_count}")
    if not parser.meta_names.get("viewport"):
        errors.append("missing viewport metadata")
    if not parser.meta_names.get("description"):
        errors.append("missing description metadata")
    if "main" not in parser.ids:
        errors.append("main landmark must have id=main for the skip link")
    if len(parser.ids) != len(set(parser.ids)):
        errors.append("duplicate element ids are not allowed")

    lowered = text.lower()
    if "skip-link" not in lowered or 'href="#main"' not in lowered:
        errors.append("missing skip link to #main")
    if "prefers-reduced-motion: reduce" not in lowered:
        errors.append("missing reduced-motion media query")
    if "@media (max-width:" not in lowered:
        errors.append("missing responsive narrow-width rule")
    if "disposable prototype" in lowered or "prototype-label" in lowered or "prototype-bar" in lowered:
        errors.append("production site must not contain prototype labelling")
    if any(token in text for token in ("<task>", "TODO", "PLACEHOLDER")):
        errors.append("production site contains an unreplaced placeholder")

    for button in parser.buttons:
        if button.get("type") != "button":
            errors.append("every button must declare type=button")
    if len(parser.mode_buttons) != 4:
        errors.append(f"expected four mode controls, found {len(parser.mode_buttons)}")
    if len(parser.mode_panels) != 4:
        errors.append(f"expected four mode panels, found {len(parser.mode_panels)}")
    if {item.get("data-mode") for item in parser.mode_buttons} != {
        item.get("data-mode-panel") for item in parser.mode_panels
    }:
        errors.append("mode controls and panels must have matching keys")
    if len(parser.capability_buttons) != 6:
        errors.append(f"expected six delivery capability controls, found {len(parser.capability_buttons)}")

    colors = {
        match.group("name"): oklch_luminance(
            float(match.group("lightness")),
            float(match.group("chroma")),
            float(match.group("hue")),
        )
        for match in OKLCH_TOKEN.finditer(text)
    }
    contrast_contracts = (
        ("white", "signal", 4.5),
        ("white", "signal-deep", 4.5),
        ("white", "route-deep", 4.5),
        ("ink", "white", 7.0),
        ("ink-soft", "white", 4.5),
        ("ink", "surface", 7.0),
        ("ink-soft", "surface", 4.5),
        ("route", "white", 3.0),
    )
    for foreground, background, minimum in contrast_contracts:
        if foreground not in colors or background not in colors:
            errors.append(f"missing contrast token: {foreground} or {background}")
            continue
        ratio = contrast_ratio(colors[foreground], colors[background])
        if ratio < minimum:
            errors.append(
                f"contrast {foreground}/{background} is {ratio:.2f}:1; expected at least {minimum:.1f}:1"
            )

    known_ids = set(parser.ids)
    for href in parser.links:
        parsed = urlparse(href)
        if parsed.scheme and parsed.scheme not in {"http", "https", "mailto"}:
            errors.append(f"unsupported link scheme: {href}")
        if href.startswith("#") and href[1:] not in known_ids:
            errors.append(f"broken fragment link: {href}")
        if not parsed.scheme and not href.startswith("#"):
            target = (site_root / parsed.path).resolve()
            if site_root.resolve() not in target.parents and target != site_root.resolve():
                errors.append(f"relative link escapes site root: {href}")
            elif not target.exists():
                errors.append(f"missing relative link target: {href}")

    for resource in parser.resource_urls:
        parsed = urlparse(resource)
        if parsed.scheme or resource.startswith("//"):
            errors.append(f"external runtime resource is not allowed: {resource}")
        elif resource:
            target = (site_root / parsed.path).resolve()
            if not target.exists():
                errors.append(f"missing local resource: {resource}")

    return errors


def validate() -> None:
    if not INDEX_PATH.is_file():
        raise ValueError("missing production site/index.html")
    if not (SITE_ROOT / ".nojekyll").is_file():
        raise ValueError("missing site/.nojekyll")

    errors = validate_html_text(INDEX_PATH.read_text(encoding="utf-8"))
    if errors:
        raise ValueError("invalid production site:\n- " + "\n- ".join(errors))
    print("Validated production visual explainer site.")


if __name__ == "__main__":
    try:
        validate()
    except ValueError as error:
        print(error, file=sys.stderr)
        raise SystemExit(1) from error
