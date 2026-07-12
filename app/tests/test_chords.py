from chords import extract_chords, keyboard_svg, remove_tabs


def test_extracts_unique_chords_without_lyrics_or_tabs():
    lines = ["[Intro] C#m7 A9 E E9", "A beautiful song", "E|-----|", "B", "Parte 1 de 5", "E7M(9) E6 B B11/D# E7M", "( C#m7 A9 E )"]
    chords, warnings = extract_chords(lines)
    assert [chord["name"] for chord in chords] == ["C#m7", "A9", "E", "E9", "E7M(9)", "E6", "B", "B11/D#", "E7M"]
    assert not warnings


def test_notes_and_svg():
    chords, _ = extract_chords(["C#m7"])
    assert chords[0]["notes"] == ["C#", "E", "G#", "B"]
    assert 'fill="#ffcc66"' in keyboard_svg("C#m7")
    assert 'fill="#66ccff"' in keyboard_svg("C#m7")


def test_warns_for_unsupported_chords():
    chords, warnings = extract_chords(["C13sus2"])
    assert not chords
    assert warnings == [{"name": "C13sus2", "reason": "unsupported chord"}]


def test_supports_requested_chord_shapes():
    names = ["C", "Cm", "C#m7", "A9", "E", "E9", "E7M", "E7M(9)", "E6", "B", "B11/D#", "Cadd9", "Gsus4", "Cm7(b5)"]
    chords, warnings = extract_chords([" ".join(names)])
    assert [chord["name"] for chord in chords] == names
    assert not warnings


def test_supports_slash_add11_and_removes_tabs():
    lines = ["[Tab - Intro]", "E5 A2", "E|---|", "   down", "[Parte]", "F#m7(11)/C#"]
    assert remove_tabs(lines) == ["[Parte]", "F#m7(11)/C#"]
    chords, warnings = extract_chords(["F#m7(11)/C#", "F#m7(11)/C#"])
    assert chords[0]["notes"] == ["C#", "F#", "A", "E", "B"]
    assert not warnings
