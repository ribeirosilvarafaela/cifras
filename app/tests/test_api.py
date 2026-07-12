import json

import api
from database import configure_database, init_db
from services import get_song


class FakeScraper:
    def cifra(self, artist, song):
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


def test_frontend_pages_and_saved_song():
    client = api.app.test_client()
    assert client.get('/').status_code == 200
    assert client.get('/songs').status_code == 200
    saved = get_song('Coldplay', 'The Scientist', scraper_cls=FakeScraper)
    response = client.get('/songs/{}'.format(saved['id']))
    assert response.status_code == 200
    assert b'The Scientist' in response.data


def test_current_json_contract_and_svg_route():
    get_song('Coldplay', 'The Scientist', scraper_cls=FakeScraper)
    client = api.app.test_client()
    response = client.get('/artists/coldplay/songs/the-scientist')
    payload = json.loads(response.data)
    assert payload['cifra'] == ['C#m7', 'Come up to meet you']
    assert payload['chords'][0]['notes'] == ['C#', 'E', 'G#', 'B']
    svg = client.get('/chords/diagram.svg?name=C%23m7')
    assert svg.status_code == 200
    assert svg.mimetype == 'image/svg+xml'
