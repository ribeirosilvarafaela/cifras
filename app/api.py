import os
import werkzeug.urls
if not hasattr(werkzeug.urls, 'url_quote'):
    from werkzeug.utils import url_quote
    werkzeug.urls.url_quote = url_quote

from flask import Flask, json, request
from cifraclub import CifraClub
from chords import keyboard_svg

app = Flask(__name__)

@app.route('/')
def home():
    """Home route"""
    return app.response_class(
        response=json.dumps({'api': 'Cifra Club API'}),
        status=200,
        mimetype='application/json'
    )

@app.route('/artists/<artist>/songs/<song>')
def get_cifra(artist, song):
    """Get cifra by artist and song"""
    cifrablub = CifraClub()
    return app.response_class(
        response=json.dumps(cifrablub.cifra(artist, song), ensure_ascii=False),
        status=200,
        mimetype='application/json'
    )

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
