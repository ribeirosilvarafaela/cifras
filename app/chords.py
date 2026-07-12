"""Chord extraction, note calculation and small keyboard diagrams."""

import re
from urllib.parse import quote

from pychord import Chord

ROOT = r"[A-G](?:#|b)?"
CHORD_TOKEN = re.compile(r"^" + ROOT + r"(?:m|min|maj|dim|aug|sus|add|[0-9]|M|\(.*\)|/" + ROOT + r")*$")
TAB_LINE = re.compile(r"^\s*[A-G](?:#|b)?\|[-0-9hHpPxX/\\| ]*$")
SECTION = re.compile(r"^\[[^]]+\]")


def _internal_name(name):
    return (name.replace("7M(9)", "maj9").replace("7M", "maj7")
            .replace("m7(b5)", "m7b5").replace("m7(11)", "m7add11"))


def _tokens(line):
    line = SECTION.sub("", line)
    line = re.sub(r"(?<!\w)\((?=\s)|(?<=\s)\)(?!\w)", " ", line)
    return [token.strip(",.;:") for token in line.split() if token.strip(",.;:")]


def _valid(token):
    if not CHORD_TOKEN.match(token):
        return None
    try:
        return Chord(_internal_name(token)).components()
    except (KeyError, TypeError, ValueError):
        return None


def _looks_like_chord(token):
    return bool(re.match(r"^[A-G](?:#|b)?(?:m|min|maj|dim|aug|sus|add|M|[0-9]|/|\().+", token))


def extract_chords(lines):
    """Return unique chord records and non-fatal parsing warnings."""
    found = []
    warnings = []
    warned = set()
    seen = set()
    for index, line in enumerate(lines):
        if TAB_LINE.match(line) or re.match(r"^\s*Parte\s+\d+\s+de\s+\d+", line, re.I):
            continue
        tokens = _tokens(line)
        parsed = [(token, _valid(token)) for token in tokens]
        strong = [item for item in parsed if item[1] and not re.match(r"^[A-G](?:#|b)?$", item[0])]
        bare = [item for item in parsed if item[1] and re.match(r"^[A-G](?:#|b)?$", item[0])]
        allow_bare = bool(strong or len(bare) > 1 or (len(tokens) == 1 and bare and index + 1 < len(lines) and TAB_LINE.match(lines[index + 1])))
        for token, notes in parsed:
            if not notes and _looks_like_chord(token):
                if token not in warned:
                    warnings.append({"name": token, "reason": "unsupported chord"})
                    warned.add(token)
                continue
            if not notes or (token in [item[0] for item in bare] and not allow_bare):
                continue
            if token in seen:
                continue
            seen.add(token)
            found.append({"name": token, "notes": notes, "diagram": "/chords/diagram.svg?name=" + quote(token, safe="()/")})
    return found, warnings


def remove_tabs(lines):
    """Remove tab sections while keeping the remaining cifra lines intact."""
    result = []
    in_tab = False
    for line in lines:
        if re.match(r"^\s*\[Tab\b", line, re.I):
            in_tab = True
            continue
        if in_tab and re.match(r"^\s*\[", line):
            in_tab = False
        if not in_tab:
            result.append(line)
    return result


def keyboard_svg(name):
    """Render two octaves of a keyboard with chord pitch classes highlighted."""
    flat_to_sharp = {"Db": "C#", "Eb": "D#", "Gb": "F#", "Ab": "G#", "Bb": "A#"}
    notes = {flat_to_sharp.get(note, note) for note in Chord(_internal_name(name)).components()}
    white = ["C", "D", "E", "F", "G", "A", "B"]
    black = {"C#": 0.68, "D#": 1.68, "F#": 3.68, "G#": 4.68, "A#": 5.68}
    white_colors = ("#ffcc66", "#66ccff")
    black_colors = ("#ff9933", "#3399cc")
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="420" height="130" viewBox="0 0 420 130">']
    for octave in range(2):
        for position, note in enumerate(white):
            x = (octave * 7 + position) * 30
            fill = white_colors[octave] if note in notes else "white"
            parts.append(f'<rect x="{x}" y="0" width="30" height="120" fill="{fill}" stroke="black"/>')
        for note, position in black.items():
            x = (octave * 7 + position) * 30
            fill = black_colors[octave] if note in notes else "black"
            parts.append(f'<rect x="{x}" y="0" width="18" height="75" fill="{fill}" stroke="black"/>')
    parts.append("</svg>")
    return "".join(parts)
