"""Application service for cached and scraped songs."""

import json
import re
import unicodedata
from datetime import datetime

from cifraclub import CifraClub
from database import get_session
from models import Song


def slugify(value):
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _loads(value):
    return json.loads(value) if value else []


def _response(song, warning=None):
    result = {
        "id": song.id,
        "artist": song.artist,
        "name": song.name,
        "youtube_url": song.youtube_url,
        "cifraclub_url": song.cifraclub_url,
        "cifra": _loads(song.cifra_json),
        "chords": _loads(song.chords_json),
        "chord_warnings": _loads(song.chord_warnings_json),
    }
    if warning:
        result["warnings"] = [warning]
    return result


def _save(session, data, artist, artist_slug, song, song_slug, existing=None):
    now = datetime.utcnow()
    target = existing or Song(
        artist=artist,
        artist_slug=artist_slug,
        name=song,
        song_slug=song_slug,
        cifra_json="[]",
        chords_json="[]",
        chord_warnings_json="[]",
    )
    target.artist = data.get("artist", artist)
    target.artist_slug = artist_slug
    target.name = data.get("name", song)
    target.song_slug = song_slug
    target.youtube_url = data.get("youtube_url")
    target.cifraclub_url = data.get("cifraclub_url", "")
    target.cifra_json = json.dumps(data.get("cifra", []), ensure_ascii=False)
    target.chords_json = json.dumps(data.get("chords", []), ensure_ascii=False)
    target.chord_warnings_json = json.dumps(data.get("chord_warnings", []), ensure_ascii=False)
    target.updated_at = now
    target.last_scraped_at = now
    session.add(target)
    session.commit()
    session.refresh(target)
    return target


def get_song(artist, song, refresh=False, scraper_cls=CifraClub):
    artist_slug = slugify(artist)
    song_slug = slugify(song)
    session = get_session()
    try:
        saved = session.query(Song).filter_by(
            artist_slug=artist_slug, song_slug=song_slug
        ).first()
        if saved and not refresh:
            return _response(saved)

        scraped = scraper_cls().cifra(artist_slug, song_slug)
        if scraped.get("error"):
            raise RuntimeError(scraped["error"])
        return _response(_save(session, scraped, artist, artist_slug, song, song_slug, saved))
    except Exception:
        session.rollback()
        if saved:
            return _response(saved, "Scraping falhou; versão salva retornada.")
        raise
    finally:
        session.close()


def list_recent(limit=10):
    session = get_session()
    try:
        return [_response(song) for song in session.query(Song).order_by(Song.updated_at.desc()).limit(limit).all()]
    finally:
        session.close()


def list_songs():
    session = get_session()
    try:
        return [_response(song) for song in session.query(Song).order_by(Song.updated_at.desc()).all()]
    finally:
        session.close()


def get_song_by_id(song_id):
    session = get_session()
    try:
        song = session.get(Song, song_id)
        return _response(song) if song else None
    finally:
        session.close()
