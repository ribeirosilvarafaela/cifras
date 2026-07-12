from services import get_song, list_recent, slugify
from database import configure_database, init_db


class FakeScraper:
    calls = 0

    def cifra(self, artist, song):
        FakeScraper.calls += 1
        return {
            'artist': 'Coldplay', 'name': 'The Scientist',
            'youtube_url': 'https://youtube.test/video',
            'cifraclub_url': 'https://cifraclub.test/coldplay/the-scientist',
            'cifra': ['C#m7', 'Come up to meet you'],
            'chords': [{'name': 'C#m7', 'notes': ['C#', 'E', 'G#', 'B'], 'diagram': '/chords/diagram.svg?name=C%23m7'}],
            'chord_warnings': [],
        }


def setup_function():
    configure_database('sqlite:///:memory:')
    init_db()
    FakeScraper.calls = 0


def test_slugify_and_cache_avoid_second_scrape():
    assert slugify('João & Banda') == 'joao-banda'
    first = get_song('Coldplay', 'The Scientist', scraper_cls=FakeScraper)
    second = get_song('coldplay', 'the scientist', scraper_cls=FakeScraper)
    assert first['cifra'] == ['C#m7', 'Come up to meet you']
    assert second['name'] == 'The Scientist'
    assert FakeScraper.calls == 1
    assert len(list_recent()) == 1


def test_refresh_scrapes_again():
    get_song('Coldplay', 'The Scientist', scraper_cls=FakeScraper)
    get_song('Coldplay', 'The Scientist', refresh=True, scraper_cls=FakeScraper)
    assert FakeScraper.calls == 2


class FailingScraper:
    def cifra(self, artist, song):
        raise RuntimeError('network failure')


def test_failed_refresh_returns_saved_version_with_warning():
    saved = get_song('Coldplay', 'The Scientist', scraper_cls=FakeScraper)
    result = get_song('Coldplay', 'The Scientist', refresh=True, scraper_cls=FailingScraper)
    assert result['id'] == saved['id']
    assert result['cifra'] == saved['cifra']
    assert result['warnings'] == ['Scraping falhou; versão salva retornada.']
