import os

import werkzeug.urls
if not hasattr(werkzeug.urls, 'url_quote'):
    from werkzeug.utils import url_quote
    werkzeug.urls.url_quote = url_quote

from flask import Flask, json, render_template, request

from chords import keyboard_svg
from services import get_song, get_song_by_id, list_recent, list_songs


app = Flask(__name__)


def json_response(payload):
    return app.response_class(
        response=json.dumps(payload, ensure_ascii=False),
        status=200,
        mimetype='application/json'
    )


@app.route('/')
def home():
    return render_template('index.html', songs=list_recent())


@app.route('/artists/<artist>/songs/<song>')
def artist_song(artist, song):
    try:
        result = get_song(artist, song, request.args.get('refresh') == 'true')
    except Exception:
        result = {
            'artist': artist,
            'name': song,
            'cifraclub_url': 'https://www.cifraclub.com.br/{}/{}'.format(artist, song),
            'error': 'error description',
        }
    return json_response(result)


@app.route('/songs')
def songs_page():
    return render_template('songs.html', songs=list_songs())


@app.route('/songs/<int:song_id>')
def saved_song_page(song_id):
    song = get_song_by_id(song_id)
    if song is None:
        return app.response_class('song not found', status=404, mimetype='text/plain')
    return render_template('song.html', song=song)


@app.route('/chords/diagram.svg')
def chord_diagram():
    name = request.args.get('name', '')
    try:
        svg = keyboard_svg(name)
    except (KeyError, TypeError, ValueError):
        return app.response_class('unsupported chord', status=400, mimetype='text/plain')
    return app.response_class(svg, status=200, mimetype='image/svg+xml')


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=os.getenv('PORT', '3000'), debug=True)
