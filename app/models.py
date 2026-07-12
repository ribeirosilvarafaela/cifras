"""Database models."""

from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text, UniqueConstraint

from database import Base


class Song(Base):
    __tablename__ = "songs"
    __table_args__ = (UniqueConstraint("artist_slug", "song_slug", name="uq_song_slug"),)

    id = Column(Integer, primary_key=True)
    artist = Column(String(255), nullable=False)
    artist_slug = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    song_slug = Column(String(255), nullable=False)
    youtube_url = Column(String(500))
    cifraclub_url = Column(String(500), nullable=False)
    cifra_json = Column(Text, nullable=False)
    chords_json = Column(Text, nullable=False)
    chord_warnings_json = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    last_scraped_at = Column(DateTime, nullable=False, default=datetime.utcnow)
